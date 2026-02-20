"""
Centralized enum definitions for the math content engine.

This module provides a single source of truth for all enums used throughout
the codebase, preventing duplication and inconsistencies.
"""

from enum import Enum


class LLMProvider(Enum):
    """Supported LLM providers."""
    CLAUDE = "claude"
    OPENAI = "openai"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"


class VideoQuality(Enum):
    """Manim video quality presets."""
    LOW = "l"          # 480p, 15fps
    MEDIUM = "m"       # 720p, 30fps
    HIGH = "h"         # 1080p, 60fps
    PRODUCTION = "p"   # 1440p, 60fps
    FOURK = "k"        # 4K, 60fps


class AnimationStyle(Enum):
    """Animation visual style presets."""
    DARK = "dark"    # Dark background (default Manim style)
    LIGHT = "light"  # Light/white background


class TTSVoice(Enum):
    """TTS voice options (maps to edge-tts voices)."""
    TEACHER_MALE = "teacher_male"
    TEACHER_FEMALE = "teacher_female"
    FRIENDLY_MALE = "friendly_male"
    FRIENDLY_FEMALE = "friendly_female"
    PROFESSIONAL_MALE = "professional_male"
    PROFESSIONAL_FEMALE = "professional_female"
    CARING_MALE = "caring_male"
    CARING_FEMALE = "caring_female"
    YOUNG_FEMALE = "young_female"


class VideoStyle(Enum):
    """Video presentation style for educational content."""
    STANDARD = "standard"          # Standard animation flow
    STEP_BY_STEP = "step_by_step"  # Clear step-by-step with pauses
    FAST_PACED = "fast_paced"      # Quick transitions
    DETAILED = "detailed"          # Detailed explanations with extra visuals


class TTSProvider(Enum):
    """Text-to-speech provider options."""
    EDGE = "edge"            # Microsoft Edge TTS (free)
    ELEVENLABS = "elevenlabs"  # ElevenLabs (requires API key)
