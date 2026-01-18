"""
Text-to-Speech engine with support for multiple providers.

Provides high-quality neural voices for narrating math animations.
Supports Edge TTS (free, no API key) and ElevenLabs (requires API key).
"""

import asyncio
import logging
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, List

from .base_provider import BaseTTSProvider
from .edge_tts_provider import VoiceStyle, EdgeTTSConfig, EdgeTTSProvider

logger = logging.getLogger(__name__)


# Re-export for backward compatibility
TTSConfig = EdgeTTSConfig


@dataclass
class NarrationSegment:
    """A segment of narration with timing information."""

    text: str
    start_time: float          # When to start speaking (seconds)
    audio_path: Optional[Path] = None
    duration: float = 0.0      # Duration of audio (filled after generation)


@dataclass
class NarrationScript:
    """Complete narration script for an animation."""

    segments: List[NarrationSegment] = field(default_factory=list)
    total_duration: float = 0.0

    def add_segment(self, text: str, start_time: float) -> None:
        """Add a narration segment."""
        self.segments.append(NarrationSegment(text=text, start_time=start_time))

    def add_wait(self, duration: float) -> None:
        """Add a pause in narration."""
        if self.segments:
            # Just extend the gap before the next segment
            pass


class TTSEngine:
    """
    Text-to-Speech engine for generating voice narration.

    Supports multiple TTS providers (Edge TTS, ElevenLabs).
    Uses provider abstraction for flexible TTS generation.

    Example:
        >>> # Using default provider (Edge TTS)
        >>> tts = TTSEngine()
        >>> audio_path = tts.generate("Hello, let's learn about equations!")

        >>> # With custom provider
        >>> from math_content_engine.tts import EdgeTTSProvider, EdgeTTSConfig
        >>> provider = EdgeTTSProvider(EdgeTTSConfig(voice=VoiceStyle.TEACHER_MALE))
        >>> tts = TTSEngine(provider=provider)
        >>> audio_path = tts.generate("Today we'll solve 2x + 3 = 7")

        >>> # Using factory
        >>> from math_content_engine.tts import create_tts_provider
        >>> from math_content_engine import Config
        >>> config = Config()
        >>> provider = create_tts_provider(config)
        >>> tts = TTSEngine(provider=provider)
    """

    def __init__(
        self,
        config: Optional[TTSConfig] = None,
        provider: Optional[BaseTTSProvider] = None
    ):
        """
        Initialize the TTS engine.

        Args:
            config: TTS configuration (for backward compatibility with Edge TTS).
                   Ignored if provider is specified.
            provider: TTS provider instance. If not provided, creates Edge TTS provider
                     with the given config.
        """
        if provider is not None:
            self.provider = provider
        else:
            # Backward compatibility: create Edge TTS provider
            edge_config = config or EdgeTTSConfig()
            self.provider = EdgeTTSProvider(edge_config)

        self._temp_dir = Path(tempfile.mkdtemp(prefix="math_tts_"))
        logger.info(f"TTS Engine initialized with provider: {type(self.provider).__name__}")

    def generate(self, text: str, output_path: Optional[Path] = None) -> Path:
        """
        Generate speech audio from text.

        Args:
            text: Text to convert to speech
            output_path: Optional output file path. If not provided,
                        generates a temp file.

        Returns:
            Path to the generated audio file
        """
        return asyncio.run(self._generate_async(text, output_path))

    async def _generate_async(self, text: str, output_path: Optional[Path] = None) -> Path:
        """Async implementation of TTS generation."""
        # Determine output path
        if output_path is None:
            output_format = getattr(self.provider.config, 'output_format', 'mp3')
            output_path = self._temp_dir / f"tts_{hash(text) & 0xFFFFFFFF}.{output_format}"

        output_path = Path(output_path)

        # Delegate to provider
        return await self.provider.generate_async(text, output_path)

    def generate_with_subtitles(
        self,
        text: str,
        audio_path: Optional[Path] = None,
        subtitle_path: Optional[Path] = None
    ) -> tuple[Path, Path]:
        """
        Generate speech audio with subtitle/timing file.

        Args:
            text: Text to convert to speech
            audio_path: Optional audio output path
            subtitle_path: Optional subtitle output path (.vtt or .srt)

        Returns:
            Tuple of (audio_path, subtitle_path)
        """
        return asyncio.run(
            self._generate_with_subtitles_async(text, audio_path, subtitle_path)
        )

    async def _generate_with_subtitles_async(
        self,
        text: str,
        audio_path: Optional[Path] = None,
        subtitle_path: Optional[Path] = None
    ) -> tuple[Path, Path]:
        """Async implementation of TTS with subtitles."""
        # Check if provider supports subtitles (only Edge TTS currently)
        if not isinstance(self.provider, EdgeTTSProvider):
            raise NotImplementedError(
                f"Subtitle generation not supported for {type(self.provider).__name__}. "
                "Only Edge TTS provider supports subtitles."
            )

        # Determine paths
        text_hash = hash(text) & 0xFFFFFFFF
        output_format = getattr(self.provider.config, 'output_format', 'mp3')
        if audio_path is None:
            audio_path = self._temp_dir / f"tts_{text_hash}.{output_format}"
        if subtitle_path is None:
            subtitle_path = self._temp_dir / f"tts_{text_hash}.vtt"

        audio_path = Path(audio_path)
        subtitle_path = Path(subtitle_path)

        # Delegate to Edge TTS provider
        return await self.provider.generate_with_subtitles(text, audio_path, subtitle_path)

    def generate_script(
        self,
        script: NarrationScript,
        output_dir: Optional[Path] = None
    ) -> NarrationScript:
        """
        Generate audio for all segments in a narration script.

        Args:
            script: NarrationScript with text segments
            output_dir: Directory for audio files

        Returns:
            Updated NarrationScript with audio paths and durations
        """
        return asyncio.run(self._generate_script_async(script, output_dir))

    async def _generate_script_async(
        self,
        script: NarrationScript,
        output_dir: Optional[Path] = None
    ) -> NarrationScript:
        """Async implementation of script generation."""
        if output_dir is None:
            output_dir = self._temp_dir
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_format = getattr(self.provider.config, 'output_format', 'mp3')
        for i, segment in enumerate(script.segments):
            audio_path = output_dir / f"segment_{i:03d}.{output_format}"
            await self.provider.generate_async(segment.text, audio_path)
            segment.audio_path = audio_path

            # Get audio duration
            segment.duration = self.provider.get_audio_duration(audio_path)

        # Calculate total duration
        if script.segments:
            last_segment = script.segments[-1]
            script.total_duration = last_segment.start_time + last_segment.duration

        return script

    def _get_audio_duration(self, audio_path: Path) -> float:
        """Get duration of an audio file in seconds."""
        return self.provider.get_audio_duration(audio_path)

    def list_voices(self) -> List[dict]:
        """
        List all available TTS voices for the current provider.

        Returns:
            List of voice information dictionaries
        """
        return self.provider.list_voices()

    def cleanup(self):
        """Clean up temporary files."""
        import shutil
        if self._temp_dir.exists():
            shutil.rmtree(self._temp_dir)
            logger.info("TTS temp files cleaned up")
        self.provider.cleanup()
