"""
Main Math Content Engine - orchestrates LLM generation and Manim rendering.
"""

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from .config import Config, AnimationStyle
from .generator.code_generator import ManimCodeGenerator, GenerationResult
from .generator.prompts import AnimationStyle as PromptAnimationStyle
from .llm.factory import create_llm_client
from .renderer.manim_renderer import ManimRenderer, RenderResult
from .personalization import ContentPersonalizer, StudentProfile, list_available_interests

if TYPE_CHECKING:
    from .api.storage import VideoStorage

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
    video_id: Optional[str] = None  # ID assigned when stored in database


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

    def __init__(
        self,
        config: Optional[Config] = None,
        interest: Optional[str] = None,
        storage: Optional["VideoStorage"] = None,
    ):
        """
        Initialize the Math Content Engine.

        Args:
            config: Configuration object. If None, loads from environment.
            interest: Student interest for content personalization (e.g., "basketball", "gaming")
            storage: Optional VideoStorage instance for persisting video metadata
        """
        self.config = config or Config.from_env()
        self.interest = interest
        self.storage = storage

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
        student_profile: Optional[StudentProfile] = None,
        save_to_storage: bool = True,
        concept_ids: Optional[list] = None,
        grade: Optional[str] = None,
    ) -> AnimationResult:
        """
        Generate a math animation from a topic description.

        Args:
            topic: Math topic to animate (e.g., "Pythagorean theorem")
            requirements: Additional requirements or customizations
            audience_level: Target audience (elementary, middle school, high school, college)
            output_filename: Optional custom filename for output
            interest: Optional interest override for personalization (e.g., "basketball")
            student_profile: Optional student profile for individual personalization
            save_to_storage: Whether to save video metadata to storage (if storage is configured)
            concept_ids: Optional list of concept IDs this video covers (e.g., ["AT-24"])
            grade: Optional grade level (e.g., "grade_8")

        Returns:
            AnimationResult with success status, video path, and metadata
        """
        start_time = time.time()
        interest_info = f" (personalized for {interest})" if interest else ""
        if student_profile and student_profile.name:
            interest_info += f", student={student_profile.name}"
        logger.info(f"Generating animation for topic: {topic}{interest_info}")

        total_attempts = 0
        render_attempts = 0
        last_generation: Optional[GenerationResult] = None
        last_render: Optional[RenderResult] = None

        # Track generation timing
        gen_start = time.time()

        # Generate initial code
        generation_result = self.code_generator.generate(
            topic=topic,
            requirements=requirements,
            audience_level=audience_level,
            interest=interest,
            student_profile=student_profile,
        )
        total_attempts = generation_result.attempts
        last_generation = generation_result
        generation_time_ms = int((time.time() - gen_start) * 1000)

        if not generation_result.validation.is_valid:
            result = AnimationResult(
                success=False,
                video_path=None,
                code=generation_result.code,
                scene_name=generation_result.scene_name,
                generation_attempts=generation_result.attempts,
                render_attempts=0,
                total_attempts=total_attempts,
                error_message=f"Code generation failed: {generation_result.validation.errors}",
            )
            # Save failed generation to storage if configured
            if save_to_storage and self.storage:
                result = self._save_to_storage(
                    result, topic, requirements, audience_level, interest,
                    generation_time_ms, None,
                    concept_ids=concept_ids, grade=grade,
                )
            return result

        # Try to render with error feedback loop
        code = generation_result.code
        scene_name = generation_result.scene_name
        render_start = time.time()

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
                render_time_ms = int((time.time() - render_start) * 1000)
                logger.info(f"Animation rendered successfully: {render_result.output_path}")
                result = AnimationResult(
                    success=True,
                    video_path=render_result.output_path,
                    code=code,
                    scene_name=scene_name,
                    generation_attempts=last_generation.attempts,
                    render_attempts=render_attempts,
                    total_attempts=total_attempts,
                    render_time=render_result.render_time,
                )
                # Save successful generation to storage if configured
                if save_to_storage and self.storage:
                    result = self._save_to_storage(
                        result, topic, requirements, audience_level, interest,
                        generation_time_ms, render_time_ms,
                        concept_ids=concept_ids, grade=grade,
                    )
                return result

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
        render_time_ms = int((time.time() - render_start) * 1000)
        error_msg = last_render.error_message if last_render else "Unknown error"
        result = AnimationResult(
            success=False,
            video_path=None,
            code=code,
            scene_name=scene_name,
            generation_attempts=last_generation.attempts,
            render_attempts=render_attempts,
            total_attempts=total_attempts,
            error_message=f"Rendering failed after {render_attempts} attempts: {error_msg}",
        )
        # Save failed generation to storage if configured
        if save_to_storage and self.storage:
            result = self._save_to_storage(
                result, topic, requirements, audience_level, interest,
                generation_time_ms, render_time_ms,
                concept_ids=concept_ids, grade=grade,
            )
        return result

    def _save_to_storage(
        self,
        result: AnimationResult,
        topic: str,
        requirements: str,
        audience_level: str,
        interest: Optional[str],
        generation_time_ms: int,
        render_time_ms: Optional[int],
        concept_ids: Optional[list] = None,
        grade: Optional[str] = None,
    ) -> AnimationResult:
        """Save video metadata to storage and return updated result with video_id."""
        if not self.storage:
            return result

        try:
            from .api.models import VideoCreate, AnimationStyle as ApiAnimationStyle, VideoQuality

            # Get file size if video exists
            file_size_bytes = None
            if result.video_path and result.video_path.exists():
                file_size_bytes = result.video_path.stat().st_size

            video_create = VideoCreate(
                topic=topic,
                scene_name=result.scene_name,
                video_path=str(result.video_path) if result.video_path else "",
                code=result.code,
                concept_ids=concept_ids or [],
                grade=grade,
                requirements=requirements if requirements else None,
                audience_level=audience_level,
                interest=interest or self.interest,
                style=ApiAnimationStyle(self.config.animation_style.value),
                quality=VideoQuality(self.config.video_quality.value),
                llm_provider=self.config.llm_provider.value,
                llm_model=self.config.get_model(),
                generation_attempts=result.generation_attempts,
                render_attempts=result.render_attempts,
                total_attempts=result.total_attempts,
                generation_time_ms=generation_time_ms,
                render_time_ms=render_time_ms,
                file_size_bytes=file_size_bytes,
                success=result.success,
                error_message=result.error_message,
            )

            metadata = self.storage.save(video_create)
            result.video_id = metadata.id
            logger.info(f"Saved video metadata with ID: {metadata.id}")
        except Exception as e:
            logger.warning(f"Failed to save video metadata: {e}")

        return result

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
        student_profile: Optional[StudentProfile] = None,
    ) -> GenerationResult:
        """
        Generate code without rendering - useful for previewing/editing.

        Args:
            topic: Math topic
            requirements: Additional requirements
            audience_level: Target audience
            interest: Optional interest for personalization
            student_profile: Optional student profile for individual personalization

        Returns:
            GenerationResult with code and validation status
        """
        return self.code_generator.generate(
            topic=topic,
            requirements=requirements,
            audience_level=audience_level,
            interest=interest,
            student_profile=student_profile,
        )

    def cleanup(self):
        """Clean up temporary files and cache."""
        self.renderer.cleanup_cache()
        logger.info("Cache cleaned up")
