# Examples

This directory contains example scripts demonstrating various features of the Math Content Engine.

## Directory Structure

```
examples/
├── basic/          # Basic usage and configuration examples
├── algebra/        # Algebra-specific examples
├── narration/      # Text-to-speech narrated animations
└── videos/         # Output directory for generated videos
```

## Basic Examples (`basic/`)

### `basic_usage.py`
The simplest example showing core functionality.

**Demonstrates:**
- Creating a MathContentEngine instance
- Generating a simple animation from a text description
- Basic configuration

**Run:**
```bash
python examples/basic/basic_usage.py
```

### `advanced_usage.py`
Advanced features and customization options.

**Demonstrates:**
- Custom configuration
- Quality settings
- Animation style selection
- Error handling

**Run:**
```bash
python examples/basic/advanced_usage.py
```

### `config_demo.py`
Comprehensive configuration demonstration.

**Demonstrates:**
- All configuration options
- Environment variable usage
- LLM provider selection
- Video quality settings

**Run:**
```bash
python examples/basic/config_demo.py
```

### `generate_all_styles.py`
Generates the same topic in different animation styles.

**Demonstrates:**
- Dark vs. light animation styles
- Style comparison
- Batch generation

**Run:**
```bash
python examples/basic/generate_all_styles.py
```

### `topic_examples.py`
Collection of various math topics.

**Demonstrates:**
- Different types of mathematical concepts
- Topic variety (geometry, algebra, calculus)
- Batch processing

**Run:**
```bash
python examples/basic/topic_examples.py
```

## Algebra Examples (`algebra/`)

### `algebra_high_school.py`
High school algebra topics and animations.

**Topics covered:**
- Linear equations and systems
- Quadratic functions
- Polynomial operations
- Exponential and logarithmic functions
- Rational expressions

**Run:**
```bash
python examples/algebra/algebra_high_school.py
```

### `algebra_middle_school.py`
Middle school algebra foundations.

**Topics covered:**
- Variables and expressions
- Simple equations
- Integer operations
- Basic graphing
- Order of operations

**Run:**
```bash
python examples/algebra/algebra_middle_school.py
```

### `graphical_algebra.py`
Visual, graph-focused algebra examples.

**Demonstrates:**
- Coordinate plane visualizations
- Function graphing
- Systems of equations (graphical solutions)
- Transformations

**Run:**
```bash
python examples/algebra/graphical_algebra.py
```

## Narration Examples (`narration/`)

These examples require TTS dependencies. Install with:
```bash
pip install -e ".[tts]"
```

### `llm_narrated_animation.py`
LLM-generated narration synchronized with animation.

**Demonstrates:**
- Automatic narration script generation
- Voice synthesis
- Audio-video synchronization
- Edge TTS integration

**Run:**
```bash
python examples/narration/llm_narrated_animation.py
```

### `narrated_graphical_equation.py`
Narrated graphical equation solving.

**Demonstrates:**
- Step-by-step narrated solutions
- Graph visualization with voice
- Synchronized explanation

**Run:**
```bash
python examples/narration/narrated_graphical_equation.py
```

### `narrated_linear_equation.py`
Linear equation solving with narration.

**Demonstrates:**
- Algebraic manipulation narration
- Voice-guided problem solving
- ElevenLabs TTS integration (if API key provided)

**Run:**
```bash
export ELEVENLABS_API_KEY="your-key"  # Optional, falls back to Edge TTS
python examples/narration/narrated_linear_equation.py
```

## Requirements

### All Examples
- Python 3.10-3.12
- Basic install: `pip install -e .`
- API key: `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`

### Narration Examples
- TTS install: `pip install -e ".[tts]"`
- Optional: `ELEVENLABS_API_KEY` for premium voices

### System Dependencies
See main README.md for Cairo, Pango, FFmpeg installation.

## Output

Generated videos are saved to:
- Default: `./media/videos/` (Manim default)
- Custom: Specify with `--output` in CLI or `output_dir` in code

## Tips

1. **Start with basic examples** to understand core concepts
2. **Check configuration** in `config_demo.py` before running others
3. **Narration examples** may take longer due to TTS processing
4. **Large algebra examples** may consume significant API tokens
5. **Use preview mode** (`math-engine preview`) to see generated code without rendering

## Troubleshooting

**Import errors:**
```bash
pip install -e ".[all]"  # Install all dependencies
```

**API errors:**
```bash
# Set your API key
export ANTHROPIC_API_KEY="your-key"
```

**Rendering fails:**
- Check system dependencies (Cairo, Pango, FFmpeg)
- See docs/CONFIGURATION.md for platform-specific setup

**TTS errors:**
- Ensure TTS dependencies: `pip install -e ".[tts]"`
- Check ELEVENLABS_API_KEY if using ElevenLabs
- Edge TTS works without API key as fallback

## More Information

- Main documentation: [`README.md`](../README.md)
- Configuration guide: [`docs/CONFIGURATION.md`](../docs/CONFIGURATION.md)
- TTS setup: [`docs/ELEVENLABS_TTS.md`](../docs/ELEVENLABS_TTS.md)
- CLI reference: See `math-engine --help`
