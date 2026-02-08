"""Tests for EngagementStore (SQLite KV) and make_store_key()."""

import pytest
from pathlib import Path

from math_content_engine.personalization import (
    EngagementStore,
    build_engagement_profile,
    create_engagement_profile,
    get_interest_profile,
    make_store_key,
    StudentProfile,
)


@pytest.fixture
def store(tmp_path: Path) -> EngagementStore:
    """Create a temporary store for each test."""
    return EngagementStore(db_path=tmp_path / "test_engagement.db")


class TestMakeStoreKey:
    """Test the key-generation helper."""

    def test_with_student_name(self):
        assert make_store_key("basketball", "Jordan") == "jordan:basketball"

    def test_anonymous(self):
        assert make_store_key("basketball") == "anonymous:basketball"

    def test_strips_and_lowercases(self):
        assert make_store_key("  Basketball ", " JORDAN ") == "jordan:basketball"


class TestEngagementStoreInit:
    """Test database and table creation."""

    def test_creates_db_file(self, tmp_path: Path):
        db_path = tmp_path / "sub" / "engagement.db"
        EngagementStore(db_path=db_path)
        assert db_path.exists()

    def test_creates_table(self, store: EngagementStore):
        import sqlite3

        with sqlite3.connect(store.db_path) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='engagement_profiles'"
            )
            assert cursor.fetchone() is not None


class TestEngagementStoreCRUD:
    """Test save / load / delete / exists / list_profiles."""

    def test_save_and_load(self, store: EngagementStore):
        ep = create_engagement_profile(address="J", student_name="Jordan")
        store.save("jordan:basketball", ep)
        loaded = store.load("jordan:basketball")
        assert loaded is not None
        assert loaded["address"] == "J"
        assert loaded["student_name"] == "Jordan"

    def test_load_missing_returns_none(self, store: EngagementStore):
        assert store.load("nonexistent") is None

    def test_exists(self, store: EngagementStore):
        ep = create_engagement_profile()
        store.save("key1", ep)
        assert store.exists("key1") is True
        assert store.exists("key2") is False

    def test_delete(self, store: EngagementStore):
        ep = create_engagement_profile()
        store.save("key1", ep)
        assert store.delete("key1") is True
        assert store.exists("key1") is False

    def test_delete_missing_returns_false(self, store: EngagementStore):
        assert store.delete("nonexistent") is False

    def test_list_profiles(self, store: EngagementStore):
        store.save("a:x", create_engagement_profile(address="A"))
        store.save("b:y", create_engagement_profile(address="B"))
        profiles = store.list_profiles(limit=10)
        assert len(profiles) == 2
        keys = {p["key"] for p in profiles}
        assert keys == {"a:x", "b:y"}

    def test_list_profiles_limit(self, store: EngagementStore):
        for i in range(5):
            store.save(f"k{i}", create_engagement_profile())
        profiles = store.list_profiles(limit=3)
        assert len(profiles) == 3

    def test_save_overwrites(self, store: EngagementStore):
        store.save("key1", create_engagement_profile(address="old"))
        store.save("key1", create_engagement_profile(address="new"))
        loaded = store.load("key1")
        assert loaded["address"] == "new"


class TestEngagementStoreRoundTrip:
    """Build a real profile, save, load, and compare."""

    def test_round_trip(self, store: EngagementStore):
        profile = get_interest_profile("basketball")
        student = StudentProfile(
            name="Jordan",
            preferred_address="J",
            favorite_figure="Stephen Curry",
            favorite_team="Warriors",
        )
        ep = build_engagement_profile(profile, student)

        key = make_store_key("basketball", "Jordan")
        store.save(key, ep)
        loaded = store.load(key)

        assert loaded is not None
        assert loaded["address"] == ep["address"]
        assert loaded["student_name"] == ep["student_name"]
        assert loaded["scenarios"] == ep["scenarios"]
        assert loaded["hooks"] == ep["hooks"]
        assert loaded["stats"] == ep["stats"]
        assert loaded["trending"] == ep["trending"]
        assert loaded["current_season"] == ep["current_season"]
        assert loaded["favorite_label"] == ep["favorite_label"]
        assert loaded["figures"] == ep["figures"]
        assert loaded["color_palette"] == ep["color_palette"]

    def test_round_trip_anonymous(self, store: EngagementStore):
        profile = get_interest_profile("gaming")
        ep = build_engagement_profile(profile)

        key = make_store_key("gaming")
        store.save(key, ep)
        loaded = store.load(key)

        assert loaded is not None
        assert loaded["address"] == "you"
        assert loaded["student_name"] is None
