"""
E2E tests for personalized content generation with local data service writes.

These tests exercise the full personalization → code generation → data service
pipeline, verifying that:
  1. Personalized content (engagement profiles) is correctly stored in the
     EngagementStore (SQLite).
  2. Generated animation metadata is correctly stored in VideoStorage (SQLite).
  3. The stored data is compatible with agentic_math_tutor's integration
     schemas (StudentContextDTO, VideoContentDTO, ContentTheme mappings).

Run with:
    pytest tests/test_e2e_personalized_data_service.py -m e2e -v
"""

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from math_content_engine import MathContentEngine, Config
from math_content_engine.api.models import (
    AnimationStyle,
    VideoCreate,
    VideoMetadata,
    VideoQuality,
    VideoSearchParams,
)
from math_content_engine.api.storage import VideoStorage
from math_content_engine.config import LLMProvider
from math_content_engine.config import VideoQuality as ConfigVideoQuality
from math_content_engine.generator.code_generator import GenerationResult, ManimCodeGenerator
from math_content_engine.integration.schemas import (
    ContentEvent,
    ContentEventType,
    StudentContextDTO,
    VideoContentDTO,
)
from math_content_engine.llm.base import LLMResponse
from math_content_engine.personalization import (
    ContentPersonalizer,
    EngagementStore,
    StudentProfile,
    build_engagement_profile,
    create_engagement_profile,
    get_interest_profile,
    has_student,
    list_available_interests,
    make_store_key,
)
from math_content_engine.renderer.manim_renderer import RenderResult
from math_content_engine.utils.validators import ValidationResult


# ---------------------------------------------------------------------------
# Sample Manim code for mock responses
# ---------------------------------------------------------------------------

PERSONALIZED_BASKETBALL_CODE = '''
from manim import *

class BasketballEquationsScene(Scene):
    def construct(self):
        title = Text("Solving Equations with Basketball Stats")
        self.play(Write(title))
        self.wait(0.5)

        equation = MathTex("2x + 5 = 11")
        self.play(FadeIn(equation))
        self.wait()

        solution = MathTex("x = 3")
        self.play(Transform(equation, solution))
        self.wait()
'''

PERSONALIZED_GAMING_CODE = '''
from manim import *

class GamingFractionsScene(Scene):
    def construct(self):
        title = Text("Understanding Fractions in Minecraft")
        self.play(Write(title))
        self.wait(0.5)

        fraction = MathTex(r"\\frac{3}{4}")
        self.play(FadeIn(fraction))
        self.wait()
'''


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def engagement_store(tmp_path: Path) -> EngagementStore:
    """Create a temporary engagement store for each test."""
    return EngagementStore(db_path=tmp_path / "test_engagement.db")


@pytest.fixture
def video_storage(tmp_path: Path) -> VideoStorage:
    """Create a temporary video storage for each test."""
    return VideoStorage(db_path=tmp_path / "test_videos.db")


@pytest.fixture
def mock_config(monkeypatch, tmp_path) -> Config:
    """Create a test configuration."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-for-e2e")
    monkeypatch.setenv("MATH_ENGINE_OUTPUT_DIR", str(tmp_path / "output"))
    monkeypatch.setenv("MATH_ENGINE_MANIM_CACHE", str(tmp_path / "cache"))
    return Config()


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client returning personalized basketball code."""
    client = Mock()
    client.generate.return_value = LLMResponse(
        content=f"```python\n{PERSONALIZED_BASKETBALL_CODE}\n```",
        model="claude-sonnet-4-20250514",
        usage={"input_tokens": 500, "output_tokens": 800},
    )
    return client


@pytest.fixture
def basketball_student() -> StudentProfile:
    """Sample basketball fan student."""
    return StudentProfile(
        name="Jordan",
        preferred_address="J",
        grade_level="8th grade",
        favorite_figure="Stephen Curry",
        favorite_team="Warriors",
    )


@pytest.fixture
def gaming_student() -> StudentProfile:
    """Sample gamer student."""
    return StudentProfile(
        name="Alex",
        preferred_address="Alex",
        grade_level="7th grade",
        favorite_figure="Technoblade",
        favorite_team=None,
    )


# ===================================================================
# Test Class 1: Engagement Profile → EngagementStore round-trip
# ===================================================================


class TestEngagementProfileDataService:
    """E2E: build engagement profiles from personalization and persist them."""

    def test_basketball_profile_stored_and_retrievable(
        self, engagement_store, basketball_student
    ):
        """Full pipeline: interest + student → engagement profile → SQLite → load."""
        interest_profile = get_interest_profile("basketball")
        assert interest_profile is not None

        # Build personalized engagement profile
        ep = build_engagement_profile(interest_profile, basketball_student)

        # Verify profile content before storage
        assert ep["address"] == "J"
        assert ep["student_name"] == "Jordan"
        assert has_student(ep)
        assert len(ep["scenarios"]) > 0
        assert len(ep["hooks"]) > 0
        assert len(ep["stats"]) > 0
        assert ep["current_season"] != ""

        # Persist to data service
        key = make_store_key("basketball", "Jordan")
        engagement_store.save(key, ep)

        # Retrieve and verify round-trip
        loaded = engagement_store.load(key)
        assert loaded is not None
        assert loaded["address"] == "J"
        assert loaded["student_name"] == "Jordan"
        assert loaded["scenarios"] == ep["scenarios"]
        assert loaded["hooks"] == ep["hooks"]
        assert loaded["stats"] == ep["stats"]
        assert loaded["current_season"] == ep["current_season"]
        assert loaded["favorite_label"] is not None
        assert "Stephen Curry" in loaded["favorite_label"]
        assert loaded["figures"] == ep["figures"]
        assert loaded["color_palette"] == ep["color_palette"]

    def test_multiple_students_same_interest(
        self, engagement_store, basketball_student, gaming_student
    ):
        """Multiple students with different interests are stored independently."""
        basketball_profile = get_interest_profile("basketball")
        gaming_profile = get_interest_profile("gaming")

        ep_basketball = build_engagement_profile(basketball_profile, basketball_student)
        ep_gaming = build_engagement_profile(gaming_profile, gaming_student)

        key_b = make_store_key("basketball", "Jordan")
        key_g = make_store_key("gaming", "Alex")

        engagement_store.save(key_b, ep_basketball)
        engagement_store.save(key_g, ep_gaming)

        # Both stored independently
        assert engagement_store.exists(key_b)
        assert engagement_store.exists(key_g)

        loaded_b = engagement_store.load(key_b)
        loaded_g = engagement_store.load(key_g)

        assert loaded_b["address"] == "J"
        assert loaded_g["address"] == "Alex"
        assert loaded_b["student_name"] == "Jordan"
        assert loaded_g["student_name"] == "Alex"

        # List shows both
        profiles = engagement_store.list_profiles(limit=10)
        assert len(profiles) == 2
        keys = {p["key"] for p in profiles}
        assert key_b in keys
        assert key_g in keys

    def test_anonymous_profile_stored(self, engagement_store):
        """Anonymous profile (no student) is stored with 'anonymous' key."""
        interest_profile = get_interest_profile("basketball")
        ep = build_engagement_profile(interest_profile, student=None)

        assert ep["address"] == "you"
        assert ep["student_name"] is None
        assert not has_student(ep)

        key = make_store_key("basketball")
        assert key == "anonymous:basketball"

        engagement_store.save(key, ep)
        loaded = engagement_store.load(key)
        assert loaded is not None
        assert loaded["address"] == "you"
        assert loaded["student_name"] is None

    def test_profile_update_overwrites(
        self, engagement_store, basketball_student
    ):
        """Updating a profile overwrites the previous version."""
        interest_profile = get_interest_profile("basketball")
        key = make_store_key("basketball", "Jordan")

        # Save initial
        ep_v1 = build_engagement_profile(interest_profile, basketball_student)
        engagement_store.save(key, ep_v1)

        # Update student preference and re-save
        updated_student = StudentProfile(
            name="Jordan",
            preferred_address="Champ",
            grade_level="9th grade",
            favorite_figure="LeBron James",
            favorite_team="Lakers",
        )
        ep_v2 = build_engagement_profile(interest_profile, updated_student)
        engagement_store.save(key, ep_v2)

        loaded = engagement_store.load(key)
        assert loaded["address"] == "Champ"
        assert "LeBron James" in loaded["favorite_label"]

    @pytest.mark.parametrize(
        "interest",
        ["basketball", "gaming", "music", "soccer", "space", "minecraft"],
    )
    def test_all_interests_produce_valid_storable_profiles(
        self, engagement_store, interest
    ):
        """Every supported interest produces a profile that round-trips through SQLite."""
        interest_profile = get_interest_profile(interest)
        if interest_profile is None:
            pytest.skip(f"Interest '{interest}' not available")

        ep = build_engagement_profile(interest_profile)
        key = make_store_key(interest)
        engagement_store.save(key, ep)

        loaded = engagement_store.load(key)
        assert loaded is not None
        assert isinstance(loaded["scenarios"], list)
        assert isinstance(loaded["hooks"], list)
        assert isinstance(loaded["stats"], dict)
        assert isinstance(loaded["figures"], list)

    def test_sqlite_schema_integrity(self, tmp_path):
        """Verify the SQLite schema is created correctly."""
        db_path = tmp_path / "schema_test.db"
        store = EngagementStore(db_path=db_path)

        conn = sqlite3.connect(db_path)
        cursor = conn.execute("PRAGMA table_info(engagement_profiles)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        conn.close()

        assert "key" in columns
        assert "data" in columns
        assert "created_at" in columns
        assert "updated_at" in columns


# ===================================================================
# Test Class 2: Personalized generation → VideoStorage round-trip
# ===================================================================


class TestPersonalizedGenerationDataService:
    """E2E: personalized code generation writes results to VideoStorage."""

    @patch("math_content_engine.engine.create_llm_client")
    @patch("math_content_engine.engine.ManimRenderer")
    def test_personalized_generation_writes_to_video_storage(
        self,
        mock_renderer_class,
        mock_create_client,
        mock_config,
        video_storage,
        basketball_student,
        tmp_path,
    ):
        """Generate personalized content and verify it's stored in VideoStorage."""
        # Setup mocks
        mock_client = Mock()
        mock_client.generate.return_value = LLMResponse(
            content=f"```python\n{PERSONALIZED_BASKETBALL_CODE}\n```",
            model="claude-sonnet-4-20250514",
            usage={"input_tokens": 500, "output_tokens": 800},
        )
        mock_create_client.return_value = mock_client

        fake_video = tmp_path / "output" / "BasketballEquationsScene.mp4"
        fake_video.parent.mkdir(parents=True, exist_ok=True)
        fake_video.write_bytes(b"\x00" * 1024)  # 1KB fake video

        mock_renderer = Mock()
        mock_renderer.render.return_value = RenderResult(
            success=True,
            output_path=fake_video,
            render_time=2.5,
        )
        mock_renderer_class.return_value = mock_renderer

        # Create engine WITH storage
        engine = MathContentEngine(
            config=mock_config,
            interest="basketball",
            storage=video_storage,
        )

        # Generate personalized content
        result = engine.generate(
            topic="Solving two-step equations",
            requirements="Use basketball statistics for examples",
            audience_level="middle school",
            interest="basketball",
            student_profile=basketball_student,
            save_to_storage=True,
            concept_ids=["AT-24"],
            grade="grade_8",
        )

        # Verify generation succeeded
        assert result.success
        assert result.video_id is not None

        # Verify data persisted in VideoStorage
        stored = video_storage.get_by_id(result.video_id)
        assert stored is not None
        assert stored.topic == "Solving two-step equations"
        assert stored.interest == "basketball"
        assert stored.concept_ids == ["AT-24"]
        assert stored.grade == "grade_8"
        assert stored.scene_name == "BasketballEquationsScene"
        assert stored.success is True
        assert stored.llm_provider == "claude"
        assert stored.llm_model is not None
        assert stored.generation_attempts >= 1
        assert stored.render_attempts >= 1
        assert stored.file_size_bytes == 1024

    @patch("math_content_engine.engine.create_llm_client")
    @patch("math_content_engine.engine.ManimRenderer")
    def test_failed_generation_also_stored(
        self,
        mock_renderer_class,
        mock_create_client,
        mock_config,
        video_storage,
        tmp_path,
    ):
        """Failed generations are also stored in VideoStorage for tracking."""
        mock_client = Mock()
        mock_client.generate.return_value = LLMResponse(
            content=f"```python\n{PERSONALIZED_BASKETBALL_CODE}\n```",
            model="claude-sonnet-4-20250514",
            usage={"input_tokens": 500, "output_tokens": 800},
        )
        mock_create_client.return_value = mock_client

        # Renderer always fails
        mock_renderer = Mock()
        mock_renderer.render.return_value = RenderResult(
            success=False,
            output_path=None,
            render_time=0.5,
            error_message="Manim render failed: LaTeX not found",
        )
        mock_renderer_class.return_value = mock_renderer

        # Also mock fix_code to prevent infinite loop
        mock_client.generate.return_value = LLMResponse(
            content=f"```python\n{PERSONALIZED_BASKETBALL_CODE}\n```",
            model="claude-sonnet-4-20250514",
            usage={"input_tokens": 500, "output_tokens": 800},
        )

        mock_config.max_retries = 1

        engine = MathContentEngine(
            config=mock_config,
            interest="basketball",
            storage=video_storage,
        )

        result = engine.generate(
            topic="Basketball fractions",
            interest="basketball",
            save_to_storage=True,
            concept_ids=["AT-24"],
            grade="grade_8",
        )

        assert not result.success
        assert result.video_id is not None

        stored = video_storage.get_by_id(result.video_id)
        assert stored is not None
        assert stored.success is False
        assert stored.error_message is not None
        assert stored.interest == "basketball"
        assert stored.concept_ids == ["AT-24"]

    @patch("math_content_engine.engine.create_llm_client")
    @patch("math_content_engine.engine.ManimRenderer")
    def test_video_storage_list_and_filter_by_interest(
        self,
        mock_renderer_class,
        mock_create_client,
        mock_config,
        video_storage,
        basketball_student,
        gaming_student,
        tmp_path,
    ):
        """Store multiple personalized videos and filter by interest."""
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        fake_video = tmp_path / "output" / "scene.mp4"
        fake_video.parent.mkdir(parents=True, exist_ok=True)
        fake_video.write_bytes(b"\x00" * 512)

        mock_renderer = Mock()
        mock_renderer.render.return_value = RenderResult(
            success=True, output_path=fake_video, render_time=1.0,
        )
        mock_renderer_class.return_value = mock_renderer

        # Generate basketball video
        mock_client.generate.return_value = LLMResponse(
            content=f"```python\n{PERSONALIZED_BASKETBALL_CODE}\n```",
            model="claude-sonnet-4-20250514",
            usage={},
        )

        engine = MathContentEngine(
            config=mock_config, interest="basketball", storage=video_storage,
        )
        result_b = engine.generate(
            topic="Basketball equations",
            interest="basketball",
            student_profile=basketball_student,
            concept_ids=["AT-24"],
            grade="grade_8",
        )

        # Generate gaming video
        mock_client.generate.return_value = LLMResponse(
            content=f"```python\n{PERSONALIZED_GAMING_CODE}\n```",
            model="claude-sonnet-4-20250514",
            usage={},
        )
        engine.set_interest("gaming")
        result_g = engine.generate(
            topic="Gaming fractions",
            interest="gaming",
            student_profile=gaming_student,
            concept_ids=["FR-10"],
            grade="grade_7",
        )

        assert result_b.success
        assert result_g.success

        # Filter by basketball
        params_b = VideoSearchParams(interest="basketball")
        videos_b, total_b = video_storage.list_videos(params_b)
        assert total_b == 1
        assert videos_b[0].interest == "basketball"
        assert videos_b[0].concept_ids == ["AT-24"]

        # Filter by gaming
        params_g = VideoSearchParams(interest="gaming")
        videos_g, total_g = video_storage.list_videos(params_g)
        assert total_g == 1
        assert videos_g[0].interest == "gaming"
        assert videos_g[0].concept_ids == ["FR-10"]

        # Stats
        stats = video_storage.get_stats()
        assert stats["total_videos"] == 2
        assert stats["successful_videos"] == 2
        assert stats["by_interest"]["basketball"] == 1
        assert stats["by_interest"]["gaming"] == 1


# ===================================================================
# Test Class 2b: Tutor PG integration (decoupled, upsert, error_message)
# ===================================================================


class TestTutorWriterIntegration:
    """Tests for tutor PG integration: decoupled writes, upsert, and error forwarding."""

    @patch("math_content_engine.engine.create_llm_client")
    @patch("math_content_engine.engine.ManimRenderer")
    def test_tutor_write_without_local_storage(
        self,
        mock_renderer_class,
        mock_create_client,
        mock_config,
        basketball_student,
        tmp_path,
    ):
        """Tutor PG write succeeds even when no local SQLite storage is configured."""
        mock_client = Mock()
        mock_client.generate.return_value = LLMResponse(
            content=f"```python\n{PERSONALIZED_BASKETBALL_CODE}\n```",
            model="claude-sonnet-4-20250514",
            usage={"input_tokens": 500, "output_tokens": 800},
        )
        mock_create_client.return_value = mock_client

        fake_video = tmp_path / "output" / "BasketballEquationsScene.mp4"
        fake_video.parent.mkdir(parents=True, exist_ok=True)
        fake_video.write_bytes(b"\x00" * 1024)

        mock_renderer = Mock()
        mock_renderer.render.return_value = RenderResult(
            success=True,
            output_path=fake_video,
            render_time=2.5,
        )
        mock_renderer_class.return_value = mock_renderer

        # Create a mock tutor_writer (no need for real PG in unit test)
        mock_tutor_writer = Mock()
        mock_tutor_writer.write_video.return_value = "fake-tutor-uuid"

        # Engine with tutor_writer but WITHOUT local storage
        engine = MathContentEngine(
            config=mock_config,
            interest="basketball",
            storage=None,
            tutor_writer=mock_tutor_writer,
        )

        result = engine.generate(
            topic="Solving two-step equations",
            interest="basketball",
            student_profile=basketball_student,
            save_to_storage=True,
            concept_ids=["AT-24"],
            grade="grade_8",
        )

        assert result.success
        assert result.video_id is None  # No local storage -> no video_id
        assert result.tutor_video_id == "fake-tutor-uuid"
        assert result.engine_video_id is not None  # UUID was generated independently

        # Verify tutor_writer.write_video was called with correct args
        mock_tutor_writer.write_video.assert_called_once()
        call_kwargs = mock_tutor_writer.write_video.call_args.kwargs
        assert call_kwargs["concept_id"] == "AT-24"
        assert call_kwargs["engine_video_id"] == result.engine_video_id
        assert call_kwargs["interest"] == "basketball"
        assert call_kwargs["grade"] == "grade_8"
        assert call_kwargs["success"] is True

    @patch("math_content_engine.engine.create_llm_client")
    @patch("math_content_engine.engine.ManimRenderer")
    def test_error_message_forwarded_to_tutor_writer(
        self,
        mock_renderer_class,
        mock_create_client,
        mock_config,
        tmp_path,
    ):
        """When generation fails, error_message is forwarded to tutor PG writer."""
        mock_client = Mock()
        mock_client.generate.return_value = LLMResponse(
            content=f"```python\n{PERSONALIZED_BASKETBALL_CODE}\n```",
            model="claude-sonnet-4-20250514",
            usage={"input_tokens": 500, "output_tokens": 800},
        )
        mock_create_client.return_value = mock_client

        mock_renderer = Mock()
        mock_renderer.render.return_value = RenderResult(
            success=False,
            output_path=None,
            render_time=0.5,
            error_message="Manim render failed: LaTeX not found",
        )
        mock_renderer_class.return_value = mock_renderer

        mock_config.max_retries = 1

        mock_tutor_writer = Mock()
        mock_tutor_writer.write_video.return_value = "fake-tutor-uuid"

        engine = MathContentEngine(
            config=mock_config,
            interest="basketball",
            tutor_writer=mock_tutor_writer,
        )

        result = engine.generate(
            topic="Basketball fractions",
            interest="basketball",
            save_to_storage=True,
            concept_ids=["AT-24"],
            grade="grade_8",
        )

        assert not result.success
        assert result.error_message is not None

        # Verify error_message was forwarded
        mock_tutor_writer.write_video.assert_called()
        call_kwargs = mock_tutor_writer.write_video.call_args.kwargs
        assert call_kwargs["error_message"] is not None
        assert call_kwargs["success"] is False

    @patch("math_content_engine.engine.create_llm_client")
    @patch("math_content_engine.engine.ManimRenderer")
    def test_engine_video_id_independent_of_local_storage(
        self,
        mock_renderer_class,
        mock_create_client,
        mock_config,
        video_storage,
        basketball_student,
        tmp_path,
    ):
        """engine_video_id is set independently and forwarded to both stores."""
        mock_client = Mock()
        mock_client.generate.return_value = LLMResponse(
            content=f"```python\n{PERSONALIZED_BASKETBALL_CODE}\n```",
            model="claude-sonnet-4-20250514",
            usage={"input_tokens": 500, "output_tokens": 800},
        )
        mock_create_client.return_value = mock_client

        fake_video = tmp_path / "output" / "BasketballEquationsScene.mp4"
        fake_video.parent.mkdir(parents=True, exist_ok=True)
        fake_video.write_bytes(b"\x00" * 1024)

        mock_renderer = Mock()
        mock_renderer.render.return_value = RenderResult(
            success=True,
            output_path=fake_video,
            render_time=2.5,
        )
        mock_renderer_class.return_value = mock_renderer

        mock_tutor_writer = Mock()
        mock_tutor_writer.write_video.return_value = "fake-tutor-uuid"

        # Engine with BOTH local storage AND tutor writer
        engine = MathContentEngine(
            config=mock_config,
            interest="basketball",
            storage=video_storage,
            tutor_writer=mock_tutor_writer,
        )

        result = engine.generate(
            topic="Solving two-step equations",
            interest="basketball",
            student_profile=basketball_student,
            save_to_storage=True,
            concept_ids=["AT-24"],
            grade="grade_8",
        )

        assert result.success
        assert result.video_id is not None  # Local storage ID
        assert result.engine_video_id is not None  # Independent UUID
        assert result.tutor_video_id == "fake-tutor-uuid"

        # engine_video_id should be different from local video_id
        assert result.engine_video_id != result.video_id

        # tutor_writer should have received engine_video_id (not video_id)
        call_kwargs = mock_tutor_writer.write_video.call_args.kwargs
        assert call_kwargs["engine_video_id"] == result.engine_video_id


# ===================================================================
# Test Class 3: Engagement + Video combined data service pipeline
# ===================================================================


class TestCombinedDataServicePipeline:
    """E2E: full pipeline storing both engagement profile AND video metadata."""

    @patch("math_content_engine.engine.create_llm_client")
    @patch("math_content_engine.engine.ManimRenderer")
    def test_full_personalized_pipeline_with_both_stores(
        self,
        mock_renderer_class,
        mock_create_client,
        mock_config,
        engagement_store,
        video_storage,
        basketball_student,
        tmp_path,
    ):
        """Complete pipeline: build profile → store engagement → generate → store video."""
        # --- Step 1: Build and persist engagement profile ---
        interest_profile = get_interest_profile("basketball")
        ep = build_engagement_profile(interest_profile, basketball_student)

        key = make_store_key("basketball", "Jordan")
        engagement_store.save(key, ep)

        # --- Step 2: Use personalizer to generate animation context ---
        personalizer = ContentPersonalizer("basketball")
        personalization_ctx = personalizer.get_animation_personalization(
            topic="solving two-step equations",
            student=basketball_student,
        )

        # Verify personalization context contains student data
        assert "J" in personalization_ctx or "Jordan" in personalization_ctx
        assert "Stephen Curry" in personalization_ctx

        # --- Step 3: Generate code with mocked LLM ---
        mock_client = Mock()
        mock_client.generate.return_value = LLMResponse(
            content=f"```python\n{PERSONALIZED_BASKETBALL_CODE}\n```",
            model="claude-sonnet-4-20250514",
            usage={"input_tokens": 600, "output_tokens": 900},
        )
        mock_create_client.return_value = mock_client

        fake_video = tmp_path / "output" / "BasketballEquationsScene.mp4"
        fake_video.parent.mkdir(parents=True, exist_ok=True)
        fake_video.write_bytes(b"\x00" * 2048)

        mock_renderer = Mock()
        mock_renderer.render.return_value = RenderResult(
            success=True, output_path=fake_video, render_time=3.0,
        )
        mock_renderer_class.return_value = mock_renderer

        engine = MathContentEngine(
            config=mock_config, interest="basketball", storage=video_storage,
        )

        result = engine.generate(
            topic="Solving two-step equations",
            interest="basketball",
            student_profile=basketball_student,
            concept_ids=["AT-24"],
            grade="grade_8",
        )

        assert result.success
        assert result.video_id is not None

        # --- Step 4: Verify both stores have consistent data ---
        loaded_ep = engagement_store.load(key)
        assert loaded_ep is not None
        assert loaded_ep["address"] == "J"

        stored_video = video_storage.get_by_id(result.video_id)
        assert stored_video is not None
        assert stored_video.interest == "basketball"
        assert stored_video.concept_ids == ["AT-24"]
        assert stored_video.grade == "grade_8"
        assert stored_video.file_size_bytes == 2048

    @patch("math_content_engine.engine.create_llm_client")
    @patch("math_content_engine.engine.ManimRenderer")
    def test_engagement_profile_is_loaded_before_generation(
        self,
        mock_renderer_class,
        mock_create_client,
        mock_config,
        engagement_store,
        video_storage,
        basketball_student,
        tmp_path,
    ):
        """Simulate loading a cached engagement profile before generating."""
        # Pre-populate engagement store (simulates prior session)
        interest_profile = get_interest_profile("basketball")
        ep = build_engagement_profile(interest_profile, basketball_student)
        key = make_store_key("basketball", "Jordan")
        engagement_store.save(key, ep)

        # Later: load profile from store and use it
        loaded_ep = engagement_store.load(key)
        assert loaded_ep is not None

        # Reconstruct student profile from stored engagement data
        student = StudentProfile(
            name=loaded_ep["student_name"],
            preferred_address=loaded_ep["address"],
        )
        assert student.get_display_address() == "J"

        # Generate with the loaded profile
        mock_client = Mock()
        mock_client.generate.return_value = LLMResponse(
            content=f"```python\n{PERSONALIZED_BASKETBALL_CODE}\n```",
            model="claude-sonnet-4-20250514",
            usage={},
        )
        mock_create_client.return_value = mock_client

        fake_video = tmp_path / "output" / "scene.mp4"
        fake_video.parent.mkdir(parents=True, exist_ok=True)
        fake_video.write_bytes(b"\x00" * 512)

        mock_renderer = Mock()
        mock_renderer.render.return_value = RenderResult(
            success=True, output_path=fake_video, render_time=1.0,
        )
        mock_renderer_class.return_value = mock_renderer

        engine = MathContentEngine(
            config=mock_config, interest="basketball", storage=video_storage,
        )

        result = engine.generate(
            topic="Linear equations",
            interest="basketball",
            student_profile=student,
        )

        assert result.success
        assert result.video_id is not None


# ===================================================================
# Test Class 4: Compatibility with agentic_math_tutor schemas
# ===================================================================


class TestDataServiceCompatibility:
    """Verify math_content_engine data is compatible with agentic_math_tutor schemas."""

    def test_video_metadata_converts_to_video_content_dto(self, video_storage):
        """VideoStorage output can populate a VideoContentDTO for the tutor."""
        video_create = VideoCreate(
            topic="Two-Step Linear Equations",
            scene_name="TwoStepEquationsScene",
            video_path="/app/output/TwoStepEquationsScene.mp4",
            code="class TwoStepEquationsScene(Scene): ...",
            concept_ids=["AT-24"],
            grade="grade_8",
            interest="basketball",
            style=AnimationStyle.DARK,
            quality=VideoQuality.MEDIUM,
            llm_provider="claude",
            llm_model="claude-sonnet-4-20250514",
            generation_attempts=1,
            render_attempts=2,
            total_attempts=3,
            generation_time_ms=1500,
            render_time_ms=3000,
            file_size_bytes=524288,
            duration_seconds=30.5,
            success=True,
        )

        # Save and retrieve
        saved = video_storage.save(video_create)
        loaded = video_storage.get_by_id(saved.id)
        assert loaded is not None

        # Convert to VideoContentDTO (integration schema)
        dto = VideoContentDTO(
            video_id=loaded.id,
            concept_ids=loaded.concept_ids,
            topic=loaded.topic,
            scene_name=loaded.scene_name,
            theme=loaded.interest or "neutral",
            grade=loaded.grade or "",
            source_path=loaded.video_path,
            code=loaded.code,
            duration_seconds=loaded.duration_seconds,
            file_size_bytes=loaded.file_size_bytes,
            style=loaded.style.value,
            quality=loaded.quality.value,
            llm_provider=loaded.llm_provider,
            llm_model=loaded.llm_model,
            created_at=loaded.created_at.isoformat(),
        )

        assert dto.video_id == loaded.id
        assert dto.concept_ids == ["AT-24"]
        assert dto.topic == "Two-Step Linear Equations"
        assert dto.theme == "basketball"
        assert dto.grade == "grade_8"
        assert dto.style == "dark"
        assert dto.quality == "m"
        assert dto.duration_seconds == 30.5
        assert dto.file_size_bytes == 524288

    def test_interest_names_map_to_content_themes(self):
        """
        Verify math_content_engine interest names can map to
        agentic_math_tutor ContentTheme values.

        agentic_math_tutor uses ContentTheme enum values like
        'sports_basketball', while math_content_engine uses short names
        like 'basketball'. This test documents the mapping convention.
        """
        # Known mapping: engine interest name → tutor ContentTheme value
        INTEREST_TO_THEME = {
            "basketball": "sports_basketball",
            "soccer": "sports_soccer",
            "minecraft": "gaming_minecraft",
            "pokemon": "gaming_pokemon",
            "animals": "nature_animals",
            "space": "nature_space",
            "music": "music_pop",
            "pop_music": "music_pop",
            "robots": "technology_robots",
            "cooking": "food_cooking",
            "art": "art_drawing",
            "drawing": "art_drawing",
        }

        available = list_available_interests()

        # Verify each mapped interest exists in the engine
        for interest_name in INTEREST_TO_THEME:
            if interest_name in available:
                profile = get_interest_profile(interest_name)
                assert profile is not None, f"Profile missing for mapped interest: {interest_name}"

    def test_student_context_dto_from_student_profile(self, basketball_student):
        """
        StudentProfile fields can populate a StudentContextDTO for the tutor.

        The tutor sends StudentContextDTO; the engine receives it and
        can create a StudentProfile from it.
        """
        # Simulate tutor → engine: StudentContextDTO
        tutor_dto = StudentContextDTO(
            student_id="student-001",
            name="Jordan",
            grade_level="grade_8",
            theme="sports_basketball",
            interests=["basketball", "gaming"],
            hobbies=["playing basketball"],
            learning_style="visual",
            preferred_pace="moderate",
            math_anxiety_level="low",
        )

        # Engine converts DTO → StudentProfile
        student = StudentProfile(
            name=tutor_dto.name,
            grade_level=tutor_dto.grade_level,
        )

        assert student.name == "Jordan"
        assert student.grade_level == "grade_8"
        assert student.get_display_address() == "Jordan"

    def test_content_event_wraps_video_dto(self, video_storage):
        """A ContentEvent can wrap a VideoContentDTO produced from VideoStorage."""
        video_create = VideoCreate(
            topic="Pythagorean Theorem",
            scene_name="PythagoreanScene",
            video_path="/app/output/PythagoreanScene.mp4",
            code="class PythagoreanScene(Scene): ...",
            concept_ids=["GE-15"],
            grade="grade_9",
            interest="basketball",
            success=True,
        )

        saved = video_storage.save(video_create)

        # Build DTO from stored metadata
        dto = VideoContentDTO(
            video_id=saved.id,
            concept_ids=saved.concept_ids,
            topic=saved.topic,
            scene_name=saved.scene_name,
            theme=saved.interest or "neutral",
            grade=saved.grade or "",
            source_path=saved.video_path,
            code=saved.code,
            created_at=saved.created_at.isoformat(),
        )

        # Wrap in ContentEvent
        event = ContentEvent(
            event_type=ContentEventType.VIDEO_GENERATED,
            event_id="evt-test-001",
            timestamp=datetime.utcnow().isoformat(),
            payload=dto.model_dump(),
        )

        assert event.event_type == ContentEventType.VIDEO_GENERATED
        assert event.payload["video_id"] == saved.id
        assert event.payload["concept_ids"] == ["GE-15"]
        assert event.payload["theme"] == "basketball"
        assert event.payload["grade"] == "grade_9"

    def test_engagement_profile_fields_satisfy_tutor_needs(
        self, engagement_store, basketball_student
    ):
        """
        Engagement profile data stored locally contains all fields needed
        by agentic_math_tutor for personalized content delivery.

        The tutor needs: address, student_name, scenarios, figures,
        color_palette, and current_season to personalize responses.
        """
        interest_profile = get_interest_profile("basketball")
        ep = build_engagement_profile(interest_profile, basketball_student)

        key = make_store_key("basketball", "Jordan")
        engagement_store.save(key, ep)
        loaded = engagement_store.load(key)

        # These fields are required by the tutor's personalization layer
        required_fields = [
            "address", "student_name", "scenarios", "hooks",
            "stats", "trending", "current_season", "favorite_label",
            "figures", "color_palette",
        ]
        for field in required_fields:
            assert field in loaded, f"Missing required field: {field}"

        # Verify types match tutor expectations
        assert isinstance(loaded["address"], str)
        assert isinstance(loaded["scenarios"], list)
        assert isinstance(loaded["hooks"], list)
        assert isinstance(loaded["stats"], dict)
        assert isinstance(loaded["trending"], list)
        assert isinstance(loaded["figures"], list)
        assert isinstance(loaded["color_palette"], str)


# ===================================================================
# Test Class 5: Real E2E with live LLM (gated by API key)
#
# The pipeline itself writes results to:
#   - agentic_math_tutor PostgreSQL  (videos table via TutorDataServiceWriter)
#   - local EngagementStore          (data/e2e/engagement.db)
#   - local VideoStorage             (data/e2e/videos.db)
#
# Tests just run the pipeline and verify data landed correctly.
# ===================================================================

# Persistent local data directory
_E2E_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "e2e"


class TestRealPersonalizedE2E:
    """
    Real E2E: generates personalized content with a live LLM.

    The engine pipeline writes results to both local SQLite and the
    agentic_math_tutor PostgreSQL ``videos`` table automatically via
    ``TutorDataServiceWriter``.  Tests simply call ``engine.generate()``
    and then verify the data in each store.
    """

    @pytest.fixture(autouse=True)
    def _ensure_data_dir(self):
        """Create the persistent e2e data directory."""
        _E2E_DATA_DIR.mkdir(parents=True, exist_ok=True)

    @pytest.fixture
    def local_video_storage(self) -> VideoStorage:
        return VideoStorage(db_path=_E2E_DATA_DIR / "videos.db")

    @pytest.fixture
    def local_engagement_store(self) -> EngagementStore:
        return EngagementStore(db_path=_E2E_DATA_DIR / "engagement.db")

    @pytest.fixture
    def tutor_writer(self):
        """TutorDataServiceWriter pointed at local Docker PG."""
        from math_content_engine.integration.tutor_writer import TutorDataServiceWriter

        writer = TutorDataServiceWriter()
        yield writer
        # Cleanup e2e rows after test
        writer.cleanup_e2e(source="math_content_engine")

    @pytest.mark.e2e
    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"),
        reason="No API key configured",
    )
    def test_real_personalized_code_generation_with_storage(
        self, local_video_storage, local_engagement_store, tutor_writer, tmp_path
    ):
        """Real LLM → personalized animation → pipeline stores in tutor PG + local SQLite."""
        # --- 1. Build and persist engagement profile ---
        basketball_student = StudentProfile(
            name="Jordan",
            preferred_address="J",
            favorite_figure="Stephen Curry",
            favorite_team="Warriors",
        )
        interest_profile = get_interest_profile("basketball")
        ep = build_engagement_profile(interest_profile, basketball_student)

        key = make_store_key("basketball", "Jordan")
        local_engagement_store.save(key, ep)

        # --- 2. Generate animation — pipeline writes to BOTH stores ---
        engine = MathContentEngine(
            interest="basketball",
            storage=local_video_storage,
            tutor_writer=tutor_writer,
        )
        engine.config.output_dir = tmp_path / "output"
        engine.config.video_quality = ConfigVideoQuality.LOW

        result = engine.generate(
            topic="Solving the equation 3x + 5 = 20",
            requirements="Use basketball statistics as context",
            audience_level="middle school",
            interest="basketball",
            student_profile=basketball_student,
            save_to_storage=True,
            concept_ids=["AT-24"],
            grade="grade_8",
        )

        # Code must always be generated
        assert result.code is not None
        assert "from manim import" in result.code

        # --- 3. Verify engagement profile in local EngagementStore ---
        loaded_ep = local_engagement_store.load(key)
        assert loaded_ep is not None
        assert loaded_ep["address"] == "J"
        assert loaded_ep["student_name"] == "Jordan"
        assert "Stephen Curry" in loaded_ep["favorite_label"]

        # --- 4. Verify video in local VideoStorage ---
        assert result.video_id is not None, "video_id must be set when save_to_storage=True"

        stored_video = local_video_storage.get_by_id(result.video_id)
        assert stored_video is not None
        assert stored_video.topic == "Solving the equation 3x + 5 = 20"
        assert stored_video.interest == "basketball"
        assert stored_video.concept_ids == ["AT-24"]
        assert stored_video.grade == "grade_8"
        assert stored_video.code is not None and len(stored_video.code) > 0
        assert stored_video.llm_provider is not None
        assert stored_video.llm_model is not None

        # --- 5. Verify row in agentic_math_tutor PostgreSQL (written by pipeline) ---
        assert result.tutor_video_id is not None, (
            "tutor_video_id must be set when tutor_writer is configured"
        )

        tutor_row = tutor_writer.read_video(result.tutor_video_id)
        assert tutor_row is not None
        assert tutor_row["concept_id"] == "AT-24"
        assert tutor_row["theme"] == "sports_basketball"
        assert tutor_row["grade"] == "grade_8"
        assert tutor_row["engine_video_id"] == result.engine_video_id
        assert tutor_row["manim_code"] is not None
        assert len(tutor_row["manim_code"]) > 0
        assert tutor_row["source"] == "math_content_engine"

    @pytest.mark.e2e
    @pytest.mark.slow
    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"),
        reason="No API key configured",
    )
    def test_real_personalized_video_generation_with_storage(
        self, local_video_storage, local_engagement_store, tutor_writer, tmp_path
    ):
        """Real LLM + Manim → pipeline stores video in tutor PG + local SQLite."""
        # --- 1. Build and persist engagement profile ---
        gaming_student = StudentProfile(
            name="Alex",
            preferred_address="Alex",
            grade_level="7th grade",
            favorite_figure="Technoblade",
        )
        interest_profile = get_interest_profile("gaming")
        ep = build_engagement_profile(interest_profile, gaming_student)

        key = make_store_key("gaming", "Alex")
        local_engagement_store.save(key, ep)

        # --- 2. Generate animation — pipeline writes to BOTH stores ---
        engine = MathContentEngine(
            interest="gaming",
            storage=local_video_storage,
            tutor_writer=tutor_writer,
        )
        engine.config.output_dir = tmp_path / "output"
        engine.config.video_quality = ConfigVideoQuality.LOW

        result = engine.generate(
            topic="Show the equation 2x + 5 = 11 and solve it step by step",
            requirements="Use gaming context, address the viewer as Alex",
            audience_level="middle school",
            interest="gaming",
            student_profile=gaming_student,
            save_to_storage=True,
            concept_ids=["AT-24"],
            grade="grade_7",
        )

        # Code should always be generated
        assert result.code is not None

        # --- 3. Verify engagement profile in local EngagementStore ---
        loaded_ep = local_engagement_store.load(key)
        assert loaded_ep is not None
        assert loaded_ep["address"] == "Alex"
        assert loaded_ep["student_name"] == "Alex"

        # --- 4. Verify video in local VideoStorage ---
        assert result.video_id is not None, "video_id must be set when save_to_storage=True"

        stored_video = local_video_storage.get_by_id(result.video_id)
        assert stored_video is not None
        assert stored_video.interest == "gaming"
        assert stored_video.concept_ids == ["AT-24"]
        assert stored_video.grade == "grade_7"

        # --- 5. Verify row in agentic_math_tutor PostgreSQL (written by pipeline) ---
        assert result.tutor_video_id is not None, (
            "tutor_video_id must be set when tutor_writer is configured"
        )

        tutor_row = tutor_writer.read_video(result.tutor_video_id)
        assert tutor_row is not None
        assert tutor_row["concept_id"] == "AT-24"
        assert tutor_row["theme"] == "gaming_minecraft"
        assert tutor_row["grade"] == "grade_7"
        assert tutor_row["engine_video_id"] == result.engine_video_id
        assert tutor_row["source"] == "math_content_engine"

        if result.success:
            assert tutor_row["status"] == "pre_generated"
        else:
            assert tutor_row["status"] == "failed"

    @pytest.mark.e2e
    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"),
        reason="No API key configured",
    )
    def test_regeneration_upserts_existing_video(self, tutor_writer):
        """Re-generating same concept/theme/grade updates existing row via upsert."""
        # First write
        first_uuid = tutor_writer.write_video(
            concept_id="UPSERT-TEST-01",
            interest="basketball",
            grade="grade_8",
            engine_video_id="first-gen-id",
            manim_code="class Scene1(Scene): pass",
            success=True,
            source="math_content_engine_test",
        )
        assert first_uuid is not None

        # Second write: same concept/theme/grade should upsert (not crash)
        second_uuid = tutor_writer.write_video(
            concept_id="UPSERT-TEST-01",
            interest="basketball",
            grade="grade_8",
            engine_video_id="second-gen-id",
            manim_code="class Scene2(Scene): pass",
            success=True,
            source="math_content_engine_test",
        )
        assert second_uuid is not None

        # The returned UUID should be the SAME row (upserted, not a new row)
        assert first_uuid == second_uuid

        # Verify the row has updated data
        row = tutor_writer.read_video(second_uuid)
        assert row is not None
        assert row["engine_video_id"] == "second-gen-id"
        assert "Scene2" in row["manim_code"]

        # Cleanup this specific test data
        tutor_writer.cleanup_e2e(source="math_content_engine_test")
