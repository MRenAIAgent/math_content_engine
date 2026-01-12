"""
Main Math Content Engine - orchestrates LLM generation and Manim rendering.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .config import Config, AnimationStyle
from .generator.code_generator import ManimCodeGenerator, GenerationResult
from .generator.prompts import AnimationStyle as PromptAnimationStyle
from .llm.factory import create_llm_client
from .renderer.manim_renderer import ManimRenderer, RenderResult
from .personalization import ContentPersonalizer, list_available_interests

logger = logging.getLogger(__name__)


@dataclass
class AnimationResult:
    """Complete result of animation generation."""
    success: bool
    video_path: Optional[Path]
    code: str
    scene_name: str
    generation_attempts: int
    render_attempts: int
    total_attempts: int
    error_message: Optional[str] = None
    render_time: float = 0.0


class MathContentEngine:
    """
    Main engine for generating math animations from text descriptions.

    This class orchestrates the entire pipeline:
    1. Generate Manim code from topic description using LLM
    2. Validate the generated code
    3. Render the animation using Manim
    4. Handle errors with automatic retry and code fixes

    Example:
        >>> from math_content_engine import MathContentEngine, Config
        >>> config = Config()
        >>> engine = MathContentEngine(config)
        >>> result = engine.generate("Pythagorean theorem proof")
        >>> if result.success:
        ...     print(f"Video saved to: {result.video_path}")
    """

    def __init__(self, config: Optional[Config] = None, interest: Optional[str] = None):
        """
        Initialize the Math Content Engine.

        Args:
            config: Configuration object. If None, loads from environment.
            interest: Student interest for content personalization (e.g., "basketball", "gaming")
        """
        self.config = config or Config.from_env()
        self.interest = interest

        # Initialize components
        self.llm_client = create_llm_client(self.config)

        # Map config AnimationStyle to prompt AnimationStyle
        prompt_style = PromptAnimationStyle(self.config.animation_style.value)

        self.code_generator = ManimCodeGenerator(
            self.llm_client,
            max_retries=self.config.max_retries,
            animation_style=prompt_style,
            interest=interest,
        )
        self.renderer = ManimRenderer(
            output_dir=self.config.output_dir,
            cache_dir=self.config.manim_cache_dir,
            quality=self.config.video_quality,
            output_format=self.config.output_format,
        )

        interest_info = ""
        if interest:
            interest_info = f", interest={interest}"
        logger.info(
            f"MathContentEngine initialized with provider={self.config.llm_provider.value}, "
            f"model={self.config.get_model()}, style={self.config.animation_style.value}{interest_info}"
        )

    def set_interest(self, interest: str) -> bool:
        """
        Set or change the personalization interest.

        Args:
            interest: Interest name (e.g., "basketball", "gaming", "music")

        Returns:
            True if interest was valid and set, False otherwise
        """
        if self.code_generator.set_interest(interest):
            self.interest = interest
            return True
        return False

    @staticmethod
    def get_available_interests() -> list:
        """Get list of available interests for personalization."""
        return list_available_interests()

    def generate(
        self,
        topic: str,
        requirements: str = "",
        audience_level: str = "high school",
        output_filename: Optional[str] = None,
        interest: Optional[str] = None,
    ) -> AnimationResult:
        """
        Generate a math animation from a topic description.

        Args:
            topic: Math topic to animate (e.g., "Pythagorean theorem")
            requirements: Additional requirements or customizations
            audience_level: Target audience (elementary, middle school, high school, college)
            output_filename: Optional custom filename for output
            interest: Optional interest override for personalization (e.g., "basketball")

        Returns:
            AnimationResult with success status, video path, and metadata
        """
        interest_info = f" (personalized for {interest})" if interest else ""
        logger.info(f"Generating animation for topic: {topic}{interest_info}")

        total_attempts = 0
        render_attempts = 0
        last_generation: Optional[GenerationResult] = None
        last_render: Optional[RenderResult] = None

        # Generate initial code
        generation_result = self.code_generator.generate(
            topic=topic,
            requirements=requirements,
            audience_level=audience_level,
            interest=interest,
        )
        total_attempts = generation_result.attempts
        last_generation = generation_result

        if not generation_result.validation.is_valid:
            return AnimationResult(
                success=False,
                video_path=None,
                code=generation_result.code,
                scene_name=generation_result.scene_name,
                generation_attempts=generation_result.attempts,
                render_attempts=0,
                total_attempts=total_attempts,
                error_message=f"Code generation failed: {generation_result.validation.errors}",
            )

        # Try to render with error feedback loop
        code = generation_result.code
        scene_name = generation_result.scene_name

        while render_attempts < self.config.max_retries:
            render_attempts += 1
            total_attempts += 1

            logger.info(f"Render attempt {render_attempts}/{self.config.max_retries}")

            render_result = self.renderer.render(
                code=code,
                scene_name=scene_name,
                output_filename=output_filename,
            )
            last_render = render_result

            if render_result.success:
                logger.info(f"Animation rendered successfully: {render_result.output_path}")
                return AnimationResult(
                    success=True,
                    video_path=render_result.output_path,
                    code=code,
                    scene_name=scene_name,
                    generation_attempts=last_generation.attempts,
                    render_attempts=render_attempts,
                    total_attempts=total_attempts,
                    render_time=render_result.render_time,
                )

            # Render failed - try to fix the code
            logger.warning(f"Render failed: {render_result.error_message}")

            if render_attempts >= self.config.max_retries:
                break

            # Use LLM to fix the code
            fix_result = self.code_generator.fix_code(
                code=code,
                error_message=render_result.error_message,
            )

            if fix_result.validation.is_valid:
                code = fix_result.code
                scene_name = fix_result.scene_name
                logger.info("Code fixed by LLM, retrying render...")
            else:
                logger.warning("LLM code fix did not produce valid code")

        # All attempts failed
        error_msg = last_render.error_message if last_render else "Unknown error"
        return AnimationResult(
            success=False,
            video_path=None,
            code=code,
            scene_name=scene_name,
            generation_attempts=last_generation.attempts,
            render_attempts=render_attempts,
            total_attempts=total_attempts,
            error_message=f"Rendering failed after {render_attempts} attempts: {error_msg}",
        )

    def generate_from_code(
        self,
        code: str,
        scene_name: Optional[str] = None,
        output_filename: Optional[str] = None,
    ) -> AnimationResult:
        """
        Render animation from existing Manim code.

        Args:
            code: Manim Python code
            scene_name: Scene class name (auto-detected if not provided)
            output_filename: Optional custom filename

        Returns:
            AnimationResult with rendering status
        """
        from .utils.code_extractor import extract_class_name
        from .utils.validators import validate_manim_code

        # Validate code
        validation = validate_manim_code(code)
        if not validation.is_valid:
            return AnimationResult(
                success=False,
                video_path=None,
                code=code,
                scene_name=scene_name or "Unknown",
                generation_attempts=0,
                render_attempts=0,
                total_attempts=0,
                error_message=f"Invalid code: {validation.errors}",
            )

        # Extract scene name if not provided
        if not scene_name:
            scene_name = extract_class_name(code) or "GeneratedScene"

        # Render
        render_result = self.renderer.render(
            code=code,
            scene_name=scene_name,
            output_filename=output_filename,
        )

        return AnimationResult(
            success=render_result.success,
            video_path=render_result.output_path,
            code=code,
            scene_name=scene_name,
            generation_attempts=0,
            render_attempts=1,
            total_attempts=1,
            error_message=render_result.error_message,
            render_time=render_result.render_time,
        )

    def preview_code(
        self,
        topic: str,
        requirements: str = "",
        audience_level: str = "high school",
        interest: Optional[str] = None,
    ) -> GenerationResult:
        """
        Generate code without rendering - useful for previewing/editing.

        Args:
            topic: Math topic
            requirements: Additional requirements
            audience_level: Target audience
            interest: Optional interest for personalization

        Returns:
            GenerationResult with code and validation status
        """
        return self.code_generator.generate(
            topic=topic,
            requirements=requirements,
            audience_level=audience_level,
            interest=interest,
        )

    def cleanup(self):
        """Clean up temporary files and cache."""
        self.renderer.cleanup_cache()
        logger.info("Cache cleaned up")
