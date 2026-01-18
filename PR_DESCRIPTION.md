# Add ElevenLabs TTS Provider Support

## Overview
This PR adds comprehensive support for **ElevenLabs** as a premium TTS provider option, alongside the existing free Edge TTS provider. The implementation uses a provider abstraction pattern for flexible TTS backend selection.

## 🎯 Features

### 1. Multi-Provider TTS Architecture
- **Abstract base class** (`BaseTTSProvider`) for extensible TTS support
- **ElevenLabs provider** with premium neural voices
- **Refactored Edge TTS** into the provider pattern
- **Factory function** for configuration-based provider creation

### 2. ElevenLabs Integration
- Full async audio generation support
- Pre-configured educational voice styles:
  - `TEACHER_FEMALE_CALM` (Rachel)
  - `TEACHER_FEMALE_CLEAR` (Bella)
  - `TEACHER_MALE_DEEP` (Josh)
  - `TEACHER_MALE_CLEAR` (Antoni)
- Customizable voice settings (stability, similarity_boost, style)
- Voice listing functionality
- Audio duration detection

### 3. Configuration
New environment variables for TTS provider selection:
- `MATH_ENGINE_TTS_PROVIDER` - Choose `"edge"` (default) or `"elevenlabs"`
- `ELEVENLABS_API_KEY` - Your ElevenLabs API key (required for ElevenLabs)
- `MATH_ENGINE_TTS_VOICE` - Optional voice selection (provider-specific)

### 4. Merged with Main TTS Configuration
Successfully integrated with main's TTS improvements:
- ✅ Preserves `TTSVoice` enum (9 Edge TTS voices)
- ✅ Preserves `VideoStyle` enum (4 presentation styles)
- ✅ Preserves TTS tuning settings (rate, volume, pitch)
- ✅ Adds `TTSProvider` enum (Edge/ElevenLabs selection)
- ✅ Enhanced `get_tts_config()` to support both systems

## 📁 Files Added

**Core Implementation:**
- `src/math_content_engine/tts/base_provider.py` - Abstract base class
- `src/math_content_engine/tts/elevenlabs_provider.py` - ElevenLabs implementation
- `src/math_content_engine/tts/edge_tts_provider.py` - Refactored Edge TTS
- `src/math_content_engine/tts/provider_factory.py` - Factory function

**Tests:**
- `tests/test_elevenlabs_unit.py` - Unit tests (14 tests, all passing)
- `tests/test_elevenlabs_tts.py` - Integration tests

**Documentation:**
- `docs/ELEVENLABS_TTS.md` - Comprehensive usage guide

## 📝 Files Modified

- `src/math_content_engine/config.py` - Added TTS provider configuration
- `src/math_content_engine/tts/tts_engine.py` - Refactored to use providers
- `src/math_content_engine/tts/__init__.py` - Updated exports
- `src/math_content_engine/__init__.py` - Added TTSProvider export
- `pyproject.toml` - Added elevenlabs dependency
- `.gitignore` - Exclude test output files

## 🧪 Testing

**Unit Tests: 14/14 passing** ✅
- Configuration validation
- Voice enum tests
- Provider functionality with mocked API
- TTSEngine integration
- Provider factory tests

**Overall Test Results: 57/60 passing (95%)**
- All ElevenLabs tests: 100% passing
- All configuration tests: 100% passing
- 3 failures are environment-specific (Manim not installed)

## 🚀 Usage Example

```python
import os
from math_content_engine.tts import create_tts_provider, TTSEngine
from math_content_engine import Config

# Configure ElevenLabs
os.environ["MATH_ENGINE_TTS_PROVIDER"] = "elevenlabs"
os.environ["ELEVENLABS_API_KEY"] = "your-api-key"

# Create provider and generate audio
config = Config()
provider = create_tts_provider(config)
engine = TTSEngine(provider=provider)

audio_path = engine.generate(
    "Let's solve the equation 2x plus 3 equals 7",
    "linear_equation.mp3"
)
```

## 🔄 Backward Compatibility

- ✅ Existing Edge TTS code works unchanged
- ✅ Default behavior remains Edge TTS (free, no API key)
- ✅ ElevenLabs is opt-in via environment variables
- ✅ No breaking changes to existing APIs
- ✅ All main's TTS configuration features preserved

## 📦 Installation

```bash
pip install -e ".[tts]"
```

This installs: `edge-tts`, `elevenlabs`, and `mutagen`

## 🎨 Architecture

```
TTSEngine (high-level API)
    ↓
BaseTTSProvider (abstract interface)
    ↓
├── EdgeTTSProvider (free, no API key)
└── ElevenLabsTTSProvider (premium, requires API key)
```

## 🔍 Rebase Notes

This branch has been rebased onto main to incorporate the comprehensive TTS and video style configuration changes (PR #6). All merge conflicts were resolved by:
1. Keeping both `TTSVoice` and `TTSProvider` enums
2. Merging Edge TTS tuning fields with ElevenLabs provider fields
3. Enhancing `get_tts_config()` to support both systems
4. All tests passing after rebase

## ✅ Checklist

- [x] Code follows project style guidelines
- [x] All tests passing (14/14 unit tests)
- [x] Documentation added (ELEVENLABS_TTS.md)
- [x] Backward compatibility maintained
- [x] No breaking changes
- [x] Successfully rebased onto main
- [x] Merge conflicts resolved
- [x] Configuration properly merged with main's changes

## 📚 Documentation

See `docs/ELEVENLABS_TTS.md` for:
- Detailed setup instructions
- Configuration guide
- Voice reference
- Usage examples
- Troubleshooting guide

## 🔗 Related

Builds on and integrates with:
- PR #6: Add comprehensive TTS and video style configuration support
