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
        None, description="Textbook markdown (for personalize / extract_concepts / generate_animation)"
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
    grade_level: Optional[str] = Field(None, description="Student's grade level (e.g. 8th grade)")
    city: Optional[str] = Field(None, description="Student's city (e.g. San Francisco)")
    state: Optional[str] = Field(None, description="Student's state (e.g. California)")
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
    grade_level: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    favorite_figure: Optional[str] = None
    favorite_team: Optional[str] = None

    # Data service integration
    concept_ids: Optional[List[str]] = Field(
        None,
        description="Concept IDs this content covers (e.g. ['algebra1.linear_equations.general_equations'])",
    )
    grade: Optional[str] = Field(
        None, description="Target grade level (e.g. 'grade_8')"
    )

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


class DataServiceStatus(BaseModel):
    """Connectivity status for the tutor data service backends."""

    postgres_available: bool = False
    neo4j_available: bool = False
    message: str = "Not configured"


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
    data_service: Optional[DataServiceStatus] = None


# ---------------------------------------------------------------------------
# Prompt persistence (GCS)
# ---------------------------------------------------------------------------


class StagePrompts(BaseModel):
    """System + user prompts for a single pipeline stage."""

    system_prompt: str = ""
    user_prompt: str = ""


class PromptSaveRequest(BaseModel):
    """Request body for saving the current prompt session to GCS."""

    prompts: Dict[str, StagePrompts] = Field(
        ...,
        description="Prompts keyed by stage: personalize, extract_concepts, generate_animation",
    )
    settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="topic, interest, animation_style, audience_level, temperature, max_tokens",
    )
    student_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="student_name, preferred_address, grade_level, city, state, etc.",
    )
    notes: str = Field("", description="Optional notes about this version")


class PromptSaveResponse(BaseModel):
    """Response after a successful save."""

    saved_at: str
    path: str


class PromptHistoryItem(BaseModel):
    """One entry in the saved-prompt history list."""

    timestamp: str
    path: str
    size: Optional[int] = None


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------


class TextbookUploadResponse(BaseModel):
    """Response after uploading textbook content."""

    content: str
    length: int
    preview: str = Field(..., description="First 500 characters")
    source: str = Field("raw", description="How content was obtained: mathpix | mathpix_cached | pymupdf | pdfplumber | raw")
    cached_md_path: Optional[str] = Field(None, description="Path to cached .md file (for PDFs parsed via Mathpix)")
