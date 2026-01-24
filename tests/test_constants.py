"""Tests for centralized constants and enums."""

import pytest
from math_content_engine.constants import (
    LLMProvider,
    VideoQuality,
    AnimationStyle,
    TTSVoice,
    VideoStyle,
    TTSProvider,
)


class TestLLMProvider:
    """Tests for LLMProvider enum."""

    def test_provider_values(self):
        """Test provider enum values."""
        assert LLMProvider.CLAUDE.value == "claude"
        assert LLMProvider.OPENAI.value == "openai"

    def test_from_string(self):
        """Test creating enum from string value."""
        assert LLMProvider("claude") == LLMProvider.CLAUDE
        assert LLMProvider("openai") == LLMProvider.OPENAI

    def test_invalid_value_raises(self):
        """Test that invalid value raises ValueError."""
        with pytest.raises(ValueError):
            LLMProvider("invalid")


class TestVideoQuality:
    """Tests for VideoQuality enum."""

    def test_quality_values(self):
        """Test quality enum values."""
        assert VideoQuality.LOW.value == "l"
        assert VideoQuality.MEDIUM.value == "m"
        assert VideoQuality.HIGH.value == "h"
        assert VideoQuality.PRODUCTION.value == "p"
        assert VideoQuality.FOURK.value == "k"

    def test_from_string(self):
        """Test creating enum from string value."""
        assert VideoQuality("m") == VideoQuality.MEDIUM
        assert VideoQuality("h") == VideoQuality.HIGH

    def test_all_qualities_defined(self):
        """Test that all expected qualities are defined."""
        qualities = [q.value for q in VideoQuality]
        assert set(qualities) == {"l", "m", "h", "p", "k"}


class TestAnimationStyle:
    """Tests for AnimationStyle enum."""

    def test_style_values(self):
        """Test style enum values."""
        assert AnimationStyle.DARK.value == "dark"
        assert AnimationStyle.LIGHT.value == "light"

    def test_from_string(self):
        """Test creating enum from string value."""
        assert AnimationStyle("dark") == AnimationStyle.DARK
        assert AnimationStyle("light") == AnimationStyle.LIGHT

    def test_default_is_dark(self):
        """Test that DARK is available (commonly used default)."""
        assert hasattr(AnimationStyle, "DARK")


class TestTTSVoice:
    """Tests for TTSVoice enum."""

    def test_voice_values(self):
        """Test voice enum values."""
        assert TTSVoice.TEACHER_MALE.value == "teacher_male"
        assert TTSVoice.TEACHER_FEMALE.value == "teacher_female"
        assert TTSVoice.FRIENDLY_MALE.value == "friendly_male"
        assert TTSVoice.FRIENDLY_FEMALE.value == "friendly_female"

    def test_all_voices_defined(self):
        """Test that common voices are defined."""
        voice_values = [v.value for v in TTSVoice]
        assert "teacher_male" in voice_values
        assert "teacher_female" in voice_values
        assert "young_female" in voice_values

    def test_from_string(self):
        """Test creating enum from string value."""
        assert TTSVoice("teacher_male") == TTSVoice.TEACHER_MALE


class TestVideoStyle:
    """Tests for VideoStyle enum."""

    def test_style_values(self):
        """Test style enum values."""
        assert VideoStyle.STANDARD.value == "standard"
        assert VideoStyle.STEP_BY_STEP.value == "step_by_step"
        assert VideoStyle.FAST_PACED.value == "fast_paced"
        assert VideoStyle.DETAILED.value == "detailed"

    def test_from_string(self):
        """Test creating enum from string value."""
        assert VideoStyle("standard") == VideoStyle.STANDARD
        assert VideoStyle("step_by_step") == VideoStyle.STEP_BY_STEP

    def test_all_styles_defined(self):
        """Test that all styles are defined."""
        styles = [s.value for s in VideoStyle]
        assert "standard" in styles
        assert "step_by_step" in styles
        assert "fast_paced" in styles
        assert "detailed" in styles


class TestTTSProvider:
    """Tests for TTSProvider enum."""

    def test_provider_values(self):
        """Test provider enum values."""
        assert TTSProvider.EDGE.value == "edge"
        assert TTSProvider.ELEVENLABS.value == "elevenlabs"

    def test_from_string(self):
        """Test creating enum from string value."""
        assert TTSProvider("edge") == TTSProvider.EDGE
        assert TTSProvider("elevenlabs") == TTSProvider.ELEVENLABS

    def test_default_is_edge(self):
        """Test that EDGE is available (free default)."""
        assert hasattr(TTSProvider, "EDGE")


class TestEnumConsistency:
    """Tests for enum consistency across codebase."""

    def test_no_duplicate_values(self):
        """Test that each enum has unique values."""
        # LLMProvider
        llm_values = [p.value for p in LLMProvider]
        assert len(llm_values) == len(set(llm_values))

        # VideoQuality
        quality_values = [q.value for q in VideoQuality]
        assert len(quality_values) == len(set(quality_values))

        # AnimationStyle
        style_values = [s.value for s in AnimationStyle]
        assert len(style_values) == len(set(style_values))

    def test_backward_compatibility_with_config(self):
        """Test that enums can be imported from config module."""
        from math_content_engine.config import (
            LLMProvider as ConfigLLMProvider,
            VideoQuality as ConfigVideoQuality,
            AnimationStyle as ConfigAnimationStyle,
        )

        # Should be the same classes (not copies)
        assert ConfigLLMProvider is LLMProvider
        assert ConfigVideoQuality is VideoQuality
        assert ConfigAnimationStyle is AnimationStyle

    def test_backward_compatibility_with_prompts(self):
        """Test that AnimationStyle can be imported from prompts module."""
        from math_content_engine.generator.prompts import (
            AnimationStyle as PromptsAnimationStyle,
        )

        # Should be the same class
        assert PromptsAnimationStyle is AnimationStyle
