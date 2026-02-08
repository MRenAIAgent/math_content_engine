"""Pipeline step wrappers for the playground web UI.

Each function wraps one pipeline stage so it can be called from an API route,
accept optional prompt overrides, and return structured dictionaries instead
of writing to disk.
"""

import logging
import re
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Optional

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


# ---------------------------------------------------------------------------
# Personalization
# ---------------------------------------------------------------------------


def run_personalization(
    textbook_content: str,
    interest: str,
    config: Config,
    system_prompt_override: Optional[str] = None,
    user_prompt_override: Optional[str] = None,
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

    return {
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
    personal_context: Optional[str] = None,
    favorite_figure: Optional[str] = None,
    favorite_team: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate Manim animation code via LLM (no rendering).

    Returns a dict with ``code``, ``scene_name``, ``validation``, etc.
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
        personal_context=personal_context,
        favorite_figure=favorite_figure,
        favorite_team=favorite_team,
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

    return {
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


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def run_render(
    code: str,
    scene_name: str,
    quality: str,
    config: Config,
) -> Dict[str, Any]:
    """Render Manim code to a video file.

    Returns a dict with ``success``, ``video_path``, ``render_time_ms``, etc.
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

    start = time.time()
    try:
        renderer = ManimRenderer(config)
        result = renderer.render(
            code=code,
            scene_name=scene_name,
            output_dir=output_dir,
            quality=video_quality,
        )
        render_time_ms = int((time.time() - start) * 1000)

        if result.success and result.output_path:
            return {
                "success": True,
                "video_path": str(result.output_path),
                "video_filename": result.output_path.name,
                "render_time_ms": render_time_ms,
            }

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


# ---------------------------------------------------------------------------
# Textbook parsing (extract animation examples)
# ---------------------------------------------------------------------------


def run_textbook_parse(textbook_content: str) -> Dict[str, Any]:
    """Parse textbook markdown to extract animation examples.

    Returns a dict with ``examples`` list and ``count``.
    """
    # Write content to a temp file so TextbookParser can read it
    tmp_path = PLAYGROUND_OUTPUT_DIR / "temp_textbook.md"
    tmp_path.write_text(textbook_content, encoding="utf-8")

    try:
        parser = TextbookParser(str(tmp_path))
        parser.parse()
        specs = parser.get_examples_for_animation()

        return {
            "examples": [
                {
                    "section": s.get("section", ""),
                    "example_num": s.get("example_num", 0),
                    "topic": s.get("topic", ""),
                    "requirements": s.get("requirements", ""),
                    "equation": s.get("equation", ""),
                    "context": s.get("context", ""),
                }
                for s in specs
            ],
            "count": len(specs),
        }
    except Exception as exc:
        logger.exception("Textbook parsing failed")
        return {"examples": [], "count": 0, "error": str(exc)}
