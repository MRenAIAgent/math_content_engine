"""Core data models for prompt engineering lab."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum
import json
import copy


class AnimationStyle(Enum):
    DARK = "dark"
    LIGHT = "light"


class AudienceLevel(Enum):
    ELEMENTARY = "elementary"
    MIDDLE_SCHOOL = "middle school"
    HIGH_SCHOOL = "high school"
    COLLEGE = "college"


class Pacing(Enum):
    SLOW = "slow"
    MEDIUM = "medium"
    FAST = "fast"


@dataclass
class AnimationPrompt:
    """Editable prompt components for animation generation."""

    topic: str
    requirements: list[str] = field(default_factory=list)
    style: str = "dark"
    audience: str = "high school"

    # Advanced options
    pacing: Optional[str] = None
    duration_hint: Optional[str] = None
    color_scheme: Optional[list[str]] = None

    def add_requirement(self, requirement: str) -> None:
        """Add a requirement to the list."""
        self.requirements.append(requirement)

    def remove_requirement(self, index: int) -> Optional[str]:
        """Remove requirement by index (0-based). Returns removed item or None."""
        if 0 <= index < len(self.requirements):
            return self.requirements.pop(index)
        return None

    def clear_requirements(self) -> None:
        """Clear all requirements."""
        self.requirements.clear()

    def to_prompt_text(self) -> str:
        """Convert to the text format sent to LLM."""
        lines = [f"TOPIC: {self.topic}"]

        if self.requirements:
            lines.append("\nREQUIREMENTS:")
            for req in self.requirements:
                lines.append(f"- {req}")

        if self.pacing:
            lines.append(f"\nPACING: {self.pacing}")

        if self.duration_hint:
            lines.append(f"DURATION: {self.duration_hint}")

        if self.color_scheme:
            lines.append(f"COLORS: {', '.join(self.color_scheme)}")

        lines.append(f"\nAUDIENCE LEVEL: {self.audience}")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "topic": self.topic,
            "requirements": self.requirements,
            "style": self.style,
            "audience": self.audience,
            "pacing": self.pacing,
            "duration_hint": self.duration_hint,
            "color_scheme": self.color_scheme,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AnimationPrompt":
        """Create from dictionary."""
        return cls(
            topic=data["topic"],
            requirements=data.get("requirements", []),
            style=data.get("style", "dark"),
            audience=data.get("audience", "high school"),
            pacing=data.get("pacing"),
            duration_hint=data.get("duration_hint"),
            color_scheme=data.get("color_scheme"),
        )

    def copy(self) -> "AnimationPrompt":
        """Create a deep copy of this prompt."""
        return AnimationPrompt(
            topic=self.topic,
            requirements=list(self.requirements),
            style=self.style,
            audience=self.audience,
            pacing=self.pacing,
            duration_hint=self.duration_hint,
            color_scheme=list(self.color_scheme) if self.color_scheme else None,
        )

    def __str__(self) -> str:
        """Human-readable representation."""
        lines = [f"Topic: {self.topic}"]
        if self.requirements:
            lines.append("Requirements:")
            for i, req in enumerate(self.requirements, 1):
                lines.append(f"  {i}. {req}")
        else:
            lines.append("Requirements: (none)")
        lines.append(f"Style: {self.style} | Audience: {self.audience}")
        if self.pacing:
            lines.append(f"Pacing: {self.pacing}")
        return "\n".join(lines)


@dataclass
class GenerationResult:
    """Result of a single generation attempt."""

    version: int
    prompt: AnimationPrompt
    code: str
    scene_name: str

    # Paths
    video_path: Optional[str] = None
    code_path: Optional[str] = None

    # Timing
    generation_time_ms: int = 0
    render_time_ms: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    # Status
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "version": self.version,
            "prompt": self.prompt.to_dict(),
            "code": self.code,
            "scene_name": self.scene_name,
            "video_path": self.video_path,
            "code_path": self.code_path,
            "generation_time_ms": self.generation_time_ms,
            "render_time_ms": self.render_time_ms,
            "created_at": self.created_at.isoformat(),
            "success": self.success,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GenerationResult":
        """Create from dictionary."""
        return cls(
            version=data["version"],
            prompt=AnimationPrompt.from_dict(data["prompt"]),
            code=data["code"],
            scene_name=data["scene_name"],
            video_path=data.get("video_path"),
            code_path=data.get("code_path"),
            generation_time_ms=data.get("generation_time_ms", 0),
            render_time_ms=data.get("render_time_ms"),
            created_at=datetime.fromisoformat(data["created_at"]),
            success=data.get("success", True),
            error=data.get("error"),
        )


@dataclass
class PromptSession:
    """A prompt engineering session with version history."""

    session_id: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Current working prompt (may not be generated yet)
    working_prompt: Optional[AnimationPrompt] = None

    # History of generations
    history: list[GenerationResult] = field(default_factory=list)

    @property
    def current(self) -> Optional[GenerationResult]:
        """Get the most recent generation result."""
        return self.history[-1] if self.history else None

    @property
    def current_prompt(self) -> Optional[AnimationPrompt]:
        """Get the current working prompt or last generated prompt."""
        if self.working_prompt:
            return self.working_prompt
        return self.current.prompt if self.current else None

    @property
    def next_version(self) -> int:
        """Get the next version number."""
        return len(self.history) + 1

    def get_version(self, version: int) -> Optional[GenerationResult]:
        """Get a specific version by number (1-based)."""
        if 1 <= version <= len(self.history):
            return self.history[version - 1]
        return None

    def add_result(self, result: GenerationResult) -> None:
        """Add a generation result to history."""
        self.history.append(result)
        self.working_prompt = result.prompt.copy()
        self.updated_at = datetime.now()

    def set_working_prompt(self, prompt: AnimationPrompt) -> None:
        """Set the current working prompt."""
        self.working_prompt = prompt
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "working_prompt": self.working_prompt.to_dict() if self.working_prompt else None,
            "history": [r.to_dict() for r in self.history],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PromptSession":
        """Create from dictionary."""
        session = cls(
            session_id=data["session_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
        if data.get("working_prompt"):
            session.working_prompt = AnimationPrompt.from_dict(data["working_prompt"])
        session.history = [GenerationResult.from_dict(r) for r in data.get("history", [])]
        return session
