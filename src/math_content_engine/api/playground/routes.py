"""FastAPI routes for the playground API."""

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from fastapi.responses import FileResponse, StreamingResponse

from ...config import Config
from ...personalization import get_interest_profile, list_available_interests
from .models import (
    InterestDetail,
    PlaygroundConfig,
    PromptPreview,
    PromptPreviewRequest,
    StageExecuteRequest,
    StageResult,
    TaskStatusResponse,
    TextbookUploadResponse,
)
from .pipeline_runner import (
    PLAYGROUND_OUTPUT_DIR,
    run_animation_generation,
    run_concept_extraction,
    run_personalization,
    run_render,
    run_textbook_parse,
)
from .prompt_builder import (
    preview_animation_prompts,
    preview_concept_extraction_prompts,
    preview_personalization_prompts,
)
from .tasks import TaskManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/playground", tags=["playground"])

# Singleton task manager (lives for the server's lifetime)
_task_manager = TaskManager()


# ---------------------------------------------------------------------------
# Configuration & metadata
# ---------------------------------------------------------------------------


@router.get("/config", response_model=PlaygroundConfig)
async def get_config() -> PlaygroundConfig:
    """Return non-sensitive engine configuration for the UI."""
    config = Config.from_env()
    return PlaygroundConfig(
        llm_provider=config.llm_provider.value,
        model=config.get_model(),
        animation_style=config.animation_style.value,
        video_quality=config.video_quality.value,
        max_retries=config.max_retries,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        available_interests=list(list_available_interests()),
    )


@router.get("/interests", response_model=list[InterestDetail])
async def list_interests() -> list[InterestDetail]:
    """Return all available interest profiles."""
    result = []
    for name in list_available_interests():
        profile = get_interest_profile(name)
        if profile:
            result.append(
                InterestDetail(
                    name=profile.name,
                    display_name=profile.display_name,
                    description=profile.description,
                    famous_figures=profile.famous_figures[:8],
                    example_scenarios=profile.example_scenarios[:6],
                    fun_facts=profile.fun_facts[:5],
                    cultural_references=getattr(
                        profile, "cultural_references", []
                    )[:4],
                    visual_theme=profile.visual_themes,
                )
            )
    return result


@router.get("/interests/{name}", response_model=InterestDetail)
async def get_interest(name: str) -> InterestDetail:
    """Return details for a specific interest."""
    profile = get_interest_profile(name)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Unknown interest: {name}")
    return InterestDetail(
        name=profile.name,
        display_name=profile.display_name,
        description=profile.description,
        famous_figures=profile.famous_figures,
        example_scenarios=profile.example_scenarios,
        fun_facts=profile.fun_facts,
        cultural_references=getattr(profile, "cultural_references", []),
        visual_theme=profile.visual_themes,
    )


# ---------------------------------------------------------------------------
# Prompt preview
# ---------------------------------------------------------------------------


@router.post("/prompts/preview", response_model=PromptPreview)
async def preview_prompts(req: PromptPreviewRequest) -> PromptPreview:
    """Preview the prompts that would be sent to the LLM (no execution)."""
    if req.stage == "personalize":
        if not req.textbook_content:
            raise HTTPException(400, "textbook_content required for personalize")
        if not req.interest:
            raise HTTPException(400, "interest required for personalize")
        return preview_personalization_prompts(req.textbook_content, req.interest)

    if req.stage == "extract_concepts":
        if not req.textbook_content:
            raise HTTPException(400, "textbook_content required for extract_concepts")
        return preview_concept_extraction_prompts(req.textbook_content)

    if req.stage == "generate_animation":
        if not req.topic:
            raise HTTPException(400, "topic required for generate_animation")
        return preview_animation_prompts(
            topic=req.topic,
            requirements=req.requirements or "",
            audience_level=req.audience_level,
            interest=req.interest,
            animation_style=req.animation_style,
            student_name=req.student_name,
        )

    raise HTTPException(400, f"Unknown stage: {req.stage}")


# ---------------------------------------------------------------------------
# Stage execution (async via task manager)
# ---------------------------------------------------------------------------


@router.post("/execute")
async def execute_stage(req: StageExecuteRequest) -> dict:
    """Start a pipeline stage in the background and return a task ID."""
    config = Config.from_env()

    # Apply LLM parameter overrides
    if req.temperature is not None:
        config.temperature = req.temperature
    if req.max_tokens is not None:
        config.max_tokens = req.max_tokens

    sys_override = req.prompt_override.system_prompt if req.prompt_override else None
    usr_override = req.prompt_override.user_prompt if req.prompt_override else None

    task_id = _task_manager.create_task(req.stage)

    if req.stage == "personalize":
        if not req.textbook_content or not req.interest:
            raise HTTPException(400, "textbook_content and interest required")
        asyncio.create_task(
            _task_manager.run_in_background(
                task_id,
                run_personalization,
                textbook_content=req.textbook_content,
                interest=req.interest,
                config=config,
                system_prompt_override=sys_override,
                user_prompt_override=usr_override,
            )
        )

    elif req.stage == "extract_concepts":
        if not req.textbook_content:
            raise HTTPException(400, "textbook_content required")
        asyncio.create_task(
            _task_manager.run_in_background(
                task_id,
                run_concept_extraction,
                markdown_content=req.textbook_content,
                config=config,
                system_prompt_override=sys_override,
                user_prompt_override=usr_override,
            )
        )

    elif req.stage == "generate_animation":
        if not req.topic:
            raise HTTPException(400, "topic required")
        asyncio.create_task(
            _task_manager.run_in_background(
                task_id,
                run_animation_generation,
                topic=req.topic,
                requirements=req.requirements or "",
                audience_level=req.audience_level,
                interest=req.interest,
                animation_style=req.animation_style,
                config=config,
                system_prompt_override=sys_override,
                user_prompt_override=usr_override,
            )
        )

    elif req.stage == "render":
        if not req.code or not req.scene_name:
            raise HTTPException(400, "code and scene_name required")
        asyncio.create_task(
            _task_manager.run_in_background(
                task_id,
                run_render,
                code=req.code,
                scene_name=req.scene_name,
                quality=req.video_quality,
                config=config,
            )
        )

    elif req.stage == "parse_examples":
        if not req.textbook_content:
            raise HTTPException(400, "textbook_content required")
        asyncio.create_task(
            _task_manager.run_in_background(
                task_id,
                run_textbook_parse,
                textbook_content=req.textbook_content,
            )
        )

    else:
        raise HTTPException(400, f"Unknown stage: {req.stage}")

    return {"task_id": task_id}


# ---------------------------------------------------------------------------
# Task status & streaming
# ---------------------------------------------------------------------------


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    """Poll for the status of a background task."""
    task = _task_manager.get_task(task_id)
    if task is None:
        raise HTTPException(404, f"Unknown task: {task_id}")

    result = None
    if task.result is not None:
        result = StageResult(
            stage=task.stage,
            success=not bool(task.error),
            output=task.result if isinstance(task.result, dict) else {},
            duration_ms=int(
                ((task.completed_at or 0) - (task.started_at or 0)) * 1000
            ),
            error=task.error,
        )

    return TaskStatusResponse(
        task_id=task.task_id,
        status=task.status,
        stage=task.stage,
        progress=task.progress_messages[-1] if task.progress_messages else None,
        result=result,
    )


@router.get("/tasks/{task_id}/stream")
async def stream_task(task_id: str) -> StreamingResponse:
    """SSE stream of progress events for a task."""
    task = _task_manager.get_task(task_id)
    if task is None:
        raise HTTPException(404, f"Unknown task: {task_id}")

    return StreamingResponse(
        _task_manager.stream_events(task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# Content upload
# ---------------------------------------------------------------------------


@router.post("/upload/textbook", response_model=TextbookUploadResponse)
async def upload_textbook(
    file: Optional[UploadFile] = File(None),
    content: Optional[str] = Body(None, embed=True),
) -> TextbookUploadResponse:
    """Upload textbook content — either as a file or as raw text."""
    if file:
        raw = await file.read()
        text = raw.decode("utf-8", errors="replace")
    elif content:
        text = content
    else:
        raise HTTPException(400, "Provide a file or content body")

    return TextbookUploadResponse(
        content=text,
        length=len(text),
        preview=text[:500],
    )


# ---------------------------------------------------------------------------
# File serving (videos / code)
# ---------------------------------------------------------------------------


@router.get("/files/video/{filename}")
async def serve_video(filename: str) -> FileResponse:
    """Serve a rendered video file."""
    video_dir = PLAYGROUND_OUTPUT_DIR / "videos"
    path = video_dir / filename
    if not path.exists() or not path.is_file():
        raise HTTPException(404, f"Video file not found: {filename}")
    return FileResponse(
        path=str(path),
        media_type="video/mp4",
        filename=filename,
    )


@router.get("/files/code/{filename}")
async def serve_code(filename: str) -> FileResponse:
    """Serve a generated Python code file."""
    code_dir = PLAYGROUND_OUTPUT_DIR / "code"
    path = code_dir / filename
    if not path.exists() or not path.is_file():
        raise HTTPException(404, f"Code file not found: {filename}")
    return FileResponse(
        path=str(path),
        media_type="text/x-python",
        filename=filename,
    )
