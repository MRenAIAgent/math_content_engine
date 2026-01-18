"""
ElevenLabs TTS provider.

Provides high-quality neural voice synthesis using ElevenLabs API.
Requires an ElevenLabs API key.
"""

import logging
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, List

from .base_provider import BaseTTSProvider, TTSProviderConfig

try:
    from elevenlabs import VoiceSettings
    from elevenlabs.client import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    VoiceSettings = None
    ElevenLabs = None

logger = logging.getLogger(__name__)


class ElevenLabsVoice(Enum):
    """Pre-configured ElevenLabs voice styles."""

    # Default high-quality voices
    RACHEL = "21m00Tcm4TlvDq8ikWAM"      # American Female, Calm
    DOMI = "AZnzlk1XvdvUeBnXmlld"        # American Female, Strong
    BELLA = "EXAVITQu4vr4xnSDxMaL"       # American Female, Soft
    ANTONI = "ErXwobaYiN019PkySvjV"      # American Male, Well-rounded
    ELLI = "MF3mGyEYCl7XYWbV9V6O"        # American Female, Emotional
    JOSH = "TxGEqnHWrfWFTfGW9XjX"        # American Male, Deep
    ARNOLD = "VR6AewLTigWG4xSOukaG"      # American Male, Crisp
    ADAM = "pNInz6obpgDQGcFmaJgB"        # American Male, Deep
    SAM = "yoZ06aMxZJJ28mfd3POQ"         # American Male, Dynamic

    # Teacher/Educational voices (recommended for math content)
    TEACHER_FEMALE_CALM = "21m00Tcm4TlvDq8ikWAM"     # Rachel
    TEACHER_FEMALE_CLEAR = "EXAVITQu4vr4xnSDxMaL"    # Bella
    TEACHER_MALE_DEEP = "TxGEqnHWrfWFTfGW9XjX"        # Josh
    TEACHER_MALE_CLEAR = "ErXwobaYiN019PkySvjV"      # Antoni


@dataclass
class ElevenLabsConfig(TTSProviderConfig):
    """Configuration for ElevenLabs TTS."""

    api_key: str = ""
    voice_id: str = ElevenLabsVoice.TEACHER_FEMALE_CALM.value
    model_id: str = "eleven_multilingual_v2"  # or "eleven_monolingual_v1"

    # Voice settings
    stability: float = 0.5       # 0.0 to 1.0 (higher = more stable/monotone)
    similarity_boost: float = 0.75  # 0.0 to 1.0 (higher = more similar to original voice)
    style: float = 0.0           # 0.0 to 1.0 (style exaggeration)
    use_speaker_boost: bool = True

    # Output format
    output_format: str = "mp3_44100_128"  # mp3_44100_128, pcm_16000, etc.

    def __post_init__(self):
        """Validate configuration."""
        if not self.api_key:
            raise ValueError("ElevenLabs API key is required")


class ElevenLabsTTSProvider(BaseTTSProvider):
    """
    ElevenLabs TTS provider.

    Uses the ElevenLabs API for high-quality text-to-speech generation.

    Example:
        >>> config = ElevenLabsConfig(api_key="your-api-key")
        >>> provider = ElevenLabsTTSProvider(config)
        >>> audio_path = await provider.generate_async("Hello, world!", Path("output.mp3"))
    """

    def __init__(self, config: ElevenLabsConfig):
        """
        Initialize ElevenLabs TTS provider.

        Args:
            config: ElevenLabs configuration including API key
        """
        super().__init__(config)
        self.config: ElevenLabsConfig = config
        self._temp_dir = Path(tempfile.mkdtemp(prefix="elevenlabs_tts_"))
        logger.info(f"ElevenLabs TTS initialized with voice: {config.voice_id}")

    async def generate_async(self, text: str, output_path: Path) -> Path:
        """
        Generate speech audio from text using ElevenLabs API.

        Args:
            text: Text to convert to speech
            output_path: Path where audio file should be saved

        Returns:
            Path to the generated audio file
        """
        if not ELEVENLABS_AVAILABLE:
            raise ImportError(
                "elevenlabs is required for ElevenLabs TTS. "
                "Install with: pip install elevenlabs"
            )

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize client
        client = ElevenLabs(api_key=self.config.api_key)

        # Generate audio
        logger.info(f"Generating speech for text: {text[:50]}...")

        # Use text_to_speech.convert method
        audio_generator = client.text_to_speech.convert(
            text=text,
            voice_id=self.config.voice_id,
            model_id=self.config.model_id,
            voice_settings=VoiceSettings(
                stability=self.config.stability,
                similarity_boost=self.config.similarity_boost,
                style=self.config.style,
                use_speaker_boost=self.config.use_speaker_boost,
            ),
        )

        # Save audio to file
        with open(output_path, "wb") as f:
            for chunk in audio_generator:
                f.write(chunk)

        logger.info(f"Generated ElevenLabs audio: {output_path}")
        return output_path

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
            from mutagen.wave import WAVE

            audio_path = Path(audio_path)

            if audio_path.suffix.lower() == '.mp3':
                audio = MP3(str(audio_path))
                return audio.info.length
            elif audio_path.suffix.lower() == '.wav':
                audio = WAVE(str(audio_path))
                return audio.info.length
            else:
                # Fallback estimate
                logger.warning(f"Unknown audio format: {audio_path.suffix}")
                return 3.0

        except ImportError:
            # Fallback: estimate based on file size
            size_kb = audio_path.stat().st_size / 1024
            # Rough estimate for 128kbps MP3: 16KB per second
            return size_kb / 16
        except Exception as e:
            logger.warning(f"Could not get audio duration: {e}")
            return 3.0

    def list_voices(self) -> List[dict]:
        """
        List all available ElevenLabs voices.

        Returns:
            List of voice information dictionaries
        """
        if not ELEVENLABS_AVAILABLE:
            raise ImportError(
                "elevenlabs is required. Install with: pip install elevenlabs"
            )

        client = ElevenLabs(api_key=self.config.api_key)
        voices = client.voices.get_all()

        return [
            {
                "voice_id": voice.voice_id,
                "name": voice.name,
                "category": voice.category if hasattr(voice, 'category') else "general",
                "description": voice.description if hasattr(voice, 'description') else "",
            }
            for voice in voices.voices
        ]

    def cleanup(self) -> None:
        """Clean up temporary files."""
        import shutil
        if self._temp_dir.exists():
            shutil.rmtree(self._temp_dir)
            logger.info("ElevenLabs TTS temp files cleaned up")
