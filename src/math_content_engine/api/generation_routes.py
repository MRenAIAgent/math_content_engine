"""
Generation API routes — on-demand content generation for the tutor.

POST /api/v1/generate   — generate a video for a concept/theme/grade
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

generation_router = APIRouter(prefix="/api/v1/generate", tags=["generation"])


# ── Request / Response models ────────────────────────────────────────────

class GenerateRequest(BaseModel):
    """Request body for on-demand content generation."""

    concept_id: str = Field(..., description="Concept ID (e.g. 'AT-24')")
    topic: str = Field(..., description="Human-readable topic name")
    theme: str = Field(default="neutral", description="Content theme (e.g. 'sports_basketball')")
    grade: str = Field(default="grade_8", description="Target grade level")
    audience_level: str = Field(default="high school", description="Audience level")
    requirements: str = Field(default="", description="Additional requirements")
    content_type: str = Field(default="video", description="'video', 'exercise', or 'both'")

    # Optional student context forwarded from the tutor
    student_name: Optional[str] = None
    student_interests: List[str] = Field(default_factory=list)
    student_grade_level: Optional[str] = None

    # Mastery context (for adaptive difficulty)
    mastery_level: Optional[float] = None
    recommended_dimension: Optional[str] = None


class GenerateResponse(BaseModel):
    """Response after a generation request is accepted / completed."""

    status: str  # "completed", "failed"
    video_id: Optional[str] = None
    video_path: Optional[str] = None
    scene_name: Optional[str] = None
    code: Optional[str] = None
    concept_id: str
    theme: str
    grade: str
    error_message: Optional[str] = None


# ── Route ────────────────────────────────────────────────────────────────

@generation_router.post("", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest) -> GenerateResponse:
    """
    Generate a math animation video on demand.

    The engine creates a Manim animation for the given concept/topic,
    personalised with the requested theme.  When ``PUBLISH_EVENTS=true``
    and Redis is available the result is also published to the
    ``content_events`` stream for tutor ingestion.
    """
    from math_content_engine.config import Config
    from math_content_engine.engine import MathContentEngine
    from math_content_engine.api.storage import VideoStorage
    from math_content_engine.personalization.theme_mapper import theme_to_interest

    # Map theme -> engine interest string
    interest = theme_to_interest(request.theme)

    # Build a StudentProfile if student context is provided
    student_profile = None
    if request.student_name or request.student_interests:
        from math_content_engine.personalization import StudentProfile

        student_profile = StudentProfile(
            name=request.student_name or "Student",
            grade_level=request.student_grade_level or request.grade,
            interests=request.student_interests,
        )

    try:
        config = Config.from_env()

        # Initialise storage (re-use the SQLite DB path from env)
        db_path_str = os.getenv("MATH_ENGINE_DB_PATH", "./data/videos.db")
        from pathlib import Path

        storage = VideoStorage(Path(db_path_str))

        engine = MathContentEngine(
            config=config,
            interest=interest if interest != "neutral" else None,
            storage=storage,
        )

        # Run the synchronous generate() in a thread so we don't block the
        # event loop (Manim rendering is CPU-bound).
        result = await asyncio.to_thread(
            engine.generate,
            topic=request.topic,
            requirements=request.requirements,
            audience_level=request.audience_level,
            interest=interest if interest != "neutral" else None,
            student_profile=student_profile,
        )

        # Optionally publish to Redis stream
        if result.success and config.publish_events and config.redis_url:
            await _publish_video_event(config, result, request)

        return GenerateResponse(
            status="completed" if result.success else "failed",
            video_id=result.video_id,
            video_path=str(result.video_path) if result.video_path else None,
            scene_name=result.scene_name,
            code=result.code,
            concept_id=request.concept_id,
            theme=request.theme,
            grade=request.grade,
            error_message=result.error_message,
        )
    except Exception as e:
        logger.exception("Generation failed for concept %s", request.concept_id)
        raise HTTPException(status_code=500, detail=str(e))


# ── Helpers ──────────────────────────────────────────────────────────────

async def _publish_video_event(config, result, request: GenerateRequest) -> None:
    """Publish the generated video to the Redis content_events stream."""
    try:
        import redis.asyncio as aioredis
        from math_content_engine.integration.publisher import ContentPublisher
        from math_content_engine.integration.schemas import VideoContentDTO
        from datetime import datetime, timezone

        redis_client = aioredis.from_url(config.redis_url, decode_responses=True)
        publisher = ContentPublisher(
            redis_client=redis_client,
            stream_name=config.redis_stream_name,
        )

        dto = VideoContentDTO(
            video_id=result.video_id or "",
            concept_ids=[request.concept_id],
            topic=request.topic,
            scene_name=result.scene_name,
            theme=request.theme,
            grade=request.grade,
            source_path=str(result.video_path) if result.video_path else "",
            code=result.code,
            style=config.animation_style.value,
            quality=config.video_quality.value,
            llm_provider=config.llm_provider.value,
            llm_model=config.get_model(),
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        await publisher.publish_video(dto)
        await redis_client.aclose()
    except Exception:
        logger.exception("Failed to publish video event to Redis")
