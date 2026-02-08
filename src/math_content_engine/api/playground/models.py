"""Pydantic models for playground API requests and responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Prompt preview / override
# ---------------------------------------------------------------------------


class PromptPreview(BaseModel):
    """Prompts that WOULD be sent to the LLM (for viewing/editing)."""

    stage: str = Field(
        ...,
        description="Pipeline stage: personalize | extract_concepts | generate_animation",
    )
    system_prompt: str = Field(..., description="System prompt text")
    user_prompt: str = Field(..., description="User prompt text")


class PromptOverride(BaseModel):
    """User-edited prompts that override the defaults."""

    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None


# ---------------------------------------------------------------------------
# Prompt preview request
# ---------------------------------------------------------------------------


class PromptPreviewRequest(BaseModel):
    """Request to preview prompts for a specific stage."""

    stage: str = Field(
        ...,
        description="personalize | extract_concepts | generate_animation",
    )
    textbook_content: Optional[str] = Field(
        None, description="Textbook markdown (for personalize / extract_concepts)"
    )
    interest: Optional[str] = Field(None, description="Interest name (for personalize)")
    topic: Optional[str] = Field(
        None, description="Animation topic (for generate_animation)"
    )
    requirements: Optional[str] = Field(
        None, description="Additional requirements (for generate_animation)"
    )
    animation_style: str = Field("dark", description="dark or light")
    audience_level: str = Field("high school", description="Audience level")
    student_name: Optional[str] = Field(None, description="Student name for direct address")
    preferred_address: Optional[str] = Field(None, description="How the student prefers to be called (nickname, etc.)")
    favorite_figure: Optional[str] = Field(None, description="Student's favorite figure (player, singer, etc.)")
    favorite_team: Optional[str] = Field(None, description="Student's favorite team or group")


# ---------------------------------------------------------------------------
# Stage execution
# ---------------------------------------------------------------------------


class StageExecuteRequest(BaseModel):
    """Request to execute a pipeline stage."""

    stage: str = Field(
        ...,
        description="personalize | extract_concepts | generate_animation | render | parse_examples",
    )
    prompt_override: Optional[PromptOverride] = Field(
        None, description="Custom prompts (overrides defaults)"
    )

    # Stage-specific parameters
    textbook_content: Optional[str] = None
    interest: Optional[str] = None
    topic: Optional[str] = None
    requirements: Optional[str] = None
    animation_style: str = "dark"
    audience_level: str = "high school"
    video_quality: str = "l"
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    student_name: Optional[str] = None
    preferred_address: Optional[str] = None
    favorite_figure: Optional[str] = None
    favorite_team: Optional[str] = None

    # For render stage
    code: Optional[str] = None
    scene_name: Optional[str] = None


class StageResult(BaseModel):
    """Result of a stage execution."""

    stage: str
    success: bool
    output: Dict[str, Any]
    duration_ms: int
    prompts_used: Optional[PromptPreview] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Task management
# ---------------------------------------------------------------------------


class TaskStatusResponse(BaseModel):
    """Status of an async task."""

    task_id: str
    status: str = Field(..., description="pending | running | completed | failed")
    stage: str
    progress: Optional[str] = None
    result: Optional[StageResult] = None


# ---------------------------------------------------------------------------
# Interest / config
# ---------------------------------------------------------------------------


class InterestDetail(BaseModel):
    """Detailed information about an interest profile."""

    name: str
    display_name: str
    description: str
    famous_figures: List[str]
    example_scenarios: List[str]
    fun_facts: List[str]
    cultural_references: List[str]
    visual_theme: Dict[str, str]


class PlaygroundConfig(BaseModel):
    """Non-sensitive engine configuration for the UI."""

    llm_provider: str
    model: str
    animation_style: str
    video_quality: str
    max_retries: int
    temperature: float
    max_tokens: int
    available_interests: List[str]
    available_styles: List[str] = ["dark", "light"]
    available_qualities: List[str] = ["l", "m", "h", "p", "k"]


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------


class TextbookUploadResponse(BaseModel):
    """Response after uploading textbook content."""

    content: str
    length: int
    preview: str = Field(..., description="First 500 characters")
