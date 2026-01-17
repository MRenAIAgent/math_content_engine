"""SQLite-based session storage for prompt engineering lab."""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from ..prompt.models import PromptSession, AnimationPrompt, GenerationResult


class SessionStorage:
    """SQLite storage for prompt engineering sessions."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize storage with database path."""
        if db_path is None:
            # Default to .lab directory in current working directory
            db_path = Path.cwd() / ".lab" / "sessions.db"

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_sessions_updated
                ON sessions(updated_at DESC);
            """)

    def save(self, session: PromptSession) -> None:
        """Save or update a session."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO sessions (id, data, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    session.session_id,
                    json.dumps(session.to_dict()),
                    session.created_at.isoformat(),
                    session.updated_at.isoformat(),
                ),
            )

    def load(self, session_id: str) -> Optional[PromptSession]:
        """Load a session by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT data FROM sessions WHERE id = ?",
                (session_id,),
            )
            row = cursor.fetchone()
            if row:
                return PromptSession.from_dict(json.loads(row[0]))
            return None

    def delete(self, session_id: str) -> bool:
        """Delete a session. Returns True if deleted."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM sessions WHERE id = ?",
                (session_id,),
            )
            return cursor.rowcount > 0

    def list_sessions(self, limit: int = 20) -> list[dict]:
        """List recent sessions with basic info."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT id, data, updated_at
                FROM sessions
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            )
            results = []
            for row in cursor.fetchall():
                data = json.loads(row[1])
                # Extract summary info
                topic = data.get("working_prompt", {}).get("topic", "")
                if not topic and data.get("history"):
                    topic = data["history"][-1].get("prompt", {}).get("topic", "")

                results.append({
                    "session_id": row[0],
                    "topic": topic,
                    "versions": len(data.get("history", [])),
                    "updated_at": row[2],
                })
            return results

    def search_by_topic(self, query: str, limit: int = 10) -> list[dict]:
        """Search sessions by topic."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT id, data, updated_at
                FROM sessions
                WHERE data LIKE ?
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (f"%{query}%", limit),
            )
            results = []
            for row in cursor.fetchall():
                data = json.loads(row[1])
                topic = data.get("working_prompt", {}).get("topic", "")
                if not topic and data.get("history"):
                    topic = data["history"][-1].get("prompt", {}).get("topic", "")

                # Only include if topic matches
                if query.lower() in topic.lower():
                    results.append({
                        "session_id": row[0],
                        "topic": topic,
                        "versions": len(data.get("history", [])),
                        "updated_at": row[2],
                    })
            return results

    def exists(self, session_id: str) -> bool:
        """Check if a session exists."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM sessions WHERE id = ?",
                (session_id,),
            )
            return cursor.fetchone() is not None
