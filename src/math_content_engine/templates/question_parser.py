"""
Question parser agent that uses LLM to extract template parameters from math questions.
"""

import json
import re
from typing import Optional

from ..llm.base import BaseLLMClient
from ..llm.factory import create_llm_client
from .base import ManimTemplate, ParseResult
from .registry import TemplateRegistry, get_registry


PARSER_SYSTEM_PROMPT = """You are a math question parser. Your job is to analyze math questions and extract structured parameters for animation templates.

Given a math question, you must:
1. Identify which template type best matches the question
2. Extract all numerical values and parameters
3. Return a JSON response with the template_id and parameters

## Available Templates:
{template_descriptions}

## Response Format:
Always respond with valid JSON only, no other text:
{{
    "template_id": "the_template_id",
    "parameters": {{
        "param1": value1,
        "param2": value2
    }},
    "confidence": 0.95,
    "reasoning": "brief explanation"
}}

## Parameter Extraction Rules:
1. For linear equations like "ax + b = c":
   - Extract a (coefficient of x), b (constant term), c (right side)
   - Handle negative signs: "3x - 5 = 10" means a=3, b=-5, c=10

2. For slope problems:
   - Extract point coordinates (x1, y1) and (x2, y2)
   - Handle formats like "(1, 2) and (4, 8)" or "from (1,2) to (4,8)"

3. For slope-intercept form (y = mx + b):
   - Extract m (slope) and b (y-intercept)
   - Handle "y = 2x - 3" as m=2, b=-3

4. For systems of equations:
   - Extract m1, b1 from first equation
   - Extract m2, b2 from second equation

5. For quadratics (ax² + bx + c = 0):
   - Extract a (coefficient of x²), b (coefficient of x), c (constant)

6. For inequalities:
   - Extract boundary value and operator (>, <, >=, <=)
   - Handle symbols: ≥ maps to ">=", ≤ maps to "<="

## Examples:

Question: "Solve 3x + 5 = 14"
Response:
{{
    "template_id": "linear_equation_graph",
    "parameters": {{"a": 3, "b": 5, "c": 14}},
    "confidence": 0.95,
    "reasoning": "Standard two-step linear equation"
}}

Question: "Find the slope between (1, 2) and (4, 8)"
Response:
{{
    "template_id": "slope_visualization",
    "parameters": {{"x1": 1, "y1": 2, "x2": 4, "y2": 8}},
    "confidence": 0.98,
    "reasoning": "Slope calculation between two points"
}}

Question: "Graph x > 5"
Response:
{{
    "template_id": "inequality_numberline",
    "parameters": {{"boundary": 5, "operator": ">"}},
    "confidence": 0.95,
    "reasoning": "Simple inequality on number line"
}}
"""


class QuestionParserAgent:
    """
    Agent that parses math questions and extracts template parameters using LLM.
    """

    def __init__(
        self,
        llm_client: Optional[BaseLLMClient] = None,
        registry: Optional[TemplateRegistry] = None,
    ):
        """
        Initialize the question parser.

        Args:
            llm_client: LLM client to use for parsing (creates default if None)
            registry: Template registry (uses global registry if None)
        """
        self.llm_client = llm_client or create_llm_client()
        self.registry = registry or get_registry()

    def parse(self, question: str) -> ParseResult:
        """
        Parse a math question and extract template parameters.

        Args:
            question: The math question to parse

        Returns:
            ParseResult with template_id and parameters
        """
        # Build system prompt with template descriptions
        template_descriptions = self.registry.get_template_descriptions()
        system_prompt = PARSER_SYSTEM_PROMPT.format(
            template_descriptions=template_descriptions
        )

        # Call LLM
        user_prompt = f"Parse this math question and extract parameters:\n\n{question}"

        try:
            response = self.llm_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
            )

            # Parse JSON response
            result = self._parse_llm_response(response.content)

            if result.success:
                # Apply derived parameter computation
                result = self._compute_derived_params(result)

            return result

        except Exception as e:
            return ParseResult(
                success=False,
                error_message=f"Failed to parse question: {str(e)}",
            )

    def _parse_llm_response(self, content: str) -> ParseResult:
        """Parse the LLM response JSON."""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{[\s\S]*\}', content)
            if not json_match:
                return ParseResult(
                    success=False,
                    error_message="No JSON found in LLM response",
                )

            data = json.loads(json_match.group())

            template_id = data.get("template_id")
            if not template_id:
                return ParseResult(
                    success=False,
                    error_message="No template_id in response",
                )

            # Verify template exists
            if template_id not in self.registry:
                return ParseResult(
                    success=False,
                    error_message=f"Unknown template: {template_id}",
                    alternative_templates=self._find_similar_templates(template_id),
                )

            return ParseResult(
                success=True,
                template_id=template_id,
                parameters=data.get("parameters", {}),
                confidence=data.get("confidence", 0.5),
            )

        except json.JSONDecodeError as e:
            return ParseResult(
                success=False,
                error_message=f"Invalid JSON in response: {str(e)}",
            )

    def _compute_derived_params(self, result: ParseResult) -> ParseResult:
        """Compute derived parameters using template's compute function."""
        template = self.registry.get(result.template_id)
        if template and template.compute_derived:
            derived = template.compute_derived(result.parameters)
            result.parameters.update(derived)
        return result

    def _find_similar_templates(self, template_id: str) -> list[str]:
        """Find similar template IDs for suggestions."""
        all_ids = self.registry.list_ids()
        # Simple similarity: check for common words
        words = template_id.lower().replace("_", " ").split()
        similar = []
        for tid in all_ids:
            tid_words = tid.lower().replace("_", " ").split()
            if any(w in tid_words for w in words):
                similar.append(tid)
        return similar[:3]

    def parse_batch(self, questions: list[str]) -> list[ParseResult]:
        """Parse multiple questions."""
        return [self.parse(q) for q in questions]


class SimpleQuestionParser:
    """
    Regex-based parser for common question patterns.
    Use this when you don't want LLM overhead for simple questions.
    """

    # Patterns for different question types
    PATTERNS = {
        "linear_equation": [
            # "Solve 3x + 5 = 14" or "3x + 5 = 14"
            r"(?:solve\s+)?(-?\d*\.?\d*)x\s*([+-])\s*(\d+\.?\d*)\s*=\s*(-?\d+\.?\d*)",
            # "Solve 2x - 3 = 7"
            r"(?:solve\s+)?(-?\d*\.?\d*)x\s*([+-])\s*(\d+\.?\d*)\s*=\s*(-?\d+\.?\d*)",
        ],
        "slope_points": [
            # "(1, 2) and (4, 8)" or "from (1,2) to (4,8)"
            r"\((-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\).*\((-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\)",
        ],
        "slope_intercept": [
            # "y = 2x + 3" or "y = -x - 5"
            r"y\s*=\s*(-?\d*\.?\d*)x\s*([+-])\s*(\d+\.?\d*)",
        ],
        "inequality": [
            # "x > 5" or "x <= 3"
            r"x\s*([<>]=?|[≤≥])\s*(-?\d+\.?\d*)",
        ],
        "quadratic": [
            # "x² - 5x + 6 = 0" or "2x² + 3x - 5 = 0"
            r"(-?\d*\.?\d*)x[²2]\s*([+-])\s*(\d*\.?\d*)x\s*([+-])\s*(\d+\.?\d*)\s*=\s*0",
        ],
    }

    def parse(self, question: str, registry: Optional[TemplateRegistry] = None) -> ParseResult:
        """
        Parse a question using regex patterns.

        Args:
            question: The math question
            registry: Template registry for derived param computation

        Returns:
            ParseResult or None if no pattern matches
        """
        question_lower = question.lower().strip()
        registry = registry or get_registry()

        # Try linear equation patterns
        for pattern in self.PATTERNS["linear_equation"]:
            match = re.search(pattern, question_lower, re.IGNORECASE)
            if match:
                a = float(match.group(1)) if match.group(1) else 1
                sign = match.group(2)
                b = float(match.group(3))
                if sign == "-":
                    b = -b
                c = float(match.group(4))

                params = {"a": a, "b": b, "c": c}

                # Compute derived params
                template = registry.get("linear_equation_graph")
                if template and template.compute_derived:
                    params.update(template.compute_derived(params))

                return ParseResult(
                    success=True,
                    template_id="linear_equation_graph",
                    parameters=params,
                    confidence=0.9,
                )

        # Try slope between points
        for pattern in self.PATTERNS["slope_points"]:
            match = re.search(pattern, question)
            if match:
                params = {
                    "x1": float(match.group(1)),
                    "y1": float(match.group(2)),
                    "x2": float(match.group(3)),
                    "y2": float(match.group(4)),
                }

                template = registry.get("slope_visualization")
                if template and template.compute_derived:
                    params.update(template.compute_derived(params))

                return ParseResult(
                    success=True,
                    template_id="slope_visualization",
                    parameters=params,
                    confidence=0.95,
                )

        # Try slope-intercept form
        for pattern in self.PATTERNS["slope_intercept"]:
            match = re.search(pattern, question_lower)
            if match:
                m = float(match.group(1)) if match.group(1) and match.group(1) != "-" else (
                    -1 if match.group(1) == "-" else 1
                )
                sign = match.group(2)
                b = float(match.group(3))
                if sign == "-":
                    b = -b

                params = {"m": m, "b": b}

                template = registry.get("slope_intercept_form")
                if template and template.compute_derived:
                    params.update(template.compute_derived(params))

                return ParseResult(
                    success=True,
                    template_id="slope_intercept_form",
                    parameters=params,
                    confidence=0.9,
                )

        # Try inequality
        for pattern in self.PATTERNS["inequality"]:
            match = re.search(pattern, question)
            if match:
                operator = match.group(1)
                # Normalize operator
                if operator == "≥":
                    operator = ">="
                elif operator == "≤":
                    operator = "<="

                params = {
                    "boundary": float(match.group(2)),
                    "operator": operator,
                }

                template = registry.get("inequality_numberline")
                if template and template.compute_derived:
                    params.update(template.compute_derived(params))

                return ParseResult(
                    success=True,
                    template_id="inequality_numberline",
                    parameters=params,
                    confidence=0.9,
                )

        # No pattern matched
        return ParseResult(
            success=False,
            error_message="No matching pattern found. Use LLM parser for complex questions.",
        )
