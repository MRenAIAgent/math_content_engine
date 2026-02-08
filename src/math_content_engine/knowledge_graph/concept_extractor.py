"""
LLM-based concept extraction from markdown content.

Uses the knowledge graph to match existing concepts and identify
new concepts found in textbook/markdown content.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from ..llm.base import BaseLLMClient
from .algebra import (
    build_concept_index,
    get_default_algebra_knowledge_graph_path,
    load_algebra_knowledge_graph,
)

logger = logging.getLogger(__name__)

MAX_CONTENT_CHARS = 15000

CONCEPT_EXTRACTOR_SYSTEM_PROMPT = """You are a math curriculum analyst. Your job is to analyze \
math textbook content and identify which mathematical concepts are covered.

You will be given:
1. A list of known concepts from our knowledge graph
2. Textbook/markdown content to analyze

## Known Concepts:
{concept_list}

## Your Task:
1. Identify which known concepts appear in the content (matched_concepts)
2. Identify any new math concepts NOT in our list (new_concepts)
3. Write a brief summary of the mathematical topics covered

## Response Format:
Return ONLY valid JSON, no other text:
{{
    "matched_concepts": [
        {{
            "concept_id": "AT-24",
            "name": "Two-Step Linear Equations",
            "confidence": 0.95,
            "evidence": "short quote or description showing where this concept appears"
        }}
    ],
    "new_concepts": [
        {{
            "suggested_id": "LF-41",
            "name": "Concept Name",
            "description": "What this concept teaches",
            "category": "Linear",
            "difficulty": 3,
            "prerequisites": ["AT-24"],
            "examples": ["Example problem 1"]
        }}
    ],
    "summary": "Brief description of the math topics covered in this content"
}}

## Rules:
- Only match concepts you are confident appear in the content (confidence >= 0.7)
- For new concepts, use ID prefixes: NS- (Number Sense), AT- (Pre-Algebra), \
LF- (Linear), Q- (Quadratic), EXP- (Exponential), POL- (Polynomials), FN- (Function Tools)
- Difficulty scale: 1 (basic) to 5 (advanced)
- Prerequisites should reference existing concept IDs when possible
- Keep evidence snippets under 100 characters
"""


@dataclass
class MatchedConcept:
    """A concept from the knowledge graph matched to content."""

    concept_id: str
    name: str
    confidence: float
    evidence: str


@dataclass
class NewConcept:
    """A concept found in content that doesn't exist in the knowledge graph."""

    suggested_id: str
    name: str
    description: str
    category: str
    difficulty: int
    prerequisites: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)


@dataclass
class ConceptExtractionResult:
    """Result of concept extraction from markdown content."""

    matched_concepts: List[MatchedConcept] = field(default_factory=list)
    new_concepts: List[NewConcept] = field(default_factory=list)
    summary: str = ""
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Serialize to JSON-safe dictionary."""
        return {
            "matched_concepts": [
                {
                    "concept_id": c.concept_id,
                    "name": c.name,
                    "confidence": c.confidence,
                    "evidence": c.evidence,
                }
                for c in self.matched_concepts
            ],
            "new_concepts": [
                {
                    "suggested_id": c.suggested_id,
                    "name": c.name,
                    "description": c.description,
                    "category": c.category,
                    "difficulty": c.difficulty,
                    "prerequisites": c.prerequisites,
                    "examples": c.examples,
                }
                for c in self.new_concepts
            ],
            "summary": self.summary,
            "error": self.error,
        }

    def display(self) -> str:
        """Format for console output."""
        lines = []
        lines.append(f"Summary: {self.summary}")
        lines.append("")

        if self.matched_concepts:
            lines.append(f"Matched Concepts ({len(self.matched_concepts)}):")
            for c in self.matched_concepts:
                lines.append(
                    f"  [{c.concept_id}] {c.name} "
                    f"(confidence: {c.confidence:.0%})"
                )
                lines.append(f"    Evidence: {c.evidence}")
        else:
            lines.append("Matched Concepts: (none)")

        lines.append("")

        if self.new_concepts:
            lines.append(f"New Concepts ({len(self.new_concepts)}):")
            for c in self.new_concepts:
                lines.append(
                    f"  [{c.suggested_id}] {c.name} "
                    f"({c.category}, difficulty {c.difficulty})"
                )
                lines.append(f"    {c.description}")
                if c.prerequisites:
                    lines.append(f"    Prerequisites: {', '.join(c.prerequisites)}")
        else:
            lines.append("New Concepts: (none)")

        if self.error:
            lines.append(f"\nError: {self.error}")

        return "\n".join(lines)


class ConceptExtractor:
    """
    Extracts mathematical concepts from markdown content using LLM.

    Loads the knowledge graph in-memory and uses LLM to identify which
    concepts appear in the given content. Results are returned in-memory
    (no file writes).
    """

    def __init__(
        self,
        llm_client: BaseLLMClient,
        graph: Optional[Dict] = None,
        graph_path: Optional[Path] = None,
    ):
        """
        Args:
            llm_client: LLM client for concept extraction
            graph: Pre-loaded knowledge graph dict (optional)
            graph_path: Path to knowledge graph JSON (optional, auto-detects)
        """
        self.llm_client = llm_client
        self.graph = graph or load_algebra_knowledge_graph(graph_path)
        self.concept_index = build_concept_index(self.graph)
        logger.info(
            f"ConceptExtractor loaded with {len(self.concept_index)} concepts"
        )

    def extract_concepts(
        self,
        markdown_content: str,
        confidence_threshold: float = 0.7,
    ) -> ConceptExtractionResult:
        """
        Extract math concepts from markdown content.

        Args:
            markdown_content: Textbook/markdown content to analyze
            confidence_threshold: Minimum confidence to include a match

        Returns:
            ConceptExtractionResult with matched and new concepts
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

        concept_list = self._build_concept_list_prompt()
        system_prompt = CONCEPT_EXTRACTOR_SYSTEM_PROMPT.format(
            concept_list=concept_list
        )

        user_prompt = (
            "Analyze this math textbook content and identify concepts:\n\n"
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
        result.matched_concepts = [
            c
            for c in result.matched_concepts
            if c.confidence >= confidence_threshold
        ]

        # Validate matched concept IDs exist in graph
        validated = []
        for concept in result.matched_concepts:
            if concept.concept_id in self.concept_index:
                validated.append(concept)
            else:
                logger.warning(
                    f"LLM returned unknown concept_id: {concept.concept_id}"
                )
        result.matched_concepts = validated

        logger.info(
            f"Extracted {len(result.matched_concepts)} matched, "
            f"{len(result.new_concepts)} new concepts"
        )
        return result

    def _build_concept_list_prompt(self) -> str:
        """Format existing concepts compactly for the system prompt."""
        lines = []
        for concept_id, concept in sorted(self.concept_index.items()):
            name = concept.get("name", "")
            category = concept.get("category", "")
            desc = concept.get("description", "")
            lines.append(f"- {concept_id}: {name} ({category}) - {desc}")
        return "\n".join(lines)

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

    def _parse_llm_response(self, content: str) -> ConceptExtractionResult:
        """Parse LLM JSON response into ConceptExtractionResult."""
        try:
            json_match = re.search(r"\{[\s\S]*\}", content)
            if not json_match:
                logger.warning("No JSON found in LLM response")
                return ConceptExtractionResult(
                    error="No JSON found in LLM response"
                )

            data = json.loads(json_match.group())

            matched = [
                MatchedConcept(
                    concept_id=m.get("concept_id", ""),
                    name=m.get("name", ""),
                    confidence=self._safe_float(m.get("confidence", 0)),
                    evidence=m.get("evidence", ""),
                )
                for m in data.get("matched_concepts", [])
                if m.get("concept_id")
            ]

            new = [
                NewConcept(
                    suggested_id=n.get("suggested_id", ""),
                    name=n.get("name", ""),
                    description=n.get("description", ""),
                    category=n.get("category", ""),
                    difficulty=self._safe_int(n.get("difficulty", 3)),
                    prerequisites=n.get("prerequisites", []),
                    examples=n.get("examples", []),
                )
                for n in data.get("new_concepts", [])
                if n.get("name")
            ]

            summary = data.get("summary", "")

            return ConceptExtractionResult(
                matched_concepts=matched,
                new_concepts=new,
                summary=summary,
            )

        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in LLM response: {e}")
            return ConceptExtractionResult(
                error=f"Invalid JSON in LLM response: {str(e)}"
            )
