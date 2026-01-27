"""
Shared pytest fixtures for Math Content Engine tests.

This module provides common fixtures used across multiple test modules.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

# Conditional imports for when package is installed
try:
    from math_content_engine.llm.base import LLMResponse
    from math_content_engine.api.models import (
        VideoCreate,
        AnimationStyle,
        VideoQuality,
    )
    PACKAGE_AVAILABLE = True
except ImportError:
    # Package not installed - fixtures will not be available
    PACKAGE_AVAILABLE = False
    LLMResponse = None
    VideoCreate = None
    AnimationStyle = None
    VideoQuality = None


# Sample valid Manim code for testing
VALID_MANIM_CODE = '''
from manim import *

class TestScene(Scene):
    def construct(self):
        title = Text("Test Animation")
        self.play(Write(title))
        self.wait()
'''


@pytest.fixture
def mock_llm_client():
    """
    Create a mock LLM client that returns valid Manim code.

    Returns:
        Mock: A mock LLM client with generate() method configured.
    """
    if not PACKAGE_AVAILABLE:
        pytest.skip("Package not installed")

    client = Mock()
    client.generate.return_value = LLMResponse(
        content=f"```python\n{VALID_MANIM_CODE}\n```",
        model="test-model",
        usage={"input_tokens": 100, "output_tokens": 200},
    )
    return client


@pytest.fixture
def temp_dir():
    """
    Create a temporary directory for test outputs.

    Yields:
        Path: Path to temporary directory (automatically cleaned up).
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_db(temp_dir):
    """
    Create a temporary database path for API testing.

    Args:
        temp_dir: Temporary directory fixture.

    Returns:
        Path: Path to temporary database file.
    """
    return temp_dir / "test_videos.db"


@pytest.fixture
def sample_video_metadata():
    """
    Create sample video metadata for testing.

    Returns:
        VideoCreate: Sample video creation request.
    """
    if not PACKAGE_AVAILABLE:
        pytest.skip("Package not installed")

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


@pytest.fixture
def api_key_available():
    """
    Check if API keys are available for integration tests.

    Returns:
        bool: True if ANTHROPIC_API_KEY or OPENAI_API_KEY is set.
    """
    return bool(
        os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
    )


@pytest.fixture
def elevenlabs_key_available():
    """
    Check if ElevenLabs API key is available.

    Returns:
        bool: True if ELEVENLABS_API_KEY is set.
    """
    return bool(os.getenv("ELEVENLABS_API_KEY"))


def pytest_configure(config):
    """
    Configure custom pytest markers.

    Args:
        config: Pytest configuration object.
    """
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (rendering videos)"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end (requires API keys)"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "api: marks tests for the video retrieval API"
    )
    config.addinivalue_line(
        "markers", "tts: marks tests for text-to-speech functionality"
    )
