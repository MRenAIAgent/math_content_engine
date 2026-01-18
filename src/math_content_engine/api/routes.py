"""
FastAPI routes for video retrieval API.
"""

import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import FileResponse

from .models import (
    VideoMetadata,
    VideoCreate,
    VideoResponse,
    VideoListResponse,
    VideoSearchParams,
    AnimationStyle,
    VideoQuality,
)
from .storage import VideoStorage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/videos", tags=["videos"])

# Storage instance (will be set by server.py)
_storage: Optional[VideoStorage] = None


def get_storage() -> VideoStorage:
    """Dependency to get storage instance."""
    if _storage is None:
        raise HTTPException(status_code=500, detail="Storage not initialized")
    return _storage


def set_storage(storage: VideoStorage) -> None:
    """Set the storage instance."""
    global _storage
    _storage = storage


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video_metadata(
    video_id: str,
    storage: VideoStorage = Depends(get_storage)
) -> VideoResponse:
    """
    Get video metadata by ID.

    Args:
        video_id: The unique video identifier

    Returns:
        Video metadata including path, topic, generation info
    """
    video = storage.get_by_id(video_id)
    if video is None:
        raise HTTPException(status_code=404, detail=f"Video not found: {video_id}")

    return VideoResponse(
        id=video.id,
        topic=video.topic,
        scene_name=video.scene_name,
        video_path=video.video_path,
        requirements=video.requirements,
        audience_level=video.audience_level,
        interest=video.interest,
        style=video.style,
        quality=video.quality,
        llm_provider=video.llm_provider,
        llm_model=video.llm_model,
        generation_attempts=video.generation_attempts,
        render_attempts=video.render_attempts,
        render_time_ms=video.render_time_ms,
        file_size_bytes=video.file_size_bytes,
        duration_seconds=video.duration_seconds,
        success=video.success,
        created_at=video.created_at,
    )


@router.get("/{video_id}/file")
async def get_video_file(
    video_id: str,
    storage: VideoStorage = Depends(get_storage)
) -> FileResponse:
    """
    Download the actual video file by ID.

    Args:
        video_id: The unique video identifier

    Returns:
        The video file as a download
    """
    video = storage.get_by_id(video_id)
    if video is None:
        raise HTTPException(status_code=404, detail=f"Video not found: {video_id}")

    video_path = Path(video.video_path)
    if not video_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Video file not found on disk: {video.video_path}"
        )

    # Determine media type based on extension
    extension = video_path.suffix.lower()
    media_type = "video/mp4" if extension == ".mp4" else "video/quicktime"

    return FileResponse(
        path=video_path,
        media_type=media_type,
        filename=video_path.name,
    )


@router.get("/{video_id}/code")
async def get_video_code(
    video_id: str,
    storage: VideoStorage = Depends(get_storage)
) -> dict:
    """
    Get the Manim code used to generate the video.

    Args:
        video_id: The unique video identifier

    Returns:
        The Manim Python code as text
    """
    video = storage.get_by_id(video_id)
    if video is None:
        raise HTTPException(status_code=404, detail=f"Video not found: {video_id}")

    return {
        "id": video.id,
        "scene_name": video.scene_name,
        "code": video.code,
    }


@router.get("", response_model=VideoListResponse)
async def list_videos(
    topic: Optional[str] = Query(None, description="Filter by topic (partial match)"),
    scene_name: Optional[str] = Query(None, description="Filter by scene name"),
    interest: Optional[str] = Query(None, description="Filter by interest"),
    style: Optional[AnimationStyle] = Query(None, description="Filter by style"),
    quality: Optional[VideoQuality] = Query(None, description="Filter by quality"),
    success_only: bool = Query(True, description="Only show successful videos"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    storage: VideoStorage = Depends(get_storage)
) -> VideoListResponse:
    """
    List videos with optional filtering and pagination.

    Returns:
        Paginated list of video metadata
    """
    params = VideoSearchParams(
        topic=topic,
        scene_name=scene_name,
        interest=interest,
        style=style,
        quality=quality,
        success_only=success_only,
        page=page,
        page_size=page_size,
    )

    videos, total = storage.list_videos(params)

    return VideoListResponse(
        videos=[
            VideoResponse(
                id=v.id,
                topic=v.topic,
                scene_name=v.scene_name,
                video_path=v.video_path,
                requirements=v.requirements,
                audience_level=v.audience_level,
                interest=v.interest,
                style=v.style,
                quality=v.quality,
                llm_provider=v.llm_provider,
                llm_model=v.llm_model,
                generation_attempts=v.generation_attempts,
                render_attempts=v.render_attempts,
                render_time_ms=v.render_time_ms,
                file_size_bytes=v.file_size_bytes,
                duration_seconds=v.duration_seconds,
                success=v.success,
                created_at=v.created_at,
            )
            for v in videos
        ],
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total,
    )


@router.post("", response_model=VideoResponse, status_code=201)
async def create_video(
    video: VideoCreate,
    storage: VideoStorage = Depends(get_storage)
) -> VideoResponse:
    """
    Create a new video record.

    This endpoint is typically called by the engine after generating a video.

    Args:
        video: Video metadata to store

    Returns:
        Created video metadata with assigned ID
    """
    metadata = storage.save(video)

    return VideoResponse(
        id=metadata.id,
        topic=metadata.topic,
        scene_name=metadata.scene_name,
        video_path=metadata.video_path,
        requirements=metadata.requirements,
        audience_level=metadata.audience_level,
        interest=metadata.interest,
        style=metadata.style,
        quality=metadata.quality,
        llm_provider=metadata.llm_provider,
        llm_model=metadata.llm_model,
        generation_attempts=metadata.generation_attempts,
        render_attempts=metadata.render_attempts,
        render_time_ms=metadata.render_time_ms,
        file_size_bytes=metadata.file_size_bytes,
        duration_seconds=metadata.duration_seconds,
        success=metadata.success,
        created_at=metadata.created_at,
    )


@router.delete("/{video_id}", status_code=204)
async def delete_video(
    video_id: str,
    storage: VideoStorage = Depends(get_storage)
) -> None:
    """
    Delete a video record.

    Note: This only deletes the metadata, not the actual video file.

    Args:
        video_id: The unique video identifier
    """
    if not storage.delete(video_id):
        raise HTTPException(status_code=404, detail=f"Video not found: {video_id}")


@router.get("/stats/summary")
async def get_stats(
    storage: VideoStorage = Depends(get_storage)
) -> dict:
    """
    Get video storage statistics.

    Returns:
        Summary statistics about stored videos
    """
    return storage.get_stats()
