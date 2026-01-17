"""Diff utilities for comparing prompts and code."""

import difflib
from typing import Optional

from ..prompt.models import AnimationPrompt, GenerationResult


def diff_prompts(prompt1: AnimationPrompt, prompt2: AnimationPrompt) -> dict:
    """Compare two prompts and return the differences.

    Returns:
        Dict with keys:
        - topic_changed: bool
        - requirements_added: list[str]
        - requirements_removed: list[str]
        - style_changed: bool
        - audience_changed: bool
        - pacing_changed: bool
    """
    diff = {
        "topic_changed": prompt1.topic != prompt2.topic,
        "old_topic": prompt1.topic if prompt1.topic != prompt2.topic else None,
        "new_topic": prompt2.topic if prompt1.topic != prompt2.topic else None,
        "requirements_added": [r for r in prompt2.requirements if r not in prompt1.requirements],
        "requirements_removed": [r for r in prompt1.requirements if r not in prompt2.requirements],
        "style_changed": prompt1.style != prompt2.style,
        "old_style": prompt1.style if prompt1.style != prompt2.style else None,
        "new_style": prompt2.style if prompt1.style != prompt2.style else None,
        "audience_changed": prompt1.audience != prompt2.audience,
        "old_audience": prompt1.audience if prompt1.audience != prompt2.audience else None,
        "new_audience": prompt2.audience if prompt1.audience != prompt2.audience else None,
        "pacing_changed": prompt1.pacing != prompt2.pacing,
        "old_pacing": prompt1.pacing if prompt1.pacing != prompt2.pacing else None,
        "new_pacing": prompt2.pacing if prompt1.pacing != prompt2.pacing else None,
    }
    return diff


def diff_code(code1: str, code2: str, context_lines: int = 3) -> str:
    """Generate a unified diff between two code strings.

    Args:
        code1: First code version
        code2: Second code version
        context_lines: Number of context lines to show

    Returns:
        Unified diff string
    """
    lines1 = code1.splitlines(keepends=True)
    lines2 = code2.splitlines(keepends=True)

    diff = difflib.unified_diff(
        lines1,
        lines2,
        fromfile="v1",
        tofile="v2",
        n=context_lines,
    )

    return "".join(diff)


def format_prompt_diff(diff: dict) -> str:
    """Format a prompt diff for display.

    Args:
        diff: Dict from diff_prompts()

    Returns:
        Formatted string for terminal display
    """
    lines = []

    if diff["topic_changed"]:
        lines.append(f"  Topic: {diff['old_topic']} → {diff['new_topic']}")

    if diff["requirements_added"]:
        for req in diff["requirements_added"]:
            lines.append(f"  + {req}")

    if diff["requirements_removed"]:
        for req in diff["requirements_removed"]:
            lines.append(f"  - {req}")

    if diff["style_changed"]:
        lines.append(f"  Style: {diff['old_style']} → {diff['new_style']}")

    if diff["audience_changed"]:
        lines.append(f"  Audience: {diff['old_audience']} → {diff['new_audience']}")

    if diff["pacing_changed"]:
        old_pacing = diff["old_pacing"] or "(none)"
        new_pacing = diff["new_pacing"] or "(none)"
        lines.append(f"  Pacing: {old_pacing} → {new_pacing}")

    if not lines:
        return "  (no changes)"

    return "\n".join(lines)


def format_code_diff(diff: str, max_lines: int = 30) -> str:
    """Format a code diff for display with optional truncation.

    Args:
        diff: Unified diff string from diff_code()
        max_lines: Maximum lines to show

    Returns:
        Formatted diff string
    """
    if not diff.strip():
        return "(no code changes)"

    lines = diff.split("\n")

    if len(lines) > max_lines:
        shown = lines[:max_lines]
        remaining = len(lines) - max_lines
        shown.append(f"... ({remaining} more lines)")
        return "\n".join(shown)

    return diff


def compare_results(result1: GenerationResult, result2: GenerationResult) -> dict:
    """Compare two generation results.

    Returns:
        Dict with prompt diff, code diff, and metadata comparison
    """
    prompt_diff = diff_prompts(result1.prompt, result2.prompt)
    code_diff = diff_code(result1.code, result2.code)

    # Count line changes
    code_lines1 = len(result1.code.splitlines())
    code_lines2 = len(result2.code.splitlines())

    return {
        "prompt_diff": prompt_diff,
        "code_diff": code_diff,
        "v1_lines": code_lines1,
        "v2_lines": code_lines2,
        "lines_diff": code_lines2 - code_lines1,
        "v1_video": result1.video_path,
        "v2_video": result2.video_path,
        "v1_render_time": result1.render_time_ms,
        "v2_render_time": result2.render_time_ms,
    }
