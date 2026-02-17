"""
Priority Generator Worker — generates content for queued requests.

Polls the tutor's ``content_generation_requests`` table (via its API)
for pending work, generates videos/exercises, and publishes results
to the Redis ``content_events`` stream.

Usage:
    python -m math_content_engine.workers.priority_generator
"""

from __future__ import annotations

import asyncio
import logging
import os
import signal

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


async def fetch_pending_requests(
    tutor_api_url: str,
    limit: int = 5,
) -> list:
    """Fetch top-priority pending generation requests from the tutor API."""
    url = f"{tutor_api_url}/api/v1/generation-requests?status=pending&limit={limit}"
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            logger.exception("Failed to fetch pending requests from %s", url)
            return []


async def mark_request_status(
    tutor_api_url: str,
    request_id: str,
    status: str,
    result_id: str | None = None,
    error_message: str | None = None,
) -> None:
    """Update a generation request's status via the tutor API."""
    url = f"{tutor_api_url}/api/v1/generation-requests/{request_id}"
    payload = {"status": status}
    if result_id:
        payload["result_id"] = result_id
    if error_message:
        payload["error_message"] = error_message

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.patch(url, json=payload)
            resp.raise_for_status()
        except Exception:
            logger.exception("Failed to update request %s to %s", request_id, status)


def generate_video_sync(
    concept_id: str,
    topic: str,
    theme: str,
    grade: str,
    mastery_context: dict | None = None,
) -> dict:
    """
    Generate a video using the local MathContentEngine.

    This is a SYNC function (CPU-bound Manim rendering). Must be called
    via ``asyncio.to_thread()`` to avoid blocking the event loop.

    Returns dict with keys: success, video_id, video_path, scene_name, code, error_message.
    """
    from math_content_engine.config import Config
    from math_content_engine.engine import MathContentEngine
    from math_content_engine.api.storage import VideoStorage
    from math_content_engine.personalization.theme_mapper import theme_to_interest
    from pathlib import Path

    interest = theme_to_interest(theme)
    config = Config.from_env()
    db_path = Path(os.getenv("MATH_ENGINE_DB_PATH", "./data/videos.db"))
    storage = VideoStorage(db_path)

    # Optionally create TutorDataServiceWriter for PostgreSQL integration
    tutor_writer = None
    tutor_db_url = os.getenv("TUTOR_DATABASE_URL")
    if tutor_db_url:
        from math_content_engine.integration.tutor_writer import TutorDataServiceWriter
        tutor_writer = TutorDataServiceWriter(database_url=tutor_db_url)

    engine = MathContentEngine(
        config=config,
        interest=interest if interest != "neutral" else None,
        storage=storage,
        tutor_writer=tutor_writer,
    )

    # Adapt topic from concept_id if not provided
    if not topic:
        topic = concept_id.replace("-", " ").replace("_", " ")

    result = engine.generate(
        topic=topic,
        requirements="",
        interest=interest if interest != "neutral" else None,
        concept_ids=[concept_id],
        grade=grade,
    )

    return {
        "success": result.success,
        "video_id": result.video_id,
        "video_path": str(result.video_path) if result.video_path else None,
        "scene_name": result.scene_name,
        "code": result.code,
        "error_message": result.error_message,
    }


async def publish_result(
    config_redis_url: str,
    stream_name: str,
    gen_result: dict,
    concept_id: str,
    theme: str,
    grade: str,
) -> None:
    """Publish generated video to Redis content_events stream."""
    if not gen_result["success"]:
        return

    try:
        import redis.asyncio as aioredis
        from math_content_engine.integration.publisher import ContentPublisher
        from math_content_engine.integration.schemas import VideoContentDTO
        from math_content_engine.config import Config
        from datetime import datetime, timezone

        config = Config.from_env()
        redis_client = aioredis.from_url(config_redis_url, decode_responses=True)
        publisher = ContentPublisher(redis_client=redis_client, stream_name=stream_name)

        dto = VideoContentDTO(
            video_id=gen_result["video_id"] or "",
            concept_ids=[concept_id],
            topic=concept_id,
            scene_name=gen_result["scene_name"],
            theme=theme,
            grade=grade,
            source_path=gen_result["video_path"] or "",
            code=gen_result["code"],
            style=config.animation_style.value,
            quality=config.video_quality.value,
            llm_provider=config.llm_provider.value,
            llm_model=config.get_model(),
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        await publisher.publish_video(dto)
        await redis_client.aclose()
    except Exception:
        logger.exception("Failed to publish video event for %s", concept_id)


async def process_one(tutor_api_url: str, request: dict) -> None:
    """Process a single generation request."""
    request_id = str(request["id"])
    concept_id = request["concept_id"]
    theme = request.get("theme", "neutral")
    grade = request.get("grade", "grade_8")
    mastery_context = request.get("mastery_context")

    logger.info(
        "Processing request %s: concept=%s theme=%s grade=%s",
        request_id, concept_id, theme, grade,
    )

    # Mark in-progress
    await mark_request_status(tutor_api_url, request_id, "in_progress")

    try:
        # Run CPU-bound Manim generation in a thread to avoid blocking event loop
        result = await asyncio.to_thread(
            generate_video_sync, concept_id, concept_id, theme, grade, mastery_context
        )

        if result["success"]:
            # Publish to Redis stream
            redis_url = os.getenv("REDIS_URL", "redis://localhost:16379")
            stream_name = os.getenv("REDIS_STREAM_NAME", "content_events")
            await publish_result(redis_url, stream_name, result, concept_id, theme, grade)

            await mark_request_status(
                tutor_api_url, request_id, "completed",
                result_id=result["video_id"],
            )
            logger.info("Completed request %s -> video %s", request_id, result["video_id"])
        else:
            await mark_request_status(
                tutor_api_url, request_id, "failed",
                error_message=result["error_message"],
            )
            logger.warning("Request %s failed: %s", request_id, result["error_message"])
    except Exception as e:
        logger.exception("Error processing request %s", request_id)
        await mark_request_status(
            tutor_api_url, request_id, "failed",
            error_message=str(e),
        )


async def poll_loop(
    tutor_api_url: str,
    poll_interval: int = 30,
    batch_size: int = 3,
) -> None:
    """
    Main polling loop.

    Fetches pending requests from the tutor API and processes them
    one at a time (video generation is CPU-heavy).
    """
    logger.info(
        "Priority generator starting — polling %s every %ds",
        tutor_api_url, poll_interval,
    )

    while True:
        try:
            requests = await fetch_pending_requests(tutor_api_url, limit=batch_size)

            if requests:
                logger.info("Found %d pending requests", len(requests))
                for req in requests:
                    await process_one(tutor_api_url, req)
            else:
                logger.debug("No pending requests")

        except Exception:
            logger.exception("Error in poll loop")

        await asyncio.sleep(poll_interval)


async def main() -> None:
    """Entry point."""
    tutor_api_url = os.getenv("TUTOR_API_URL", "http://localhost:8080")
    poll_interval = int(os.getenv("POLL_INTERVAL", "30"))
    batch_size = int(os.getenv("BATCH_SIZE", "3"))

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def shutdown():
        logger.info("Shutdown signal received")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown)

    poll_task = asyncio.create_task(
        poll_loop(tutor_api_url, poll_interval, batch_size)
    )

    # Wait for shutdown or task failure
    done, pending = await asyncio.wait(
        [poll_task, asyncio.create_task(stop_event.wait())],
        return_when=asyncio.FIRST_COMPLETED,
    )

    for t in pending:
        t.cancel()

    logger.info("Priority generator stopped.")


if __name__ == "__main__":
    asyncio.run(main())
