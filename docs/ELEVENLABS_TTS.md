# ElevenLabs TTS Integration

This document describes how to use ElevenLabs TTS provider in the Math Content Engine.

## Overview

The Math Content Engine now supports multiple TTS providers:
- **Edge TTS** (default): Free Microsoft Edge neural TTS, no API key required
- **ElevenLabs**: Premium quality TTS with natural voices, requires API key

## Installation

Install the TTS dependencies including ElevenLabs support:

```bash
pip install -e ".[tts]"
```

This installs:
- `edge-tts` - Microsoft Edge TTS (free)
- `elevenlabs` - ElevenLabs SDK
- `mutagen` - Audio duration detection

## Configuration

### Environment Variables

Set the TTS provider and API key:

```bash
export MATH_ENGINE_TTS_PROVIDER=elevenlabs  # or "edge" (default)
export ELEVENLABS_API_KEY=your-api-key-here
```

Optional voice selection:

```bash
export MATH_ENGINE_TTS_VOICE=TEACHER_FEMALE_CALM  # Voice enum name or ID
```

### Available ElevenLabs Voices

Pre-configured voice styles for education:

- `TEACHER_FEMALE_CALM` - Rachel (calm, clear)
- `TEACHER_FEMALE_CLEAR` - Bella (soft, clear)
- `TEACHER_MALE_DEEP` - Josh (deep, authoritative)
- `TEACHER_MALE_CLEAR` - Antoni (well-rounded)

Other high-quality voices:

- `RACHEL` - American Female, Calm
- `DOMI` - American Female, Strong
- `BELLA` - American Female, Soft
- `ANTONI` - American Male, Well-rounded
- `ELLI` - American Female, Emotional
- `JOSH` - American Male, Deep
- `ARNOLD` - American Male, Crisp
- `ADAM` - American Male, Deep
- `SAM` - American Male, Dynamic

## Usage Examples

### Basic Usage with Factory

The simplest way is to use the factory function:

```python
import os
from math_content_engine import Config
from math_content_engine.tts import create_tts_provider, TTSEngine

# Configure via environment
os.environ["MATH_ENGINE_TTS_PROVIDER"] = "elevenlabs"
os.environ["ELEVENLABS_API_KEY"] = "your-key"

# Create provider from config
config = Config()
provider = create_tts_provider(config)
engine = TTSEngine(provider=provider)

# Generate audio
audio_path = engine.generate("Let's solve 2x + 3 = 7", "output.mp3")
print(f"Audio saved to: {audio_path}")
```

### Direct Provider Usage

For more control, create the provider directly:

```python
from math_content_engine.tts import (
    ElevenLabsTTSProvider,
    ElevenLabsConfig,
    ElevenLabsVoice,
)
import asyncio

# Configure ElevenLabs
config = ElevenLabsConfig(
    api_key="your-api-key",
    voice_id=ElevenLabsVoice.TEACHER_MALE_DEEP.value,
    stability=0.5,
    similarity_boost=0.75,
)

# Create provider
provider = ElevenLabsTTSProvider(config)

# Generate audio (async)
async def generate():
    audio_path = await provider.generate_async(
        "The quadratic formula is x equals negative b plus or minus...",
        Path("quadratic.mp3")
    )
    return audio_path

audio_path = asyncio.run(generate())
print(f"Generated: {audio_path}")
```

### Using with Math Content Engine

Generate narrated math animations:

```python
from math_content_engine import MathContentEngine, Config
from math_content_engine.tts import (
    NarratedAnimationGenerator,
    create_tts_provider,
)
import os

# Configure
os.environ["MATH_ENGINE_TTS_PROVIDER"] = "elevenlabs"
os.environ["ELEVENLABS_API_KEY"] = "your-key"

# Create engine and generate animation
config = Config()
engine = MathContentEngine(config)

animation_result = engine.generate(
    topic="Solving linear equations",
    requirements="Show steps for solving 2x + 3 = 7",
    output_filename="linear_equation"
)

# Create narrated version with ElevenLabs
provider = create_tts_provider(config)
narrator = NarratedAnimationGenerator(provider=provider)

# Add narration script
from math_content_engine.tts import AnimationScript

script = AnimationScript("Linear Equations")
script.add_intro("Let's solve the equation 2x + 3 = 7", time=0.0)
script.add_step("First, subtract 3 from both sides", time=3.0)
script.add_step("This gives us 2x = 4", time=6.0)
script.add_step("Finally, divide by 2 to get x = 2", time=9.0)

result = narrator.create_narrated_video(
    video_path=animation_result.video_path,
    script=script,
    output_path="narrated_linear_equation.mp4"
)
```

### List Available Voices

```python
from math_content_engine.tts import ElevenLabsTTSProvider, ElevenLabsConfig

config = ElevenLabsConfig(api_key="your-key")
provider = ElevenLabsTTSProvider(config)

voices = provider.list_voices()
for voice in voices:
    print(f"{voice['name']} ({voice['voice_id']})")
```

## Voice Settings

Customize voice characteristics:

```python
from math_content_engine.tts import ElevenLabsConfig

config = ElevenLabsConfig(
    api_key="your-key",
    voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel
    stability=0.7,           # 0.0-1.0: Higher = more stable/monotone
    similarity_boost=0.8,    # 0.0-1.0: Higher = more similar to original
    style=0.2,              # 0.0-1.0: Style exaggeration
    use_speaker_boost=True, # Enhance clarity
)
```

## Testing

Run the unit tests (no API key required):

```bash
pytest tests/test_elevenlabs_unit.py -v
```

Run integration tests (requires valid API key):

```bash
ELEVENLABS_API_KEY=your-key pytest tests/test_elevenlabs_tts.py -v
```

## Architecture

The TTS system uses a provider abstraction pattern:

```
TTSEngine (high-level API)
    ↓
BaseTTSProvider (abstract interface)
    ↓
├── EdgeTTSProvider (free, no API key)
└── ElevenLabsTTSProvider (premium, requires API key)
```

### Key Components

1. **BaseTTSProvider**: Abstract base class defining the TTS interface
2. **ElevenLabsTTSProvider**: ElevenLabs implementation
3. **EdgeTTSProvider**: Microsoft Edge TTS implementation
4. **TTSEngine**: High-level engine that wraps providers
5. **create_tts_provider()**: Factory function for creating providers from config

## Troubleshooting

### API Key Issues

If you get authentication errors:

```python
# Verify your API key is set
import os
print(os.getenv("ELEVENLABS_API_KEY"))

# Test directly
from elevenlabs import ElevenLabs
client = ElevenLabs(api_key="your-key")
voices = client.voices.get_all()
print(f"Found {len(voices.voices)} voices")
```

### Network/Proxy Issues

If you're behind a corporate proxy, you may need to configure proxy settings:

```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

### Audio Duration Detection

If duration detection fails, ensure `mutagen` is installed:

```bash
pip install mutagen
```

## Comparison: Edge TTS vs ElevenLabs

| Feature | Edge TTS | ElevenLabs |
|---------|----------|------------|
| Cost | Free | Paid (API key) |
| Quality | Good | Excellent |
| Voices | Many options | Premium voices |
| API Key | Not required | Required |
| Subtitles | Supported | Not supported |
| Rate Limits | Generous | Based on plan |
| Best For | Development, testing | Production, high-quality content |

## Best Practices

1. **Development**: Use Edge TTS for development and testing
2. **Production**: Use ElevenLabs for final, high-quality content
3. **Voice Selection**: Choose TEACHER_* voices for educational content
4. **Settings**: Start with default stability/similarity, adjust as needed
5. **Error Handling**: Always handle API errors gracefully with fallback to Edge TTS

## Example: Fallback Pattern

```python
from math_content_engine.tts import create_tts_provider, EdgeTTSProvider, EdgeTTSConfig
from math_content_engine import Config

try:
    # Try ElevenLabs first
    config = Config()
    provider = create_tts_provider(config)
except Exception as e:
    print(f"ElevenLabs unavailable: {e}")
    print("Falling back to Edge TTS")
    provider = EdgeTTSProvider(EdgeTTSConfig())

engine = TTSEngine(provider=provider)
```

## API Reference

See the module docstrings for detailed API documentation:

```python
help(ElevenLabsTTSProvider)
help(ElevenLabsConfig)
help(create_tts_provider)
```
