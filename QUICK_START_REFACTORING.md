# Quick Start: Using Centralized Enums

## What Changed?

All enum definitions have been centralized to eliminate duplication and provide a single source of truth.

## New Import Pattern

### Before (Old Way - Still Works!)
```python
from math_content_engine.config import AnimationStyle, VideoQuality, LLMProvider
```

### After (Recommended)
```python
from math_content_engine.constants import AnimationStyle, VideoQuality, LLMProvider
```

### Also Works (Backward Compatible)
```python
# Config still re-exports for compatibility
from math_content_engine.config import AnimationStyle

# Prompts still works
from math_content_engine.generator.prompts import AnimationStyle
```

## Available Enums

### From `math_content_engine.constants`:

```python
# LLM Providers
from math_content_engine.constants import LLMProvider
LLMProvider.CLAUDE    # "claude"
LLMProvider.OPENAI    # "openai"

# Video Quality
from math_content_engine.constants import VideoQuality
VideoQuality.LOW          # "l" - 480p, 15fps
VideoQuality.MEDIUM       # "m" - 720p, 30fps
VideoQuality.HIGH         # "h" - 1080p, 60fps
VideoQuality.PRODUCTION   # "p" - 1440p, 60fps
VideoQuality.FOURK        # "k" - 4K, 60fps

# Animation Style
from math_content_engine.constants import AnimationStyle
AnimationStyle.DARK    # "dark" - Dark background
AnimationStyle.LIGHT   # "light" - Light background

# TTS Voice
from math_content_engine.constants import TTSVoice
TTSVoice.TEACHER_MALE
TTSVoice.TEACHER_FEMALE
TTSVoice.FRIENDLY_MALE
TTSVoice.FRIENDLY_FEMALE
# ... and more

# Video Style
from math_content_engine.constants import VideoStyle
VideoStyle.STANDARD
VideoStyle.STEP_BY_STEP
VideoStyle.FAST_PACED
VideoStyle.DETAILED

# TTS Provider
from math_content_engine.constants import TTSProvider
TTSProvider.EDGE         # "edge" - Microsoft Edge TTS (free)
TTSProvider.ELEVENLABS   # "elevenlabs" - ElevenLabs (requires API key)
```

## Migration Guide

### For Existing Code

**No changes required!** All old imports still work due to re-exports in `config.py` and `prompts.py`.

### For New Code

Use the centralized imports:

```python
# Instead of:
from math_content_engine.config import AnimationStyle, VideoQuality

# Use:
from math_content_engine.constants import AnimationStyle, VideoQuality
```

### For API/Pydantic Models

The API models maintain Pydantic compatibility with `str, Enum` pattern:

```python
# api/models.py still has Pydantic-compatible versions
from math_content_engine.api.models import AnimationStyle, VideoQuality

# These work with Pydantic BaseModel
class VideoCreate(BaseModel):
    style: AnimationStyle = AnimationStyle.DARK  # ✅ Works with Pydantic
```

## Testing

All 88 tests pass, including new tests for enum consistency:

```bash
# Run all tests
pytest tests/test_validators.py tests/test_code_extractor.py tests/test_config.py tests/test_constants.py tests/test_templates.py -v

# Run just enum tests
pytest tests/test_constants.py -v
```

## Benefits

1. ✅ **Single Source of Truth** - All enums defined once in `constants/enums.py`
2. ✅ **No Duplication** - Eliminated 4 duplicate enum definitions
3. ✅ **Backward Compatible** - Old imports still work
4. ✅ **Better Organization** - Clear separation of constants
5. ✅ **Easier Maintenance** - Add new enum values in one place

## File Structure

```
src/math_content_engine/
├── constants/           # NEW - Single source of truth
│   ├── __init__.py      # Public exports
│   └── enums.py         # All enum definitions
├── config.py            # Re-exports for backward compatibility
├── generator/
│   └── prompts.py       # Re-exports AnimationStyle
└── api/
    └── models.py        # Pydantic-compatible versions
```

## Example Usage

```python
from math_content_engine.constants import (
    LLMProvider,
    VideoQuality,
    AnimationStyle,
    VideoStyle,
)
from math_content_engine.config import Config

# Create config with enums
config = Config(
    llm_provider=LLMProvider.CLAUDE,
    video_quality=VideoQuality.HIGH,
    animation_style=AnimationStyle.DARK,
    video_style=VideoStyle.STEP_BY_STEP,
)

# Use enum values
print(config.video_quality.value)  # "h"
print(config.animation_style.value)  # "dark"
```

## Next Steps

See `REFACTORING_SUMMARY.md` for:
- Complete architectural analysis
- Identified issues and priorities
- Recommended next refactorings
- Test coverage analysis
- Metrics and scorecard
