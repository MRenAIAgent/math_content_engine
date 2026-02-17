"""
Bidirectional mapping between tutor ContentTheme strings and engine interest strings.

The tutor uses ContentTheme enum values like "sports_basketball".
The engine uses simple interest strings like "basketball".
"""

from __future__ import annotations

from typing import Dict

# Tutor theme -> engine interest
_THEME_TO_INTEREST: Dict[str, str] = {
    "neutral": "neutral",
    "sports_basketball": "basketball",
    "sports_soccer": "soccer",
    "gaming_minecraft": "gaming",
    "gaming_pokemon": "pokemon",
    "nature_animals": "animals",
    "nature_space": "space",
    "music_pop": "music",
    "technology_robots": "robots",
    "food_cooking": "cooking",
    "art_drawing": "art",
}

# Engine interest -> tutor theme
_INTEREST_TO_THEME: Dict[str, str] = {
    "neutral": "neutral",
    "basketball": "sports_basketball",
    "soccer": "sports_soccer",
    "football": "sports_soccer",
    "gaming": "gaming_minecraft",
    "minecraft": "gaming_minecraft",
    "pokemon": "gaming_pokemon",
    "pokémon": "gaming_pokemon",
    "music": "music_pop",
    "pop music": "music_pop",
    "nature": "nature_animals",
    "animals": "nature_animals",
    "space": "nature_space",
    "astronomy": "nature_space",
    "robots": "technology_robots",
    "technology": "technology_robots",
    "coding": "technology_robots",
    "cooking": "food_cooking",
    "food": "food_cooking",
    "baking": "food_cooking",
    "art": "art_drawing",
    "drawing": "art_drawing",
    "painting": "art_drawing",
}


def theme_to_interest(theme: str) -> str:
    """Convert a tutor ContentTheme value to an engine interest string."""
    return _THEME_TO_INTEREST.get(theme.lower(), "neutral")


def interest_to_theme(interest: str) -> str:
    """Convert an engine interest string to a tutor ContentTheme value."""
    if not interest:
        return "neutral"
    return _INTEREST_TO_THEME.get(interest.strip().lower(), "neutral")
