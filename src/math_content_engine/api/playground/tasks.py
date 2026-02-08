"""Async task manager with SSE progress streaming."""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Callable, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class TaskInfo:
    """Information about a running or completed task."""

    task_id: str
    stage: str
    status: str = "pending"  # pending | running | completed | failed
    progress_messages: list = field(default_factory=list)
    result: Any = None
    error: Optional[str] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None


class TaskManager:
    """Manages background tasks with SSE progress updates.

    Tasks run synchronous pipeline functions in a thread pool via
    ``asyncio.to_thread`` so the FastAPI event loop stays responsive.
    """

    def __init__(self) -> None:
        self._tasks: Dict[str, TaskInfo] = {}
        self._events: Dict[str, asyncio.Queue] = {}

    def create_task(self, stage: str) -> str:
        """Create a new task and return its ID."""
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        self._tasks[task_id] = TaskInfo(task_id=task_id, stage=stage)
        self._events[task_id] = asyncio.Queue()
        return task_id

    async def run_in_background(
        self,
        task_id: str,
        func: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run *func* in a background thread and stream events."""
        task = self._tasks[task_id]
        task.status = "running"
        task.started_at = time.time()
        await self._send_event(task_id, "status", "running")

        try:
            result = await asyncio.to_thread(func, *args, **kwargs)
            task.result = result
            task.status = "completed"
            task.completed_at = time.time()
            await self._send_event(task_id, "result", result)
            await self._send_event(task_id, "completed", "done")
        except Exception as exc:
            logger.exception("Background task %s failed", task_id)
            task.error = str(exc)
            task.status = "failed"
            task.completed_at = time.time()
            await self._send_event(task_id, "error", str(exc))
            await self._send_event(task_id, "failed", str(exc))

    async def send_progress(self, task_id: str, message: str) -> None:
        """Push a progress message to the SSE stream."""
        if task_id in self._tasks:
            self._tasks[task_id].progress_messages.append(message)
            await self._send_event(task_id, "progress", message)

    # ------------------------------------------------------------------
    # SSE streaming
    # ------------------------------------------------------------------

    async def stream_events(self, task_id: str) -> AsyncGenerator[str, None]:
        """Yield SSE-formatted strings for a specific task."""
        queue = self._events.get(task_id)
        if queue is None:
            yield _format_sse("error", "Unknown task")
            return

        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=300)
            except asyncio.TimeoutError:
                yield _format_sse("timeout", "Stream timed out")
                return

            yield _format_sse(event["event"], event["data"])

            if event["event"] in ("completed", "failed"):
                return

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """Return task info or ``None``."""
        return self._tasks.get(task_id)

    def cleanup_old_tasks(self, max_age_seconds: int = 3600) -> int:
        """Remove completed tasks older than *max_age_seconds*."""
        now = time.time()
        to_remove = [
            tid
            for tid, t in self._tasks.items()
            if t.completed_at and (now - t.completed_at) > max_age_seconds
        ]
        for tid in to_remove:
            del self._tasks[tid]
            self._events.pop(tid, None)
        return len(to_remove)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _send_event(self, task_id: str, event_type: str, data: Any) -> None:
        if task_id in self._events:
            await self._events[task_id].put({"event": event_type, "data": data})


def _format_sse(event: str, data: Any) -> str:
    """Format a single SSE message."""
    if isinstance(data, (dict, list)):
        payload = json.dumps(data, default=str)
    else:
        payload = str(data)
    return f"event: {event}\ndata: {payload}\n\n"
