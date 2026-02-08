"""Tests for engagement fields on InterestProfile and their flow through personalization."""

import pytest

from math_content_engine.personalization import (
    ContentPersonalizer,
    StudentProfile,
    get_interest_profile,
    list_available_interests,
)


class TestEngagementFieldsPopulated:
    """Verify engagement fields are populated on profiles."""

    def test_basketball_second_person_scenarios(self):
        profile = get_interest_profile("basketball")
        assert len(profile.second_person_scenarios) >= 3
        # All should use "you" or "your"
        for scenario in profile.second_person_scenarios:
            assert "you" in scenario.lower() or "your" in scenario.lower(), (
                f"Second-person scenario should use 'you/your': {scenario}"
            )

    def test_basketball_engagement_hooks(self):
        profile = get_interest_profile("basketball")
        assert len(profile.engagement_hooks) >= 2

    def test_basketball_verified_stats(self):
        profile = get_interest_profile("basketball")
        assert len(profile.verified_stats) >= 4
        # Should have specific real numbers
        assert "3pt_line_distance" in profile.verified_stats

    def test_basketball_trending_now(self):
        profile = get_interest_profile("basketball")
        assert len(profile.trending_now) >= 2

    def test_basketball_current_season(self):
        profile = get_interest_profile("basketball")
        assert profile.current_season
        assert "NBA" in profile.current_season or "2024" in profile.current_season

    @pytest.mark.parametrize("interest", list_available_interests())
    def test_all_profiles_have_engagement_fields(self, interest):
        """Every profile should have at least some engagement data."""
        profile = get_interest_profile(interest)
        assert profile is not None, f"Profile not found: {interest}"
        # At minimum, every profile should have second_person_scenarios
        assert len(profile.second_person_scenarios) >= 2, (
            f"{interest} should have at least 2 second_person_scenarios"
        )
        assert len(profile.engagement_hooks) >= 1, (
            f"{interest} should have at least 1 engagement_hook"
        )


class TestAnimationPersonalizationEngagement:
    """Test that get_animation_personalization() includes engagement data."""

    def test_includes_second_person_scenarios(self):
        personalizer = ContentPersonalizer("basketball")
        result = personalizer.get_animation_personalization("linear equations")
        # Should prefer 2nd person scenarios
        assert "you" in result.lower()
        assert "Scenarios" in result

    def test_includes_engagement_hooks(self):
        personalizer = ContentPersonalizer("basketball")
        result = personalizer.get_animation_personalization("linear equations")
        assert "Engagement hooks" in result

    def test_includes_current_season(self):
        personalizer = ContentPersonalizer("basketball")
        result = personalizer.get_animation_personalization("linear equations")
        assert "2024-25" in result or "NBA Season" in result

    def test_includes_trending_now(self):
        personalizer = ContentPersonalizer("basketball")
        result = personalizer.get_animation_personalization("linear equations")
        assert "Current references" in result

    def test_includes_verified_stats(self):
        personalizer = ContentPersonalizer("basketball")
        result = personalizer.get_animation_personalization("linear equations")
        assert "Real stats" in result

    def test_includes_engagement_rules(self):
        personalizer = ContentPersonalizer("basketball")
        result = personalizer.get_animation_personalization("linear equations")
        assert "you/your" in result
        assert "REAL numbers" in result
        assert "hook" in result.lower()

    def test_with_student_name(self):
        personalizer = ContentPersonalizer("basketball")
        student = StudentProfile(name="Jordan")
        result = personalizer.get_animation_personalization(
            "linear equations", student=student
        )
        assert "Jordan" in result
        assert "Address the viewer as" in result

    def test_with_student_favorite_figure(self):
        personalizer = ContentPersonalizer("basketball")
        student = StudentProfile(
            name="Jordan",
            favorite_figure="Stephen Curry",
        )
        result = personalizer.get_animation_personalization(
            "linear equations", student=student
        )
        # Curry should appear with "favorite" label
        assert "Stephen Curry" in result
        assert "favorite" in result.lower()

    def test_without_student_defaults_to_you(self):
        personalizer = ContentPersonalizer("basketball")
        result = personalizer.get_animation_personalization("linear equations")
        assert "\"you\"" in result
        assert "2nd person" in result

    def test_backward_compatible_with_minimal_profile(self):
        """Profiles without new fields should still work."""
        from math_content_engine.personalization.interests import InterestProfile

        minimal_profile = InterestProfile(
            name="test",
            display_name="Test Interest",
            description="For testing",
            context_intro="Testing",
            famous_figures=["Figure 1", "Figure 2"],
            example_scenarios=["Scenario 1", "Scenario 2"],
            visual_themes={"primary_colors": "blue, red"},
            # No engagement fields set - defaults to empty
        )
        personalizer = ContentPersonalizer()
        personalizer._profile = minimal_profile

        result = personalizer.get_animation_personalization("math topic")
        # Should still produce valid output
        assert "Theme: Test Interest" in result
        assert "Figure 1" in result
        # Should fall back to generic scenarios
        assert "Scenario 1" in result

    def test_analogy_matching_still_works(self):
        personalizer = ContentPersonalizer("basketball")
        result = personalizer.get_animation_personalization("solving equations")
        assert "Analogy" in result


class TestPromptTemplateEngagement:
    """Test that engagement style appears in generation prompts."""

    def test_engagement_section_in_template(self):
        from math_content_engine.generator.prompts import build_generation_prompt

        result = build_generation_prompt("linear equations")
        assert "## ENGAGEMENT STYLE" in result
        assert "you" in result
        assert "challenge moment" in result

    def test_student_name_in_personalized_prompt(self):
        from math_content_engine.generator.prompts import build_generation_prompt

        result = build_generation_prompt(
            "linear equations",
            personalization_context="Theme: Basketball",
            student_name="Jordan",
        )
        assert "Jordan" in result
        assert "address them directly" in result.lower()

    def test_student_name_not_included_without_personalization(self):
        from math_content_engine.generator.prompts import build_generation_prompt

        result = build_generation_prompt(
            "linear equations",
            student_name="Jordan",
        )
        # Student name only appears in personalization section
        # If no personalization context, it shouldn't appear
        assert "Student's name" not in result


class TestNarrationStudentName:
    """Test that narration prompts support student name."""

    def test_build_narration_prompt_with_name(self):
        from math_content_engine.tts.narration_generator import build_narration_prompt

        result = build_narration_prompt(
            topic="linear equations",
            animation_description="Solving x + 3 = 7",
            animation_duration=30.0,
            student_name="Jordan",
        )
        assert "Jordan" in result
        assert "STUDENT ADDRESS" in result

    def test_build_narration_prompt_without_name(self):
        from math_content_engine.tts.narration_generator import build_narration_prompt

        result = build_narration_prompt(
            topic="linear equations",
            animation_description="Solving x + 3 = 7",
            animation_duration=30.0,
        )
        assert "STUDENT ADDRESS" not in result
        # But should still have "you" address guidance
        assert "you" in result.lower()


class TestPlaygroundPromptPreview:
    """Test that playground preview uses the same personalization path."""

    def test_preview_with_student_name(self):
        from math_content_engine.api.playground.prompt_builder import (
            preview_animation_prompts,
        )

        preview = preview_animation_prompts(
            topic="linear equations",
            interest="basketball",
            student_name="Jordan",
        )
        assert "Jordan" in preview.user_prompt
        assert "ENGAGEMENT STYLE" in preview.user_prompt

    def test_preview_without_student_name(self):
        from math_content_engine.api.playground.prompt_builder import (
            preview_animation_prompts,
        )

        preview = preview_animation_prompts(
            topic="linear equations",
            interest="basketball",
        )
        assert "ENGAGEMENT STYLE" in preview.user_prompt
        assert "you" in preview.user_prompt.lower()

    def test_preview_uses_get_animation_personalization(self):
        """Playground should use the same path as the main engine."""
        from math_content_engine.api.playground.prompt_builder import (
            preview_animation_prompts,
        )

        preview = preview_animation_prompts(
            topic="linear equations",
            interest="basketball",
        )
        # Should include engagement hooks (from get_animation_personalization)
        assert "Engagement hooks" in preview.user_prompt
        # Should include verified stats
        assert "Real stats" in preview.user_prompt
