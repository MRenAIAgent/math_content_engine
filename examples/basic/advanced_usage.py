#!/usr/bin/env python3
"""
Advanced usage examples for Math Content Engine.

Demonstrates:
- Custom configuration
- Rendering from existing code
- Error handling
- Different output formats
"""

import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)

from math_content_engine import MathContentEngine, Config
from math_content_engine.config import LLMProvider, VideoQuality


def example_custom_config():
    """Use custom configuration settings."""
    print("\n" + "="*60)
    print("Example: Custom Configuration")
    print("="*60)

    # Create custom configuration
    config = Config()
    config.video_quality = VideoQuality.HIGH  # 1080p
    config.max_retries = 3
    config.temperature = 0.5  # More deterministic

    engine = MathContentEngine(config)

    result = engine.generate(
        topic="Euler's identity: e^(iπ) + 1 = 0",
        requirements="Explain why this formula is beautiful. Show the connection between e, i, π, 1, and 0.",
        audience_level="college",
        output_filename="eulers_identity_hd"
    )

    return result


def example_render_existing_code():
    """Render animation from existing Manim code."""
    print("\n" + "="*60)
    print("Example: Render Existing Code")
    print("="*60)

    # Pre-written Manim code
    manim_code = '''
from manim import *

class CircleAreaScene(Scene):
    def construct(self):
        # Title
        title = Text("Area of a Circle").scale(0.8)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))

        # Create circle
        circle = Circle(radius=2, color=BLUE, fill_opacity=0.3)
        radius_line = Line(circle.get_center(), circle.get_right(), color=YELLOW)
        r_label = MathTex("r").next_to(radius_line, DOWN)

        self.play(Create(circle))
        self.play(Create(radius_line), Write(r_label))
        self.wait()

        # Show formula
        formula = MathTex("A", "=", "\\\\pi", "r^2")
        formula.scale(1.5)
        formula.to_edge(DOWN)

        self.play(Write(formula))
        self.wait()

        # Highlight pi
        self.play(
            formula[2].animate.set_color(RED),
            run_time=0.5
        )
        self.wait()

        # Highlight r²
        self.play(
            formula[3].animate.set_color(YELLOW),
            r_label.animate.set_color(YELLOW),
            run_time=0.5
        )
        self.wait(2)
'''

    engine = MathContentEngine()

    result = engine.generate_from_code(
        code=manim_code,
        output_filename="circle_area_custom"
    )

    if result.success:
        print(f"✓ Video rendered: {result.video_path}")
    else:
        print(f"✗ Rendering failed: {result.error_message}")

    return result


def example_gif_output():
    """Generate GIF output instead of MP4."""
    print("\n" + "="*60)
    print("Example: GIF Output")
    print("="*60)

    config = Config()
    config.output_format = "gif"
    config.video_quality = VideoQuality.LOW  # Lower quality for smaller GIF

    engine = MathContentEngine(config)

    result = engine.generate(
        topic="Simple sine wave animation",
        requirements="Show y = sin(x) being drawn smoothly. Keep it short and loopable.",
        audience_level="high school",
        output_filename="sine_wave"
    )

    if result.success:
        print(f"✓ GIF generated: {result.video_path}")
    else:
        print(f"✗ Generation failed: {result.error_message}")

    return result


def example_batch_generation():
    """Generate multiple animations in sequence."""
    print("\n" + "="*60)
    print("Example: Batch Generation")
    print("="*60)

    topics = [
        {
            "topic": "Addition of fractions with common denominators",
            "audience": "elementary",
            "filename": "fractions_add"
        },
        {
            "topic": "Multiplication of negative numbers",
            "audience": "middle school",
            "filename": "negative_multiply"
        },
        {
            "topic": "Slope of a line",
            "audience": "high school",
            "filename": "line_slope"
        },
    ]

    engine = MathContentEngine()
    results = []

    for i, item in enumerate(topics, 1):
        print(f"\n[{i}/{len(topics)}] Generating: {item['topic']}")

        result = engine.generate(
            topic=item["topic"],
            audience_level=item["audience"],
            output_filename=item["filename"]
        )

        results.append({
            "topic": item["topic"],
            "success": result.success,
            "path": result.video_path,
            "error": result.error_message
        })

        if result.success:
            print(f"  ✓ Success: {result.video_path}")
        else:
            print(f"  ✗ Failed: {result.error_message}")

    # Summary
    print("\n" + "="*60)
    print("Batch Generation Summary")
    print("="*60)
    successful = sum(1 for r in results if r["success"])
    print(f"Successful: {successful}/{len(results)}")

    return results


def example_error_handling():
    """Demonstrate error handling and recovery."""
    print("\n" + "="*60)
    print("Example: Error Handling")
    print("="*60)

    engine = MathContentEngine()

    # Try to render intentionally broken code
    broken_code = '''
from manim import *

class BrokenScene(Scene):
    def construct(self):
        # This will cause an error - undefined variable
        self.play(Write(undefined_text))
'''

    result = engine.generate_from_code(code=broken_code)

    if not result.success:
        print(f"Expected failure: {result.error_message}")
        print("\nThe engine detected the error properly.")
    else:
        print("Unexpectedly succeeded!")

    return result


def main():
    """Run advanced examples."""
    print("Math Content Engine - Advanced Examples")
    print("="*60)

    # Run examples that don't require actual rendering
    example_error_handling()

    # Uncomment to run full examples:
    # example_custom_config()
    # example_render_existing_code()
    # example_gif_output()
    # example_batch_generation()

    print("\n" + "="*60)
    print("Advanced examples completed!")
    print("="*60)


if __name__ == "__main__":
    main()
