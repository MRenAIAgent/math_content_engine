"""
ContentPublisher — publishes content events to Redis Streams.

Events are consumed by the agentic_math_tutor ingestion worker.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from .schemas import (
    ContentEvent,
    ContentEventType,
    ConceptDTO,
    ExerciseDTO,
    VideoContentDTO,
)

logger = logging.getLogger(__name__)


class ContentPublisher:
    """Publishes content events to a Redis Stream for tutor ingestion."""

    def __init__(
        self,
        redis_client,
        stream_name: str = "content_events",
    ):
        self._redis = redis_client
        self._stream = stream_name

    async def publish_video(self, dto: VideoContentDTO) -> Optional[str]:
        """Publish a video_generated event. Returns the stream entry ID."""
        return await self._publish(
            ContentEventType.VIDEO_GENERATED,
            dto.model_dump(),
        )

    async def publish_concept(self, dto: ConceptDTO) -> Optional[str]:
        """Publish a concept_created event."""
        return await self._publish(
            ContentEventType.CONCEPT_CREATED,
            dto.model_dump(),
        )

    async def publish_exercise(self, dto: ExerciseDTO) -> Optional[str]:
        """Publish an exercise_generated event."""
        return await self._publish(
            ContentEventType.EXERCISE_GENERATED,
            dto.model_dump(),
        )

    async def _publish(
        self,
        event_type: ContentEventType,
        payload: dict,
    ) -> Optional[str]:
        """Publish an event to the Redis Stream."""
        event = ContentEvent(
            event_type=event_type,
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            payload=payload,
        )

        try:
            # Redis XADD expects a flat dict of string key-value pairs
            entry_id = await self._redis.xadd(
                self._stream,
                {
                    "event_type": event.event_type.value,
                    "event_id": event.event_id,
                    "timestamp": event.timestamp,
                    "payload": json.dumps(event.payload),
                },
            )
            logger.info(
                "Published %s event %s -> stream entry %s",
                event_type.value,
                event.event_id,
                entry_id,
            )
            return entry_id
        except Exception:
            logger.exception("Failed to publish %s event", event_type.value)
            return None
