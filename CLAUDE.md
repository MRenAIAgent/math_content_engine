# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Development Commands

```bash
# Install (requires Python 3.10-3.12, NOT 3.13+)
pip install -e .              # Basic install
pip install -e ".[dev]"       # With dev dependencies
pip install -e ".[tts]"       # With TTS support
pip install -e ".[all]"       # Everything

# System dependencies required BEFORE pip install
# macOS: brew install cairo pkg-config pango ffmpeg
# Ubuntu: sudo apt install libcairo2-dev libpango1.0-dev pkg-config ffmpeg

# Run tests (see tests/README.md for comprehensive guide)
pytest -m unit -v                                  # Unit tests (no deps)
pytest tests/test_render_only.py -v               # Render tests (needs Manim)
pytest -m e2e -v                                   # E2E tests (needs API key)
pytest -m "not slow" -v                            # Skip video rendering tests
pytest tests/test_api.py -v                        # API tests
pytest tests/test_algebra_integration.py::TestAlgebraAnimations::test_linear_equation_code_generation -v  # Single test

# Linting & formatting
ruff check src/                # Lint
black src/ tests/              # Format
mypy src/                      # Type check

# CLI usage
math-engine generate "Pythagorean theorem" --quality h --output pythagorean
math-engine preview "Quadratic formula" --save formula.py
math-engine render my_scene.py MySceneName
```

## Architecture

The engine follows a pipeline: **Text Input → LLM Code Generation → Validation → Manim Rendering → Error Feedback Loop**

```
src/math_content_engine/
├── engine.py              # MathContentEngine - main orchestrator, handles retry loop
├── config.py              # Config dataclass, LLMProvider/VideoQuality enums, env var loading
├── cli.py                 # Click-based CLI (math-engine command)
├── llm/
│   ├── base.py            # Abstract LLMClient base class
│   ├── claude.py          # Anthropic Claude implementation
│   ├── openai.py          # OpenAI implementation
│   └── factory.py         # create_llm_client() factory function
├── generator/
│   ├── code_generator.py  # ManimCodeGenerator - LLM prompting, GenerationResult dataclass
│   └── prompts.py         # System prompts and few-shot examples for Manim generation
├── renderer/
│   └── manim_renderer.py  # ManimRenderer - subprocess execution, RenderResult dataclass
├── utils/
│   ├── code_extractor.py  # Extract Python code blocks and class names from LLM responses
│   └── validators.py      # validate_manim_code() - syntax and Manim-specific validation
├── api/                   # Video retrieval API (FastAPI)
│   ├── server.py          # API server
│   ├── routes.py          # API routes
│   ├── models.py          # Data models
│   ├── storage.py         # Video storage
│   └── cli.py             # math-api CLI command
├── tts/                   # Optional text-to-speech
│   ├── narration_generator.py
│   ├── audio_video_combiner.py
│   └── providers/         # TTS provider implementations (Edge TTS, ElevenLabs)
├── lab/                   # Prompt engineering tool (math-lab CLI command)
│   ├── interactive/       # REPL interface
│   ├── prompt/            # Prompt data models
│   ├── session/           # Session management
│   └── suggest/           # AI suggestions
└── personalization/       # Content personalization
    ├── interests.py       # Interest profiles
    ├── personalizer.py    # Content adapter
    └── textbook_parser.py # Textbook parser
```

Key flow in `MathContentEngine.generate()`:
1. `ManimCodeGenerator.generate()` prompts LLM with topic/requirements
2. `validate_manim_code()` checks syntax and Manim patterns
3. `ManimRenderer.render()` runs `manim` subprocess
4. On render failure, `ManimCodeGenerator.fix_code()` sends error back to LLM
5. Retry up to `config.max_retries` times

## Testing

See `tests/README.md` for comprehensive testing guide.

### Test Organization

```
tests/
├── conftest.py                    # Shared fixtures (mock_llm_client, temp_dir, etc.)
├── test_validators.py             # Unit tests
├── test_code_extractor.py         # Unit tests
├── test_config.py                 # Unit tests
├── test_render_only.py            # Render tests (requires Manim)
├── test_integration.py            # Integration tests
├── test_algebra_integration.py    # Algebra E2E tests (requires API key)
├── test_api.py                    # API tests
├── test_elevenlabs_tts.py         # TTS integration tests
├── test_elevenlabs_unit.py        # TTS unit tests
└── test_voice_video_sync.py       # A/V sync tests
```

### Test Markers

- `@pytest.mark.unit` - Fast unit tests, no external dependencies
- `@pytest.mark.integration` - Integration tests with dependencies
- `@pytest.mark.e2e` - End-to-end tests requiring API keys
- `@pytest.mark.slow` - Tests that render actual videos (takes minutes)
- `@pytest.mark.api` - Video retrieval API tests
- `@pytest.mark.tts` - Text-to-speech functionality tests

### Shared Fixtures (conftest.py)

- `mock_llm_client` - Mock LLM client returning valid Manim code
- `temp_dir` - Temporary directory for test outputs
- `temp_db` - Temporary database path for API tests
- `sample_video_metadata` - Sample video creation request
- `api_key_available` - Boolean indicating if API keys are set
- `elevenlabs_key_available` - Boolean for ElevenLabs key

## Environment Variables

Key config via `MATH_ENGINE_*` prefix:
- `MATH_ENGINE_LLM_PROVIDER`: `claude` (default) or `openai`
- `MATH_ENGINE_VIDEO_QUALITY`: `l`/`m`/`h`/`p`/`k` (480p to 4K)
- `MATH_ENGINE_ANIMATION_STYLE`: `dark` (default) or `light`
- `ANTHROPIC_API_KEY` / `OPENAI_API_KEY`: Required for respective provider

## Animation Styles

Two visual styles are available in `prompts.py`:
- **DARK** (`DARK_SYSTEM_PROMPT`): Default Manim dark background
- **LIGHT** (`LIGHT_SYSTEM_PROMPT`): White background with dark text/colors

Style-specific prompts instruct the LLM on color palettes, avoiding LaTeX issues (e.g., use `Text()` instead of `axes.get_axis_labels()`).

## Project Organization

### Examples (examples/)

Examples are organized by category:
- `basic/` - Basic usage, configuration, and topic demos
- `algebra/` - Middle school and high school algebra examples
- `narration/` - TTS narrated animations (requires TTS dependencies)

See `examples/README.md` for full documentation.

### Scripts (scripts/)

Utility scripts for automation:
- `generate_personalized_textbook.py` - Generate personalized textbooks
- `personalized_content_pipeline.py` - End-to-end personalization pipeline
- `curriculum/` - Curriculum-specific scripts

See `scripts/README.md` for usage.

### Documentation (docs/)

- `CONFIGURATION.md` - Configuration guide
- `ELEVENLABS_TTS.md` - TTS setup and usage
- `testing/` - Test-specific documentation
- `archive/` - Archived/historical documentation

### Curriculum Resources (curriculum/)

`curriculum/algebra1/` contains Common Core-aligned Algebra 1 content:
- `common_core_standards.md` - CCSS standards (A-SSE, A-REI, F-IF, etc.)
- `curriculum_map.md` - 12 units with pacing
- `animation_topics.md` - Topics ranked by animation potential
- `textbooks/` - OpenStax-based chapter content and exercises
