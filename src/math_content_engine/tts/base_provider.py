"""
Base TTS provider abstraction.

Provides a common interface for different TTS providers (Edge TTS, ElevenLabs, etc.).
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class TTSProviderConfig(ABC):
    """Base configuration for TTS providers."""
    output_format: str = "mp3"


class BaseTTSProvider(ABC):
    """
    Abstract base class for TTS providers.

    All TTS providers (Edge TTS, ElevenLabs, etc.) should implement this interface.
    """

    def __init__(self, config: Optional[TTSProviderConfig] = None):
        """
        Initialize the TTS provider.

        Args:
            config: Provider-specific configuration
        """
        self.config = config

    @abstractmethod
    async def generate_async(self, text: str, output_path: Path) -> Path:
        """
        Generate speech audio from text asynchronously.

        Args:
            text: Text to convert to speech
            output_path: Path where audio file should be saved

        Returns:
            Path to the generated audio file
        """
        pass

    @abstractmethod
    def get_audio_duration(self, audio_path: Path) -> float:
        """
        Get duration of an audio file in seconds.

        Args:
            audio_path: Path to audio file

        Returns:
            Duration in seconds
        """
        pass

    @abstractmethod
    def list_voices(self) -> List[dict]:
        """
        List all available voices for this provider.

        Returns:
            List of voice information dictionaries
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up any temporary resources."""
        pass
