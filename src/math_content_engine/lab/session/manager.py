"""Session manager for prompt engineering lab."""

import uuid
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

from ..prompt.models import AnimationPrompt, GenerationResult, PromptSession
from .storage import SessionStorage


class SessionManager:
    """Manages prompt engineering sessions and generation workflow."""

    def __init__(
        self,
        storage: Optional[SessionStorage] = None,
        output_dir: Optional[Path] = None,
    ):
        """Initialize session manager."""
        self.storage = storage or SessionStorage()
        self.output_dir = output_dir or Path.cwd() / ".lab" / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Will be set when engine is available
        self._engine = None
        self._code_generator = None
        self._renderer = None

    def _get_engine(self):
        """Lazy load the math content engine."""
        if self._engine is None:
            from ...engine import MathContentEngine
            from ...config import Config

            config = Config.from_env()
            self._engine = MathContentEngine(config)
        return self._engine

    def _get_code_generator(self):
        """Lazy load the code generator."""
        if self._code_generator is None:
            from ...generator.code_generator import ManimCodeGenerator
            from ...config import Config

            config = Config.from_env()
            self._code_generator = ManimCodeGenerator(config)
        return self._code_generator

    def _get_renderer(self):
        """Lazy load the renderer."""
        if self._renderer is None:
            from ...renderer.manim_renderer import ManimRenderer
            from ...config import Config

            config = Config.from_env()
            self._renderer = ManimRenderer(config)
        return self._renderer

    def create_session(self, topic: str, requirements: Optional[list[str]] = None) -> PromptSession:
        """Create a new prompt engineering session."""
        session_id = f"ses_{uuid.uuid4().hex[:8]}"
        session = PromptSession(session_id=session_id)

        prompt = AnimationPrompt(
            topic=topic,
            requirements=requirements or [],
        )
        session.set_working_prompt(prompt)

        self.storage.save(session)
        return session

    def load_session(self, session_id: str) -> Optional[PromptSession]:
        """Load an existing session."""
        return self.storage.load(session_id)

    def save_session(self, session: PromptSession) -> None:
        """Save session to storage."""
        self.storage.save(session)

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        return self.storage.delete(session_id)

    def list_sessions(self, limit: int = 20) -> list[dict]:
        """List recent sessions."""
        return self.storage.list_sessions(limit)

    def generate(
        self,
        session: PromptSession,
        render: bool = True,
        quality: str = "l",
    ) -> GenerationResult:
        """Generate code from current prompt and optionally render video.

        Args:
            session: The prompt session
            render: Whether to render the video
            quality: Video quality (l=480p, m=720p, h=1080p)

        Returns:
            GenerationResult with code and optional video path
        """
        prompt = session.current_prompt
        if not prompt:
            raise ValueError("No prompt set for session")

        # Generate code
        start_time = time.time()
        code_gen = self._get_code_generator()

        try:
            gen_result = code_gen.generate(
                topic=prompt.topic,
                requirements="\n".join(f"- {r}" for r in prompt.requirements) if prompt.requirements else "",
                audience_level=prompt.audience,
            )
            code = gen_result.code
            scene_name = gen_result.scene_name
            generation_time_ms = int((time.time() - start_time) * 1000)

        except Exception as e:
            # Return failed result
            result = GenerationResult(
                version=session.next_version,
                prompt=prompt.copy(),
                code="",
                scene_name="",
                generation_time_ms=int((time.time() - start_time) * 1000),
                success=False,
                error=str(e),
            )
            session.add_result(result)
            self.storage.save(session)
            return result

        # Save code to file
        session_dir = self.output_dir / session.session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        version = session.next_version
        code_path = session_dir / f"v{version}_{scene_name}.py"
        code_path.write_text(code)

        # Create result
        result = GenerationResult(
            version=version,
            prompt=prompt.copy(),
            code=code,
            scene_name=scene_name,
            code_path=str(code_path),
            generation_time_ms=generation_time_ms,
        )

        # Render if requested
        if render:
            render_result = self._render_code(
                code=code,
                scene_name=scene_name,
                output_dir=session_dir,
                version=version,
                quality=quality,
            )
            result.video_path = render_result.get("video_path")
            result.render_time_ms = render_result.get("render_time_ms")
            if render_result.get("error"):
                result.success = False
                result.error = render_result["error"]

        session.add_result(result)
        self.storage.save(session)
        return result

    def _render_code(
        self,
        code: str,
        scene_name: str,
        output_dir: Path,
        version: int,
        quality: str = "l",
    ) -> dict:
        """Render code to video."""
        start_time = time.time()

        try:
            renderer = self._get_renderer()

            # Map quality string to VideoQuality enum
            from ...config import VideoQuality
            quality_map = {
                "l": VideoQuality.LOW,
                "m": VideoQuality.MEDIUM,
                "h": VideoQuality.HIGH,
                "p": VideoQuality.PRODUCTION,
                "k": VideoQuality.FOURK,
            }
            video_quality = quality_map.get(quality, VideoQuality.LOW)

            render_result = renderer.render(
                code=code,
                scene_name=scene_name,
                output_dir=output_dir,
                quality=video_quality,
            )

            render_time_ms = int((time.time() - start_time) * 1000)

            if render_result.success:
                # Rename to versioned filename
                if render_result.output_path:
                    new_path = output_dir / f"v{version}.mp4"
                    render_result.output_path.rename(new_path)
                    return {
                        "video_path": str(new_path),
                        "render_time_ms": render_time_ms,
                    }

            return {
                "error": render_result.error_message or "Unknown render error",
                "render_time_ms": render_time_ms,
            }

        except Exception as e:
            return {
                "error": str(e),
                "render_time_ms": int((time.time() - start_time) * 1000),
            }

    def render_version(
        self,
        session: PromptSession,
        version: int,
        quality: str = "l",
    ) -> Optional[str]:
        """Render a specific version that wasn't rendered before.

        Returns video path or None if failed.
        """
        result = session.get_version(version)
        if not result:
            return None

        if result.video_path and Path(result.video_path).exists():
            return result.video_path

        session_dir = self.output_dir / session.session_id
        render_result = self._render_code(
            code=result.code,
            scene_name=result.scene_name,
            output_dir=session_dir,
            version=version,
            quality=quality,
        )

        if render_result.get("video_path"):
            result.video_path = render_result["video_path"]
            result.render_time_ms = render_result.get("render_time_ms")
            self.storage.save(session)
            return result.video_path

        return None

    def export_code(
        self,
        session: PromptSession,
        version: Optional[int] = None,
        output_path: Optional[Path] = None,
    ) -> Path:
        """Export code to a standalone Python file.

        Args:
            session: The session to export from
            version: Version number (default: latest)
            output_path: Output file path (default: <topic>.py in current dir)

        Returns:
            Path to exported file
        """
        if version is None:
            result = session.current
        else:
            result = session.get_version(version)

        if not result:
            raise ValueError(f"Version {version} not found")

        if output_path is None:
            # Generate filename from topic
            safe_name = "".join(c if c.isalnum() else "_" for c in result.prompt.topic)
            safe_name = safe_name.lower()[:30]
            output_path = Path.cwd() / f"{safe_name}.py"

        output_path.write_text(result.code)
        return output_path
