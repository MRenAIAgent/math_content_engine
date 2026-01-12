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
from ..personalization import ContentPersonalizer, get_interest_profile

logger = logging.getLogger(__name__)


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
        interest: Optional[str] = None
    ) -> GenerationResult:
        """
        Generate Manim code for a given topic.

        Args:
            topic: Math topic to animate
            requirements: Additional requirements
            audience_level: Target audience level
            interest: Optional interest override for personalization

        Returns:
            GenerationResult with generated code and metadata
        """
        # Apply personalization if available
        personalization_context = ""
        if interest:
            # Use one-time interest override
            temp_personalizer = ContentPersonalizer(interest)
            if temp_personalizer.profile:
                personalized = temp_personalizer.personalize_prompt(topic, requirements)
                personalization_context = personalized.personalization_prompt
                logger.info(f"Using personalization: {temp_personalizer.profile.display_name}")
        elif self.personalizer and self.personalizer.profile:
            # Use default personalizer
            personalized = self.personalizer.personalize_prompt(topic, requirements)
            personalization_context = personalized.personalization_prompt

        prompt = build_generation_prompt(
            topic, requirements, audience_level, personalization_context
        )

        interest_info = ""
        if personalization_context:
            interest_info = f", personalized"
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

        Args:
            code: The code that failed
            error_message: Error message from Manim

        Returns:
            GenerationResult with fixed code
        """
        fix_prompt = f"""The following Manim code failed with an error. Please fix it:

```python
{code}
```

ERROR:
{error_message}

Return ONLY the corrected Python code."""

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
        """Build error context for retry prompt."""
        errors = "\n".join(f"- {e}" for e in validation.errors)
        warnings = "\n".join(f"- {w}" for w in validation.warnings) if validation.warnings else "None"

        return f"""CODE:
```python
{code}
```

ERRORS:
{errors}

WARNINGS:
{warnings}"""
