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
pytest tests/test_playground_prompt_builder.py -v                                      # Playground prompt builder tests
pytest tests/test_render_only.py -v                                                    # Render tests (needs Manim)
pytest tests/test_algebra_integration.py -v                                            # Integration (needs API key)
pytest tests/test_algebra_integration.py::TestAlgebraAnimations::test_linear_equation_code_generation -v  # Single test

# Run the Playground (prompt tuning UI)
pip install -e ".[api]"                              # Install API dependencies
source .env                                          # Load API keys (ANTHROPIC_API_KEY required)
python -m math_content_engine.api.server             # Start server on http://localhost:8000
# Open http://localhost:8000/playground/ in browser

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
├── api/
│   ├── server.py          # FastAPI app factory, mounts all routes + static files
│   ├── routes.py          # Video API endpoints
│   └── playground/        # Prompt tuning playground
│       ├── __init__.py    # Exports playground_router
│       ├── models.py      # Pydantic request/response models
│       ├── prompt_builder.py  # Prompt introspection (preview without LLM calls)
│       ├── pipeline_runner.py # Wraps pipeline steps with prompt override support
│       ├── routes.py      # All /api/v1/playground/* endpoints
│       └── tasks.py       # Async task manager with SSE streaming
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
├── static/playground/     # Frontend (vanilla JS, no build step)
│   ├── index.html         # Single-page app layout
│   ├── app.js             # Frontend logic, state management, SSE handling
│   └── styles.css         # Dark theme styling
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

## Playground (Prompt Tuning UI)

A web-based developer tool for iterating on prompts. Start the server and open `http://localhost:8000/playground/`.

```bash
source .env && python -m math_content_engine.api.server
```

**Pipeline stages** (each with editable system + user prompts):
1. **Upload Content** — Paste textbook markdown, select student interest
2. **Extract Concepts** — Identify math concepts in content (returns JSON)
3. **Personalize** — Transform textbook into interest-themed version
4. **Generate Animation** — Produce Manim Python code for a topic
5. **Render Video** — Compile Manim code into MP4

**Tuning workflow**: Preview Prompts → Edit in textarea → Execute → Compare in Run History

**LLM Settings bar** exposes temperature, max tokens, model, and provider. Prompt overrides bypass default prompt construction and call the LLM directly.

**Key API endpoints** (`/api/v1/playground/`):
- `GET /config` — LLM provider, model, available interests
- `POST /prompts/preview` — Preview prompts without calling the LLM
- `POST /execute` — Run a stage (returns task ID, streams progress via SSE)
- `GET /tasks/{id}/stream` — SSE event stream for task progress

## Curriculum Resources

`curriculum/algebra1/` contains Common Core-aligned Algebra 1 content:
- `common_core_standards.md` - CCSS standards (A-SSE, A-REI, F-IF, etc.)
- `curriculum_map.md` - 12 units with pacing
- `animation_topics.md` - Topics ranked by animation potential
- `textbooks/` - OpenStax-based chapter content and exercises
