"""Tests for StudentProfile dataclass."""

from math_content_engine.personalization import StudentProfile


class TestStudentProfile:
    """Test StudentProfile creation and defaults."""

    def test_defaults_all_none(self):
        profile = StudentProfile()
        assert profile.name is None
        assert profile.grade_level is None
        assert profile.favorite_figure is None
        assert profile.favorite_team is None
        assert profile.personal_context is None

    def test_with_name_only(self):
        profile = StudentProfile(name="Jordan")
        assert profile.name == "Jordan"
        assert profile.grade_level is None

    def test_with_full_data(self):
        profile = StudentProfile(
            name="Jordan",
            grade_level="8th grade",
            favorite_figure="Stephen Curry",
            favorite_team="Warriors",
            personal_context="Plays point guard on school team",
        )
        assert profile.name == "Jordan"
        assert profile.grade_level == "8th grade"
        assert profile.favorite_figure == "Stephen Curry"
        assert profile.favorite_team == "Warriors"
        assert "point guard" in profile.personal_context

    def test_import_from_package(self):
        """StudentProfile should be importable from the personalization package."""
        from math_content_engine.personalization import StudentProfile as SP
        assert SP is StudentProfile
