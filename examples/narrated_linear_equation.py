"""
Narrated Linear Equation Animation

This example creates a math animation with voice narration explaining
how to solve the equation 2x + 3 = 7.

The animation shows both:
1. Step-by-step algebraic solution
2. Graphical representation (line intersection)

Requirements:
    pip install edge-tts

Run:
    python examples/narrated_linear_equation.py

Output:
    tests/test_output/narrated_linear_equation.mp4
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from manim import *


class NarratedLinearEquationScene(Scene):
    """
    Linear equation animation designed for voice narration.

    Timing is carefully planned to sync with narration cues.
    """

    def construct(self):
        # ===== INTRO (0-3s) =====
        # Narration: "Let's solve the equation 2x plus 3 equals 7"
        title = Text("Solving Linear Equations", font_size=42, color=BLUE)
        equation = Text("2x + 3 = 7", font_size=48)
        equation.next_to(title, DOWN, buff=0.5)

        self.play(Write(title))
        self.play(Write(equation))
        self.wait(2)  # Total: ~3s

        # ===== STEP 1 (3-7s) =====
        # Narration: "First, we need to isolate x. Let's subtract 3 from both sides."
        self.play(title.animate.scale(0.6).to_edge(UP))
        self.play(equation.animate.move_to(UP * 1.5))

        step1 = Text("Step 1: Subtract 3 from both sides", font_size=28, color=YELLOW)
        step1.next_to(equation, DOWN, buff=0.5)
        self.play(Write(step1))
        self.wait(1)

        # Show the operation
        minus3 = Text("- 3", font_size=36, color=RED)
        minus3_copy = Text("- 3", font_size=36, color=RED)
        minus3.next_to(equation, DOWN, buff=0.3).shift(LEFT * 0.5)
        minus3_copy.next_to(equation, DOWN, buff=0.3).shift(RIGHT * 1.2)

        self.play(Write(minus3), Write(minus3_copy))
        self.wait(1)  # Total: ~7s

        # ===== STEP 2 (7-11s) =====
        # Narration: "This gives us 2x equals 4."
        equation2 = Text("2x = 4", font_size=48, color=GREEN)
        equation2.move_to(equation.get_center())

        self.play(
            FadeOut(step1), FadeOut(minus3), FadeOut(minus3_copy),
            ReplacementTransform(equation, equation2)
        )
        self.wait(1)

        step2 = Text("Step 2: Divide both sides by 2", font_size=28, color=YELLOW)
        step2.next_to(equation2, DOWN, buff=0.5)
        self.play(Write(step2))
        self.wait(2)  # Total: ~11s

        # ===== STEP 3 (11-15s) =====
        # Narration: "Now we divide both sides by 2 to get x by itself."
        divide2 = Text("÷ 2", font_size=36, color=RED)
        divide2_copy = Text("÷ 2", font_size=36, color=RED)
        divide2.next_to(equation2, DOWN, buff=0.3).shift(LEFT * 0.3)
        divide2_copy.next_to(equation2, DOWN, buff=0.3).shift(RIGHT * 0.5)

        self.play(Write(divide2), Write(divide2_copy))
        self.wait(2)  # Total: ~15s

        # ===== SOLUTION (15-19s) =====
        # Narration: "And we find that x equals 2!"
        solution = Text("x = 2", font_size=56, color=YELLOW)
        solution.move_to(equation2.get_center())

        self.play(
            FadeOut(step2), FadeOut(divide2), FadeOut(divide2_copy),
            ReplacementTransform(equation2, solution)
        )
        self.play(Indicate(solution, scale_factor=1.3, color=YELLOW))
        self.wait(1)  # Total: ~19s

        # ===== VERIFICATION (19-25s) =====
        # Narration: "Let's check: 2 times 2 plus 3 equals 4 plus 3 equals 7. Correct!"
        box = SurroundingRectangle(solution, color=GREEN, buff=0.2)
        self.play(Create(box))

        verify_title = Text("Verification:", font_size=28, color=WHITE)
        verify_title.next_to(box, DOWN, buff=0.5)

        verify1 = Text("2(2) + 3 = ?", font_size=32)
        verify1.next_to(verify_title, DOWN, buff=0.3)

        self.play(Write(verify_title), Write(verify1))
        self.wait(1)

        verify2 = Text("4 + 3 = 7 ✓", font_size=32, color=GREEN)
        verify2.next_to(verify1, DOWN, buff=0.2)

        self.play(Write(verify2))
        self.play(Indicate(verify2, color=GREEN))
        self.wait(2)  # Total: ~25s

        # ===== CONCLUSION (25-28s) =====
        # Narration: "Great job! Remember, always do the same operation to both sides."
        self.play(FadeOut(verify_title), FadeOut(verify1), FadeOut(verify2))

        conclusion = Text(
            "Remember: Same operation on both sides!",
            font_size=32, color=BLUE
        )
        conclusion.next_to(box, DOWN, buff=0.5)
        self.play(Write(conclusion))
        self.wait(3)  # Total: ~28s


def create_narration_script():
    """Create the narration script with timing."""
    from math_content_engine.tts import AnimationScript

    script = AnimationScript("Solving 2x + 3 = 7")

    # Intro (starts at 0s)
    script.add_cue(
        "Let's solve the equation 2x plus 3 equals 7.",
        time=0.0
    )

    # Step 1 (starts at 3s)
    script.add_cue(
        "First, we need to isolate x. Let's subtract 3 from both sides.",
        time=3.0
    )

    # Step 2 (starts at 7s)
    script.add_cue(
        "This gives us 2x equals 4.",
        time=7.5
    )

    # Step 3 (starts at 11s)
    script.add_cue(
        "Now we divide both sides by 2 to get x by itself.",
        time=11.0
    )

    # Solution (starts at 15s)
    script.add_cue(
        "And we find that x equals 2!",
        time=15.5
    )

    # Verification (starts at 19s)
    script.add_cue(
        "Let's check our answer. 2 times 2 plus 3 equals 4 plus 3, which equals 7. Correct!",
        time=19.0
    )

    # Conclusion (starts at 25s)
    script.add_cue(
        "Great job! Remember, always do the same operation to both sides of the equation.",
        time=25.0
    )

    return script


def main():
    """Generate the narrated animation."""
    import subprocess
    import tempfile

    output_dir = Path(__file__).parent.parent / "tests" / "test_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Creating Narrated Linear Equation Animation")
    print("=" * 60)

    # Step 1: Render the Manim animation
    print("\n[1/3] Rendering Manim animation...")

    with tempfile.TemporaryDirectory() as temp_dir:
        # Render video
        cmd = [
            "manim", "-ql",  # Low quality for faster testing
            "--media_dir", temp_dir,
            __file__,
            "NarratedLinearEquationScene",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error rendering: {result.stderr}")
            return

        # Find the rendered video
        video_path = None
        for mp4 in Path(temp_dir).rglob("*.mp4"):
            video_path = mp4
            break

        if not video_path:
            print("Error: Video not found after rendering")
            return

        print(f"   Video rendered: {video_path.name}")

        # Step 2: Generate TTS narration
        print("\n[2/3] Generating voice narration...")

        try:
            from math_content_engine.tts import (
                NarratedAnimationGenerator,
                VoiceStyle
            )

            script = create_narration_script()

            # Use teacher voice
            generator = NarratedAnimationGenerator(voice=VoiceStyle.TEACHER_FEMALE)

            print(f"   Voice: {VoiceStyle.TEACHER_FEMALE.value}")
            print(f"   Narration cues: {len(script.cues)}")

            # Step 3: Combine video with narration
            print("\n[3/3] Combining video with narration...")

            output_path = output_dir / "narrated_linear_equation.mp4"

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
            print("Install with: pip install edge-tts")

            # Still save the silent video
            import shutil
            silent_output = output_dir / "linear_equation_silent.mp4"
            shutil.copy(video_path, silent_output)
            print(f"\nSilent video saved to: {silent_output}")


if __name__ == "__main__":
    main()
