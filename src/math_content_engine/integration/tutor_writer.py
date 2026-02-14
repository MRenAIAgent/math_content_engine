"""
TutorDataServiceWriter — writes generated video metadata to the
agentic_math_tutor data service (PostgreSQL + Neo4j) as part of the
engine pipeline.

This module bridges math_content_engine → agentic_math_tutor by:
  1. Upserting video records into the tutor's PostgreSQL ``videos`` table
  2. Creating/merging a ``Video`` node in Neo4j and linking it to the
     ``Concept`` node via a ``DEMONSTRATES`` relationship
"""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# Interest name → agentic_math_tutor ContentTheme value
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


class TutorDataServiceWriter:
    """Writes video records into the agentic_math_tutor data service.

    Targets **two** stores:

    * **PostgreSQL** — ``videos`` table (upsert on concept_id/theme/grade)
    * **Neo4j** — ``Video`` node + ``DEMONSTRATES`` edge → ``Concept`` node

    This is a synchronous wrapper around asyncpg / neo4j for easy use inside
    the synchronous ``MathContentEngine.generate()`` pipeline.

    Usage::

        writer = TutorDataServiceWriter(
            database_url="postgresql://...",
            neo4j_uri="bolt://localhost:17687",
        )
        writer.write_video(
            concept_id="AT-24",
            interest="basketball",
            grade="grade_8",
            engine_video_id="abc-123",
            manim_code="class Scene...",
            success=True,
        )
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
                self._async_write(
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
            self._write_neo4j(
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

    def read_video(self, video_uuid: str) -> Optional[dict]:
        """Read a video row from the tutor PostgreSQL by UUID.

        Returns the row as a dict, or ``None`` if not found.
        """
        try:
            loop = self._get_or_create_event_loop()
            return loop.run_until_complete(self._async_read(video_uuid))
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

    def cleanup_e2e(self, source: str = "math_content_engine") -> None:
        """Remove videos inserted by this writer (matching source) from PG and Neo4j."""
        # PostgreSQL cleanup
        try:
            loop = self._get_or_create_event_loop()
            loop.run_until_complete(self._async_cleanup(source))
        except Exception:
            logger.exception("Failed to cleanup e2e videos from tutor PostgreSQL")

        # Neo4j cleanup
        try:
            self._cleanup_neo4j(source)
        except Exception:
            logger.exception("Failed to cleanup e2e videos from Neo4j")

    # ------------------------------------------------------------------
    # Private async helpers
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

    async def _async_write(
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

    async def _async_read(self, video_uuid: str) -> Optional[dict]:
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

    async def _async_cleanup(self, source: str) -> None:
        import asyncpg

        conn = await asyncpg.connect(self._database_url)
        try:
            deleted = await conn.execute(
                "DELETE FROM videos WHERE source = $1",
                source,
            )
            logger.info("Cleaned up tutor PG videos with source=%s: %s", source, deleted)
        finally:
            await conn.close()

    # ------------------------------------------------------------------
    # Private Neo4j helpers
    # ------------------------------------------------------------------

    def _write_neo4j(
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

            # Link Video → Concept via DEMONSTRATES
            # MERGE the Concept if it doesn't exist yet (engine may
            # reference concepts not yet seeded), then MERGE the edge.
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

    def _cleanup_neo4j(self, source: str) -> None:
        """Remove Video nodes (and their edges) matching source from Neo4j."""
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(
            self._neo4j_uri,
            auth=(self._neo4j_user, self._neo4j_password),
        )
        with driver.session() as session:
            result = session.run(
                """
                MATCH (v:Video {source: $source})
                DETACH DELETE v
                RETURN count(v) AS deleted
                """,
                source=source,
            )
            record = result.single()
            cnt = record["deleted"] if record else 0
            logger.info(
                "Cleaned up Neo4j Video nodes with source=%s: %d deleted",
                source,
                cnt,
            )
        driver.close()
