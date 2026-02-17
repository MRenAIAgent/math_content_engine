"""
Tests for integration schemas (DTOs shared with agentic_math_tutor).

Validates:
- All DTOs can be created with valid data
- Required fields are enforced
- Default values work correctly
- Serialization/deserialization round-trips work
- Validation constraints (Field(ge=1, le=5) etc.) are enforced
"""
import json
import pytest
from pydantic import ValidationError

from math_content_engine.integration.schemas import (
    ConceptDTO,
    ContentEvent,
    ContentEventType,
    ExerciseDTO,
    MasteryContextDTO,
    StudentContextDTO,
    VideoContentDTO,
)


class TestContentEventType:
    """Tests for ContentEventType enum."""

    def test_event_type_values(self):
        """Verify all ContentEventType enum values."""
        assert ContentEventType.VIDEO_GENERATED.value == "video_generated"
        assert ContentEventType.CONCEPT_CREATED.value == "concept_created"
        assert ContentEventType.EXERCISE_GENERATED.value == "exercise_generated"

    def test_event_type_is_string_enum(self):
        """ContentEventType should be usable as a string."""
        assert str(ContentEventType.VIDEO_GENERATED) == "ContentEventType.VIDEO_GENERATED"
        assert ContentEventType.VIDEO_GENERATED.value == "video_generated"

    def test_event_type_comparison(self):
        """ContentEventType can be compared to string values."""
        assert ContentEventType.VIDEO_GENERATED == ContentEventType.VIDEO_GENERATED
        assert ContentEventType.VIDEO_GENERATED.value == "video_generated"


class TestConceptDTO:
    """Tests for ConceptDTO."""

    def test_concept_dto_creation_minimal(self):
        """ConceptDTO can be created with only required fields."""
        dto = ConceptDTO(
            concept_id="C-001",
            name="Test Concept",
            description="A test concept",
            difficulty=3,
            category="Algebra",
        )
        assert dto.concept_id == "C-001"
        assert dto.name == "Test Concept"
        assert dto.description == "A test concept"
        assert dto.difficulty == 3
        assert dto.category == "Algebra"

    def test_concept_dto_creation_full(self, sample_concept_dto_data):
        """ConceptDTO can be created with all fields."""
        dto = ConceptDTO(**sample_concept_dto_data)
        assert dto.concept_id == "AT-24"
        assert dto.name == "Two-Step Linear Equations"
        assert dto.subcategory == "Equations"
        assert dto.time_to_master_minutes == 45
        assert dto.grade_levels == ["7", "8"]
        assert len(dto.examples) == 2
        assert dto.prerequisites == ["OO-14", "OO-15"]
        assert dto.dependents == ["AT-25"]
        assert dto.related == ["AT-23"]

    def test_concept_dto_difficulty_validation_minimum(self):
        """Difficulty must be at least 1."""
        with pytest.raises(ValidationError) as exc_info:
            ConceptDTO(
                concept_id="C-001",
                name="Test",
                description="Test",
                difficulty=0,
                category="Algebra",
            )
        errors = exc_info.value.errors()
        assert any("greater than or equal to 1" in str(e) for e in errors)

    def test_concept_dto_difficulty_validation_maximum(self):
        """Difficulty must be at most 5."""
        with pytest.raises(ValidationError) as exc_info:
            ConceptDTO(
                concept_id="C-001",
                name="Test",
                description="Test",
                difficulty=6,
                category="Algebra",
            )
        errors = exc_info.value.errors()
        assert any("less than or equal to 5" in str(e) for e in errors)

    def test_concept_dto_difficulty_validation_valid_range(self):
        """Difficulty values 1-5 are all valid."""
        for difficulty in [1, 2, 3, 4, 5]:
            dto = ConceptDTO(
                concept_id="C-001",
                name="Test",
                description="Test",
                difficulty=difficulty,
                category="Algebra",
            )
            assert dto.difficulty == difficulty

    def test_concept_dto_serialization_roundtrip(self, sample_concept_dto_data):
        """ConceptDTO can be serialized to JSON and deserialized back."""
        original = ConceptDTO(**sample_concept_dto_data)
        json_str = original.model_dump_json()
        restored = ConceptDTO.model_validate_json(json_str)

        assert restored.concept_id == original.concept_id
        assert restored.name == original.name
        assert restored.difficulty == original.difficulty
        assert restored.prerequisites == original.prerequisites
        assert restored.examples == original.examples

    def test_concept_dto_default_values(self):
        """Optional list fields default to empty lists."""
        dto = ConceptDTO(
            concept_id="C-001",
            name="Test",
            description="Test",
            difficulty=3,
            category="Algebra",
        )
        assert dto.subcategory is None
        assert dto.time_to_master_minutes is None
        assert dto.grade_levels == []
        assert dto.examples == []
        assert dto.keywords == []
        assert dto.learning_objectives == []
        assert dto.common_misconceptions == []
        assert dto.prerequisites == []
        assert dto.dependents == []
        assert dto.related == []


class TestVideoContentDTO:
    """Tests for VideoContentDTO."""

    def test_video_dto_creation(self, sample_video_dto_data):
        """VideoContentDTO can be created with valid data."""
        dto = VideoContentDTO(**sample_video_dto_data)
        assert dto.video_id == "test-video-001"
        assert dto.concept_ids == ["AT-24"]
        assert dto.topic == "Two-Step Linear Equations"
        assert dto.scene_name == "TwoStepEquationsScene"
        assert dto.source_path == "/app/output/TwoStepEquationsScene.mp4"
        assert dto.llm_provider == "claude"
        assert dto.llm_model == "claude-sonnet-4-20250514"

    def test_video_dto_defaults(self):
        """VideoContentDTO has correct default values."""
        dto = VideoContentDTO(
            video_id="v-001",
            concept_ids=["C-001"],
            topic="Test Topic",
            scene_name="TestScene",
            source_path="/path/to/video.mp4",
            code="class TestScene(Scene): pass",
        )
        assert dto.theme == "neutral"
        assert dto.grade == ""
        assert dto.style == "dark"
        assert dto.quality == "m"
        assert dto.duration_seconds is None
        assert dto.file_size_bytes is None
        assert dto.llm_provider is None
        assert dto.llm_model is None
        assert dto.created_at == ""

    def test_video_dto_serialization_roundtrip(self, sample_video_dto_data):
        """VideoContentDTO can be serialized and deserialized."""
        original = VideoContentDTO(**sample_video_dto_data)
        json_str = original.model_dump_json()
        restored = VideoContentDTO.model_validate_json(json_str)

        assert restored.video_id == original.video_id
        assert restored.concept_ids == original.concept_ids
        assert restored.theme == original.theme
        assert restored.code == original.code

    def test_video_dto_with_duration_and_size(self):
        """VideoContentDTO can store duration and file size."""
        dto = VideoContentDTO(
            video_id="v-001",
            concept_ids=["C-001"],
            topic="Test",
            scene_name="TestScene",
            source_path="/path/to/video.mp4",
            code="class TestScene(Scene): pass",
            duration_seconds=120.5,
            file_size_bytes=1024000,
        )
        assert dto.duration_seconds == 120.5
        assert dto.file_size_bytes == 1024000


class TestExerciseDTO:
    """Tests for ExerciseDTO."""

    def test_exercise_dto_creation(self, sample_exercise_dto_data):
        """ExerciseDTO can be created with valid data."""
        dto = ExerciseDTO(**sample_exercise_dto_data)
        assert dto.exercise_id == "ex-001"
        assert dto.concept_ids == ["AT-24"]
        assert dto.title == "Solve: 2x + 5 = 11"
        assert dto.answer == "x = 3"
        assert dto.difficulty == 3
        assert len(dto.hints) == 2

    def test_exercise_dto_difficulty_validation_minimum(self):
        """Exercise difficulty must be at least 1."""
        with pytest.raises(ValidationError) as exc_info:
            ExerciseDTO(
                exercise_id="ex-001",
                concept_ids=["C-001"],
                title="Test",
                problem="Test problem",
                solution="Test solution",
                difficulty=0,
            )
        errors = exc_info.value.errors()
        assert any("greater than or equal to 1" in str(e) for e in errors)

    def test_exercise_dto_difficulty_validation_maximum(self):
        """Exercise difficulty must be at most 5."""
        with pytest.raises(ValidationError) as exc_info:
            ExerciseDTO(
                exercise_id="ex-001",
                concept_ids=["C-001"],
                title="Test",
                problem="Test problem",
                solution="Test solution",
                difficulty=6,
            )
        errors = exc_info.value.errors()
        assert any("less than or equal to 5" in str(e) for e in errors)

    def test_exercise_dto_defaults(self):
        """ExerciseDTO has correct default values."""
        dto = ExerciseDTO(
            exercise_id="ex-001",
            concept_ids=["C-001"],
            title="Test",
            problem="Test problem",
            solution="Test solution",
            difficulty=3,
        )
        assert dto.answer is None
        assert dto.hints == []
        assert dto.theme == "neutral"
        assert dto.grade == ""
        assert dto.skill_tested == "procedural"
        assert dto.estimated_time_minutes is None
        assert dto.keywords == []

    def test_exercise_dto_serialization_roundtrip(self, sample_exercise_dto_data):
        """ExerciseDTO can be serialized and deserialized."""
        original = ExerciseDTO(**sample_exercise_dto_data)
        json_str = original.model_dump_json()
        restored = ExerciseDTO.model_validate_json(json_str)

        assert restored.exercise_id == original.exercise_id
        assert restored.hints == original.hints
        assert restored.difficulty == original.difficulty


class TestMasteryContextDTO:
    """Tests for MasteryContextDTO."""

    def test_mastery_dto_creation(self, sample_mastery_dto_data):
        """MasteryContextDTO can be created with valid data."""
        dto = MasteryContextDTO(**sample_mastery_dto_data)
        assert dto.concept_id == "AT-24"
        assert dto.overall_mastery == 0.75
        assert dto.dimension_breakdown["procedural"] == 0.8
        assert dto.recommended_dimension == "conceptual"
        assert dto.attempt_count == 5

    def test_mastery_dto_mastery_range_minimum(self):
        """overall_mastery can be 0.0."""
        dto = MasteryContextDTO(
            concept_id="C-001",
            overall_mastery=0.0,
        )
        assert dto.overall_mastery == 0.0

    def test_mastery_dto_mastery_range_maximum(self):
        """overall_mastery can be 1.0."""
        dto = MasteryContextDTO(
            concept_id="C-001",
            overall_mastery=1.0,
        )
        assert dto.overall_mastery == 1.0

    def test_mastery_dto_invalid_range_above(self):
        """overall_mastery > 1.0 should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            MasteryContextDTO(
                concept_id="C-001",
                overall_mastery=1.1,
            )
        errors = exc_info.value.errors()
        assert any("less than or equal to 1" in str(e) for e in errors)

    def test_mastery_dto_invalid_range_below(self):
        """overall_mastery < 0.0 should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            MasteryContextDTO(
                concept_id="C-001",
                overall_mastery=-0.1,
            )
        errors = exc_info.value.errors()
        assert any("greater than or equal to 0" in str(e) for e in errors)

    def test_mastery_dto_defaults(self):
        """MasteryContextDTO has correct default values."""
        dto = MasteryContextDTO(
            concept_id="C-001",
            overall_mastery=0.5,
        )
        assert dto.dimension_breakdown == {}
        assert dto.recommended_dimension == "procedural"
        assert dto.attempt_count == 0
        assert dto.common_errors == []

    def test_mastery_dto_serialization_roundtrip(self, sample_mastery_dto_data):
        """MasteryContextDTO can be serialized and deserialized."""
        original = MasteryContextDTO(**sample_mastery_dto_data)
        json_str = original.model_dump_json()
        restored = MasteryContextDTO.model_validate_json(json_str)

        assert restored.overall_mastery == original.overall_mastery
        assert restored.dimension_breakdown == original.dimension_breakdown


class TestStudentContextDTO:
    """Tests for StudentContextDTO."""

    def test_student_dto_creation(self, sample_student_dto_data):
        """StudentContextDTO can be created with valid data."""
        dto = StudentContextDTO(**sample_student_dto_data)
        assert dto.student_id == "student-001"
        assert dto.name == "Test Student"
        assert dto.grade_level == "8"
        assert dto.theme == "sports_basketball"
        assert dto.interests == ["basketball", "gaming"]
        assert dto.learning_style == "visual"

    def test_student_dto_with_mastery_gaps(self, sample_student_dto_data):
        """StudentContextDTO can contain MasteryContextDTO objects."""
        dto = StudentContextDTO(**sample_student_dto_data)
        assert len(dto.mastery_gaps) == 1
        assert dto.mastery_gaps[0].concept_id == "AT-24"
        assert dto.mastery_gaps[0].overall_mastery == 0.75

    def test_student_dto_defaults(self):
        """StudentContextDTO has correct default values."""
        dto = StudentContextDTO(
            student_id="s-001",
            name="Test",
        )
        assert dto.grade_level == ""
        assert dto.theme == "neutral"
        assert dto.interests == []
        assert dto.hobbies == []
        assert dto.learning_style is None
        assert dto.preferred_pace is None
        assert dto.math_anxiety_level is None
        assert dto.mastery_gaps == []

    def test_student_dto_serialization_roundtrip(self, sample_student_dto_data):
        """StudentContextDTO can be serialized and deserialized."""
        original = StudentContextDTO(**sample_student_dto_data)
        json_str = original.model_dump_json()
        restored = StudentContextDTO.model_validate_json(json_str)

        assert restored.student_id == original.student_id
        assert restored.interests == original.interests
        assert len(restored.mastery_gaps) == len(original.mastery_gaps)
        assert restored.mastery_gaps[0].concept_id == original.mastery_gaps[0].concept_id

    def test_student_dto_nested_mastery_validation(self):
        """StudentContextDTO validates nested MasteryContextDTO objects."""
        with pytest.raises(ValidationError):
            StudentContextDTO(
                student_id="s-001",
                name="Test",
                mastery_gaps=[
                    {
                        "concept_id": "C-001",
                        "overall_mastery": 1.5,  # Invalid: > 1.0
                    }
                ],
            )


class TestContentEvent:
    """Tests for ContentEvent."""

    def test_content_event_video_type(self, sample_video_dto_data):
        """ContentEvent can wrap a video event."""
        event = ContentEvent(
            event_type=ContentEventType.VIDEO_GENERATED,
            event_id="evt-001",
            timestamp="2024-01-01T00:00:00Z",
            payload=sample_video_dto_data,
        )
        assert event.event_type == ContentEventType.VIDEO_GENERATED
        assert event.event_id == "evt-001"
        assert event.payload["video_id"] == "test-video-001"

    def test_content_event_concept_type(self, sample_concept_dto_data):
        """ContentEvent can wrap a concept event."""
        event = ContentEvent(
            event_type=ContentEventType.CONCEPT_CREATED,
            event_id="evt-002",
            timestamp="2024-01-01T00:00:00Z",
            payload=sample_concept_dto_data,
        )
        assert event.event_type == ContentEventType.CONCEPT_CREATED
        assert event.payload["concept_id"] == "AT-24"

    def test_content_event_exercise_type(self, sample_exercise_dto_data):
        """ContentEvent can wrap an exercise event."""
        event = ContentEvent(
            event_type=ContentEventType.EXERCISE_GENERATED,
            event_id="evt-003",
            timestamp="2024-01-01T00:00:00Z",
            payload=sample_exercise_dto_data,
        )
        assert event.event_type == ContentEventType.EXERCISE_GENERATED
        assert event.payload["exercise_id"] == "ex-001"

    def test_content_event_serialization(self, sample_video_dto_data):
        """ContentEvent can be serialized to JSON."""
        event = ContentEvent(
            event_type=ContentEventType.VIDEO_GENERATED,
            event_id="evt-001",
            timestamp="2024-01-01T00:00:00Z",
            payload=sample_video_dto_data,
        )
        json_str = event.model_dump_json()
        data = json.loads(json_str)

        assert data["event_type"] == "video_generated"
        assert data["event_id"] == "evt-001"
        assert "payload" in data
        assert data["payload"]["video_id"] == "test-video-001"

    def test_content_event_default_payload(self):
        """ContentEvent payload defaults to empty dict."""
        event = ContentEvent(
            event_type=ContentEventType.VIDEO_GENERATED,
            event_id="evt-001",
            timestamp="2024-01-01T00:00:00Z",
        )
        assert event.payload == {}

    def test_content_event_roundtrip(self, sample_video_dto_data):
        """ContentEvent can be serialized and deserialized."""
        original = ContentEvent(
            event_type=ContentEventType.VIDEO_GENERATED,
            event_id="evt-001",
            timestamp="2024-01-01T00:00:00Z",
            payload=sample_video_dto_data,
        )
        json_str = original.model_dump_json()
        restored = ContentEvent.model_validate_json(json_str)

        assert restored.event_type == original.event_type
        assert restored.event_id == original.event_id
        assert restored.timestamp == original.timestamp
        assert restored.payload == original.payload
