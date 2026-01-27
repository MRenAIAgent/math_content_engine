"""
Configuration Demo - Using environment variables to control TTS and video style

This example demonstrates how to use configuration files (.env) to control:
1. TTS voice selection and tuning (rate, volume, pitch)
2. Video presentation style (step-by-step, fast-paced, etc.)
3. Animation visual style (dark, light)

Setup:
    1. Copy .env.example to .env
    2. Modify the settings in .env
    3. Run this script to see the configuration in action

Configuration Options in .env:

    # TTS Voice Settings
    MATH_ENGINE_TTS_VOICE=teacher_male              # Voice selection
    MATH_ENGINE_TTS_RATE=-10%                       # Slower speech
    MATH_ENGINE_TTS_VOLUME=+10%                     # Louder volume
    MATH_ENGINE_TTS_PITCH=+5Hz                      # Slightly higher pitch

    # Video Style
    MATH_ENGINE_VIDEO_STYLE=step_by_step            # Clear step-by-step presentation
    MATH_ENGINE_STEP_DURATION=4.0                   # 4 seconds per step
    MATH_ENGINE_PAUSE_BETWEEN_STEPS=0.5             # 0.5 second pauses

    # Animation Style
    MATH_ENGINE_ANIMATION_STYLE=dark                # Dark or light background

Run:
    python examples/config_demo.py
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from math_content_engine import (
    Config,
    MathContentEngine,
    TTSVoice,
    VideoStyle,
    AnimationStyle,
)

try:
    from math_content_engine import NarratedAnimationGenerator, AnimationScript
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("Warning: TTS not available. Install with: pip install edge-tts")


def print_config(config: Config):
    """Display the current configuration."""
    print("\n" + "=" * 60)
    print("CURRENT CONFIGURATION (loaded from environment)")
    print("=" * 60)

    print("\n🎨 Animation Settings:")
    print(f"  Style: {config.animation_style.value}")
    print(f"  Quality: {config.video_quality.value}")
    print(f"  Output: {config.output_dir}")

    print("\n🎤 TTS Settings:")
    print(f"  Voice: {config.tts_voice.value}")
    print(f"  Rate: {config.tts_rate}")
    print(f"  Volume: {config.tts_volume}")
    print(f"  Pitch: {config.tts_pitch}")
    if config.tts_custom_voice:
        print(f"  Custom Voice: {config.tts_custom_voice}")

    print("\n🎬 Video Style Settings:")
    print(f"  Style: {config.video_style.value}")
    print(f"  Step Duration: {config.step_duration}s")
    print(f"  Pause Between Steps: {config.pause_between_steps}s")

    print("\n🤖 LLM Settings:")
    print(f"  Provider: {config.llm_provider.value}")
    print(f"  Model: {config.get_model()}")
    print(f"  Max Retries: {config.max_retries}")

    print("\n" + "=" * 60 + "\n")


def demo_config_loading():
    """Demonstrate loading configuration from environment."""
    print("\n📋 Demo 1: Loading Configuration from Environment Variables")
    print("-" * 60)

    # Load config from environment (.env file)
    config = Config.from_env()
    print_config(config)

    return config


def demo_programmatic_override():
    """Demonstrate programmatically overriding configuration."""
    print("\n📋 Demo 2: Programmatically Overriding Configuration")
    print("-" * 60)

    # Load base config from environment
    config = Config.from_env()

    # Override specific settings programmatically
    config.tts_voice = TTSVoice.FRIENDLY_MALE
    config.tts_rate = "+20%"
    config.video_style = VideoStyle.FAST_PACED
    config.animation_style = AnimationStyle.LIGHT

    print("✅ Overridden settings:")
    print(f"  TTS Voice: {config.tts_voice.value}")
    print(f"  TTS Rate: {config.tts_rate}")
    print(f"  Video Style: {config.video_style.value}")
    print(f"  Animation Style: {config.animation_style.value}")

    return config


def demo_tts_generator():
    """Demonstrate using config with TTS generator."""
    if not TTS_AVAILABLE:
        print("\n⚠️  Skipping TTS demo (edge-tts not installed)")
        return

    print("\n📋 Demo 3: Using Config with NarratedAnimationGenerator")
    print("-" * 60)

    # Load config - TTS settings are automatically applied
    config = Config.from_env()

    # Create generator - it will use the config settings
    generator = NarratedAnimationGenerator(config=config)

    print(f"✅ NarratedAnimationGenerator created with config:")
    print(f"  Voice: {config.tts_voice.value}")
    print(f"  Rate: {config.tts_rate}")
    print(f"  Volume: {config.tts_volume}")
    print(f"  Pitch: {config.tts_pitch}")

    # Create a simple script
    script = AnimationScript("Configuration Demo")
    script.add_intro("This narration uses your configured voice settings.")
    script.add_step("The voice, speed, volume, and pitch are all from your .env file.", time=4.0)
    script.add_conclusion("Pretty cool, right?", time=8.0)

    print(f"\n✅ Animation script created with {len(script.cues)} cues")
    print("   (To generate audio, provide a video file to create_narrated_video)")


def demo_engine_integration():
    """Demonstrate config integration with MathContentEngine."""
    print("\n📋 Demo 4: Config with MathContentEngine")
    print("-" * 60)

    # Create config
    config = Config.from_env()

    # Engine automatically uses all config settings
    engine = MathContentEngine(config=config)

    print("✅ MathContentEngine initialized with config:")
    print(f"  LLM Provider: {config.llm_provider.value}")
    print(f"  Animation Style: {config.animation_style.value}")
    print(f"  Video Quality: {config.video_quality.value}")
    print(f"  TTS Voice: {config.tts_voice.value}")

    print("\n💡 The engine is ready to generate animations with your configured settings!")
    print("   Example: engine.generate('Pythagorean theorem')")


def demo_available_options():
    """Display all available configuration options."""
    print("\n📋 Demo 5: Available Configuration Options")
    print("-" * 60)

    print("\n🎤 Available TTS Voices:")
    for voice in TTSVoice:
        print(f"  - {voice.value}")

    print("\n🎬 Available Video Styles:")
    for style in VideoStyle:
        print(f"  - {style.value}")

    print("\n🎨 Available Animation Styles:")
    for style in AnimationStyle:
        print(f"  - {style.value}")


def main():
    """Run all configuration demos."""
    print("\n" + "=" * 60)
    print("MATH CONTENT ENGINE - CONFIGURATION DEMO")
    print("=" * 60)

    try:
        # Demo 1: Load from environment
        config = demo_config_loading()

        # Demo 2: Programmatic override
        demo_programmatic_override()

        # Demo 3: TTS generator with config
        demo_tts_generator()

        # Demo 4: Engine integration
        demo_engine_integration()

        # Demo 5: Available options
        demo_available_options()

        print("\n" + "=" * 60)
        print("✅ Configuration demo complete!")
        print("=" * 60)
        print("\n💡 Tips:")
        print("  1. Copy .env.example to .env and customize your settings")
        print("  2. All settings are optional - defaults are provided")
        print("  3. Environment variables override code defaults")
        print("  4. You can still override programmatically if needed")
        print("\n")

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\n💡 Make sure you have set the required API key in your .env file:")
        print("   ANTHROPIC_API_KEY=your-key-here")
        print("   or")
        print("   OPENAI_API_KEY=your-key-here")


if __name__ == "__main__":
    main()
