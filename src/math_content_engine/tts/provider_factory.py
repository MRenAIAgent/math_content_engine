"""
TTS provider factory.

Creates the appropriate TTS provider based on configuration.
"""

import logging
from typing import Optional

from ..config import Config, TTSProvider
from .base_provider import BaseTTSProvider
from .edge_tts_provider import EdgeTTSProvider, EdgeTTSConfig, VoiceStyle
from .elevenlabs_provider import ElevenLabsTTSProvider, ElevenLabsConfig, ElevenLabsVoice

logger = logging.getLogger(__name__)


def create_tts_provider(
    config: Optional[Config] = None,
    provider: Optional[TTSProvider] = None,
) -> BaseTTSProvider:
    """
    Create a TTS provider based on configuration.

    Args:
        config: Application configuration. If not provided, uses defaults.
        provider: Override the TTS provider from config.

    Returns:
        Initialized TTS provider

    Raises:
        ValueError: If provider is not supported or required API keys are missing

    Example:
        >>> from math_content_engine import Config
        >>> config = Config()
        >>> provider = create_tts_provider(config)
        >>> # Use provider for TTS generation
    """
    if config is None:
        from ..config import Config
        config = Config()

    # Use override provider if specified, otherwise use config
    selected_provider = provider or config.tts_provider

    if selected_provider == TTSProvider.EDGE:
        return _create_edge_tts_provider(config)
    elif selected_provider == TTSProvider.ELEVENLABS:
        return _create_elevenlabs_provider(config)
    else:
        raise ValueError(f"Unsupported TTS provider: {selected_provider}")


def _create_edge_tts_provider(config: Config) -> EdgeTTSProvider:
    """Create Edge TTS provider from config."""
    edge_config = EdgeTTSConfig()

    # Override voice if specified in config
    if config.tts_voice:
        # Try to match with enum, otherwise use as custom voice
        try:
            edge_config.voice = VoiceStyle[config.tts_voice.upper()]
        except KeyError:
            edge_config.custom_voice = config.tts_voice

    logger.info("Created Edge TTS provider")
    return EdgeTTSProvider(edge_config)


def _create_elevenlabs_provider(config: Config) -> ElevenLabsTTSProvider:
    """Create ElevenLabs TTS provider from config."""
    if not config.elevenlabs_api_key:
        raise ValueError(
            "ELEVENLABS_API_KEY environment variable is required for ElevenLabs TTS"
        )

    elevenlabs_config = ElevenLabsConfig(
        api_key=config.elevenlabs_api_key,
    )

    # Override voice if specified in config
    if config.tts_voice:
        # Try to match with enum, otherwise use as voice ID
        try:
            elevenlabs_config.voice_id = ElevenLabsVoice[config.tts_voice.upper()].value
        except KeyError:
            # Assume it's a voice ID
            elevenlabs_config.voice_id = config.tts_voice

    logger.info("Created ElevenLabs TTS provider")
    return ElevenLabsTTSProvider(elevenlabs_config)
