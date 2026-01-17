"""Suggestion engine for prompt modifications."""

from dataclasses import dataclass
from typing import Optional

from ..prompt.models import AnimationPrompt
from .patterns import CHANGE_PATTERNS, find_matching_patterns


@dataclass
class PromptSuggestion:
    """A suggestion for how to modify the prompt."""

    description: str
    requirements_to_add: list[str]
    pacing: Optional[str] = None
    confidence: str = "medium"  # high, medium, low

    def apply_to(self, prompt: AnimationPrompt) -> AnimationPrompt:
        """Apply this suggestion to a prompt, returning a new prompt."""
        new_prompt = prompt.copy()
        for req in self.requirements_to_add:
            if req not in new_prompt.requirements:
                new_prompt.add_requirement(req)
        if self.pacing:
            new_prompt.pacing = self.pacing
        return new_prompt


class SuggestionEngine:
    """Generates suggestions for prompt modifications based on user requests."""

    def __init__(self):
        """Initialize the suggestion engine."""
        self._llm_client = None

    def _get_llm_client(self):
        """Lazy load LLM client for advanced suggestions."""
        if self._llm_client is None:
            from ...llm.factory import create_llm_client
            from ...config import Config

            config = Config.from_env()
            self._llm_client = create_llm_client(config)
        return self._llm_client

    def suggest_from_request(
        self,
        user_request: str,
        current_prompt: Optional[AnimationPrompt] = None,
    ) -> list[PromptSuggestion]:
        """Generate suggestions based on user's request.

        Args:
            user_request: What the user wants to change (e.g., "make it slower")
            current_prompt: The current prompt (for context)

        Returns:
            List of suggestions
        """
        suggestions = []

        # First, try pattern matching
        matches = find_matching_patterns(user_request)

        for match in matches:
            suggestion = PromptSuggestion(
                description=match["description"],
                requirements_to_add=match["suggestions"][:2],  # Top 2 suggestions
                pacing=match.get("pacing"),
                confidence="high" if len(match["suggestions"]) > 1 else "medium",
            )
            suggestions.append(suggestion)

        # If no pattern matches, use LLM for suggestion
        if not suggestions:
            llm_suggestion = self._suggest_with_llm(user_request, current_prompt)
            if llm_suggestion:
                suggestions.append(llm_suggestion)

        return suggestions

    def _suggest_with_llm(
        self,
        user_request: str,
        current_prompt: Optional[AnimationPrompt] = None,
    ) -> Optional[PromptSuggestion]:
        """Use LLM to generate a suggestion for non-matching requests."""
        try:
            llm = self._get_llm_client()

            context = ""
            if current_prompt:
                context = f"""
Current prompt:
Topic: {current_prompt.topic}
Requirements: {', '.join(current_prompt.requirements) if current_prompt.requirements else 'none'}
"""

            prompt = f"""You are helping someone create a math animation. They want to change their animation prompt.

{context}

The user says: "{user_request}"

Suggest 1-2 specific requirements they should add to their prompt to achieve this.
Each requirement should be a clear, actionable instruction for generating Manim animation code.

Respond in this exact format (one requirement per line):
REQUIREMENT: <requirement text>
REQUIREMENT: <requirement text>

Keep requirements concise (under 15 words each)."""

            response = llm.generate(prompt, max_tokens=200, temperature=0.3)

            # Parse response
            requirements = []
            for line in response.content.split("\n"):
                if line.strip().startswith("REQUIREMENT:"):
                    req = line.replace("REQUIREMENT:", "").strip()
                    if req:
                        requirements.append(req)

            if requirements:
                return PromptSuggestion(
                    description=f"Based on: {user_request}",
                    requirements_to_add=requirements[:2],
                    confidence="medium",
                )

        except Exception:
            pass  # Fall through to return None

        return None

    def suggest_improvements(
        self,
        current_prompt: AnimationPrompt,
        current_code: Optional[str] = None,
    ) -> list[PromptSuggestion]:
        """Suggest general improvements for the current animation.

        Args:
            current_prompt: The current prompt
            current_code: The generated code (optional, for analysis)

        Returns:
            List of improvement suggestions
        """
        suggestions = []

        # Check for common missing elements
        requirements_text = " ".join(current_prompt.requirements).lower()

        # Suggest pacing if not set
        if not current_prompt.pacing and "slow" not in requirements_text and "fast" not in requirements_text:
            suggestions.append(PromptSuggestion(
                description="Control animation pacing",
                requirements_to_add=["Use slow pacing with 1-2 second pauses between steps"],
                pacing="slow",
                confidence="medium",
            ))

        # Suggest labels if not mentioned
        if "label" not in requirements_text and "text" not in requirements_text:
            suggestions.append(PromptSuggestion(
                description="Add labels and annotations",
                requirements_to_add=["Label key elements clearly", "Add descriptive text annotations"],
                confidence="medium",
            ))

        # Suggest sequential animation if not mentioned
        if "one at a time" not in requirements_text and "sequential" not in requirements_text:
            suggestions.append(PromptSuggestion(
                description="Show elements sequentially",
                requirements_to_add=["Introduce elements one at a time"],
                confidence="low",
            ))

        # Suggest formula display for math topics
        topic_lower = current_prompt.topic.lower()
        math_keywords = ["theorem", "formula", "equation", "proof", "derivative", "integral"]
        if any(kw in topic_lower for kw in math_keywords):
            if "formula" not in requirements_text and "equation" not in requirements_text:
                suggestions.append(PromptSuggestion(
                    description="Display the mathematical formula",
                    requirements_to_add=["Show the main formula or equation clearly"],
                    confidence="high",
                ))

        return suggestions[:3]  # Return top 3 suggestions

    def get_pattern_help(self) -> dict[str, list[str]]:
        """Get a summary of available patterns for help display.

        Returns:
            Dict mapping category to list of keywords
        """
        categories = {
            "Timing": ["slower", "faster", "pause"],
            "Sequencing": ["one at a time", "step by step", "simultaneous"],
            "Visual": ["color", "highlight", "simpler", "more detail"],
            "Text": ["label", "bigger text", "formula", "equation"],
            "Animation": ["draw gradually", "transform", "fade"],
            "Camera": ["zoom", "pan", "focus"],
        }
        return categories
