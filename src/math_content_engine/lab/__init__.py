"""Animation Prompt Engineering Lab.

A tool for iteratively designing math animations through prompt engineering.
"""

from .prompt.models import AnimationPrompt, GenerationResult, PromptSession
from .session.manager import SessionManager

__all__ = [
    "AnimationPrompt",
    "GenerationResult",
    "PromptSession",
    "SessionManager",
]
