# Configuration Guide

This guide explains how to configure the Math Content Engine using environment variables for TTS voice settings, video presentation styles, and animation preferences.

## Quick Start

1. **Copy the example configuration file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your preferences:**
   ```bash
   nano .env  # or use your preferred editor
   ```

3. **Set your API key:**
   ```bash
   # Required: Set at least one API key
   ANTHROPIC_API_KEY=your-key-here
   # or
   OPENAI_API_KEY=your-key-here
   ```

4. **Run your code:**
   ```python
   from math_content_engine import MathContentEngine

   # Config is automatically loaded from environment
   engine = MathContentEngine()
   result = engine.generate("Pythagorean theorem")
   ```

## Configuration Options

### Text-to-Speech (TTS) Settings

Control voice characteristics for narrated animations.

#### Voice Selection

```bash
MATH_ENGINE_TTS_VOICE=teacher_female
```

**Available voices:**
- `teacher_male` - Male teacher voice (authoritative, reliable)
- `teacher_female` - Female teacher voice (friendly, considerate) **[default]**
- `friendly_male` - Approachable casual male voice
- `friendly_female` - Cheerful clear female voice
- `professional_male` - Professional newsreader style (male)
- `professional_female` - Confident positive voice (female)
- `caring_male` - Warm confident male voice (good for younger audiences)
- `caring_female` - Expressive caring female voice
- `young_female` - Cute cartoon-like voice for young children

#### Voice Tuning

Fine-tune speech characteristics:

```bash
# Speech rate: -50% (slower) to +100% (faster)
MATH_ENGINE_TTS_RATE=+0%

# Volume: -50% (quieter) to +50% (louder)
MATH_ENGINE_TTS_VOLUME=+0%

# Pitch: -100Hz (lower) to +100Hz (higher)
MATH_ENGINE_TTS_PITCH=+0Hz
```

**Examples:**
```bash
# Slower, louder narration for younger students
MATH_ENGINE_TTS_RATE=-20%
MATH_ENGINE_TTS_VOLUME=+10%

# Faster paced for advanced students
MATH_ENGINE_TTS_RATE=+30%

# Higher pitched voice
MATH_ENGINE_TTS_PITCH=+20Hz
```

#### Custom Voice

Use any Microsoft Edge TTS voice:

```bash
# Override voice selection with a custom edge-tts voice
MATH_ENGINE_TTS_CUSTOM_VOICE=en-GB-RyanNeural
```

**Examples:**
- `en-GB-RyanNeural` - British English (male)
- `en-AU-WilliamNeural` - Australian English (male)
- `en-IN-NeerjaNeural` - Indian English (female)
- `es-ES-AlvaroNeural` - Spanish (male)
- `fr-FR-DeniseNeural` - French (female)

[See full list of voices](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts)

### Video Presentation Style

Control how animations are paced and presented.

```bash
MATH_ENGINE_VIDEO_STYLE=step_by_step
```

**Available styles:**
- `standard` - Normal animation flow
- `step_by_step` - Clear pauses between steps, easier to follow **[recommended for learning]**
- `fast_paced` - Quick transitions, less pause time
- `detailed` - Extended timing with extra visual explanations

#### Timing Parameters

Fine-tune step-by-step presentation:

```bash
# Duration of each step (seconds)
MATH_ENGINE_STEP_DURATION=4.0

# Pause between steps (seconds)
MATH_ENGINE_PAUSE_BETWEEN_STEPS=0.5
```

**Examples:**
```bash
# Slower pacing for complex topics
MATH_ENGINE_STEP_DURATION=6.0
MATH_ENGINE_PAUSE_BETWEEN_STEPS=1.0

# Faster pacing for review
MATH_ENGINE_STEP_DURATION=2.5
MATH_ENGINE_PAUSE_BETWEEN_STEPS=0.3
```

### Animation Visual Style

Control background and color scheme.

```bash
MATH_ENGINE_ANIMATION_STYLE=dark
```

**Options:**
- `dark` - Dark background with bright colors **[default]**
- `light` - White background with dark text

### Video Quality

Control output video resolution and frame rate.

```bash
MATH_ENGINE_VIDEO_QUALITY=m
```

**Options:**
- `l` - Low quality (480p, 15fps) - fast rendering
- `m` - Medium quality (720p, 30fps) **[default]** - good balance
- `h` - High quality (1080p, 60fps) - production ready
- `p` - Production quality (1440p, 60fps) - professional
- `k` - 4K quality (2160p, 60fps) - maximum quality

### LLM Settings

Configure the AI model for code generation.

```bash
# Provider: claude or openai
MATH_ENGINE_LLM_PROVIDER=claude

# Model selection (optional)
MATH_ENGINE_CLAUDE_MODEL=claude-sonnet-4-20250514
MATH_ENGINE_OPENAI_MODEL=gpt-4o

# Generation parameters
MATH_ENGINE_MAX_RETRIES=5
MATH_ENGINE_TEMPERATURE=0.7
MATH_ENGINE_MAX_TOKENS=4096
```

### Output Settings

Configure where files are saved.

```bash
# Output directory for generated videos
MATH_ENGINE_OUTPUT_DIR=./output

# Manim cache directory
MATH_ENGINE_MANIM_CACHE=./.manim_cache

# Output video format
MATH_ENGINE_OUTPUT_FORMAT=mp4
```

## Usage Examples

### Example 1: Using Configuration in Code

```python
from math_content_engine import (
    MathContentEngine,
    NarratedAnimationGenerator,
    AnimationScript,
)

# Engine automatically loads config from .env
engine = MathContentEngine()

# Generate animation with configured settings
result = engine.generate(
    topic="Solving quadratic equations",
    audience_level="high school"
)

# TTS generator also uses config automatically
narrator = NarratedAnimationGenerator()  # Uses .env settings

script = AnimationScript("Equation Demo")
script.add_intro("Let's solve this equation step by step.")
script.add_step("First, we move terms to one side.", time=3.0)

# Generate narrated video with configured voice
narrator.create_narrated_video(
    video_path=result.video_path,
    script=script,
    output_path="narrated_output.mp4"
)
```

### Example 2: Overriding Configuration

You can override environment settings programmatically:

```python
from math_content_engine import (
    Config,
    MathContentEngine,
    TTSVoice,
    VideoStyle,
)

# Load base config from .env
config = Config.from_env()

# Override specific settings
config.tts_voice = TTSVoice.FRIENDLY_MALE
config.tts_rate = "+20%"
config.video_style = VideoStyle.FAST_PACED

# Use modified config
engine = MathContentEngine(config=config)
```

### Example 3: Different Configurations for Different Content

Create multiple `.env` files for different use cases:

**`.env.elementary`:**
```bash
MATH_ENGINE_TTS_VOICE=caring_female
MATH_ENGINE_TTS_RATE=-15%
MATH_ENGINE_VIDEO_STYLE=step_by_step
MATH_ENGINE_STEP_DURATION=5.0
```

**`.env.advanced`:**
```bash
MATH_ENGINE_TTS_VOICE=professional_male
MATH_ENGINE_TTS_RATE=+10%
MATH_ENGINE_VIDEO_STYLE=fast_paced
MATH_ENGINE_STEP_DURATION=2.5
```

Load specific config:
```bash
# Load elementary config
cp .env.elementary .env
python my_script.py

# Or load advanced config
cp .env.advanced .env
python my_script.py
```

## Preset Configurations

### For Young Students (Elementary)

```bash
MATH_ENGINE_TTS_VOICE=caring_female
MATH_ENGINE_TTS_RATE=-15%
MATH_ENGINE_TTS_VOLUME=+5%
MATH_ENGINE_VIDEO_STYLE=step_by_step
MATH_ENGINE_STEP_DURATION=5.0
MATH_ENGINE_PAUSE_BETWEEN_STEPS=1.0
MATH_ENGINE_ANIMATION_STYLE=light
MATH_ENGINE_VIDEO_QUALITY=m
```

### For High School Students

```bash
MATH_ENGINE_TTS_VOICE=teacher_female
MATH_ENGINE_TTS_RATE=+0%
MATH_ENGINE_VIDEO_STYLE=step_by_step
MATH_ENGINE_STEP_DURATION=4.0
MATH_ENGINE_PAUSE_BETWEEN_STEPS=0.5
MATH_ENGINE_ANIMATION_STYLE=dark
MATH_ENGINE_VIDEO_QUALITY=h
```

### For College/Advanced Students

```bash
MATH_ENGINE_TTS_VOICE=professional_male
MATH_ENGINE_TTS_RATE=+15%
MATH_ENGINE_VIDEO_STYLE=standard
MATH_ENGINE_STEP_DURATION=3.0
MATH_ENGINE_PAUSE_BETWEEN_STEPS=0.3
MATH_ENGINE_ANIMATION_STYLE=dark
MATH_ENGINE_VIDEO_QUALITY=h
```

### For Quick Review/Recap Videos

```bash
MATH_ENGINE_TTS_VOICE=friendly_female
MATH_ENGINE_TTS_RATE=+25%
MATH_ENGINE_VIDEO_STYLE=fast_paced
MATH_ENGINE_STEP_DURATION=2.0
MATH_ENGINE_PAUSE_BETWEEN_STEPS=0.2
MATH_ENGINE_VIDEO_QUALITY=m
```

## Troubleshooting

### Configuration Not Loading

**Problem:** Changes to `.env` file not taking effect.

**Solutions:**
1. Make sure `.env` is in the working directory where you run the script
2. Restart your Python interpreter/kernel
3. Check for typos in variable names (must match exactly)
4. Verify no quotes around values in `.env` file

### Voice Sounds Wrong

**Problem:** Voice doesn't match the selected setting.

**Solutions:**
1. Check `MATH_ENGINE_TTS_CUSTOM_VOICE` isn't overriding your voice selection
2. Verify edge-tts is installed: `pip install edge-tts`
3. Test voice: `python examples/config_demo.py`

### Invalid Configuration Error

**Problem:** Error message about invalid configuration values.

**Solutions:**
1. Check enum values are spelled correctly (lowercase, underscores)
2. Verify percentage values have `%` suffix: `+10%` not `+10`
3. Verify pitch values have `Hz` suffix: `+5Hz` not `+5`

## See Also

- [Examples Directory](../examples/) - Example scripts using configuration
- [.env.example](../.env.example) - Complete configuration template
- [config_demo.py](../examples/config_demo.py) - Interactive configuration demo

## Advanced Configuration

### Environment Variable Priority

Configuration is loaded in this order (later overrides earlier):
1. Default values in `config.py`
2. Environment variables from `.env` file
3. Programmatic overrides in code

### Creating Custom Voice Mappings

You can create your own voice presets by subclassing `Config`:

```python
from math_content_engine.config import Config, TTSVoice
from enum import Enum

class MyTTSVoice(Enum):
    CUSTOM_VOICE_1 = "custom_1"
    CUSTOM_VOICE_2 = "custom_2"

# Map to actual edge-tts voices
voice_mapping = {
    MyTTSVoice.CUSTOM_VOICE_1: "en-GB-RyanNeural",
    MyTTSVoice.CUSTOM_VOICE_2: "en-AU-WilliamNeural",
}
```

### Dynamic Configuration

Change configuration at runtime:

```python
config = Config.from_env()

# Generate with one voice
config.tts_voice = TTSVoice.TEACHER_MALE
engine = MathContentEngine(config=config)
result1 = engine.generate("Topic 1")

# Switch to different voice for next generation
config.tts_voice = TTSVoice.FRIENDLY_FEMALE
engine = MathContentEngine(config=config)
result2 = engine.generate("Topic 2")
```
