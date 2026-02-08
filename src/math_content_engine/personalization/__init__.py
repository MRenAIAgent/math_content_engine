"""
Personalization module for adapting math content to student interests.

This module enables generating math content that uses contexts, examples,
and terminology from various interests like sports, music, gaming, etc.
"""

from .interests import (
    InterestProfile,
    get_interest_profile,
    list_available_interests,
    INTEREST_PROFILES,
)
from .personalizer import ContentPersonalizer
from .student_profile import StudentProfile
from .engagement_profile import (
    EngagementProfile,
    build_engagement_profile,
    create_engagement_profile,
    has_student,
)
from .engagement_store import EngagementStore, make_store_key
from .textbook_parser import (
    TextbookParser,
    TextbookChapter,
    TextbookSection,
    MathExample,
    parse_textbook,
    get_animation_specs_from_textbook,
)
from .pdf_parser import (
    MathpixPDFParser,
    MathpixConfig,
    parse_textbook_pdf,
)

__all__ = [
    "InterestProfile",
    "get_interest_profile",
    "list_available_interests",
    "ContentPersonalizer",
    "StudentProfile",
    "EngagementProfile",
    "build_engagement_profile",
    "create_engagement_profile",
    "has_student",
    "EngagementStore",
    "make_store_key",
    "INTEREST_PROFILES",
    # Textbook parsing
    "TextbookParser",
    "TextbookChapter",
    "TextbookSection",
    "MathExample",
    "parse_textbook",
    "get_animation_specs_from_textbook",
    # PDF parsing
    "MathpixPDFParser",
    "MathpixConfig",
    "parse_textbook_pdf",
]
