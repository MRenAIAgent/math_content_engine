"""
Test utilities for verifying voice-video synchronization and content consistency.

This module provides tools to validate that:
1. Voice narration timing matches video content
2. Narration content describes what's shown visually
3. Audio and video are properly synchronized
"""

import os
from pathlib import Path
from typing import List, Tuple, Optional
import subprocess
import json


class VideoAudioSyncValidator:
    """Validates synchronization between video content and audio narration."""

    def __init__(self, video_path: Path):
        """
        Initialize validator with video file.

        Args:
            video_path: Path to the video file to validate
        """
        self.video_path = video_path
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

    def get_video_duration(self) -> float:
        """
        Get total duration of the video in seconds.

        Returns:
            Duration in seconds

        Requires:
            ffprobe (part of FFmpeg)
        """
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json",
            str(self.video_path)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            return float(data["format"]["duration"])
        except (subprocess.CalledProcessError, KeyError, ValueError) as e:
            raise RuntimeError(f"Failed to get video duration: {e}")

    def extract_audio_track(self, output_path: Optional[Path] = None) -> Path:
        """
        Extract audio track from video for analysis.

        Args:
            output_path: Where to save extracted audio (default: temp file)

        Returns:
            Path to extracted audio file
        """
        if output_path is None:
            output_path = self.video_path.parent / f"{self.video_path.stem}_audio.mp3"

        cmd = [
            "ffmpeg",
            "-i", str(self.video_path),
            "-vn",  # No video
            "-acodec", "mp3",
            "-y",  # Overwrite
            str(output_path)
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True)
            return output_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to extract audio: {e.stderr.decode()}")

    def check_audio_presence(self) -> bool:
        """
        Check if video has an audio track.

        Returns:
            True if audio track exists, False otherwise
        """
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=codec_type",
            "-of", "json",
            str(self.video_path)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            return len(data.get("streams", [])) > 0
        except (subprocess.CalledProcessError, KeyError, json.JSONDecodeError):
            return False

    def get_audio_duration(self) -> float:
        """
        Get duration of audio track.

        Returns:
            Audio duration in seconds
        """
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=duration",
            "-of", "json",
            str(self.video_path)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            return float(data["streams"][0]["duration"])
        except (subprocess.CalledProcessError, KeyError, ValueError) as e:
            raise RuntimeError(f"Failed to get audio duration: {e}")

    def check_sync_alignment(self, tolerance_seconds: float = 0.5) -> Tuple[bool, str]:
        """
        Check if audio and video durations are aligned.

        Args:
            tolerance_seconds: Acceptable difference in seconds

        Returns:
            (is_aligned, message) tuple
        """
        video_duration = self.get_video_duration()
        audio_duration = self.get_audio_duration()

        diff = abs(video_duration - audio_duration)

        if diff <= tolerance_seconds:
            return True, f"✅ Sync OK: video={video_duration:.2f}s, audio={audio_duration:.2f}s, diff={diff:.2f}s"
        else:
            return False, f"❌ Sync issue: video={video_duration:.2f}s, audio={audio_duration:.2f}s, diff={diff:.2f}s > {tolerance_seconds}s"

    def validate_narration_timing(
        self,
        narration_cues: List[Tuple[float, str]],
        buffer_seconds: float = 1.0
    ) -> List[str]:
        """
        Validate that narration cues fall within video duration.

        Args:
            narration_cues: List of (time, text) tuples
            buffer_seconds: Buffer time before end of video

        Returns:
            List of validation issues (empty if all valid)
        """
        video_duration = self.get_video_duration()
        issues = []

        for time, text in narration_cues:
            if time < 0:
                issues.append(f"❌ Cue at {time}s is negative: '{text[:50]}'")
            elif time > video_duration - buffer_seconds:
                issues.append(
                    f"⚠️  Cue at {time}s is near/past end ({video_duration:.2f}s): '{text[:50]}'"
                )

        if not issues:
            issues.append(f"✅ All {len(narration_cues)} cues within video duration ({video_duration:.2f}s)")

        return issues

    def generate_subtitle_file(
        self,
        narration_cues: List[Tuple[float, str]],
        output_path: Optional[Path] = None,
        cue_duration: float = 3.0
    ) -> Path:
        """
        Generate SRT subtitle file for manual review.

        Args:
            narration_cues: List of (time, text) tuples
            output_path: Where to save SRT file
            cue_duration: Default duration for each cue

        Returns:
            Path to generated SRT file
        """
        if output_path is None:
            output_path = self.video_path.parent / f"{self.video_path.stem}_subs.srt"

        def format_srt_time(seconds: float) -> str:
            """Convert seconds to SRT time format (HH:MM:SS,mmm)."""
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

        srt_content = []
        for i, (time, text) in enumerate(narration_cues, 1):
            start_time = format_srt_time(time)
            end_time = format_srt_time(time + cue_duration)

            srt_content.append(f"{i}")
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(text)
            srt_content.append("")  # Blank line between cues

        output_path.write_text("\n".join(srt_content))
        return output_path

    def create_review_video_with_subtitles(
        self,
        subtitle_file: Path,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Create a video with burned-in subtitles for easy review.

        Args:
            subtitle_file: Path to SRT subtitle file
            output_path: Where to save output video

        Returns:
            Path to video with subtitles
        """
        if output_path is None:
            output_path = self.video_path.parent / f"{self.video_path.stem}_with_subs.mp4"

        # Escape Windows paths and special characters for ffmpeg
        subtitle_path_escaped = str(subtitle_file).replace("\\", "/").replace(":", "\\:")

        cmd = [
            "ffmpeg",
            "-i", str(self.video_path),
            "-vf", f"subtitles={subtitle_path_escaped}",
            "-c:a", "copy",
            "-y",
            str(output_path)
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True)
            return output_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to create subtitle video: {e.stderr.decode()}")


def validate_narration_content_consistency(
    narration_cues: List[Tuple[float, str]],
    expected_topics: List[str]
) -> Tuple[bool, List[str]]:
    """
    Validate that narration covers expected topics.

    Args:
        narration_cues: List of (time, text) tuples
        expected_topics: Keywords/phrases that should appear in narration

    Returns:
        (all_covered, issues) tuple
    """
    all_text = " ".join(text.lower() for _, text in narration_cues)
    issues = []

    for topic in expected_topics:
        if topic.lower() not in all_text:
            issues.append(f"❌ Missing topic in narration: '{topic}'")

    if not issues:
        return True, [f"✅ All {len(expected_topics)} topics covered in narration"]
    else:
        return False, issues


def check_narration_pacing(
    narration_cues: List[Tuple[float, str]],
    min_gap: float = 2.0,
    max_gap: float = 10.0
) -> List[str]:
    """
    Check if narration pacing is appropriate (not too fast or slow).

    Args:
        narration_cues: List of (time, text) tuples
        min_gap: Minimum seconds between cues
        max_gap: Maximum seconds between cues

    Returns:
        List of pacing issues
    """
    issues = []

    for i in range(len(narration_cues) - 1):
        current_time, current_text = narration_cues[i]
        next_time, next_text = narration_cues[i + 1]

        gap = next_time - current_time

        if gap < min_gap:
            issues.append(
                f"⚠️  Too fast: {gap:.1f}s gap between cues at {current_time}s and {next_time}s"
            )
        elif gap > max_gap:
            issues.append(
                f"⚠️  Too slow: {gap:.1f}s gap between cues at {current_time}s and {next_time}s"
            )

    if not issues:
        issues.append(f"✅ Narration pacing is good (gaps between {min_gap}s and {max_gap}s)")

    return issues


# Example usage and test
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python test_voice_video_sync.py <video_file>")
        sys.exit(1)

    video_path = Path(sys.argv[1])
    validator = VideoAudioSyncValidator(video_path)

    print("="*80)
    print("VIDEO-AUDIO SYNCHRONIZATION VALIDATION")
    print("="*80)
    print(f"\nVideo: {video_path.name}")

    # Check basic properties
    print(f"\n1. Audio track present: {validator.check_audio_presence()}")
    print(f"2. Video duration: {validator.get_video_duration():.2f}s")
    if validator.check_audio_presence():
        print(f"3. Audio duration: {validator.get_audio_duration():.2f}s")

    # Check alignment
    is_aligned, message = validator.check_sync_alignment()
    print(f"\n4. Sync check: {message}")

    # Example narration cues (would come from test)
    example_cues = [
        (0.0, "Let's solve the linear equation: 2x plus 3 equals 7"),
        (3.0, "First, we need to isolate the variable x"),
        (6.0, "Subtract 3 from both sides of the equation"),
        (9.0, "This gives us 2x equals 4"),
        (12.0, "Now, divide both sides by 2"),
        (15.0, "Therefore, x equals 2. That's our solution!")
    ]

    print("\n5. Narration timing validation:")
    timing_issues = validator.validate_narration_timing(example_cues)
    for issue in timing_issues:
        print(f"   {issue}")

    print("\n6. Narration pacing check:")
    pacing_issues = check_narration_pacing(example_cues)
    for issue in pacing_issues:
        print(f"   {issue}")

    # Generate subtitles for review
    print("\n7. Generating subtitle file for manual review...")
    srt_path = validator.generate_subtitle_file(example_cues)
    print(f"   ✅ Subtitles saved to: {srt_path}")

    print("\n" + "="*80)
    print("VALIDATION COMPLETE")
    print("="*80)
