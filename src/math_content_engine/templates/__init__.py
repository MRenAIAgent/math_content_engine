"""
Parameterized Manim template system for personalized math videos.

This module provides a template-based approach to generating math animations:
1. Templates define reusable Manim code with parameters
2. QuestionParser extracts parameters from math questions
3. TemplateEngine orchestrates the generation pipeline

Usage:
    from math_content_engine.templates import TemplateEngine

    engine = TemplateEngine()
    result = engine.generate_from_question(
        question="Solve 3x + 5 = 14",
        output_filename="my_problem"
    )
"""

from .base import ManimTemplate, ParamSpec, TemplateCategory, ParseResult
from .registry import TemplateRegistry, get_registry
from .question_parser import QuestionParserAgent
from .renderer import TemplateRenderer
from .engine import TemplateEngine

__all__ = [
    "ManimTemplate",
    "ParamSpec",
    "TemplateCategory",
    "ParseResult",
    "TemplateRegistry",
    "get_registry",
    "QuestionParserAgent",
    "TemplateRenderer",
    "TemplateEngine",
]
