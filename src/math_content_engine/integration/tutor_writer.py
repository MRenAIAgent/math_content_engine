"""
TutorDataServiceWriter — writes generated content metadata to the
agentic_math_tutor data service (PostgreSQL + Neo4j) as part of the
engine pipeline.

This module bridges math_content_engine -> agentic_math_tutor by:
  1. Upserting video records into the tutor's PostgreSQL ``videos`` table
  2. Upserting exercise records into the ``exercises`` table
  3. Upserting textbook chunk records into the ``textbook_chunks`` table
  4. Upserting personalized content records into ``personalized_content``
  5. Creating/merging corresponding nodes and edges in Neo4j
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import List, Optional

logger = logging.getLogger(__name__)

# Interest name -> agentic_math_tutor ContentTheme value
INTEREST_TO_THEME = {
    "basketball": "sports_basketball",
    "soccer": "sports_soccer",
    "gaming": "gaming_minecraft",
    "minecraft": "gaming_minecraft",
    "pokemon": "gaming_pokemon",
    "space": "nature_space",
    "animals": "nature_animals",
    "music": "music_pop",
    "pop_music": "music_pop",
    "robots": "technology_robots",
    "cooking": "food_cooking",
    "art": "art_drawing",
    "drawing": "art_drawing",
}

# Prefix used in the keywords array to track source for cleanup.
# Tables like exercises and textbook_chunks lack a dedicated ``source``
# column, so we embed a ``_source:<value>`` marker in keywords instead.
_SOURCE_KEYWORD_PREFIX = "_source:"


def map_interest_to_theme(interest: Optional[str]) -> str:
    """Map engine interest name to tutor ContentTheme value."""
    if not interest:
        return "neutral"
    return INTEREST_TO_THEME.get(interest, "neutral")


def normalize_grade(grade: Optional[str]) -> str:
    """Normalise grade strings to tutor GradeLevel values (e.g. 'grade_8')."""
    if not grade:
        return "grade_7"
    if grade.startswith("grade_"):
        return grade
    return grade


def _keywords_with_source(keywords: Optional[List[str]], source: str) -> List[str]:
    """Return a keywords list that includes a ``_source:<source>`` marker.

    The marker enables cleanup queries to find rows written by a given
    source without requiring a dedicated ``source`` column.
    """
    base = list(keywords) if keywords else []
    marker = f"{_SOURCE_KEYWORD_PREFIX}{source}"
    if marker not in base:
        base.append(marker)
    return base


class TutorDataServiceWriter:
    """Writes content records into the agentic_math_tutor data service.

    Targets **two** stores:

    * **PostgreSQL** -- ``videos``, ``exercises``, ``textbook_chunks``,
      and ``personalized_content`` tables (upsert semantics).
    * **Neo4j** -- corresponding nodes and relationship edges to
      ``Concept`` nodes.

    This is a synchronous wrapper around asyncpg / neo4j for easy use
    inside the synchronous ``MathContentEngine.generate()`` pipeline.
    """

    def __init__(
        self,
        database_url: Optional[str] = None,
        neo4j_uri: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_password: Optional[str] = None,
    ):
        self._database_url = database_url or os.getenv(
            "TUTOR_DATABASE_URL",
            "postgresql://math_tutor_app:local_dev_password@localhost:15432/math_tutor",
        )
        self._neo4j_uri = neo4j_uri or os.getenv(
            "NEO4J_URI", "bolt://localhost:17687"
        )
        self._neo4j_user = neo4j_user or os.getenv("NEO4J_USER", "neo4j")
        self._neo4j_password = neo4j_password or os.getenv(
            "NEO4J_PASSWORD", "local_dev_password"
        )

    @property
    def database_url(self) -> str:
        return self._database_url

    # ------------------------------------------------------------------
    # Video write (existing)
    # ------------------------------------------------------------------

    def write_video(
        self,
        *,
        concept_id: str,
        interest: Optional[str] = None,
        grade: Optional[str] = None,
        engine_video_id: str,
        manim_code: str,
        success: bool = True,
        file_size_bytes: Optional[int] = None,
        generation_time_seconds: Optional[float] = None,
        error_message: Optional[str] = None,
        source: str = "math_content_engine",
    ) -> Optional[str]:
        """Insert or update a video record in both PostgreSQL and Neo4j.

        * **PostgreSQL**: upsert into ``videos`` table (ON CONFLICT on
          concept_id/theme/grade).
        * **Neo4j**: MERGE a ``Video`` node keyed on ``engine_video_id`` and
          create/update a ``DEMONSTRATES`` relationship to the ``Concept``
          node matching ``concept_id``.

        Returns the UUID string of the PG row, or ``None`` on failure.
        """
        theme = map_interest_to_theme(interest)
        grade_val = normalize_grade(grade)
        status = "pre_generated" if success else "failed"

        pg_id: Optional[str] = None

        # --- PostgreSQL ---
        try:
            loop = self._get_or_create_event_loop()
            pg_id = loop.run_until_complete(
                self._async_write_video(
                    concept_id=concept_id,
                    theme=theme,
                    grade=grade_val,
                    engine_video_id=engine_video_id,
                    manim_code=manim_code,
                    status=status,
                    file_size_bytes=file_size_bytes,
                    generation_time_seconds=generation_time_seconds,
                    error_message=error_message,
                    source=source,
                )
            )
        except Exception:
            logger.exception("Failed to write video to tutor PostgreSQL")

        # --- Neo4j ---
        try:
            self._write_neo4j_video(
                concept_id=concept_id,
                theme=theme,
                grade=grade_val,
                engine_video_id=engine_video_id,
                status=status,
                source=source,
                generation_time_seconds=generation_time_seconds,
            )
        except Exception:
            logger.exception("Failed to write video to Neo4j")

        return pg_id

    # ------------------------------------------------------------------
    # Exercise write (new)
    # ------------------------------------------------------------------

    def write_exercise(
        self,
        *,
        exercise_id: str,
        concept_id: str,
        title: str,
        problem: str,
        solution: str,
        answer: Optional[str] = None,
        difficulty: int,
        hints: Optional[List[str]] = None,
        theme: str = "neutral",
        grade: str,
        keywords: Optional[List[str]] = None,
        skill_tested: str = "procedural",
        estimated_time_minutes: Optional[int] = None,
        source_exercise_id: Optional[str] = None,
        source: str = "math_content_engine",
    ) -> Optional[str]:
        """Insert or update an exercise in both PostgreSQL and Neo4j.

        * **PostgreSQL**: upsert into ``exercises`` table
          (ON CONFLICT exercise_id DO UPDATE).
        * **Neo4j**: MERGE an ``Exercise`` node keyed on ``exercise_id``
          and create/update a ``TESTS`` relationship to the ``Concept``
          node matching ``concept_id``.

        Returns ``exercise_id`` on success, or ``None`` on failure.
        """
        kw_with_source = _keywords_with_source(keywords, source)

        pg_id: Optional[str] = None

        # --- PostgreSQL ---
        try:
            loop = self._get_or_create_event_loop()
            pg_id = loop.run_until_complete(
                self._async_write_exercise(
                    exercise_id=exercise_id,
                    concept_id=concept_id,
                    title=title,
                    problem=problem,
                    solution=solution,
                    answer=answer,
                    difficulty=difficulty,
                    hints=hints or [],
                    theme=theme,
                    grade=grade,
                    keywords=kw_with_source,
                    skill_tested=skill_tested,
                    estimated_time_minutes=estimated_time_minutes,
                    source_exercise_id=source_exercise_id,
                )
            )
        except Exception:
            logger.exception("Failed to write exercise to tutor PostgreSQL")

        # --- Neo4j ---
        try:
            self._write_neo4j_exercise(
                exercise_id=exercise_id,
                concept_id=concept_id,
                title=title,
                difficulty=difficulty,
                theme=theme,
                grade=grade,
                skill_tested=skill_tested,
                source=source,
            )
        except Exception:
            logger.exception("Failed to write exercise to Neo4j")

        return pg_id

    # ------------------------------------------------------------------
    # Textbook chunk write (new)
    # ------------------------------------------------------------------

    def write_textbook_chunk(
        self,
        *,
        chunk_id: str,
        textbook_id: str,
        concept_id: str,
        content: str,
        content_type: str,
        chapter: int,
        section: int,
        page: Optional[int] = None,
        title: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        difficulty_level: str = "basic",
        source_url: Optional[str] = None,
        source: str = "math_content_engine",
    ) -> Optional[str]:
        """Insert or update a textbook chunk in both PostgreSQL and Neo4j.

        * **PostgreSQL**: upsert into ``textbook_chunks`` table
          (ON CONFLICT chunk_id DO UPDATE).
        * **Neo4j**: MERGE a ``TextbookChunk`` node keyed on ``chunk_id``
          and create/update an ``EXPLAINS`` relationship to the ``Concept``
          node matching ``concept_id``.

        Returns ``chunk_id`` on success, or ``None`` on failure.
        """
        kw_with_source = _keywords_with_source(keywords, source)

        pg_id: Optional[str] = None

        # --- PostgreSQL ---
        try:
            loop = self._get_or_create_event_loop()
            pg_id = loop.run_until_complete(
                self._async_write_textbook_chunk(
                    chunk_id=chunk_id,
                    textbook_id=textbook_id,
                    concept_id=concept_id,
                    content=content,
                    content_type=content_type,
                    chapter=chapter,
                    section=section,
                    page=page,
                    title=title,
                    keywords=kw_with_source,
                    difficulty_level=difficulty_level,
                    source_url=source_url,
                )
            )
        except Exception:
            logger.exception("Failed to write textbook chunk to tutor PostgreSQL")

        # --- Neo4j ---
        try:
            self._write_neo4j_textbook_chunk(
                chunk_id=chunk_id,
                textbook_id=textbook_id,
                concept_id=concept_id,
                content_type=content_type,
                chapter=chapter,
                section=section,
                difficulty_level=difficulty_level,
                title=title,
                source=source,
            )
        except Exception:
            logger.exception("Failed to write textbook chunk to Neo4j")

        return pg_id

    # ------------------------------------------------------------------
    # Personalized content write (new)
    # ------------------------------------------------------------------

    def write_personalized_content(
        self,
        *,
        content_id: str,
        source_chunk_id: Optional[str] = None,
        theme: str,
        grade: str,
        personalized_content: str,
        original_content: Optional[str] = None,
        educational_integrity: Optional[float] = None,
        engagement_score: Optional[float] = None,
        personalization_method: str = "llm",
        llm_model: Optional[str] = None,
    ) -> Optional[str]:
        """Insert or update a personalized content record.

        * **PostgreSQL**: upsert into ``personalized_content`` table
          (ON CONFLICT content_id DO UPDATE).
        * **Neo4j**: MERGE a ``PersonalizedContent`` node keyed on
          ``content_id``. If ``source_chunk_id`` is provided, creates a
          ``PERSONALIZED_FROM`` edge to the corresponding
          ``TextbookChunk`` node.

        Returns ``content_id`` on success, or ``None`` on failure.
        """
        pg_id: Optional[str] = None

        # --- PostgreSQL ---
        try:
            loop = self._get_or_create_event_loop()
            pg_id = loop.run_until_complete(
                self._async_write_personalized_content(
                    content_id=content_id,
                    source_chunk_id=source_chunk_id,
                    theme=theme,
                    grade=grade,
                    personalized_content=personalized_content,
                    original_content=original_content,
                    educational_integrity=educational_integrity,
                    engagement_score=engagement_score,
                    personalization_method=personalization_method,
                    llm_model=llm_model,
                )
            )
        except Exception:
            logger.exception(
                "Failed to write personalized content to tutor PostgreSQL"
            )

        # --- Neo4j ---
        try:
            self._write_neo4j_personalized_content(
                content_id=content_id,
                source_chunk_id=source_chunk_id,
                theme=theme,
                grade=grade,
                personalization_method=personalization_method,
            )
        except Exception:
            logger.exception("Failed to write personalized content to Neo4j")

        return pg_id

    # ------------------------------------------------------------------
    # Read helpers (existing)
    # ------------------------------------------------------------------

    def read_video(self, video_uuid: str) -> Optional[dict]:
        """Read a video row from the tutor PostgreSQL by UUID.

        Returns the row as a dict, or ``None`` if not found.
        """
        try:
            loop = self._get_or_create_event_loop()
            return loop.run_until_complete(self._async_read_video(video_uuid))
        except Exception:
            logger.exception("Failed to read video from tutor PostgreSQL")
            return None

    def read_neo4j_video(self, engine_video_id: str) -> Optional[dict]:
        """Read a Video node and its DEMONSTRATES relationship from Neo4j.

        Returns a dict with video node properties plus ``demonstrates_concept``
        (the concept_id it links to), or ``None`` if not found.
        """
        try:
            from neo4j import GraphDatabase

            driver = GraphDatabase.driver(
                self._neo4j_uri,
                auth=(self._neo4j_user, self._neo4j_password),
            )
            try:
                with driver.session() as session:
                    result = session.run(
                        """
                        MATCH (v:Video {engine_video_id: $vid})
                        OPTIONAL MATCH (v)-[r:DEMONSTRATES]->(c:Concept)
                        RETURN v, r, c.concept_id AS concept_id
                        """,
                        vid=engine_video_id,
                    )
                    record = result.single()
                    if record is None:
                        return None

                    video_props = dict(record["v"])
                    video_props["demonstrates_concept"] = record["concept_id"]
                    if record["r"] is not None:
                        video_props["demonstrates_props"] = dict(record["r"])
                    return video_props
            finally:
                driver.close()
        except Exception:
            logger.exception("Failed to read video from Neo4j")
            return None

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup_e2e(self, source: str = "math_content_engine") -> None:
        """Remove content inserted by this writer (matching source) from PG and Neo4j.

        Cleans up rows from **all** content tables: videos, exercises,
        textbook_chunks, and personalized_content.

        For tables without a dedicated ``source`` column (exercises,
        textbook_chunks), cleanup uses the ``_source:<value>`` keyword
        marker that is embedded on write.  For personalized_content,
        rows referencing cleaned-up textbook_chunks are removed first.
        """
        # PostgreSQL cleanup
        try:
            loop = self._get_or_create_event_loop()
            loop.run_until_complete(self._async_cleanup(source))
        except Exception:
            logger.exception(
                "Failed to cleanup e2e content from tutor PostgreSQL"
            )

        # Neo4j cleanup
        try:
            self._cleanup_neo4j(source)
        except Exception:
            logger.exception("Failed to cleanup e2e content from Neo4j")

    # ------------------------------------------------------------------
    # Private: event loop helper
    # ------------------------------------------------------------------

    @staticmethod
    def _get_or_create_event_loop() -> asyncio.AbstractEventLoop:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("closed")
            return loop
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    # ------------------------------------------------------------------
    # Private: async PG helpers -- video
    # ------------------------------------------------------------------

    async def _async_write_video(
        self,
        *,
        concept_id: str,
        theme: str,
        grade: str,
        engine_video_id: str,
        manim_code: str,
        status: str,
        file_size_bytes: Optional[int],
        generation_time_seconds: Optional[float],
        error_message: Optional[str],
        source: str,
    ) -> str:
        import asyncpg

        conn = await asyncpg.connect(self._database_url)
        try:
            row_id = await conn.fetchval(
                """
                INSERT INTO videos (
                    concept_id, template_id, theme, grade,
                    gcs_bucket, gcs_path, cdn_url, status,
                    file_size_bytes, generation_time_seconds,
                    manim_code, engine_video_id, source,
                    error_message,
                    created_at, updated_at, generated_at
                ) VALUES (
                    $1, $2, $3, $4,
                    $5, $6, $7, $8,
                    $9, $10,
                    $11, $12, $13,
                    $14,
                    NOW(), NOW(), NOW()
                )
                ON CONFLICT (concept_id, theme, grade) DO UPDATE SET
                    gcs_path = EXCLUDED.gcs_path,
                    cdn_url = EXCLUDED.cdn_url,
                    status = EXCLUDED.status,
                    file_size_bytes = EXCLUDED.file_size_bytes,
                    generation_time_seconds = EXCLUDED.generation_time_seconds,
                    manim_code = EXCLUDED.manim_code,
                    engine_video_id = EXCLUDED.engine_video_id,
                    error_message = EXCLUDED.error_message,
                    updated_at = NOW()
                RETURNING id
                """,
                concept_id,
                "personalized",
                theme,
                grade,
                "local",
                f"engine/{engine_video_id}.mp4",
                None,
                status,
                file_size_bytes,
                generation_time_seconds,
                manim_code,
                engine_video_id,
                source,
                error_message,
            )
            logger.info(
                "Wrote video %s to tutor PG (concept=%s, theme=%s, grade=%s)",
                row_id,
                concept_id,
                theme,
                grade,
            )
            return str(row_id)
        finally:
            await conn.close()

    async def _async_read_video(self, video_uuid: str) -> Optional[dict]:
        import asyncpg
        import uuid as _uuid

        conn = await asyncpg.connect(self._database_url)
        try:
            row = await conn.fetchrow(
                "SELECT * FROM videos WHERE id = $1",
                _uuid.UUID(video_uuid),
            )
            return dict(row) if row else None
        finally:
            await conn.close()

    # ------------------------------------------------------------------
    # Private: async PG helpers -- exercise
    # ------------------------------------------------------------------

    async def _async_write_exercise(
        self,
        *,
        exercise_id: str,
        concept_id: str,
        title: str,
        problem: str,
        solution: str,
        answer: Optional[str],
        difficulty: int,
        hints: List[str],
        theme: str,
        grade: str,
        keywords: List[str],
        skill_tested: str,
        estimated_time_minutes: Optional[int],
        source_exercise_id: Optional[str],
    ) -> str:
        import asyncpg

        conn = await asyncpg.connect(self._database_url)
        try:
            returned_id = await conn.fetchval(
                """
                INSERT INTO exercises (
                    exercise_id, concept_id, title, problem, solution,
                    answer, difficulty, hints, theme, grade,
                    keywords, skill_tested, estimated_time_minutes,
                    source_exercise_id,
                    created_at, updated_at
                ) VALUES (
                    $1, $2, $3, $4, $5,
                    $6, $7, $8, $9, $10,
                    $11, $12, $13,
                    $14,
                    NOW(), NOW()
                )
                ON CONFLICT (exercise_id) DO UPDATE SET
                    concept_id = EXCLUDED.concept_id,
                    title = EXCLUDED.title,
                    problem = EXCLUDED.problem,
                    solution = EXCLUDED.solution,
                    answer = EXCLUDED.answer,
                    difficulty = EXCLUDED.difficulty,
                    hints = EXCLUDED.hints,
                    theme = EXCLUDED.theme,
                    grade = EXCLUDED.grade,
                    keywords = EXCLUDED.keywords,
                    skill_tested = EXCLUDED.skill_tested,
                    estimated_time_minutes = EXCLUDED.estimated_time_minutes,
                    source_exercise_id = EXCLUDED.source_exercise_id,
                    updated_at = NOW()
                RETURNING exercise_id
                """,
                exercise_id,
                concept_id,
                title,
                problem,
                solution,
                answer,
                difficulty,
                hints,
                theme,
                grade,
                keywords,
                skill_tested,
                estimated_time_minutes,
                source_exercise_id,
            )
            logger.info(
                "Wrote exercise %s to tutor PG (concept=%s, theme=%s, grade=%s)",
                returned_id,
                concept_id,
                theme,
                grade,
            )
            return str(returned_id)
        finally:
            await conn.close()

    # ------------------------------------------------------------------
    # Private: async PG helpers -- textbook chunk
    # ------------------------------------------------------------------

    async def _async_write_textbook_chunk(
        self,
        *,
        chunk_id: str,
        textbook_id: str,
        concept_id: str,
        content: str,
        content_type: str,
        chapter: int,
        section: int,
        page: Optional[int],
        title: Optional[str],
        keywords: List[str],
        difficulty_level: str,
        source_url: Optional[str],
    ) -> str:
        import asyncpg

        conn = await asyncpg.connect(self._database_url)
        try:
            returned_id = await conn.fetchval(
                """
                INSERT INTO textbook_chunks (
                    chunk_id, textbook_id, concept_id, content,
                    content_type, chapter, section, page,
                    title, keywords, difficulty_level, source_url,
                    created_at
                ) VALUES (
                    $1, $2, $3, $4,
                    $5, $6, $7, $8,
                    $9, $10, $11, $12,
                    NOW()
                )
                ON CONFLICT (chunk_id) DO UPDATE SET
                    textbook_id = EXCLUDED.textbook_id,
                    concept_id = EXCLUDED.concept_id,
                    content = EXCLUDED.content,
                    content_type = EXCLUDED.content_type,
                    chapter = EXCLUDED.chapter,
                    section = EXCLUDED.section,
                    page = EXCLUDED.page,
                    title = EXCLUDED.title,
                    keywords = EXCLUDED.keywords,
                    difficulty_level = EXCLUDED.difficulty_level,
                    source_url = EXCLUDED.source_url
                RETURNING chunk_id
                """,
                chunk_id,
                textbook_id,
                concept_id,
                content,
                content_type,
                chapter,
                section,
                page,
                title,
                keywords,
                difficulty_level,
                source_url,
            )
            logger.info(
                "Wrote textbook chunk %s to tutor PG (concept=%s, ch=%d, sec=%d)",
                returned_id,
                concept_id,
                chapter,
                section,
            )
            return str(returned_id)
        finally:
            await conn.close()

    # ------------------------------------------------------------------
    # Private: async PG helpers -- personalized content
    # ------------------------------------------------------------------

    async def _async_write_personalized_content(
        self,
        *,
        content_id: str,
        source_chunk_id: Optional[str],
        theme: str,
        grade: str,
        personalized_content: str,
        original_content: Optional[str],
        educational_integrity: Optional[float],
        engagement_score: Optional[float],
        personalization_method: str,
        llm_model: Optional[str],
    ) -> str:
        import asyncpg

        conn = await asyncpg.connect(self._database_url)
        try:
            returned_id = await conn.fetchval(
                """
                INSERT INTO personalized_content (
                    content_id, source_chunk_id, theme, grade,
                    personalized_content, original_content,
                    educational_integrity, engagement_score,
                    personalization_method, llm_model,
                    validation_status, created_at
                ) VALUES (
                    $1, $2, $3, $4,
                    $5, $6,
                    $7, $8,
                    $9, $10,
                    'pending', NOW()
                )
                ON CONFLICT (content_id) DO UPDATE SET
                    source_chunk_id = EXCLUDED.source_chunk_id,
                    theme = EXCLUDED.theme,
                    grade = EXCLUDED.grade,
                    personalized_content = EXCLUDED.personalized_content,
                    original_content = EXCLUDED.original_content,
                    educational_integrity = EXCLUDED.educational_integrity,
                    engagement_score = EXCLUDED.engagement_score,
                    personalization_method = EXCLUDED.personalization_method,
                    llm_model = EXCLUDED.llm_model
                RETURNING content_id
                """,
                content_id,
                source_chunk_id,
                theme,
                grade,
                personalized_content,
                original_content,
                educational_integrity,
                engagement_score,
                personalization_method,
                llm_model,
            )
            logger.info(
                "Wrote personalized content %s to tutor PG (theme=%s, grade=%s)",
                returned_id,
                theme,
                grade,
            )
            return str(returned_id)
        finally:
            await conn.close()

    # ------------------------------------------------------------------
    # Private: async PG cleanup
    # ------------------------------------------------------------------

    async def _async_cleanup(self, source: str) -> None:
        import asyncpg

        source_marker = f"{_SOURCE_KEYWORD_PREFIX}{source}"

        conn = await asyncpg.connect(self._database_url)
        try:
            # Order matters: personalized_content has FK -> textbook_chunks,
            # so delete personalized rows first that reference chunks we will
            # remove, then exercises, then chunks, then videos.

            # 1. Delete personalized_content referencing chunks with our source marker
            pc_deleted = await conn.execute(
                """
                DELETE FROM personalized_content
                WHERE source_chunk_id IN (
                    SELECT chunk_id FROM textbook_chunks
                    WHERE $1 = ANY(keywords)
                )
                """,
                source_marker,
            )
            logger.info(
                "Cleaned up tutor PG personalized_content with source=%s: %s",
                source,
                pc_deleted,
            )

            # 2. Delete exercises with source marker in keywords
            ex_deleted = await conn.execute(
                "DELETE FROM exercises WHERE $1 = ANY(keywords)",
                source_marker,
            )
            logger.info(
                "Cleaned up tutor PG exercises with source=%s: %s",
                source,
                ex_deleted,
            )

            # 3. Delete textbook_chunks with source marker in keywords
            tc_deleted = await conn.execute(
                "DELETE FROM textbook_chunks WHERE $1 = ANY(keywords)",
                source_marker,
            )
            logger.info(
                "Cleaned up tutor PG textbook_chunks with source=%s: %s",
                source,
                tc_deleted,
            )

            # 4. Delete videos (has a dedicated source column)
            v_deleted = await conn.execute(
                "DELETE FROM videos WHERE source = $1",
                source,
            )
            logger.info(
                "Cleaned up tutor PG videos with source=%s: %s",
                source,
                v_deleted,
            )
        finally:
            await conn.close()

    # ------------------------------------------------------------------
    # Private: Neo4j helpers -- video
    # ------------------------------------------------------------------

    def _write_neo4j_video(
        self,
        *,
        concept_id: str,
        theme: str,
        grade: str,
        engine_video_id: str,
        status: str,
        source: str,
        generation_time_seconds: Optional[float],
    ) -> None:
        """Create/merge a Video node and DEMONSTRATES edge in Neo4j."""
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(
            self._neo4j_uri,
            auth=(self._neo4j_user, self._neo4j_password),
        )
        with driver.session() as session:
            session.run(
                """
                MERGE (v:Video {engine_video_id: $engine_video_id})
                ON CREATE SET
                    v.concept_id = $concept_id,
                    v.theme = $theme,
                    v.grade = $grade,
                    v.status = $status,
                    v.source = $source,
                    v.generation_time_seconds = $gen_time,
                    v.created_at = datetime(),
                    v.updated_at = datetime()
                ON MATCH SET
                    v.status = $status,
                    v.source = $source,
                    v.generation_time_seconds = $gen_time,
                    v.updated_at = datetime()
                """,
                engine_video_id=engine_video_id,
                concept_id=concept_id,
                theme=theme,
                grade=grade,
                status=status,
                source=source,
                gen_time=generation_time_seconds,
            )

            # Link Video -> Concept via DEMONSTRATES
            session.run(
                """
                MERGE (v:Video {engine_video_id: $engine_video_id})
                MERGE (c:Concept {concept_id: $concept_id})
                MERGE (v)-[r:DEMONSTRATES]->(c)
                ON CREATE SET
                    r.is_primary = true,
                    r.demonstration_type = 'step_by_step',
                    r.created_at = datetime()
                ON MATCH SET
                    r.updated_at = datetime()
                """,
                engine_video_id=engine_video_id,
                concept_id=concept_id,
            )
        driver.close()
        logger.info(
            "Wrote Video node + DEMONSTRATES edge to Neo4j "
            "(engine_video_id=%s, concept=%s)",
            engine_video_id,
            concept_id,
        )

    # ------------------------------------------------------------------
    # Private: Neo4j helpers -- exercise
    # ------------------------------------------------------------------

    def _write_neo4j_exercise(
        self,
        *,
        exercise_id: str,
        concept_id: str,
        title: str,
        difficulty: int,
        theme: str,
        grade: str,
        skill_tested: str,
        source: str,
    ) -> None:
        """Create/merge an Exercise node and TESTS edge in Neo4j."""
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(
            self._neo4j_uri,
            auth=(self._neo4j_user, self._neo4j_password),
        )
        with driver.session() as session:
            session.run(
                """
                MERGE (e:Exercise {exercise_id: $exercise_id})
                ON CREATE SET
                    e.concept_id = $concept_id,
                    e.title = $title,
                    e.difficulty = $difficulty,
                    e.theme = $theme,
                    e.grade = $grade,
                    e.skill_tested = $skill_tested,
                    e.source = $source,
                    e.created_at = datetime(),
                    e.updated_at = datetime()
                ON MATCH SET
                    e.title = $title,
                    e.difficulty = $difficulty,
                    e.theme = $theme,
                    e.grade = $grade,
                    e.skill_tested = $skill_tested,
                    e.source = $source,
                    e.updated_at = datetime()
                """,
                exercise_id=exercise_id,
                concept_id=concept_id,
                title=title,
                difficulty=difficulty,
                theme=theme,
                grade=grade,
                skill_tested=skill_tested,
                source=source,
            )

            # Link Exercise -> Concept via TESTS
            session.run(
                """
                MERGE (e:Exercise {exercise_id: $exercise_id})
                MERGE (c:Concept {concept_id: $concept_id})
                MERGE (e)-[r:TESTS]->(c)
                ON CREATE SET
                    r.skill_tested = $skill_tested,
                    r.difficulty = $difficulty,
                    r.created_at = datetime()
                ON MATCH SET
                    r.skill_tested = $skill_tested,
                    r.difficulty = $difficulty,
                    r.updated_at = datetime()
                """,
                exercise_id=exercise_id,
                concept_id=concept_id,
                skill_tested=skill_tested,
                difficulty=difficulty,
            )
        driver.close()
        logger.info(
            "Wrote Exercise node + TESTS edge to Neo4j "
            "(exercise_id=%s, concept=%s)",
            exercise_id,
            concept_id,
        )

    # ------------------------------------------------------------------
    # Private: Neo4j helpers -- textbook chunk
    # ------------------------------------------------------------------

    def _write_neo4j_textbook_chunk(
        self,
        *,
        chunk_id: str,
        textbook_id: str,
        concept_id: str,
        content_type: str,
        chapter: int,
        section: int,
        difficulty_level: str,
        title: Optional[str],
        source: str,
    ) -> None:
        """Create/merge a TextbookChunk node and EXPLAINS edge in Neo4j."""
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(
            self._neo4j_uri,
            auth=(self._neo4j_user, self._neo4j_password),
        )
        with driver.session() as session:
            session.run(
                """
                MERGE (t:TextbookChunk {chunk_id: $chunk_id})
                ON CREATE SET
                    t.textbook_id = $textbook_id,
                    t.concept_id = $concept_id,
                    t.content_type = $content_type,
                    t.chapter = $chapter,
                    t.section = $section,
                    t.difficulty_level = $difficulty_level,
                    t.title = $title,
                    t.source = $source,
                    t.created_at = datetime(),
                    t.updated_at = datetime()
                ON MATCH SET
                    t.content_type = $content_type,
                    t.chapter = $chapter,
                    t.section = $section,
                    t.difficulty_level = $difficulty_level,
                    t.title = $title,
                    t.source = $source,
                    t.updated_at = datetime()
                """,
                chunk_id=chunk_id,
                textbook_id=textbook_id,
                concept_id=concept_id,
                content_type=content_type,
                chapter=chapter,
                section=section,
                difficulty_level=difficulty_level,
                title=title,
                source=source,
            )

            # Link TextbookChunk -> Concept via EXPLAINS
            session.run(
                """
                MERGE (t:TextbookChunk {chunk_id: $chunk_id})
                MERGE (c:Concept {concept_id: $concept_id})
                MERGE (t)-[r:EXPLAINS]->(c)
                ON CREATE SET
                    r.content_type = $content_type,
                    r.difficulty_level = $difficulty_level,
                    r.created_at = datetime()
                ON MATCH SET
                    r.content_type = $content_type,
                    r.difficulty_level = $difficulty_level,
                    r.updated_at = datetime()
                """,
                chunk_id=chunk_id,
                concept_id=concept_id,
                content_type=content_type,
                difficulty_level=difficulty_level,
            )
        driver.close()
        logger.info(
            "Wrote TextbookChunk node + EXPLAINS edge to Neo4j "
            "(chunk_id=%s, concept=%s)",
            chunk_id,
            concept_id,
        )

    # ------------------------------------------------------------------
    # Private: Neo4j helpers -- personalized content
    # ------------------------------------------------------------------

    def _write_neo4j_personalized_content(
        self,
        *,
        content_id: str,
        source_chunk_id: Optional[str],
        theme: str,
        grade: str,
        personalization_method: str,
    ) -> None:
        """Create/merge a PersonalizedContent node in Neo4j.

        If ``source_chunk_id`` is provided, also creates a
        ``PERSONALIZED_FROM`` edge to the matching ``TextbookChunk`` node.
        """
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(
            self._neo4j_uri,
            auth=(self._neo4j_user, self._neo4j_password),
        )
        with driver.session() as session:
            session.run(
                """
                MERGE (p:PersonalizedContent {content_id: $content_id})
                ON CREATE SET
                    p.theme = $theme,
                    p.grade = $grade,
                    p.personalization_method = $method,
                    p.source_chunk_id = $source_chunk_id,
                    p.created_at = datetime(),
                    p.updated_at = datetime()
                ON MATCH SET
                    p.theme = $theme,
                    p.grade = $grade,
                    p.personalization_method = $method,
                    p.source_chunk_id = $source_chunk_id,
                    p.updated_at = datetime()
                """,
                content_id=content_id,
                theme=theme,
                grade=grade,
                method=personalization_method,
                source_chunk_id=source_chunk_id,
            )

            # Link PersonalizedContent -> TextbookChunk via PERSONALIZED_FROM
            if source_chunk_id:
                session.run(
                    """
                    MERGE (p:PersonalizedContent {content_id: $content_id})
                    MERGE (t:TextbookChunk {chunk_id: $chunk_id})
                    MERGE (p)-[r:PERSONALIZED_FROM]->(t)
                    ON CREATE SET
                        r.created_at = datetime()
                    ON MATCH SET
                        r.updated_at = datetime()
                    """,
                    content_id=content_id,
                    chunk_id=source_chunk_id,
                )
        driver.close()
        logger.info(
            "Wrote PersonalizedContent node to Neo4j "
            "(content_id=%s, source_chunk=%s)",
            content_id,
            source_chunk_id,
        )

    # ------------------------------------------------------------------
    # Private: Neo4j cleanup
    # ------------------------------------------------------------------

    def _cleanup_neo4j(self, source: str) -> None:
        """Remove content nodes (and their edges) matching source from Neo4j.

        Deletes Video, Exercise, TextbookChunk, and PersonalizedContent
        nodes that have ``source`` set to the given value.  For
        PersonalizedContent nodes, removes those linked to cleaned-up
        TextbookChunk nodes via PERSONALIZED_FROM.
        """
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(
            self._neo4j_uri,
            auth=(self._neo4j_user, self._neo4j_password),
        )
        with driver.session() as session:
            # 1. PersonalizedContent linked to source TextbookChunks
            result_pc = session.run(
                """
                MATCH (p:PersonalizedContent)-[:PERSONALIZED_FROM]->(t:TextbookChunk {source: $source})
                DETACH DELETE p
                RETURN count(p) AS deleted
                """,
                source=source,
            )
            rec_pc = result_pc.single()
            cnt_pc = rec_pc["deleted"] if rec_pc else 0
            logger.info(
                "Cleaned up Neo4j PersonalizedContent nodes via source=%s: %d deleted",
                source,
                cnt_pc,
            )

            # 2. Exercise nodes
            result_ex = session.run(
                """
                MATCH (e:Exercise {source: $source})
                DETACH DELETE e
                RETURN count(e) AS deleted
                """,
                source=source,
            )
            rec_ex = result_ex.single()
            cnt_ex = rec_ex["deleted"] if rec_ex else 0
            logger.info(
                "Cleaned up Neo4j Exercise nodes with source=%s: %d deleted",
                source,
                cnt_ex,
            )

            # 3. TextbookChunk nodes
            result_tc = session.run(
                """
                MATCH (t:TextbookChunk {source: $source})
                DETACH DELETE t
                RETURN count(t) AS deleted
                """,
                source=source,
            )
            rec_tc = result_tc.single()
            cnt_tc = rec_tc["deleted"] if rec_tc else 0
            logger.info(
                "Cleaned up Neo4j TextbookChunk nodes with source=%s: %d deleted",
                source,
                cnt_tc,
            )

            # 4. Video nodes (original)
            result_v = session.run(
                """
                MATCH (v:Video {source: $source})
                DETACH DELETE v
                RETURN count(v) AS deleted
                """,
                source=source,
            )
            rec_v = result_v.single()
            cnt_v = rec_v["deleted"] if rec_v else 0
            logger.info(
                "Cleaned up Neo4j Video nodes with source=%s: %d deleted",
                source,
                cnt_v,
            )
        driver.close()
