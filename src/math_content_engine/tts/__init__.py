"""
Text-to-Speech module for math content narration.

Provides high-quality neural voice narration for math animations.
Supports multiple TTS providers:
- Edge TTS (free, no API key required)
- ElevenLabs (requires API key, premium quality)

Example:
    >>> from math_content_engine.tts import (
    ...     TTSEngine, VoiceStyle, NarratedAnimationGenerator, AnimationScript,
    ...     create_tts_provider
    ... )
    >>>
    >>> # Simple TTS with default provider (Edge TTS)
    >>> tts = TTSEngine()
    >>> audio = tts.generate("Hello, let's learn math!")
    >>>
    >>> # With ElevenLabs
    >>> from math_content_engine import Config
    >>> from math_content_engine.config import TTSProvider
    >>> import os
    >>> os.environ["ELEVENLABS_API_KEY"] = "your-key"
    >>> os.environ["MATH_ENGINE_TTS_PROVIDER"] = "elevenlabs"
    >>> config = Config()
    >>> provider = create_tts_provider(config)
    >>> tts = TTSEngine(provider=provider)
    >>>
    >>> # Narrated animation
    >>> generator = NarratedAnimationGenerator(voice=VoiceStyle.TEACHER_FEMALE)
    >>> script = AnimationScript("Linear Equations")
    >>> script.add_intro("Let's solve 2x + 3 = 7")
    >>> script.add_step("Subtract 3 from both sides", time=3.0)
    >>> result = generator.create_narrated_video(video_path, script, output_path)
"""

from .tts_engine import TTSEngine, TTSConfig, NarrationScript, NarrationSegment
from .edge_tts_provider import VoiceStyle, EdgeTTSConfig, EdgeTTSProvider
from .elevenlabs_provider import (
    ElevenLabsVoice,
    ElevenLabsConfig,
    ElevenLabsTTSProvider,
)
from .base_provider import BaseTTSProvider, TTSProviderConfig
from .provider_factory import create_tts_provider
from .audio_video_combiner import AudioVideoCombiner, AudioSegment, CombineResult
from .narrated_animation import (
    NarratedAnimationGenerator,
    AnimationScript,
    NarrationCue,
    NarratedAnimationResult,
    create_equation_narration,
    create_concept_narration,
)
from .narration_generator import (
    NarrationScriptGenerator,
    GeneratedNarrationScript,
    NarrationCueGenerated,
    convert_script_to_animation_script,
)

__all__ = [
    # TTS Engine
    "TTSEngine",
    "TTSConfig",
    "VoiceStyle",
    "NarrationScript",
    "NarrationSegment",

    # TTS Providers
    "BaseTTSProvider",
    "TTSProviderConfig",
    "EdgeTTSProvider",
    "EdgeTTSConfig",
    "ElevenLabsTTSProvider",
    "ElevenLabsConfig",
    "ElevenLabsVoice",
    "create_tts_provider",

    # Audio-Video Combiner
    "AudioVideoCombiner",
    "AudioSegment",
    "CombineResult",

    # Narrated Animation
    "NarratedAnimationGenerator",
    "AnimationScript",
    "NarrationCue",
    "NarratedAnimationResult",

    # LLM Narration Generator
    "NarrationScriptGenerator",
    "GeneratedNarrationScript",
    "NarrationCueGenerated",
    "convert_script_to_animation_script",

    # Convenience functions
    "create_equation_narration",
    "create_concept_narration",
]
