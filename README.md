# Math Content Engine

An automated math animation generator that combines **Manim** (the animation engine behind 3Blue1Brown) with **Large Language Models** (Claude/GPT-4) to create educational math videos from text descriptions.

## Features

- **AI-Powered Code Generation**: Describe a math topic in plain English, get a professional animation
- **Multiple LLM Support**: Works with Claude (Anthropic) or GPT-4 (OpenAI)
- **Automatic Error Recovery**: Failed renders are automatically fixed and retried
- **Quality Presets**: From quick previews (480p) to production quality (4K)
- **Comprehensive Examples**: 47+ pre-built algebra examples for middle and high school

## Requirements

- **Python 3.10, 3.11, or 3.12** (Python 3.13+ not yet supported due to dependency issues)
- macOS, Linux, or Windows
- API key for Claude (Anthropic) or GPT-4 (OpenAI)

## Quick Start

### 1. Install System Dependencies (BEFORE pip install)

Manim requires system libraries that must be installed **before** running `pip install`.

**macOS (Homebrew):**
```bash
# Install required system dependencies
brew install cairo pkg-config pango ffmpeg

# Optional: Install LaTeX for advanced math rendering
brew install --cask mactex-no-gui
```

**Ubuntu/Debian:**
```bash
# Install required system dependencies
sudo apt update
sudo apt install -y \
    libcairo2-dev \
    libpango1.0-dev \
    pkg-config \
    python3-dev \
    ffmpeg \
    libgirepository1.0-dev

# Optional: Install LaTeX for advanced math rendering
sudo apt install -y texlive texlive-latex-extra
```

**Windows:**
```powershell
# Install Chocolatey first (https://chocolatey.org/install), then:
choco install miktex ffmpeg

# Or use the Windows installer from https://docs.manim.community/en/stable/installation/windows.html
```

### 2. Install the Package

```bash
# Clone the repository
git clone https://github.com/your-repo/math_content_engine.git
cd math_content_engine

# IMPORTANT: Use Python 3.10-3.12 (not 3.13+)
# Check your Python version
python3 --version

# If you have Python 3.13+, use a specific version:
# macOS: /opt/homebrew/opt/python@3.12/bin/python3.12 -m venv venv
# Ubuntu: python3.12 -m venv venv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip first
pip install --upgrade pip

# Install the package
pip install -e .
```

### 3. Configure API Keys

Copy the example environment file and add your API key:

```bash
cp .env.example .env
```

Edit `.env` with your preferred editor:

```bash
# For Claude (recommended)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# OR for OpenAI
MATH_ENGINE_LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

### 4. Generate Your First Animation

```python
from math_content_engine import MathContentEngine

engine = MathContentEngine()
result = engine.generate("Pythagorean theorem with visual proof")

if result.success:
    print(f"Video saved to: {result.video_path}")
```

## Usage

### Python API

#### Basic Generation

```python
from math_content_engine import MathContentEngine

engine = MathContentEngine()

# Generate animation from topic description
result = engine.generate(
    topic="Quadratic formula derivation",
    requirements="Show step-by-step completing the square method",
    audience_level="high school",  # elementary, middle school, high school, college
    output_filename="quadratic_formula"
)

if result.success:
    print(f"Video: {result.video_path}")
    print(f"Render time: {result.render_time:.2f}s")
else:
    print(f"Error: {result.error_message}")
```

#### Preview Code Without Rendering

```python
# Generate code only (faster, no video output)
result = engine.preview_code(
    topic="Unit circle and trigonometry",
    audience_level="high school"
)

print(result.code)  # View the generated Manim code
print(f"Valid: {result.validation.is_valid}")
```

#### Render Existing Code

```python
# Render your own Manim code
manim_code = '''
from manim import *

class MyScene(Scene):
    def construct(self):
        eq = MathTex(r"e^{i\pi} + 1 = 0")
        self.play(Write(eq))
        self.wait()
'''

result = engine.generate_from_code(manim_code, output_filename="euler")
```

#### Custom Configuration

```python
from math_content_engine import MathContentEngine, Config
from math_content_engine.config import VideoQuality, LLMProvider

config = Config()
config.llm_provider = LLMProvider.OPENAI  # Use GPT-4 instead of Claude
config.video_quality = VideoQuality.HIGH   # 1080p output
config.max_retries = 3                     # Fewer retry attempts
config.output_format = "gif"               # GIF instead of MP4

engine = MathContentEngine(config)
```

### Command Line Interface

```bash
# Generate animation from topic
math-engine generate "Pythagorean theorem proof"

# With options
math-engine generate "Quadratic formula" \
    --output quadratic \
    --quality h \
    --audience "high school"

# Preview code without rendering
math-engine preview "Slope of a line" --save slope.py

# Render existing Manim file
math-engine render my_scene.py MySceneName --quality h

# Get help
math-engine --help
math-engine generate --help
```

### Using Pre-built Examples

```python
# Middle School Algebra (18 examples)
from examples.algebra_middle_school import (
    variables_introduction,
    two_step_equations,
    solving_proportions,
    run_all_examples
)

# Generate specific animation
result = two_step_equations()

# Generate all middle school examples
results = run_all_examples()

# High School Algebra (29 examples)
from examples.algebra_high_school import (
    quadratic_formula,
    systems_elimination,
    logarithm_properties,
    run_all_examples
)

result = quadratic_formula()
```

## Configuration

All settings can be configured via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `MATH_ENGINE_LLM_PROVIDER` | `claude` | LLM provider (`claude` or `openai`) |
| `ANTHROPIC_API_KEY` | - | Anthropic API key (required for Claude) |
| `OPENAI_API_KEY` | - | OpenAI API key (required for OpenAI) |
| `MATH_ENGINE_CLAUDE_MODEL` | `claude-sonnet-4-20250514` | Claude model to use |
| `MATH_ENGINE_OPENAI_MODEL` | `gpt-4o` | OpenAI model to use |
| `MATH_ENGINE_MAX_RETRIES` | `5` | Max retry attempts for failed renders |
| `MATH_ENGINE_TEMPERATURE` | `0.7` | LLM temperature (0.0-1.0) |
| `MATH_ENGINE_VIDEO_QUALITY` | `m` | Quality: `l`(480p), `m`(720p), `h`(1080p), `p`(1440p), `k`(4K) |
| `MATH_ENGINE_OUTPUT_FORMAT` | `mp4` | Output format (`mp4` or `gif`) |
| `MATH_ENGINE_OUTPUT_DIR` | `./output` | Output directory for videos |

## Running Tests

### Quick Start

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all unit tests (fast, no API key needed)
pytest tests/test_validators.py tests/test_code_extractor.py tests/test_config.py -v

# Run render tests (tests Manim rendering, no API key needed)
pytest tests/test_render_only.py -v

# Run all tests
pytest
```

### Test Categories

**1. Unit Tests (No dependencies required)**
```bash
# Code validation tests
pytest tests/test_validators.py -v

# Code extraction tests
pytest tests/test_code_extractor.py -v

# Configuration tests
pytest tests/test_config.py -v
```

**2. Render Tests (Requires Manim installed)**
```bash
# Test Manim rendering with pre-written code (no API key needed)
pytest tests/test_render_only.py -v

# These tests create actual video files to verify the rendering pipeline works
```

**3. Integration Tests (Requires API key)**
```bash
# Set your API key first
export ANTHROPIC_API_KEY=your-key-here

# Run algebra animation tests
pytest tests/test_algebra_integration.py -v

# Run only code generation tests (faster, no rendering)
pytest tests/test_algebra_integration.py -v -k "code_generation"

# Run full render tests (slower, creates actual videos)
pytest tests/test_algebra_integration.py -v -m slow
```

### Test Options

```bash
# Run with coverage report
pytest --cov=math_content_engine --cov-report=html

# Skip slow tests (rendering)
pytest -m "not slow"

# Run end-to-end tests only
pytest -m e2e

# Verbose output with print statements
pytest -v -s

# Run a specific test
pytest tests/test_algebra_integration.py::TestAlgebraAnimations::test_linear_equation_code_generation -v
```

### Test Structure

```
tests/
├── test_validators.py          # Code validation unit tests
├── test_code_extractor.py      # LLM response parsing tests
├── test_config.py              # Configuration tests
├── test_render_only.py         # Manim rendering tests (no API key)
├── test_algebra_integration.py # Algebra animation integration tests
└── test_integration.py         # General integration & E2E tests
```

## Project Structure

```
math_content_engine/
├── src/math_content_engine/
│   ├── __init__.py          # Package exports
│   ├── config.py            # Configuration management
│   ├── engine.py            # Main orchestrator
│   ├── cli.py               # Command-line interface
│   ├── llm/
│   │   ├── base.py          # Abstract LLM client
│   │   ├── claude.py        # Anthropic Claude client
│   │   ├── openai.py        # OpenAI client
│   │   └── factory.py       # Client factory
│   ├── generator/
│   │   ├── code_generator.py # LLM code generation
│   │   └── prompts.py       # Prompt templates
│   ├── renderer/
│   │   └── manim_renderer.py # Manim rendering
│   └── utils/
│       ├── code_extractor.py # Extract code from responses
│       └── validators.py     # Code validation
├── examples/
│   ├── basic_usage.py       # Basic usage examples
│   ├── advanced_usage.py    # Advanced features
│   ├── topic_examples.py    # Various math topics
│   ├── algebra_middle_school.py  # 18 middle school examples
│   └── algebra_high_school.py    # 29 high school examples
├── tests/                   # Test suite
├── .env.example             # Environment template
├── pyproject.toml           # Package configuration
└── requirements.txt         # Dependencies
```

## Examples Catalog

### Middle School Algebra (Grades 6-8)

| Topic | Function |
|-------|----------|
| Variables Introduction | `variables_introduction()` |
| Evaluating Expressions | `evaluating_expressions()` |
| Writing Expressions | `writing_expressions()` |
| One-Step Equations (+/-) | `one_step_addition()` |
| One-Step Equations (×/÷) | `one_step_multiplication()` |
| Two-Step Equations | `two_step_equations()` |
| Equations with Negatives | `equations_with_negatives()` |
| Inequalities Introduction | `inequality_introduction()` |
| Solving Inequalities | `solving_inequalities()` |
| Order of Operations | `order_of_operations()` |
| Ratios Introduction | `ratios_introduction()` |
| Solving Proportions | `solving_proportions()` |
| Coordinate Plane | `coordinate_plane_intro()` |
| Graphing Linear Equations | `graphing_linear_equations()` |
| Adding Integers | `adding_integers()` |
| Multiplying Integers | `multiplying_integers()` |
| Distributive Property | `distributive_property()` |
| Combining Like Terms | `combining_like_terms()` |

### High School Algebra (Grades 9-12)

| Topic | Function |
|-------|----------|
| Slope-Intercept Form | `slope_intercept_form()` |
| Point-Slope Form | `point_slope_form()` |
| Systems (Substitution) | `systems_substitution()` |
| Systems (Elimination) | `systems_elimination()` |
| Systems (Graphing) | `systems_graphing()` |
| Quadratic Standard Form | `quadratic_standard_form()` |
| Factoring Quadratics | `factoring_quadratics()` |
| Quadratic Formula | `quadratic_formula()` |
| Discriminant | `discriminant()` |
| Completing the Square | `completing_the_square()` |
| Polynomial Operations | `polynomial_operations()` |
| Polynomial Division | `polynomial_division()` |
| Special Factoring | `factoring_special_forms()` |
| Simplifying Rationals | `simplifying_rationals()` |
| Multiplying Rationals | `multiplying_rationals()` |
| Adding Rationals | `adding_rationals()` |
| Exponent Rules | `exponent_rules()` |
| Simplifying Radicals | `simplifying_radicals()` |
| Rational Exponents | `rational_exponents()` |
| Function Notation | `function_notation()` |
| Transformations | `function_transformations()` |
| Inverse Functions | `inverse_functions()` |
| Exponential Functions | `exponential_functions()` |
| Logarithm Introduction | `logarithm_introduction()` |
| Logarithm Properties | `logarithm_properties()` |
| Solving Exp/Log Equations | `solving_exponential_equations()` |
| Arithmetic Sequences | `arithmetic_sequences()` |
| Geometric Sequences | `geometric_sequences()` |
| Complex Numbers | `complex_numbers()` |

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    Math Content Engine                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Text Input  │───▶│  LLM Agent   │───▶│ Manim Code   │  │
│  │  (Topic)     │    │  (Claude/    │    │ Generator    │  │
│  │              │    │   GPT-4)     │    │              │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                             │                    │          │
│                             ▼                    ▼          │
│                    ┌──────────────┐    ┌──────────────┐    │
│                    │  Validator   │◀───│   Manim CE   │    │
│                    │  (Auto-fix)  │    │   Renderer   │    │
│                    └──────────────┘    └──────────────┘    │
│                             │                    │          │
│                             │         ┌──────────┘          │
│                             ▼         ▼                     │
│                         ┌──────────────┐                    │
│                         │   MP4/GIF    │                    │
│                         │   Output     │                    │
│                         └──────────────┘                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

1. **Input**: Describe your math topic in plain English
2. **Generation**: LLM generates Manim Python code with educational animations
3. **Validation**: Code is validated for syntax and Manim-specific requirements
4. **Rendering**: Manim renders the animation to video
5. **Error Recovery**: If rendering fails, the error is fed back to the LLM for automatic fixing
6. **Output**: Final MP4 or GIF video file

## Troubleshooting

### Common Issues

**Build fails with Python 3.13 or 3.14**

Manim and some dependencies don't yet support Python 3.13+. Use Python 3.12:

```bash
# macOS - install Python 3.12 if needed
brew install python@3.12

# Create venv with Python 3.12
/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -e .
```

**pycairo build fails with "Dependency lookup for cairo failed" (macOS)**

You must install system dependencies BEFORE pip install:

```bash
# Install cairo and pkg-config first
brew install cairo pkg-config pango

# Then reinstall in a fresh venv
deactivate
rm -rf venv
python3.12 -m venv venv  # Use Python 3.12
source venv/bin/activate
pip install --upgrade pip
pip install -e .
```

**pycairo build fails (Ubuntu/Debian)**
```bash
sudo apt install libcairo2-dev pkg-config python3-dev
pip install --upgrade pip
pip install -e .
```

**"Manim is not installed"**
```bash
pip install manim
# Make sure system dependencies are installed first (see Step 1)
```

**"ANTHROPIC_API_KEY environment variable is required"**
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
# Or add to .env file
```

**"LaTeX errors during rendering"**

Manim uses LaTeX for mathematical text. If you see LaTeX-related errors:

```bash
# macOS
brew install --cask mactex-no-gui
# Then restart your terminal

# Ubuntu
sudo apt install texlive texlive-latex-extra

# Alternative: Use Manim without LaTeX (limited math rendering)
# Add to your code: config.tex_template = None
```

**Rendering takes too long**
```bash
# Use lower quality for testing
math-engine generate "topic" --quality l
```

**FFmpeg not found**
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg

# Windows
choco install ffmpeg
```

**Verify Installation**

Run this to check if everything is installed correctly:
```bash
python -c "from manim import *; print('Manim OK')"
python -c "from math_content_engine import MathContentEngine; print('Math Engine OK')"
```

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- [Manim Community](https://www.manim.community/) - The animation engine
- [3Blue1Brown](https://www.3blue1brown.com/) - Original Manim creator
- [Anthropic](https://www.anthropic.com/) - Claude AI
- [OpenAI](https://openai.com/) - GPT-4
