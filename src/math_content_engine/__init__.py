"""
Math Content Engine - Automated math animation generation using Manim + LLM.

Features:
- LLM-powered Manim code generation (Claude, OpenAI)
- Automatic code validation and error fixing
- Content personalization for student interests
- Text-to-Speech narration with neural voices
- Audio-video combination for narrated animations
"""

from .engine import MathContentEngine
from .config import Config

# Personalization components
from .personalization import (
    ContentPersonalizer,
    InterestProfile,
    get_interest_profile,
    list_available_interests,
)

# TTS components (optional - requires edge-tts)
try:
    from .tts import (
        TTSEngine,
        TTSConfig,
        VoiceStyle,
        NarratedAnimationGenerator,
        AnimationScript,
        create_equation_narration,
        create_concept_narration,
    )
    _TTS_AVAILABLE = True
except ImportError:
    _TTS_AVAILABLE = False

__version__ = "0.1.0"

__all__ = [
    "MathContentEngine",
    "Config",
    # Personalization
    "ContentPersonalizer",
    "InterestProfile",
    "get_interest_profile",
    "list_available_interests",
]

if _TTS_AVAILABLE:
    __all__.extend([
        "TTSEngine",
        "TTSConfig",
        "VoiceStyle",
        "NarratedAnimationGenerator",
        "AnimationScript",
        "create_equation_narration",
        "create_concept_narration",
    ])
