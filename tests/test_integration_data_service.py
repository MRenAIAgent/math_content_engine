"""
Integration tests for TutorDataServiceWriter → agentic_math_tutor data service.

Writes REAL data to **both** PostgreSQL and Neo4j, reads it back, verifies.
By default, test data is cleaned up after the run.

To keep data for manual inspection, pass --keep-data:
    pytest tests/test_integration_data_service.py -v --keep-data

Then inspect with:
    # PostgreSQL
    docker exec -i math_tutor_postgres psql -U math_tutor_app -d math_tutor \
        -c "SELECT concept_id, theme, grade, status, source, engine_video_id FROM videos ORDER BY created_at DESC;"

    # Neo4j
    docker exec -i math_tutor_neo4j cypher-shell -u neo4j -p local_dev_password \
        "MATCH (v:Video)-[r:DEMONSTRATES]->(c:Concept) RETURN v.engine_video_id, c.concept_id, v.source ORDER BY v.created_at DESC;"

Requires:
  - agentic_math_tutor PostgreSQL running (docker-compose up postgres)
  - agentic_math_tutor Neo4j running (docker-compose up neo4j)
  - TUTOR_DATABASE_URL or default localhost:15432
  - NEO4J_URI or default bolt://localhost:17687

Run with:
    pytest tests/test_integration_data_service.py -v
"""

import os
import uuid

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


# ---------------------------------------------------------------------------
# Fixtures — cleanup by default, skip cleanup with --keep-data
# ---------------------------------------------------------------------------


@pytest.fixture
def writer(request):
    """TutorDataServiceWriter pointed at local Docker PG.

    Cleans up rows with source='math_content_engine' after tests
    unless --keep-data is passed.
    """
    w = TutorDataServiceWriter()
    yield w
    if not request.config.getoption("--keep-data"):
        w.cleanup_e2e(source="math_content_engine")


# ---------------------------------------------------------------------------
# 1. Write → Read round-trip with real concept IDs
# ---------------------------------------------------------------------------


class TestWriteReadRoundTrip:
    """Write videos to tutor PG with real data, read back, verify every field."""

    def test_write_basketball_video_for_algebra(self, writer):
        """Write AT-001 basketball grade_7 video, read back all fields from PG and Neo4j."""
        engine_vid = str(uuid.uuid4())
        vid = writer.write_video(
            concept_id="AT-001",
            interest="basketball",
            grade="grade_7",
            engine_video_id=engine_vid,
            manim_code=(
                "from manim import *\n\n"
                "class BasketballAlgebraScene(Scene):\n"
                "    def construct(self):\n"
                "        title = Text('Solving Equations with Basketball Stats')\n"
                "        self.play(Write(title))\n"
                "        eq = MathTex('2x + 5 = 11')\n"
                "        self.play(FadeIn(eq))\n"
                "        self.wait()\n"
            ),
            success=True,
            file_size_bytes=524288,
            generation_time_seconds=45.2,
        )
        assert vid is not None

        # --- PostgreSQL verification ---
        row = writer.read_video(vid)
        assert row is not None
        assert row["concept_id"] == "AT-001"
        assert row["theme"] == "sports_basketball"
        assert row["grade"] == "grade_7"
        assert row["status"] == "pre_generated"
        assert row["source"] == "math_content_engine"
        assert row["engine_video_id"] == engine_vid
        assert row["gcs_path"] == f"engine/{engine_vid}.mp4"
        assert row["template_id"] == "personalized"
        assert "BasketballAlgebraScene" in row["manim_code"]
        assert row["file_size_bytes"] == 524288
        assert row["generation_time_seconds"] == pytest.approx(45.2)
        assert row["error_message"] is None
        assert row["created_at"] is not None
        assert row["updated_at"] is not None

        # --- Neo4j verification ---
        neo = writer.read_neo4j_video(engine_vid)
        assert neo is not None, "Video node not found in Neo4j"
        assert neo["concept_id"] == "AT-001"
        assert neo["theme"] == "sports_basketball"
        assert neo["grade"] == "grade_7"
        assert neo["status"] == "pre_generated"
        assert neo["source"] == "math_content_engine"
        assert neo["demonstrates_concept"] == "AT-001"
        assert neo["demonstrates_props"]["is_primary"] is True

    def test_write_gaming_video_for_fractions(self, writer):
        """Write LF-001 gaming grade_6 video, read back and verify."""
        engine_vid = str(uuid.uuid4())
        vid = writer.write_video(
            concept_id="LF-001",
            interest="gaming",
            grade="grade_6",
            engine_video_id=engine_vid,
            manim_code=(
                "from manim import *\n\n"
                "class MinecraftFractionsScene(Scene):\n"
                "    def construct(self):\n"
                "        title = Text('Fractions in Minecraft')\n"
                "        self.play(Write(title))\n"
                "        frac = MathTex(r'\\frac{3}{4}')\n"
                "        self.play(FadeIn(frac))\n"
                "        self.wait()\n"
            ),
            success=True,
            file_size_bytes=612000,
            generation_time_seconds=38.7,
        )

        row = writer.read_video(vid)
        assert row is not None
        assert row["concept_id"] == "LF-001"
        assert row["theme"] == "gaming_minecraft"
        assert row["grade"] == "grade_6"
        assert row["status"] == "pre_generated"
        assert row["source"] == "math_content_engine"
        assert "MinecraftFractionsScene" in row["manim_code"]

    def test_write_space_video_for_number_systems(self, writer):
        """Write NS-001 space grade_8 video, read back and verify."""
        engine_vid = str(uuid.uuid4())
        vid = writer.write_video(
            concept_id="NS-001",
            interest="space",
            grade="grade_8",
            engine_video_id=engine_vid,
            manim_code=(
                "from manim import *\n\n"
                "class SpaceNumbersScene(Scene):\n"
                "    def construct(self):\n"
                "        title = Text('Number Systems in Space')\n"
                "        self.play(Write(title))\n"
                "        self.wait()\n"
            ),
            success=True,
            file_size_bytes=480000,
            generation_time_seconds=32.1,
        )

        row = writer.read_video(vid)
        assert row is not None
        assert row["concept_id"] == "NS-001"
        assert row["theme"] == "nature_space"
        assert row["grade"] == "grade_8"
        assert row["status"] == "pre_generated"
        assert row["source"] == "math_content_engine"

    def test_write_neutral_video_for_quadratics(self, writer):
        """Write Q-001 neutral (no interest) grade_9 video."""
        engine_vid = str(uuid.uuid4())
        vid = writer.write_video(
            concept_id="Q-001",
            interest=None,
            grade="grade_9",
            engine_video_id=engine_vid,
            manim_code=(
                "from manim import *\n\n"
                "class QuadraticsScene(Scene):\n"
                "    def construct(self):\n"
                "        eq = MathTex('ax^2 + bx + c = 0')\n"
                "        self.play(Write(eq))\n"
                "        self.wait()\n"
            ),
            success=True,
            file_size_bytes=390000,
            generation_time_seconds=28.5,
        )

        row = writer.read_video(vid)
        assert row is not None
        assert row["concept_id"] == "Q-001"
        assert row["theme"] == "neutral"
        assert row["grade"] == "grade_9"
        assert row["source"] == "math_content_engine"

    def test_write_failed_video_with_error_message(self, writer):
        """Write a failed generation — status='failed', error_message persists."""
        engine_vid = str(uuid.uuid4())
        vid = writer.write_video(
            concept_id="AT-001",
            interest="soccer",
            grade="grade_8",
            engine_video_id=engine_vid,
            manim_code="class BrokenScene(Scene): ...",
            success=False,
            error_message="Manim render failed: LaTeX not found",
            generation_time_seconds=5.0,
        )

        row = writer.read_video(vid)
        assert row is not None
        assert row["concept_id"] == "AT-001"
        assert row["theme"] == "sports_soccer"
        assert row["grade"] == "grade_8"
        assert row["status"] == "failed"
        assert row["error_message"] == "Manim render failed: LaTeX not found"
        assert row["source"] == "math_content_engine"


# ---------------------------------------------------------------------------
# 2. Upsert — re-generation updates, not crashes
# ---------------------------------------------------------------------------


class TestUpsertBehaviour:
    """Re-generating same concept/theme/grade updates the existing row."""

    def test_upsert_returns_same_uuid(self, writer):
        """Two writes for same (concept_id, theme, grade) return the same row id."""
        first = writer.write_video(
            concept_id="AT-001",
            interest="music",
            grade="grade_7",
            engine_video_id="gen-v1",
            manim_code="class V1(Scene): pass",
            success=True,
        )
        second = writer.write_video(
            concept_id="AT-001",
            interest="music",
            grade="grade_7",
            engine_video_id="gen-v2",
            manim_code="class V2(Scene): pass",
            success=True,
        )
        assert first == second  # Same PG row

    def test_upsert_updates_fields_on_regen(self, writer):
        """After upsert, row reflects the latest write's data."""
        writer.write_video(
            concept_id="LF-001",
            interest="music",
            grade="grade_8",
            engine_video_id="old-id",
            manim_code="class OldVersion(Scene): pass",
            success=False,
            error_message="first attempt failed",
            file_size_bytes=100,
            generation_time_seconds=5.0,
        )
        vid = writer.write_video(
            concept_id="LF-001",
            interest="music",
            grade="grade_8",
            engine_video_id="new-id",
            manim_code="class NewVersion(Scene):\n    def construct(self): pass",
            success=True,
            error_message=None,
            file_size_bytes=512000,
            generation_time_seconds=40.0,
        )

        row = writer.read_video(vid)
        assert row["engine_video_id"] == "new-id"
        assert "NewVersion" in row["manim_code"]
        assert row["status"] == "pre_generated"
        assert row["error_message"] is None
        assert row["file_size_bytes"] == 512000
        assert row["generation_time_seconds"] == pytest.approx(40.0)

    def test_failed_then_success_clears_error(self, writer):
        """Failed gen followed by successful re-gen clears error_message."""
        writer.write_video(
            concept_id="NS-001",
            interest="robots",
            grade="grade_7",
            engine_video_id="attempt-1",
            manim_code="class Broken(Scene): ...",
            success=False,
            error_message="Timeout during render",
        )
        vid = writer.write_video(
            concept_id="NS-001",
            interest="robots",
            grade="grade_7",
            engine_video_id="attempt-2",
            manim_code="class Fixed(Scene):\n    def construct(self): pass",
            success=True,
            error_message=None,
        )

        row = writer.read_video(vid)
        assert row["status"] == "pre_generated"
        assert row["error_message"] is None
        assert row["engine_video_id"] == "attempt-2"


# ---------------------------------------------------------------------------
# 3. Different concept/theme/grade combos → separate rows
# ---------------------------------------------------------------------------


class TestSeparateRows:
    """Verify the UNIQUE (concept_id, theme, grade) constraint creates separate rows correctly."""

    def test_same_concept_different_themes(self, writer):
        """AT-001 basketball vs AT-001 gaming → two separate rows."""
        vid_bb = writer.write_video(
            concept_id="AT-001",
            interest="basketball",
            grade="grade_8",
            engine_video_id="at001-bb-g8",
            manim_code="class BasketballVersion(Scene): pass",
            success=True,
        )
        vid_gm = writer.write_video(
            concept_id="AT-001",
            interest="gaming",
            grade="grade_8",
            engine_video_id="at001-gm-g8",
            manim_code="class GamingVersion(Scene): pass",
            success=True,
        )

        assert vid_bb != vid_gm

        row_bb = writer.read_video(vid_bb)
        row_gm = writer.read_video(vid_gm)
        assert row_bb["theme"] == "sports_basketball"
        assert row_gm["theme"] == "gaming_minecraft"
        assert row_bb["concept_id"] == row_gm["concept_id"] == "AT-001"

    def test_same_concept_different_grades(self, writer):
        """LF-001 basketball grade_7 vs grade_9 → two separate rows."""
        vid_g7 = writer.write_video(
            concept_id="LF-001",
            interest="basketball",
            grade="grade_7",
            engine_video_id="lf001-bb-g7",
            manim_code="class Grade7(Scene): pass",
            success=True,
        )
        vid_g9 = writer.write_video(
            concept_id="LF-001",
            interest="basketball",
            grade="grade_9",
            engine_video_id="lf001-bb-g9",
            manim_code="class Grade9(Scene): pass",
            success=True,
        )

        assert vid_g7 != vid_g9

        row_g7 = writer.read_video(vid_g7)
        row_g9 = writer.read_video(vid_g9)
        assert row_g7["grade"] == "grade_7"
        assert row_g9["grade"] == "grade_9"

    def test_different_concepts_same_theme_grade(self, writer):
        """AT-001 vs NS-001 both basketball grade_8 → two separate rows."""
        vid_at = writer.write_video(
            concept_id="AT-001",
            interest="basketball",
            grade="grade_9",
            engine_video_id="at-bb-g9",
            manim_code="class Algebra(Scene): pass",
            success=True,
        )
        vid_ns = writer.write_video(
            concept_id="NS-001",
            interest="basketball",
            grade="grade_9",
            engine_video_id="ns-bb-g9",
            manim_code="class NumberSystems(Scene): pass",
            success=True,
        )

        assert vid_at != vid_ns

        row_at = writer.read_video(vid_at)
        row_ns = writer.read_video(vid_ns)
        assert row_at["concept_id"] == "AT-001"
        assert row_ns["concept_id"] == "NS-001"
        assert row_at["theme"] == row_ns["theme"] == "sports_basketball"


# ---------------------------------------------------------------------------
# 4. All interest/theme combinations persisted
# ---------------------------------------------------------------------------


class TestAllThemes:
    """Write a video for each interest, verify correct theme persists in PG."""

    @pytest.mark.parametrize(
        "interest,expected_theme",
        list(INTEREST_TO_THEME.items()),
    )
    def test_interest_persists_as_correct_theme(self, writer, interest, expected_theme):
        vid = writer.write_video(
            concept_id="AT-001",
            interest=interest,
            grade="grade_10",
            engine_video_id=f"theme-test-{interest}",
            manim_code=f"class {interest.title().replace('_','')}Scene(Scene): pass",
            success=True,
        )
        row = writer.read_video(vid)
        assert row["theme"] == expected_theme
        assert row["source"] == "math_content_engine"


# ---------------------------------------------------------------------------
# 5. Mapping helpers (pure logic, no DB)
# ---------------------------------------------------------------------------


class TestMappingHelpers:
    """Verify interest→theme and grade normalisation."""

    def test_known_interests(self):
        assert map_interest_to_theme("basketball") == "sports_basketball"
        assert map_interest_to_theme("gaming") == "gaming_minecraft"
        assert map_interest_to_theme("space") == "nature_space"
        assert map_interest_to_theme("music") == "music_pop"

    def test_unknown_defaults_to_neutral(self):
        assert map_interest_to_theme("unknown") == "neutral"
        assert map_interest_to_theme(None) == "neutral"
        assert map_interest_to_theme("") == "neutral"

    def test_normalize_grade(self):
        assert normalize_grade("grade_8") == "grade_8"
        assert normalize_grade(None) == "grade_7"

    def test_read_nonexistent_returns_none(self, writer):
        """Reading a UUID that doesn't exist returns None."""
        fake_uuid = str(uuid.uuid4())
        assert writer.read_video(fake_uuid) is None


# ---------------------------------------------------------------------------
# 6. Neo4j — Video node + DEMONSTRATES relationship
# ---------------------------------------------------------------------------


class TestNeo4jVideoNode:
    """Verify Video nodes and DEMONSTRATES edges are created in Neo4j."""

    def test_video_node_created_in_neo4j(self, writer):
        """write_video creates a Video node in Neo4j with correct properties."""
        engine_vid = str(uuid.uuid4())
        writer.write_video(
            concept_id="AT-001",
            interest="basketball",
            grade="grade_7",
            engine_video_id=engine_vid,
            manim_code="class Neo4jTest(Scene): pass",
            success=True,
            generation_time_seconds=12.5,
        )

        neo = writer.read_neo4j_video(engine_vid)
        assert neo is not None, "Video node not found in Neo4j"
        assert neo["engine_video_id"] == engine_vid
        assert neo["concept_id"] == "AT-001"
        assert neo["theme"] == "sports_basketball"
        assert neo["grade"] == "grade_7"
        assert neo["status"] == "pre_generated"
        assert neo["source"] == "math_content_engine"
        assert neo["generation_time_seconds"] == pytest.approx(12.5)

    def test_demonstrates_relationship_created(self, writer):
        """write_video creates a DEMONSTRATES edge from Video → Concept."""
        engine_vid = str(uuid.uuid4())
        writer.write_video(
            concept_id="LF-001",
            interest="gaming",
            grade="grade_6",
            engine_video_id=engine_vid,
            manim_code="class DemoRelTest(Scene): pass",
            success=True,
        )

        neo = writer.read_neo4j_video(engine_vid)
        assert neo is not None
        assert neo["demonstrates_concept"] == "LF-001"
        assert neo["demonstrates_props"]["is_primary"] is True
        assert neo["demonstrates_props"]["demonstration_type"] == "step_by_step"

    def test_neo4j_video_merge_on_regen(self, writer):
        """Re-generating same engine_video_id merges (updates) the Video node."""
        engine_vid = "neo4j-merge-test"
        writer.write_video(
            concept_id="NS-001",
            interest="space",
            grade="grade_8",
            engine_video_id=engine_vid,
            manim_code="class V1(Scene): pass",
            success=False,
        )
        writer.write_video(
            concept_id="NS-001",
            interest="space",
            grade="grade_8",
            engine_video_id=engine_vid,
            manim_code="class V2(Scene): pass",
            success=True,
        )

        neo = writer.read_neo4j_video(engine_vid)
        assert neo is not None
        # After merge, status should be the latest write
        assert neo["status"] == "pre_generated"

    def test_failed_video_node_in_neo4j(self, writer):
        """Failed generation still creates a Video node with status='failed'."""
        engine_vid = str(uuid.uuid4())
        writer.write_video(
            concept_id="Q-001",
            interest=None,
            grade="grade_9",
            engine_video_id=engine_vid,
            manim_code="class Broken(Scene): ...",
            success=False,
            error_message="LaTeX not found",
        )

        neo = writer.read_neo4j_video(engine_vid)
        assert neo is not None
        assert neo["status"] == "failed"
        assert neo["demonstrates_concept"] == "Q-001"

    def test_neo4j_read_nonexistent_returns_none(self, writer):
        """Reading a non-existent engine_video_id returns None."""
        assert writer.read_neo4j_video("does-not-exist") is None
