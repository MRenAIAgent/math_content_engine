"""
Configuration management using environment variables.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Import centralized enums
from .constants import (
    LLMProvider,
    VideoQuality,
    AnimationStyle,
    TTSVoice,
    VideoStyle,
    TTSProvider,
)

# Re-export for backward compatibility
__all__ = [
    "Config",
    "LLMProvider",
    "VideoQuality",
    "AnimationStyle",
    "TTSVoice",
    "VideoStyle",
    "TTSProvider",
]


@dataclass
class Config:
    """
    Configuration for the Math Content Engine.

    All settings can be overridden via environment variables with the
    MATH_ENGINE_ prefix.

    Example:
        export MATH_ENGINE_LLM_PROVIDER=claude
        export ANTHROPIC_API_KEY=sk-ant-...
    """

    # LLM Settings
    llm_provider: LLMProvider = field(default_factory=lambda: LLMProvider(
        os.getenv("MATH_ENGINE_LLM_PROVIDER", "claude")
    ))

    # API Keys (loaded from standard env vars)
    anthropic_api_key: Optional[str] = field(default_factory=lambda:
        os.getenv("ANTHROPIC_API_KEY")
    )
    openai_api_key: Optional[str] = field(default_factory=lambda:
        os.getenv("OPENAI_API_KEY")
    )

    # Mathpix API Keys (for PDF parsing)
    mathpix_app_id: Optional[str] = field(default_factory=lambda:
        os.getenv("MATHPIX_APP_ID")
    )
    mathpix_app_key: Optional[str] = field(default_factory=lambda:
        os.getenv("MATHPIX_APP_KEY")
    )

    # Model Settings
    claude_model: str = field(default_factory=lambda:
        os.getenv("MATH_ENGINE_CLAUDE_MODEL", "claude-sonnet-4-20250514")
    )
    openai_model: str = field(default_factory=lambda:
        os.getenv("MATH_ENGINE_OPENAI_MODEL", "gpt-4o")
    )

    # Generation Settings
    max_retries: int = field(default_factory=lambda:
        int(os.getenv("MATH_ENGINE_MAX_RETRIES", "5"))
    )
    temperature: float = field(default_factory=lambda:
        float(os.getenv("MATH_ENGINE_TEMPERATURE", "0.7"))
    )
    max_tokens: int = field(default_factory=lambda:
        int(os.getenv("MATH_ENGINE_MAX_TOKENS", "4096"))
    )

    # Rendering Settings
    video_quality: VideoQuality = field(default_factory=lambda: VideoQuality(
        os.getenv("MATH_ENGINE_VIDEO_QUALITY", "m")
    ))
    output_format: str = field(default_factory=lambda:
        os.getenv("MATH_ENGINE_OUTPUT_FORMAT", "mp4")
    )
    output_dir: Path = field(default_factory=lambda:
        Path(os.getenv("MATH_ENGINE_OUTPUT_DIR", "./output"))
    )

    # Manim Settings
    manim_cache_dir: Path = field(default_factory=lambda:
        Path(os.getenv("MATH_ENGINE_MANIM_CACHE", "./.manim_cache"))
    )

    # Animation Style
    animation_style: AnimationStyle = field(default_factory=lambda: AnimationStyle(
        os.getenv("MATH_ENGINE_ANIMATION_STYLE", "dark")
    ))

    # TTS Settings - Provider Selection
    tts_provider: TTSProvider = field(default_factory=lambda: TTSProvider(
        os.getenv("MATH_ENGINE_TTS_PROVIDER", "edge")
    ))
    elevenlabs_api_key: Optional[str] = field(default_factory=lambda:
        os.getenv("ELEVENLABS_API_KEY")
    )

    # TTS Settings - Voice Configuration (for Edge TTS compatibility)
    tts_voice: Optional[str] = field(default_factory=lambda:
        os.getenv("MATH_ENGINE_TTS_VOICE")  # Provider-specific voice ID/name or TTSVoice enum value
    )
    tts_rate: str = field(default_factory=lambda:
        os.getenv("MATH_ENGINE_TTS_RATE", "+0%")
    )
    tts_volume: str = field(default_factory=lambda:
        os.getenv("MATH_ENGINE_TTS_VOLUME", "+0%")
    )
    tts_pitch: str = field(default_factory=lambda:
        os.getenv("MATH_ENGINE_TTS_PITCH", "+0Hz")
    )
    tts_custom_voice: Optional[str] = field(default_factory=lambda:
        os.getenv("MATH_ENGINE_TTS_CUSTOM_VOICE")
    )

    # Integration Settings
    redis_url: Optional[str] = field(default_factory=lambda:
        os.getenv("REDIS_URL")
    )
    tutor_api_url: Optional[str] = field(default_factory=lambda:
        os.getenv("TUTOR_API_URL")
    )
    publish_events: bool = field(default_factory=lambda:
        os.getenv("PUBLISH_EVENTS", "false").lower() == "true"
    )
    redis_stream_name: str = field(default_factory=lambda:
        os.getenv("REDIS_STREAM_NAME", "content_events")
    )

    # Video Style Settings
    video_style: VideoStyle = field(default_factory=lambda: VideoStyle(
        os.getenv("MATH_ENGINE_VIDEO_STYLE", "standard")
    ))
    step_duration: float = field(default_factory=lambda:
        float(os.getenv("MATH_ENGINE_STEP_DURATION", "4.0"))
    )
    pause_between_steps: float = field(default_factory=lambda:
        float(os.getenv("MATH_ENGINE_PAUSE_BETWEEN_STEPS", "0.5"))
    )

    def __post_init__(self):
        """Validate configuration after initialization."""
        # Ensure output directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.manim_cache_dir.mkdir(parents=True, exist_ok=True)

        # Validate API key is set for chosen provider
        if self.llm_provider == LLMProvider.CLAUDE and not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is required when using Claude"
            )
        if self.llm_provider == LLMProvider.OPENAI and not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required when using OpenAI"
            )

        # Validate TTS API key for ElevenLabs
        if self.tts_provider == TTSProvider.ELEVENLABS and not self.elevenlabs_api_key:
            raise ValueError(
                "ELEVENLABS_API_KEY environment variable is required when using ElevenLabs TTS"
            )

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        # Load environment variables from .env file
        load_dotenv()
        
        return cls()

    def get_api_key(self) -> str:
        """Get the API key for the configured LLM provider."""
        if self.llm_provider == LLMProvider.CLAUDE:
            return self.anthropic_api_key
        return self.openai_api_key

    def get_model(self) -> str:
        """Get the model name for the configured LLM provider."""
        if self.llm_provider == LLMProvider.CLAUDE:
            return self.claude_model
        return self.openai_model

    def get_tts_config(self):
        """
        Get TTSConfig from environment settings.

        Returns:
            TTSConfig object configured from environment variables for Edge TTS.
            For ElevenLabs, use create_tts_provider() instead.
        """
        # Import here to avoid circular dependency
        from math_content_engine.tts import TTSConfig, VoiceStyle

        # If tts_voice is a string matching TTSVoice enum values, map it
        # Otherwise, use it as a custom voice or provider-specific ID
        voice_style = VoiceStyle.TEACHER_FEMALE  # default

        if self.tts_voice:
            try:
                # Try to parse as TTSVoice enum value
                tts_voice_enum = TTSVoice(self.tts_voice)

                # Map config enum to VoiceStyle enum
                voice_map = {
                    TTSVoice.TEACHER_MALE: VoiceStyle.TEACHER_MALE,
                    TTSVoice.TEACHER_FEMALE: VoiceStyle.TEACHER_FEMALE,
                    TTSVoice.FRIENDLY_MALE: VoiceStyle.FRIENDLY_MALE,
                    TTSVoice.FRIENDLY_FEMALE: VoiceStyle.FRIENDLY_FEMALE,
                    TTSVoice.PROFESSIONAL_MALE: VoiceStyle.PROFESSIONAL_MALE,
                    TTSVoice.PROFESSIONAL_FEMALE: VoiceStyle.PROFESSIONAL_FEMALE,
                    TTSVoice.CARING_MALE: VoiceStyle.CARING_MALE,
                    TTSVoice.CARING_FEMALE: VoiceStyle.CARING_FEMALE,
                    TTSVoice.YOUNG_FEMALE: VoiceStyle.YOUNG_FEMALE,
                }
                voice_style = voice_map[tts_voice_enum]
            except (ValueError, KeyError):
                # If not a TTSVoice enum, it might be a custom voice name
                # We'll use custom_voice parameter instead
                pass

        return TTSConfig(
            voice=voice_style,
            rate=self.tts_rate,
            volume=self.tts_volume,
            pitch=self.tts_pitch,
            custom_voice=self.tts_custom_voice or self.tts_voice
        )
