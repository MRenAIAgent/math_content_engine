"""
Engagement profile — merges interest data with student context.

The engagement profile is a **computed** object: it takes a static
InterestProfile (curated per-domain data) and an optional StudentProfile
(individual preferences) and produces a personalized engagement bundle.

No LLM call is needed — this uses template-based personalization to
combine the best of both sources.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .interests import InterestProfile
from .student_profile import StudentProfile


@dataclass(frozen=True)
class EngagementProfile:
    """Personalized engagement data ready to inject into prompts.

    Attributes:
        address: How to call the student ("Jordan", "J", "champ", or "you")
        student_name: The student's actual name (may differ from address)
        scenarios: 2nd-person scenarios personalized to the student
        hooks: Interactive engagement hooks / challenge questions
        stats: Verified real-world statistics (factual, from interest profile)
        trending: Current/trending references from the domain
        current_season: Time-anchor string (e.g. "2024-25 NBA Season")
        favorite_label: Formatted label for the student's favorite figure
        figures: List of domain figures (with favorite highlighted)
        color_palette: Suggested color palette string
    """

    address: str = "you"
    student_name: Optional[str] = None
    scenarios: List[str] = field(default_factory=list)
    hooks: List[str] = field(default_factory=list)
    stats: Dict[str, str] = field(default_factory=dict)
    trending: List[str] = field(default_factory=list)
    current_season: str = ""
    favorite_label: Optional[str] = None
    figures: List[str] = field(default_factory=list)
    color_palette: str = "thematic colors"

    @property
    def has_student(self) -> bool:
        """Whether this profile has individual student data."""
        return self.address != "you" or self.student_name is not None


def build_engagement_profile(
    interest_profile: InterestProfile,
    student: Optional[StudentProfile] = None,
) -> EngagementProfile:
    """Build a personalized engagement profile from interest + student data.

    Merges curated per-domain engagement data (scenarios, hooks, stats,
    trending) with the individual student's preferences (name, preferred
    address, favorite figure/team).

    No LLM call needed — uses template-based personalization.

    Args:
        interest_profile: The domain interest profile (e.g. basketball).
        student: Optional individual student context.

    Returns:
        A fully-populated EngagementProfile ready for prompt injection.
    """
    # --- 1. Resolve address ---
    address = "you"
    student_name: Optional[str] = None
    if student:
        address = student.get_display_address()
        student_name = student.name

    # --- 2. Build scenarios (personalized with student's favorite) ---
    base_scenarios = (
        list(interest_profile.second_person_scenarios)
        if interest_profile.second_person_scenarios
        else list(interest_profile.example_scenarios)
    )

    # If student has a favorite figure, prepend a custom scenario
    if student and student.favorite_figure:
        custom_scenario = (
            f"You just saw {student.favorite_figure} pull off an amazing play — "
            f"can you calculate the stats behind it?"
        )
        base_scenarios = [custom_scenario] + base_scenarios

    # If student has a favorite team, add a team scenario
    if student and student.favorite_team:
        team_scenario = (
            f"Your favorite team, the {student.favorite_team}, just won a big game. "
            f"Let's break down the numbers!"
        )
        base_scenarios = [team_scenario] + base_scenarios

    # --- 3. Build hooks ---
    hooks = list(interest_profile.engagement_hooks)

    # --- 4. Stats — factual, from interest profile ---
    stats = dict(interest_profile.verified_stats)

    # --- 5. Trending — current references from interest profile ---
    trending = list(interest_profile.trending_now)

    # --- 6. Build figures list (highlight student's favorite) ---
    figures = list(interest_profile.famous_figures[:3])
    favorite_label: Optional[str] = None

    if student and student.favorite_figure:
        fav = student.favorite_figure
        # Determine possessive form of address
        possessive = f"{address}'s" if address != "you" else "your"
        favorite_label = f"{fav} ({possessive} favorite)"

        # Ensure favorite is in the list and highlighted
        if fav in figures:
            figures[figures.index(fav)] = favorite_label
        else:
            figures = [favorite_label] + figures[:2]

    # --- 7. Color palette ---
    color_palette = interest_profile.visual_themes.get(
        "primary_colors", "thematic colors"
    )

    return EngagementProfile(
        address=address,
        student_name=student_name,
        scenarios=base_scenarios[:4],
        hooks=hooks[:3],
        stats=stats,
        trending=trending[:3],
        current_season=interest_profile.current_season,
        favorite_label=favorite_label,
        figures=figures,
        color_palette=color_palette,
    )
