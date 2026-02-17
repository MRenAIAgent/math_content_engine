"""
E2E tests for Chapter 1.3 "General Equations" with basketball personalization.

This test module exercises the FULL pipeline:
  1. Parse chapter 1.3 content from the textbook markdown
  2. Personalize with basketball interest for student "Jordan"
  3. Store textbook chunks, exercises, personalized content, and video
     metadata in the data service (PostgreSQL + Neo4j) via TutorDataServiceWriter
  4. Store engagement profiles and video metadata locally (SQLite)
  5. Verify all stored data is correct and retrievable
  6. Test top features end-to-end for a basketball-interested user

Infrastructure required (all running in Docker):
  - PostgreSQL: postgresql://math_tutor_app:local_dev_password@localhost:15432/math_tutor
  - Neo4j:      bolt://localhost:17687  (neo4j / local_dev_password)
  - Redis:      localhost:16379
  - Local SQLite for EngagementStore and VideoStorage

Run with:
    pytest tests/test_e2e_chapter_1_3_basketball.py -m e2e -v
    pytest tests/test_e2e_chapter_1_3_basketball.py -v          # all tests
"""

import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
from unittest.mock import Mock, patch

import pytest

from math_content_engine import MathContentEngine, Config
from math_content_engine.api.storage import VideoStorage
from math_content_engine.config import LLMProvider, VideoQuality as ConfigVideoQuality
from math_content_engine.integration.schemas import (
    ContentEvent,
    ContentEventType,
    StudentContextDTO,
    VideoContentDTO,
)
from math_content_engine.integration.tutor_writer import (
    TutorDataServiceWriter,
    map_interest_to_theme,
)
from math_content_engine.personalization import (
    ContentPersonalizer,
    EngagementStore,
    StudentProfile,
    build_engagement_profile,
    get_interest_profile,
    list_available_interests,
    make_store_key,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

E2E_SOURCE = "e2e_ch13_basketball"
CONCEPT_ID = "algebra1.linear_equations.general_equations"
TEXTBOOK_ID = "beginning_intermediate_algebra"
GRADE = "grade_8"
INTEREST = "basketball"
THEME = "sports_basketball"

# Persistent local data directory for E2E artifacts
_E2E_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "e2e"

# Textbook file path
_TEXTBOOK_PATH = (
    Path(__file__).resolve().parent.parent
    / "curriculum"
    / "textbooks"
    / "beginning_intermediate_algebra.md"
)

# Chapter 1.3 line range (1-indexed, inclusive)
_CH13_START_LINE = 1384
_CH13_END_LINE = 1638


# ---------------------------------------------------------------------------
# Helper: extract chapter content from textbook
# ---------------------------------------------------------------------------

def _extract_chapter_1_3() -> str:
    """Read lines 1384-1638 from the textbook markdown file.

    Returns the raw text of Chapter 1.3 "General Equations" including
    theory, examples 59-68, and practice problems 1-50.
    """
    with open(_TEXTBOOK_PATH, "r", encoding="utf-8") as fh:
        all_lines = fh.readlines()
    # Convert to 0-indexed
    start = _CH13_START_LINE - 1
    end = _CH13_END_LINE  # exclusive upper bound gives line 1638 inclusive
    return "".join(all_lines[start:end])


# ---------------------------------------------------------------------------
# Chunk definitions for Chapter 1.3
# ---------------------------------------------------------------------------

CHUNK_DEFINITIONS = [
    {
        "chunk_id": "e2e_ch13_chunk_01",
        "title": "Distributive Property & Combining Terms",
        "content_type": "exposition_with_examples",
        "difficulty_level": "basic",
        "keywords": ["distributive property", "combining like terms", "parentheses"],
        "description": "Examples 59-60: Using distribution to clear parentheses, then solving as two-step equations.",
    },
    {
        "chunk_id": "e2e_ch13_chunk_02",
        "title": "Variables on Both Sides",
        "content_type": "exposition_with_examples",
        "difficulty_level": "intermediate",
        "keywords": ["variables both sides", "move variable term", "negative coefficients"],
        "description": "Examples 61-63: Moving variables to one side of the equation.",
    },
    {
        "chunk_id": "e2e_ch13_chunk_03",
        "title": "Combined Problems - Distribution & Variables on Both Sides",
        "content_type": "exposition_with_examples",
        "difficulty_level": "intermediate",
        "keywords": ["distribution", "variables both sides", "5-step process", "combined"],
        "description": "Examples 64-66: Combined use of distribution and gathering variables.",
    },
    {
        "chunk_id": "e2e_ch13_chunk_04",
        "title": "Special Cases - All Real Numbers & No Solution",
        "content_type": "exposition_with_examples",
        "difficulty_level": "advanced",
        "keywords": ["identity equation", "no solution", "all real numbers", "special cases"],
        "description": "Examples 67-68: When the variable cancels out — infinite solutions or contradiction.",
    },
]


# ---------------------------------------------------------------------------
# Exercise definitions (basketball-themed)
# ---------------------------------------------------------------------------

EXERCISE_DEFINITIONS = [
    {
        "exercise_id": "e2e_ch13_ex_01",
        "title": "Basketball Scoring Equation",
        "problem": (
            "During a basketball game, a player's total points can be modeled by "
            "the equation 2(-3a - 8) = 1, where 'a' represents the number of "
            "assists that led to bonus scoring plays. Solve for a."
        ),
        "solution": (
            "2(-3a - 8) = 1\n"
            "-6a - 16 = 1        Distribute 2 through parenthesis\n"
            "-6a = 17            Add 16 to both sides\n"
            "a = -17/6           Divide both sides by -6"
        ),
        "answer": "a = -17/6",
        "difficulty": 2,
        "hints": [
            "Start by distributing the 2 through the parentheses.",
            "After distributing, add 16 to both sides to isolate the variable term.",
            "Finally, divide both sides by -6.",
        ],
        "skill_tested": "procedural",
        "estimated_time_minutes": 5,
    },
    {
        "exercise_id": "e2e_ch13_ex_02",
        "title": "Three-Point Challenge",
        "problem": (
            "Stephen Curry's three-point practice session can be modeled by "
            "-5(-4 + 2v) = -50, where v is the number of made shots per set. "
            "How many three-pointers does he make per set?"
        ),
        "solution": (
            "-5(-4 + 2v) = -50\n"
            "20 - 10v = -50      Distribute -5\n"
            "-10v = -70           Subtract 20 from both sides\n"
            "v = 7                Divide both sides by -10"
        ),
        "answer": "v = 7",
        "difficulty": 2,
        "hints": [
            "Distribute -5 across the parentheses carefully — watch the signs.",
            "Subtract 20 from both sides to get the variable term alone.",
            "Divide by -10 to find v.",
        ],
        "skill_tested": "procedural",
        "estimated_time_minutes": 5,
    },
    {
        "exercise_id": "e2e_ch13_ex_03",
        "title": "Stats Comparison - Variables on Both Sides",
        "problem": (
            "Two basketball players are compared: Player A's scoring trend is "
            "-3x + 9 and Player B's is 6x - 27. Find the game number x where "
            "they score equally: -3x + 9 = 6x - 27."
        ),
        "solution": (
            "-3x + 9 = 6x - 27\n"
            "+3x      +3x           Add 3x to both sides\n"
            "9 = 9x - 27            Simplify\n"
            "+27     +27             Add 27 to both sides\n"
            "36 = 9x                 Simplify\n"
            "x = 4                   Divide both sides by 9"
        ),
        "answer": "x = 4",
        "difficulty": 3,
        "hints": [
            "Move the smaller variable term to the other side.",
            "Add 3x to both sides to collect variables on the right.",
            "Then add 27 to both sides and divide by 9.",
        ],
        "skill_tested": "procedural",
        "estimated_time_minutes": 7,
    },
    {
        "exercise_id": "e2e_ch13_ex_04",
        "title": "Season Scoring Equation",
        "problem": (
            "A basketball team's season scoring model uses distribution and "
            "variables on both sides: 4(2x - 6) + 9 = 3(x - 7) + 8x. "
            "Solve for x to find the key performance metric."
        ),
        "solution": (
            "4(2x - 6) + 9 = 3(x - 7) + 8x      Distribute 4 and 3\n"
            "8x - 24 + 9 = 3x - 21 + 8x          Combine like terms\n"
            "8x - 15 = 11x - 21                    Simplify both sides\n"
            "-8x      -8x                           Subtract 8x from both sides\n"
            "-15 = 3x - 21                          Simplify\n"
            "+21      +21                            Add 21 to both sides\n"
            "6 = 3x                                 Simplify\n"
            "x = 2                                  Divide both sides by 3"
        ),
        "answer": "x = 2",
        "difficulty": 4,
        "hints": [
            "Distribute 4 and 3 through their respective parentheses first.",
            "Combine like terms on each side before moving variables.",
            "Move the smaller variable term to the other side, then solve the two-step equation.",
        ],
        "skill_tested": "procedural",
        "estimated_time_minutes": 10,
    },
]


# ===================================================================
# Test Class: TestChapter13BasketballPipeline
# ===================================================================


class TestChapter13BasketballPipeline:
    """
    E2E pipeline tests for Chapter 1.3 "General Equations" with basketball
    personalization.

    The test class exercises:
      - Textbook content extraction
      - Basketball personalization and engagement profiles
      - Data service writes (PostgreSQL + Neo4j) for chunks, exercises,
        videos, and personalized content
      - Local SQLite writes for engagement and video storage
      - Top-feature verification for a basketball-interested user
    """

    # ------------------------------------------------------------------
    # Fixtures
    # ------------------------------------------------------------------

    @pytest.fixture(autouse=True)
    def _ensure_data_dir(self):
        """Create the persistent e2e data directory."""
        _E2E_DATA_DIR.mkdir(parents=True, exist_ok=True)

    @pytest.fixture
    def chapter_1_3_content(self) -> str:
        """Extract Chapter 1.3 text (lines 1384-1638) from the textbook."""
        return _extract_chapter_1_3()

    @pytest.fixture
    def basketball_student(self) -> StudentProfile:
        """Sample basketball fan student."""
        return StudentProfile(
            name="Jordan",
            preferred_address="J",
            grade_level="8th grade",
            favorite_figure="Stephen Curry",
            favorite_team="Warriors",
        )

    @pytest.fixture
    def tutor_writer(self):
        """TutorDataServiceWriter pointed at local Docker PG + Neo4j.

        Cleans up all rows written with source="e2e_ch13_basketball" at
        teardown.
        """
        writer = TutorDataServiceWriter(
            database_url="postgresql://math_tutor_app:local_dev_password@localhost:15432/math_tutor",
            neo4j_uri="bolt://localhost:17687",
            neo4j_user="neo4j",
            neo4j_password="local_dev_password",
        )
        yield writer
        writer.cleanup_e2e(source=E2E_SOURCE)

    @pytest.fixture
    def local_engagement_store(self) -> EngagementStore:
        """Local SQLite engagement store in data/e2e/."""
        return EngagementStore(db_path=_E2E_DATA_DIR / "engagement.db")

    @pytest.fixture
    def local_video_storage(self) -> VideoStorage:
        """Local SQLite video storage in data/e2e/."""
        return VideoStorage(db_path=_E2E_DATA_DIR / "videos.db")

    @pytest.fixture
    def basketball_personalizer(self) -> ContentPersonalizer:
        """ContentPersonalizer configured for basketball."""
        return ContentPersonalizer("basketball")

    # ------------------------------------------------------------------
    # Test 1: Content extraction
    # ------------------------------------------------------------------

    def test_extract_chapter_content(self, chapter_1_3_content: str):
        """Verify chapter 1.3 content is extracted correctly from the textbook.

        Checks that the raw text contains:
          - The chapter heading "General Equations"
          - Key math topics: distributive property, examples with equations
          - Practice problems section
        """
        content = chapter_1_3_content

        # Chapter heading
        assert "General Equations" in content, (
            "Chapter 1.3 heading 'General Equations' not found in extracted content"
        )

        # Objective statement
        assert "Solve general linear equations" in content

        # Key mathematical content
        assert "distributive property" in content.lower(), (
            "Distributive property not mentioned in chapter content"
        )
        assert "variables on both sides" in content.lower() or "variable on both sides" in content.lower(), (
            "Variables on both sides topic not found"
        )

        # Examples are present
        assert "Example 59" in content
        assert "Example 60" in content
        assert "Example 67" in content
        assert "Example 68" in content

        # Key equations from examples
        assert "4(2x" in content, "Example 59 equation not found"
        assert "all real numbers" in content.lower() or "R" in content, (
            "Special case 'all real numbers' not found"
        )
        assert "no solution" in content.lower(), (
            "Special case 'no solution' not found"
        )

        # Practice problems section
        assert "Practice" in content, "Practice section not found"
        assert "3a" in content, "Practice problem 1 content not found"

        # Verify reasonable content length
        assert len(content) > 2000, (
            f"Content seems too short ({len(content)} chars) for a full chapter section"
        )

    # ------------------------------------------------------------------
    # Test 2: Basketball personalization
    # ------------------------------------------------------------------

    def test_personalize_chapter_with_basketball(
        self,
        basketball_student: StudentProfile,
        basketball_personalizer: ContentPersonalizer,
        local_engagement_store: EngagementStore,
    ):
        """Build engagement profile, store in SQLite, and verify personalization.

        Pipeline:
          1. Get basketball interest profile
          2. Build engagement profile with student "Jordan"
          3. Store in EngagementStore (SQLite)
          4. Use ContentPersonalizer.get_animation_personalization()
          5. Verify personalization context references basketball
          6. Verify engagement profile round-trips through SQLite
        """
        # 1. Interest profile
        interest_profile = get_interest_profile(INTEREST)
        assert interest_profile is not None, (
            f"Interest profile for '{INTEREST}' not found. "
            f"Available: {list_available_interests()}"
        )

        # 2. Build engagement profile
        ep = build_engagement_profile(interest_profile, basketball_student)
        assert ep["address"] == "J"
        assert ep["student_name"] == "Jordan"
        assert len(ep["scenarios"]) > 0
        assert len(ep["hooks"]) > 0
        assert len(ep["stats"]) > 0
        assert ep["current_season"] != ""

        # 3. Store in EngagementStore
        key = make_store_key(INTEREST, "Jordan")
        local_engagement_store.save(key, ep)

        # 4. Generate personalization context
        personalization_ctx = basketball_personalizer.get_animation_personalization(
            topic="solving general linear equations",
            student=basketball_student,
        )
        assert len(personalization_ctx) > 0, "Personalization context is empty"

        # 5. Verify basketball references in context
        ctx_lower = personalization_ctx.lower()
        assert "basketball" in ctx_lower or "curry" in ctx_lower or "warriors" in ctx_lower, (
            f"Personalization context does not reference basketball: {personalization_ctx[:200]}"
        )
        assert "J" in personalization_ctx or "Jordan" in personalization_ctx, (
            "Student address not found in personalization context"
        )
        assert "Stephen Curry" in personalization_ctx, (
            "Favorite figure 'Stephen Curry' not in personalization context"
        )

        # 6. Verify round-trip through SQLite
        loaded = local_engagement_store.load(key)
        assert loaded is not None, "Engagement profile not found in SQLite"
        assert loaded["address"] == ep["address"]
        assert loaded["student_name"] == ep["student_name"]
        assert loaded["scenarios"] == ep["scenarios"]
        assert loaded["hooks"] == ep["hooks"]
        assert loaded["stats"] == ep["stats"]
        assert loaded["current_season"] == ep["current_season"]
        assert loaded["favorite_label"] is not None
        assert "Stephen Curry" in loaded["favorite_label"]
        assert loaded["figures"] == ep["figures"]
        assert loaded["color_palette"] == ep["color_palette"]

    # ------------------------------------------------------------------
    # Test 3: Store textbook chunks in data service (PG + Neo4j)
    # ------------------------------------------------------------------

    @pytest.mark.e2e
    def test_store_textbook_chunks_in_data_service(
        self,
        chapter_1_3_content: str,
        tutor_writer: TutorDataServiceWriter,
    ):
        """Parse chapter 1.3 into 4 logical chunks and write to PG + Neo4j.

        Chunks:
          1. Distributive Property & Combining Terms (Examples 59-60)
          2. Variables on Both Sides (Examples 61-63)
          3. Combined Problems (Examples 64-66)
          4. Special Cases (Examples 67-68)

        Verifies each chunk is readable from PostgreSQL.
        """
        content = chapter_1_3_content

        # Split content into approximate chunks based on example boundaries
        chunk_contents = [
            # Chunk 1: beginning through Example 60
            content[:content.index("Example 61") if "Example 61" in content else len(content) // 4],
            # Chunk 2: Example 61 through Example 63
            content[
                content.index("Example 61") if "Example 61" in content else len(content) // 4:
                content.index("Example 64") if "Example 64" in content else len(content) // 2
            ],
            # Chunk 3: Example 64 through Example 66
            content[
                content.index("Example 64") if "Example 64" in content else len(content) // 2:
                content.index("Example 67") if "Example 67" in content else 3 * len(content) // 4
            ],
            # Chunk 4: Example 67 through end
            content[
                content.index("Example 67") if "Example 67" in content else 3 * len(content) // 4:
            ],
        ]

        written_ids = []
        for i, chunk_def in enumerate(CHUNK_DEFINITIONS):
            chunk_content = chunk_contents[i].strip()
            assert len(chunk_content) > 50, (
                f"Chunk {chunk_def['chunk_id']} is too short ({len(chunk_content)} chars)"
            )

            result_id = tutor_writer.write_textbook_chunk(
                chunk_id=chunk_def["chunk_id"],
                textbook_id=TEXTBOOK_ID,
                concept_id=CONCEPT_ID,
                content=chunk_content,
                content_type=chunk_def["content_type"],
                chapter=1,
                section=3,
                title=chunk_def["title"],
                keywords=chunk_def["keywords"],
                difficulty_level=chunk_def["difficulty_level"],
                source=E2E_SOURCE,
            )

            assert result_id is not None, (
                f"Failed to write chunk {chunk_def['chunk_id']} to PostgreSQL"
            )
            written_ids.append(result_id)
            logger.info(
                "Wrote textbook chunk %s -> PG id=%s", chunk_def["chunk_id"], result_id
            )

        # Verify all 4 chunks are in PG via direct async query
        assert len(written_ids) == 4, f"Expected 4 chunks written, got {len(written_ids)}"

        import asyncio
        import asyncpg

        async def _verify_chunks():
            conn = await asyncpg.connect(tutor_writer.database_url)
            try:
                for chunk_def in CHUNK_DEFINITIONS:
                    row = await conn.fetchrow(
                        "SELECT chunk_id, concept_id, title, chapter, section "
                        "FROM textbook_chunks WHERE chunk_id = $1",
                        chunk_def["chunk_id"],
                    )
                    assert row is not None, (
                        f"Chunk {chunk_def['chunk_id']} not found in PG"
                    )
                    assert row["concept_id"] == CONCEPT_ID
                    assert row["chapter"] == 1
                    assert row["section"] == 3
                    assert row["title"] == chunk_def["title"]
            finally:
                await conn.close()

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(_verify_chunks())
        finally:
            loop.close()

    # ------------------------------------------------------------------
    # Test 4: Store exercises in data service (PG + Neo4j)
    # ------------------------------------------------------------------

    @pytest.mark.e2e
    def test_store_exercises_in_data_service(
        self,
        tutor_writer: TutorDataServiceWriter,
    ):
        """Write 4 basketball-themed exercises to PG + Neo4j and verify.

        Exercises:
          1. Basketball Scoring Equation (distribution)
          2. Three-Point Challenge (distribution with negatives)
          3. Stats Comparison (variables on both sides)
          4. Season Scoring Equation (combined distribution + both sides)
        """
        written_ids = []
        for ex_def in EXERCISE_DEFINITIONS:
            result_id = tutor_writer.write_exercise(
                exercise_id=ex_def["exercise_id"],
                concept_id=CONCEPT_ID,
                title=ex_def["title"],
                problem=ex_def["problem"],
                solution=ex_def["solution"],
                answer=ex_def["answer"],
                difficulty=ex_def["difficulty"],
                hints=ex_def["hints"],
                theme=THEME,
                grade=GRADE,
                keywords=["general equations", "chapter 1.3", INTEREST],
                skill_tested=ex_def["skill_tested"],
                estimated_time_minutes=ex_def["estimated_time_minutes"],
                source=E2E_SOURCE,
            )

            assert result_id is not None, (
                f"Failed to write exercise {ex_def['exercise_id']} to PostgreSQL"
            )
            written_ids.append(result_id)
            logger.info(
                "Wrote exercise %s -> PG id=%s", ex_def["exercise_id"], result_id
            )

        assert len(written_ids) == 4, f"Expected 4 exercises written, got {len(written_ids)}"

        # Verify all 4 exercises in PG
        import asyncio
        import asyncpg

        async def _verify_exercises():
            conn = await asyncpg.connect(tutor_writer.database_url)
            try:
                for ex_def in EXERCISE_DEFINITIONS:
                    row = await conn.fetchrow(
                        "SELECT exercise_id, concept_id, title, theme, grade, difficulty "
                        "FROM exercises WHERE exercise_id = $1",
                        ex_def["exercise_id"],
                    )
                    assert row is not None, (
                        f"Exercise {ex_def['exercise_id']} not found in PG"
                    )
                    assert row["concept_id"] == CONCEPT_ID
                    assert row["theme"] == THEME
                    assert row["grade"] == GRADE
                    assert row["difficulty"] == ex_def["difficulty"]
            finally:
                await conn.close()

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(_verify_exercises())
        finally:
            loop.close()

    # ------------------------------------------------------------------
    # Test 5: Generate personalized video and store
    # ------------------------------------------------------------------

    @pytest.mark.e2e
    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"),
        reason="No API key configured — skipping real LLM generation",
    )
    def test_generate_personalized_video_and_store(
        self,
        basketball_student: StudentProfile,
        tutor_writer: TutorDataServiceWriter,
        local_video_storage: VideoStorage,
        tmp_path: Path,
    ):
        """Real LLM call: generate a basketball-personalized video for Ch 1.3.

        Pipeline:
          1. Create MathContentEngine with basketball interest
          2. Generate animation about distributive property
          3. Verify code is generated (contains 'from manim import')
          4. Verify stored in local VideoStorage (SQLite)
          5. Verify stored in tutor PostgreSQL (via tutor_writer.read_video)
          6. Verify Neo4j video node exists (via tutor_writer.read_neo4j_video)
        """
        engine = MathContentEngine(
            interest=INTEREST,
            storage=local_video_storage,
            tutor_writer=tutor_writer,
        )
        engine.config.output_dir = tmp_path / "output"
        engine.config.video_quality = ConfigVideoQuality.LOW

        result = engine.generate(
            topic="Solving general linear equations using distributive property",
            requirements=(
                "Use basketball statistics as context. "
                "Show step-by-step solution of 4(2x - 6) = 16 using basketball scoring analogy."
            ),
            audience_level="middle school",
            interest=INTEREST,
            student_profile=basketball_student,
            save_to_storage=True,
            concept_ids=[CONCEPT_ID],
            grade=GRADE,
        )

        # 1. Code must always be generated
        assert result.code is not None, "No code was generated"
        assert "from manim import" in result.code, (
            "Generated code does not contain 'from manim import'"
        )

        # 2. Verify in local VideoStorage
        assert result.video_id is not None, (
            "video_id must be set when save_to_storage=True and storage is configured"
        )
        stored_video = local_video_storage.get_by_id(result.video_id)
        assert stored_video is not None, "Video not found in local VideoStorage"
        assert stored_video.interest == INTEREST
        assert stored_video.concept_ids == [CONCEPT_ID]
        assert stored_video.grade == GRADE
        assert stored_video.code is not None
        assert len(stored_video.code) > 0

        # 3. Verify in tutor PostgreSQL
        assert result.tutor_video_id is not None, (
            "tutor_video_id must be set when tutor_writer is configured"
        )
        tutor_row = tutor_writer.read_video(result.tutor_video_id)
        assert tutor_row is not None, "Video row not found in tutor PostgreSQL"
        assert tutor_row["concept_id"] == CONCEPT_ID
        assert tutor_row["theme"] == THEME
        assert tutor_row["grade"] == GRADE
        assert tutor_row["engine_video_id"] == result.engine_video_id
        assert tutor_row["manim_code"] is not None
        assert len(tutor_row["manim_code"]) > 0

        # 4. Verify in Neo4j
        neo4j_video = tutor_writer.read_neo4j_video(result.engine_video_id)
        assert neo4j_video is not None, "Video node not found in Neo4j"
        assert neo4j_video["concept_id"] == CONCEPT_ID
        assert neo4j_video["demonstrates_concept"] == CONCEPT_ID

    # ------------------------------------------------------------------
    # Test 6: Store personalized content linking chunk to basketball version
    # ------------------------------------------------------------------

    @pytest.mark.e2e
    def test_store_personalized_content(
        self,
        tutor_writer: TutorDataServiceWriter,
    ):
        """Write a personalized content record linking a textbook chunk to
        its basketball-themed version and verify in PostgreSQL.
        """
        content_id = "e2e_ch13_pc_01"
        source_chunk_id = "e2e_ch13_chunk_01"

        # First ensure the source chunk exists so the FK is valid
        tutor_writer.write_textbook_chunk(
            chunk_id=source_chunk_id,
            textbook_id=TEXTBOOK_ID,
            concept_id=CONCEPT_ID,
            content="Placeholder content for distributive property section.",
            content_type="exposition_with_examples",
            chapter=1,
            section=3,
            title="Distributive Property & Combining Terms",
            keywords=["distributive property"],
            difficulty_level="basic",
            source=E2E_SOURCE,
        )

        # Write personalized content
        personalized_text = (
            "Imagine you are Stephen Curry at the free-throw line. "
            "Your points equation is 4(2x - 6) = 16. Just like breaking "
            "down a play, first distribute the 4 to get 8x - 24 = 16, "
            "then add 24 to both sides to get 8x = 40, and divide by 8 "
            "to find x = 5 -- that is your scoring target per quarter!"
        )

        result_id = tutor_writer.write_personalized_content(
            content_id=content_id,
            source_chunk_id=source_chunk_id,
            theme=THEME,
            grade=GRADE,
            personalized_content=personalized_text,
            original_content="4(2x - 6) = 16: Distribute 4, then solve two-step equation.",
            educational_integrity=0.95,
            engagement_score=0.88,
            personalization_method="llm",
            llm_model="claude-sonnet-4-20250514",
        )

        assert result_id is not None, "Failed to write personalized content to PG"

        # Verify via direct PG query
        import asyncio
        import asyncpg

        async def _verify_personalized():
            conn = await asyncpg.connect(tutor_writer.database_url)
            try:
                row = await conn.fetchrow(
                    "SELECT content_id, source_chunk_id, theme, grade, "
                    "educational_integrity, engagement_score "
                    "FROM personalized_content WHERE content_id = $1",
                    content_id,
                )
                assert row is not None, "Personalized content not found in PG"
                assert row["source_chunk_id"] == source_chunk_id
                assert row["theme"] == THEME
                assert row["grade"] == GRADE
                assert float(row["educational_integrity"]) == pytest.approx(0.95, abs=0.01)
                assert float(row["engagement_score"]) == pytest.approx(0.88, abs=0.01)
            finally:
                await conn.close()

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(_verify_personalized())
        finally:
            loop.close()

    # ------------------------------------------------------------------
    # Test 7: Show all stored data (summary/audit test)
    # ------------------------------------------------------------------

    @pytest.mark.e2e
    def test_show_all_stored_data(
        self,
        tutor_writer: TutorDataServiceWriter,
        local_engagement_store: EngagementStore,
        local_video_storage: VideoStorage,
        basketball_student: StudentProfile,
        chapter_1_3_content: str,
        caplog,
    ):
        """Query all stores and log a summary of stored data.

        This test populates data, then queries:
          - PG: count of chunks, exercises, videos, personalized_content
          - Neo4j: count of nodes and edges
          - Local SQLite: count of engagement profiles and video records
          - Redis: check for cached concept keys

        Asserts all counts are > 0.
        """
        # --- Populate data first ---

        # 1. Write a textbook chunk
        tutor_writer.write_textbook_chunk(
            chunk_id="e2e_ch13_audit_chunk",
            textbook_id=TEXTBOOK_ID,
            concept_id=CONCEPT_ID,
            content=chapter_1_3_content[:500],
            content_type="exposition",
            chapter=1,
            section=3,
            title="Chapter 1.3 Audit Chunk",
            keywords=["audit"],
            difficulty_level="basic",
            source=E2E_SOURCE,
        )

        # 2. Write an exercise
        tutor_writer.write_exercise(
            exercise_id="e2e_ch13_audit_ex",
            concept_id=CONCEPT_ID,
            title="Audit Exercise",
            problem="Solve 2x + 5 = 11",
            solution="2x = 6, x = 3",
            answer="x = 3",
            difficulty=2,
            theme=THEME,
            grade=GRADE,
            keywords=["audit"],
            source=E2E_SOURCE,
        )

        # 3. Write a video record
        #    Use a unique concept_id to avoid ON CONFLICT with rows from
        #    test_generate_personalized_video_and_store (whose source is
        #    'math_content_engine', not our E2E_SOURCE).  The PG upsert
        #    key is (concept_id, theme, grade); a collision would keep the
        #    old source value, making our count query return 0.
        tutor_writer.write_video(
            concept_id=f"{CONCEPT_ID}.audit",
            interest=INTEREST,
            grade=GRADE,
            engine_video_id="e2e-ch13-audit-video-id",
            manim_code="class AuditScene(Scene): pass",
            success=True,
            source=E2E_SOURCE,
        )

        # 3b. Write a personalized content record linked to the audit chunk
        tutor_writer.write_personalized_content(
            content_id="e2e_ch13_audit_pc",
            source_chunk_id="e2e_ch13_audit_chunk",
            theme=THEME,
            grade=GRADE,
            personalized_content="Basketball-themed version of general equations...",
            original_content=chapter_1_3_content[:300],
            educational_integrity=0.95,
            engagement_score=0.85,
            personalization_method="llm",
            llm_model="claude-sonnet-4-20250514",
        )

        # 4. Write engagement profile
        interest_profile = get_interest_profile(INTEREST)
        ep = build_engagement_profile(interest_profile, basketball_student)
        key = make_store_key(INTEREST, "Jordan")
        local_engagement_store.save(key, ep)

        # --- Query all stores ---
        import asyncio
        import asyncpg

        pg_counts = {}

        async def _count_pg():
            conn = await asyncpg.connect(tutor_writer.database_url)
            try:
                source_marker = f"_source:{E2E_SOURCE}"

                chunks = await conn.fetchval(
                    "SELECT count(*) FROM textbook_chunks WHERE $1 = ANY(keywords)",
                    source_marker,
                )
                exercises = await conn.fetchval(
                    "SELECT count(*) FROM exercises WHERE $1 = ANY(keywords)",
                    source_marker,
                )
                videos = await conn.fetchval(
                    "SELECT count(*) FROM videos WHERE source = $1",
                    E2E_SOURCE,
                )
                personalized = await conn.fetchval(
                    """SELECT count(*) FROM personalized_content
                       WHERE source_chunk_id IN (
                           SELECT chunk_id FROM textbook_chunks
                           WHERE $1 = ANY(keywords)
                       )""",
                    source_marker,
                )
                pg_counts["chunks"] = chunks
                pg_counts["exercises"] = exercises
                pg_counts["videos"] = videos
                pg_counts["personalized"] = personalized
            finally:
                await conn.close()

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(_count_pg())
        finally:
            loop.close()

        # Neo4j counts
        neo4j_counts = {"nodes": 0, "edges": 0}
        try:
            from neo4j import GraphDatabase

            driver = GraphDatabase.driver(
                "bolt://localhost:17687",
                auth=("neo4j", "local_dev_password"),
            )
            with driver.session() as session:
                result = session.run(
                    """
                    MATCH (n)
                    WHERE n.source = $source
                       OR (n:PersonalizedContent AND EXISTS {
                           MATCH (n)-[:PERSONALIZED_FROM]->(t:TextbookChunk {source: $source})
                       })
                    RETURN count(n) AS node_count
                    """,
                    source=E2E_SOURCE,
                )
                rec = result.single()
                neo4j_counts["nodes"] = rec["node_count"] if rec else 0

                result_edges = session.run(
                    """
                    MATCH (n {source: $source})-[r]->()
                    RETURN count(r) AS edge_count
                    """,
                    source=E2E_SOURCE,
                )
                rec_edges = result_edges.single()
                neo4j_counts["edges"] = rec_edges["edge_count"] if rec_edges else 0
            driver.close()
        except Exception as exc:
            logger.warning("Neo4j query failed (non-fatal): %s", exc)

        # Local SQLite counts
        engagement_profiles = local_engagement_store.list_profiles(limit=100)
        engagement_count = len(engagement_profiles)

        video_stats = local_video_storage.get_stats()
        video_count = video_stats.get("total_videos", 0)

        # Redis check (non-fatal)
        redis_key_count = 0
        try:
            import redis

            r = redis.Redis(host="localhost", port=16379, decode_responses=True)
            keys = r.keys("concept:*")
            redis_key_count = len(keys) if keys else 0
            r.close()
        except Exception as exc:
            logger.warning("Redis check failed (non-fatal): %s", exc)

        # --- Log summary ---
        with caplog.at_level(logging.INFO):
            logger.info("=" * 60)
            logger.info("E2E Data Audit Summary - Chapter 1.3 Basketball")
            logger.info("=" * 60)
            logger.info("PostgreSQL:")
            logger.info("  Textbook chunks:      %d", pg_counts.get("chunks", 0))
            logger.info("  Exercises:             %d", pg_counts.get("exercises", 0))
            logger.info("  Videos:                %d", pg_counts.get("videos", 0))
            logger.info("  Personalized content:  %d", pg_counts.get("personalized", 0))
            logger.info("Neo4j:")
            logger.info("  Nodes (source=%s):  %d", E2E_SOURCE, neo4j_counts["nodes"])
            logger.info("  Edges (source=%s):  %d", E2E_SOURCE, neo4j_counts["edges"])
            logger.info("Local SQLite:")
            logger.info("  Engagement profiles:   %d", engagement_count)
            logger.info("  Video records:         %d", video_count)
            logger.info("Redis:")
            logger.info("  Cached concept keys:   %d", redis_key_count)
            logger.info("=" * 60)

        # Assert at least our explicitly-written data exists
        assert pg_counts.get("chunks", 0) >= 1, "No textbook chunks found in PG"
        assert pg_counts.get("exercises", 0) >= 1, "No exercises found in PG"
        assert pg_counts.get("videos", 0) >= 1, "No videos found in PG"
        assert pg_counts.get("personalized", 0) >= 1, "No personalized content found in PG"
        assert neo4j_counts["nodes"] >= 1, "No Neo4j nodes found for our source"
        assert engagement_count >= 1, "No engagement profiles found in SQLite"

    # ------------------------------------------------------------------
    # Test 8: Top features with basketball user
    # ------------------------------------------------------------------

    @pytest.mark.e2e
    def test_top_features_with_basketball_user(
        self,
        basketball_student: StudentProfile,
        basketball_personalizer: ContentPersonalizer,
        tutor_writer: TutorDataServiceWriter,
        local_engagement_store: EngagementStore,
        local_video_storage: VideoStorage,
    ):
        """Verify top features end-to-end for a basketball-interested user.

        Sub-checks:
          1. Interest profile: get_interest_profile("basketball") returns
             a valid profile with scenarios, hooks, figures.
          2. Engagement store: basketball engagement profile is stored and
             retrievable from SQLite.
          3. Personalized content: personalizer generates basketball
             context for "general equations".
          4. Video generation: stored video has interest="basketball" and
             correct concept_ids.
          5. Exercise retrieval: stored exercises have
             theme="sports_basketball".
          6. Textbook chunks: stored chunks linked to correct concept.
          7. Data compatibility: VideoContentDTO can be constructed from
             stored video data.
          8. StudentContextDTO: can be built from basketball user profile.
        """
        # --- Setup: populate all stores ---

        # Write engagement profile
        interest_profile = get_interest_profile(INTEREST)
        ep = build_engagement_profile(interest_profile, basketball_student)
        eng_key = make_store_key(INTEREST, "Jordan")
        local_engagement_store.save(eng_key, ep)

        # Write a textbook chunk
        tutor_writer.write_textbook_chunk(
            chunk_id="e2e_ch13_feat_chunk",
            textbook_id=TEXTBOOK_ID,
            concept_id=CONCEPT_ID,
            content="General equations involve distributive property and variables on both sides.",
            content_type="exposition",
            chapter=1,
            section=3,
            title="General Equations Overview",
            keywords=["general equations", "distributive"],
            difficulty_level="basic",
            source=E2E_SOURCE,
        )

        # Write an exercise
        tutor_writer.write_exercise(
            exercise_id="e2e_ch13_feat_ex",
            concept_id=CONCEPT_ID,
            title="Feature Test Exercise",
            problem="Solve 4(2x - 6) = 16 using basketball context",
            solution="8x - 24 = 16, 8x = 40, x = 5",
            answer="x = 5",
            difficulty=2,
            theme=THEME,
            grade=GRADE,
            keywords=["general equations", INTEREST],
            source=E2E_SOURCE,
        )

        # Write a video record
        engine_vid_id = "e2e-ch13-feat-video"
        tutor_video_uuid = tutor_writer.write_video(
            concept_id=CONCEPT_ID,
            interest=INTEREST,
            grade=GRADE,
            engine_video_id=engine_vid_id,
            manim_code="from manim import *\nclass FeatScene(Scene):\n    def construct(self): pass",
            success=True,
            source=E2E_SOURCE,
        )

        # --- 1. Interest Profile ---
        assert interest_profile is not None
        assert len(interest_profile.example_scenarios) > 0, "No example scenarios"
        assert len(interest_profile.engagement_hooks) > 0, "No engagement hooks"
        assert len(interest_profile.famous_figures) > 0, "No famous figures"

        # --- 2. Engagement Store ---
        loaded_ep = local_engagement_store.load(eng_key)
        assert loaded_ep is not None, "Engagement profile not retrievable"
        assert loaded_ep["address"] == "J"
        assert loaded_ep["student_name"] == "Jordan"
        assert "Stephen Curry" in loaded_ep["favorite_label"]

        # --- 3. Personalized Content ---
        ctx = basketball_personalizer.get_animation_personalization(
            topic="general equations",
            student=basketball_student,
        )
        assert len(ctx) > 0
        assert "Stephen Curry" in ctx

        # --- 4. Video Generation ---
        assert tutor_video_uuid is not None
        tutor_row = tutor_writer.read_video(tutor_video_uuid)
        assert tutor_row is not None
        assert tutor_row["concept_id"] == CONCEPT_ID
        assert tutor_row["theme"] == THEME

        neo4j_video = tutor_writer.read_neo4j_video(engine_vid_id)
        assert neo4j_video is not None
        assert neo4j_video["demonstrates_concept"] == CONCEPT_ID

        # --- 5. Exercise Retrieval ---
        import asyncio
        import asyncpg

        async def _check_exercise():
            conn = await asyncpg.connect(tutor_writer.database_url)
            try:
                row = await conn.fetchrow(
                    "SELECT theme, grade FROM exercises WHERE exercise_id = $1",
                    "e2e_ch13_feat_ex",
                )
                assert row is not None, "Feature test exercise not found"
                assert row["theme"] == THEME
                assert row["grade"] == GRADE
            finally:
                await conn.close()

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(_check_exercise())
        finally:
            loop.close()

        # --- 6. Textbook Chunks ---
        async def _check_chunk():
            conn = await asyncpg.connect(tutor_writer.database_url)
            try:
                row = await conn.fetchrow(
                    "SELECT concept_id, chapter, section FROM textbook_chunks WHERE chunk_id = $1",
                    "e2e_ch13_feat_chunk",
                )
                assert row is not None, "Feature test chunk not found"
                assert row["concept_id"] == CONCEPT_ID
                assert row["chapter"] == 1
                assert row["section"] == 3
            finally:
                await conn.close()

        loop2 = asyncio.new_event_loop()
        try:
            loop2.run_until_complete(_check_chunk())
        finally:
            loop2.close()

        # --- 7. Data Compatibility: VideoContentDTO ---
        dto = VideoContentDTO(
            video_id=str(tutor_video_uuid),
            concept_ids=[CONCEPT_ID],
            topic="Solving general linear equations using distributive property",
            scene_name="FeatScene",
            theme=THEME,
            grade=GRADE,
            source_path=f"engine/{engine_vid_id}.mp4",
            code="from manim import *\nclass FeatScene(Scene):\n    def construct(self): pass",
            created_at=datetime.utcnow().isoformat(),
        )
        assert dto.video_id == str(tutor_video_uuid)
        assert dto.concept_ids == [CONCEPT_ID]
        assert dto.theme == THEME
        assert dto.grade == GRADE

        # --- 8. StudentContextDTO ---
        student_dto = StudentContextDTO(
            student_id="student-jordan-001",
            name="Jordan",
            grade_level=GRADE,
            theme=THEME,
            interests=[INTEREST, "gaming"],
            hobbies=["playing basketball"],
            learning_style="visual",
            preferred_pace="moderate",
            math_anxiety_level="low",
        )
        assert student_dto.name == "Jordan"
        assert student_dto.theme == THEME
        assert INTEREST in student_dto.interests

        # Verify we can reconstruct a StudentProfile from the DTO
        reconstructed = StudentProfile(
            name=student_dto.name,
            grade_level=student_dto.grade_level,
        )
        assert reconstructed.name == "Jordan"
        assert reconstructed.get_display_address() == "Jordan"
