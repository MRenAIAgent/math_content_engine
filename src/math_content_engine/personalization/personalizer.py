"""
Content personalizer that adapts math content to student interests.

This module provides the ContentPersonalizer class which can transform
generic math content or generation prompts to use interest-specific
contexts, examples, and terminology.
"""

import logging
from dataclasses import dataclass
from typing import Optional, List

from .interests import InterestProfile, get_interest_profile, list_available_interests
from .student_profile import StudentProfile

logger = logging.getLogger(__name__)


@dataclass
class PersonalizedContent:
    """Result of content personalization."""
    original_topic: str
    personalized_topic: str
    original_requirements: str
    personalized_requirements: str
    interest_profile: InterestProfile
    personalization_prompt: str


class ContentPersonalizer:
    """
    Personalizes math content based on student interests.

    This class can be used to:
    1. Generate personalization prompts for LLM-based content generation
    2. Transform existing content to use interest-specific contexts
    3. Provide interest-specific examples and analogies
    """

    def __init__(self, interest: Optional[str] = None):
        """
        Initialize the personalizer with an optional default interest.

        Args:
            interest: Default interest to use for personalization
        """
        self.default_interest = interest
        self._profile: Optional[InterestProfile] = None
        if interest:
            self._profile = get_interest_profile(interest)
            if not self._profile:
                logger.warning(f"Unknown interest '{interest}'. Available: {list_available_interests()}")

    @property
    def profile(self) -> Optional[InterestProfile]:
        """Get the current interest profile."""
        return self._profile

    def set_interest(self, interest: str) -> bool:
        """
        Set the interest for personalization.

        Args:
            interest: Interest name (e.g., "basketball", "gaming")

        Returns:
            True if interest was found and set, False otherwise
        """
        profile = get_interest_profile(interest)
        if profile:
            self._profile = profile
            self.default_interest = interest
            logger.info(f"Personalization set to: {profile.display_name}")
            return True
        else:
            logger.warning(f"Unknown interest '{interest}'. Available: {list_available_interests()}")
            return False

    def personalize_prompt(
        self,
        topic: str,
        requirements: str = "",
        interest: Optional[str] = None
    ) -> PersonalizedContent:
        """
        Add personalization context to a generation prompt.

        Args:
            topic: The math topic to animate/explain
            requirements: Additional requirements for the content
            interest: Optional interest override (uses default if not provided)

        Returns:
            PersonalizedContent with enhanced prompts
        """
        # Get the profile to use
        profile = self._get_profile(interest)
        if not profile:
            # Return original content if no profile
            return PersonalizedContent(
                original_topic=topic,
                personalized_topic=topic,
                original_requirements=requirements,
                personalized_requirements=requirements,
                interest_profile=None,
                personalization_prompt=""
            )

        # Generate personalization prompt
        personalization_prompt = profile.get_personalization_prompt()

        # Enhance the topic with context
        personalized_topic = f"{topic} (using {profile.display_name} examples and context)"

        # Enhance requirements with personalization instructions
        personalized_requirements = self._build_personalized_requirements(
            requirements, profile
        )

        return PersonalizedContent(
            original_topic=topic,
            personalized_topic=personalized_topic,
            original_requirements=requirements,
            personalized_requirements=personalized_requirements,
            interest_profile=profile,
            personalization_prompt=personalization_prompt
        )

    def get_example_scenarios(
        self,
        math_concept: str,
        interest: Optional[str] = None,
        count: int = 3
    ) -> List[str]:
        """
        Get interest-specific example scenarios for a math concept.

        Args:
            math_concept: The math concept (e.g., "solving equations")
            interest: Optional interest override
            count: Number of examples to return

        Returns:
            List of example scenarios
        """
        profile = self._get_profile(interest)
        if not profile:
            return []

        # Return scenarios, limited by count
        return profile.example_scenarios[:count]

    def get_analogy(
        self,
        math_concept: str,
        interest: Optional[str] = None
    ) -> Optional[str]:
        """
        Get an interest-specific analogy for a math concept.

        Args:
            math_concept: The math concept to find an analogy for
            interest: Optional interest override

        Returns:
            Analogy string if found, None otherwise
        """
        profile = self._get_profile(interest)
        if not profile:
            return None

        # Look for matching analogy
        concept_lower = math_concept.lower()
        for key, analogy in profile.analogies.items():
            if key in concept_lower or concept_lower in key:
                return analogy

        return None

    def get_famous_figures(
        self,
        interest: Optional[str] = None,
        count: int = 5
    ) -> List[str]:
        """
        Get famous figures from the interest domain.

        Args:
            interest: Optional interest override
            count: Number of figures to return

        Returns:
            List of famous figure names
        """
        profile = self._get_profile(interest)
        if not profile:
            return []

        return profile.famous_figures[:count]

    def get_visual_theme(
        self,
        interest: Optional[str] = None
    ) -> dict:
        """
        Get visual theme suggestions for the interest.

        Args:
            interest: Optional interest override

        Returns:
            Dictionary of visual theme suggestions
        """
        profile = self._get_profile(interest)
        if not profile:
            return {}

        return profile.visual_themes

    def _get_profile(self, interest: Optional[str] = None) -> Optional[InterestProfile]:
        """Get profile from interest param or default."""
        if interest:
            return get_interest_profile(interest)
        return self._profile

    def get_animation_personalization(
        self,
        topic: str,
        interest: Optional[str] = None,
        student: Optional[StudentProfile] = None,
    ) -> str:
        """Get personalization context for Manim animation code generation.

        Returns data AND instructions so the LLM knows both WHAT to
        reference and HOW to make it engaging (2nd-person address,
        engagement hooks, current references).

        Args:
            topic: Math topic being animated
            interest: Optional interest override
            student: Optional student profile for individual personalization

        Returns:
            A concise personalization string, or empty string if no profile.
        """
        profile = self._get_profile(interest)
        if not profile:
            return ""

        parts: list[str] = []

        # --- Header with current context ---
        header = f"Theme: {profile.display_name}"
        if profile.current_season:
            header += f" ({profile.current_season})"
        parts.append(header)

        # --- Student address ---
        if student and student.name:
            parts.append(
                f"Address the viewer as: \"{student.name}\" "
                f"(or \"you\" when paraphrasing)"
            )
        else:
            parts.append("Address the viewer as: \"you\" (2nd person, not \"a player\")")

        # --- Current/trending references ---
        if profile.trending_now:
            trending = ", ".join(profile.trending_now[:2])
            parts.append(f"Current references: {trending}")

        # --- Figures (prefer student's favorite) ---
        figures_list = list(profile.famous_figures[:3])
        if student and student.favorite_figure:
            fav = student.favorite_figure
            if fav not in figures_list:
                figures_list = [fav] + figures_list[:2]
            label = f"{fav} ({student.name}'s favorite)" if student.name else fav
            figures_list[figures_list.index(fav)] = label
        parts.append(f"Figures: {', '.join(figures_list)}")

        # --- Color palette ---
        colors = profile.visual_themes.get("primary_colors", "thematic colors")
        parts.append(f"Color palette: {colors}")

        # --- Scenarios (prefer 2nd person) ---
        scenarios_source = (
            profile.second_person_scenarios
            if profile.second_person_scenarios
            else profile.example_scenarios
        )
        scenarios = "\n".join(f"  - {s}" for s in scenarios_source[:2])
        parts.append(
            f"Scenarios (use 2nd person — say \"you\", not \"a player\"):\n{scenarios}"
        )

        # --- Engagement hooks ---
        if profile.engagement_hooks:
            hooks = "\n".join(f"  - {h}" for h in profile.engagement_hooks[:2])
            parts.append(f"Engagement hooks (weave one into the animation):\n{hooks}")

        # --- Verified stats ---
        if profile.verified_stats:
            stats = ", ".join(
                f"{k}: {v}" for k, v in list(profile.verified_stats.items())[:3]
            )
            parts.append(f"Real stats you can use: {stats}")

        # --- Analogy (if topic-relevant) ---
        topic_lower = topic.lower()
        for key, analogy in profile.analogies.items():
            if key in topic_lower or topic_lower in key:
                parts.append(f"Analogy: {key} is like {analogy}")
                break

        # --- Engagement rules ---
        parts.append(
            "Rules:\n"
            "1. Say \"you/your\" not \"a player\" — make it personal\n"
            "2. Use REAL numbers from the stats above, not made-up ones\n"
            "3. Start with a hook or question, not a dry definition\n"
            f"4. Keep ALL math rigorous — engagement is secondary to correctness"
        )

        return "\n".join(parts)

    def _build_personalized_requirements(
        self,
        original_requirements: str,
        profile: InterestProfile
    ) -> str:
        """Build enhanced requirements with personalization."""
        # Get a few example scenarios
        examples = "\n".join(f"  - {s}" for s in profile.example_scenarios[:3])

        # Get famous figures
        figures = ", ".join(profile.famous_figures[:4])

        # Get visual theme
        colors = profile.visual_themes.get("primary_colors", "thematic colors")

        personalization_section = f"""
## PERSONALIZATION: {profile.display_name} Theme

{profile.context_intro}

### Make It Engaging:
- Use these figures/references: {figures}
- Example scenarios to adapt:
{examples}

### Visual Style:
- Color palette: {colors}
- Make animations thematically appropriate

### Guidelines:
1. Replace generic "x" and "y" with meaningful variable names when appropriate
2. Use real-world {profile.name} statistics and scenarios
3. Reference well-known {profile.name} events, players, or facts
4. Keep math rigorous while making context relatable and fun

"""
        if original_requirements:
            return f"{personalization_section}\n## ORIGINAL REQUIREMENTS:\n{original_requirements}"
        return personalization_section


def create_personalized_generator(interest: str):
    """
    Factory function to create a personalized content generator.

    Args:
        interest: The interest to personalize for

    Returns:
        ContentPersonalizer configured for the interest
    """
    personalizer = ContentPersonalizer(interest)
    if not personalizer.profile:
        raise ValueError(
            f"Unknown interest '{interest}'. "
            f"Available interests: {', '.join(list_available_interests())}"
        )
    return personalizer
