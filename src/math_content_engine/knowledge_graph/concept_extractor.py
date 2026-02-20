"""
LLM-based concept extraction from markdown content.

Purely extracts mathematical concepts from textbook/markdown content
using LLM analysis — no predefined knowledge graph required.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from ..llm.base import BaseLLMClient

logger = logging.getLogger(__name__)

MAX_CONTENT_CHARS = 15000


def _escape_ctrl(m: re.Match) -> str:
    """``re.sub`` callback: escape bare control characters inside a JSON
    string value (newlines, tabs, etc.) so the JSON parser won't choke."""
    return m.group(0).replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")

CONCEPT_EXTRACTOR_SYSTEM_PROMPT = """You are a math curriculum analyst. Your job is to analyze \
math textbook content and extract all mathematical concepts that are taught or referenced.

You will be given textbook/markdown content to analyze.

## Your Task:
1. Identify every mathematical concept covered in the content
2. For each concept, provide a clear name, description, and evidence from the text
3. Categorize each concept by topic area
4. Estimate the difficulty level
5. Write a brief summary of the mathematical topics covered

## Response Format:
Return ONLY valid JSON, no other text:
{
    "concepts": [
        {
            "concept_id": "algebra.pre_algebra.two_step_equations",
            "name": "Two-Step Linear Equations",
            "description": "Solving equations that require two inverse operations",
            "category": "pre_algebra",
            "difficulty": 2,
            "confidence": 0.95,
            "evidence": "short quote or description showing where this concept appears",
            "prerequisites": ["algebra.pre_algebra.one_step_equations"],
            "examples": ["2x + 3 = 11"]
        }
    ],
    "summary": "Brief description of the math topics covered in this content"
}

## Rules:
- Extract ALL math concepts you find — do not limit to any predefined list
- Concept IDs use hierarchical dot notation: algebra.{topic}.{concept}
  Topics include but are not limited to: number_sense, pre_algebra, linear_functions, \
quadratics, exponential_functions, polynomials, function_tools, geometry, statistics, \
trigonometry, calculus
- Only include concepts you are confident appear in the content (confidence >= 0.7)
- Difficulty scale: 1 (basic) to 5 (advanced)
- Keep evidence snippets under 100 characters
- List prerequisites as concept IDs when relationships are clear from the content
"""


@dataclass
class ExtractedConcept:
    """A mathematical concept extracted from content."""

    concept_id: str
    name: str
    description: str
    category: str
    difficulty: int
    confidence: float
    evidence: str
    prerequisites: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)


@dataclass
class ConceptExtractionResult:
    """Result of concept extraction from markdown content."""

    concepts: List[ExtractedConcept] = field(default_factory=list)
    summary: str = ""
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Serialize to JSON-safe dictionary."""
        return {
            "concepts": [
                {
                    "concept_id": c.concept_id,
                    "name": c.name,
                    "description": c.description,
                    "category": c.category,
                    "difficulty": c.difficulty,
                    "confidence": c.confidence,
                    "evidence": c.evidence,
                    "prerequisites": c.prerequisites,
                    "examples": c.examples,
                }
                for c in self.concepts
            ],
            "summary": self.summary,
            "error": self.error,
        }

    def display(self) -> str:
        """Format for console output."""
        lines = []
        lines.append(f"Summary: {self.summary}")
        lines.append("")

        if self.concepts:
            lines.append(f"Extracted Concepts ({len(self.concepts)}):")
            for c in self.concepts:
                lines.append(
                    f"  [{c.concept_id}] {c.name} "
                    f"(confidence: {c.confidence:.0%}, difficulty: {c.difficulty})"
                )
                lines.append(f"    {c.description}")
                lines.append(f"    Evidence: {c.evidence}")
                if c.prerequisites:
                    lines.append(f"    Prerequisites: {', '.join(c.prerequisites)}")
        else:
            lines.append("Extracted Concepts: (none)")

        if self.error:
            lines.append(f"\nError: {self.error}")

        return "\n".join(lines)


class ConceptExtractor:
    """
    Extracts mathematical concepts from markdown content using LLM.

    Purely analyzes textbook content to identify math concepts —
    no predefined knowledge graph required.
    """

    def __init__(
        self,
        llm_client: BaseLLMClient,
    ):
        """
        Args:
            llm_client: LLM client for concept extraction
        """
        self.llm_client = llm_client
        logger.info("ConceptExtractor initialized (pure extraction mode)")

    def extract_concepts(
        self,
        markdown_content: str,
        confidence_threshold: float = 0.7,
    ) -> ConceptExtractionResult:
        """
        Extract math concepts from markdown content.

        Args:
            markdown_content: Textbook/markdown content to analyze
            confidence_threshold: Minimum confidence to include a concept

        Returns:
            ConceptExtractionResult with extracted concepts
        """
        if not markdown_content.strip():
            return ConceptExtractionResult(error="Empty content provided")

        truncated = markdown_content[:MAX_CONTENT_CHARS]
        if len(markdown_content) > MAX_CONTENT_CHARS:
            truncated += "\n\n[Content truncated for analysis]"
            logger.info(
                f"Content truncated from {len(markdown_content)} "
                f"to {MAX_CONTENT_CHARS} chars"
            )

        system_prompt = CONCEPT_EXTRACTOR_SYSTEM_PROMPT

        user_prompt = (
            "Analyze this math textbook content and extract all mathematical concepts:\n\n"
            f"{truncated}"
        )

        try:
            response = self.llm_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
            )
            result = self._parse_llm_response(response.content)
        except Exception as e:
            logger.exception("Concept extraction failed")
            return ConceptExtractionResult(
                error=f"LLM call failed: {str(e)}"
            )

        # Filter by confidence threshold
        result.concepts = [
            c
            for c in result.concepts
            if c.confidence >= confidence_threshold
        ]

        logger.info(
            f"Extracted {len(result.concepts)} concepts"
        )
        return result

    @staticmethod
    def _safe_float(value, default: float = 0.0) -> float:
        """Safely convert a value to float."""
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _safe_int(value, default: int = 3) -> int:
        """Safely convert a value to int."""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _repair_json(raw: str) -> dict:
        """Best-effort repair of malformed JSON from LLMs.

        Only called when ``json.loads`` fails on the raw string.  Applies
        a sequence of lightweight fixups that handle the most common LLM
        mistakes (trailing / missing commas, unescaped control chars,
        truncated output) without pulling in a heavy third-party library.

        Raises ``json.JSONDecodeError`` if repair still fails.
        """
        s = raw

        # 1. Remove trailing commas before } or ]  (e.g.  , } → } )
        s = re.sub(r",\s*([}\]])", r"\1", s)

        # 2. Insert missing commas between } { or } " or ] { patterns
        #    e.g.  } { → }, {   or  } "key" → }, "key"
        s = re.sub(r"(\})\s*(\{)", r"\1, \2", s)
        s = re.sub(r"(\})\s*(\")", r"\1, \2", s)
        s = re.sub(r"(\])\s*(\{)", r"\1, \2", s)

        # 3. Fix unescaped newlines / tabs inside string values
        #    Walk through and escape bare control chars within quoted strings.
        #    (Only the simple cases — not a full parser.)
        s = re.sub(r'(?<=": ")(.*?)(?="[,\s}\]])', _escape_ctrl, s, flags=re.DOTALL)

        # 4. If the JSON is truncated (e.g. max-tokens hit), try to close it.
        #    Count unmatched braces/brackets and append closers.
        open_braces = s.count("{") - s.count("}")
        open_brackets = s.count("[") - s.count("]")
        if open_braces > 0 or open_brackets > 0:
            # Strip any trailing partial key/value and comma
            s = re.sub(r",?\s*\"[^\"]*$", "", s)
            s = s.rstrip().rstrip(",")
            # If we still have unmatched braces, try removing the last
            # incomplete object from an array (everything after the last
            # complete }, in the innermost array).
            still_open = s.count("{") - s.count("}")
            if still_open > 0:
                last_complete = s.rfind("},")
                if last_complete != -1:
                    # Keep everything up to and including the last }, then
                    # re-count and close.
                    s = s[: last_complete + 1]
                    s = s.rstrip().rstrip(",")
            open_braces = s.count("{") - s.count("}")
            open_brackets = s.count("[") - s.count("]")
            s += "]" * max(open_brackets, 0)
            s += "}" * max(open_braces, 0)

        return json.loads(s)

    def _parse_llm_response(self, content: str) -> ConceptExtractionResult:
        """Parse LLM JSON response into ConceptExtractionResult.

        Handles both the current ``concepts`` format and the legacy
        ``matched_concepts`` + ``new_concepts`` format (for backward
        compatibility with previously-saved prompts).

        If the raw JSON is malformed (common with DeepSeek-Reasoner on
        long outputs), a lightweight repair pass is attempted before
        giving up.  This fallback does not affect models that already
        produce valid JSON (Claude, Gemini).
        """
        try:
            json_match = re.search(r"\{[\s\S]*\}", content)
            if not json_match:
                logger.warning("No JSON found in LLM response")
                return ConceptExtractionResult(
                    error="No JSON found in LLM response"
                )

            raw_json = json_match.group()

            # First try: strict parse (works for Claude, Gemini, etc.)
            try:
                data = json.loads(raw_json)
            except json.JSONDecodeError as first_err:
                # Second try: repair common LLM mistakes and re-parse
                logger.info(
                    f"Strict JSON parse failed ({first_err}), "
                    "attempting repair…"
                )
                try:
                    data = self._repair_json(raw_json)
                    logger.info("JSON repair succeeded")
                except json.JSONDecodeError:
                    # Repair also failed — raise the original error
                    raise first_err

            # --- New format: flat "concepts" list ---
            raw_concepts = data.get("concepts", [])

            # --- Legacy format: "matched_concepts" + "new_concepts" ---
            if not raw_concepts:
                matched = data.get("matched_concepts", [])
                new = data.get("new_concepts", [])
                if matched or new:
                    logger.info(
                        "Parsing legacy response format "
                        "(matched_concepts + new_concepts)"
                    )
                    raw_concepts = list(matched) + list(new)

            concepts = [
                ExtractedConcept(
                    concept_id=c.get("concept_id", c.get("suggested_id", "")),
                    name=c.get("name", ""),
                    description=c.get("description", ""),
                    category=c.get("category", ""),
                    difficulty=self._safe_int(c.get("difficulty", 3)),
                    confidence=self._safe_float(c.get("confidence", 0.8)),
                    evidence=c.get("evidence", ""),
                    prerequisites=c.get("prerequisites", []),
                    examples=c.get("examples", []),
                )
                for c in raw_concepts
                if c.get("name")
            ]

            summary = data.get("summary", "")

            return ConceptExtractionResult(
                concepts=concepts,
                summary=summary,
            )

        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in LLM response: {e}")
            return ConceptExtractionResult(
                error=f"Invalid JSON in LLM response: {str(e)}"
            )
