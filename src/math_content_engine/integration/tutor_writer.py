"""
TutorDataServiceWriter — writes generated video metadata to the
agentic_math_tutor PostgreSQL database as part of the engine pipeline.

This module bridges math_content_engine → agentic_math_tutor by inserting
video records into the tutor's `videos` table after successful (or failed)
content generation.
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
    """Writes video records into the agentic_math_tutor PostgreSQL `videos` table.

    This is a synchronous wrapper around asyncpg for easy use inside the
    synchronous ``MathContentEngine.generate()`` pipeline.

    Usage::

        writer = TutorDataServiceWriter(database_url="postgresql://...")
        writer.write_video(
            concept_id="AT-24",
            interest="basketball",
            grade="grade_8",
            engine_video_id="abc-123",
            manim_code="class Scene...",
            success=True,
        )
    """

    def __init__(self, database_url: Optional[str] = None):
        self._database_url = database_url or os.getenv(
            "TUTOR_DATABASE_URL",
            "postgresql://math_tutor_app:local_dev_password@localhost:15432/math_tutor",
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
        """Insert or update a video record in the tutor's PostgreSQL videos table.

        Uses upsert (ON CONFLICT) so re-generating the same concept/theme/grade
        updates the existing row rather than raising a unique-constraint error.

        Returns the UUID string of the created/updated row, or ``None`` on failure.
        """
        theme = map_interest_to_theme(interest)
        grade_val = normalize_grade(grade)
        status = "pre_generated" if success else "failed"

        try:
            loop = self._get_or_create_event_loop()
            return loop.run_until_complete(
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
            return None

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

    def cleanup_e2e(self, source: str = "math_content_engine") -> None:
        """Remove videos inserted by this writer (matching source)."""
        try:
            loop = self._get_or_create_event_loop()
            loop.run_until_complete(self._async_cleanup(source))
        except Exception:
            logger.exception("Failed to cleanup e2e videos from tutor PostgreSQL")

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
