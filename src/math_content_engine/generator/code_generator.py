"""
Manim code generator using LLM.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from ..llm.base import BaseLLMClient
from ..utils.code_extractor import extract_python_code
from ..utils.validators import validate_manim_code, ValidationResult
from .prompts import AnimationStyle, get_system_prompt, build_generation_prompt
from ..personalization import ContentPersonalizer, StudentProfile, get_interest_profile

logger = logging.getLogger(__name__)


# Common Manim pitfalls included in error-recovery prompts so the LLM
# can diagnose the root cause faster instead of rewriting from scratch.
_COMMON_MANIM_PITFALLS = """
Common Manim pitfalls (check if any apply):
- `ShowCreation` is deprecated → use `Create`
- `axes.get_axis_labels()` uses LaTeX and can fail → create labels manually with `Text()`
- Animating the same Mobject in two parallel animations causes conflicts
- Using `NumberPlane` when `NumberLine` was intended (or vice versa)
- Forgetting `self.wait()` at the end so the last frame disappears
- Using `r"\\\\frac{a}{b}"` (double-escaped) in a raw string — should be `r"\\frac{a}{b}"`
- Referencing a Mobject that was already removed via `FadeOut`
- Passing a Python list where a VGroup is expected
"""


@dataclass
class GenerationResult:
    """Result of code generation."""
    code: str
    scene_name: str
    validation: ValidationResult
    attempts: int
    raw_response: str


class ManimCodeGenerator:
    """
    Generates Manim animation code from text descriptions using LLM.
    """

    def __init__(
        self,
        llm_client: BaseLLMClient,
        max_retries: int = 5,
        animation_style: Optional[AnimationStyle] = None,
        interest: Optional[str] = None
    ):
        """
        Initialize the code generator.

        Args:
            llm_client: LLM client for code generation
            max_retries: Maximum retry attempts for failed generations
            animation_style: Visual style preset for animations
            interest: Student interest for content personalization (e.g., "basketball", "gaming")
        """
        self.llm_client = llm_client
        self.max_retries = max_retries
        self.animation_style = animation_style or AnimationStyle.DARK
        self.system_prompt = get_system_prompt(self.animation_style)

        # Initialize personalization if interest is provided
        self.personalizer: Optional[ContentPersonalizer] = None
        if interest:
            self.personalizer = ContentPersonalizer(interest)
            if self.personalizer.profile:
                logger.info(f"Content personalization enabled: {self.personalizer.profile.display_name}")

    def set_interest(self, interest: str) -> bool:
        """
        Set or change the personalization interest.

        Args:
            interest: Interest name (e.g., "basketball", "gaming", "music")

        Returns:
            True if interest was valid and set, False otherwise
        """
        profile = get_interest_profile(interest)
        if profile:
            self.personalizer = ContentPersonalizer(interest)
            logger.info(f"Content personalization set to: {profile.display_name}")
            return True
        else:
            logger.warning(f"Unknown interest: {interest}")
            return False

    def generate(
        self,
        topic: str,
        requirements: str = "",
        audience_level: str = "high school",
        interest: Optional[str] = None,
        student_profile: Optional[StudentProfile] = None,
    ) -> GenerationResult:
        """
        Generate Manim code for a given topic.

        Args:
            topic: Math topic to animate
            requirements: Additional requirements
            audience_level: Target audience level
            interest: Optional interest override for personalization
            student_profile: Optional student profile for individual personalization

        Returns:
            GenerationResult with generated code and metadata
        """
        # Build animation personalization context with engagement data
        personalization_context = ""
        if interest:
            temp_personalizer = ContentPersonalizer(interest)
            if temp_personalizer.profile:
                personalization_context = temp_personalizer.get_animation_personalization(
                    topic, student=student_profile
                )
                logger.info(f"Using personalization: {temp_personalizer.profile.display_name}")
        elif self.personalizer and self.personalizer.profile:
            personalization_context = self.personalizer.get_animation_personalization(
                topic, student=student_profile
            )

        student_name = student_profile.name if student_profile else None
        student_address = student_profile.get_display_address() if student_profile else None
        # Don't pass "you" as an explicit address — only pass actual names/nicknames
        if student_address == "you":
            student_address = None
        prompt = build_generation_prompt(
            topic, requirements, audience_level, personalization_context,
            student_name=student_name,
            student_address=student_address,
        )

        interest_info = ""
        if personalization_context:
            interest_info = ", personalized"
        logger.info(f"Generating Manim code for topic: {topic} (style: {self.animation_style.value}{interest_info})")

        # Initial generation
        response = self.llm_client.generate(prompt, self.system_prompt)
        code = extract_python_code(response.content)
        validation = validate_manim_code(code)
        attempt = 1

        # Retry loop for invalid code
        while not validation.is_valid and attempt < self.max_retries:
            attempt += 1
            logger.warning(
                f"Validation failed (attempt {attempt-1}/{self.max_retries}): {validation.errors}"
            )

            error_context = self._build_error_context(code, validation)
            response = self.llm_client.generate_with_retry(
                prompt, self.system_prompt, error_context
            )
            code = extract_python_code(response.content)
            validation = validate_manim_code(code)

        if not validation.is_valid:
            logger.error(f"Failed to generate valid code after {self.max_retries} attempts")

        scene_name = self._extract_scene_name(code)

        return GenerationResult(
            code=code,
            scene_name=scene_name,
            validation=validation,
            attempts=attempt,
            raw_response=response.content,
        )

    def fix_code(self, code: str, error_message: str) -> GenerationResult:
        """
        Fix existing code that failed during rendering.

        Uses a structured diagnosis approach so the LLM identifies the root
        cause before attempting a minimal fix (rather than rewriting the
        whole scene from scratch).

        Args:
            code: The code that failed
            error_message: Error message from Manim

        Returns:
            GenerationResult with fixed code
        """
        fix_prompt = f"""The following Manim code failed with an error. Fix it using a MINIMAL change.

## FAILED CODE
```python
{code}
```

## ERROR MESSAGE
{error_message}

## DIAGNOSIS INSTRUCTIONS
1. Identify the exact line(s) causing the error
2. Determine the root cause (wrong API, missing import, type error, etc.)
3. Apply the smallest possible fix — do NOT rewrite the entire scene
4. Preserve all working animations and visual structure

{_COMMON_MANIM_PITFALLS}

Return ONLY the corrected Python code. Keep everything that was already working."""

        response = self.llm_client.generate(fix_prompt, self.system_prompt)
        fixed_code = extract_python_code(response.content)
        validation = validate_manim_code(fixed_code)
        scene_name = self._extract_scene_name(fixed_code)

        return GenerationResult(
            code=fixed_code,
            scene_name=scene_name,
            validation=validation,
            attempts=1,
            raw_response=response.content,
        )

    def _extract_scene_name(self, code: str) -> str:
        """Extract the Scene class name from code."""
        import re
        match = re.search(r'class\s+(\w+)\s*\(\s*Scene\s*\)', code)
        if match:
            return match.group(1)
        return "GeneratedScene"

    def _build_error_context(self, code: str, validation: ValidationResult) -> str:
        """Build error context for retry prompt with structured diagnosis."""
        errors = "\n".join(f"- {e}" for e in validation.errors)
        warnings = "\n".join(f"- {w}" for w in validation.warnings) if validation.warnings else "None"

        return f"""The previous code had validation errors. Fix them with MINIMAL changes.

CODE:
```python
{code}
```

ERRORS:
{errors}

WARNINGS:
{warnings}

{_COMMON_MANIM_PITFALLS}

Apply the smallest fix that resolves each error. Do NOT rewrite unrelated parts."""
