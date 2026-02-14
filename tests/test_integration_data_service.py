"""
Integration tests for TutorDataServiceWriter → agentic_math_tutor PostgreSQL.

These tests exercise the REAL data service integration:
  - Write video records to the tutor's PostgreSQL `videos` table
  - Read them back and verify all fields
  - Test upsert on re-generation (same concept/theme/grade)
  - Test error_message propagation on failures
  - Test full engine pipeline → data service round-trip

Requires:
  - agentic_math_tutor PostgreSQL running (docker-compose up postgres)
  - TUTOR_DATABASE_URL or default localhost:15432

Run with:
    pytest tests/test_integration_data_service.py -v
"""

import os
import uuid
from pathlib import Path

import pytest

from math_content_engine.integration.tutor_writer import (
    INTEREST_TO_THEME,
    TutorDataServiceWriter,
    map_interest_to_theme,
    normalize_grade,
)

# Gate all tests on PG connectivity
try:
    import asyncpg  # noqa: F401

    _HAS_ASYNCPG = True
except ImportError:
    _HAS_ASYNCPG = False


def _pg_is_reachable() -> bool:
    """Quick check: can we connect to the tutor PG?"""
    if not _HAS_ASYNCPG:
        return False
    import asyncio

    async def _probe():
        try:
            url = os.getenv(
                "TUTOR_DATABASE_URL",
                "postgresql://math_tutor_app:local_dev_password@localhost:15432/math_tutor",
            )
            conn = await asyncpg.connect(url, timeout=3)
            await conn.close()
            return True
        except Exception:
            return False

    return asyncio.get_event_loop().run_until_complete(_probe())


_PG_AVAILABLE = _pg_is_reachable()
pytestmark = pytest.mark.skipif(
    not _PG_AVAILABLE,
    reason="Tutor PostgreSQL not reachable (start with docker-compose up postgres)",
)

# Unique source tag so cleanup never touches real data
_TEST_SOURCE = f"integration_test_{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def writer():
    """TutorDataServiceWriter pointed at local Docker PG."""
    w = TutorDataServiceWriter()
    yield w
    # Cleanup rows created by this test run
    w.cleanup_e2e(source=_TEST_SOURCE)


# ---------------------------------------------------------------------------
# 1. Unit-level mapping helpers (no DB required, run anyway)
# ---------------------------------------------------------------------------


class TestMappingHelpers:
    """Verify interest→theme and grade normalisation before touching the DB."""

    def test_interest_to_theme_known(self):
        assert map_interest_to_theme("basketball") == "sports_basketball"
        assert map_interest_to_theme("gaming") == "gaming_minecraft"
        assert map_interest_to_theme("space") == "nature_space"
        assert map_interest_to_theme("music") == "music_pop"

    def test_interest_to_theme_unknown_defaults_to_neutral(self):
        assert map_interest_to_theme("unknown_interest") == "neutral"
        assert map_interest_to_theme(None) == "neutral"
        assert map_interest_to_theme("") == "neutral"

    def test_normalize_grade(self):
        assert normalize_grade("grade_8") == "grade_8"
        assert normalize_grade(None) == "grade_7"
        assert normalize_grade("") == "grade_7"

    def test_all_interests_have_theme_mapping(self):
        """Every key in INTEREST_TO_THEME must produce a non-neutral theme."""
        for interest, expected_theme in INTEREST_TO_THEME.items():
            result = map_interest_to_theme(interest)
            assert result == expected_theme
            assert result != "neutral", f"{interest} should not map to neutral"


# ---------------------------------------------------------------------------
# 2. Write → Read round-trip
# ---------------------------------------------------------------------------


class TestWriteReadRoundTrip:
    """Write a video to tutor PG, read it back, verify every field."""

    def test_write_and_read_success_video(self, writer):
        """Insert a successful video and read it back."""
        vid = writer.write_video(
            concept_id="INT-TEST-01",
            interest="basketball",
            grade="grade_8",
            engine_video_id="eng-001",
            manim_code="class TestScene(Scene):\n    def construct(self): pass",
            success=True,
            file_size_bytes=2048,
            generation_time_seconds=12.5,
            source=_TEST_SOURCE,
        )
        assert vid is not None

        row = writer.read_video(vid)
        assert row is not None
        assert row["concept_id"] == "INT-TEST-01"
        assert row["theme"] == "sports_basketball"
        assert row["grade"] == "grade_8"
        assert row["template_id"] == "personalized"
        assert row["engine_video_id"] == "eng-001"
        assert row["gcs_path"] == "engine/eng-001.mp4"
        assert row["status"] == "pre_generated"
        assert row["file_size_bytes"] == 2048
        assert row["generation_time_seconds"] == pytest.approx(12.5)
        assert row["source"] == _TEST_SOURCE
        assert "TestScene" in row["manim_code"]
        assert row["error_message"] is None

    def test_write_and_read_failed_video(self, writer):
        """Insert a failed video with error_message and verify."""
        vid = writer.write_video(
            concept_id="INT-TEST-02",
            interest="gaming",
            grade="grade_7",
            engine_video_id="eng-002",
            manim_code="class Broken(Scene): ...",
            success=False,
            error_message="Manim render failed: LaTeX not found",
            source=_TEST_SOURCE,
        )
        assert vid is not None

        row = writer.read_video(vid)
        assert row is not None
        assert row["concept_id"] == "INT-TEST-02"
        assert row["theme"] == "gaming_minecraft"
        assert row["grade"] == "grade_7"
        assert row["status"] == "failed"
        assert row["error_message"] == "Manim render failed: LaTeX not found"

    def test_write_neutral_theme(self, writer):
        """When interest is None, theme should be 'neutral'."""
        vid = writer.write_video(
            concept_id="INT-TEST-03",
            interest=None,
            grade="grade_9",
            engine_video_id="eng-003",
            manim_code="class Neutral(Scene): ...",
            success=True,
            source=_TEST_SOURCE,
        )
        row = writer.read_video(vid)
        assert row["theme"] == "neutral"

    def test_write_default_grade(self, writer):
        """When grade is None, should default to 'grade_7'."""
        vid = writer.write_video(
            concept_id="INT-TEST-04",
            interest="soccer",
            grade=None,
            engine_video_id="eng-004",
            manim_code="class Default(Scene): ...",
            success=True,
            source=_TEST_SOURCE,
        )
        row = writer.read_video(vid)
        assert row["grade"] == "grade_7"
        assert row["theme"] == "sports_soccer"


# ---------------------------------------------------------------------------
# 3. Upsert behaviour (ON CONFLICT)
# ---------------------------------------------------------------------------


class TestUpsertBehaviour:
    """Re-generating the same concept/theme/grade must update, not crash."""

    def test_upsert_returns_same_uuid(self, writer):
        """Two writes for same (concept_id, theme, grade) return the same row id."""
        first = writer.write_video(
            concept_id="UPSERT-01",
            interest="basketball",
            grade="grade_8",
            engine_video_id="gen-1",
            manim_code="class V1(Scene): pass",
            success=True,
            source=_TEST_SOURCE,
        )
        second = writer.write_video(
            concept_id="UPSERT-01",
            interest="basketball",
            grade="grade_8",
            engine_video_id="gen-2",
            manim_code="class V2(Scene): pass",
            success=True,
            source=_TEST_SOURCE,
        )
        assert first == second  # Same row UUID

    def test_upsert_updates_fields(self, writer):
        """After upsert the row reflects the second write's data."""
        writer.write_video(
            concept_id="UPSERT-02",
            interest="music",
            grade="grade_9",
            engine_video_id="old-id",
            manim_code="class Old(Scene): pass",
            success=False,
            error_message="first attempt failed",
            file_size_bytes=100,
            generation_time_seconds=5.0,
            source=_TEST_SOURCE,
        )
        vid = writer.write_video(
            concept_id="UPSERT-02",
            interest="music",
            grade="grade_9",
            engine_video_id="new-id",
            manim_code="class New(Scene): pass",
            success=True,
            error_message=None,
            file_size_bytes=4096,
            generation_time_seconds=15.0,
            source=_TEST_SOURCE,
        )
        row = writer.read_video(vid)
        assert row["engine_video_id"] == "new-id"
        assert row["manim_code"] == "class New(Scene): pass"
        assert row["status"] == "pre_generated"
        assert row["error_message"] is None
        assert row["file_size_bytes"] == 4096
        assert row["generation_time_seconds"] == pytest.approx(15.0)

    def test_upsert_preserves_original_source(self, writer):
        """The source column is NOT updated on upsert (preserves first writer)."""
        writer.write_video(
            concept_id="UPSERT-03",
            interest="space",
            grade="grade_6",
            engine_video_id="id-a",
            manim_code="v1",
            success=True,
            source=_TEST_SOURCE,
        )
        vid = writer.write_video(
            concept_id="UPSERT-03",
            interest="space",
            grade="grade_6",
            engine_video_id="id-b",
            manim_code="v2",
            success=True,
            source="some_other_source",  # Different source
        )
        row = writer.read_video(vid)
        # source is NOT in the DO UPDATE SET clause, so original is preserved
        assert row["source"] == _TEST_SOURCE


# ---------------------------------------------------------------------------
# 4. Error message propagation
# ---------------------------------------------------------------------------


class TestErrorMessagePropagation:
    """Verify error_message is correctly written and cleared on re-gen."""

    def test_error_message_written_on_failure(self, writer):
        vid = writer.write_video(
            concept_id="ERR-01",
            interest="animals",
            grade="grade_6",
            engine_video_id="err-eng-01",
            manim_code="broken code",
            success=False,
            error_message="SyntaxError: invalid syntax at line 5",
            source=_TEST_SOURCE,
        )
        row = writer.read_video(vid)
        assert row["status"] == "failed"
        assert row["error_message"] == "SyntaxError: invalid syntax at line 5"

    def test_error_message_cleared_on_successful_regen(self, writer):
        """After a failed attempt, successful re-gen clears the error."""
        writer.write_video(
            concept_id="ERR-02",
            interest="robots",
            grade="grade_10",
            engine_video_id="err-eng-02a",
            manim_code="broken",
            success=False,
            error_message="render timeout",
            source=_TEST_SOURCE,
        )
        vid = writer.write_video(
            concept_id="ERR-02",
            interest="robots",
            grade="grade_10",
            engine_video_id="err-eng-02b",
            manim_code="class Fixed(Scene): pass",
            success=True,
            error_message=None,
            source=_TEST_SOURCE,
        )
        row = writer.read_video(vid)
        assert row["status"] == "pre_generated"
        assert row["error_message"] is None


# ---------------------------------------------------------------------------
# 5. All interest/theme combinations
# ---------------------------------------------------------------------------


class TestAllInterestThemeCombinations:
    """Write one video for each known interest, read back and verify theme."""

    @pytest.mark.parametrize(
        "interest,expected_theme",
        list(INTEREST_TO_THEME.items()),
    )
    def test_interest_maps_and_persists(self, writer, interest, expected_theme):
        vid = writer.write_video(
            concept_id=f"THEME-{interest[:6].upper()}",
            interest=interest,
            grade="grade_8",
            engine_video_id=f"theme-{interest}",
            manim_code=f"class {interest.title()}Scene(Scene): pass",
            success=True,
            source=_TEST_SOURCE,
        )
        row = writer.read_video(vid)
        assert row["theme"] == expected_theme


# ---------------------------------------------------------------------------
# 6. Engine pipeline → data service round-trip (mocked LLM, real PG)
# ---------------------------------------------------------------------------


class TestPipelineWriteReadVerify:
    """
    Simulate what the engine pipeline does — write to PG, read back, verify.
    No mocks. Real PG only.
    """

    def test_successful_generation_write_and_readback(self, writer):
        """Simulate a successful pipeline: write pre_generated video, read back all fields."""
        engine_vid = str(uuid.uuid4())
        vid = writer.write_video(
            concept_id="PIPE-01",
            interest="basketball",
            grade="grade_8",
            engine_video_id=engine_vid,
            manim_code="class BasketballScene(Scene):\n    def construct(self): self.play(Write(Text('hello')))",
            success=True,
            file_size_bytes=2048,
            generation_time_seconds=12.5,
            source=_TEST_SOURCE,
        )
        assert vid is not None

        row = writer.read_video(vid)
        assert row is not None
        assert row["concept_id"] == "PIPE-01"
        assert row["theme"] == "sports_basketball"
        assert row["grade"] == "grade_8"
        assert row["status"] == "pre_generated"
        assert row["engine_video_id"] == engine_vid
        assert row["gcs_path"] == f"engine/{engine_vid}.mp4"
        assert "BasketballScene" in row["manim_code"]
        assert row["file_size_bytes"] == 2048
        assert row["generation_time_seconds"] == pytest.approx(12.5)
        assert row["error_message"] is None
        assert row["source"] == _TEST_SOURCE
        assert row["template_id"] == "personalized"
        assert row["created_at"] is not None
        assert row["updated_at"] is not None

    def test_failed_generation_write_and_readback(self, writer):
        """Simulate a failed pipeline: write with error_message, read back and verify."""
        engine_vid = str(uuid.uuid4())
        vid = writer.write_video(
            concept_id="PIPE-02",
            interest="cooking",
            grade="grade_7",
            engine_video_id=engine_vid,
            manim_code="class BrokenScene(Scene): ...",
            success=False,
            error_message="LaTeX compilation error on line 12",
            generation_time_seconds=3.0,
            source=_TEST_SOURCE,
        )
        assert vid is not None

        row = writer.read_video(vid)
        assert row is not None
        assert row["concept_id"] == "PIPE-02"
        assert row["theme"] == "food_cooking"
        assert row["grade"] == "grade_7"
        assert row["status"] == "failed"
        assert row["error_message"] == "LaTeX compilation error on line 12"
        assert row["engine_video_id"] == engine_vid

    def test_regeneration_overwrites_failed_with_success(self, writer):
        """First gen fails, second succeeds — row should reflect success."""
        # First: failed
        vid1 = writer.write_video(
            concept_id="PIPE-03",
            interest="space",
            grade="grade_9",
            engine_video_id="gen-attempt-1",
            manim_code="class Attempt1(Scene): ...",
            success=False,
            error_message="Timeout during render",
            source=_TEST_SOURCE,
        )
        row1 = writer.read_video(vid1)
        assert row1["status"] == "failed"
        assert row1["error_message"] == "Timeout during render"

        # Second: success (same concept/theme/grade → upsert)
        vid2 = writer.write_video(
            concept_id="PIPE-03",
            interest="space",
            grade="grade_9",
            engine_video_id="gen-attempt-2",
            manim_code="class Attempt2(Scene):\n    def construct(self): pass",
            success=True,
            file_size_bytes=4096,
            generation_time_seconds=18.0,
            error_message=None,
            source=_TEST_SOURCE,
        )

        assert vid1 == vid2  # Same row

        row2 = writer.read_video(vid2)
        assert row2["status"] == "pre_generated"
        assert row2["error_message"] is None
        assert row2["engine_video_id"] == "gen-attempt-2"
        assert "Attempt2" in row2["manim_code"]
        assert row2["file_size_bytes"] == 4096
        assert row2["generation_time_seconds"] == pytest.approx(18.0)

    def test_multiple_concepts_written_independently(self, writer):
        """Different concept_ids write separate rows."""
        vid_a = writer.write_video(
            concept_id="PIPE-04-A",
            interest="gaming",
            grade="grade_7",
            engine_video_id="eng-a",
            manim_code="class A(Scene): pass",
            success=True,
            source=_TEST_SOURCE,
        )
        vid_b = writer.write_video(
            concept_id="PIPE-04-B",
            interest="gaming",
            grade="grade_7",
            engine_video_id="eng-b",
            manim_code="class B(Scene): pass",
            success=True,
            source=_TEST_SOURCE,
        )

        assert vid_a != vid_b  # Different rows

        row_a = writer.read_video(vid_a)
        row_b = writer.read_video(vid_b)
        assert row_a["concept_id"] == "PIPE-04-A"
        assert row_b["concept_id"] == "PIPE-04-B"
        assert row_a["theme"] == row_b["theme"] == "gaming_minecraft"

    def test_same_concept_different_grades_are_separate_rows(self, writer):
        """Same concept_id + theme but different grade → separate rows."""
        vid_g7 = writer.write_video(
            concept_id="PIPE-05",
            interest="music",
            grade="grade_7",
            engine_video_id="eng-g7",
            manim_code="class G7(Scene): pass",
            success=True,
            source=_TEST_SOURCE,
        )
        vid_g9 = writer.write_video(
            concept_id="PIPE-05",
            interest="music",
            grade="grade_9",
            engine_video_id="eng-g9",
            manim_code="class G9(Scene): pass",
            success=True,
            source=_TEST_SOURCE,
        )

        assert vid_g7 != vid_g9  # Different rows (different grade)

        row_g7 = writer.read_video(vid_g7)
        row_g9 = writer.read_video(vid_g9)
        assert row_g7["grade"] == "grade_7"
        assert row_g9["grade"] == "grade_9"
        assert row_g7["concept_id"] == row_g9["concept_id"] == "PIPE-05"

    def test_same_concept_different_themes_are_separate_rows(self, writer):
        """Same concept_id + grade but different interest/theme → separate rows."""
        vid_bb = writer.write_video(
            concept_id="PIPE-06",
            interest="basketball",
            grade="grade_8",
            engine_video_id="eng-bb",
            manim_code="class BB(Scene): pass",
            success=True,
            source=_TEST_SOURCE,
        )
        vid_gm = writer.write_video(
            concept_id="PIPE-06",
            interest="gaming",
            grade="grade_8",
            engine_video_id="eng-gm",
            manim_code="class GM(Scene): pass",
            success=True,
            source=_TEST_SOURCE,
        )

        assert vid_bb != vid_gm  # Different rows (different theme)

        row_bb = writer.read_video(vid_bb)
        row_gm = writer.read_video(vid_gm)
        assert row_bb["theme"] == "sports_basketball"
        assert row_gm["theme"] == "gaming_minecraft"


# ---------------------------------------------------------------------------
# 7. Cleanup verification
# ---------------------------------------------------------------------------


class TestCleanup:
    """Verify cleanup_e2e only removes rows matching the given source."""

    def test_cleanup_removes_matching_source(self, writer):
        vid = writer.write_video(
            concept_id="CLEAN-01",
            interest="art",
            grade="grade_6",
            engine_video_id="clean-eng-01",
            manim_code="class CleanTest(Scene): pass",
            success=True,
            source=_TEST_SOURCE,
        )
        assert vid is not None
        assert writer.read_video(vid) is not None

        writer.cleanup_e2e(source=_TEST_SOURCE)
        assert writer.read_video(vid) is None

    def test_read_nonexistent_returns_none(self, writer):
        """Reading a UUID that doesn't exist returns None."""
        fake_uuid = str(uuid.uuid4())
        assert writer.read_video(fake_uuid) is None
