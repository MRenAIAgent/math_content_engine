"""
GCP Cloud Storage backend for saving and loading tuned prompt sessions.

Each save creates a timestamped snapshot under ``prompts/history/`` and
overwrites ``prompts/current.json`` so the playground always loads the
latest version.

File layout inside the bucket::

    prompts/
      current.json                        ← always the latest version
      history/
        2026-02-17T23-15-44Z.json        ← timestamped snapshots
        2026-02-17T22-30-12Z.json
        ...
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

CURRENT_KEY = "prompts/current.json"
HISTORY_PREFIX = "prompts/history/"


class GCSPromptStorage:
    """Manages prompt-session persistence in a GCS bucket."""

    def __init__(self, bucket_name: str, project_id: Optional[str] = None):
        self.bucket_name = bucket_name
        self.project_id = project_id
        self._client = None
        self._bucket = None

    # ------------------------------------------------------------------
    # Lazy initialisation (so importing the module is cheap)
    # ------------------------------------------------------------------

    def _get_bucket(self):
        if self._bucket is None:
            from google.cloud import storage as gcs

            self._client = gcs.Client(project=self.project_id)
            self._bucket = self._client.bucket(self.bucket_name)
            logger.info(
                "GCS prompt storage initialised: bucket=%s project=%s",
                self.bucket_name,
                self.project_id,
            )
        return self._bucket

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Persist the current prompt session.

        1. Stamp ``saved_at`` into *data*.
        2. Write ``prompts/history/{timestamp}.json``.
        3. Overwrite ``prompts/current.json`` with the same content.

        Returns ``{"saved_at": ..., "path": "gs://..."}``
        """
        bucket = self._get_bucket()
        now = datetime.now(timezone.utc)
        ts = now.strftime("%Y-%m-%dT%H-%M-%SZ")
        data["saved_at"] = now.isoformat()

        payload = json.dumps(data, indent=2, ensure_ascii=False)

        # 1. History snapshot
        history_path = f"{HISTORY_PREFIX}{ts}.json"
        bucket.blob(history_path).upload_from_string(
            payload, content_type="application/json"
        )

        # 2. Overwrite current
        bucket.blob(CURRENT_KEY).upload_from_string(
            payload, content_type="application/json"
        )

        gcs_uri = f"gs://{self.bucket_name}/{history_path}"
        logger.info("Prompt session saved: %s", gcs_uri)
        return {"saved_at": now.isoformat(), "path": gcs_uri}

    def load_latest(self) -> Optional[Dict[str, Any]]:
        """Load the latest saved prompt session (``current.json``).

        Returns ``None`` if no session has been saved yet.
        """
        bucket = self._get_bucket()
        blob = bucket.blob(CURRENT_KEY)
        if not blob.exists():
            return None
        raw = blob.download_as_text()
        return json.loads(raw)

    def list_history(self, limit: int = 20) -> List[Dict[str, str]]:
        """List saved history entries, newest first.

        Returns a list of ``{"timestamp": ..., "path": "gs://..."}``
        dicts, capped at *limit* entries.
        """
        bucket = self._get_bucket()
        blobs = list(
            self._client.list_blobs(
                bucket, prefix=HISTORY_PREFIX, max_results=200
            )
        )
        # Sort newest first by name (ISO timestamps sort lexicographically)
        blobs.sort(key=lambda b: b.name, reverse=True)

        result: List[Dict[str, str]] = []
        for blob in blobs[:limit]:
            name = blob.name.removeprefix(HISTORY_PREFIX).removesuffix(".json")
            result.append(
                {
                    "timestamp": name,
                    "path": f"gs://{self.bucket_name}/{blob.name}",
                    "size": blob.size,
                }
            )
        return result

    def load_version(self, timestamp: str) -> Optional[Dict[str, Any]]:
        """Load a specific historical version by its timestamp string.

        The *timestamp* should match the filename stem, e.g.
        ``2026-02-17T23-15-44Z``.
        """
        bucket = self._get_bucket()
        blob = bucket.blob(f"{HISTORY_PREFIX}{timestamp}.json")
        if not blob.exists():
            return None
        raw = blob.download_as_text()
        return json.loads(raw)
