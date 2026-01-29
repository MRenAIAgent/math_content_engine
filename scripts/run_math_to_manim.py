#!/usr/bin/env python3
"""
Wrapper script to run Math-To-Manim pipeline with textbook content.

This uses the actual Math-To-Manim submodule (not a reimplementation).

Usage:
    # Install dependencies first
    pip install -r external/Math-To-Manim/requirements.txt

    # Run with topic
    python scripts/run_math_to_manim.py "Pythagorean theorem"

    # Run with textbook section
    python scripts/run_math_to_manim.py --section 2.3

    # Launch Gradio UI
    python scripts/run_math_to_manim.py --ui

    # List available sections
    python scripts/run_math_to_manim.py --list
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
MATH_TO_MANIM_DIR = PROJECT_ROOT / "external" / "Math-To-Manim"
OUTPUT_DIR = PROJECT_ROOT / "output"


# =============================================================================
# TEXTBOOK SECTIONS (from your Algebra 1 curriculum)
# =============================================================================

TEXTBOOK_SECTIONS = {
    "2.1": {
        "title": "Solving Equations with Addition/Subtraction",
        "prompt": """Create a Manim animation explaining how to solve equations using Addition and Subtraction Properties of Equality.

Key concepts:
- If a = b, then a - c = b - c (Subtraction Property)
- If a = b, then a + c = b + c (Addition Property)

Show step-by-step solutions for:
1. y + 37 = -13 (subtract 37 from both sides)
2. a - 28 = -37 (add 28 to both sides)

Use a balance scale visualization to show equality being maintained.
Include verification steps at the end.""",
    },
    "2.2": {
        "title": "Solving Equations with Multiplication/Division",
        "prompt": """Create a Manim animation explaining how to solve equations using Multiplication and Division Properties of Equality.

Key concepts:
- Division Property: if a = b, then a/c = b/c (c ≠ 0)
- Multiplication Property: if a = b, then ac = bc

Show step-by-step solutions for:
1. 7x = 91 (divide both sides by 7)
2. n/6 = 15 (multiply both sides by 6)
3. (2/3)x = 18 (multiply by reciprocal 3/2)

Visualize the operations geometrically where possible.""",
    },
    "2.3": {
        "title": "Two-Step Equations",
        "prompt": """Create a Manim animation showing how to solve two-step equations like 2x + 3 = 11.

Process:
1. First, isolate the variable term (use addition/subtraction)
2. Then, solve for the variable (use multiplication/division)

Show with balance scale model:
- Start: 2x + 3 = 11
- Step 1: 2x + 3 - 3 = 11 - 3 → 2x = 8
- Step 2: 2x/2 = 8/2 → x = 4
- Verify: 2(4) + 3 = 11 ✓

Use color coding: variable terms in blue, constants in orange.""",
    },
    "5.1": {
        "title": "Slope of a Line",
        "prompt": """Create a Manim animation explaining slope as rise over run.

Key concepts:
- Slope formula: m = (y₂ - y₁)/(x₂ - x₁) = rise/run
- Positive slope: line goes up from left to right
- Negative slope: line goes down from left to right
- Zero slope: horizontal line
- Undefined slope: vertical line

Visualize:
1. Draw coordinate plane
2. Plot two points: (1, 2) and (4, 8)
3. Show the "rise" (vertical change) = 6
4. Show the "run" (horizontal change) = 3
5. Calculate slope = 6/3 = 2

Add slope triangles animated between the points.""",
    },
    "5.2": {
        "title": "Slope-Intercept Form y = mx + b",
        "prompt": """Create a Manim animation demonstrating slope-intercept form y = mx + b.

Show how:
- m (slope) controls the steepness/direction
- b (y-intercept) controls vertical position

Animate three lines side by side:
1. y = 2x + 1 (slope=2, crosses y-axis at 1)
2. y = 2x - 3 (same slope, shifted down)
3. y = -x + 1 (negative slope, same y-intercept as line 1)

Use sliders/transitions to show what happens when m or b changes.
Label each component clearly with color coding.""",
    },
    "6.1": {
        "title": "Systems of Equations - Graphing",
        "prompt": """Create a Manim animation showing how to solve systems of equations by graphing.

System to solve:
- Line 1: y = 2x + 1 (blue)
- Line 2: y = -x + 4 (red)

Steps:
1. Draw coordinate plane
2. Graph Line 1: start at (0,1), use slope 2
3. Graph Line 2: start at (0,4), use slope -1
4. Animate the intersection point appearing
5. Show solution is (1, 3)
6. Verify: 3 = 2(1) + 1 ✓ and 3 = -(1) + 4 ✓

Highlight the intersection point with a circle and label.""",
    },
    "9.1": {
        "title": "Graphing Quadratic Functions",
        "prompt": """Create a Manim animation explaining quadratic functions and parabolas.

Graph y = x² - 4x + 3 showing:
1. The parabola shape (opens upward since a=1>0)
2. Vertex at (2, -1) - use formula x = -b/(2a)
3. Axis of symmetry: x = 2 (dashed vertical line)
4. Y-intercept: (0, 3)
5. X-intercepts: (1, 0) and (3, 0)

Animate:
- Points plotting along the curve
- The vertex being highlighted
- Symmetry by reflecting points across axis""",
    },
    "9.3": {
        "title": "Completing the Square",
        "prompt": """Create a Manim animation demonstrating completing the square geometrically.

Show x² + 6x + ? = (x + 3)²

Geometric visualization:
1. Start with a square of side x (area = x²)
2. Add rectangles: two rectangles of area 3x each (total 6x)
3. Show the missing corner piece needed to complete the square
4. The missing piece is 3² = 9
5. Final perfect square: (x + 3)²

Use colored squares and rectangles to build up the visual.
This connects algebra to geometry beautifully.""",
    },
    "9.4": {
        "title": "Quadratic Formula",
        "prompt": """Create a Manim animation deriving and applying the quadratic formula.

Derivation from ax² + bx + c = 0:
1. Divide by a: x² + (b/a)x + c/a = 0
2. Move constant: x² + (b/a)x = -c/a
3. Complete square: add (b/2a)² to both sides
4. Factor left side: (x + b/2a)² = (b² - 4ac)/4a²
5. Take square root: x + b/2a = ±√(b² - 4ac)/2a
6. Solve for x: x = (-b ± √(b² - 4ac))/2a

Then apply to solve x² + 5x + 6 = 0:
- a=1, b=5, c=6
- x = (-5 ± √(25-24))/2 = (-5 ± 1)/2
- x = -2 or x = -3

Show each step with proper LaTeX formatting.""",
    },
}


def check_dependencies():
    """Check if Math-To-Manim dependencies are installed."""
    try:
        import anthropic
        import gradio
        return True
    except ImportError:
        return False


def install_dependencies():
    """Install Math-To-Manim dependencies."""
    req_file = MATH_TO_MANIM_DIR / "requirements.txt"
    if req_file.exists():
        print("📦 Installing Math-To-Manim dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file)], check=True)
    else:
        print(f"❌ Requirements file not found: {req_file}")
        print("   Run: git submodule update --init")
        sys.exit(1)


def run_claude_ui():
    """Launch the Math-To-Manim Gradio UI."""
    print("\n🚀 Launching Math-To-Manim Gradio UI...")
    print("   URL: http://localhost:7860\n")

    app_path = MATH_TO_MANIM_DIR / "src" / "app_claude.py"
    os.chdir(MATH_TO_MANIM_DIR)
    subprocess.run([sys.executable, str(app_path)])


def run_claude_pipeline(prompt: str, output_file: str = None):
    """Run the Claude pipeline directly (without Gradio)."""
    from anthropic import Anthropic
    from dotenv import load_dotenv
    import re

    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = Anthropic(api_key=api_key)

    # Use Claude Sonnet for cost efficiency (Opus is expensive)
    model = "claude-sonnet-4-20250514"

    system_prompt = """You are an expert Manim animator and mathematics educator.

Generate complete, working Manim Community Edition code for the requested animation.

Requirements:
1. Use proper imports: from manim import *
2. Define a Scene class with construct() method
3. Use LaTeX for mathematical expressions (raw strings)
4. Include timing with self.wait() between steps
5. Use appropriate colors and positioning
6. Add comments explaining the animation logic

Return ONLY the Python code, no explanations."""

    print(f"\n🤖 Generating animation code with Claude...")
    print(f"   Prompt: {prompt[:100]}...")

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.content[0].text

    # Extract Python code
    code_match = re.search(r"```python\s*(.*?)```", content, re.DOTALL)
    code = code_match.group(1) if code_match else content

    # Save code
    if not output_file:
        output_file = OUTPUT_DIR / "math_to_manim_output.py"
    else:
        output_file = Path(output_file)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(code)

    print(f"\n✅ Code generated: {output_file}")

    # Extract scene name for render command
    scene_match = re.search(r"class\s+(\w+)\s*\(\s*Scene\s*\)", code)
    scene_name = scene_match.group(1) if scene_match else "GeneratedScene"

    print(f"\n📋 To render, run:")
    print(f"   manim -pql {output_file} {scene_name}")

    return output_file, scene_name


def render_video(code_file: Path, scene_name: str, quality: str = "l"):
    """Render the generated Manim code."""
    cmd = f"manim -pq{quality} {code_file} {scene_name}"
    print(f"\n🎥 Rendering: {cmd}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0


def list_sections():
    """List available textbook sections."""
    print("\n📚 Available Textbook Sections (Algebra 1)")
    print("=" * 60)

    for key, section in TEXTBOOK_SECTIONS.items():
        print(f"\n{key}: {section['title']}")
        # Show first 100 chars of prompt
        preview = section['prompt'].split('\n')[0][:80]
        print(f"   {preview}...")


def main():
    parser = argparse.ArgumentParser(
        description="Run Math-To-Manim with textbook content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Generate from topic
    python scripts/run_math_to_manim.py "Pythagorean theorem"

    # Generate from textbook section
    python scripts/run_math_to_manim.py --section 2.3

    # Launch Gradio UI
    python scripts/run_math_to_manim.py --ui

    # List available sections
    python scripts/run_math_to_manim.py --list

    # Generate and render
    python scripts/run_math_to_manim.py "Slope" --render
        """
    )

    parser.add_argument("topic", nargs="?", help="Math topic to animate")
    parser.add_argument("--section", "-s", help="Textbook section (e.g., 2.3, 5.1)")
    parser.add_argument("--ui", action="store_true", help="Launch Gradio web interface")
    parser.add_argument("--list", action="store_true", help="List textbook sections")
    parser.add_argument("--render", action="store_true", help="Render after generation")
    parser.add_argument("--quality", "-q", choices=["l", "m", "h"], default="l", help="Render quality")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--install", action="store_true", help="Install dependencies")

    args = parser.parse_args()

    # Check submodule exists
    if not MATH_TO_MANIM_DIR.exists():
        print("❌ Math-To-Manim submodule not found!")
        print("   Run: git submodule update --init")
        return 1

    # Install dependencies if requested
    if args.install:
        install_dependencies()
        return 0

    # List sections
    if args.list:
        list_sections()
        return 0

    # Launch UI
    if args.ui:
        if not check_dependencies():
            print("❌ Dependencies not installed. Run with --install first")
            return 1
        run_claude_ui()
        return 0

    # Get prompt from section or topic
    if args.section:
        if args.section not in TEXTBOOK_SECTIONS:
            print(f"❌ Unknown section: {args.section}")
            print(f"   Available: {', '.join(TEXTBOOK_SECTIONS.keys())}")
            return 1
        section = TEXTBOOK_SECTIONS[args.section]
        prompt = section["prompt"]
        print(f"\n📖 Section {args.section}: {section['title']}")
    elif args.topic:
        prompt = f"Create a Manim animation explaining: {args.topic}"
    else:
        parser.print_help()
        return 1

    # Check dependencies
    if not check_dependencies():
        print("❌ Dependencies not installed. Run with --install first")
        return 1

    # Run pipeline
    code_file, scene_name = run_claude_pipeline(prompt, args.output)

    # Render if requested
    if args.render:
        success = render_video(code_file, scene_name, args.quality)
        return 0 if success else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
