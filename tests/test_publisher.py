"""
Tests for ContentPublisher -- Redis stream publishing.

Uses mock Redis client to test without requiring a real Redis instance.
"""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from math_content_engine.integration.publisher import ContentPublisher
from math_content_engine.integration.schemas import (
    ConceptDTO,
    ExerciseDTO,
    VideoContentDTO,
)


@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    redis = AsyncMock()
    redis.xadd = AsyncMock(return_value="1234567890-0")
    return redis


@pytest.fixture
def publisher(mock_redis):
    """Create a ContentPublisher with mock Redis."""
    return ContentPublisher(redis_client=mock_redis)


@pytest.fixture
def video_dto(sample_video_dto_data):
    """Create a VideoContentDTO from sample data."""
    return VideoContentDTO(**sample_video_dto_data)


@pytest.fixture
def concept_dto(sample_concept_dto_data):
    """Create a ConceptDTO from sample data."""
    return ConceptDTO(**sample_concept_dto_data)


@pytest.fixture
def exercise_dto(sample_exercise_dto_data):
    """Create an ExerciseDTO from sample data."""
    return ExerciseDTO(**sample_exercise_dto_data)


class TestPublishVideo:
    """Tests for publish_video method."""

    @pytest.mark.asyncio
    async def test_publish_video_calls_xadd(self, publisher, mock_redis, video_dto):
        """publish_video should call redis.xadd with correct stream name."""
        await publisher.publish_video(video_dto)

        mock_redis.xadd.assert_called_once()
        call_args = mock_redis.xadd.call_args
        assert call_args[0][0] == "content_events"  # Stream name

    @pytest.mark.asyncio
    async def test_publish_video_event_structure(self, publisher, mock_redis, video_dto):
        """Verify published event has correct structure: event_type, event_id, timestamp, payload."""
        await publisher.publish_video(video_dto)

        call_args = mock_redis.xadd.call_args
        event_data = call_args[0][1]

        # Check all required fields are present
        assert "event_type" in event_data
        assert "event_id" in event_data
        assert "timestamp" in event_data
        assert "payload" in event_data

        # Check event_type is correct
        assert event_data["event_type"] == "video_generated"

        # Check event_id is a UUID string
        assert len(event_data["event_id"]) == 36  # UUID format

        # Check timestamp is ISO format
        assert "T" in event_data["timestamp"]  # ISO 8601 format includes T

    @pytest.mark.asyncio
    async def test_publish_video_payload_is_json(self, publisher, mock_redis, video_dto):
        """Payload should be json.dumps of dto.model_dump()."""
        await publisher.publish_video(video_dto)

        call_args = mock_redis.xadd.call_args
        event_data = call_args[0][1]
        payload_str = event_data["payload"]

        # Payload should be valid JSON
        payload = json.loads(payload_str)

        # Should match the DTO data
        assert payload["video_id"] == video_dto.video_id
        assert payload["concept_ids"] == video_dto.concept_ids
        assert payload["topic"] == video_dto.topic
        assert payload["scene_name"] == video_dto.scene_name
        assert payload["theme"] == video_dto.theme

    @pytest.mark.asyncio
    async def test_publish_video_returns_stream_entry_id(self, publisher, mock_redis, video_dto):
        """publish_video should return the stream entry ID."""
        result = await publisher.publish_video(video_dto)
        assert result == "1234567890-0"


class TestPublishConcept:
    """Tests for publish_concept method."""

    @pytest.mark.asyncio
    async def test_publish_concept_event_type(self, publisher, mock_redis, concept_dto):
        """Event type should be 'concept_created'."""
        await publisher.publish_concept(concept_dto)

        call_args = mock_redis.xadd.call_args
        event_data = call_args[0][1]
        assert event_data["event_type"] == "concept_created"

    @pytest.mark.asyncio
    async def test_publish_concept_payload(self, publisher, mock_redis, concept_dto):
        """Concept payload should contain concept data."""
        await publisher.publish_concept(concept_dto)

        call_args = mock_redis.xadd.call_args
        event_data = call_args[0][1]
        payload = json.loads(event_data["payload"])

        assert payload["concept_id"] == concept_dto.concept_id
        assert payload["name"] == concept_dto.name
        assert payload["difficulty"] == concept_dto.difficulty

    @pytest.mark.asyncio
    async def test_publish_concept_returns_entry_id(self, publisher, mock_redis, concept_dto):
        """publish_concept should return the stream entry ID."""
        result = await publisher.publish_concept(concept_dto)
        assert result == "1234567890-0"


class TestPublishExercise:
    """Tests for publish_exercise method."""

    @pytest.mark.asyncio
    async def test_publish_exercise_event_type(self, publisher, mock_redis, exercise_dto):
        """Event type should be 'exercise_generated'."""
        await publisher.publish_exercise(exercise_dto)

        call_args = mock_redis.xadd.call_args
        event_data = call_args[0][1]
        assert event_data["event_type"] == "exercise_generated"

    @pytest.mark.asyncio
    async def test_publish_exercise_payload(self, publisher, mock_redis, exercise_dto):
        """Exercise payload should contain exercise data."""
        await publisher.publish_exercise(exercise_dto)

        call_args = mock_redis.xadd.call_args
        event_data = call_args[0][1]
        payload = json.loads(event_data["payload"])

        assert payload["exercise_id"] == exercise_dto.exercise_id
        assert payload["title"] == exercise_dto.title
        assert payload["difficulty"] == exercise_dto.difficulty

    @pytest.mark.asyncio
    async def test_publish_exercise_returns_entry_id(self, publisher, mock_redis, exercise_dto):
        """publish_exercise should return the stream entry ID."""
        result = await publisher.publish_exercise(exercise_dto)
        assert result == "1234567890-0"


class TestPublisherErrorHandling:
    """Tests for error handling in ContentPublisher."""

    @pytest.mark.asyncio
    async def test_publish_handles_redis_error(self, mock_redis, video_dto):
        """When xadd raises exception, should return None."""
        mock_redis.xadd = AsyncMock(side_effect=Exception("Redis connection failed"))
        publisher = ContentPublisher(redis_client=mock_redis)

        result = await publisher.publish_video(video_dto)
        assert result is None

    @pytest.mark.asyncio
    async def test_publish_handles_connection_error(self, mock_redis, concept_dto):
        """Connection errors should be handled gracefully."""
        mock_redis.xadd = AsyncMock(side_effect=ConnectionError("Connection refused"))
        publisher = ContentPublisher(redis_client=mock_redis)

        result = await publisher.publish_concept(concept_dto)
        assert result is None

    @pytest.mark.asyncio
    async def test_publish_handles_timeout_error(self, mock_redis, exercise_dto):
        """Timeout errors should be handled gracefully."""
        mock_redis.xadd = AsyncMock(side_effect=TimeoutError("Operation timed out"))
        publisher = ContentPublisher(redis_client=mock_redis)

        result = await publisher.publish_exercise(exercise_dto)
        assert result is None


class TestPublisherConfiguration:
    """Tests for ContentPublisher configuration."""

    def test_publisher_uses_correct_stream_name(self, mock_redis):
        """Default stream name should be 'content_events'."""
        publisher = ContentPublisher(redis_client=mock_redis)
        assert publisher._stream == "content_events"

    def test_publisher_custom_stream_name(self, mock_redis):
        """Publisher should accept custom stream name."""
        publisher = ContentPublisher(
            redis_client=mock_redis,
            stream_name="custom_stream",
        )
        assert publisher._stream == "custom_stream"

    @pytest.mark.asyncio
    async def test_custom_stream_name_used_in_xadd(self, mock_redis, video_dto):
        """Custom stream name should be passed to xadd."""
        publisher = ContentPublisher(
            redis_client=mock_redis,
            stream_name="my_custom_stream",
        )
        await publisher.publish_video(video_dto)

        call_args = mock_redis.xadd.call_args
        assert call_args[0][0] == "my_custom_stream"

    def test_publisher_stores_redis_client(self, mock_redis):
        """Publisher should store the Redis client reference."""
        publisher = ContentPublisher(redis_client=mock_redis)
        assert publisher._redis is mock_redis


class TestEventIdGeneration:
    """Tests for event ID generation."""

    @pytest.mark.asyncio
    async def test_event_ids_are_unique(self, mock_redis, video_dto):
        """Each publish call should generate a unique event ID."""
        publisher = ContentPublisher(redis_client=mock_redis)

        event_ids = set()
        for _ in range(10):
            await publisher.publish_video(video_dto)
            call_args = mock_redis.xadd.call_args
            event_data = call_args[0][1]
            event_ids.add(event_data["event_id"])

        assert len(event_ids) == 10, "All event IDs should be unique"

    @pytest.mark.asyncio
    async def test_event_id_is_valid_uuid(self, publisher, mock_redis, video_dto):
        """Event ID should be a valid UUID4."""
        import uuid

        await publisher.publish_video(video_dto)

        call_args = mock_redis.xadd.call_args
        event_data = call_args[0][1]
        event_id = event_data["event_id"]

        # Should not raise ValueError if valid UUID
        parsed_uuid = uuid.UUID(event_id)
        assert str(parsed_uuid) == event_id


class TestTimestampGeneration:
    """Tests for timestamp generation."""

    @pytest.mark.asyncio
    async def test_timestamp_is_iso_format(self, publisher, mock_redis, video_dto):
        """Timestamp should be in ISO 8601 format."""
        from datetime import datetime

        await publisher.publish_video(video_dto)

        call_args = mock_redis.xadd.call_args
        event_data = call_args[0][1]
        timestamp = event_data["timestamp"]

        # Should be parseable as ISO format
        # The timestamp includes timezone info (+00:00 or Z)
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        assert parsed is not None

    @pytest.mark.asyncio
    async def test_timestamp_is_utc(self, publisher, mock_redis, video_dto):
        """Timestamp should be in UTC timezone."""
        await publisher.publish_video(video_dto)

        call_args = mock_redis.xadd.call_args
        event_data = call_args[0][1]
        timestamp = event_data["timestamp"]

        # UTC timestamps typically end with +00:00 or Z
        assert "+00:00" in timestamp or timestamp.endswith("Z")


class TestMultiplePublishCalls:
    """Tests for multiple sequential publish calls."""

    @pytest.mark.asyncio
    async def test_multiple_video_publishes(self, publisher, mock_redis, video_dto):
        """Multiple video publishes should all succeed."""
        results = []
        for _ in range(5):
            result = await publisher.publish_video(video_dto)
            results.append(result)

        assert all(r == "1234567890-0" for r in results)
        assert mock_redis.xadd.call_count == 5

    @pytest.mark.asyncio
    async def test_mixed_content_type_publishes(
        self, publisher, mock_redis, video_dto, concept_dto, exercise_dto
    ):
        """Publishing different content types should all work."""
        video_result = await publisher.publish_video(video_dto)
        concept_result = await publisher.publish_concept(concept_dto)
        exercise_result = await publisher.publish_exercise(exercise_dto)

        assert video_result == "1234567890-0"
        assert concept_result == "1234567890-0"
        assert exercise_result == "1234567890-0"
        assert mock_redis.xadd.call_count == 3

        # Verify each call had the correct event type
        calls = mock_redis.xadd.call_args_list
        assert calls[0][0][1]["event_type"] == "video_generated"
        assert calls[1][0][1]["event_type"] == "concept_created"
        assert calls[2][0][1]["event_type"] == "exercise_generated"
