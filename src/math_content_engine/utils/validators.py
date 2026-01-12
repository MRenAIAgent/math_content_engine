"""
Validation utilities for Manim code.
"""

import ast
import re
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """Result of code validation."""
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_manim_code(code: str) -> ValidationResult:
    """
    Validate Manim code for common issues.

    Checks:
    - Valid Python syntax
    - Contains manim import
    - Has a Scene class
    - Has construct method
    - Uses self.play() calls

    Args:
        code: Python code string

    Returns:
        ValidationResult with errors and warnings
    """
    errors = []
    warnings = []

    # Check for empty code
    if not code or not code.strip():
        return ValidationResult(
            is_valid=False,
            errors=["Empty code provided"]
        )

    # Check Python syntax
    try:
        ast.parse(code)
    except SyntaxError as e:
        return ValidationResult(
            is_valid=False,
            errors=[f"Syntax error at line {e.lineno}: {e.msg}"]
        )

    # Check for manim import
    if 'from manim import' not in code and 'import manim' not in code:
        errors.append("Missing manim import statement")

    # Check for Scene class
    scene_pattern = r'class\s+\w+\s*\(\s*(?:Scene|ThreeDScene|MovingCameraScene)\s*\)'
    if not re.search(scene_pattern, code):
        errors.append("No Scene class found (must inherit from Scene, ThreeDScene, or MovingCameraScene)")

    # Check for construct method
    if 'def construct(self)' not in code:
        errors.append("Missing construct(self) method")

    # Check for self.play() calls
    if 'self.play(' not in code:
        warnings.append("No self.play() calls found - animation may be static")

    # Check for common issues
    if 'self.wait()' not in code and 'self.wait(' not in code:
        warnings.append("No self.wait() calls - consider adding pauses between animations")

    # Check for potentially problematic patterns
    if 'input(' in code:
        errors.append("Code contains input() which will hang rendering")

    if 'plt.show()' in code:
        warnings.append("Code contains plt.show() which may interfere with rendering")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def validate_scene_name(name: str) -> bool:
    """
    Validate that a scene name is a valid Python identifier.

    Args:
        name: Scene class name

    Returns:
        True if valid
    """
    return bool(re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', name))
