"""Tests for playground prompt builder (no API keys needed).

Tests that prompt preview functions return well-formed PromptPreview
objects with the expected structure and content, without calling any LLM.
"""

from unittest.mock import MagicMock, patch

import pytest

from math_content_engine.api.playground.prompt_builder import (
    _build_personalization_user_prompt,
    _PERSONALIZATION_SYSTEM_PROMPT,
    _StubLLMClient,
    preview_animation_prompts,
    preview_concept_extraction_prompts,
    preview_personalization_prompts,
)
from math_content_engine.api.playground.models import PromptPreview


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

SAMPLE_TEXTBOOK = """\
# Chapter 2: Solving Linear Equations

## 2.1 One-Step Equations

A one-step equation requires one operation to solve.

**Example 1:** Solve x + 5 = 12
- Subtract 5 from both sides: x = 7

**Example 2:** Solve 3x = 15
- Divide both sides by 3: x = 5

## 2.2 Two-Step Equations

**Example 3:** Solve 2x + 3 = 11
- Subtract 3: 2x = 8
- Divide by 2: x = 4
"""


# ---------------------------------------------------------------------------
# Personalization prompt preview
# ---------------------------------------------------------------------------


class TestPersonalizationPromptPreview:
    """Test personalization prompt construction."""

    def test_returns_prompt_preview(self):
        result = preview_personalization_prompts(SAMPLE_TEXTBOOK, "basketball")

        assert isinstance(result, PromptPreview)
        assert result.stage == "personalize"

    def test_system_prompt_is_constant(self):
        result = preview_personalization_prompts(SAMPLE_TEXTBOOK, "basketball")

        assert result.system_prompt == _PERSONALIZATION_SYSTEM_PROMPT
        assert "educational content creator" in result.system_prompt

    def test_user_prompt_contains_textbook_content(self):
        result = preview_personalization_prompts(SAMPLE_TEXTBOOK, "basketball")

        assert "Solving Linear Equations" in result.user_prompt
        assert "x + 5 = 12" in result.user_prompt

    def test_user_prompt_contains_interest_context(self):
        result = preview_personalization_prompts(SAMPLE_TEXTBOOK, "basketball")

        # Should contain basketball-related content from the profile
        prompt = result.user_prompt.lower()
        assert "basketball" in prompt

    def test_user_prompt_has_transformation_rules(self):
        result = preview_personalization_prompts(SAMPLE_TEXTBOOK, "basketball")

        assert "TRANSFORMATION RULES" in result.user_prompt
        assert "Keep ALL Math Content Intact" in result.user_prompt

    def test_user_prompt_has_famous_figures(self):
        result = preview_personalization_prompts(SAMPLE_TEXTBOOK, "basketball")

        # Should include at least one famous basketball figure
        assert "Famous Figures" in result.user_prompt

    def test_user_prompt_has_scenarios(self):
        result = preview_personalization_prompts(SAMPLE_TEXTBOOK, "basketball")

        assert "Example Scenarios" in result.user_prompt

    def test_unknown_interest_returns_error_prompt(self):
        result = preview_personalization_prompts(SAMPLE_TEXTBOOK, "nonexistent_xyz")

        assert "ERROR" in result.user_prompt
        assert "nonexistent_xyz" in result.user_prompt

    def test_different_interests_produce_different_prompts(self):
        basketball = preview_personalization_prompts(SAMPLE_TEXTBOOK, "basketball")
        gaming = preview_personalization_prompts(SAMPLE_TEXTBOOK, "gaming")

        assert basketball.user_prompt != gaming.user_prompt


class TestBuildPersonalizationUserPrompt:
    """Test the internal _build_personalization_user_prompt function."""

    def test_includes_visual_theme(self):
        prompt = _build_personalization_user_prompt(SAMPLE_TEXTBOOK, "basketball")

        assert "Visual Theme" in prompt
        assert "Colors:" in prompt

    def test_includes_fun_facts_section(self):
        prompt = _build_personalization_user_prompt(SAMPLE_TEXTBOOK, "basketball")

        assert "Fun Facts" in prompt

    def test_includes_original_content(self):
        prompt = _build_personalization_user_prompt("Special math: y = mx + b", "basketball")

        assert "y = mx + b" in prompt

    def test_unknown_interest_returns_error_string(self):
        prompt = _build_personalization_user_prompt("content", "totally_fake_interest")

        assert "[ERROR:" in prompt
        assert "totally_fake_interest" in prompt


# ---------------------------------------------------------------------------
# Concept extraction prompt preview
# ---------------------------------------------------------------------------


class TestConceptExtractionPromptPreview:
    """Test concept extraction prompt construction."""

    def test_returns_prompt_preview(self):
        result = preview_concept_extraction_prompts(SAMPLE_TEXTBOOK)

        assert isinstance(result, PromptPreview)
        assert result.stage == "extract_concepts"

    def test_system_prompt_has_concept_list(self):
        result = preview_concept_extraction_prompts(SAMPLE_TEXTBOOK)

        # System prompt should contain concept IDs from the knowledge graph
        assert "AT-" in result.system_prompt or "concept" in result.system_prompt.lower()

    def test_user_prompt_contains_content(self):
        result = preview_concept_extraction_prompts(SAMPLE_TEXTBOOK)

        assert "Linear Equations" in result.user_prompt
        assert "Analyze" in result.user_prompt

    def test_long_content_is_truncated(self):
        long_content = "x" * 20000
        result = preview_concept_extraction_prompts(long_content)

        # Should truncate and add notice
        assert "[Content truncated" in result.user_prompt
        assert len(result.user_prompt) < 20000

    def test_short_content_not_truncated(self):
        result = preview_concept_extraction_prompts("Short content about algebra")

        assert "[Content truncated" not in result.user_prompt

    def test_system_prompt_is_well_formed(self):
        result = preview_concept_extraction_prompts(SAMPLE_TEXTBOOK)

        # Should be a non-empty system prompt
        assert len(result.system_prompt) > 100


# ---------------------------------------------------------------------------
# Animation prompt preview
# ---------------------------------------------------------------------------


class TestAnimationPromptPreview:
    """Test animation generation prompt construction."""

    def test_returns_prompt_preview(self):
        result = preview_animation_prompts(topic="Pythagorean Theorem")

        assert isinstance(result, PromptPreview)
        assert result.stage == "generate_animation"

    def test_system_prompt_dark_style(self):
        result = preview_animation_prompts(
            topic="Pythagorean Theorem",
            animation_style="dark",
        )

        # Dark system prompt should reference dark theme concepts
        assert len(result.system_prompt) > 100

    def test_system_prompt_light_style(self):
        result = preview_animation_prompts(
            topic="Pythagorean Theorem",
            animation_style="light",
        )

        assert len(result.system_prompt) > 100

    def test_dark_and_light_prompts_differ(self):
        dark = preview_animation_prompts(topic="Test", animation_style="dark")
        light = preview_animation_prompts(topic="Test", animation_style="light")

        assert dark.system_prompt != light.system_prompt

    def test_user_prompt_contains_topic(self):
        result = preview_animation_prompts(topic="Pythagorean Theorem")

        assert "Pythagorean Theorem" in result.user_prompt

    def test_user_prompt_contains_requirements(self):
        result = preview_animation_prompts(
            topic="Quadratic Formula",
            requirements="Show step-by-step derivation",
        )

        assert "step-by-step" in result.user_prompt

    def test_user_prompt_contains_audience_level(self):
        result = preview_animation_prompts(
            topic="Integration",
            audience_level="college",
        )

        assert "college" in result.user_prompt

    def test_with_interest_personalization(self):
        result_plain = preview_animation_prompts(topic="Linear Equations")
        result_personalized = preview_animation_prompts(
            topic="Linear Equations",
            interest="basketball",
        )

        # Personalized version should have additional context
        assert len(result_personalized.user_prompt) >= len(result_plain.user_prompt)

    def test_with_invalid_interest_still_works(self):
        """An invalid interest should not crash — just skips personalization."""
        result = preview_animation_prompts(
            topic="Fractions",
            interest="nonexistent_xyz",
        )

        assert isinstance(result, PromptPreview)
        assert "Fractions" in result.user_prompt

    def test_default_parameters(self):
        result = preview_animation_prompts(topic="Algebra Basics")

        assert result.stage == "generate_animation"
        assert "Algebra Basics" in result.user_prompt


# ---------------------------------------------------------------------------
# StubLLMClient
# ---------------------------------------------------------------------------


class TestStubLLMClient:
    """Test that _StubLLMClient behaves correctly."""

    def test_init_succeeds(self):
        client = _StubLLMClient()

        assert client.api_key == "stub"
        assert client.model == "stub"

    def test_generate_raises(self):
        client = _StubLLMClient()

        with pytest.raises(RuntimeError, match="should never be called"):
            client.generate("test prompt")

    def test_generate_with_retry_raises(self):
        client = _StubLLMClient()

        with pytest.raises(RuntimeError, match="should never be called"):
            client.generate_with_retry("test prompt")


# ---------------------------------------------------------------------------
# Cross-stage consistency
# ---------------------------------------------------------------------------


class TestCrossStageConsistency:
    """Ensure all stages produce consistent PromptPreview objects."""

    def test_all_previews_have_non_empty_prompts(self):
        stages = [
            preview_personalization_prompts(SAMPLE_TEXTBOOK, "basketball"),
            preview_concept_extraction_prompts(SAMPLE_TEXTBOOK),
            preview_animation_prompts(topic="Linear Equations"),
        ]

        for preview in stages:
            assert len(preview.system_prompt) > 0, f"Empty system prompt for {preview.stage}"
            assert len(preview.user_prompt) > 0, f"Empty user prompt for {preview.stage}"
            assert preview.stage in (
                "personalize",
                "extract_concepts",
                "generate_animation",
            )

    def test_previews_are_serializable(self):
        """All PromptPreview objects should serialize to dict cleanly."""
        stages = [
            preview_personalization_prompts(SAMPLE_TEXTBOOK, "basketball"),
            preview_concept_extraction_prompts(SAMPLE_TEXTBOOK),
            preview_animation_prompts(topic="Linear Equations"),
        ]

        for preview in stages:
            d = preview.model_dump()
            assert "stage" in d
            assert "system_prompt" in d
            assert "user_prompt" in d
            assert isinstance(d["system_prompt"], str)
            assert isinstance(d["user_prompt"], str)

    def test_empty_textbook_content(self):
        """All stages handle empty input gracefully."""
        p1 = preview_personalization_prompts("", "basketball")
        p2 = preview_concept_extraction_prompts("")

        assert isinstance(p1, PromptPreview)
        assert isinstance(p2, PromptPreview)
