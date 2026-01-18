"""
Narrated animation generator - combines Manim animations with TTS narration.

This module provides a high-level interface for creating educational math
animations with voice narration.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .tts_engine import TTSEngine, TTSConfig, VoiceStyle
from .audio_video_combiner import AudioVideoCombiner, AudioSegment, CombineResult

logger = logging.getLogger(__name__)


@dataclass
class NarrationCue:
    """A single narration cue with text and timing."""

    text: str
    time: float            # Time in seconds when narration starts
    pause_after: float = 0.5  # Pause after this narration (seconds)


@dataclass
class AnimationScript:
    """
    Script for a narrated animation.

    Contains the narration cues and timing information.
    """

    title: str
    cues: List[NarrationCue] = field(default_factory=list)

    def add_cue(self, text: str, time: float, pause_after: float = 0.5) -> "AnimationScript":
        """Add a narration cue. Returns self for chaining."""
        self.cues.append(NarrationCue(text=text, time=time, pause_after=pause_after))
        return self

    def add_intro(self, text: str) -> "AnimationScript":
        """Add introduction narration at time 0."""
        return self.add_cue(text, time=0.0, pause_after=1.0)

    def add_step(self, text: str, time: float) -> "AnimationScript":
        """Add a step explanation."""
        return self.add_cue(text, time=time, pause_after=0.5)

    def add_conclusion(self, text: str, time: float) -> "AnimationScript":
        """Add conclusion narration."""
        return self.add_cue(text, time=time, pause_after=1.0)


@dataclass
class NarratedAnimationResult:
    """Result of narrated animation generation."""

    success: bool
    video_path: Optional[Path]
    audio_paths: List[Path] = field(default_factory=list)
    error_message: Optional[str] = None
    script: Optional[AnimationScript] = None


class NarratedAnimationGenerator:
    """
    Generates narrated math animations by combining:
    1. Manim animation video
    2. TTS voice narration

    Example:
        >>> generator = NarratedAnimationGenerator(voice=VoiceStyle.TEACHER_FEMALE)
        >>>
        >>> script = AnimationScript("Linear Equation")
        >>> script.add_intro("Let's solve the equation 2x plus 3 equals 7.")
        >>> script.add_step("First, subtract 3 from both sides.", time=3.0)
        >>> script.add_step("This gives us 2x equals 4.", time=6.0)
        >>> script.add_step("Now divide both sides by 2.", time=9.0)
        >>> script.add_conclusion("The solution is x equals 2!", time=12.0)
        >>>
        >>> result = generator.create_narrated_video(
        ...     video_path=Path("animation.mp4"),
        ...     script=script,
        ...     output_path=Path("narrated_animation.mp4")
        ... )
    """

    def __init__(
        self,
        voice: Optional[VoiceStyle] = None,
        tts_config: Optional[TTSConfig] = None,
        config: Optional["Config"] = None
    ):
        """
        Initialize the narrated animation generator.

        Args:
            voice: Voice style for narration (deprecated, use config instead)
            tts_config: Optional custom TTS configuration (overrides config)
            config: Optional Config object with TTS settings from environment
        """
        if tts_config:
            # Explicit TTS config takes highest priority
            self.tts_config = tts_config
        elif config:
            # Use config from environment variables
            self.tts_config = config.get_tts_config()
            self.config = config
        elif voice:
            # Legacy: voice parameter (for backward compatibility)
            self.tts_config = TTSConfig(voice=voice)
        else:
            # Default: use environment config
            from math_content_engine.config import Config
            self.config = Config.from_env()
            self.tts_config = self.config.get_tts_config()

        self.tts_engine = TTSEngine(self.tts_config)
        self.combiner = AudioVideoCombiner()

    def create_narrated_video(
        self,
        video_path: Path,
        script: AnimationScript,
        output_path: Path,
        extend_video: bool = True
    ) -> NarratedAnimationResult:
        """
        Create a narrated video from an animation and script.

        Args:
            video_path: Path to the Manim animation video
            script: AnimationScript with narration cues
            output_path: Path for the output video

        Returns:
            NarratedAnimationResult with the final video path
        """
        video_path = Path(video_path)
        output_path = Path(output_path)

        if not video_path.exists():
            return NarratedAnimationResult(
                success=False,
                video_path=None,
                error_message=f"Video not found: {video_path}"
            )

        try:
            # Generate audio for each cue
            audio_paths = []
            audio_segments = []

            for i, cue in enumerate(script.cues):
                # Generate TTS audio
                audio_path = output_path.parent / f"_narration_{i:03d}.mp3"
                audio_path = self.tts_engine.generate(cue.text, audio_path)
                audio_paths.append(audio_path)

                # Create segment with timing
                audio_segments.append(AudioSegment(
                    audio_path=audio_path,
                    start_time=cue.time,
                    volume=1.0
                ))

                logger.info(f"Generated narration {i+1}/{len(script.cues)}: {cue.text[:50]}...")

            # Combine video with audio segments
            if len(audio_segments) == 1:
                # Single audio - use simple combination
                result = self.combiner.combine_simple(
                    video_path=video_path,
                    audio_path=audio_segments[0].audio_path,
                    output_path=output_path,
                    extend_video=extend_video
                )
            else:
                # Multiple segments - use complex combination
                result = self.combiner.combine_segments(
                    video_path=video_path,
                    segments=audio_segments,
                    output_path=output_path
                )

            if not result.success:
                return NarratedAnimationResult(
                    success=False,
                    video_path=None,
                    audio_paths=audio_paths,
                    error_message=result.error_message,
                    script=script
                )

            # Clean up temporary audio files
            for audio_path in audio_paths:
                try:
                    audio_path.unlink()
                except Exception:
                    pass

            logger.info(f"Narrated video created: {output_path}")

            return NarratedAnimationResult(
                success=True,
                video_path=output_path,
                audio_paths=[],  # Cleaned up
                script=script
            )

        except Exception as e:
            logger.error(f"Error creating narrated video: {e}")
            return NarratedAnimationResult(
                success=False,
                video_path=None,
                error_message=str(e)
            )

    def create_simple_narration(
        self,
        video_path: Path,
        narration_text: str,
        output_path: Path
    ) -> NarratedAnimationResult:
        """
        Add simple single-track narration to a video.

        Args:
            video_path: Path to the video
            narration_text: Full narration text
            output_path: Output video path

        Returns:
            NarratedAnimationResult
        """
        video_path = Path(video_path)
        output_path = Path(output_path)

        try:
            # Generate TTS audio
            audio_path = output_path.parent / "_temp_narration.mp3"
            audio_path = self.tts_engine.generate(narration_text, audio_path)

            # Combine
            result = self.combiner.combine_simple(
                video_path=video_path,
                audio_path=audio_path,
                output_path=output_path,
                extend_video=True
            )

            # Clean up
            try:
                audio_path.unlink()
            except Exception:
                pass

            if result.success:
                return NarratedAnimationResult(
                    success=True,
                    video_path=output_path
                )
            else:
                return NarratedAnimationResult(
                    success=False,
                    video_path=None,
                    error_message=result.error_message
                )

        except Exception as e:
            return NarratedAnimationResult(
                success=False,
                video_path=None,
                error_message=str(e)
            )

    def generate_narration_audio_only(
        self,
        script: AnimationScript,
        output_dir: Path
    ) -> List[Path]:
        """
        Generate only the audio files for a script (no video combination).

        Useful for previewing narration before rendering video.

        Args:
            script: AnimationScript with narration cues
            output_dir: Directory for audio files

        Returns:
            List of generated audio file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        audio_paths = []
        for i, cue in enumerate(script.cues):
            audio_path = output_dir / f"narration_{i:03d}_{cue.time:.1f}s.mp3"
            audio_path = self.tts_engine.generate(cue.text, audio_path)
            audio_paths.append(audio_path)
            logger.info(f"Generated: {audio_path.name}")

        return audio_paths


# Convenience functions for common educational scenarios
def create_equation_narration(
    equation: str,
    steps: List[str],
    solution: str
) -> AnimationScript:
    """
    Create a standard narration script for solving an equation.

    Args:
        equation: The equation being solved (e.g., "2x + 3 = 7")
        steps: List of step explanations
        solution: The final solution

    Returns:
        AnimationScript with appropriate timing
    """
    script = AnimationScript(title=f"Solving {equation}")

    # Intro
    script.add_intro(f"Let's solve the equation {equation}.")

    # Steps (spaced 4 seconds apart)
    time = 3.0
    for step in steps:
        script.add_step(step, time=time)
        time += 4.0

    # Conclusion
    script.add_conclusion(f"And our solution is {solution}!", time=time)

    return script


def create_concept_narration(
    concept: str,
    explanation: str,
    example: str,
    conclusion: str
) -> AnimationScript:
    """
    Create a narration script for explaining a math concept.

    Args:
        concept: Name of the concept
        explanation: Main explanation
        example: An example
        conclusion: Wrap-up statement

    Returns:
        AnimationScript
    """
    script = AnimationScript(title=concept)

    script.add_intro(f"Today we're learning about {concept}.")
    script.add_step(explanation, time=4.0)
    script.add_step(example, time=10.0)
    script.add_conclusion(conclusion, time=16.0)

    return script
