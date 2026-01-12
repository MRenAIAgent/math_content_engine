"""
Generate Narrated Graphical Equation Animation in All Styles

This script generates the same math animation (graphical solution to 2x + 3 = 7)
in two different visual styles:
1. Dark - Dark background (default Manim style)
2. Light - Light/white background

Requirements:
    - API key configured (ANTHROPIC_API_KEY or OPENAI_API_KEY)
    - pip install edge-tts (for narration)

Run:
    python examples/generate_all_styles.py

Output:
    tests/test_output/graphical_dark.mp4
    tests/test_output/graphical_light.mp4
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from math_content_engine import MathContentEngine, Config
from math_content_engine.config import AnimationStyle, VideoQuality


# Topic description for the LLM
TOPIC = "Solving the equation 2x + 3 = 7 graphically"

REQUIREMENTS = """
Create a graphical/visual solution showing:
1. A coordinate plane with x and y axes (x from -1 to 5, y from -1 to 10)
2. Plot the line y = 2x + 3 in blue
3. Plot the horizontal line y = 7 in red
4. Highlight where they intersect (at point (2, 7))
5. Show that the solution is x = 2
6. Include clear labels for both lines
7. Add a final answer box showing "Solution: x = 2"

Keep the animation between 30-45 seconds.
Use Text() instead of MathTex() for labels to avoid LaTeX issues.
"""


def create_narration_script():
    """Create narration script for the graphical solution."""
    from math_content_engine.tts import AnimationScript

    script = AnimationScript("Graphical Solution to 2x + 3 = 7")

    # Intro
    script.add_cue(
        "Let's solve the equation 2x plus 3 equals 7 using a graph.",
        time=0.0
    )

    # Setting up axes
    script.add_cue(
        "First, we set up a coordinate plane with x and y axes.",
        time=5.0
    )

    # First line
    script.add_cue(
        "Now let's graph the left side of our equation. "
        "The line y equals 2x plus 3 is shown in blue.",
        time=10.0
    )

    # Second line
    script.add_cue(
        "Next, we graph y equals 7, which is a horizontal red line.",
        time=18.0
    )

    # Finding intersection
    script.add_cue(
        "Where do these lines intersect? They cross at the point 2 comma 7.",
        time=25.0
    )

    # Solution
    script.add_cue(
        "So our solution is x equals 2. That's the x-coordinate where the lines meet!",
        time=32.0
    )

    return script


def generate_for_style(style: AnimationStyle, output_dir: Path) -> bool:
    """Generate animation for a specific style."""
    style_name = style.value
    print(f"\n{'='*60}")
    print(f"Generating {style_name.upper()} style...")
    print(f"{'='*60}")

    # Configure engine with this style
    config = Config()
    config.animation_style = style
    config.video_quality = VideoQuality.MEDIUM
    config.output_dir = output_dir

    engine = MathContentEngine(config)

    # Generate the animation
    result = engine.generate(
        topic=TOPIC,
        requirements=REQUIREMENTS,
        audience_level="high school",
        output_filename=f"graphical_{style_name}"
    )

    if result.success:
        print(f"Video generated: {result.video_path}")
        print(f"Render time: {result.render_time:.2f}s")
        print(f"Attempts: {result.total_attempts}")
        return True
    else:
        print(f"Failed: {result.error_message}")
        # Save the generated code for debugging
        code_path = output_dir / f"graphical_{style_name}_failed.py"
        code_path.write_text(result.code)
        print(f"Code saved to: {code_path}")
        return False


def add_narration(video_path: Path, output_path: Path) -> bool:
    """Add narration to a video."""
    try:
        from math_content_engine.tts import NarratedAnimationGenerator, VoiceStyle

        script = create_narration_script()
        generator = NarratedAnimationGenerator(voice=VoiceStyle.TEACHER_MALE)

        result = generator.create_narrated_video(
            video_path=video_path,
            script=script,
            output_path=output_path
        )

        return result.success
    except ImportError:
        print("TTS not available - skipping narration")
        return False


def main():
    """Generate animations in all three styles."""
    output_dir = Path(__file__).parent.parent / "tests" / "test_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    styles = [
        AnimationStyle.DARK,
        AnimationStyle.LIGHT,
    ]

    results = {}

    # Generate each style
    for style in styles:
        success = generate_for_style(style, output_dir)
        results[style.value] = success

    # Summary
    print("\n" + "="*60)
    print("GENERATION SUMMARY")
    print("="*60)

    for style_name, success in results.items():
        status = "SUCCESS" if success else "FAILED"
        video_path = output_dir / f"graphical_{style_name}.mp4"
        print(f"  {style_name:15} {status:10} {video_path}")

    # Add narration to successful videos
    print("\n" + "="*60)
    print("ADDING NARRATION")
    print("="*60)

    for style_name, success in results.items():
        if success:
            video_path = output_dir / f"graphical_{style_name}.mp4"
            narrated_path = output_dir / f"narrated_graphical_{style_name}.mp4"

            print(f"\nAdding narration to {style_name}...")
            if add_narration(video_path, narrated_path):
                print(f"  Created: {narrated_path}")
            else:
                print(f"  Failed to add narration")

    print("\n" + "="*60)
    print("DONE!")
    print("="*60)
    print(f"\nOutput directory: {output_dir}")
    print("\nTo play videos:")
    for style_name in results.keys():
        print(f"  open {output_dir}/narrated_graphical_{style_name}.mp4")


if __name__ == "__main__":
    main()
