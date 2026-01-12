"""
Utility functions for extracting code from LLM responses.
"""

import re
from typing import Optional


def extract_python_code(text: str) -> str:
    """
    Extract Python code from LLM response text.

    Handles various formats:
    - Code in ```python ... ``` blocks
    - Code in ``` ... ``` blocks
    - Raw code without markers

    Args:
        text: Raw text from LLM response

    Returns:
        Extracted Python code
    """
    # Try to find code in ```python ... ``` blocks
    python_pattern = r'```python\s*(.*?)\s*```'
    matches = re.findall(python_pattern, text, re.DOTALL)
    if matches:
        return matches[0].strip()

    # Try to find code in ``` ... ``` blocks
    generic_pattern = r'```\s*(.*?)\s*```'
    matches = re.findall(generic_pattern, text, re.DOTALL)
    if matches:
        # Return the first match that looks like Python (has 'from manim' or 'class')
        for match in matches:
            if 'from manim' in match or 'class' in match:
                return match.strip()
        # If no obvious Python, return first match
        return matches[0].strip()

    # If no code blocks, check if the whole text is code
    if 'from manim import' in text and 'class' in text:
        return text.strip()

    # Return original text as fallback
    return text.strip()


def extract_class_name(code: str) -> Optional[str]:
    """
    Extract the main Scene class name from Manim code.

    Args:
        code: Python code string

    Returns:
        Class name or None if not found
    """
    pattern = r'class\s+(\w+)\s*\(\s*(?:Scene|ThreeDScene|MovingCameraScene)\s*\)'
    match = re.search(pattern, code)
    return match.group(1) if match else None


def extract_imports(code: str) -> list[str]:
    """
    Extract import statements from code.

    Args:
        code: Python code string

    Returns:
        List of import lines
    """
    import_pattern = r'^(?:from|import)\s+.+$'
    return re.findall(import_pattern, code, re.MULTILINE)
