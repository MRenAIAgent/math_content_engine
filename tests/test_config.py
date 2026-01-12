"""Tests for configuration management."""

import os
import pytest
from pathlib import Path
from math_content_engine.config import Config, LLMProvider, VideoQuality


class TestConfig:
    """Tests for Config class."""

    def test_default_values(self, monkeypatch):
        """Test default configuration values."""
        # Set required API key
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        config = Config()

        assert config.llm_provider == LLMProvider.CLAUDE
        assert config.max_retries == 5
        assert config.temperature == 0.7
        assert config.video_quality == VideoQuality.MEDIUM
        assert config.output_format == "mp4"

    def test_env_override(self, monkeypatch):
        """Test that environment variables override defaults."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("MATH_ENGINE_MAX_RETRIES", "10")
        monkeypatch.setenv("MATH_ENGINE_TEMPERATURE", "0.5")
        monkeypatch.setenv("MATH_ENGINE_VIDEO_QUALITY", "h")

        config = Config()

        assert config.max_retries == 10
        assert config.temperature == 0.5
        assert config.video_quality == VideoQuality.HIGH

    def test_openai_provider(self, monkeypatch):
        """Test OpenAI provider configuration."""
        monkeypatch.setenv("MATH_ENGINE_LLM_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")

        config = Config()

        assert config.llm_provider == LLMProvider.OPENAI
        assert config.get_api_key() == "test-openai-key"
        assert config.get_model() == "gpt-4o"

    def test_claude_provider(self, monkeypatch):
        """Test Claude provider configuration."""
        monkeypatch.setenv("MATH_ENGINE_LLM_PROVIDER", "claude")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-claude-key")

        config = Config()

        assert config.llm_provider == LLMProvider.CLAUDE
        assert config.get_api_key() == "test-claude-key"
        assert "claude" in config.get_model().lower()

    def test_missing_api_key_raises(self, monkeypatch):
        """Test that missing API key raises error."""
        # Clear API keys
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            Config()

    def test_output_dir_created(self, monkeypatch, tmp_path):
        """Test that output directory is created."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        output_dir = tmp_path / "test_output"
        monkeypatch.setenv("MATH_ENGINE_OUTPUT_DIR", str(output_dir))

        config = Config()

        assert output_dir.exists()
        assert config.output_dir == output_dir

    def test_custom_model(self, monkeypatch):
        """Test custom model configuration."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("MATH_ENGINE_CLAUDE_MODEL", "claude-opus-4-20250514")

        config = Config()

        assert config.claude_model == "claude-opus-4-20250514"


class TestVideoQuality:
    """Tests for VideoQuality enum."""

    def test_quality_values(self):
        """Test quality enum values."""
        assert VideoQuality.LOW.value == "l"
        assert VideoQuality.MEDIUM.value == "m"
        assert VideoQuality.HIGH.value == "h"
        assert VideoQuality.PRODUCTION.value == "p"
        assert VideoQuality.FOURK.value == "k"


class TestLLMProvider:
    """Tests for LLMProvider enum."""

    def test_provider_values(self):
        """Test provider enum values."""
        assert LLMProvider.CLAUDE.value == "claude"
        assert LLMProvider.OPENAI.value == "openai"
