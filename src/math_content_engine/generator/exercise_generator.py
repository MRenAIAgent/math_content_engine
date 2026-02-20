"""
LLM-based structured exercise generator for math content.
"""

import json
import logging
import re
import uuid
from dataclasses import dataclass
from typing import List, Optional

from ..integration.schemas import ExerciseDTO, MasteryContextDTO
from ..llm.base import BaseLLMClient
from ..personalization.theme_mapper import theme_to_interest
from ..utils.json_repair import parse_json_with_repair

logger = logging.getLogger(__name__)


@dataclass
class GenerationConfig:
    """Configuration for exercise generation."""
    concept_id: str
    concept_name: str
    concept_description: str
    theme: str
    grade: str
    difficulty: int
    skill_tested: str
    num_exercises: int
    mastery_context: Optional[MasteryContextDTO] = None


# Skill type descriptions for prompt construction
_SKILL_DESCRIPTIONS = {
    "conceptual": "understanding the underlying mathematical concepts and relationships",
    "procedural": "applying step-by-step procedures and algorithms correctly",
    "fluency": "quick and accurate computation with numbers and expressions",
    "transfer": "applying knowledge to new contexts and real-world problems",
}

# Interest-specific scenario templates for personalization
_INTEREST_SCENARIOS = {
    "basketball": [
        "basketball game statistics",
        "scoring points in a basketball match",
        "player shooting percentages",
        "basketball court measurements",
    ],
    "soccer": [
        "soccer match statistics",
        "goals scored in a tournament",
        "player passing accuracy",
        "soccer field dimensions",
    ],
    "gaming": [
        "video game scores and levels",
        "collecting items in a game",
        "game character statistics",
        "building structures in a game",
    ],
    "pokemon": [
        "collecting and trading cards",
        "Pokemon battle statistics",
        "experience points and leveling up",
        "Pokemon type matchups",
    ],
    "animals": [
        "animal populations and habitats",
        "pet care and feeding schedules",
        "wildlife conservation data",
        "animal growth patterns",
    ],
    "space": [
        "distances between planets",
        "spacecraft speeds and travel times",
        "counting stars and constellations",
        "astronaut mission planning",
    ],
    "music": [
        "song lengths and playlists",
        "concert ticket sales",
        "music streaming statistics",
        "rhythm and beat patterns",
    ],
    "robots": [
        "robot movement and programming",
        "coding logic and sequences",
        "electronic component counts",
        "automation efficiency",
    ],
    "cooking": [
        "recipe measurements and scaling",
        "cooking times and temperatures",
        "ingredient quantities",
        "nutrition calculations",
    ],
    "art": [
        "paint color mixing ratios",
        "canvas dimensions and areas",
        "art supply inventory",
        "gallery exhibit planning",
    ],
    "neutral": [
        "everyday situations",
        "shopping and money",
        "time and schedules",
        "measurement tasks",
    ],
}


def _build_system_prompt() -> str:
    """Build the system prompt for exercise generation."""
    return """You are an expert math education specialist who creates engaging,
pedagogically sound math exercises for students.

Your exercises should:
1. Be age-appropriate and aligned with the specified grade level
2. Have clear, unambiguous problem statements
3. Include detailed step-by-step solutions
4. Provide helpful hints that guide without giving away the answer
5. Use the specified theme/interest to make problems relatable and engaging
6. Target the specified skill type (conceptual, procedural, fluency, or transfer)
7. Match the specified difficulty level (1=easy, 5=challenging)

Always respond with valid JSON in the exact format requested."""


def _build_generation_prompt(config: GenerationConfig, interest: str) -> str:
    """Build the generation prompt for creating exercises."""
    skill_description = _SKILL_DESCRIPTIONS.get(
        config.skill_tested, _SKILL_DESCRIPTIONS["procedural"]
    )

    # Get interest-specific scenarios
    scenarios = _INTEREST_SCENARIOS.get(interest, _INTEREST_SCENARIOS["neutral"])
    scenarios_text = ", ".join(scenarios[:3])

    # Build mastery context section if provided
    mastery_section = ""
    if config.mastery_context:
        ctx = config.mastery_context
        mastery_section = f"""
## Student Mastery Context
- Current mastery level: {ctx.overall_mastery * 100:.0f}%
- Recommended focus: {ctx.recommended_dimension}
- Previous attempts: {ctx.attempt_count}
- Common errors to address: {', '.join(ctx.common_errors) if ctx.common_errors else 'None identified'}

Consider this context when designing exercises. If mastery is low, include more scaffolding.
If common errors exist, design exercises that specifically address those misconceptions."""

    prompt = f"""Generate {config.num_exercises} math exercises for the following concept:

## Concept Information
- **Concept ID**: {config.concept_id}
- **Name**: {config.concept_name}
- **Description**: {config.concept_description}

## Exercise Requirements
- **Grade Level**: {config.grade}
- **Difficulty**: {config.difficulty}/5
- **Skill Type**: {config.skill_tested} ({skill_description})
- **Theme**: {config.theme} (interest: {interest})

## Personalization
Use scenarios related to: {scenarios_text}
Make the problems engaging for students interested in {interest}.
{mastery_section}

## Output Format
Return a JSON object with an "exercises" array containing exactly {config.num_exercises} exercises.
Each exercise must have:
- "title": A short, descriptive title (max 60 characters)
- "problem": The complete problem statement
- "solution": Detailed step-by-step solution
- "answer": The final answer (concise, for quick checking)
- "hints": An array of 2-3 progressive hints
- "estimated_time_minutes": Estimated time to complete (integer)
- "keywords": Array of 3-5 relevant keywords

Example JSON structure:
```json
{{
  "exercises": [
    {{
      "title": "Basketball Points Calculation",
      "problem": "In a basketball game, Marcus scored 12 two-point baskets and 5 three-point baskets. How many total points did Marcus score?",
      "solution": "Step 1: Calculate points from two-point baskets: 12 x 2 = 24 points\\nStep 2: Calculate points from three-point baskets: 5 x 3 = 15 points\\nStep 3: Add the totals: 24 + 15 = 39 points",
      "answer": "39 points",
      "hints": [
        "Think about how many points each type of basket is worth",
        "Calculate the points from each type separately first",
        "Two-point baskets: 12 x 2 = ?"
      ],
      "estimated_time_minutes": 3,
      "keywords": ["multiplication", "addition", "sports", "word problem"]
    }}
  ]
}}
```

Generate {config.num_exercises} unique exercises following this exact format.
Ensure variety in problem scenarios while staying within the {interest} theme.
All exercises must target the {config.skill_tested} skill at difficulty level {config.difficulty}."""

    return prompt


def _extract_json_from_response(response: str) -> dict:
    """
    Extract JSON from LLM response, handling markdown code blocks.

    Args:
        response: Raw LLM response text

    Returns:
        Parsed JSON dictionary

    Raises:
        ValueError: If JSON cannot be extracted or parsed
    """
    # Try to find JSON in code blocks first
    json_match = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', response)
    if json_match:
        json_str = json_match.group(1).strip()
    else:
        # Try to find raw JSON object
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            json_str = json_match.group(0)
        else:
            raise ValueError("No JSON found in response")

    try:
        return parse_json_with_repair(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")


def _parse_exercises(
    data: dict,
    config: GenerationConfig,
) -> List[ExerciseDTO]:
    """
    Parse LLM response data into ExerciseDTO objects.

    Args:
        data: Parsed JSON data from LLM
        config: Generation configuration

    Returns:
        List of validated ExerciseDTO objects
    """
    exercises = []
    raw_exercises = data.get("exercises", [])

    for i, raw in enumerate(raw_exercises):
        try:
            exercise = ExerciseDTO(
                exercise_id=f"{config.concept_id}_ex_{uuid.uuid4().hex[:8]}",
                concept_ids=[config.concept_id],
                title=raw.get("title", f"Exercise {i + 1}"),
                problem=raw.get("problem", ""),
                solution=raw.get("solution", ""),
                answer=raw.get("answer"),
                difficulty=config.difficulty,
                hints=raw.get("hints", []),
                theme=config.theme,
                grade=config.grade,
                skill_tested=config.skill_tested,
                estimated_time_minutes=raw.get("estimated_time_minutes"),
                keywords=raw.get("keywords", []),
            )

            # Validate required fields
            if not exercise.problem or not exercise.solution:
                logger.warning(f"Exercise {i + 1} missing required fields, skipping")
                continue

            exercises.append(exercise)

        except Exception as e:
            logger.warning(f"Failed to parse exercise {i + 1}: {e}")
            continue

    return exercises


class ExerciseGenerator:
    """
    Generates structured math exercises using LLM.

    The generator creates pedagogically sound exercises that are:
    - Aligned with specific math concepts
    - Personalized to student interests via themes
    - Targeted to specific skill types and difficulty levels
    - Optionally informed by student mastery context
    """

    def __init__(self, llm_client: BaseLLMClient, max_retries: int = 3):
        """
        Initialize the exercise generator.

        Args:
            llm_client: LLM client for content generation
            max_retries: Maximum retry attempts for failed generations
        """
        self.llm_client = llm_client
        self.max_retries = max_retries
        self.system_prompt = _build_system_prompt()

    def generate(
        self,
        concept_id: str,
        concept_name: str,
        concept_description: str,
        theme: str = "neutral",
        grade: str = "6",
        difficulty: int = 3,
        skill_tested: str = "procedural",
        num_exercises: int = 3,
        mastery_context: Optional[MasteryContextDTO] = None,
    ) -> List[ExerciseDTO]:
        """
        Generate structured exercises for a math concept.

        Args:
            concept_id: Unique identifier for the concept
            concept_name: Human-readable concept name
            concept_description: Description of what the concept covers
            theme: Personalization theme (e.g., "sports_basketball")
            grade: Target grade level (e.g., "6", "7-8", "high school")
            difficulty: Difficulty level from 1 (easy) to 5 (challenging)
            skill_tested: Skill type - conceptual, procedural, fluency, or transfer
            num_exercises: Number of exercises to generate (default 3, max 5)
            mastery_context: Optional mastery context for adaptive generation

        Returns:
            List of ExerciseDTO objects

        Raises:
            RuntimeError: If generation fails after all retries
        """
        # Clamp parameters to valid ranges
        difficulty = max(1, min(5, difficulty))
        num_exercises = max(1, min(5, num_exercises))

        if skill_tested not in _SKILL_DESCRIPTIONS:
            skill_tested = "procedural"

        # Map theme to interest for personalization
        interest = theme_to_interest(theme)

        config = GenerationConfig(
            concept_id=concept_id,
            concept_name=concept_name,
            concept_description=concept_description,
            theme=theme,
            grade=grade,
            difficulty=difficulty,
            skill_tested=skill_tested,
            num_exercises=num_exercises,
            mastery_context=mastery_context,
        )

        logger.info(
            f"Generating {num_exercises} exercises for '{concept_name}' "
            f"(difficulty={difficulty}, skill={skill_tested}, interest={interest})"
        )

        prompt = _build_generation_prompt(config, interest)

        # Initial generation
        attempt = 1
        last_error = None

        while attempt <= self.max_retries:
            try:
                if attempt == 1:
                    response = self.llm_client.generate(prompt, self.system_prompt, json_mode=True)
                else:
                    error_context = self._build_error_context(last_error)
                    response = self.llm_client.generate_with_retry(
                        prompt, self.system_prompt, error_context
                    )

                data = _extract_json_from_response(response.content)
                exercises = _parse_exercises(data, config)

                if not exercises:
                    raise ValueError("No valid exercises parsed from response")

                logger.info(
                    f"Successfully generated {len(exercises)} exercises "
                    f"(attempt {attempt}/{self.max_retries})"
                )
                return exercises

            except Exception as e:
                last_error = str(e)
                logger.warning(
                    f"Generation attempt {attempt}/{self.max_retries} failed: {e}"
                )
                attempt += 1

        error_msg = f"Failed to generate exercises after {self.max_retries} attempts"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    def _build_error_context(self, error: str) -> str:
        """Build error context for retry prompt."""
        return f"""The previous generation attempt failed with the following error:

{error}

Please fix the issue and generate valid exercises in the exact JSON format requested.
Ensure all required fields are present and the JSON is properly formatted."""

    def generate_batch(
        self,
        concepts: List[dict],
        theme: str = "neutral",
        grade: str = "6",
        difficulty: int = 3,
        skill_tested: str = "procedural",
        exercises_per_concept: int = 3,
    ) -> dict:
        """
        Generate exercises for multiple concepts.

        Args:
            concepts: List of concept dicts with 'id', 'name', 'description'
            theme: Personalization theme
            grade: Target grade level
            difficulty: Difficulty level (1-5)
            skill_tested: Skill type to target
            exercises_per_concept: Number of exercises per concept

        Returns:
            Dict mapping concept_id to list of ExerciseDTO objects
        """
        results = {}

        for concept in concepts:
            concept_id = concept.get("id", concept.get("concept_id"))
            concept_name = concept.get("name", concept.get("concept_name"))
            concept_description = concept.get("description", concept.get("concept_description", ""))

            if not concept_id or not concept_name:
                logger.warning(f"Skipping concept with missing id or name: {concept}")
                continue

            try:
                exercises = self.generate(
                    concept_id=concept_id,
                    concept_name=concept_name,
                    concept_description=concept_description,
                    theme=theme,
                    grade=grade,
                    difficulty=difficulty,
                    skill_tested=skill_tested,
                    num_exercises=exercises_per_concept,
                )
                results[concept_id] = exercises

            except Exception as e:
                logger.error(f"Failed to generate exercises for concept '{concept_name}': {e}")
                results[concept_id] = []

        return results
