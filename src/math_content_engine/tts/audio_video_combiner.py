"""
Audio-Video combiner for adding narration to Manim animations.

Uses ffmpeg to combine generated TTS audio with rendered video.
"""

import logging
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class AudioSegment:
    """An audio segment with timing information."""

    audio_path: Path
    start_time: float      # When to start in the video (seconds)
    volume: float = 1.0    # Volume multiplier (0.0 to 2.0)


@dataclass
class CombineResult:
    """Result of audio-video combination."""

    success: bool
    output_path: Optional[Path]
    error_message: Optional[str] = None


class AudioVideoCombiner:
    """
    Combines audio narration with video files using ffmpeg.

    Supports:
    - Single audio track overlay
    - Multiple timed audio segments
    - Volume adjustment
    - Extending video to match audio duration

    Example:
        >>> combiner = AudioVideoCombiner()
        >>> result = combiner.combine_simple(
        ...     video_path=Path("animation.mp4"),
        ...     audio_path=Path("narration.mp3"),
        ...     output_path=Path("final.mp4")
        ... )
        >>> print(f"Output: {result.output_path}")
    """

    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        """
        Initialize the combiner.

        Args:
            ffmpeg_path: Path to ffmpeg executable
        """
        self.ffmpeg_path = ffmpeg_path
        self._verify_ffmpeg()

    def _verify_ffmpeg(self):
        """Verify ffmpeg is available."""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                timeout=10
            )
            if result.returncode != 0:
                raise RuntimeError("ffmpeg not found or not working")
        except FileNotFoundError:
            raise RuntimeError(
                "ffmpeg not found. Install with: brew install ffmpeg (macOS) "
                "or apt install ffmpeg (Linux)"
            )

    def combine_simple(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path,
        extend_video: bool = True
    ) -> CombineResult:
        """
        Combine a single audio track with video.

        Args:
            video_path: Path to input video
            audio_path: Path to audio file
            output_path: Path for output video
            extend_video: If True, extend video with last frame if audio is longer

        Returns:
            CombineResult with output path or error
        """
        video_path = Path(video_path)
        audio_path = Path(audio_path)
        output_path = Path(output_path)

        if not video_path.exists():
            return CombineResult(False, None, f"Video not found: {video_path}")
        if not audio_path.exists():
            return CombineResult(False, None, f"Audio not found: {audio_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Get durations
        video_duration = self._get_duration(video_path)
        audio_duration = self._get_duration(audio_path)

        logger.info(f"Video duration: {video_duration:.2f}s, Audio duration: {audio_duration:.2f}s")

        try:
            if extend_video and audio_duration > video_duration:
                # Need to extend video to match audio
                return self._combine_with_extension(
                    video_path, audio_path, output_path,
                    video_duration, audio_duration
                )
            else:
                # Simple overlay
                return self._combine_direct(video_path, audio_path, output_path)

        except subprocess.CalledProcessError as e:
            return CombineResult(False, None, f"ffmpeg error: {e.stderr}")
        except Exception as e:
            return CombineResult(False, None, str(e))

    def _combine_direct(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path
    ) -> CombineResult:
        """Direct combination without video extension."""
        cmd = [
            self.ffmpeg_path,
            "-y",  # Overwrite output
            "-i", str(video_path),
            "-i", str(audio_path),
            "-c:v", "copy",  # Copy video stream
            "-c:a", "aac",   # Encode audio to AAC
            "-b:a", "192k",  # Audio bitrate
            "-map", "0:v:0",  # Use video from first input
            "-map", "1:a:0",  # Use audio from second input
            "-shortest",      # End when shortest stream ends
            str(output_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            return CombineResult(False, None, result.stderr)

        logger.info(f"Combined video saved to: {output_path}")
        return CombineResult(True, output_path)

    def _combine_with_extension(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path,
        video_duration: float,
        audio_duration: float
    ) -> CombineResult:
        """Combine and extend video to match audio duration."""
        # Use tpad filter to extend video with last frame
        extra_time = audio_duration - video_duration + 0.5  # Add small buffer

        cmd = [
            self.ffmpeg_path,
            "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-filter_complex",
            f"[0:v]tpad=stop_mode=clone:stop_duration={extra_time}[v]",
            "-map", "[v]",
            "-map", "1:a:0",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "192k",
            str(output_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            return CombineResult(False, None, result.stderr)

        logger.info(f"Combined video (extended) saved to: {output_path}")
        return CombineResult(True, output_path)

    def combine_segments(
        self,
        video_path: Path,
        segments: List[AudioSegment],
        output_path: Path,
        background_music: Optional[Path] = None,
        music_volume: float = 0.1
    ) -> CombineResult:
        """
        Combine multiple timed audio segments with video.

        Args:
            video_path: Path to input video
            segments: List of AudioSegment with timing
            output_path: Path for output video
            background_music: Optional background music track
            music_volume: Volume for background music (0.0 to 1.0)

        Returns:
            CombineResult with output path or error
        """
        video_path = Path(video_path)
        output_path = Path(output_path)

        if not video_path.exists():
            return CombineResult(False, None, f"Video not found: {video_path}")

        for seg in segments:
            if not seg.audio_path.exists():
                return CombineResult(False, None, f"Audio not found: {seg.audio_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Build complex filter for multiple audio inputs
            inputs = ["-i", str(video_path)]
            filter_parts = []
            audio_labels = []

            for i, seg in enumerate(segments):
                inputs.extend(["-i", str(seg.audio_path)])
                # Delay each audio segment and adjust volume
                delay_ms = int(seg.start_time * 1000)
                filter_parts.append(
                    f"[{i+1}:a]adelay={delay_ms}|{delay_ms},volume={seg.volume}[a{i}]"
                )
                audio_labels.append(f"[a{i}]")

            # Add background music if provided
            if background_music and background_music.exists():
                music_idx = len(segments) + 1
                inputs.extend(["-i", str(background_music)])
                filter_parts.append(
                    f"[{music_idx}:a]volume={music_volume}[music]"
                )
                audio_labels.append("[music]")

            # Mix all audio streams
            filter_complex = ";".join(filter_parts)
            if len(audio_labels) > 1:
                filter_complex += f";{''.join(audio_labels)}amix=inputs={len(audio_labels)}:duration=longest[aout]"
            else:
                filter_complex += f";{audio_labels[0]}acopy[aout]"

            cmd = [
                self.ffmpeg_path,
                "-y",
                *inputs,
                "-filter_complex", filter_complex,
                "-map", "0:v:0",
                "-map", "[aout]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                str(output_path)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                return CombineResult(False, None, result.stderr)

            logger.info(f"Combined video with {len(segments)} segments: {output_path}")
            return CombineResult(True, output_path)

        except Exception as e:
            return CombineResult(False, None, str(e))

    def _get_duration(self, file_path: Path) -> float:
        """Get duration of audio/video file using ffprobe."""
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(file_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            logger.warning(f"Could not get duration for {file_path}")
            return 0.0

        try:
            return float(result.stdout.strip())
        except ValueError:
            return 0.0

    def add_background_music(
        self,
        video_path: Path,
        music_path: Path,
        output_path: Path,
        music_volume: float = 0.15,
        fade_out: float = 2.0
    ) -> CombineResult:
        """
        Add background music to a video (with existing audio).

        Args:
            video_path: Input video with narration
            music_path: Background music file
            output_path: Output video path
            music_volume: Music volume (0.0 to 1.0)
            fade_out: Fade out duration at the end (seconds)

        Returns:
            CombineResult
        """
        video_path = Path(video_path)
        music_path = Path(music_path)
        output_path = Path(output_path)

        video_duration = self._get_duration(video_path)

        # Fade out music at the end
        fade_start = max(0, video_duration - fade_out)

        cmd = [
            self.ffmpeg_path,
            "-y",
            "-i", str(video_path),
            "-i", str(music_path),
            "-filter_complex",
            f"[1:a]volume={music_volume},afade=t=out:st={fade_start}:d={fade_out}[music];"
            f"[0:a][music]amix=inputs=2:duration=first[aout]",
            "-map", "0:v:0",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            str(output_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            return CombineResult(False, None, result.stderr)

        return CombineResult(True, output_path)
