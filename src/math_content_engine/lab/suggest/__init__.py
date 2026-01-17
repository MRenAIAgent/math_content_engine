"""Suggestion engine for prompt modifications."""

from .engine import SuggestionEngine
from .patterns import CHANGE_PATTERNS

__all__ = ["SuggestionEngine", "CHANGE_PATTERNS"]
