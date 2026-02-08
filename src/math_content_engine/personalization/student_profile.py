"""
Student profile for individual-level personalization.

Captures optional details about a specific student so the system can
address them by name and reference their particular favorites.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class StudentProfile:
    """Optional student context for deeper personalization.

    All fields are optional.  When provided, the system addresses the
    student by name (or preferred nickname) and uses their specific
    interests (e.g. favorite player, team) to make content more relatable.

    Example::

        profile = StudentProfile(
            name="Jordan",
            preferred_address="J",        # "Hey J, let's figure this out!"
            grade_level="8th grade",
            favorite_figure="Stephen Curry",
            favorite_team="Warriors",
        )
    """

    name: Optional[str] = None              # "Jordan"
    preferred_address: Optional[str] = None  # "J", "champ", "bro" — how they prefer to be called
    grade_level: Optional[str] = None       # "8th grade"
    favorite_figure: Optional[str] = None   # "Stephen Curry"
    favorite_team: Optional[str] = None     # "Warriors"
    personal_context: Optional[str] = None  # Free-text custom context

    def get_display_address(self) -> str:
        """Return the best way to address this student.

        Priority: preferred_address → name → "you"

        Returns:
            String to use when addressing the student.
        """
        return self.preferred_address or self.name or "you"
