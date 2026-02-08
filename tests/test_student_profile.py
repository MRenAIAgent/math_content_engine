"""Tests for StudentProfile dataclass."""

from math_content_engine.personalization import StudentProfile


class TestStudentProfile:
    """Test StudentProfile creation and defaults."""

    def test_defaults_all_none(self):
        profile = StudentProfile()
        assert profile.name is None
        assert profile.preferred_address is None
        assert profile.grade_level is None
        assert profile.favorite_figure is None
        assert profile.favorite_team is None
        assert profile.personal_context is None

    def test_with_name_only(self):
        profile = StudentProfile(name="Jordan")
        assert profile.name == "Jordan"
        assert profile.preferred_address is None
        assert profile.grade_level is None

    def test_with_full_data(self):
        profile = StudentProfile(
            name="Jordan",
            preferred_address="J",
            grade_level="8th grade",
            favorite_figure="Stephen Curry",
            favorite_team="Warriors",
            personal_context="Plays point guard on school team",
        )
        assert profile.name == "Jordan"
        assert profile.preferred_address == "J"
        assert profile.grade_level == "8th grade"
        assert profile.favorite_figure == "Stephen Curry"
        assert profile.favorite_team == "Warriors"
        assert "point guard" in profile.personal_context

    def test_import_from_package(self):
        """StudentProfile should be importable from the personalization package."""
        from math_content_engine.personalization import StudentProfile as SP
        assert SP is StudentProfile


class TestGetDisplayAddress:
    """Test the get_display_address() priority chain."""

    def test_no_data_returns_you(self):
        profile = StudentProfile()
        assert profile.get_display_address() == "you"

    def test_name_only(self):
        profile = StudentProfile(name="Jordan")
        assert profile.get_display_address() == "Jordan"

    def test_preferred_address_takes_priority(self):
        profile = StudentProfile(name="Jordan", preferred_address="J")
        assert profile.get_display_address() == "J"

    def test_preferred_address_without_name(self):
        profile = StudentProfile(preferred_address="champ")
        assert profile.get_display_address() == "champ"
