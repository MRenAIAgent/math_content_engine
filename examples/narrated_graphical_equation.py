"""
Narrated Graphical Equation Animation

This example creates a math animation that shows the graphical solution
to 2x + 3 = 7 with voice narration.

Visual approach: Shows where the line y = 2x + 3 intersects y = 7

Requirements:
    pip install edge-tts

Run:
    python examples/narrated_graphical_equation.py

Output:
    tests/test_output/narrated_graphical_equation.mp4
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from manim import *


class NarratedGraphicalSolutionScene(Scene):
    """
    Graphical solution with timing designed for narration.
    Shows the intersection of y = 2x + 3 and y = 7.
    """

    def construct(self):
        # ===== INTRO (0-4s) =====
        title = Text("Solving Equations Graphically", font_size=38, color=BLUE)
        self.play(Write(title))
        self.wait(1)

        subtitle = Text("Finding where 2x + 3 = 7", font_size=28)
        subtitle.next_to(title, DOWN, buff=0.3)
        self.play(Write(subtitle))
        self.wait(2)

        self.play(FadeOut(title), FadeOut(subtitle))  # Total: ~4s

        # ===== SETUP AXES (4-8s) =====
        axes = Axes(
            x_range=[-1, 5, 1],
            y_range=[-1, 10, 2],
            x_length=6,
            y_length=5,
            axis_config={"include_numbers": False},
        ).shift(DOWN * 0.3)

        # Manual labels (no LaTeX)
        x_nums = VGroup(*[
            Text(str(i), font_size=16).next_to(axes.c2p(i, 0), DOWN, buff=0.1)
            for i in range(0, 5)
        ])
        y_nums = VGroup(*[
            Text(str(i), font_size=16).next_to(axes.c2p(0, i), LEFT, buff=0.1)
            for i in range(0, 10, 2)
        ])

        x_label = Text("x", font_size=24).next_to(axes.x_axis, RIGHT)
        y_label = Text("y", font_size=24).next_to(axes.y_axis, UP)

        self.play(Create(axes))
        self.play(Write(x_nums), Write(y_nums), Write(x_label), Write(y_label))
        self.wait(1)  # Total: ~8s

        # ===== FIRST LINE (8-14s) =====
        line1 = axes.plot(lambda x: 2*x + 3, x_range=[-0.3, 3.5], color=BLUE)
        line1_label = Text("y = 2x + 3", font_size=24, color=BLUE)
        line1_label.next_to(axes.c2p(3.5, 10), LEFT)

        equation_box = Rectangle(width=3, height=0.6, color=BLUE, fill_opacity=0.2)
        equation_box.move_to(line1_label)

        self.play(Create(line1), run_time=2)
        self.play(Write(line1_label), Create(equation_box))
        self.wait(2)  # Total: ~14s

        # ===== SECOND LINE (14-20s) =====
        line2 = axes.plot(lambda x: 7, x_range=[-0.5, 4], color=RED)
        line2_label = Text("y = 7", font_size=24, color=RED)
        line2_label.next_to(axes.c2p(-0.5, 7), LEFT)

        self.play(Create(line2), run_time=1.5)
        self.play(Write(line2_label))

        # Explain what we're looking for
        question = Text("Where do they intersect?", font_size=26, color=YELLOW)
        question.to_edge(UP)
        self.play(Write(question))
        self.wait(2)  # Total: ~20s

        # ===== FIND INTERSECTION (20-28s) =====
        self.play(FadeOut(question))

        # Highlight intersection
        intersection = Dot(axes.c2p(2, 7), color=YELLOW, radius=0.18)
        self.play(Create(intersection))
        self.play(Flash(intersection, color=YELLOW, line_length=0.4))
        self.wait(1)

        # Label the point
        point_label = Text("(2, 7)", font_size=28, color=YELLOW)
        point_label.next_to(intersection, UR, buff=0.2)
        self.play(Write(point_label))
        self.wait(1)

        # Draw vertical dashed line to x-axis
        dashed = DashedLine(axes.c2p(2, 7), axes.c2p(2, 0), color=GREEN)
        x_dot = Dot(axes.c2p(2, 0), color=GREEN, radius=0.12)

        self.play(Create(dashed), Create(x_dot))
        self.wait(1)  # Total: ~28s

        # ===== SOLUTION (28-45s) =====
        solution_box = Rectangle(width=4, height=1.2, color=GREEN, fill_opacity=0.2)
        solution_box.to_edge(DOWN).shift(UP * 0.5)

        solution_text = Text("Solution: x = 2", font_size=36, color=GREEN)
        solution_text.move_to(solution_box)

        self.play(Create(solution_box), Write(solution_text))
        self.play(Indicate(solution_text, scale_factor=1.2, color=GREEN))
        self.wait(2)

        # Additional explanation
        explain = Text("The x-value where the lines cross!", font_size=22)
        explain.next_to(solution_box, UP, buff=0.2)
        self.play(Write(explain))
        self.wait(8)  # Extended wait for narration to complete - Total: ~45s


def create_graphical_narration_script():
    """Create narration script for graphical solution.

    IMPORTANT: Each cue needs enough time gap to complete before the next one starts.
    Rule of thumb: ~150 words per minute = ~2.5 words per second
    So a 10-word sentence takes about 4 seconds.
    """
    from math_content_engine.tts import AnimationScript

    script = AnimationScript("Graphical Solution to 2x + 3 = 7")

    # Intro (0-6s) - ~15 words = ~6s
    script.add_cue(
        "Let's solve the equation 2x plus 3 equals 7 using a graph.",
        time=0.0
    )

    # Setting up axes (7-10s) - ~10 words = ~4s
    script.add_cue(
        "First, we set up a coordinate plane with x and y axes.",
        time=7.0
    )

    # First line (12-20s) - ~20 words = ~8s
    script.add_cue(
        "Now let's graph the left side of our equation. "
        "The line y equals 2x plus 3 is a straight line.",
        time=12.0
    )

    # Second line (21-26s) - ~12 words = ~5s
    script.add_cue(
        "Next, we graph y equals 7, which is a horizontal line.",
        time=21.0
    )

    # Finding intersection (27-35s) - ~18 words = ~7s
    script.add_cue(
        "Where do these lines intersect? Look! They cross at the point 2 comma 7.",
        time=27.0
    )

    # Solution (36-42s) - ~15 words = ~6s
    script.add_cue(
        "So our solution is x equals 2. That's the x-coordinate where the lines meet!",
        time=36.0
    )

    return script


def main():
    """Generate the narrated graphical animation."""
    import subprocess
    import tempfile

    output_dir = Path(__file__).parent.parent / "tests" / "test_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Creating Narrated Graphical Equation Animation")
    print("=" * 60)

    # Step 1: Render the Manim animation
    print("\n[1/3] Rendering Manim animation...")

    with tempfile.TemporaryDirectory() as temp_dir:
        cmd = [
            "manim", "-ql",
            "--media_dir", temp_dir,
            __file__,
            "NarratedGraphicalSolutionScene",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error rendering: {result.stderr}")
            return

        video_path = None
        for mp4 in Path(temp_dir).rglob("*.mp4"):
            video_path = mp4
            break

        if not video_path:
            print("Error: Video not found")
            return

        print(f"   Video rendered: {video_path.name}")

        # Step 2: Generate TTS narration with MALE teacher voice
        print("\n[2/3] Generating voice narration...")

        try:
            from math_content_engine.tts import (
                NarratedAnimationGenerator,
                VoiceStyle
            )

            script = create_graphical_narration_script()

            # Use male teacher voice for variety
            generator = NarratedAnimationGenerator(voice=VoiceStyle.TEACHER_MALE)

            print(f"   Voice: {VoiceStyle.TEACHER_MALE.value} (Male Teacher)")
            print(f"   Narration cues: {len(script.cues)}")

            # Step 3: Combine
            print("\n[3/3] Combining video with narration...")

            output_path = output_dir / "narrated_graphical_equation.mp4"

            result = generator.create_narrated_video(
                video_path=video_path,
                script=script,
                output_path=output_path
            )

            if result.success:
                print(f"\n{'=' * 60}")
                print("SUCCESS!")
                print(f"{'=' * 60}")
                print(f"Output: {result.video_path}")
                print(f"\nPlay with: open {result.video_path}")
            else:
                print(f"\nError: {result.error_message}")

        except ImportError as e:
            print(f"\nTTS not available: {e}")


if __name__ == "__main__":
    main()
