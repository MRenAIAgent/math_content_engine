"""SQLite KV store for engagement profiles.

Follows the same pattern as ``SessionStorage`` in
``math_content_engine.lab.session.storage`` — a simple key/value table
where the value is the JSON-serialised ``EngagementProfile`` dict.

Key convention:
    ``"{student_name}:{interest}"``  — e.g. ``"jordan:basketball"``
    ``"anonymous:{interest}"``       — when no student name is available
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .engagement_profile import EngagementProfile


class EngagementStore:
    """Persist and retrieve engagement profiles in a local SQLite database."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        if db_path is None:
            db_path = Path.cwd() / "data" / "engagement.db"

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS engagement_profiles (
                    key         TEXT PRIMARY KEY,
                    data        TEXT NOT NULL,
                    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_engagement_updated
                ON engagement_profiles(updated_at DESC);
            """)

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def save(self, key: str, profile: EngagementProfile) -> None:
        """Insert or update a profile."""
        now = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO engagement_profiles
                    (key, data, created_at, updated_at)
                VALUES (?, ?, COALESCE(
                    (SELECT created_at FROM engagement_profiles WHERE key = ?),
                    ?
                ), ?)
                """,
                (key, json.dumps(profile), key, now, now),
            )

    def load(self, key: str) -> Optional[EngagementProfile]:
        """Load a profile by key.  Returns ``None`` if not found."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT data FROM engagement_profiles WHERE key = ?",
                (key,),
            )
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None

    def delete(self, key: str) -> bool:
        """Delete a profile.  Returns ``True`` if a row was removed."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM engagement_profiles WHERE key = ?",
                (key,),
            )
            return cursor.rowcount > 0

    def list_profiles(self, limit: int = 20) -> list[dict]:
        """List recently-updated profiles (summary only)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT key, data, updated_at
                FROM engagement_profiles
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            )
            results: list[dict] = []
            for row in cursor.fetchall():
                data = json.loads(row[1])
                results.append({
                    "key": row[0],
                    "address": data.get("address", "you"),
                    "student_name": data.get("student_name"),
                    "updated_at": row[2],
                })
            return results

    def exists(self, key: str) -> bool:
        """Check whether a profile with the given key exists."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM engagement_profiles WHERE key = ?",
                (key,),
            )
            return cursor.fetchone() is not None


def make_store_key(
    interest: str,
    student_name: Optional[str] = None,
) -> str:
    """Build a canonical store key from an interest and optional student name.

    Examples:
        ``make_store_key("basketball", "jordan")``  → ``"jordan:basketball"``
        ``make_store_key("basketball")``             → ``"anonymous:basketball"``
    """
    name_part = student_name.strip().lower() if student_name else "anonymous"
    return f"{name_part}:{interest.strip().lower()}"
