"""Tests for the shared JSON repair utility.

Covers typical LLM failure modes: trailing commas, missing commas,
unescaped control characters, truncated output (max-tokens cutoff),
and valid pass-through.
"""

import json

import pytest

from math_content_engine.utils.json_repair import parse_json_with_repair, repair_json


# ---------------------------------------------------------------------------
# repair_json — trailing commas
# ---------------------------------------------------------------------------


class TestRepairTrailingCommas:
    def test_trailing_comma_in_object(self):
        raw = '{"a": 1, "b": 2,}'
        assert repair_json(raw) == {"a": 1, "b": 2}

    def test_trailing_comma_in_array(self):
        raw = '{"items": [1, 2, 3,]}'
        assert repair_json(raw) == {"items": [1, 2, 3]}

    def test_nested_trailing_commas(self):
        raw = '{"a": {"b": 1,}, "c": [1,],}'
        result = repair_json(raw)
        assert result == {"a": {"b": 1}, "c": [1]}

    def test_trailing_comma_top_level_array(self):
        raw = '[{"a": 1}, {"b": 2},]'
        result = repair_json(raw)
        assert len(result) == 2


# ---------------------------------------------------------------------------
# repair_json — missing commas
# ---------------------------------------------------------------------------


class TestRepairMissingCommas:
    def test_missing_comma_between_objects_in_array(self):
        raw = '{"items": [{"a": 1} {"b": 2}]}'
        result = repair_json(raw)
        assert len(result["items"]) == 2

    def test_missing_comma_after_object_before_string_key(self):
        raw = '[{"a": 1} {"b": 2}]'
        result = repair_json(raw)
        assert len(result) == 2

    def test_missing_comma_after_array_before_object(self):
        # ] { pattern gets a comma, but the resulting structure may still
        # be invalid (object-as-value without key). Use parse_json_with_repair
        # which falls back gracefully.
        raw = '[{"a": 1}] [{"b": 2}]'
        # This is not repairable to valid JSON — verify it raises
        with pytest.raises(json.JSONDecodeError):
            repair_json(raw)


# ---------------------------------------------------------------------------
# repair_json — unescaped control characters
# ---------------------------------------------------------------------------


class TestRepairControlCharacters:
    def test_unescaped_newline_in_value(self):
        raw = '{"text": "line1\nline2"}'
        result = repair_json(raw)
        assert "line1" in result["text"]
        assert "line2" in result["text"]

    def test_unescaped_tab_in_value(self):
        raw = '{"text": "col1\tcol2"}'
        result = repair_json(raw)
        assert "col1" in result["text"]
        assert "col2" in result["text"]


# ---------------------------------------------------------------------------
# repair_json — truncated JSON (max-tokens cutoff)
# ---------------------------------------------------------------------------


class TestRepairTruncatedJson:
    def test_truncated_object_auto_closes(self):
        # The inner array + object are complete; just missing the outer }
        raw = '{"concepts": [{"id": 1}], "count": 2'
        result = repair_json(raw)
        assert result["concepts"][0]["id"] == 1
        assert result["count"] == 2

    def test_truncated_mid_value_drops_incomplete_object(self):
        raw = '{"concepts": [{"name": "test"}, {"name": "incom'
        result = repair_json(raw)
        assert len(result["concepts"]) >= 1
        assert result["concepts"][0]["name"] == "test"

    def test_truncated_array_auto_closes(self):
        raw = '[{"text": "cue1", "time": 0.0}, {"text": "cue2"'
        result = repair_json(raw)
        assert len(result) >= 1
        assert result[0]["text"] == "cue1"

    def test_truncated_with_trailing_comma(self):
        # Truncated after a complete object + comma — repair strips the
        # trailing comma and auto-closes brackets/braces
        raw = '{"items": [{"a": 1}, {"b": 2},'
        result = repair_json(raw)
        assert result["items"][0]["a"] == 1


# ---------------------------------------------------------------------------
# parse_json_with_repair — wrapper behavior
# ---------------------------------------------------------------------------


class TestParseJsonWithRepair:
    def test_valid_json_passes_through(self):
        raw = '{"key": "value"}'
        assert parse_json_with_repair(raw) == {"key": "value"}

    def test_valid_array_passes_through(self):
        raw = '[{"a": 1}, {"b": 2}]'
        result = parse_json_with_repair(raw)
        assert len(result) == 2

    def test_invalid_json_triggers_repair(self):
        raw = '{"key": "value",}'  # trailing comma
        assert parse_json_with_repair(raw) == {"key": "value"}

    def test_unrepairable_json_raises_original_error(self):
        with pytest.raises(json.JSONDecodeError):
            parse_json_with_repair("not json at all {{{")

    def test_empty_string_raises(self):
        with pytest.raises(json.JSONDecodeError):
            parse_json_with_repair("")

    def test_integers_pass_through(self):
        assert parse_json_with_repair("42") == 42

    def test_string_passes_through(self):
        assert parse_json_with_repair('"hello"') == "hello"


# ---------------------------------------------------------------------------
# DeepSeek-specific real-world failure patterns
# ---------------------------------------------------------------------------


class TestDeepSeekSpecificFailures:
    def test_trailing_comma_in_concepts_array(self):
        raw = """{
            "concepts": [
                {"concept_id": "test.1", "name": "Slope", "confidence": 0.9},
                {"concept_id": "test.2", "name": "Intercept", "confidence": 0.8},
            ],
            "summary": "Test"
        }"""
        result = parse_json_with_repair(raw)
        assert len(result["concepts"]) == 2
        assert result["summary"] == "Test"

    def test_max_tokens_truncation_mid_object(self):
        raw = """{
            "concepts": [
                {"concept_id": "test.1", "name": "Slope", "confidence": 0.9},
                {"concept_id": "test.2", "name": "Intercep"""
        result = parse_json_with_repair(raw)
        assert len(result["concepts"]) >= 1
        assert result["concepts"][0]["name"] == "Slope"

    def test_narration_cues_array_with_trailing_comma(self):
        """narration_generator.py parses JSON arrays, not objects."""
        raw = """[
            {"text": "Welcome to the lesson", "time": 0.0},
            {"text": "Let us begin with slope", "time": 3.5},
        ]"""
        result = parse_json_with_repair(raw)
        assert len(result) == 2
        assert result[0]["text"] == "Welcome to the lesson"

    def test_exercise_in_code_block_with_trailing_comma(self):
        """exercise_generator.py first strips code fences, then parses."""
        raw = '{"exercises": [{"question": "Solve 2x=4", "answer": "x=2",}]}'
        result = parse_json_with_repair(raw)
        assert len(result["exercises"]) == 1

    def test_missing_comma_between_concept_objects(self):
        raw = """{
            "concepts": [
                {"concept_id": "a", "name": "X"}
                {"concept_id": "b", "name": "Y"}
            ]
        }"""
        result = parse_json_with_repair(raw)
        assert len(result["concepts"]) == 2
