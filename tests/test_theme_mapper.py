"""
Tests for bidirectional theme mapping between tutor and engine.

The theme_mapper module provides:
- theme_to_interest: Convert tutor ContentTheme values to engine interest strings
- interest_to_theme: Convert engine interest strings to tutor ContentTheme values
"""
import pytest

from math_content_engine.personalization.theme_mapper import (
    theme_to_interest,
    interest_to_theme,
    _THEME_TO_INTEREST,
    _INTEREST_TO_THEME,
)


class TestThemeToInterest:
    """Tests for theme_to_interest function."""

    def test_theme_to_interest_all_themes(self):
        """Test all 11 entries in _THEME_TO_INTEREST mapping."""
        expected_mappings = {
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

        # Verify all expected mappings
        for theme, expected_interest in expected_mappings.items():
            result = theme_to_interest(theme)
            assert result == expected_interest, f"theme_to_interest('{theme}') should be '{expected_interest}', got '{result}'"

        # Verify we have all 11 entries
        assert len(_THEME_TO_INTEREST) == 11

    def test_theme_to_interest_case_insensitive(self):
        """theme_to_interest should be case-insensitive."""
        assert theme_to_interest("SPORTS_BASKETBALL") == "basketball"
        assert theme_to_interest("Sports_Basketball") == "basketball"
        assert theme_to_interest("NEUTRAL") == "neutral"
        assert theme_to_interest("Gaming_Minecraft") == "gaming"
        assert theme_to_interest("NATURE_SPACE") == "space"

    def test_unknown_theme_returns_neutral(self):
        """Unknown themes should return 'neutral'."""
        assert theme_to_interest("unknown_theme") == "neutral"
        assert theme_to_interest("sports_tennis") == "neutral"
        assert theme_to_interest("music_rock") == "neutral"
        assert theme_to_interest("random_value") == "neutral"

    def test_theme_to_interest_empty_string(self):
        """Empty string theme should return 'neutral'."""
        # Empty string lowercased is still empty string, not in mapping
        assert theme_to_interest("") == "neutral"

    def test_theme_to_interest_whitespace(self):
        """Whitespace themes should return 'neutral'."""
        assert theme_to_interest("  ") == "neutral"
        assert theme_to_interest("\t") == "neutral"


class TestInterestToTheme:
    """Tests for interest_to_theme function."""

    def test_interest_to_theme_all_interests(self):
        """Test all 23 entries in _INTEREST_TO_THEME mapping."""
        expected_mappings = {
            # Core/neutral
            "neutral": "neutral",
            # Sports (3 entries)
            "basketball": "sports_basketball",
            "soccer": "sports_soccer",
            "football": "sports_soccer",  # alias for soccer
            # Gaming (4 entries)
            "gaming": "gaming_minecraft",
            "minecraft": "gaming_minecraft",
            "pokemon": "gaming_pokemon",
            "pokémon": "gaming_pokemon",  # with accent
            # Music (2 entries)
            "music": "music_pop",
            "pop music": "music_pop",
            # Nature (4 entries)
            "nature": "nature_animals",
            "animals": "nature_animals",
            "space": "nature_space",
            "astronomy": "nature_space",
            # Technology (3 entries)
            "robots": "technology_robots",
            "technology": "technology_robots",
            "coding": "technology_robots",
            # Food (3 entries)
            "cooking": "food_cooking",
            "food": "food_cooking",
            "baking": "food_cooking",
            # Art (3 entries)
            "art": "art_drawing",
            "drawing": "art_drawing",
            "painting": "art_drawing",
        }

        # Verify all expected mappings
        for interest, expected_theme in expected_mappings.items():
            result = interest_to_theme(interest)
            assert result == expected_theme, f"interest_to_theme('{interest}') should be '{expected_theme}', got '{result}'"

        # Verify we have all 23 entries
        assert len(_INTEREST_TO_THEME) == 23

    def test_interest_to_theme_case_insensitive(self):
        """interest_to_theme should be case-insensitive."""
        assert interest_to_theme("BASKETBALL") == "sports_basketball"
        assert interest_to_theme("Basketball") == "sports_basketball"
        assert interest_to_theme("MINECRAFT") == "gaming_minecraft"
        assert interest_to_theme("Robots") == "technology_robots"
        assert interest_to_theme("COOKING") == "food_cooking"

    def test_unknown_interest_returns_neutral(self):
        """Unknown interests should return 'neutral'."""
        assert interest_to_theme("tennis") == "neutral"
        assert interest_to_theme("swimming") == "neutral"
        assert interest_to_theme("reading") == "neutral"
        assert interest_to_theme("unknown") == "neutral"

    def test_empty_interest_returns_neutral(self):
        """Empty string interest should return 'neutral'."""
        assert interest_to_theme("") == "neutral"

    def test_interest_to_theme_whitespace_handling(self):
        """interest_to_theme should strip whitespace."""
        assert interest_to_theme("  basketball  ") == "sports_basketball"
        assert interest_to_theme("\tgaming\t") == "gaming_minecraft"
        assert interest_to_theme("  space  ") == "nature_space"

    def test_interest_to_theme_aliases(self):
        """Test that interest aliases map correctly."""
        # Football -> sports_soccer (not sports_football)
        assert interest_to_theme("football") == "sports_soccer"

        # Minecraft -> gaming_minecraft
        assert interest_to_theme("minecraft") == "gaming_minecraft"

        # Pokémon with accent -> gaming_pokemon
        assert interest_to_theme("pokémon") == "gaming_pokemon"

        # Astronomy -> nature_space
        assert interest_to_theme("astronomy") == "nature_space"

        # Coding -> technology_robots
        assert interest_to_theme("coding") == "technology_robots"

        # Baking -> food_cooking
        assert interest_to_theme("baking") == "food_cooking"

        # Painting -> art_drawing
        assert interest_to_theme("painting") == "art_drawing"


class TestRoundtripConversion:
    """Tests for bidirectional conversion consistency."""

    def test_roundtrip_theme_interest_theme(self):
        """Theme -> interest -> theme should preserve the original theme."""
        themes = [
            "neutral",
            "sports_basketball",
            "sports_soccer",
            "gaming_minecraft",
            "gaming_pokemon",
            "nature_animals",
            "nature_space",
            "music_pop",
            "technology_robots",
            "food_cooking",
            "art_drawing",
        ]

        for theme in themes:
            interest = theme_to_interest(theme)
            result_theme = interest_to_theme(interest)
            assert result_theme == theme, (
                f"Roundtrip failed for '{theme}': "
                f"theme_to_interest('{theme}')='{interest}', "
                f"interest_to_theme('{interest}')='{result_theme}'"
            )

    def test_interest_to_theme_primary_interests(self):
        """Primary interests (direct mappings from theme_to_interest) should roundtrip."""
        primary_interests = [
            "neutral",
            "basketball",
            "soccer",
            "gaming",
            "pokemon",
            "animals",
            "space",
            "music",
            "robots",
            "cooking",
            "art",
        ]

        for interest in primary_interests:
            theme = interest_to_theme(interest)
            result_interest = theme_to_interest(theme)
            assert result_interest == interest, (
                f"Roundtrip failed for '{interest}': "
                f"interest_to_theme('{interest}')='{theme}', "
                f"theme_to_interest('{theme}')='{result_interest}'"
            )

    def test_alias_interests_map_to_canonical(self):
        """Alias interests should map to themes that map back to canonical interests."""
        # These are aliases that map to the same theme as a primary interest
        alias_to_canonical = {
            "football": "soccer",       # football -> sports_soccer -> soccer
            "minecraft": "gaming",      # minecraft -> gaming_minecraft -> gaming
            "astronomy": "space",       # astronomy -> nature_space -> space
            "technology": "robots",     # technology -> technology_robots -> robots
            "coding": "robots",         # coding -> technology_robots -> robots
            "food": "cooking",          # food -> food_cooking -> cooking
            "baking": "cooking",        # baking -> food_cooking -> cooking
            "drawing": "art",           # drawing -> art_drawing -> art
            "painting": "art",          # painting -> art_drawing -> art
            "nature": "animals",        # nature -> nature_animals -> animals
            "pop music": "music",       # pop music -> music_pop -> music
        }

        for alias, canonical in alias_to_canonical.items():
            theme = interest_to_theme(alias)
            result_interest = theme_to_interest(theme)
            assert result_interest == canonical, (
                f"Alias '{alias}' should resolve to canonical '{canonical}', "
                f"but got '{result_interest}'"
            )


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_none_like_values(self):
        """Test handling of None-like string values."""
        assert interest_to_theme("none") == "neutral"
        assert interest_to_theme("null") == "neutral"
        assert theme_to_interest("none") == "neutral"

    def test_special_characters_in_interest(self):
        """Test handling of special characters."""
        # Pokemon with accent should work
        assert interest_to_theme("pokémon") == "gaming_pokemon"

        # But other special characters should return neutral
        assert interest_to_theme("basket-ball") == "neutral"
        assert interest_to_theme("gaming!") == "neutral"

    def test_mapping_completeness(self):
        """Verify mapping dictionaries have expected sizes."""
        assert len(_THEME_TO_INTEREST) == 11, "Should have 11 theme mappings"
        assert len(_INTEREST_TO_THEME) == 23, "Should have 23 interest mappings"

    def test_all_themes_have_interest_mapping(self):
        """Every theme should have a corresponding interest that maps back."""
        for theme in _THEME_TO_INTEREST:
            interest = theme_to_interest(theme)
            back_to_theme = interest_to_theme(interest)
            assert back_to_theme == theme, (
                f"Theme '{theme}' maps to interest '{interest}' "
                f"which maps back to '{back_to_theme}'"
            )
