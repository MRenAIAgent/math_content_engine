"""
Text-to-Speech module for math content narration.

Provides high-quality neural voice narration for math animations.
Uses Microsoft Edge TTS (no API key required).

Example:
    >>> from math_content_engine.tts import (
    ...     TTSEngine, VoiceStyle, NarratedAnimationGenerator, AnimationScript
    ... )
    >>>
    >>> # Simple TTS
    >>> tts = TTSEngine()
    >>> audio = tts.generate("Hello, let's learn math!")
    >>>
    >>> # Narrated animation
    >>> generator = NarratedAnimationGenerator(voice=VoiceStyle.TEACHER_FEMALE)
    >>> script = AnimationScript("Linear Equations")
    >>> script.add_intro("Let's solve 2x + 3 = 7")
    >>> script.add_step("Subtract 3 from both sides", time=3.0)
    >>> result = generator.create_narrated_video(video_path, script, output_path)
"""

from .tts_engine import TTSEngine, TTSConfig, VoiceStyle, NarrationScript, NarrationSegment
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
