"""
Test configuration for Math Content Engine.

Provides shared fixtures for testing integration schemas, publishers, and theme mappers.
"""
import os
import pytest
from dotenv import load_dotenv

# Load .env at collection time so that @pytest.mark.skipif decorators
# that check os.getenv("ANTHROPIC_API_KEY") see the value.
# override=True is needed because the shell may export the var as empty.
load_dotenv(override=True)


@pytest.fixture
def sample_concept_data():
    """Sample concept data matching the knowledge graph structure."""
    return {
        "id": "AT-24",
        "name": "Two-Step Linear Equations",
        "description": "Solving equations that require two operations",
        "difficulty": 3,
        "category": "Linear",
        "subcategory": "Equations",
        "grade_level": "7-8",
        "time_to_master": 45,
        "examples": ["2x + 5 = 11", "3x - 7 = 14"],
        "prerequisites": ["OO-14", "OO-15"],
        "dependents": ["AT-25"],
        "related": ["AT-23"],
    }


@pytest.fixture
def sample_concept_dto_data():
    """Sample ConceptDTO data matching the schema exactly."""
    return {
        "concept_id": "AT-24",
        "name": "Two-Step Linear Equations",
        "description": "Solving equations that require two operations",
        "difficulty": 3,
        "category": "Linear",
        "subcategory": "Equations",
        "time_to_master_minutes": 45,
        "grade_levels": ["7", "8"],
        "examples": ["2x + 5 = 11", "3x - 7 = 14"],
        "keywords": ["linear", "equations", "two-step"],
        "learning_objectives": ["Solve two-step equations"],
        "common_misconceptions": ["Forgetting to apply operation to both sides"],
        "prerequisites": ["OO-14", "OO-15"],
        "dependents": ["AT-25"],
        "related": ["AT-23"],
    }


@pytest.fixture
def sample_video_dto_data():
    """Sample VideoContentDTO data."""
    return {
        "video_id": "test-video-001",
        "concept_ids": ["AT-24"],
        "topic": "Two-Step Linear Equations",
        "scene_name": "TwoStepEquationsScene",
        "theme": "sports_basketball",
        "grade": "grade_8",
        "source_path": "/app/output/TwoStepEquationsScene.mp4",
        "code": "class TwoStepEquationsScene(Scene):\n    def construct(self):\n        pass",
        "style": "dark",
        "quality": "m",
        "llm_provider": "claude",
        "llm_model": "claude-sonnet-4-20250514",
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_exercise_dto_data():
    """Sample ExerciseDTO data."""
    return {
        "exercise_id": "ex-001",
        "concept_ids": ["AT-24"],
        "title": "Solve: 2x + 5 = 11",
        "problem": "Find the value of x in the equation 2x + 5 = 11",
        "solution": "2x + 5 = 11\n2x = 6\nx = 3",
        "answer": "x = 3",
        "difficulty": 3,
        "hints": ["Subtract 5 from both sides first", "Then divide by 2"],
        "theme": "sports_basketball",
        "grade": "grade_8",
        "skill_tested": "procedural",
        "estimated_time_minutes": 5,
        "keywords": ["linear equations", "two-step", "solving"],
    }


@pytest.fixture
def sample_mastery_dto_data():
    """Sample MasteryContextDTO data."""
    return {
        "concept_id": "AT-24",
        "overall_mastery": 0.75,
        "dimension_breakdown": {
            "procedural": 0.8,
            "conceptual": 0.7,
            "application": 0.75,
        },
        "recommended_dimension": "conceptual",
        "attempt_count": 5,
        "common_errors": ["sign errors", "division errors"],
    }


@pytest.fixture
def sample_student_dto_data(sample_mastery_dto_data):
    """Sample StudentContextDTO data."""
    return {
        "student_id": "student-001",
        "name": "Test Student",
        "grade_level": "8",
        "theme": "sports_basketball",
        "interests": ["basketball", "gaming"],
        "hobbies": ["playing basketball", "video games"],
        "learning_style": "visual",
        "preferred_pace": "moderate",
        "math_anxiety_level": "low",
        "mastery_gaps": [sample_mastery_dto_data],
    }


@pytest.fixture
def sample_content_event_data(sample_video_dto_data):
    """Sample ContentEvent data."""
    return {
        "event_type": "video_generated",
        "event_id": "evt-001",
        "timestamp": "2024-01-01T00:00:00Z",
        "payload": sample_video_dto_data,
    }
