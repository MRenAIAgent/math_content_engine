"""
Shared integration DTOs for math_content_engine <-> agentic_math_tutor.

These models define the JSON contract between the two services.
Communication happens via HTTP API and Redis Streams — never via
direct Python imports. Both repos maintain their own copy of these
schemas; integration tests validate they stay in sync.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ContentEventType(str, Enum):
    """Types of content events published to Redis Streams."""
    VIDEO_GENERATED = "video_generated"
    CONCEPT_CREATED = "concept_created"
    EXERCISE_GENERATED = "exercise_generated"


class ConceptDTO(BaseModel):
    """Knowledge graph concept exchanged between engine and tutor."""
    concept_id: str
    name: str
    description: str
    difficulty: int = Field(ge=1, le=5)
    category: str
    subcategory: Optional[str] = None
    time_to_master_minutes: Optional[int] = None
    grade_levels: List[str] = []
    examples: List[str] = []
    keywords: List[str] = []
    learning_objectives: List[str] = []
    common_misconceptions: List[str] = []
    prerequisites: List[str] = []
    dependents: List[str] = []
    related: List[str] = []


class VideoContentDTO(BaseModel):
    """Video content produced by the engine for tutor ingestion."""
    video_id: str
    concept_ids: List[str]
    topic: str
    scene_name: str
    theme: str = "neutral"
    grade: str = ""
    source_path: str
    code: str
    duration_seconds: Optional[float] = None
    file_size_bytes: Optional[int] = None
    style: str = "dark"
    quality: str = "m"
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    created_at: str = ""


class ExerciseDTO(BaseModel):
    """Structured exercise exchanged between engine and tutor."""
    exercise_id: str
    concept_ids: List[str]
    title: str
    problem: str
    solution: str
    answer: Optional[str] = None
    difficulty: int = Field(ge=1, le=5)
    hints: List[str] = []
    theme: str = "neutral"
    grade: str = ""
    skill_tested: str = "procedural"
    estimated_time_minutes: Optional[int] = None
    keywords: List[str] = []


class MasteryContextDTO(BaseModel):
    """Mastery snapshot sent to the engine to guide content generation."""
    concept_id: str
    overall_mastery: float = Field(ge=0.0, le=1.0)
    dimension_breakdown: Dict[str, float] = {}
    recommended_dimension: str = "procedural"
    attempt_count: int = 0
    common_errors: List[str] = []


class StudentContextDTO(BaseModel):
    """Student profile sent to the engine for personalized generation."""
    student_id: str
    name: str
    grade_level: str = ""
    theme: str = "neutral"
    interests: List[str] = []
    hobbies: List[str] = []
    learning_style: Optional[str] = None
    preferred_pace: Optional[str] = None
    math_anxiety_level: Optional[str] = None
    mastery_gaps: List[MasteryContextDTO] = []


class ContentEvent(BaseModel):
    """Event envelope published to Redis Streams."""
    event_type: ContentEventType
    event_id: str
    timestamp: str
    payload: dict = {}
