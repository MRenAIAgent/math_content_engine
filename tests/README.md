# Testing Guide

This directory contains the test suite for the Math Content Engine. Tests are organized by type and scope, with proper markers for selective execution.

## Test Organization

```
tests/
├── conftest.py                    # Shared fixtures and pytest configuration
├── test_validators.py             # Unit tests for code validation
├── test_code_extractor.py         # Unit tests for code extraction
├── test_config.py                 # Unit tests for configuration
├── test_render_only.py            # Manim rendering tests (requires Manim)
├── test_integration.py            # End-to-end integration tests
├── test_algebra_integration.py    # Algebra-specific integration tests
├── test_api.py                    # Video retrieval API tests
├── test_elevenlabs_tts.py         # ElevenLabs TTS integration tests
├── test_elevenlabs_unit.py        # ElevenLabs TTS unit tests
└── test_voice_video_sync.py       # Audio-video synchronization tests
```

## Test Categories

### Unit Tests (Fast, No Dependencies)
These tests run quickly and don't require external services or heavy dependencies.

**Files:**
- `test_validators.py` - Code validation logic
- `test_code_extractor.py` - Python code extraction from LLM responses
- `test_config.py` - Configuration loading and validation
- `test_elevenlabs_unit.py` - TTS provider unit tests (mocked)

**Run:**
```bash
pytest tests/test_validators.py tests/test_code_extractor.py tests/test_config.py -v
```

### Integration Tests (Require Dependencies)
These tests verify components work together but may be mocked or use local resources.

**Files:**
- `test_integration.py` - Full pipeline integration
- `test_api.py` - FastAPI endpoints and storage
- `test_render_only.py` - Manim rendering (requires Manim installed)

**Run:**
```bash
# API tests (no external dependencies)
pytest tests/test_api.py -v

# Render tests (requires Manim)
pytest tests/test_render_only.py -v
```

### End-to-End Tests (Require API Keys)
These tests exercise the complete system with real API calls.

**Files:**
- `test_algebra_integration.py` - Algebra topic generation and rendering
- `test_elevenlabs_tts.py` - ElevenLabs voice synthesis
- `test_voice_video_sync.py` - Audio-video synchronization

**Requirements:**
- API keys: `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
- For TTS: `ELEVENLABS_API_KEY` (optional, falls back to Edge TTS)

**Run:**
```bash
# Set API key
export ANTHROPIC_API_KEY="your-key-here"

# Run E2E tests
pytest tests/test_integration.py -v
pytest tests/test_algebra_integration.py -v

# Run TTS tests (with ElevenLabs)
export ELEVENLABS_API_KEY="your-key-here"
pytest tests/test_elevenlabs_tts.py -v
pytest tests/test_voice_video_sync.py -v
```

## Test Markers

Tests are marked for selective execution:

- `@pytest.mark.unit` - Fast unit tests, no external dependencies
- `@pytest.mark.integration` - Integration tests with dependencies
- `@pytest.mark.e2e` - End-to-end tests requiring API keys
- `@pytest.mark.slow` - Tests that render videos (takes minutes)
- `@pytest.mark.api` - Video retrieval API tests
- `@pytest.mark.tts` - Text-to-speech functionality tests

**Examples:**
```bash
# Run only unit tests
pytest -m unit -v

# Run only fast tests (exclude slow)
pytest -m "not slow" -v

# Run API tests
pytest -m api -v

# Run TTS tests
pytest -m tts -v

# Run E2E tests only
pytest -m e2e -v
```

## Running Tests

### Quick Test (No Dependencies)
```bash
# Unit tests only - fastest, no API keys or Manim needed
pytest tests/test_validators.py tests/test_code_extractor.py tests/test_config.py -v
```

### Standard Test Suite
```bash
# All tests except those requiring API keys
pytest -m "not e2e" -v
```

### Full Test Suite
```bash
# Everything (requires API keys and all dependencies)
export ANTHROPIC_API_KEY="your-key"
export ELEVENLABS_API_KEY="your-key"  # Optional
pytest -v
```

### Specific Test Files
```bash
# Single file
pytest tests/test_config.py -v

# Multiple files
pytest tests/test_validators.py tests/test_config.py -v
```

### Specific Test Functions
```bash
# Single test
pytest tests/test_algebra_integration.py::TestAlgebraAnimations::test_linear_equation_code_generation -v

# Pattern matching
pytest -k "linear_equation" -v
```

### With Coverage
```bash
# Generate coverage report
pytest --cov=math_content_engine --cov-report=html tests/

# View report
open htmlcov/index.html
```

## Common Test Scenarios

### 1. Pre-Commit Checks (CI/Local)
```bash
# Fast tests that should always pass
pytest -m "not slow and not e2e" -v
```

### 2. Development Testing
```bash
# Test specific feature you're working on
pytest tests/test_integration.py::TestManimCodeGenerator -v
```

### 3. Full Validation Before Release
```bash
# All tests including slow rendering
export ANTHROPIC_API_KEY="your-key"
pytest -v --slow
```

### 4. TTS Development
```bash
# TTS-related tests only
pytest -m tts -v
```

## Shared Fixtures

Common fixtures are defined in `conftest.py`:

- **`mock_llm_client`** - Mock LLM client returning valid Manim code
- **`temp_dir`** - Temporary directory for test outputs
- **`temp_db`** - Temporary database path for API tests
- **`sample_video_metadata`** - Sample video creation request
- **`api_key_available`** - Boolean indicating if API keys are set
- **`elevenlabs_key_available`** - Boolean for ElevenLabs key

**Usage in tests:**
```python
def test_example(mock_llm_client, temp_dir):
    # Use fixtures directly as function parameters
    generator = ManimCodeGenerator(mock_llm_client)
    output_path = temp_dir / "output.mp4"
    # ... test code
```

## Test Data

### Sample Manim Code
Valid Manim code samples are defined in `conftest.py` as `VALID_MANIM_CODE`.

### Topics for Testing
Common test topics:
- "Pythagorean theorem"
- "Quadratic formula"
- "Linear equation solving"
- "Systems of equations"

## Troubleshooting

### Import Errors
```bash
# Install package in development mode
pip install -e ".[dev]"

# For TTS tests
pip install -e ".[tts]"

# Everything
pip install -e ".[all]"
```

### API Key Issues
```bash
# Check if key is set
echo $ANTHROPIC_API_KEY

# Set temporarily
export ANTHROPIC_API_KEY="your-key"

# Or use .env file (loaded automatically)
echo 'ANTHROPIC_API_KEY=your-key' >> .env
```

### Manim Not Found
```bash
# Install system dependencies first
# macOS:
brew install cairo pkg-config pango ffmpeg

# Ubuntu:
sudo apt install libcairo2-dev libpango1.0-dev pkg-config ffmpeg

# Then install package with Manim
pip install -e ".[all]"
```

### Tests Timing Out
```bash
# Increase timeout for slow tests
pytest --timeout=300 tests/test_algebra_integration.py -v

# Or skip slow tests
pytest -m "not slow" -v
```

### Database Lock Errors (API tests)
```bash
# Clean up test databases
rm tests/test_*.db 2>/dev/null

# Run tests sequentially instead of parallel
pytest tests/test_api.py -v --maxfail=1
```

## Performance Tips

1. **Use markers** to run only relevant tests during development
2. **Mock external services** when possible (see `mock_llm_client`)
3. **Skip slow tests** during rapid iteration with `-m "not slow"`
4. **Run unit tests first** - they're fast and catch most issues
5. **Use `-x`** to stop on first failure: `pytest -x -v`
6. **Use `-v`** for detailed output, `-vv` for even more detail
7. **Parallelize** with pytest-xdist: `pytest -n auto` (when tests are independent)

## Continuous Integration

Our CI pipeline runs:

1. **Fast checks** (lint, type check): `ruff check`, `mypy`
2. **Unit tests**: `pytest -m unit`
3. **Integration tests**: `pytest -m "integration and not slow"`
4. **API tests**: `pytest -m api`
5. **E2E tests** (if API keys available): `pytest -m e2e`

## Writing New Tests

### Guidelines

1. **Use appropriate markers**: `@pytest.mark.unit`, `@pytest.mark.e2e`, etc.
2. **Use shared fixtures** from `conftest.py` when possible
3. **Mock external dependencies** in unit tests
4. **Add docstrings** explaining what the test verifies
5. **Follow naming convention**: `test_<feature>_<scenario>`
6. **Keep tests isolated** - don't depend on test execution order
7. **Clean up resources** - use fixtures with yield for setup/teardown

### Example Test
```python
import pytest
from math_content_engine import MathContentEngine

@pytest.mark.unit
def test_config_loading(temp_dir):
    """Test that configuration loads correctly from environment."""
    # Setup
    config = Config(output_dir=temp_dir)

    # Test
    assert config.output_dir == temp_dir
    assert config.max_retries == 3  # default

    # No cleanup needed - temp_dir auto-cleaned by fixture

@pytest.mark.e2e
@pytest.mark.slow
def test_full_generation(api_key_available):
    """Test complete generation pipeline with real API."""
    if not api_key_available:
        pytest.skip("API key required")

    engine = MathContentEngine()
    result = engine.generate("Pythagorean theorem")

    assert result.success
    assert result.video_path.exists()
```

## Documentation

- **ElevenLabs TTS Testing**: See [`docs/testing/README_ELEVENLABS_TESTS.md`](../docs/testing/README_ELEVENLABS_TESTS.md)
- **Voice-Video Sync**: See [`docs/testing/VOICE_VIDEO_SYNC_GUIDE.md`](../docs/testing/VOICE_VIDEO_SYNC_GUIDE.md)
- **Configuration**: See [`docs/CONFIGURATION.md`](../docs/CONFIGURATION.md)

## Questions?

- Check main [`README.md`](../README.md) for project overview
- See [`CLAUDE.md`](../CLAUDE.md) for development commands
- Review existing tests for patterns and examples
- Run `pytest --markers` to see all available markers
- Run `pytest --fixtures` to see all available fixtures
