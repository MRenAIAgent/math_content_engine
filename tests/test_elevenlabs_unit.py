"""
Unit tests for ElevenLabs TTS provider (no API calls required).

These tests verify the implementation without making actual API calls.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import asyncio

from math_content_engine.tts import (
    ElevenLabsTTSProvider,
    ElevenLabsConfig,
    ElevenLabsVoice,
    TTSEngine,
    create_tts_provider,
)
from math_content_engine.config import Config, TTSProvider


class TestElevenLabsConfig:
    """Test ElevenLabs configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ElevenLabsConfig(api_key="test-key")
        assert config.api_key == "test-key"
        assert config.voice_id == ElevenLabsVoice.TEACHER_FEMALE_CALM.value
        assert config.model_id == "eleven_multilingual_v2"
        assert config.stability == 0.5
        assert config.similarity_boost == 0.75

    def test_custom_config(self):
        """Test custom configuration."""
        config = ElevenLabsConfig(
            api_key="custom-key",
            voice_id=ElevenLabsVoice.TEACHER_MALE_DEEP.value,
            stability=0.7,
            similarity_boost=0.8,
        )
        assert config.api_key == "custom-key"
        assert config.voice_id == ElevenLabsVoice.TEACHER_MALE_DEEP.value
        assert config.stability == 0.7
        assert config.similarity_boost == 0.8

    def test_requires_api_key(self):
        """Test that API key is required."""
        with pytest.raises(ValueError, match="API key is required"):
            ElevenLabsConfig(api_key="")


class TestElevenLabsVoice:
    """Test ElevenLabs voice enumeration."""

    def test_voice_enum_values(self):
        """Test that voice enum has expected values."""
        assert ElevenLabsVoice.RACHEL.value == "21m00Tcm4TlvDq8ikWAM"
        assert ElevenLabsVoice.TEACHER_FEMALE_CALM.value == "21m00Tcm4TlvDq8ikWAM"
        assert ElevenLabsVoice.TEACHER_MALE_DEEP.value == "TxGEqnHWrfWFTfGW9XjX"

    def test_all_voices_defined(self):
        """Test that all expected voices are defined."""
        voices = [v.name for v in ElevenLabsVoice]
        # All basic voices should be present
        assert "RACHEL" in voices
        assert "ANTONI" in voices
        # Teacher aliases may not be in the raw enum list
        # since they're just references to other voice IDs


class TestElevenLabsProvider:
    """Test ElevenLabs TTS provider with mocked API."""

    @pytest.fixture
    def mock_elevenlabs(self):
        """Mock the ElevenLabs client."""
        with patch('math_content_engine.tts.elevenlabs_provider.ElevenLabs') as mock:
            mock_client = MagicMock()
            mock.return_value = mock_client
            yield mock, mock_client

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return ElevenLabsConfig(api_key="test-api-key")

    @pytest.mark.asyncio
    async def test_generate_async(self, config, mock_elevenlabs, tmp_path):
        """Test async audio generation."""
        mock_cls, mock_client = mock_elevenlabs

        # Mock the audio generation
        mock_audio_data = b"fake audio data"
        mock_client.text_to_speech.convert.return_value = iter([mock_audio_data])

        # Create provider and generate
        provider = ElevenLabsTTSProvider(config)
        output_path = tmp_path / "test.mp3"

        result = await provider.generate_async("Test text", output_path)

        # Verify
        assert result == output_path
        assert output_path.exists()
        assert output_path.read_bytes() == mock_audio_data

        # Verify API was called correctly
        mock_client.text_to_speech.convert.assert_called_once()
        call_kwargs = mock_client.text_to_speech.convert.call_args[1]
        assert call_kwargs['text'] == "Test text"
        assert call_kwargs['voice_id'] == config.voice_id
        assert call_kwargs['model_id'] == config.model_id

    @pytest.mark.asyncio
    async def test_generate_creates_parent_dirs(self, config, mock_elevenlabs, tmp_path):
        """Test that parent directories are created."""
        mock_cls, mock_client = mock_elevenlabs
        mock_client.text_to_speech.convert.return_value = iter([b"data"])

        provider = ElevenLabsTTSProvider(config)
        output_path = tmp_path / "subdir" / "test.mp3"

        result = await provider.generate_async("Test", output_path)

        assert result.exists()
        assert result.parent.exists()

    def test_get_audio_duration_mp3(self, config, tmp_path):
        """Test getting duration for MP3 files."""
        # Create a fake MP3 file
        output_path = tmp_path / "test.mp3"
        output_path.write_bytes(b"fake mp3 data" * 100)

        provider = ElevenLabsTTSProvider(config)
        duration = provider.get_audio_duration(output_path)

        # Should return a fallback estimate
        assert duration > 0

    def test_list_voices(self, config, mock_elevenlabs):
        """Test listing available voices."""
        mock_cls, mock_client = mock_elevenlabs

        # Mock voice response
        mock_voice1 = MagicMock()
        mock_voice1.voice_id = "voice1"
        mock_voice1.name = "Test Voice 1"
        mock_voice1.category = "general"
        mock_voice1.description = "A test voice"

        mock_voice2 = MagicMock()
        mock_voice2.voice_id = "voice2"
        mock_voice2.name = "Test Voice 2"

        mock_voices_response = MagicMock()
        mock_voices_response.voices = [mock_voice1, mock_voice2]
        mock_client.voices.get_all.return_value = mock_voices_response

        provider = ElevenLabsTTSProvider(config)
        voices = provider.list_voices()

        assert len(voices) == 2
        assert voices[0]['voice_id'] == 'voice1'
        assert voices[0]['name'] == 'Test Voice 1'
        assert voices[1]['voice_id'] == 'voice2'

    def test_cleanup(self, config, tmp_path):
        """Test cleanup of temporary files."""
        provider = ElevenLabsTTSProvider(config)
        temp_dir = provider._temp_dir

        assert temp_dir.exists()
        provider.cleanup()
        assert not temp_dir.exists()


class TestTTSEngineIntegration:
    """Test TTSEngine with ElevenLabs provider."""

    @pytest.fixture
    def mock_provider(self):
        """Create a mock TTS provider."""
        provider = Mock()
        provider.config = ElevenLabsConfig(api_key="test")

        async def mock_generate(text, output_path):
            output_path.write_bytes(b"fake audio")
            return output_path

        provider.generate_async = mock_generate
        provider.get_audio_duration = Mock(return_value=3.5)
        provider.cleanup = Mock()
        return provider

    def test_engine_with_elevenlabs_provider(self, mock_provider, tmp_path):
        """Test TTSEngine with ElevenLabs provider."""
        engine = TTSEngine(provider=mock_provider)

        output_path = tmp_path / "output.mp3"
        result = engine.generate("Test text", output_path)

        assert result.exists()
        mock_provider.cleanup.assert_not_called()

        engine.cleanup()
        mock_provider.cleanup.assert_called_once()


class TestProviderFactory:
    """Test provider factory."""

    def test_create_elevenlabs_from_config(self, monkeypatch):
        """Test creating ElevenLabs provider from config."""
        monkeypatch.setenv("MATH_ENGINE_TTS_PROVIDER", "elevenlabs")
        monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "dummy-key")  # Required for Config validation

        config = Config()
        provider = create_tts_provider(config)

        assert isinstance(provider, ElevenLabsTTSProvider)
        assert provider.config.api_key == "test-key"

    def test_create_elevenlabs_with_custom_voice(self, monkeypatch):
        """Test creating ElevenLabs with custom voice."""
        monkeypatch.setenv("MATH_ENGINE_TTS_PROVIDER", "elevenlabs")
        monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "dummy-key")  # Required for Config validation
        monkeypatch.setenv("MATH_ENGINE_TTS_VOICE", "TEACHER_MALE_DEEP")

        config = Config()
        provider = create_tts_provider(config)

        assert provider.config.voice_id == ElevenLabsVoice.TEACHER_MALE_DEEP.value

    def test_create_elevenlabs_missing_api_key(self, monkeypatch):
        """Test that missing API key raises error."""
        monkeypatch.setenv("MATH_ENGINE_TTS_PROVIDER", "elevenlabs")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "dummy-key")  # Required for Config validation
        monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)

        with pytest.raises(ValueError, match="ELEVENLABS_API_KEY"):
            Config()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
