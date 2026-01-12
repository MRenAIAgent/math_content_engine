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

# Run tests
pytest tests/test_validators.py tests/test_code_extractor.py tests/test_config.py -v  # Unit tests (no deps)
pytest tests/test_render_only.py -v                                                    # Render tests (needs Manim)
pytest tests/test_algebra_integration.py -v                                            # Integration (needs API key)
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
└── tts/                   # Optional text-to-speech (edge-tts)
    ├── narration_generator.py
    └── audio_video_combiner.py
```

Key flow in `MathContentEngine.generate()`:
1. `ManimCodeGenerator.generate()` prompts LLM with topic/requirements
2. `validate_manim_code()` checks syntax and Manim patterns
3. `ManimRenderer.render()` runs `manim` subprocess
4. On render failure, `ManimCodeGenerator.fix_code()` sends error back to LLM
5. Retry up to `config.max_retries` times

## Test Markers

- `@pytest.mark.slow` - Tests that render actual videos
- `@pytest.mark.e2e` - End-to-end tests requiring API keys

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

## Curriculum Resources

`curriculum/algebra1/` contains Common Core-aligned Algebra 1 content:
- `common_core_standards.md` - CCSS standards (A-SSE, A-REI, F-IF, etc.)
- `curriculum_map.md` - 12 units with pacing
- `animation_topics.md` - Topics ranked by animation potential
- `textbooks/` - OpenStax-based chapter content and exercises
