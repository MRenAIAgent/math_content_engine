"""Tests for knowledge graph concept extractor (no API key needed)."""

import json
from unittest.mock import MagicMock

import pytest

from math_content_engine.knowledge_graph.concept_extractor import (
    ConceptExtractor,
    ConceptExtractionResult,
    ExtractedConcept,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


VALID_LLM_RESPONSE = json.dumps(
    {
        "concepts": [
            {
                "concept_id": "algebra.pre_algebra.two_step_equations",
                "name": "Two-Step Linear Equations",
                "description": "Solve ax+b=c using inverse operations.",
                "category": "pre_algebra",
                "difficulty": 3,
                "confidence": 0.95,
                "evidence": "Solve 2x + 3 = 7 example in section 2.1",
                "prerequisites": ["algebra.pre_algebra.one_step_equations"],
                "examples": ["2x+3=7"],
            },
            {
                "concept_id": "algebra.linear_functions.slope",
                "name": "Slope of a Line",
                "description": "Calculate rise/run between two points.",
                "category": "linear_functions",
                "difficulty": 3,
                "confidence": 0.8,
                "evidence": "Finding slope between two points",
                "prerequisites": [],
                "examples": ["Find slope between (1,2) and (3,6)"],
            },
            {
                "concept_id": "algebra.linear_functions.point_slope_form",
                "name": "Point-Slope Form",
                "description": "Write equation using point and slope.",
                "category": "linear_functions",
                "difficulty": 3,
                "confidence": 0.85,
                "evidence": "y-2=3(x-1) example",
                "prerequisites": ["algebra.linear_functions.slope"],
                "examples": ["y-2=3(x-1)"],
            },
        ],
        "summary": "Chapter covers linear equations and slope basics.",
    }
)


LOW_CONFIDENCE_RESPONSE = json.dumps(
    {
        "concepts": [
            {
                "concept_id": "algebra.pre_algebra.two_step_equations",
                "name": "Two-Step Linear Equations",
                "description": "Solving equations with two steps.",
                "category": "pre_algebra",
                "difficulty": 3,
                "confidence": 0.95,
                "evidence": "Direct equation solving",
            },
            {
                "concept_id": "algebra.number_sense.counting",
                "name": "Counting Up/Down",
                "description": "Count forward or backward.",
                "category": "number_sense",
                "difficulty": 1,
                "confidence": 0.3,
                "evidence": "Vaguely mentioned counting",
            },
        ],
        "summary": "Mostly linear equations.",
    }
)


def _make_extractor(llm_response: str) -> ConceptExtractor:
    """Create a ConceptExtractor with mocked LLM returning given response."""
    mock_client = MagicMock()
    mock_client.generate.return_value = MagicMock(content=llm_response)
    return ConceptExtractor(llm_client=mock_client)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestParseValidResponse:
    def test_extracted_concepts(self):
        extractor = _make_extractor(VALID_LLM_RESPONSE)
        result = extractor.extract_concepts("some math content")

        assert len(result.concepts) == 3
        assert result.concepts[0].concept_id == "algebra.pre_algebra.two_step_equations"
        assert result.concepts[0].confidence == 0.95
        assert result.concepts[1].concept_id == "algebra.linear_functions.slope"

    def test_concept_details(self):
        extractor = _make_extractor(VALID_LLM_RESPONSE)
        result = extractor.extract_concepts("some math content")

        c = result.concepts[2]
        assert c.name == "Point-Slope Form"
        assert c.category == "linear_functions"
        assert c.prerequisites == ["algebra.linear_functions.slope"]

    def test_summary(self):
        extractor = _make_extractor(VALID_LLM_RESPONSE)
        result = extractor.extract_concepts("some math content")

        assert "linear equations" in result.summary.lower()

    def test_no_error(self):
        extractor = _make_extractor(VALID_LLM_RESPONSE)
        result = extractor.extract_concepts("some math content")

        assert result.error is None


class TestMalformedResponse:
    def test_not_json(self):
        extractor = _make_extractor("This is not JSON at all")
        result = extractor.extract_concepts("some content")

        assert result.error is not None
        assert len(result.concepts) == 0

    def test_empty_response(self):
        extractor = _make_extractor("")
        result = extractor.extract_concepts("some content")

        assert result.error is not None

    def test_llm_exception(self):
        mock_client = MagicMock()
        mock_client.generate.side_effect = RuntimeError("API down")
        extractor = ConceptExtractor(llm_client=mock_client)

        result = extractor.extract_concepts("some content")
        assert result.error is not None
        assert "API down" in result.error

    def test_empty_content(self):
        extractor = _make_extractor(VALID_LLM_RESPONSE)
        result = extractor.extract_concepts("")

        assert result.error == "Empty content provided"


class TestConfidenceThreshold:
    def test_default_threshold_filters_low(self):
        extractor = _make_extractor(LOW_CONFIDENCE_RESPONSE)
        result = extractor.extract_concepts("some content")

        assert len(result.concepts) == 1
        assert result.concepts[0].concept_id == "algebra.pre_algebra.two_step_equations"

    def test_low_threshold_keeps_all(self):
        extractor = _make_extractor(LOW_CONFIDENCE_RESPONSE)
        result = extractor.extract_concepts("some content", confidence_threshold=0.1)

        assert len(result.concepts) == 2

    def test_high_threshold_filters_more(self):
        extractor = _make_extractor(VALID_LLM_RESPONSE)
        result = extractor.extract_concepts("some content", confidence_threshold=0.9)

        assert len(result.concepts) == 1
        assert result.concepts[0].concept_id == "algebra.pre_algebra.two_step_equations"


class TestSerialization:
    def test_to_dict(self):
        result = ConceptExtractionResult(
            concepts=[
                ExtractedConcept(
                    concept_id="algebra.pre_algebra.two_step",
                    name="Test",
                    description="desc",
                    category="pre_algebra",
                    difficulty=3,
                    confidence=0.9,
                    evidence="evidence",
                    prerequisites=["AT-24"],
                    examples=["ex"],
                ),
            ],
            summary="test summary",
        )
        d = result.to_dict()

        assert len(d["concepts"]) == 1
        assert d["concepts"][0]["concept_id"] == "algebra.pre_algebra.two_step"
        assert d["concepts"][0]["confidence"] == 0.9
        assert d["summary"] == "test summary"
        assert d["error"] is None

    def test_to_dict_roundtrip(self):
        result = ConceptExtractionResult(
            concepts=[
                ExtractedConcept(
                    concept_id="algebra.pre_algebra.two_step",
                    name="Test",
                    description="desc",
                    category="pre_algebra",
                    difficulty=3,
                    confidence=0.9,
                    evidence="evidence",
                ),
            ],
            summary="test",
        )
        serialized = json.dumps(result.to_dict())
        loaded = json.loads(serialized)

        assert loaded["concepts"][0]["concept_id"] == "algebra.pre_algebra.two_step"


class TestDisplay:
    def test_display_with_concepts(self):
        result = ConceptExtractionResult(
            concepts=[
                ExtractedConcept(
                    concept_id="algebra.pre_algebra.two_step",
                    name="Two-Step Equations",
                    description="Solve two-step equations",
                    category="pre_algebra",
                    difficulty=3,
                    confidence=0.95,
                    evidence="section 2.1",
                ),
                ExtractedConcept(
                    concept_id="algebra.linear_functions.point_slope",
                    name="Point-Slope Form",
                    description="Write equation using point and slope",
                    category="linear_functions",
                    difficulty=3,
                    confidence=0.85,
                    evidence="example problem",
                    prerequisites=["algebra.linear_functions.slope"],
                ),
            ],
            summary="Linear algebra basics",
        )
        output = result.display()

        assert "two_step" in output
        assert "95%" in output
        assert "point_slope" in output
        assert "Point-Slope" in output
        assert "Linear algebra basics" in output

    def test_display_empty(self):
        result = ConceptExtractionResult(summary="Nothing found")
        output = result.display()

        assert "(none)" in output
        assert "Nothing found" in output

    def test_display_with_error(self):
        result = ConceptExtractionResult(error="Something broke")
        output = result.display()

        assert "Error: Something broke" in output


class TestEdgeCases:
    def test_non_numeric_confidence_defaults(self):
        """LLM returns non-numeric confidence value."""
        bad_response = json.dumps({
            "concepts": [
                {
                    "concept_id": "algebra.pre_algebra.two_step",
                    "name": "Test",
                    "description": "desc",
                    "category": "pre_algebra",
                    "confidence": "high",
                    "difficulty": "hard",
                    "evidence": "test",
                }
            ],
            "summary": "test",
        })
        extractor = _make_extractor(bad_response)
        result = extractor.extract_concepts("some content", confidence_threshold=0.0)

        assert len(result.concepts) == 1
        assert result.concepts[0].confidence == 0.0
        assert result.concepts[0].difficulty == 3  # default

    def test_large_content_truncated(self):
        """Content over 15K chars is truncated before sending to LLM."""
        extractor = _make_extractor(VALID_LLM_RESPONSE)
        large_content = "x" * 20000
        result = extractor.extract_concepts(large_content)

        # Should still work (LLM mock returns valid response)
        assert result.error is None
        assert len(result.concepts) == 3

    def test_concepts_with_missing_optional_fields(self):
        """LLM omits optional fields in response."""
        minimal_response = json.dumps({
            "concepts": [
                {"name": "Minimal Concept"}
            ],
            "summary": "minimal",
        })
        extractor = _make_extractor(minimal_response)
        result = extractor.extract_concepts("content", confidence_threshold=0.0)

        assert len(result.concepts) == 1
        assert result.concepts[0].concept_id == ""
        assert result.concepts[0].difficulty == 3
        assert result.concepts[0].confidence == 0.8  # default

    def test_legacy_format_matched_and_new_concepts(self):
        """Parser handles old matched_concepts + new_concepts format."""
        legacy_response = json.dumps({
            "matched_concepts": [
                {
                    "concept_id": "AT-24",
                    "name": "Two-Step Equations",
                    "confidence": 0.95,
                    "evidence": "section 2.1",
                },
            ],
            "new_concepts": [
                {
                    "suggested_id": "LF-41",
                    "name": "Point-Slope Form",
                    "description": "Write equation using point and slope",
                    "category": "Linear",
                    "difficulty": 3,
                },
            ],
            "summary": "Linear algebra basics",
        })
        extractor = _make_extractor(legacy_response)
        result = extractor.extract_concepts("content", confidence_threshold=0.0)

        assert len(result.concepts) == 2
        assert result.concepts[0].concept_id == "AT-24"
        assert result.concepts[0].confidence == 0.95
        assert result.concepts[1].concept_id == "LF-41"
        assert result.concepts[1].name == "Point-Slope Form"
        assert result.summary == "Linear algebra basics"

    def test_legacy_format_only_matched(self):
        """Parser handles old format with only matched_concepts."""
        legacy_response = json.dumps({
            "matched_concepts": [
                {
                    "concept_id": "AT-24",
                    "name": "Two-Step Equations",
                    "confidence": 0.9,
                    "evidence": "test",
                },
            ],
            "new_concepts": [],
            "summary": "test",
        })
        extractor = _make_extractor(legacy_response)
        result = extractor.extract_concepts("content", confidence_threshold=0.0)

        assert len(result.concepts) == 1
        assert result.concepts[0].concept_id == "AT-24"
