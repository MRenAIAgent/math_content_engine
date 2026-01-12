"""
Text-to-Speech engine using Microsoft Edge TTS.

Provides high-quality neural voices for narrating math animations.
No API key required - uses Microsoft Edge's free TTS service.
"""

import asyncio
import logging
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)


class VoiceStyle(Enum):
    """Pre-configured voice styles for different teaching scenarios."""

    # Teacher voices - clear, authoritative, educational
    TEACHER_MALE = "en-US-ChristopherNeural"      # Reliable, Authority
    TEACHER_FEMALE = "en-US-JennyNeural"          # Friendly, Considerate

    # Friendly/casual teaching
    FRIENDLY_MALE = "en-US-BrianNeural"           # Approachable, Casual
    FRIENDLY_FEMALE = "en-US-EmmaNeural"          # Cheerful, Clear

    # News/professional style
    PROFESSIONAL_MALE = "en-US-GuyNeural"         # Passion
    PROFESSIONAL_FEMALE = "en-US-AriaNeural"      # Positive, Confident

    # Warm/caring style (good for younger audiences)
    CARING_MALE = "en-US-AndrewNeural"            # Warm, Confident
    CARING_FEMALE = "en-US-AvaNeural"             # Expressive, Caring

    # For younger students
    YOUNG_FEMALE = "en-US-AnaNeural"              # Cartoon, Cute


@dataclass
class TTSConfig:
    """Configuration for TTS generation."""

    voice: VoiceStyle = VoiceStyle.TEACHER_FEMALE
    rate: str = "+0%"          # Speed: -50% to +100%
    volume: str = "+0%"        # Volume: -50% to +50%
    pitch: str = "+0Hz"        # Pitch adjustment
    output_format: str = "mp3"  # mp3, wav, etc.

    # Custom voice name (overrides voice style if set)
    custom_voice: Optional[str] = None

    def get_voice_name(self) -> str:
        """Get the voice name to use."""
        if self.custom_voice:
            return self.custom_voice
        return self.voice.value


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

    Uses Microsoft Edge's neural TTS voices (via edge-tts library).
    No API key required.

    Example:
        >>> tts = TTSEngine()
        >>> audio_path = tts.generate("Hello, let's learn about equations!")
        >>> print(f"Audio saved to: {audio_path}")

        >>> # With custom config
        >>> config = TTSConfig(voice=VoiceStyle.TEACHER_MALE, rate="-10%")
        >>> tts = TTSEngine(config)
        >>> audio_path = tts.generate("Today we'll solve 2x + 3 = 7")
    """

    def __init__(self, config: Optional[TTSConfig] = None):
        """
        Initialize the TTS engine.

        Args:
            config: TTS configuration. Uses defaults if not provided.
        """
        self.config = config or TTSConfig()
        self._temp_dir = Path(tempfile.mkdtemp(prefix="math_tts_"))
        logger.info(f"TTS Engine initialized with voice: {self.config.get_voice_name()}")

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
        try:
            import edge_tts
        except ImportError:
            raise ImportError(
                "edge-tts is required for TTS. Install with: pip install edge-tts"
            )

        # Determine output path
        if output_path is None:
            output_path = self._temp_dir / f"tts_{hash(text) & 0xFFFFFFFF}.{self.config.output_format}"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create communicate object
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.config.get_voice_name(),
            rate=self.config.rate,
            volume=self.config.volume,
            pitch=self.config.pitch,
        )

        # Generate audio
        await communicate.save(str(output_path))

        logger.info(f"Generated TTS audio: {output_path}")
        return output_path

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
        try:
            import edge_tts
        except ImportError:
            raise ImportError(
                "edge-tts is required for TTS. Install with: pip install edge-tts"
            )

        # Determine paths
        text_hash = hash(text) & 0xFFFFFFFF
        if audio_path is None:
            audio_path = self._temp_dir / f"tts_{text_hash}.{self.config.output_format}"
        if subtitle_path is None:
            subtitle_path = self._temp_dir / f"tts_{text_hash}.vtt"

        audio_path = Path(audio_path)
        subtitle_path = Path(subtitle_path)
        audio_path.parent.mkdir(parents=True, exist_ok=True)

        # Create communicate object
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.config.get_voice_name(),
            rate=self.config.rate,
            volume=self.config.volume,
            pitch=self.config.pitch,
        )

        # Generate with subtitles
        submaker = edge_tts.SubMaker()

        with open(audio_path, "wb") as audio_file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    submaker.feed(chunk)

        # Save subtitles
        with open(subtitle_path, "w", encoding="utf-8") as sub_file:
            sub_file.write(submaker.get_srt())

        logger.info(f"Generated TTS with subtitles: {audio_path}, {subtitle_path}")
        return audio_path, subtitle_path

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

        for i, segment in enumerate(script.segments):
            audio_path = output_dir / f"segment_{i:03d}.{self.config.output_format}"
            await self._generate_async(segment.text, audio_path)
            segment.audio_path = audio_path

            # Get audio duration
            segment.duration = self._get_audio_duration(audio_path)

        # Calculate total duration
        if script.segments:
            last_segment = script.segments[-1]
            script.total_duration = last_segment.start_time + last_segment.duration

        return script

    def _get_audio_duration(self, audio_path: Path) -> float:
        """Get duration of an audio file in seconds."""
        try:
            from mutagen.mp3 import MP3
            audio = MP3(str(audio_path))
            return audio.info.length
        except ImportError:
            # Fallback: estimate based on file size
            # Rough estimate: 16kbps = 2KB per second
            size_kb = audio_path.stat().st_size / 1024
            return size_kb / 16
        except Exception as e:
            logger.warning(f"Could not get audio duration: {e}")
            return 3.0  # Default estimate

    @staticmethod
    def list_voices() -> List[dict]:
        """
        List all available TTS voices.

        Returns:
            List of voice information dictionaries
        """
        return asyncio.run(TTSEngine._list_voices_async())

    @staticmethod
    async def _list_voices_async() -> List[dict]:
        """Async implementation of voice listing."""
        try:
            import edge_tts
            voices = await edge_tts.list_voices()
            return voices
        except ImportError:
            raise ImportError(
                "edge-tts is required. Install with: pip install edge-tts"
            )

    def cleanup(self):
        """Clean up temporary files."""
        import shutil
        if self._temp_dir.exists():
            shutil.rmtree(self._temp_dir)
            logger.info("TTS temp files cleaned up")
