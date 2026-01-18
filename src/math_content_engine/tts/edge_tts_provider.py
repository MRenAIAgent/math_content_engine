"""
Edge TTS provider.

Provides TTS using Microsoft Edge's free neural TTS service.
No API key required.
"""

import logging
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, List

from .base_provider import BaseTTSProvider, TTSProviderConfig

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
class EdgeTTSConfig(TTSProviderConfig):
    """Configuration for Edge TTS."""

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


class EdgeTTSProvider(BaseTTSProvider):
    """
    Edge TTS provider using Microsoft Edge's neural TTS voices.

    No API key required - uses Microsoft Edge's free TTS service.

    Example:
        >>> config = EdgeTTSConfig(voice=VoiceStyle.TEACHER_MALE)
        >>> provider = EdgeTTSProvider(config)
        >>> audio_path = await provider.generate_async("Hello, world!", Path("output.mp3"))
    """

    def __init__(self, config: Optional[EdgeTTSConfig] = None):
        """
        Initialize Edge TTS provider.

        Args:
            config: Edge TTS configuration. Uses defaults if not provided.
        """
        super().__init__(config)
        self.config: EdgeTTSConfig = config or EdgeTTSConfig()
        self._temp_dir = Path(tempfile.mkdtemp(prefix="edge_tts_"))
        logger.info(f"Edge TTS initialized with voice: {self.config.get_voice_name()}")

    async def generate_async(self, text: str, output_path: Path) -> Path:
        """
        Generate speech audio from text using Edge TTS.

        Args:
            text: Text to convert to speech
            output_path: Path where audio file should be saved

        Returns:
            Path to the generated audio file
        """
        try:
            import edge_tts
        except ImportError:
            raise ImportError(
                "edge-tts is required for Edge TTS. Install with: pip install edge-tts"
            )

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

        logger.info(f"Generated Edge TTS audio: {output_path}")
        return output_path

    async def generate_with_subtitles(
        self,
        text: str,
        audio_path: Path,
        subtitle_path: Path
    ) -> tuple[Path, Path]:
        """
        Generate speech audio with subtitle/timing file.

        Args:
            text: Text to convert to speech
            audio_path: Audio output path
            subtitle_path: Subtitle output path (.vtt or .srt)

        Returns:
            Tuple of (audio_path, subtitle_path)
        """
        try:
            import edge_tts
        except ImportError:
            raise ImportError(
                "edge-tts is required for Edge TTS. Install with: pip install edge-tts"
            )

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

        logger.info(f"Generated Edge TTS with subtitles: {audio_path}, {subtitle_path}")
        return audio_path, subtitle_path

    def get_audio_duration(self, audio_path: Path) -> float:
        """
        Get duration of an audio file in seconds.

        Args:
            audio_path: Path to audio file

        Returns:
            Duration in seconds
        """
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

    def list_voices(self) -> List[dict]:
        """
        List all available Edge TTS voices.

        Returns:
            List of voice information dictionaries
        """
        try:
            import edge_tts
            import asyncio

            async def get_voices():
                return await edge_tts.list_voices()

            return asyncio.run(get_voices())
        except ImportError:
            raise ImportError(
                "edge-tts is required. Install with: pip install edge-tts"
            )

    def cleanup(self) -> None:
        """Clean up temporary files."""
        import shutil
        if self._temp_dir.exists():
            shutil.rmtree(self._temp_dir)
            logger.info("Edge TTS temp files cleaned up")
