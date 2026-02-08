"""Tests for EngagementProfile and build_engagement_profile()."""

import pytest

from math_content_engine.personalization import (
    StudentProfile,
    EngagementProfile,
    build_engagement_profile,
    get_interest_profile,
    list_available_interests,
)


class TestEngagementProfileDataclass:
    """Test EngagementProfile creation and properties."""

    def test_defaults(self):
        ep = EngagementProfile()
        assert ep.address == "you"
        assert ep.student_name is None
        assert ep.scenarios == []
        assert ep.hooks == []
        assert ep.stats == {}
        assert ep.trending == []
        assert ep.current_season == ""
        assert ep.favorite_label is None
        assert ep.figures == []
        assert ep.color_palette == "thematic colors"

    def test_has_student_false_by_default(self):
        ep = EngagementProfile()
        assert ep.has_student is False

    def test_has_student_true_with_name(self):
        ep = EngagementProfile(address="Jordan", student_name="Jordan")
        assert ep.has_student is True

    def test_frozen(self):
        ep = EngagementProfile()
        with pytest.raises(AttributeError):
            ep.address = "mutated"

    def test_import_from_package(self):
        from math_content_engine.personalization import EngagementProfile as EP
        from math_content_engine.personalization import build_engagement_profile as bep
        assert EP is EngagementProfile
        assert bep is build_engagement_profile


class TestBuildEngagementProfileNoStudent:
    """Test build_engagement_profile with interest only, no student."""

    def test_address_is_you(self):
        profile = get_interest_profile("basketball")
        ep = build_engagement_profile(profile)
        assert ep.address == "you"
        assert ep.student_name is None
        assert ep.has_student is False

    def test_scenarios_from_interest(self):
        profile = get_interest_profile("basketball")
        ep = build_engagement_profile(profile)
        assert len(ep.scenarios) > 0
        assert len(ep.scenarios) <= 4

    def test_hooks_from_interest(self):
        profile = get_interest_profile("basketball")
        ep = build_engagement_profile(profile)
        assert len(ep.hooks) > 0
        assert len(ep.hooks) <= 3

    def test_stats_from_interest(self):
        profile = get_interest_profile("basketball")
        ep = build_engagement_profile(profile)
        assert len(ep.stats) > 0

    def test_trending_from_interest(self):
        profile = get_interest_profile("basketball")
        ep = build_engagement_profile(profile)
        assert len(ep.trending) > 0
        assert len(ep.trending) <= 3

    def test_figures_from_interest(self):
        profile = get_interest_profile("basketball")
        ep = build_engagement_profile(profile)
        assert len(ep.figures) > 0

    def test_no_favorite_label(self):
        profile = get_interest_profile("basketball")
        ep = build_engagement_profile(profile)
        assert ep.favorite_label is None

    def test_color_palette(self):
        profile = get_interest_profile("basketball")
        ep = build_engagement_profile(profile)
        assert ep.color_palette != "thematic colors"

    def test_current_season(self):
        profile = get_interest_profile("basketball")
        ep = build_engagement_profile(profile)
        assert ep.current_season != ""


class TestBuildEngagementProfileWithStudent:
    """Test build_engagement_profile with student data."""

    def test_address_uses_name(self):
        profile = get_interest_profile("basketball")
        student = StudentProfile(name="Jordan")
        ep = build_engagement_profile(profile, student)
        assert ep.address == "Jordan"
        assert ep.student_name == "Jordan"
        assert ep.has_student is True

    def test_address_prefers_preferred_address(self):
        profile = get_interest_profile("basketball")
        student = StudentProfile(name="Jordan", preferred_address="J")
        ep = build_engagement_profile(profile, student)
        assert ep.address == "J"
        assert ep.student_name == "Jordan"

    def test_address_preferred_without_name(self):
        profile = get_interest_profile("basketball")
        student = StudentProfile(preferred_address="champ")
        ep = build_engagement_profile(profile, student)
        assert ep.address == "champ"
        assert ep.student_name is None

    def test_favorite_figure_highlighted(self):
        profile = get_interest_profile("basketball")
        student = StudentProfile(
            name="Jordan",
            favorite_figure="Stephen Curry",
        )
        ep = build_engagement_profile(profile, student)
        assert ep.favorite_label is not None
        assert "Stephen Curry" in ep.favorite_label
        assert "favorite" in ep.favorite_label.lower()

    def test_favorite_figure_in_figures_list(self):
        profile = get_interest_profile("basketball")
        student = StudentProfile(
            name="Jordan",
            favorite_figure="Stephen Curry",
        )
        ep = build_engagement_profile(profile, student)
        # The favorite should appear in the figures list (highlighted)
        figures_str = " ".join(ep.figures)
        assert "Stephen Curry" in figures_str

    def test_favorite_label_uses_preferred_address(self):
        profile = get_interest_profile("basketball")
        student = StudentProfile(
            name="Jordan",
            preferred_address="J",
            favorite_figure="Stephen Curry",
        )
        ep = build_engagement_profile(profile, student)
        assert "J's favorite" in ep.favorite_label

    def test_favorite_label_uses_your_when_address_is_you(self):
        """When no name/address, favorite label uses 'your'."""
        profile = get_interest_profile("basketball")
        student = StudentProfile(favorite_figure="Stephen Curry")
        ep = build_engagement_profile(profile, student)
        assert "your favorite" in ep.favorite_label

    def test_favorite_figure_adds_custom_scenario(self):
        profile = get_interest_profile("basketball")
        student = StudentProfile(favorite_figure="Stephen Curry")
        ep = build_engagement_profile(profile, student)
        # Should have a custom scenario mentioning the favorite
        assert any("Stephen Curry" in s for s in ep.scenarios)

    def test_favorite_team_adds_team_scenario(self):
        profile = get_interest_profile("basketball")
        student = StudentProfile(favorite_team="Warriors")
        ep = build_engagement_profile(profile, student)
        # Should have a team scenario
        assert any("Warriors" in s for s in ep.scenarios)

    def test_both_favorite_figure_and_team(self):
        profile = get_interest_profile("basketball")
        student = StudentProfile(
            name="Jordan",
            favorite_figure="Stephen Curry",
            favorite_team="Warriors",
        )
        ep = build_engagement_profile(profile, student)
        # Both custom scenarios should be present
        has_figure = any("Stephen Curry" in s for s in ep.scenarios)
        has_team = any("Warriors" in s for s in ep.scenarios)
        assert has_figure
        assert has_team


class TestBuildEngagementProfileAllInterests:
    """Test that build_engagement_profile works for all interest profiles."""

    @pytest.mark.parametrize("interest_name", list(list_available_interests()))
    def test_builds_without_error(self, interest_name):
        profile = get_interest_profile(interest_name)
        ep = build_engagement_profile(profile)
        assert ep.address == "you"
        assert isinstance(ep.scenarios, list)
        assert isinstance(ep.hooks, list)
        assert isinstance(ep.stats, dict)

    @pytest.mark.parametrize("interest_name", list(list_available_interests()))
    def test_builds_with_student(self, interest_name):
        profile = get_interest_profile(interest_name)
        student = StudentProfile(
            name="Alex",
            preferred_address="champ",
            favorite_figure="Someone Famous",
        )
        ep = build_engagement_profile(profile, student)
        assert ep.address == "champ"
        assert ep.student_name == "Alex"
        assert ep.favorite_label is not None
        assert "Someone Famous" in ep.favorite_label


class TestPersonalizerUsesEngagementProfile:
    """Test that get_animation_personalization uses EngagementProfile internally."""

    def test_preferred_address_in_output(self):
        from math_content_engine.personalization import ContentPersonalizer
        personalizer = ContentPersonalizer("basketball")
        student = StudentProfile(name="Jordan", preferred_address="J")
        result = personalizer.get_animation_personalization(
            "Linear equations", student=student
        )
        assert '"J"' in result
        assert "Address the viewer" in result

    def test_no_student_says_you(self):
        from math_content_engine.personalization import ContentPersonalizer
        personalizer = ContentPersonalizer("basketball")
        result = personalizer.get_animation_personalization("Linear equations")
        assert '"you"' in result
