"""
Manim rendering engine with error handling.
"""

import logging
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..config import VideoQuality

logger = logging.getLogger(__name__)


@dataclass
class RenderResult:
    """Result of a rendering operation."""
    success: bool
    output_path: Optional[Path]
    error_message: Optional[str] = None
    stdout: str = ""
    stderr: str = ""
    render_time: float = 0.0


class ManimRenderer:
    """
    Renders Manim code to video files.
    """

    QUALITY_FLAGS = {
        VideoQuality.LOW: "-ql",
        VideoQuality.MEDIUM: "-qm",
        VideoQuality.HIGH: "-qh",
        VideoQuality.PRODUCTION: "-qp",
        VideoQuality.FOURK: "-qk",
    }

    def __init__(
        self,
        output_dir: Path,
        cache_dir: Path,
        quality: VideoQuality = VideoQuality.MEDIUM,
        output_format: str = "mp4",
    ):
        """
        Initialize the renderer.

        Args:
            output_dir: Directory for output videos
            cache_dir: Directory for Manim cache
            quality: Video quality preset
            output_format: Output format (mp4 or gif)
        """
        self.output_dir = Path(output_dir)
        self.cache_dir = Path(cache_dir)
        self.quality = quality
        self.output_format = output_format

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def render(
        self,
        code: str,
        scene_name: str,
        output_filename: Optional[str] = None,
    ) -> RenderResult:
        """
        Render Manim code to a video file.

        Args:
            code: Python code containing the Manim scene
            scene_name: Name of the Scene class to render
            output_filename: Optional custom output filename

        Returns:
            RenderResult with success status and output path
        """
        import time
        start_time = time.time()

        # Create temporary file for the code
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False,
            dir=self.cache_dir,
        ) as f:
            f.write(code)
            temp_file = Path(f.name)

        try:
            result = self._run_manim(temp_file, scene_name)
            render_time = time.time() - start_time
            result.render_time = render_time

            # Move output to final location
            if result.success and result.output_path:
                final_path = self._move_to_output(result.output_path, output_filename)
                result.output_path = final_path

            return result

        finally:
            # Cleanup temp file
            if temp_file.exists():
                temp_file.unlink()

    def _run_manim(self, script_path: Path, scene_name: str) -> RenderResult:
        """Run manim command on the script."""
        quality_flag = self.QUALITY_FLAGS.get(self.quality, "-qm")

        # Build command
        cmd = [
            "manim",
            quality_flag,
            str(script_path),
            scene_name,
            "--media_dir", str(self.cache_dir),
        ]

        # Add format flag for GIF
        if self.output_format == "gif":
            cmd.append("--format=gif")

        logger.info(f"Running: {' '.join(cmd)}")

        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if process.returncode == 0:
                output_path = self._find_output_file(scene_name)
                return RenderResult(
                    success=True,
                    output_path=output_path,
                    stdout=process.stdout,
                    stderr=process.stderr,
                )
            else:
                error_msg = self._extract_error(process.stderr)
                return RenderResult(
                    success=False,
                    output_path=None,
                    error_message=error_msg,
                    stdout=process.stdout,
                    stderr=process.stderr,
                )

        except subprocess.TimeoutExpired:
            return RenderResult(
                success=False,
                output_path=None,
                error_message="Rendering timed out after 5 minutes",
            )
        except FileNotFoundError:
            return RenderResult(
                success=False,
                output_path=None,
                error_message="Manim is not installed. Run: pip install manim",
            )
        except Exception as e:
            return RenderResult(
                success=False,
                output_path=None,
                error_message=f"Unexpected error: {str(e)}",
            )

    def _find_output_file(self, scene_name: str) -> Optional[Path]:
        """Find the output file in the media directory."""
        media_dir = self.cache_dir / "videos"

        if not media_dir.exists():
            return None

        # Search for the output file
        extension = "gif" if self.output_format == "gif" else "mp4"
        pattern = f"**/{scene_name}.{extension}"

        matches = list(media_dir.glob(pattern))
        if matches:
            # Return the most recent
            return max(matches, key=lambda p: p.stat().st_mtime)

        return None

    def _move_to_output(
        self,
        source_path: Path,
        output_filename: Optional[str]
    ) -> Path:
        """Move rendered file to output directory."""
        if output_filename:
            # Add extension if not present
            if not output_filename.endswith(f".{self.output_format}"):
                output_filename = f"{output_filename}.{self.output_format}"
            dest_path = self.output_dir / output_filename
        else:
            dest_path = self.output_dir / source_path.name

        # Handle existing files
        if dest_path.exists():
            counter = 1
            stem = dest_path.stem
            while dest_path.exists():
                dest_path = self.output_dir / f"{stem}_{counter}.{self.output_format}"
                counter += 1

        shutil.move(str(source_path), str(dest_path))
        return dest_path

    def _extract_error(self, stderr: str) -> str:
        """Extract relevant error message from stderr."""
        lines = stderr.strip().split('\n')

        # Look for Python traceback
        error_lines = []
        in_traceback = False

        for line in lines:
            if 'Traceback' in line:
                in_traceback = True
            if in_traceback:
                error_lines.append(line)
            elif 'Error' in line or 'Exception' in line:
                error_lines.append(line)

        if error_lines:
            return '\n'.join(error_lines[-10:])  # Last 10 lines of error

        return stderr[-500:] if len(stderr) > 500 else stderr

    def cleanup_cache(self):
        """Remove all cached files."""
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
