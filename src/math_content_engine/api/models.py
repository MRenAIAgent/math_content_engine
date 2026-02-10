"""
Pydantic models for video metadata and API requests/responses.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict

# Import centralized enums
from ..constants import VideoQuality as _VideoQuality
from ..constants import AnimationStyle as _AnimationStyle


# Pydantic-compatible versions (str, Enum)
class VideoQuality(str, Enum):
    """Video quality levels (Pydantic-compatible)."""
    LOW = "l"
    MEDIUM = "m"
    HIGH = "h"
    PRODUCTION = "p"
    FOURK = "k"


class AnimationStyle(str, Enum):
    """Animation visual style (Pydantic-compatible)."""
    DARK = "dark"
    LIGHT = "light"


class VideoMetadata(BaseModel):
    """Complete video metadata stored in the database."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # Core info
    topic: str
    scene_name: str
    video_path: str
    code: str

    # Integration fields
    concept_ids: List[str] = Field(default_factory=list)
    grade: Optional[str] = None

    # Generation settings
    requirements: Optional[str] = None
    audience_level: str = "high school"
    interest: Optional[str] = None
    style: AnimationStyle = AnimationStyle.DARK
    quality: VideoQuality = VideoQuality.MEDIUM

    # LLM metadata
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None

    # Performance metrics
    generation_attempts: int = 1
    render_attempts: int = 1
    total_attempts: int = 1
    generation_time_ms: Optional[int] = None
    render_time_ms: Optional[int] = None

    # File metadata
    file_size_bytes: Optional[int] = None
    duration_seconds: Optional[float] = None

    # Status
    success: bool = True
    error_message: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)


class VideoCreate(BaseModel):
    """Request model for creating a new video record."""
    topic: str
    scene_name: str
    video_path: str
    code: str

    # Integration fields
    concept_ids: List[str] = Field(default_factory=list)
    grade: Optional[str] = None

    # Optional fields
    requirements: Optional[str] = None
    audience_level: str = "high school"
    interest: Optional[str] = None
    style: AnimationStyle = AnimationStyle.DARK
    quality: VideoQuality = VideoQuality.MEDIUM

    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None

    generation_attempts: int = 1
    render_attempts: int = 1
    total_attempts: int = 1
    generation_time_ms: Optional[int] = None
    render_time_ms: Optional[int] = None

    file_size_bytes: Optional[int] = None
    duration_seconds: Optional[float] = None

    success: bool = True
    error_message: Optional[str] = None


class VideoResponse(BaseModel):
    """Response model for a single video."""
    id: str
    topic: str
    scene_name: str
    video_path: str

    requirements: Optional[str] = None
    audience_level: str
    interest: Optional[str] = None
    style: AnimationStyle
    quality: VideoQuality

    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None

    generation_attempts: int
    render_attempts: int
    render_time_ms: Optional[int] = None

    file_size_bytes: Optional[int] = None
    duration_seconds: Optional[float] = None

    success: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VideoListResponse(BaseModel):
    """Response model for listing videos."""
    videos: List[VideoResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class VideoSearchParams(BaseModel):
    """Search/filter parameters for listing videos."""
    topic: Optional[str] = None
    scene_name: Optional[str] = None
    interest: Optional[str] = None
    grade: Optional[str] = None
    style: Optional[AnimationStyle] = None
    quality: Optional[VideoQuality] = None
    success_only: bool = True
    page: int = 1
    page_size: int = 20
