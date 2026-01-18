"""
Tests for ElevenLabs TTS integration.

Run with:
    ELEVENLABS_API_KEY=your-key pytest tests/test_elevenlabs_tts.py -v
"""

import os
import pytest
from pathlib import Path
import asyncio

from math_content_engine.tts import (
    ElevenLabsTTSProvider,
    ElevenLabsConfig,
    ElevenLabsVoice,
    TTSEngine,
    create_tts_provider,
)
from math_content_engine import Config
from math_content_engine.config import TTSProvider


@pytest.fixture
def api_key():
    """Get ElevenLabs API key from environment."""
    key = os.getenv("ELEVENLABS_API_KEY")
    if not key:
        pytest.skip("ELEVENLABS_API_KEY not set")
    return key


@pytest.fixture
def output_dir(tmp_path):
    """Create a temporary output directory."""
    output = tmp_path / "elevenlabs_output"
    output.mkdir(exist_ok=True)
    return output


@pytest.fixture
def elevenlabs_config(api_key):
    """Create ElevenLabs configuration."""
    return ElevenLabsConfig(
        api_key=api_key,
        voice_id=ElevenLabsVoice.TEACHER_FEMALE_CALM.value,
    )


class TestElevenLabsProvider:
    """Test ElevenLabs TTS provider directly."""

    @pytest.mark.asyncio
    async def test_generate_simple_audio(self, elevenlabs_config, output_dir):
        """Test basic audio generation."""
        provider = ElevenLabsTTSProvider(elevenlabs_config)

        text = "Hello, let's learn about linear equations."
        output_path = output_dir / "test_simple.mp3"

        result_path = await provider.generate_async(text, output_path)

        assert result_path.exists()
        assert result_path.stat().st_size > 0
        print(f"Generated audio: {result_path}")
        print(f"Audio size: {result_path.stat().st_size} bytes")

        provider.cleanup()

    @pytest.mark.asyncio
    async def test_generate_math_narration(self, elevenlabs_config, output_dir):
        """Test generating narration for math content."""
        provider = ElevenLabsTTSProvider(elevenlabs_config)

        text = """
        Let's solve the equation 2x plus 3 equals 7.
        First, we'll subtract 3 from both sides to isolate the term with x.
        This gives us 2x equals 4.
        Now, we divide both sides by 2 to find x equals 2.
        Let's verify: 2 times 2 plus 3 equals 4 plus 3, which equals 7.
        Our solution is correct!
        """

        output_path = output_dir / "test_math_narration.mp3"
        result_path = await provider.generate_async(text, output_path)

        assert result_path.exists()
        assert result_path.stat().st_size > 0

        # Check audio duration
        duration = provider.get_audio_duration(result_path)
        assert duration > 0
        print(f"Audio duration: {duration:.2f} seconds")

        provider.cleanup()

    def test_list_voices(self, elevenlabs_config):
        """Test listing available voices."""
        provider = ElevenLabsTTSProvider(elevenlabs_config)

        voices = provider.list_voices()
        assert len(voices) > 0
        assert all("voice_id" in v and "name" in v for v in voices)

        print(f"\nAvailable ElevenLabs voices ({len(voices)} total):")
        for voice in voices[:5]:  # Print first 5
            print(f"  - {voice['name']} ({voice['voice_id']})")

        provider.cleanup()


class TestTTSEngine:
    """Test TTS engine with ElevenLabs provider."""

    def test_tts_engine_with_elevenlabs(self, elevenlabs_config, output_dir):
        """Test TTSEngine using ElevenLabs provider."""
        provider = ElevenLabsTTSProvider(elevenlabs_config)
        engine = TTSEngine(provider=provider)

        text = "The quadratic formula is x equals negative b plus or minus the square root of b squared minus 4ac, all over 2a."
        output_path = output_dir / "test_quadratic.mp3"

        result_path = engine.generate(text, output_path)

        assert result_path.exists()
        assert result_path.stat().st_size > 0

        # Check duration
        duration = engine._get_audio_duration(result_path)
        print(f"Quadratic formula audio duration: {duration:.2f}s")

        engine.cleanup()


class TestProviderFactory:
    """Test TTS provider factory."""

    def test_create_elevenlabs_provider(self, api_key):
        """Test creating ElevenLabs provider from config."""
        # Set environment variables
        os.environ["MATH_ENGINE_TTS_PROVIDER"] = "elevenlabs"
        os.environ["ELEVENLABS_API_KEY"] = api_key

        config = Config()
        provider = create_tts_provider(config)

        assert isinstance(provider, ElevenLabsTTSProvider)
        assert provider.config.api_key == api_key

        provider.cleanup()

    def test_create_elevenlabs_with_custom_voice(self, api_key):
        """Test creating ElevenLabs provider with custom voice."""
        os.environ["MATH_ENGINE_TTS_PROVIDER"] = "elevenlabs"
        os.environ["ELEVENLABS_API_KEY"] = api_key
        os.environ["MATH_ENGINE_TTS_VOICE"] = "TEACHER_MALE_DEEP"

        config = Config()
        provider = create_tts_provider(config)

        assert isinstance(provider, ElevenLabsTTSProvider)
        assert provider.config.voice_id == ElevenLabsVoice.TEACHER_MALE_DEEP.value

        provider.cleanup()

        # Clean up env vars
        del os.environ["MATH_ENGINE_TTS_VOICE"]


class TestIntegration:
    """Integration tests for ElevenLabs TTS."""

    @pytest.mark.slow
    def test_full_narration_generation(self, api_key, output_dir):
        """Test complete narration generation workflow."""
        os.environ["MATH_ENGINE_TTS_PROVIDER"] = "elevenlabs"
        os.environ["ELEVENLABS_API_KEY"] = api_key

        from math_content_engine.tts import NarrationScript

        config = Config()
        provider = create_tts_provider(config)
        engine = TTSEngine(provider=provider)

        # Create a narration script
        script = NarrationScript()
        script.add_segment("Welcome to our lesson on linear equations.", 0.0)
        script.add_segment("Today we'll solve 2x plus 3 equals 7.", 3.0)
        script.add_segment("First, subtract 3 from both sides.", 6.0)
        script.add_segment("This gives us 2x equals 4.", 9.0)
        script.add_segment("Finally, divide by 2 to get x equals 2.", 12.0)

        # Generate all segments
        result_script = engine.generate_script(script, output_dir)

        # Verify all segments were generated
        assert len(result_script.segments) == 5
        for i, segment in enumerate(result_script.segments):
            assert segment.audio_path is not None
            assert segment.audio_path.exists()
            assert segment.duration > 0
            print(f"Segment {i+1}: {segment.duration:.2f}s - {segment.text[:40]}...")

        print(f"Total narration duration: {result_script.total_duration:.2f}s")

        engine.cleanup()


if __name__ == "__main__":
    # Quick test
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("Please set ELEVENLABS_API_KEY environment variable")
        exit(1)

    print("Testing ElevenLabs TTS Provider...")

    config = ElevenLabsConfig(api_key=api_key)
    provider = ElevenLabsTTSProvider(config)

    output_dir = Path("./test_output")
    output_dir.mkdir(exist_ok=True)

    async def test():
        text = "Hello! This is a test of the ElevenLabs text-to-speech system for math education."
        output = output_dir / "elevenlabs_test.mp3"
        result = await provider.generate_async(text, output)
        print(f"Audio generated: {result}")
        print(f"Duration: {provider.get_audio_duration(result):.2f}s")

    asyncio.run(test())
    provider.cleanup()
    print("Test complete!")
