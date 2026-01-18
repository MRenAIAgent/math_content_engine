"""
Integration tests for algebra animations.

These tests generate actual Manim animations to verify the full pipeline works.
They require:
1. ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable
2. Manim and its dependencies installed
3. Sufficient time (each test renders a video)

Run these tests with:
    pytest tests/test_algebra_integration.py -v

Run a specific test:
    pytest tests/test_algebra_integration.py::TestAlgebraAnimations::test_linear_equation -v

Skip slow rendering tests (code generation only):
    pytest tests/test_algebra_integration.py -m "not slow"

Test results are saved to: tests/test_output/
"""

import os
import subprocess
import pytest
from pathlib import Path
from datetime import datetime

from math_content_engine import MathContentEngine, Config
from math_content_engine.config import VideoQuality


# Directory to save test results
TEST_OUTPUT_DIR = Path(__file__).parent / "test_output"


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


def save_test_result(test_name: str, result, output_dir: Path):
    """Save test result (code and video) to output directory.

    Handles both GenerationResult (from preview_code) and AnimationResult (from generate).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save the generated code
    code_file = output_dir / f"{test_name}.py"
    code_file.write_text(result.code)

    # Check if this is an AnimationResult (from generate) or GenerationResult (from preview_code)
    is_animation_result = hasattr(result, 'success')

    # Save metadata
    meta_file = output_dir / f"{test_name}_meta.txt"

    if is_animation_result:
        # AnimationResult from generate() or generate_from_code()
        meta_content = f"""Test: {test_name}
Timestamp: {datetime.now().isoformat()}
Success: {result.success}
Scene Name: {result.scene_name}
Generation Attempts: {result.generation_attempts}
Render Attempts: {result.render_attempts}
Total Attempts: {result.total_attempts}
Render Time: {result.render_time:.2f}s
Video Path: {result.video_path}
Error: {result.error_message or 'None'}
"""
    else:
        # GenerationResult from preview_code()
        meta_content = f"""Test: {test_name}
Timestamp: {datetime.now().isoformat()}
Valid: {result.validation.is_valid}
Scene Name: {result.scene_name}
Attempts: {result.attempts}
Validation Errors: {result.validation.errors or 'None'}
Validation Warnings: {result.validation.warnings or 'None'}
"""

    meta_file.write_text(meta_content)

    # If video was created and exists in tmp, copy it (only for AnimationResult)
    if is_animation_result and result.video_path and result.video_path.exists():
        import shutil
        dest_video = output_dir / f"{test_name}.mp4"
        shutil.copy(result.video_path, dest_video)
        return dest_video

    return None


# Skip all tests if no API key is configured
pytestmark = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"),
    reason="No API key configured. Set ANTHROPIC_API_KEY or OPENAI_API_KEY."
)


class TestAlgebraAnimations:
    """
    Integration tests that generate algebra animations.

    These tests verify:
    1. LLM generates valid Manim code
    2. Code passes validation
    3. Manim renders the video successfully
    """

    @pytest.fixture
    def engine(self, tmp_path):
        """Create engine with temporary output directory."""
        config = Config()
        config.output_dir = tmp_path / "output"
        config.manim_cache_dir = tmp_path / "cache"
        config.video_quality = VideoQuality.LOW  # Fast rendering for tests
        config.max_retries = 3
        return MathContentEngine(config)

    @pytest.fixture
    def output_dir(self):
        """Return the persistent output directory for test results."""
        TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        return TEST_OUTPUT_DIR

    # =========================================================================
    # CODE GENERATION TESTS (Fast - no rendering)
    # =========================================================================

    def test_linear_equation_code_generation(self, engine, output_dir):
        """Test that linear equation code is generated correctly."""
        result = engine.preview_code(
            topic="Solving the linear equation 2x + 3 = 7",
            requirements="Show step-by-step solution. Use Text instead of MathTex to avoid LaTeX dependency.",
            audience_level="middle school"
        )

        # Save result
        save_test_result("linear_equation_code", result, output_dir)

        assert result.code is not None
        assert result.validation.is_valid, f"Validation errors: {result.validation.errors}"
        assert "from manim import" in result.code
        assert "Scene" in result.code
        assert "construct" in result.code
        print(f"\nGenerated scene: {result.scene_name}")
        print(f"Attempts: {result.attempts}")
        print(f"Code saved to: {output_dir}/linear_equation_code.py")

    def test_quadratic_formula_code_generation(self, engine, output_dir):
        """Test that quadratic formula code is generated correctly."""
        result = engine.preview_code(
            topic="The quadratic formula x = (-b ± sqrt(b²-4ac)) / 2a",
            requirements="Show the formula. Use Text for labels to avoid LaTeX. If using MathTex, keep it simple.",
            audience_level="high school"
        )

        # Save result
        save_test_result("quadratic_formula_code", result, output_dir)

        assert result.code is not None
        assert result.validation.is_valid, f"Validation errors: {result.validation.errors}"
        assert "from manim import" in result.code
        print(f"\nGenerated scene: {result.scene_name}")
        print(f"Code saved to: {output_dir}/quadratic_formula_code.py")

    def test_slope_intercept_code_generation(self, engine, output_dir):
        """Test that slope-intercept form code is generated correctly."""
        result = engine.preview_code(
            topic="Slope-intercept form y = mx + b",
            requirements="Show a line on coordinate plane using Axes. Label slope and y-intercept using Text (not MathTex).",
            audience_level="high school"
        )

        # Save result
        save_test_result("slope_intercept_code", result, output_dir)

        assert result.code is not None
        assert result.validation.is_valid, f"Validation errors: {result.validation.errors}"
        print(f"\nGenerated scene: {result.scene_name}")
        print(f"Code saved to: {output_dir}/slope_intercept_code.py")

    # =========================================================================
    # FULL RENDERING TESTS (Slow - actually renders video)
    # These tests avoid MathTex to work without LaTeX
    # =========================================================================

    @pytest.mark.slow
    def test_linear_equation_full_render(self, engine, output_dir):
        """Test full rendering of a linear equation animation."""
        result = engine.generate(
            topic="Solving 2x + 3 = 7 step by step",
            requirements="""
            IMPORTANT: Use Text() instead of MathTex() to avoid LaTeX dependency.
            1. Show the equation using Text("2x + 3 = 7")
            2. Show "Subtract 3 from both sides"
            3. Show Text("2x = 4")
            4. Show "Divide by 2"
            5. Show Text("x = 2")
            Use simple Text objects, NOT MathTex.
            Keep it simple with clear steps.
            """,
            audience_level="middle school",
            output_filename="test_linear_equation"
        )

        # Save result
        video_path = save_test_result("linear_equation_render", result, output_dir)

        print(f"\nSuccess: {result.success}")
        print(f"Video path: {result.video_path}")
        print(f"Render time: {result.render_time:.2f}s")
        print(f"Total attempts: {result.total_attempts}")
        print(f"Results saved to: {output_dir}")

        if not result.success:
            print(f"Error: {result.error_message}")
            print(f"\nGenerated code:\n{result.code}")

        assert result.success, f"Rendering failed: {result.error_message}"
        assert result.video_path is not None
        assert result.video_path.exists(), f"Video file not found at {result.video_path}"

    @pytest.mark.slow
    @pytest.mark.skipif(not latex_available(), reason="LaTeX not installed")
    def test_quadratic_formula_full_render(self, engine, output_dir):
        """Test full rendering of quadratic formula animation (requires LaTeX)."""
        result = engine.generate(
            topic="The quadratic formula",
            requirements="""
            Show x = (-b ± √(b²-4ac)) / 2a using MathTex
            Use colors: a=blue, b=red, c=green
            Add a title "The Quadratic Formula"
            Keep animation under 10 seconds
            """,
            audience_level="high school",
            output_filename="test_quadratic_formula"
        )

        # Save result
        video_path = save_test_result("quadratic_formula_render", result, output_dir)

        print(f"\nSuccess: {result.success}")
        print(f"Video path: {result.video_path}")
        print(f"Render time: {result.render_time:.2f}s")
        print(f"Results saved to: {output_dir}")

        if not result.success:
            print(f"Error: {result.error_message}")

        assert result.success, f"Rendering failed: {result.error_message}"
        assert result.video_path.exists()

    @pytest.mark.slow
    def test_pythagorean_theorem_full_render(self, engine, output_dir):
        """Test full rendering of Pythagorean theorem animation."""
        result = engine.generate(
            topic="Pythagorean theorem a² + b² = c²",
            requirements="""
            IMPORTANT: Use Text() instead of MathTex() to avoid LaTeX dependency.
            1. Draw a right triangle using Polygon
            2. Label sides as "a", "b", "c" using Text objects
            3. Show the formula using Text("a² + b² = c²")
            Use Text() NOT MathTex(). Simple animation, under 15 seconds.
            """,
            audience_level="middle school",
            output_filename="test_pythagorean"
        )

        # Save result
        video_path = save_test_result("pythagorean_render", result, output_dir)

        print(f"\nSuccess: {result.success}")
        print(f"Video path: {result.video_path}")
        print(f"Results saved to: {output_dir}")

        if not result.success:
            print(f"Error: {result.error_message}")

        assert result.success, f"Rendering failed: {result.error_message}"
        assert result.video_path.exists()

    # =========================================================================
    # RENDER FROM EXISTING CODE TEST (No LaTeX needed)
    # =========================================================================

    @pytest.mark.slow
    def test_render_existing_algebra_code(self, engine, output_dir):
        """Test rendering from pre-written Manim code (no LaTeX)."""
        algebra_code = '''
from manim import *

class SimpleAlgebraScene(Scene):
    def construct(self):
        # Title
        title = Text("Solving for x").scale(0.8)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))

        # Equation (using Text to avoid LaTeX)
        eq1 = Text("2x + 4 = 10", font_size=48)
        self.play(Write(eq1))
        self.wait(0.5)

        # Step 1: Subtract 4
        step1 = Text("Subtract 4 from both sides", font_size=24)
        step1.next_to(eq1, DOWN)
        self.play(Write(step1))
        self.wait(0.5)

        eq2 = Text("2x = 6", font_size=48)
        eq2.move_to(eq1.get_center())
        self.play(
            FadeOut(step1),
            Transform(eq1, eq2)
        )
        self.wait(0.5)

        # Step 2: Divide by 2
        step2 = Text("Divide both sides by 2", font_size=24)
        step2.next_to(eq1, DOWN)
        self.play(Write(step2))
        self.wait(0.5)

        eq3 = Text("x = 3", font_size=48, color=GREEN)
        eq3.move_to(eq1.get_center())
        self.play(
            FadeOut(step2),
            Transform(eq1, eq3)
        )

        # Highlight answer
        box = SurroundingRectangle(eq1, color=GREEN)
        self.play(Create(box))
        self.wait(1)
'''

        result = engine.generate_from_code(
            code=algebra_code,
            output_filename="test_existing_code"
        )

        # Save result
        video_path = save_test_result("existing_code_render", result, output_dir)

        print(f"\nSuccess: {result.success}")
        print(f"Video path: {result.video_path}")
        print(f"Render time: {result.render_time:.2f}s")
        print(f"Results saved to: {output_dir}")

        if not result.success:
            print(f"Error: {result.error_message}")

        assert result.success, f"Rendering failed: {result.error_message}"
        assert result.video_path.exists()


class TestAlgebraElevenLabsNarration:
    """Integration tests for algebra videos with ElevenLabs voice narration."""

    @pytest.fixture
    def engine(self, tmp_path):
        """Create engine with temporary output directory."""
        config = Config()
        config.output_dir = tmp_path / "output"
        config.manim_cache_dir = tmp_path / "cache"
        config.video_quality = VideoQuality.LOW  # Fast rendering for tests
        config.max_retries = 3
        return MathContentEngine(config)

    @pytest.fixture
    def output_dir(self):
        """Return the persistent output directory for test results."""
        TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        return TEST_OUTPUT_DIR

    @pytest.mark.skipif(
        not os.getenv("ELEVENLABS_API_KEY"),
        reason="ELEVENLABS_API_KEY not set. Set it to run ElevenLabs tests."
    )
    def test_elevenlabs_tts_generation_only(self, output_dir):
        """
        Quick test: verify ElevenLabs TTS generation works (no video rendering).

        This is a fast test that only checks:
        1. ElevenLabs API key is valid
        2. TTS provider can be created
        3. Audio can be generated from text
        """
        from math_content_engine.tts import create_tts_provider, TTSEngine
        from math_content_engine.config import TTSProvider

        print("\n" + "="*80)
        print("Testing ElevenLabs TTS Audio Generation (Fast)")
        print("="*80)

        # Set up ElevenLabs configuration
        elevenlabs_config = Config()
        elevenlabs_config.tts_provider = TTSProvider.ELEVENLABS
        elevenlabs_config.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")

        # Create TTS provider
        tts_provider = create_tts_provider(elevenlabs_config)
        print(f"\nTTS Provider: {type(tts_provider).__name__}")

        # Create TTS engine
        tts_engine = TTSEngine(provider=tts_provider)

        # Test audio generation
        test_text = "Let's solve the equation 2x plus 3 equals 7. First, subtract 3 from both sides."
        audio_path = output_dir / "test_elevenlabs_audio.mp3"

        print(f"\nGenerating audio for: '{test_text[:50]}...'")
        result_audio = tts_engine.generate(test_text, audio_path)

        print(f"\nAudio generated:")
        print(f"  Path: {result_audio}")
        print(f"  Exists: {result_audio.exists()}")
        print(f"  Size: {result_audio.stat().st_size / 1024:.1f} KB")

        # Get duration
        duration = tts_engine._get_audio_duration(result_audio)
        print(f"  Duration: {duration:.2f} seconds")

        assert result_audio.exists(), "Audio file was not created"
        assert result_audio.stat().st_size > 1000, "Audio file is too small"
        assert duration > 0, "Could not determine audio duration"

        print("\n" + "="*80)
        print("ElevenLabs TTS test PASSED!")
        print("="*80)

    @pytest.mark.slow
    @pytest.mark.skipif(
        not os.getenv("ELEVENLABS_API_KEY"),
        reason="ELEVENLABS_API_KEY not set. Set it to run ElevenLabs tests."
    )
    def test_linear_equation_with_elevenlabs_narration(self, engine, output_dir):
        """
        Test full pipeline: generate linear equation video with graphics + ElevenLabs voice.

        This test:
        1. Generates a Manim animation for solving a linear equation
        2. Creates a narration script with step-by-step explanation
        3. Adds ElevenLabs voice narration to the video
        4. Verifies the final narrated video exists and is valid
        """
        from math_content_engine.tts import (
            NarratedAnimationGenerator,
            AnimationScript,
            create_tts_provider,
        )
        from math_content_engine.config import TTSProvider

        print("\n" + "="*80)
        print("STEP 1: Generating base animation video with graphics")
        print("="*80)

        # Generate the base video with graphics representation
        result = engine.generate(
            topic="Solving the linear equation 2x + 3 = 7",
            requirements="""
            Create a clear, visual step-by-step solution:

            IMPORTANT: Use Text() instead of MathTex() to avoid LaTeX dependency.

            1. Show title "Solving Linear Equations"
            2. Display the equation: 2x + 3 = 7
            3. Use a number line or visual representation to show the equation
            4. Step 1: Show "Subtract 3 from both sides"
               - Visually remove 3 from both sides
               - Show: 2x = 4
            5. Step 2: Show "Divide both sides by 2"
               - Visually divide by 2
               - Show: x = 2
            6. Highlight the solution with a box or circle
            7. Optionally show verification by plugging x=2 back into original equation

            Use colors to make it engaging:
            - Original equation: WHITE
            - Steps: BLUE
            - Solution: GREEN
            - Highlight box: YELLOW

            Keep each step visible for ~3-4 seconds.
            Total animation should be 15-20 seconds.
            """,
            audience_level="middle school",
            output_filename="linear_equation_base"
        )

        # Save base video result
        save_test_result("elevenlabs_linear_base", result, output_dir)

        print(f"\nBase video generation:")
        print(f"  Success: {result.success}")
        print(f"  Video path: {result.video_path}")
        print(f"  Render time: {result.render_time:.2f}s")
        print(f"  Total attempts: {result.total_attempts}")

        assert result.success, f"Base video generation failed: {result.error_message}"
        assert result.video_path is not None
        assert result.video_path.exists(), f"Video file not found at {result.video_path}"

        print("\n" + "="*80)
        print("STEP 2: Creating narration script for the equation")
        print("="*80)

        # Create narration script that matches the visual steps
        script = AnimationScript("Solving 2x + 3 = 7")
        script.add_intro("Let's solve the linear equation: 2x plus 3 equals 7")
        script.add_step("First, we need to isolate the variable x", time=3.0)
        script.add_step("Subtract 3 from both sides of the equation", time=6.0)
        script.add_step("This gives us 2x equals 4", time=9.0)
        script.add_step("Now, divide both sides by 2", time=12.0)
        script.add_conclusion("Therefore, x equals 2. That's our solution!", time=15.0)

        print(f"\nNarration script created with {len(script.cues)} cues:")
        for i, cue in enumerate(script.cues):
            print(f"  {i+1}. [{cue.time}s] {cue.text}")

        print("\n" + "="*80)
        print("STEP 3: Setting up ElevenLabs TTS provider")
        print("="*80)

        # Set up ElevenLabs configuration
        elevenlabs_config = Config()
        elevenlabs_config.tts_provider = TTSProvider.ELEVENLABS
        elevenlabs_config.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")

        # Use a teacher voice suitable for educational content
        # You can customize this by setting MATH_ENGINE_TTS_VOICE env var
        # to any ElevenLabs voice ID
        if os.getenv("MATH_ENGINE_TTS_VOICE"):
            elevenlabs_config.tts_voice = os.getenv("MATH_ENGINE_TTS_VOICE")

        print(f"\nElevenLabs config:")
        print(f"  Provider: {elevenlabs_config.tts_provider.value}")
        print(f"  Voice: {elevenlabs_config.tts_voice or 'default (TEACHER_FEMALE_CALM)'}")

        # Create TTS provider
        tts_provider = create_tts_provider(elevenlabs_config)
        print(f"  Provider created: {type(tts_provider).__name__}")

        print("\n" + "="*80)
        print("STEP 4: Generating narrated video with ElevenLabs voice")
        print("="*80)

        # Create narrated animation generator with ElevenLabs
        from math_content_engine.tts import TTSEngine
        narration_gen = NarratedAnimationGenerator(config=elevenlabs_config)

        # Output path for final narrated video
        narrated_output = output_dir / "linear_equation_elevenlabs_narrated.mp4"

        # Generate narrated video
        print("\nCombining video with ElevenLabs narration...")
        narration_result = narration_gen.create_narrated_video(
            video_path=result.video_path,
            script=script,
            output_path=narrated_output
        )

        print(f"\nNarration result:")
        print(f"  Success: {narration_result.success}")
        print(f"  Video path: {narration_result.video_path}")
        if narration_result.error_message:
            print(f"  Error: {narration_result.error_message}")

        assert narration_result.success, f"Narration failed: {narration_result.error_message}"
        assert narration_result.video_path is not None
        assert narration_result.video_path.exists(), f"Narrated video not found"

        print("\n" + "="*80)
        print("STEP 5: Verifying final output")
        print("="*80)

        # Verify the video file has reasonable size
        video_size = narrated_output.stat().st_size
        print(f"\nFinal video stats:")
        print(f"  Path: {narrated_output}")
        print(f"  Size: {video_size / 1024:.1f} KB")
        print(f"  Exists: {narrated_output.exists()}")

        assert video_size > 1000, "Video file is too small, likely corrupted"

        # Save metadata about the test
        meta_file = output_dir / "elevenlabs_linear_narrated_meta.txt"
        meta_content = f"""Test: Linear Equation with ElevenLabs Narration
Timestamp: {datetime.now().isoformat()}

Base Video Generation:
  Success: {result.success}
  Video Path: {result.video_path}
  Scene Name: {result.scene_name}
  Render Time: {result.render_time:.2f}s
  Total Attempts: {result.total_attempts}

Narration:
  Provider: ElevenLabs
  Script Cues: {len(script.cues)}
  Success: {narration_result.success}

Final Output:
  Path: {narrated_output}
  Size: {video_size / 1024:.1f} KB

Narration Script:
"""
        for i, cue in enumerate(script.cues):
            meta_content += f"  {i+1}. [{cue.time}s] {cue.text}\n"

        meta_file.write_text(meta_content)

        print("\n" + "="*80)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("="*80)
        print(f"\nOutput files saved to: {output_dir}")
        print(f"  - Base animation code: elevenlabs_linear_base.py")
        print(f"  - Base animation metadata: elevenlabs_linear_base_meta.txt")
        print(f"  - Final narrated video: {narrated_output.name}")
        print(f"  - Test metadata: {meta_file.name}")
        print("\nYou can play the video to verify it has both graphics and voice narration!")


class TestAlgebraCodeValidation:
    """Tests for validating generated algebra code without rendering."""

    @pytest.fixture
    def engine(self):
        """Create engine for code validation."""
        return MathContentEngine()

    @pytest.fixture
    def output_dir(self):
        """Return the persistent output directory for test results."""
        TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        return TEST_OUTPUT_DIR

    def test_multiple_topics_code_generation(self, engine, output_dir):
        """Test code generation for multiple algebra topics."""
        topics = [
            ("Adding fractions: show 1/2 + 1/3 = 5/6 using Text objects", "elementary"),
            ("Distributive property: show a(b+c) = ab + ac using Text", "middle school"),
            ("Factoring: show x² - 9 = (x+3)(x-3) using Text objects", "high school"),
        ]

        results = []
        for i, (topic, level) in enumerate(topics):
            result = engine.preview_code(
                topic=topic,
                requirements="Use Text() instead of MathTex() to avoid LaTeX dependency.",
                audience_level=level
            )

            # Save each result
            save_test_result(f"topic_{i+1}_{level.replace(' ', '_')}", result, output_dir)

            results.append({
                "topic": topic,
                "valid": result.validation.is_valid,
                "errors": result.validation.errors,
                "scene": result.scene_name,
            })
            print(f"\n{topic}: {'✓' if result.validation.is_valid else '✗'}")
            if not result.validation.is_valid:
                print(f"  Errors: {result.validation.errors}")

        print(f"\nAll code saved to: {output_dir}")

        # At least 2 out of 3 should be valid
        valid_count = sum(1 for r in results if r["valid"])
        assert valid_count >= 2, f"Only {valid_count}/3 topics generated valid code"


# Register custom markers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (renders actual videos)"
    )
