"""
Tests for the Video Retrieval API.
"""

import pytest
import tempfile
from pathlib import Path

from math_content_engine.api.models import (
    VideoCreate,
    VideoMetadata,
    VideoResponse,
    VideoSearchParams,
    AnimationStyle,
    VideoQuality,
)
from math_content_engine.api.storage import VideoStorage


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_videos.db"
        yield db_path


@pytest.fixture
def storage(temp_db):
    """Create a storage instance with temporary database."""
    return VideoStorage(temp_db)


@pytest.fixture
def sample_video():
    """Create a sample video for testing."""
    return VideoCreate(
        topic="Pythagorean Theorem",
        scene_name="PythagoreanScene",
        video_path="/path/to/video.mp4",
        code="from manim import *\n\nclass PythagoreanScene(Scene):\n    pass",
        requirements="Show visual proof",
        audience_level="high school",
        interest="basketball",
        style=AnimationStyle.DARK,
        quality=VideoQuality.MEDIUM,
        llm_provider="claude",
        llm_model="claude-sonnet-4-20250514",
        generation_attempts=1,
        render_attempts=1,
        total_attempts=2,
        generation_time_ms=1500,
        render_time_ms=5000,
        file_size_bytes=1024000,
        success=True,
    )


class TestVideoStorage:
    """Tests for VideoStorage."""

    def test_save_and_get(self, storage, sample_video):
        """Test saving and retrieving a video."""
        # Save
        metadata = storage.save(sample_video)

        assert metadata.id is not None
        assert metadata.topic == sample_video.topic
        assert metadata.scene_name == sample_video.scene_name
        assert metadata.success is True

        # Get by ID
        retrieved = storage.get_by_id(metadata.id)

        assert retrieved is not None
        assert retrieved.id == metadata.id
        assert retrieved.topic == sample_video.topic
        assert retrieved.code == sample_video.code

    def test_get_nonexistent(self, storage):
        """Test getting a video that doesn't exist."""
        result = storage.get_by_id("nonexistent-id")
        assert result is None

    def test_list_videos(self, storage, sample_video):
        """Test listing videos with pagination."""
        # Save multiple videos
        for i in range(5):
            video = VideoCreate(
                topic=f"Topic {i}",
                scene_name=f"Scene{i}",
                video_path=f"/path/to/video{i}.mp4",
                code=f"# Code {i}",
            )
            storage.save(video)

        # List all
        videos, total = storage.list_videos()
        assert total == 5
        assert len(videos) == 5

        # List with pagination
        params = VideoSearchParams(page=1, page_size=2)
        videos, total = storage.list_videos(params)
        assert total == 5
        assert len(videos) == 2

    def test_list_with_filter(self, storage):
        """Test listing videos with filters."""
        # Save videos with different interests
        for interest in ["basketball", "basketball", "music"]:
            video = VideoCreate(
                topic=f"Topic with {interest}",
                scene_name="TestScene",
                video_path="/path/to/video.mp4",
                code="# Code",
                interest=interest,
            )
            storage.save(video)

        # Filter by interest
        params = VideoSearchParams(interest="basketball")
        videos, total = storage.list_videos(params)
        assert total == 2

        params = VideoSearchParams(interest="music")
        videos, total = storage.list_videos(params)
        assert total == 1

    def test_delete(self, storage, sample_video):
        """Test deleting a video."""
        metadata = storage.save(sample_video)

        # Delete
        result = storage.delete(metadata.id)
        assert result is True

        # Verify deleted
        retrieved = storage.get_by_id(metadata.id)
        assert retrieved is None

        # Delete nonexistent
        result = storage.delete("nonexistent-id")
        assert result is False

    def test_get_stats(self, storage):
        """Test getting storage statistics."""
        # Save some videos
        for i in range(3):
            storage.save(VideoCreate(
                topic=f"Topic {i}",
                scene_name=f"Scene{i}",
                video_path=f"/path/video{i}.mp4",
                code="# Code",
                interest="basketball" if i < 2 else None,
                style=AnimationStyle.DARK if i == 0 else AnimationStyle.LIGHT,
                success=i != 2,  # One failed
            ))

        stats = storage.get_stats()

        assert stats["total_videos"] == 3
        assert stats["successful_videos"] == 2
        assert stats["failed_videos"] == 1
        assert stats["by_interest"].get("basketball") == 2


class TestVideoModels:
    """Tests for Pydantic models."""

    def test_video_metadata_defaults(self):
        """Test VideoMetadata default values."""
        metadata = VideoMetadata(
            topic="Test",
            scene_name="TestScene",
            video_path="/path/to/video.mp4",
            code="# Code",
        )

        assert metadata.id is not None
        assert metadata.audience_level == "high school"
        assert metadata.style == AnimationStyle.DARK
        assert metadata.quality == VideoQuality.MEDIUM
        assert metadata.success is True

    def test_video_create_to_metadata(self, storage, sample_video):
        """Test converting VideoCreate to VideoMetadata via save."""
        metadata = storage.save(sample_video)

        assert metadata.topic == sample_video.topic
        assert metadata.interest == sample_video.interest
        assert metadata.generation_time_ms == sample_video.generation_time_ms


# Integration test with FastAPI (requires httpx)
@pytest.fixture
def client(temp_db):
    """Create a test client for the API."""
    try:
        from fastapi.testclient import TestClient
        from math_content_engine.api.server import create_app
    except ImportError:
        pytest.skip("FastAPI not installed")

    app = create_app(db_path=temp_db)
    return TestClient(app)


class TestAPIEndpoints:
    """Tests for API endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "endpoints" in response.json()

    def test_create_and_get_video(self, client, sample_video):
        """Test creating and retrieving a video via API."""
        # Create
        response = client.post(
            "/api/v1/videos",
            json=sample_video.model_dump(),
        )
        assert response.status_code == 201
        data = response.json()
        video_id = data["id"]
        assert data["topic"] == sample_video.topic

        # Get
        response = client.get(f"/api/v1/videos/{video_id}")
        assert response.status_code == 200
        assert response.json()["topic"] == sample_video.topic

    def test_get_video_not_found(self, client):
        """Test getting a nonexistent video."""
        response = client.get("/api/v1/videos/nonexistent-id")
        assert response.status_code == 404

    def test_list_videos(self, client, sample_video):
        """Test listing videos."""
        # Create some videos
        for _ in range(3):
            client.post("/api/v1/videos", json=sample_video.model_dump())

        # List
        response = client.get("/api/v1/videos")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["videos"]) == 3

    def test_delete_video(self, client, sample_video):
        """Test deleting a video."""
        # Create
        response = client.post("/api/v1/videos", json=sample_video.model_dump())
        video_id = response.json()["id"]

        # Delete
        response = client.delete(f"/api/v1/videos/{video_id}")
        assert response.status_code == 204

        # Verify deleted
        response = client.get(f"/api/v1/videos/{video_id}")
        assert response.status_code == 404

    def test_get_video_code(self, client, sample_video):
        """Test getting video code."""
        # Create
        response = client.post("/api/v1/videos", json=sample_video.model_dump())
        video_id = response.json()["id"]

        # Get code
        response = client.get(f"/api/v1/videos/{video_id}/code")
        assert response.status_code == 200
        assert response.json()["code"] == sample_video.code

    def test_stats_endpoint(self, client, sample_video):
        """Test stats endpoint."""
        # Create some videos
        for _ in range(2):
            client.post("/api/v1/videos", json=sample_video.model_dump())

        # Get stats
        response = client.get("/api/v1/videos/stats/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total_videos"] == 2
