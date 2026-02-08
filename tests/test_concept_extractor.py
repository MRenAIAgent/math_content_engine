"""Tests for knowledge graph concept extractor (no API key needed)."""

import json
from unittest.mock import MagicMock

import pytest

from math_content_engine.knowledge_graph.concept_extractor import (
    ConceptExtractor,
    ConceptExtractionResult,
    MatchedConcept,
    NewConcept,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_GRAPH = {
    "name": "Test Graph",
    "concepts": [
        {
            "id": "AT-24",
            "name": "Two-Step Linear Equations",
            "description": "Solve ax+b=c.",
            "difficulty": 3,
            "category": "Pre-Algebra",
            "prerequisites": ["AT-22"],
            "dependents": ["AT-25"],
            "examples": ["Solve 2x+3=7"],
            "grade_level": "",
            "related": [],
            "time_to_master": 120,
        },
        {
            "id": "LF-30",
            "name": "Slope of a Line",
            "description": "Calculate rise/run.",
            "difficulty": 3,
            "category": "Linear",
            "prerequisites": [],
            "dependents": [],
            "examples": ["Find slope between (1,2) and (3,6)"],
            "grade_level": "",
            "related": [],
            "time_to_master": 90,
        },
        {
            "id": "NS-01",
            "name": "Counting Up/Down",
            "description": "Count forward or backward by 1s.",
            "difficulty": 1,
            "category": "Number Sense",
            "prerequisites": [],
            "dependents": [],
            "examples": ["Count from 1 to 10"],
            "grade_level": "",
            "related": [],
            "time_to_master": 30,
        },
    ],
    "relationships": [],
}


VALID_LLM_RESPONSE = json.dumps(
    {
        "matched_concepts": [
            {
                "concept_id": "AT-24",
                "name": "Two-Step Linear Equations",
                "confidence": 0.95,
                "evidence": "Solve 2x + 3 = 7 example in section 2.1",
            },
            {
                "concept_id": "LF-30",
                "name": "Slope of a Line",
                "confidence": 0.8,
                "evidence": "Finding slope between two points",
            },
        ],
        "new_concepts": [
            {
                "suggested_id": "LF-41",
                "name": "Point-Slope Form",
                "description": "Write equation using point and slope.",
                "category": "Linear",
                "difficulty": 3,
                "prerequisites": ["LF-30"],
                "examples": ["Write y-2=3(x-1)"],
            }
        ],
        "summary": "Chapter covers linear equations and slope basics.",
    }
)


LOW_CONFIDENCE_RESPONSE = json.dumps(
    {
        "matched_concepts": [
            {
                "concept_id": "AT-24",
                "name": "Two-Step Linear Equations",
                "confidence": 0.95,
                "evidence": "Direct equation solving",
            },
            {
                "concept_id": "NS-01",
                "name": "Counting Up/Down",
                "confidence": 0.3,
                "evidence": "Vaguely mentioned counting",
            },
        ],
        "new_concepts": [],
        "summary": "Mostly linear equations.",
    }
)


INVALID_ID_RESPONSE = json.dumps(
    {
        "matched_concepts": [
            {
                "concept_id": "FAKE-99",
                "name": "Not Real",
                "confidence": 0.9,
                "evidence": "Does not exist",
            },
            {
                "concept_id": "AT-24",
                "name": "Two-Step Linear Equations",
                "confidence": 0.9,
                "evidence": "Real concept",
            },
        ],
        "new_concepts": [],
        "summary": "Test invalid IDs.",
    }
)


def _make_extractor(llm_response: str) -> ConceptExtractor:
    """Create a ConceptExtractor with mocked LLM returning given response."""
    mock_client = MagicMock()
    mock_client.generate.return_value = MagicMock(content=llm_response)
    return ConceptExtractor(llm_client=mock_client, graph=SAMPLE_GRAPH)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestParseValidResponse:
    def test_matched_concepts(self):
        extractor = _make_extractor(VALID_LLM_RESPONSE)
        result = extractor.extract_concepts("some math content")

        assert len(result.matched_concepts) == 2
        assert result.matched_concepts[0].concept_id == "AT-24"
        assert result.matched_concepts[0].confidence == 0.95
        assert result.matched_concepts[1].concept_id == "LF-30"

    def test_new_concepts(self):
        extractor = _make_extractor(VALID_LLM_RESPONSE)
        result = extractor.extract_concepts("some math content")

        assert len(result.new_concepts) == 1
        assert result.new_concepts[0].suggested_id == "LF-41"
        assert result.new_concepts[0].name == "Point-Slope Form"
        assert result.new_concepts[0].category == "Linear"
        assert result.new_concepts[0].prerequisites == ["LF-30"]

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
        assert len(result.matched_concepts) == 0
        assert len(result.new_concepts) == 0

    def test_empty_response(self):
        extractor = _make_extractor("")
        result = extractor.extract_concepts("some content")

        assert result.error is not None

    def test_llm_exception(self):
        mock_client = MagicMock()
        mock_client.generate.side_effect = RuntimeError("API down")
        extractor = ConceptExtractor(llm_client=mock_client, graph=SAMPLE_GRAPH)

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

        assert len(result.matched_concepts) == 1
        assert result.matched_concepts[0].concept_id == "AT-24"

    def test_low_threshold_keeps_all(self):
        extractor = _make_extractor(LOW_CONFIDENCE_RESPONSE)
        result = extractor.extract_concepts("some content", confidence_threshold=0.1)

        assert len(result.matched_concepts) == 2

    def test_high_threshold_filters_more(self):
        extractor = _make_extractor(VALID_LLM_RESPONSE)
        result = extractor.extract_concepts("some content", confidence_threshold=0.9)

        assert len(result.matched_concepts) == 1
        assert result.matched_concepts[0].concept_id == "AT-24"


class TestConceptIdValidation:
    def test_invalid_ids_rejected(self):
        extractor = _make_extractor(INVALID_ID_RESPONSE)
        result = extractor.extract_concepts("some content")

        assert len(result.matched_concepts) == 1
        assert result.matched_concepts[0].concept_id == "AT-24"

    def test_all_valid_ids_kept(self):
        extractor = _make_extractor(VALID_LLM_RESPONSE)
        result = extractor.extract_concepts("some content")

        ids = {c.concept_id for c in result.matched_concepts}
        assert ids == {"AT-24", "LF-30"}


class TestSerialization:
    def test_to_dict(self):
        result = ConceptExtractionResult(
            matched_concepts=[
                MatchedConcept("AT-24", "Test", 0.9, "evidence"),
            ],
            new_concepts=[
                NewConcept("LF-41", "New", "desc", "Linear", 3, ["AT-24"], ["ex"]),
            ],
            summary="test summary",
        )
        d = result.to_dict()

        assert len(d["matched_concepts"]) == 1
        assert d["matched_concepts"][0]["concept_id"] == "AT-24"
        assert len(d["new_concepts"]) == 1
        assert d["new_concepts"][0]["suggested_id"] == "LF-41"
        assert d["summary"] == "test summary"
        assert d["error"] is None

    def test_to_dict_roundtrip(self):
        result = ConceptExtractionResult(
            matched_concepts=[
                MatchedConcept("AT-24", "Test", 0.9, "evidence"),
            ],
            new_concepts=[],
            summary="test",
        )
        serialized = json.dumps(result.to_dict())
        loaded = json.loads(serialized)

        assert loaded["matched_concepts"][0]["concept_id"] == "AT-24"


class TestDisplay:
    def test_display_with_concepts(self):
        result = ConceptExtractionResult(
            matched_concepts=[
                MatchedConcept("AT-24", "Two-Step Equations", 0.95, "section 2.1"),
            ],
            new_concepts=[
                NewConcept("LF-41", "Point-Slope", "desc", "Linear", 3, ["LF-30"], []),
            ],
            summary="Linear algebra basics",
        )
        output = result.display()

        assert "AT-24" in output
        assert "95%" in output
        assert "LF-41" in output
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


class TestBuildConceptListPrompt:
    def test_all_concepts_listed(self):
        extractor = _make_extractor(VALID_LLM_RESPONSE)
        prompt = extractor._build_concept_list_prompt()

        assert "AT-24" in prompt
        assert "LF-30" in prompt
        assert "NS-01" in prompt
        assert "Two-Step Linear Equations" in prompt
        assert "Pre-Algebra" in prompt


class TestEdgeCases:
    def test_non_numeric_confidence_defaults_to_zero(self):
        """LLM returns non-numeric confidence value."""
        bad_response = json.dumps({
            "matched_concepts": [
                {
                    "concept_id": "AT-24",
                    "name": "Test",
                    "confidence": "high",
                    "evidence": "test",
                }
            ],
            "new_concepts": [
                {
                    "suggested_id": "LF-41",
                    "name": "New",
                    "description": "desc",
                    "category": "Linear",
                    "difficulty": "hard",
                    "prerequisites": [],
                    "examples": [],
                }
            ],
            "summary": "test",
        })
        extractor = _make_extractor(bad_response)
        result = extractor.extract_concepts("some content", confidence_threshold=0.0)

        assert len(result.matched_concepts) == 1
        assert result.matched_concepts[0].confidence == 0.0
        assert len(result.new_concepts) == 1
        assert result.new_concepts[0].difficulty == 3  # default

    def test_large_content_truncated(self):
        """Content over 15K chars is truncated before sending to LLM."""
        extractor = _make_extractor(VALID_LLM_RESPONSE)
        large_content = "x" * 20000
        result = extractor.extract_concepts(large_content)

        # Should still work (LLM mock returns valid response)
        assert result.error is None
        assert len(result.matched_concepts) == 2

    def test_concepts_with_missing_optional_fields(self):
        """LLM omits optional fields in response."""
        minimal_response = json.dumps({
            "matched_concepts": [
                {"concept_id": "AT-24", "name": "Test", "confidence": 0.9}
            ],
            "new_concepts": [
                {"name": "Minimal Concept"}
            ],
            "summary": "minimal",
        })
        extractor = _make_extractor(minimal_response)
        result = extractor.extract_concepts("content")

        assert len(result.matched_concepts) == 1
        assert result.matched_concepts[0].evidence == ""
        assert len(result.new_concepts) == 1
        assert result.new_concepts[0].suggested_id == ""
        assert result.new_concepts[0].difficulty == 3
