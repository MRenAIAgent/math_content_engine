"""
SQLite storage for video metadata.
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple

from .models import VideoMetadata, VideoCreate, VideoSearchParams

logger = logging.getLogger(__name__)


class VideoStorage:
    """SQLite-based storage for video metadata."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize video storage.

        Args:
            db_path: Path to SQLite database file. Defaults to ./data/videos.db
        """
        if db_path is None:
            db_path = Path("./data/videos.db")
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initialize database schema."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id TEXT PRIMARY KEY,
                    topic TEXT NOT NULL,
                    scene_name TEXT NOT NULL,
                    video_path TEXT NOT NULL,
                    code TEXT NOT NULL,

                    concept_ids TEXT,
                    grade TEXT,

                    requirements TEXT,
                    audience_level TEXT DEFAULT 'high school',
                    interest TEXT,
                    style TEXT DEFAULT 'dark',
                    quality TEXT DEFAULT 'm',

                    llm_provider TEXT,
                    llm_model TEXT,
                    input_tokens INTEGER,
                    output_tokens INTEGER,

                    generation_attempts INTEGER DEFAULT 1,
                    render_attempts INTEGER DEFAULT 1,
                    total_attempts INTEGER DEFAULT 1,
                    generation_time_ms INTEGER,
                    render_time_ms INTEGER,

                    file_size_bytes INTEGER,
                    duration_seconds REAL,

                    success INTEGER DEFAULT 1,
                    error_message TEXT,

                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # Migrate existing tables: add columns if they don't exist
            existing_cols = {
                row[1]
                for row in conn.execute("PRAGMA table_info(videos)").fetchall()
            }
            if "concept_ids" not in existing_cols:
                conn.execute("ALTER TABLE videos ADD COLUMN concept_ids TEXT")
                logger.info("Migrated: added concept_ids column to videos table")
            if "grade" not in existing_cols:
                conn.execute("ALTER TABLE videos ADD COLUMN grade TEXT")
                logger.info("Migrated: added grade column to videos table")

            # Create indexes for common queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_videos_topic ON videos(topic)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_videos_scene_name ON videos(scene_name)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_videos_interest ON videos(interest)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_videos_created_at ON videos(created_at)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_videos_success ON videos(success)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_videos_grade ON videos(grade)
            """)

            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")

    def save(self, video: VideoCreate) -> VideoMetadata:
        """
        Save a new video record.

        Args:
            video: Video data to save

        Returns:
            VideoMetadata with generated ID and timestamps
        """
        metadata = VideoMetadata(
            topic=video.topic,
            scene_name=video.scene_name,
            video_path=video.video_path,
            code=video.code,
            concept_ids=video.concept_ids,
            grade=video.grade,
            requirements=video.requirements,
            audience_level=video.audience_level,
            interest=video.interest,
            style=video.style,
            quality=video.quality,
            llm_provider=video.llm_provider,
            llm_model=video.llm_model,
            input_tokens=video.input_tokens,
            output_tokens=video.output_tokens,
            generation_attempts=video.generation_attempts,
            render_attempts=video.render_attempts,
            total_attempts=video.total_attempts,
            generation_time_ms=video.generation_time_ms,
            render_time_ms=video.render_time_ms,
            file_size_bytes=video.file_size_bytes,
            duration_seconds=video.duration_seconds,
            success=video.success,
            error_message=video.error_message,
        )

        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO videos (
                    id, topic, scene_name, video_path, code,
                    concept_ids, grade,
                    requirements, audience_level, interest, style, quality,
                    llm_provider, llm_model, input_tokens, output_tokens,
                    generation_attempts, render_attempts, total_attempts,
                    generation_time_ms, render_time_ms,
                    file_size_bytes, duration_seconds,
                    success, error_message,
                    created_at, updated_at
                ) VALUES (
                    ?, ?, ?, ?, ?,
                    ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?,
                    ?, ?,
                    ?, ?,
                    ?, ?
                )
            """, (
                metadata.id,
                metadata.topic,
                metadata.scene_name,
                metadata.video_path,
                metadata.code,
                json.dumps(metadata.concept_ids),
                metadata.grade,
                metadata.requirements,
                metadata.audience_level,
                metadata.interest,
                metadata.style.value,
                metadata.quality.value,
                metadata.llm_provider,
                metadata.llm_model,
                metadata.input_tokens,
                metadata.output_tokens,
                metadata.generation_attempts,
                metadata.render_attempts,
                metadata.total_attempts,
                metadata.generation_time_ms,
                metadata.render_time_ms,
                metadata.file_size_bytes,
                metadata.duration_seconds,
                1 if metadata.success else 0,
                metadata.error_message,
                metadata.created_at.isoformat(),
                metadata.updated_at.isoformat(),
            ))
            conn.commit()

        logger.info(f"Saved video metadata: id={metadata.id}, topic={metadata.topic}")
        return metadata

    def get_by_id(self, video_id: str) -> Optional[VideoMetadata]:
        """
        Get video metadata by ID.

        Args:
            video_id: The video ID

        Returns:
            VideoMetadata if found, None otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM videos WHERE id = ?",
                (video_id,)
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_metadata(row)

    def list_videos(
        self,
        params: Optional[VideoSearchParams] = None
    ) -> Tuple[List[VideoMetadata], int]:
        """
        List videos with optional filtering and pagination.

        Args:
            params: Search/filter parameters

        Returns:
            Tuple of (list of videos, total count)
        """
        if params is None:
            params = VideoSearchParams()

        # Build WHERE clause
        conditions = []
        values = []

        if params.topic:
            conditions.append("topic LIKE ?")
            values.append(f"%{params.topic}%")

        if params.scene_name:
            conditions.append("scene_name LIKE ?")
            values.append(f"%{params.scene_name}%")

        if params.interest:
            conditions.append("interest = ?")
            values.append(params.interest)

        if params.grade:
            conditions.append("grade = ?")
            values.append(params.grade)

        if params.style:
            conditions.append("style = ?")
            values.append(params.style.value)

        if params.quality:
            conditions.append("quality = ?")
            values.append(params.quality.value)

        if params.success_only:
            conditions.append("success = 1")

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        with self._get_connection() as conn:
            # Get total count
            count_query = f"SELECT COUNT(*) FROM videos {where_clause}"
            total = conn.execute(count_query, values).fetchone()[0]

            # Get paginated results
            offset = (params.page - 1) * params.page_size
            query = f"""
                SELECT * FROM videos
                {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            cursor = conn.execute(query, values + [params.page_size, offset])
            rows = cursor.fetchall()

        videos = [self._row_to_metadata(row) for row in rows]
        return videos, total

    def delete(self, video_id: str) -> bool:
        """
        Delete a video record.

        Args:
            video_id: The video ID to delete

        Returns:
            True if deleted, False if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM videos WHERE id = ?",
                (video_id,)
            )
            conn.commit()
            deleted = cursor.rowcount > 0

        if deleted:
            logger.info(f"Deleted video: id={video_id}")
        return deleted

    def update(self, video_id: str, **updates) -> Optional[VideoMetadata]:
        """
        Update video metadata.

        Args:
            video_id: The video ID
            **updates: Fields to update

        Returns:
            Updated VideoMetadata if found, None otherwise
        """
        if not updates:
            return self.get_by_id(video_id)

        # Add updated_at timestamp
        updates["updated_at"] = datetime.utcnow().isoformat()

        # Build SET clause
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [video_id]

        with self._get_connection() as conn:
            conn.execute(
                f"UPDATE videos SET {set_clause} WHERE id = ?",
                values
            )
            conn.commit()

        return self.get_by_id(video_id)

    def _row_to_metadata(self, row: sqlite3.Row) -> VideoMetadata:
        """Convert a database row to VideoMetadata."""
        from .models import AnimationStyle, VideoQuality

        return VideoMetadata(
            id=row["id"],
            topic=row["topic"],
            scene_name=row["scene_name"],
            video_path=row["video_path"],
            code=row["code"],
            concept_ids=json.loads(row["concept_ids"] or "[]"),
            grade=row["grade"],
            requirements=row["requirements"],
            audience_level=row["audience_level"] or "high school",
            interest=row["interest"],
            style=AnimationStyle(row["style"]) if row["style"] else AnimationStyle.DARK,
            quality=VideoQuality(row["quality"]) if row["quality"] else VideoQuality.MEDIUM,
            llm_provider=row["llm_provider"],
            llm_model=row["llm_model"],
            input_tokens=row["input_tokens"],
            output_tokens=row["output_tokens"],
            generation_attempts=row["generation_attempts"] or 1,
            render_attempts=row["render_attempts"] or 1,
            total_attempts=row["total_attempts"] or 1,
            generation_time_ms=row["generation_time_ms"],
            render_time_ms=row["render_time_ms"],
            file_size_bytes=row["file_size_bytes"],
            duration_seconds=row["duration_seconds"],
            success=bool(row["success"]),
            error_message=row["error_message"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def get_stats(self) -> dict:
        """Get storage statistics."""
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM videos").fetchone()[0]
            successful = conn.execute(
                "SELECT COUNT(*) FROM videos WHERE success = 1"
            ).fetchone()[0]
            by_interest = conn.execute("""
                SELECT interest, COUNT(*) as count
                FROM videos
                WHERE interest IS NOT NULL
                GROUP BY interest
            """).fetchall()
            by_style = conn.execute("""
                SELECT style, COUNT(*) as count
                FROM videos
                GROUP BY style
            """).fetchall()

        return {
            "total_videos": total,
            "successful_videos": successful,
            "failed_videos": total - successful,
            "by_interest": {row["interest"]: row["count"] for row in by_interest},
            "by_style": {row["style"]: row["count"] for row in by_style},
        }
