"""Pipeline step wrappers for the playground web UI.

Each function wraps one pipeline stage so it can be called from an API route,
accept optional prompt overrides, and return structured dictionaries instead
of writing to disk.

Generated content (personalized textbooks, textbook chunks, videos) is
optionally persisted to the agentic_math_tutor PostgreSQL + Neo4j tables
via TutorDataServiceWriter.
"""

import logging
import re
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...config import Config
from ...knowledge_graph.concept_extractor import ConceptExtractor
from ...llm import create_llm_client
from ...llm.base import BaseLLMClient
from ...personalization import TextbookParser, get_interest_profile
from ...utils.code_extractor import extract_python_code
from ...utils.validators import validate_manim_code
from .models import PromptPreview
from .prompt_builder import (
    preview_animation_prompts,
    preview_concept_extraction_prompts,
    preview_personalization_prompts,
)

logger = logging.getLogger(__name__)

# Shared output dir for playground artifacts
PLAYGROUND_OUTPUT_DIR = Path(tempfile.gettempdir()) / "math_playground"
PLAYGROUND_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Source tag used in all playground data service writes
_PLAYGROUND_SOURCE = "playground"


def _get_tutor_writer():
    """Lazily create a TutorDataServiceWriter if the tutor DB is reachable."""
    try:
        from ...integration.tutor_writer import TutorDataServiceWriter
        return TutorDataServiceWriter()
    except Exception:
        logger.debug("TutorDataServiceWriter not available, skipping PG persistence")
        return None


def check_data_service_status() -> dict:
    """Probe PostgreSQL and Neo4j connectivity and return a status dict."""
    pg_ok = False
    neo4j_ok = False
    message_parts = []

    writer = _get_tutor_writer()
    if writer is None:
        return {"postgres_available": False, "neo4j_available": False, "message": "TutorDataServiceWriter not available"}

    # Check PostgreSQL
    try:
        import asyncio
        import asyncpg

        loop = writer._get_or_create_event_loop()

        async def _pg_ping():
            conn = await asyncpg.connect(writer.database_url)
            try:
                await conn.fetchval("SELECT 1")
                return True
            finally:
                await conn.close()

        pg_ok = loop.run_until_complete(_pg_ping())
        message_parts.append("PostgreSQL: connected")
    except Exception as exc:
        message_parts.append(f"PostgreSQL: unavailable ({exc})")

    # Check Neo4j
    try:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(
            writer._neo4j_uri,
            auth=(writer._neo4j_user, writer._neo4j_password),
        )
        try:
            with driver.session() as session:
                session.run("RETURN 1").consume()
            neo4j_ok = True
            message_parts.append("Neo4j: connected")
        finally:
            driver.close()
    except Exception as exc:
        message_parts.append(f"Neo4j: unavailable ({exc})")

    return {
        "postgres_available": pg_ok,
        "neo4j_available": neo4j_ok,
        "message": "; ".join(message_parts),
    }


# ---------------------------------------------------------------------------
# Personalization
# ---------------------------------------------------------------------------


def run_personalization(
    textbook_content: str,
    interest: str,
    config: Config,
    system_prompt_override: Optional[str] = None,
    user_prompt_override: Optional[str] = None,
    grade: Optional[str] = None,
) -> Dict[str, Any]:
    """Personalize textbook content via LLM.

    Returns a dict with ``personalized_content``, ``model_used``,
    ``tokens_used``, and ``duration_ms``.
    """
    preview = preview_personalization_prompts(textbook_content, interest)

    system_prompt = system_prompt_override or preview.system_prompt
    user_prompt = user_prompt_override or preview.user_prompt

    start = time.time()
    llm_client = create_llm_client(config)
    response = llm_client.generate(
        prompt=user_prompt,
        system_prompt=system_prompt,
    )
    duration_ms = int((time.time() - start) * 1000)

    result = {
        "personalized_content": response.content,
        "interest": interest,
        "model_used": response.model,
        "tokens_used": response.usage,
        "duration_ms": duration_ms,
        "prompts_used": PromptPreview(
            stage="personalize",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        ).model_dump(),
    }

    # Persist personalized content to agentic_math_tutor PG
    writer = _get_tutor_writer()
    if writer and hasattr(writer, "write_personalized_content"):
        try:
            from ...integration.tutor_writer import map_interest_to_theme

            content_id = f"playground_{uuid.uuid4().hex[:12]}"
            theme = map_interest_to_theme(interest)
            grade_val = grade or "grade_8"
            writer.write_personalized_content(
                content_id=content_id,
                theme=theme,
                grade=grade_val,
                personalized_content=response.content,
                original_content=textbook_content[:2000],
                personalization_method="llm",
                llm_model=response.model,
            )
            result["tutor_content_id"] = content_id
            logger.info("Persisted personalized content %s to tutor PG", content_id)
        except Exception:
            logger.debug("Failed to persist personalized content to tutor PG", exc_info=True)

    return result


# ---------------------------------------------------------------------------
# Concept extraction
# ---------------------------------------------------------------------------


def run_concept_extraction(
    markdown_content: str,
    config: Config,
    system_prompt_override: Optional[str] = None,
    user_prompt_override: Optional[str] = None,
) -> Dict[str, Any]:
    """Extract concepts from markdown content via LLM + knowledge graph.

    Returns a dict with ``matched_concepts``, ``new_concepts``, ``summary``,
    etc.
    """
    start = time.time()
    llm_client = create_llm_client(config)

    if system_prompt_override or user_prompt_override:
        # Custom prompts — call LLM directly and parse result
        preview = preview_concept_extraction_prompts(markdown_content, config)
        sys_prompt = system_prompt_override or preview.system_prompt
        usr_prompt = user_prompt_override or preview.user_prompt

        response = llm_client.generate(prompt=usr_prompt, system_prompt=sys_prompt)

        # Parse using the extractor's static parser
        extractor = ConceptExtractor(llm_client=llm_client)
        result = extractor._parse_llm_response(response.content)

        # Filter by confidence and validate IDs
        result.matched_concepts = [
            c for c in result.matched_concepts if c.confidence >= 0.7
        ]
        validated = [
            c
            for c in result.matched_concepts
            if c.concept_id in extractor.concept_index
        ]
        result.matched_concepts = validated
    else:
        # Standard flow
        extractor = ConceptExtractor(llm_client=llm_client)
        result = extractor.extract_concepts(markdown_content)
        preview = preview_concept_extraction_prompts(markdown_content, config)
        sys_prompt = preview.system_prompt
        usr_prompt = preview.user_prompt

    duration_ms = int((time.time() - start) * 1000)

    return {
        **result.to_dict(),
        "model_used": config.get_model(),
        "duration_ms": duration_ms,
        "prompts_used": PromptPreview(
            stage="extract_concepts",
            system_prompt=sys_prompt,
            user_prompt=usr_prompt,
        ).model_dump(),
    }


# ---------------------------------------------------------------------------
# Animation code generation
# ---------------------------------------------------------------------------


def run_animation_generation(
    topic: str,
    requirements: str,
    audience_level: str,
    interest: Optional[str],
    animation_style: str,
    config: Config,
    system_prompt_override: Optional[str] = None,
    user_prompt_override: Optional[str] = None,
    student_name: Optional[str] = None,
    preferred_address: Optional[str] = None,
    grade_level: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    favorite_figure: Optional[str] = None,
    favorite_team: Optional[str] = None,
    textbook_content: Optional[str] = None,
    concept_ids: Optional[List[str]] = None,
    grade: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate Manim animation code via LLM (no rendering).

    Returns a dict with ``code``, ``scene_name``, ``validation``, etc.
    The generated code metadata is also persisted to the tutor data service
    when available.
    """
    preview = preview_animation_prompts(
        topic=topic,
        requirements=requirements,
        audience_level=audience_level,
        interest=interest,
        animation_style=animation_style,
        student_name=student_name,
        preferred_address=preferred_address,
        grade_level=grade_level,
        city=city,
        state=state,
        favorite_figure=favorite_figure,
        favorite_team=favorite_team,
        textbook_content=textbook_content,
    )

    system_prompt = system_prompt_override or preview.system_prompt
    user_prompt = user_prompt_override or preview.user_prompt

    start = time.time()
    llm_client = create_llm_client(config)
    response = llm_client.generate(prompt=user_prompt, system_prompt=system_prompt)
    duration_ms = int((time.time() - start) * 1000)

    code = extract_python_code(response.content)
    validation = validate_manim_code(code)

    # Extract scene name
    scene_match = re.search(r"class\s+(\w+)\s*\(\s*Scene\s*\)", code)
    scene_name = scene_match.group(1) if scene_match else "GeneratedScene"

    result = {
        "code": code,
        "scene_name": scene_name,
        "validation": {
            "is_valid": validation.is_valid,
            "errors": validation.errors,
            "warnings": validation.warnings,
        },
        "raw_response": response.content,
        "model_used": response.model,
        "tokens_used": response.usage,
        "duration_ms": duration_ms,
        "prompts_used": PromptPreview(
            stage="generate_animation",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        ).model_dump(),
    }

    # Persist video metadata to tutor data service (code only — not yet rendered)
    writer = _get_tutor_writer()
    if writer and concept_ids:
        try:
            from ...integration.tutor_writer import map_interest_to_theme

            engine_video_id = f"playground_{uuid.uuid4().hex[:12]}"
            first_concept = concept_ids[0]
            gen_time_seconds = duration_ms / 1000.0

            pg_id = writer.write_video(
                concept_id=first_concept,
                interest=interest,
                grade=grade,
                engine_video_id=engine_video_id,
                manim_code=code,
                success=validation.is_valid,
                generation_time_seconds=gen_time_seconds,
                error_message=(
                    "; ".join(validation.errors) if validation.errors else None
                ),
                source=_PLAYGROUND_SOURCE,
            )
            if pg_id:
                result["tutor_video_id"] = pg_id
                result["engine_video_id"] = engine_video_id
                logger.info(
                    "Persisted animation code %s to tutor PG (concept=%s)",
                    engine_video_id, first_concept,
                )
        except Exception:
            logger.debug(
                "Failed to persist animation code to tutor PG", exc_info=True
            )

    return result


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def run_render(
    code: str,
    scene_name: str,
    quality: str,
    config: Config,
    concept_ids: Optional[List[str]] = None,
    interest: Optional[str] = None,
    grade: Optional[str] = None,
    topic: Optional[str] = None,
) -> Dict[str, Any]:
    """Render Manim code to a video file.

    Returns a dict with ``success``, ``video_path``, ``render_time_ms``, etc.
    After a successful render the video metadata is persisted to the tutor
    data service when available.
    """
    from ...renderer.manim_renderer import ManimRenderer
    from ...constants import VideoQuality

    quality_map = {
        "l": VideoQuality.LOW,
        "m": VideoQuality.MEDIUM,
        "h": VideoQuality.HIGH,
        "p": VideoQuality.PRODUCTION,
        "k": VideoQuality.FOURK,
    }
    video_quality = quality_map.get(quality, VideoQuality.LOW)

    output_dir = PLAYGROUND_OUTPUT_DIR / "videos"
    output_dir.mkdir(parents=True, exist_ok=True)

    cache_dir = PLAYGROUND_OUTPUT_DIR / "manim_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    start = time.time()
    try:
        renderer = ManimRenderer(
            output_dir=output_dir,
            cache_dir=cache_dir,
            quality=video_quality,
        )
        result = renderer.render(
            code=code,
            scene_name=scene_name,
        )
        render_time_ms = int((time.time() - start) * 1000)

        if result.success and result.output_path:
            render_result = {
                "success": True,
                "video_path": str(result.output_path),
                "video_filename": result.output_path.name,
                "render_time_ms": render_time_ms,
            }

            # Persist rendered video to tutor data service
            _persist_rendered_video(
                code=code,
                concept_ids=concept_ids,
                interest=interest,
                grade=grade,
                render_time_ms=render_time_ms,
                video_path=result.output_path,
                render_result=render_result,
            )

            return render_result

        return {
            "success": False,
            "error": result.error_message or "Unknown render error",
            "render_time_ms": render_time_ms,
        }

    except Exception as exc:
        render_time_ms = int((time.time() - start) * 1000)
        return {
            "success": False,
            "error": str(exc),
            "render_time_ms": render_time_ms,
        }


def _persist_rendered_video(
    *,
    code: str,
    concept_ids: Optional[List[str]],
    interest: Optional[str],
    grade: Optional[str],
    render_time_ms: int,
    video_path: Path,
    render_result: Dict[str, Any],
) -> None:
    """Persist a successfully rendered video to the tutor data service."""
    if not concept_ids:
        return

    writer = _get_tutor_writer()
    if not writer:
        return

    try:
        engine_video_id = f"playground_render_{uuid.uuid4().hex[:12]}"
        first_concept = concept_ids[0]
        file_size_bytes = video_path.stat().st_size if video_path.exists() else None

        pg_id = writer.write_video(
            concept_id=first_concept,
            interest=interest,
            grade=grade,
            engine_video_id=engine_video_id,
            manim_code=code,
            success=True,
            file_size_bytes=file_size_bytes,
            generation_time_seconds=render_time_ms / 1000.0,
            source=_PLAYGROUND_SOURCE,
        )
        if pg_id:
            render_result["tutor_video_id"] = pg_id
            render_result["engine_video_id"] = engine_video_id
            logger.info(
                "Persisted rendered video %s to tutor PG (concept=%s)",
                engine_video_id, first_concept,
            )
    except Exception:
        logger.debug("Failed to persist rendered video to tutor PG", exc_info=True)


# ---------------------------------------------------------------------------
# Textbook parsing (extract animation examples)
# ---------------------------------------------------------------------------


def run_textbook_parse(textbook_content: str) -> Dict[str, Any]:
    """Parse textbook markdown to extract animation examples.

    Returns a dict with ``examples`` list and ``count``.
    Also persists extracted chunks to agentic_math_tutor PG if available.
    """
    # Write content to a temp file so TextbookParser can read it
    tmp_path = PLAYGROUND_OUTPUT_DIR / "temp_textbook.md"
    tmp_path.write_text(textbook_content, encoding="utf-8")

    try:
        parser = TextbookParser(str(tmp_path))
        parser.parse()
        specs = parser.get_examples_for_animation()

        examples = [
            {
                "section": s.get("section", ""),
                "example_num": s.get("example_num", 0),
                "topic": s.get("topic", ""),
                "requirements": s.get("requirements", ""),
                "equation": s.get("equation", ""),
                "context": s.get("context", ""),
            }
            for s in specs
        ]

        result = {"examples": examples, "count": len(specs)}

        # Persist textbook chunks to agentic_math_tutor PG
        writer = _get_tutor_writer()
        if writer and hasattr(writer, "write_textbook_chunk") and examples:
            chunk_ids = []
            for i, ex in enumerate(examples):
                try:
                    chunk_id = f"playground_chunk_{uuid.uuid4().hex[:12]}"
                    content = f"{ex.get('topic', '')}\n{ex.get('requirements', '')}\n{ex.get('equation', '')}"
                    writer.write_textbook_chunk(
                        chunk_id=chunk_id,
                        textbook_id="playground_upload",
                        concept_id=f"algebra.unknown.{ex.get('topic', 'unknown').replace(' ', '_').lower()[:40]}",
                        content=content.strip(),
                        content_type="example",
                        chapter=0,
                        section=i + 1,
                        title=ex.get("topic", ""),
                        source=_PLAYGROUND_SOURCE,
                    )
                    chunk_ids.append(chunk_id)
                except Exception:
                    logger.debug("Failed to persist chunk %d to tutor PG", i, exc_info=True)
            if chunk_ids:
                result["tutor_chunk_ids"] = chunk_ids
                logger.info("Persisted %d textbook chunks to tutor PG", len(chunk_ids))

        return result
    except Exception as exc:
        logger.exception("Textbook parsing failed")
        return {"examples": [], "count": 0, "error": str(exc)}
