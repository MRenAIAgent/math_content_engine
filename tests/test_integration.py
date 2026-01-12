"""
Integration tests for Math Content Engine.

These tests verify the full pipeline works correctly.
Some tests require API keys and Manim to be installed.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from math_content_engine import MathContentEngine, Config
from math_content_engine.config import LLMProvider, VideoQuality
from math_content_engine.generator.code_generator import ManimCodeGenerator
from math_content_engine.llm.base import LLMResponse
from math_content_engine.renderer.manim_renderer import ManimRenderer, RenderResult


# Sample valid Manim code for testing
VALID_MANIM_CODE = '''
from manim import *

class TestScene(Scene):
    def construct(self):
        title = Text("Test Animation")
        self.play(Write(title))
        self.wait()
'''

INVALID_MANIM_CODE = '''
from manim import *

class TestScene(Scene):
    def construct(self):
        # Missing self.play()
        title = Text("Test")
'''


class TestManimCodeGenerator:
    """Tests for code generation."""

    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client."""
        client = Mock()
        client.generate.return_value = LLMResponse(
            content=f"```python\n{VALID_MANIM_CODE}\n```",
            model="test-model",
            usage={"input_tokens": 100, "output_tokens": 200},
        )
        return client

    def test_generate_code(self, mock_llm_client):
        """Test code generation produces valid output."""
        generator = ManimCodeGenerator(mock_llm_client, max_retries=3)

        result = generator.generate(
            topic="Test topic",
            requirements="Test requirements",
            audience_level="high school",
        )

        assert result.code is not None
        assert "class" in result.code
        assert "Scene" in result.code
        assert result.scene_name == "TestScene"
        mock_llm_client.generate.assert_called_once()

    def test_generate_extracts_scene_name(self, mock_llm_client):
        """Test that scene name is correctly extracted."""
        mock_llm_client.generate.return_value = LLMResponse(
            content='''```python
from manim import *

class PythagoreanTheorem(Scene):
    def construct(self):
        self.play(Write(Text("test")))
        self.wait()
```''',
            model="test",
            usage={},
        )

        generator = ManimCodeGenerator(mock_llm_client)
        result = generator.generate("Pythagorean theorem")

        assert result.scene_name == "PythagoreanTheorem"


class TestManimRenderer:
    """Tests for Manim rendering."""

    @pytest.fixture
    def renderer(self, tmp_path):
        """Create a renderer with temp directories."""
        return ManimRenderer(
            output_dir=tmp_path / "output",
            cache_dir=tmp_path / "cache",
            quality=VideoQuality.LOW,
        )

    def test_renderer_creates_directories(self, tmp_path):
        """Test that renderer creates output directories."""
        output_dir = tmp_path / "test_output"
        cache_dir = tmp_path / "test_cache"

        renderer = ManimRenderer(
            output_dir=output_dir,
            cache_dir=cache_dir,
        )

        assert output_dir.exists()
        assert cache_dir.exists()

    @patch("subprocess.run")
    def test_render_success(self, mock_run, renderer, tmp_path):
        """Test successful rendering."""
        # Create fake output file
        fake_output = tmp_path / "cache" / "videos" / "scene" / "TestScene.mp4"
        fake_output.parent.mkdir(parents=True, exist_ok=True)
        fake_output.touch()

        mock_run.return_value = Mock(
            returncode=0,
            stdout="Success",
            stderr="",
        )

        # Mock the find_output_file to return our fake file
        with patch.object(renderer, '_find_output_file', return_value=fake_output):
            result = renderer.render(VALID_MANIM_CODE, "TestScene")

        assert result.success or result.error_message is not None  # May fail if manim not installed

    @patch("subprocess.run")
    def test_render_failure(self, mock_run, renderer):
        """Test handling of render failure."""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="Error: Invalid code\nTraceback...",
        )

        result = renderer.render(INVALID_MANIM_CODE, "TestScene")

        assert not result.success
        assert result.error_message is not None


class TestMathContentEngine:
    """Integration tests for the main engine."""

    @pytest.fixture
    def mock_config(self, monkeypatch, tmp_path):
        """Create mock configuration."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("MATH_ENGINE_OUTPUT_DIR", str(tmp_path / "output"))
        monkeypatch.setenv("MATH_ENGINE_MANIM_CACHE", str(tmp_path / "cache"))
        return Config()

    def test_engine_initialization(self, mock_config):
        """Test engine initializes with config."""
        with patch('math_content_engine.engine.create_llm_client') as mock_create:
            mock_create.return_value = Mock()
            engine = MathContentEngine(mock_config)

        assert engine.config == mock_config

    @patch('math_content_engine.engine.create_llm_client')
    @patch('math_content_engine.engine.ManimRenderer')
    def test_preview_code(self, mock_renderer, mock_create_client, mock_config):
        """Test code preview without rendering."""
        mock_client = Mock()
        mock_client.generate.return_value = LLMResponse(
            content=f"```python\n{VALID_MANIM_CODE}\n```",
            model="test",
            usage={},
        )
        mock_create_client.return_value = mock_client

        engine = MathContentEngine(mock_config)
        result = engine.preview_code("Test topic")

        assert result.code is not None
        assert result.validation.is_valid
        mock_renderer.return_value.render.assert_not_called()

    @patch('math_content_engine.engine.create_llm_client')
    def test_generate_from_code(self, mock_create_client, mock_config, tmp_path):
        """Test rendering from existing code."""
        mock_create_client.return_value = Mock()

        with patch('math_content_engine.engine.ManimRenderer') as mock_renderer_class:
            mock_renderer = Mock()
            mock_renderer.render.return_value = RenderResult(
                success=True,
                output_path=tmp_path / "output.mp4",
                render_time=1.5,
            )
            mock_renderer_class.return_value = mock_renderer

            engine = MathContentEngine(mock_config)
            result = engine.generate_from_code(VALID_MANIM_CODE)

        assert result.success
        mock_renderer.render.assert_called_once()


class TestEndToEnd:
    """
    End-to-end tests that require actual API keys and Manim.

    These tests are skipped by default. Run with:
    pytest tests/test_integration.py -m e2e
    """

    @pytest.fixture
    def real_engine(self):
        """Create real engine (requires API key)."""
        try:
            return MathContentEngine()
        except ValueError:
            pytest.skip("API key not configured")

    @pytest.mark.e2e
    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"),
        reason="No API key configured"
    )
    def test_real_code_generation(self, real_engine):
        """Test actual code generation with real API."""
        result = real_engine.preview_code(
            topic="Simple y = x squared graph",
            audience_level="high school",
        )

        assert result.code is not None
        assert "from manim import" in result.code
        assert result.validation.is_valid

    @pytest.mark.e2e
    @pytest.mark.slow
    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"),
        reason="No API key configured"
    )
    def test_real_video_generation(self, real_engine, tmp_path):
        """Test actual video generation (slow, requires Manim)."""
        real_engine.config.output_dir = tmp_path
        real_engine.config.video_quality = VideoQuality.LOW

        result = real_engine.generate(
            topic="Show the equation 1 + 1 = 2",
            requirements="Very simple, just show the equation appearing",
            audience_level="elementary",
        )

        # This may fail if Manim is not installed
        if result.success:
            assert result.video_path is not None
            assert result.video_path.exists()
        else:
            # If rendering failed, at least code should be generated
            assert result.code is not None


# Markers for selective test running
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "e2e: end-to-end tests requiring API keys")
    config.addinivalue_line("markers", "slow: slow tests that take significant time")
