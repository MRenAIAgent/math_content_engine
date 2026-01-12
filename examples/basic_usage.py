#!/usr/bin/env python3
"""
Basic usage example for Math Content Engine.

This example demonstrates how to generate math animations from text descriptions.

Prerequisites:
1. Install dependencies: pip install -e .
2. Set up your API key:
   export ANTHROPIC_API_KEY=your-key-here
   # OR
   export OPENAI_API_KEY=your-key-here

3. Install Manim dependencies (see: https://docs.manim.community/en/stable/installation.html)
"""

import logging
from pathlib import Path

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

from math_content_engine import MathContentEngine, Config


def example_pythagorean_theorem():
    """Generate an animation explaining the Pythagorean theorem."""
    print("\n" + "="*60)
    print("Example 1: Pythagorean Theorem")
    print("="*60)

    engine = MathContentEngine()

    result = engine.generate(
        topic="Pythagorean theorem proof with visual squares on each side",
        requirements="Show the a² + b² = c² formula prominently. Use blue for side a, red for side b, and green for the hypotenuse c.",
        audience_level="high school",
        output_filename="pythagorean_theorem"
    )

    if result.success:
        print(f"✓ Video generated successfully!")
        print(f"  Output: {result.video_path}")
        print(f"  Render time: {result.render_time:.2f}s")
        print(f"  Total attempts: {result.total_attempts}")
    else:
        print(f"✗ Generation failed: {result.error_message}")
        print(f"\nGenerated code:\n{result.code}")

    return result


def example_quadratic_formula():
    """Generate an animation explaining the quadratic formula."""
    print("\n" + "="*60)
    print("Example 2: Quadratic Formula")
    print("="*60)

    engine = MathContentEngine()

    result = engine.generate(
        topic="Deriving the quadratic formula from ax² + bx + c = 0",
        requirements="Show step-by-step derivation using completing the square method. Highlight each transformation.",
        audience_level="high school",
        output_filename="quadratic_formula"
    )

    if result.success:
        print(f"✓ Video generated successfully!")
        print(f"  Output: {result.video_path}")
        print(f"  Render time: {result.render_time:.2f}s")
    else:
        print(f"✗ Generation failed: {result.error_message}")

    return result


def example_derivative_power_rule():
    """Generate an animation explaining the power rule for derivatives."""
    print("\n" + "="*60)
    print("Example 3: Derivative Power Rule")
    print("="*60)

    engine = MathContentEngine()

    result = engine.generate(
        topic="Power rule for derivatives: d/dx(x^n) = nx^(n-1)",
        requirements="Start with definition of derivative as a limit. Show examples with n=2, n=3. Include graphical representation showing tangent lines.",
        audience_level="college",
        output_filename="power_rule"
    )

    if result.success:
        print(f"✓ Video generated successfully!")
        print(f"  Output: {result.video_path}")
    else:
        print(f"✗ Generation failed: {result.error_message}")

    return result


def example_unit_circle():
    """Generate an animation about the unit circle and trigonometry."""
    print("\n" + "="*60)
    print("Example 4: Unit Circle Trigonometry")
    print("="*60)

    engine = MathContentEngine()

    result = engine.generate(
        topic="Unit circle and basic trigonometric functions",
        requirements="Show a point moving around the unit circle. Display corresponding sine and cosine values. Show the relationship between the angle and the x,y coordinates.",
        audience_level="high school",
        output_filename="unit_circle"
    )

    if result.success:
        print(f"✓ Video generated successfully!")
        print(f"  Output: {result.video_path}")
    else:
        print(f"✗ Generation failed: {result.error_message}")

    return result


def example_preview_code():
    """Demonstrate code preview without rendering."""
    print("\n" + "="*60)
    print("Example 5: Preview Code (No Rendering)")
    print("="*60)

    engine = MathContentEngine()

    # Just generate the code without rendering
    result = engine.preview_code(
        topic="Simple graph of y = x²",
        requirements="Show the parabola with labeled vertex and axis of symmetry",
        audience_level="middle school"
    )

    print(f"Code valid: {result.validation.is_valid}")
    print(f"Scene name: {result.scene_name}")
    print(f"Attempts: {result.attempts}")

    if result.validation.warnings:
        print(f"Warnings: {result.validation.warnings}")

    print(f"\nGenerated code:\n{'='*40}")
    print(result.code)
    print("="*40)

    return result


def main():
    """Run all examples."""
    print("Math Content Engine - Usage Examples")
    print("="*60)

    # Run the preview example (doesn't require Manim rendering)
    example_preview_code()

    # Uncomment to run full video generation examples:
    # example_pythagorean_theorem()
    # example_quadratic_formula()
    # example_derivative_power_rule()
    # example_unit_circle()

    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60)


if __name__ == "__main__":
    main()
