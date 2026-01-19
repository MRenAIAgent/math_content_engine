# ElevenLabs Integration Tests

This guide explains how to run the algebra linear equation integration tests with ElevenLabs voice narration.

## Overview

The ElevenLabs integration tests demonstrate the full pipeline:
1. **Graphics Generation**: Create a Manim animation with visual step-by-step equation solving
2. **Voice Narration**: Add high-quality ElevenLabs AI voice narration
3. **Video Combination**: Merge the graphics and voice into a final educational video

## Prerequisites

### 1. Install Dependencies

Make sure you have the TTS dependencies installed:

```bash
# Install with ElevenLabs support
pip install -e ".[tts]"

# Or install all dependencies
pip install -e ".[all]"
```

This installs:
- `elevenlabs` - ElevenLabs Python SDK
- `ffmpeg-python` - For video/audio combining
- `edge-tts` - Alternative free TTS provider

### 2. System Requirements

- **FFmpeg**: Required for video processing
  ```bash
  # macOS
  brew install ffmpeg

  # Ubuntu/Debian
  sudo apt install ffmpeg
  ```

- **Manim**: Required for rendering animations
  ```bash
  pip install manim

  # System dependencies for Manim
  # macOS: brew install cairo pkg-config pango
  # Ubuntu: sudo apt install libcairo2-dev libpango1.0-dev pkg-config
  ```

### 3. API Keys

Get an ElevenLabs API key:
1. Sign up at https://elevenlabs.io/
2. Navigate to your profile settings
3. Copy your API key
4. Set the environment variable:

```bash
export ELEVENLABS_API_KEY="your-api-key-here"
```

You also need an LLM API key for code generation:

```bash
# For Claude (recommended)
export ANTHROPIC_API_KEY="sk-ant-..."

# OR for OpenAI
export OPENAI_API_KEY="sk-..."
```

## Running the Tests

### Quick Test: ElevenLabs Audio Only (Fast)

Test just the ElevenLabs TTS without rendering video:

```bash
pytest tests/test_algebra_integration.py::TestAlgebraElevenLabsNarration::test_elevenlabs_tts_generation_only -v
```

**What it does:**
- Verifies ElevenLabs API key is valid
- Generates a sample audio file
- Saves output to `tests/test_output/test_elevenlabs_audio.mp3`

**Expected runtime:** ~5-10 seconds

### Full Test: Complete Video with Graphics + Voice (Slow)

Run the full integration test:

```bash
pytest tests/test_algebra_integration.py::TestAlgebraElevenLabsNarration::test_linear_equation_with_elevenlabs_narration -v
```

**What it does:**
1. Generates Manim code for solving "2x + 3 = 7"
2. Renders the animation with graphics (number line, steps, colors)
3. Creates a narration script with 6 voice cues
4. Generates ElevenLabs voice audio for each cue
5. Combines video and audio into final narrated video

**Expected runtime:** 1-3 minutes (depending on LLM and render speed)

**Output files** (in `tests/test_output/`):
- `elevenlabs_linear_base.py` - Generated Manim code
- `elevenlabs_linear_base_meta.txt` - Base video metadata
- `linear_equation_elevenlabs_narrated.mp4` - **Final narrated video** ⭐
- `elevenlabs_linear_narrated_meta.txt` - Test metadata

### Run All ElevenLabs Tests

```bash
pytest tests/test_algebra_integration.py::TestAlgebraElevenLabsNarration -v
```

## Customizing the Voice

You can customize which ElevenLabs voice is used:

```bash
# Use a specific voice ID (see ElevenLabs voice library)
export MATH_ENGINE_TTS_VOICE="21m00Tcm4TlvDq8ikWAM"  # Rachel (calm female)

# Or use a voice name from ElevenLabsVoice enum:
export MATH_ENGINE_TTS_VOICE="TEACHER_MALE_DEEP"    # Josh (deep male)

# Run test
pytest tests/test_algebra_integration.py::TestAlgebraElevenLabsNarration::test_linear_equation_with_elevenlabs_narration -v
```

**Available pre-configured voices:**
- `TEACHER_FEMALE_CALM` - Rachel (default, warm and clear)
- `TEACHER_FEMALE_CLEAR` - Bella (soft, articulate)
- `TEACHER_MALE_DEEP` - Josh (authoritative, clear)
- `TEACHER_MALE_CLEAR` - Antoni (well-rounded, friendly)

See `src/math_content_engine/tts/elevenlabs_provider.py` for all available voices.

## Test Output

After running the full test, you'll get:

```
tests/test_output/
├── elevenlabs_linear_base.py              # Generated Manim code
├── elevenlabs_linear_base_meta.txt        # Metadata from base video
├── linear_equation_elevenlabs_narrated.mp4  # Final video with voice! 🎥🔊
└── elevenlabs_linear_narrated_meta.txt    # Test metadata
```

**Play the video:**
```bash
# macOS
open tests/test_output/linear_equation_elevenlabs_narrated.mp4

# Linux
xdg-open tests/test_output/linear_equation_elevenlabs_narrated.mp4

# Windows
start tests/test_output/linear_equation_elevenlabs_narrated.mp4
```

## Troubleshooting

### "ELEVENLABS_API_KEY not set"

Make sure you've exported the API key:
```bash
export ELEVENLABS_API_KEY="your-key"
echo $ELEVENLABS_API_KEY  # Verify it's set
```

### "No API key configured" (LLM)

You need an LLM API key for generating the Manim code:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# OR
export OPENAI_API_KEY="sk-..."
```

### FFmpeg errors

Make sure FFmpeg is installed:
```bash
ffmpeg -version  # Should show version info
```

### "elevenlabs module not found"

Install the TTS dependencies:
```bash
pip install -e ".[tts]"
```

### Audio but no video / Video but no audio

This usually means FFmpeg failed to combine them. Check:
1. FFmpeg is installed and in PATH
2. Both video and audio files were generated
3. Check the error message in test output

## Architecture

The test demonstrates this flow:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. MathContentEngine.generate()                             │
│    - LLM generates Manim code                               │
│    - Renders animation with graphics                        │
│    - Output: base_video.mp4                                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. AnimationScript                                          │
│    - Define narration cues with timing                      │
│    - "Let's solve 2x + 3 = 7" @ 0s                         │
│    - "Subtract 3 from both sides" @ 6s                      │
│    - etc.                                                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. NarratedAnimationGenerator                               │
│    - create_tts_provider(config) → ElevenLabsTTSProvider   │
│    - Generate audio for each cue                            │
│    - AudioVideoCombiner.combine_segments()                  │
│    - Output: narrated_video.mp4                             │
└─────────────────────────────────────────────────────────────┘
```

## Code Structure

Key files:
- `tests/test_algebra_integration.py` - Integration tests (this is where the test lives)
- `src/math_content_engine/engine.py` - Main engine for video generation
- `src/math_content_engine/tts/elevenlabs_provider.py` - ElevenLabs TTS provider
- `src/math_content_engine/tts/narrated_animation.py` - Narration combining logic
- `src/math_content_engine/tts/audio_video_combiner.py` - FFmpeg audio/video merge

## Next Steps

After running the tests successfully, you can:

1. **Use in your own code:**
   ```python
   from math_content_engine import MathContentEngine, Config
   from math_content_engine.config import TTSProvider
   from math_content_engine.tts import NarratedAnimationGenerator, AnimationScript

   # Generate base video
   config = Config()
   config.tts_provider = TTSProvider.ELEVENLABS
   engine = MathContentEngine(config)
   result = engine.generate("Solve 3x - 5 = 10", output_filename="my_video")

   # Add narration
   script = AnimationScript("My Equation")
   script.add_intro("Let's solve this equation step by step")
   # ... add more cues

   narration_gen = NarratedAnimationGenerator(config=config)
   narrated = narration_gen.create_narrated_video(
       video_path=result.video_path,
       script=script,
       output_path="my_narrated_video.mp4"
   )
   ```

2. **Try different equations:**
   - Modify the test to solve different equations
   - Experiment with different visual styles
   - Try different narration scripts

3. **Compare TTS providers:**
   - Test with Edge TTS (free): `config.tts_provider = TTSProvider.EDGE`
   - Compare voice quality and cost

## Cost Considerations

ElevenLabs charges per character:
- Free tier: ~10,000 characters/month
- Paid: Starting at $5/month for 30,000 characters

This test uses approximately:
- ~300 characters for narration
- Cost: < $0.01 per test run

Monitor your usage at: https://elevenlabs.io/subscription

---

**Happy testing! 🎓🎬**

For more information, see:
- Main README: `README.md`
- CLAUDE.md for build commands
- ElevenLabs docs: https://elevenlabs.io/docs
