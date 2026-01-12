"""
Render-only integration tests.

These tests verify Manim rendering works without requiring an API key.
They use pre-written Manim code to test the rendering pipeline.

Run these tests with:
    pytest tests/test_render_only.py -v

Note: Some tests require LaTeX to be installed. Tests that use MathTex
will be skipped if LaTeX is not available.
"""

import subprocess
import pytest
from pathlib import Path

from math_content_engine import MathContentEngine, Config
from math_content_engine.config import VideoQuality


def latex_available():
    """Check if LaTeX is available on the system."""
    try:
        result = subprocess.run(
            ["latex", "--version"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


# Pre-written Manim code for testing (no LaTeX needed)
SIMPLE_TEXT_ANIMATION = '''
from manim import *

class SimpleTextAnimation(Scene):
    def construct(self):
        # Title using Text (no LaTeX needed)
        title = Text("Simple Animation Test").scale(0.8)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))

        # Create shapes
        circle = Circle(color=BLUE, fill_opacity=0.5)
        square = Square(color=RED, fill_opacity=0.5)
        square.next_to(circle, RIGHT)

        self.play(Create(circle), Create(square))
        self.wait(0.5)

        # Transform
        self.play(circle.animate.shift(UP), square.animate.shift(DOWN))
        self.wait(0.5)
'''

SHAPES_ANIMATION = '''
from manim import *

class ShapesAnimation(Scene):
    def construct(self):
        # Create various shapes
        shapes = VGroup(
            Circle(color=RED),
            Square(color=GREEN),
            Triangle(color=BLUE),
        ).arrange(RIGHT, buff=1)

        self.play(Create(shapes))
        self.wait(0.5)

        # Animate them
        self.play(shapes.animate.scale(0.5))
        self.play(Rotate(shapes, PI/4))
        self.wait(0.5)
'''

NUMBER_LINE_ANIMATION = '''
from manim import *

class NumberLineAnimation(Scene):
    def construct(self):
        # Create number line (without numbers to avoid LaTeX)
        line = NumberLine(
            x_range=[-5, 5, 1],
            length=10,
            include_numbers=False,  # Avoid LaTeX
            include_ticks=True
        )
        self.play(Create(line))

        # Add a dot at position 2
        dot = Dot(color=RED).move_to(line.n2p(2))
        label = Text("x = 2", font_size=24).next_to(dot, UP)

        self.play(Create(dot), Write(label))
        self.wait(0.5)

        # Move dot to -3
        new_label = Text("x = -3", font_size=24).next_to(line.n2p(-3), UP)
        self.play(
            dot.animate.move_to(line.n2p(-3)),
            Transform(label, new_label)
        )
        self.wait(0.5)
'''

# Code that requires LaTeX
EQUATION_WITH_LATEX = '''
from manim import *

class EquationWithLatex(Scene):
    def construct(self):
        # This requires LaTeX
        eq = MathTex("x^2 + y^2 = r^2")
        self.play(Write(eq))
        self.wait(1)
'''


class TestManimRenderingNoLatex:
    """Test Manim rendering without LaTeX dependency."""

    @pytest.fixture
    def engine(self, tmp_path):
        """Create engine with mock API key."""
        import os
        original_key = os.environ.get("ANTHROPIC_API_KEY")
        os.environ["ANTHROPIC_API_KEY"] = "test-key-not-used"

        try:
            config = Config()
            config.output_dir = tmp_path / "output"
            config.manim_cache_dir = tmp_path / "cache"
            config.video_quality = VideoQuality.LOW
            engine = MathContentEngine(config)
            yield engine
        finally:
            if original_key:
                os.environ["ANTHROPIC_API_KEY"] = original_key
            else:
                os.environ.pop("ANTHROPIC_API_KEY", None)

    def test_render_simple_text(self, engine):
        """Test rendering simple text animation (no LaTeX)."""
        result = engine.generate_from_code(
            code=SIMPLE_TEXT_ANIMATION,
            output_filename="simple_text"
        )

        print(f"\nSuccess: {result.success}")
        print(f"Video path: {result.video_path}")
        print(f"Render time: {result.render_time:.2f}s")

        if not result.success:
            print(f"Error: {result.error_message}")

        assert result.success, f"Rendering failed: {result.error_message}"
        assert result.video_path is not None
        assert result.video_path.exists()
        assert result.video_path.stat().st_size > 0

    def test_render_shapes(self, engine):
        """Test rendering shapes animation (no LaTeX)."""
        result = engine.generate_from_code(
            code=SHAPES_ANIMATION,
            output_filename="shapes"
        )

        print(f"\nSuccess: {result.success}")
        print(f"Video path: {result.video_path}")

        if not result.success:
            print(f"Error: {result.error_message}")

        assert result.success, f"Rendering failed: {result.error_message}"
        assert result.video_path.exists()

    def test_render_number_line(self, engine):
        """Test rendering number line animation (no LaTeX)."""
        result = engine.generate_from_code(
            code=NUMBER_LINE_ANIMATION,
            output_filename="number_line"
        )

        print(f"\nSuccess: {result.success}")
        print(f"Video path: {result.video_path}")

        if not result.success:
            print(f"Error: {result.error_message}")

        assert result.success, f"Rendering failed: {result.error_message}"
        assert result.video_path.exists()


class TestManimRenderingWithLatex:
    """Tests that require LaTeX to be installed."""

    @pytest.fixture
    def engine(self, tmp_path):
        """Create engine with mock API key."""
        import os
        original_key = os.environ.get("ANTHROPIC_API_KEY")
        os.environ["ANTHROPIC_API_KEY"] = "test-key-not-used"

        try:
            config = Config()
            config.output_dir = tmp_path / "output"
            config.manim_cache_dir = tmp_path / "cache"
            config.video_quality = VideoQuality.LOW
            engine = MathContentEngine(config)
            yield engine
        finally:
            if original_key:
                os.environ["ANTHROPIC_API_KEY"] = original_key
            else:
                os.environ.pop("ANTHROPIC_API_KEY", None)

    @pytest.mark.skipif(not latex_available(), reason="LaTeX not installed")
    def test_render_equation_with_latex(self, engine):
        """Test rendering equation with LaTeX (requires LaTeX)."""
        result = engine.generate_from_code(
            code=EQUATION_WITH_LATEX,
            output_filename="equation_latex"
        )

        print(f"\nSuccess: {result.success}")
        print(f"Video path: {result.video_path}")

        if not result.success:
            print(f"Error: {result.error_message}")

        assert result.success, f"Rendering failed: {result.error_message}"
        assert result.video_path.exists()


class TestCodeValidation:
    """Test code validation without rendering."""

    def test_valid_code_passes(self):
        """Test that valid Manim code passes validation."""
        from math_content_engine.utils.validators import validate_manim_code

        result = validate_manim_code(SIMPLE_TEXT_ANIMATION)
        assert result.is_valid, f"Validation failed: {result.errors}"

    def test_all_test_codes_valid(self):
        """Test that all pre-written test codes are valid."""
        from math_content_engine.utils.validators import validate_manim_code

        codes = [
            ("Simple Text", SIMPLE_TEXT_ANIMATION),
            ("Shapes", SHAPES_ANIMATION),
            ("Number Line", NUMBER_LINE_ANIMATION),
            ("Equation (LaTeX)", EQUATION_WITH_LATEX),
        ]

        for name, code in codes:
            result = validate_manim_code(code)
            assert result.is_valid, f"{name} validation failed: {result.errors}"
            print(f"✓ {name} - valid")
