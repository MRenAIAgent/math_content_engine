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
from unittest.mock import Mock, patch

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


class TestEnginePipelineToDataService:
    """
    Run the engine.generate() pipeline with mocked LLM and renderer,
    but REAL tutor PG writes. Verifies the full flow end-to-end.
    """

    SAMPLE_CODE = '''
from manim import *

class IntegrationTestScene(Scene):
    def construct(self):
        title = Text("Integration Test")
        self.play(Write(title))
        self.wait()
'''

    @patch("math_content_engine.engine.create_llm_client")
    @patch("math_content_engine.engine.ManimRenderer")
    def test_engine_generate_writes_to_tutor_pg(
        self, mock_renderer_class, mock_create_client, writer, tmp_path
    ):
        """engine.generate() → tutor PG write → read back and verify."""
        from math_content_engine import MathContentEngine, Config
        from math_content_engine.llm.base import LLMResponse
        from math_content_engine.renderer.manim_renderer import RenderResult

        # Mock LLM
        mock_client = Mock()
        mock_client.generate.return_value = LLMResponse(
            content=f"```python\n{self.SAMPLE_CODE}\n```",
            model="claude-sonnet-4-20250514",
            usage={"input_tokens": 100, "output_tokens": 200},
        )
        mock_create_client.return_value = mock_client

        # Mock renderer
        fake_video = tmp_path / "output" / "IntegrationTestScene.mp4"
        fake_video.parent.mkdir(parents=True, exist_ok=True)
        fake_video.write_bytes(b"\x00" * 2048)

        mock_renderer = Mock()
        mock_renderer.render.return_value = RenderResult(
            success=True, output_path=fake_video, render_time=3.0,
        )
        mock_renderer_class.return_value = mock_renderer

        # Create engine with REAL tutor_writer (test source for cleanup)
        real_writer = TutorDataServiceWriter()
        config = Config()
        config.output_dir = tmp_path / "output"

        engine = MathContentEngine(
            config=config,
            interest="basketball",
            tutor_writer=real_writer,
        )

        result = engine.generate(
            topic="Test integration pipeline",
            interest="basketball",
            save_to_storage=True,
            concept_ids=["PIPE-01"],
            grade="grade_8",
        )

        # Pipeline should succeed
        assert result.success
        assert result.engine_video_id is not None
        assert result.tutor_video_id is not None

        # Read back from tutor PG and verify
        row = real_writer.read_video(result.tutor_video_id)
        assert row is not None
        assert row["concept_id"] == "PIPE-01"
        assert row["theme"] == "sports_basketball"
        assert row["grade"] == "grade_8"
        assert row["status"] == "pre_generated"
        assert row["engine_video_id"] == result.engine_video_id
        assert "IntegrationTestScene" in row["manim_code"]
        assert row["file_size_bytes"] == 2048
        # generation_time_seconds may be None with mocked instant LLM (0ms)
        assert row["error_message"] is None

        # Cleanup
        real_writer.cleanup_e2e(source="math_content_engine")

    @patch("math_content_engine.engine.create_llm_client")
    @patch("math_content_engine.engine.ManimRenderer")
    def test_engine_generate_without_local_storage_still_writes_pg(
        self, mock_renderer_class, mock_create_client, writer, tmp_path
    ):
        """Even without local SQLite, the tutor PG write should succeed."""
        from math_content_engine import MathContentEngine, Config
        from math_content_engine.llm.base import LLMResponse
        from math_content_engine.renderer.manim_renderer import RenderResult

        mock_client = Mock()
        mock_client.generate.return_value = LLMResponse(
            content=f"```python\n{self.SAMPLE_CODE}\n```",
            model="claude-sonnet-4-20250514",
            usage={"input_tokens": 100, "output_tokens": 200},
        )
        mock_create_client.return_value = mock_client

        fake_video = tmp_path / "output" / "IntegrationTestScene.mp4"
        fake_video.parent.mkdir(parents=True, exist_ok=True)
        fake_video.write_bytes(b"\x00" * 1024)

        mock_renderer = Mock()
        mock_renderer.render.return_value = RenderResult(
            success=True, output_path=fake_video, render_time=1.5,
        )
        mock_renderer_class.return_value = mock_renderer

        real_writer = TutorDataServiceWriter()
        config = Config()
        config.output_dir = tmp_path / "output"

        engine = MathContentEngine(
            config=config,
            interest="space",
            storage=None,  # NO local storage
            tutor_writer=real_writer,
        )

        result = engine.generate(
            topic="Test no local storage",
            interest="space",
            save_to_storage=True,
            concept_ids=["PIPE-02"],
            grade="grade_9",
        )

        assert result.success
        assert result.video_id is None  # No local storage
        assert result.tutor_video_id is not None
        assert result.engine_video_id is not None

        row = real_writer.read_video(result.tutor_video_id)
        assert row is not None
        assert row["concept_id"] == "PIPE-02"
        assert row["theme"] == "nature_space"
        assert row["grade"] == "grade_9"
        assert row["engine_video_id"] == result.engine_video_id

        real_writer.cleanup_e2e(source="math_content_engine")

    @patch("math_content_engine.engine.create_llm_client")
    @patch("math_content_engine.engine.ManimRenderer")
    def test_engine_failed_generation_writes_error_to_pg(
        self, mock_renderer_class, mock_create_client, writer, tmp_path
    ):
        """Failed pipeline writes status='failed' and error_message to PG."""
        from math_content_engine import MathContentEngine, Config
        from math_content_engine.llm.base import LLMResponse
        from math_content_engine.renderer.manim_renderer import RenderResult

        mock_client = Mock()
        mock_client.generate.return_value = LLMResponse(
            content=f"```python\n{self.SAMPLE_CODE}\n```",
            model="claude-sonnet-4-20250514",
            usage={"input_tokens": 100, "output_tokens": 200},
        )
        mock_create_client.return_value = mock_client

        mock_renderer = Mock()
        mock_renderer.render.return_value = RenderResult(
            success=False, output_path=None, render_time=0.5,
            error_message="LaTeX compilation error",
        )
        mock_renderer_class.return_value = mock_renderer

        real_writer = TutorDataServiceWriter()
        config = Config()
        config.output_dir = tmp_path / "output"
        config.max_retries = 1

        engine = MathContentEngine(
            config=config,
            interest="cooking",
            storage=None,
            tutor_writer=real_writer,
        )

        result = engine.generate(
            topic="Test failed pipeline",
            interest="cooking",
            save_to_storage=True,
            concept_ids=["PIPE-03"],
            grade="grade_7",
        )

        assert not result.success
        assert result.tutor_video_id is not None

        row = real_writer.read_video(result.tutor_video_id)
        assert row is not None
        assert row["concept_id"] == "PIPE-03"
        assert row["theme"] == "food_cooking"
        assert row["status"] == "failed"
        assert row["error_message"] is not None

        real_writer.cleanup_e2e(source="math_content_engine")


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
