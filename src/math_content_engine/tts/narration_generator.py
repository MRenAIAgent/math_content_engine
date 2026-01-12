"""
LLM-powered narration script generator.

Generates teacher-quality narration scripts for math animations
using Claude or OpenAI.
"""

import logging
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class NarrationCueGenerated:
    """A generated narration cue with timing."""
    text: str
    time: float
    duration_estimate: float  # Estimated speaking duration


@dataclass
class GeneratedNarrationScript:
    """Complete generated narration script."""
    title: str
    cues: List[NarrationCueGenerated]
    total_duration: float
    audience_level: str


NARRATION_SYSTEM_PROMPT = """You are an excellent, experienced math teacher who explains concepts clearly and engagingly.

Your teaching style:
- Warm, encouraging, and patient tone
- Use simple, clear language appropriate for the audience level
- Break down complex ideas into digestible steps
- Use phrases like "Let's", "Notice that", "Remember", "Great!"
- Pause naturally between ideas (reflected in separate cues)
- Celebrate small wins and discoveries
- Connect abstract concepts to visual elements

Speaking guidelines:
- Write exactly how you would SPEAK, not write
- Use contractions naturally (let's, we'll, that's, it's)
- Avoid jargon unless explaining it
- Numbers: write "2" as "two" for single digits, use digits for larger numbers
- Math symbols: write out as spoken ("plus", "minus", "equals", "times", "divided by")
- Fractions: "one half", "two thirds", "three fourths"
- Variables: just say the letter ("x", "y")
- Exponents: "x squared", "x cubed", "x to the fourth power"

CRITICAL TIMING RULES:
- Each cue should be 8-15 words (about 3-6 seconds of speech)
- Leave at least 5-7 seconds between cue start times
- Speaking rate is approximately 2.5 words per second
- Total script should match the animation duration

Output format: Return a JSON array of narration cues with timing."""


def build_narration_prompt(
    topic: str,
    animation_description: str,
    animation_duration: float,
    audience_level: str = "middle school",
    visual_cues: Optional[List[str]] = None
) -> str:
    """Build the prompt for generating narration."""

    visual_cues_text = ""
    if visual_cues:
        visual_cues_text = "\n\nVisual elements in the animation (with approximate timing):\n"
        for cue in visual_cues:
            visual_cues_text += f"- {cue}\n"

    return f"""Generate a narration script for a math animation video.

TOPIC: {topic}

AUDIENCE: {audience_level} students

ANIMATION DESCRIPTION:
{animation_description}

ANIMATION DURATION: {animation_duration} seconds
{visual_cues_text}

Generate narration cues that:
1. Explain the concept clearly as an excellent teacher would
2. Sync with the visual elements shown in the animation
3. Are appropriately paced (8-15 words per cue, 5-7 seconds apart)
4. Use encouraging, clear language suitable for {audience_level} students
5. Total narration fits within {animation_duration} seconds

Return ONLY a JSON array in this exact format:
[
  {{"text": "Welcome! Today we're going to learn something exciting.", "time": 0.0}},
  {{"text": "Let's start by looking at our equation.", "time": 6.0}},
  ...
]

Remember:
- Write as SPOKEN words, not written text
- "2x + 3 = 7" should be "two x plus three equals seven"
- Be warm, encouraging, and clear
- Each cue should be a complete thought
- Time values are in seconds from video start"""


class NarrationScriptGenerator:
    """
    Generates teacher-quality narration scripts using LLM.

    Example:
        >>> from math_content_engine import MathContentEngine
        >>> from math_content_engine.tts import NarrationScriptGenerator
        >>>
        >>> engine = MathContentEngine()
        >>> generator = NarrationScriptGenerator(engine.llm_client)
        >>>
        >>> script = generator.generate(
        ...     topic="Solving 2x + 3 = 7",
        ...     animation_description="Shows step-by-step algebraic solution",
        ...     animation_duration=30.0,
        ...     audience_level="middle school"
        ... )
    """

    def __init__(self, llm_client):
        """
        Initialize the narration generator.

        Args:
            llm_client: LLM client (Claude or OpenAI) from MathContentEngine
        """
        self.llm_client = llm_client

    def generate(
        self,
        topic: str,
        animation_description: str,
        animation_duration: float,
        audience_level: str = "middle school",
        visual_cues: Optional[List[str]] = None
    ) -> GeneratedNarrationScript:
        """
        Generate a narration script for an animation.

        Args:
            topic: Math topic being taught
            animation_description: Description of what the animation shows
            animation_duration: Total animation length in seconds
            audience_level: Target audience (elementary, middle school, high school, college)
            visual_cues: Optional list of visual elements with timing hints

        Returns:
            GeneratedNarrationScript with cues and timing
        """
        prompt = build_narration_prompt(
            topic=topic,
            animation_description=animation_description,
            animation_duration=animation_duration,
            audience_level=audience_level,
            visual_cues=visual_cues
        )

        logger.info(f"Generating narration for: {topic}")

        response = self.llm_client.generate(prompt, NARRATION_SYSTEM_PROMPT)

        # Parse the JSON response
        cues = self._parse_response(response.content)

        # Calculate durations
        for i, cue in enumerate(cues):
            word_count = len(cue.text.split())
            cue.duration_estimate = word_count / 2.5  # ~2.5 words per second

        total_duration = max(
            cue.time + cue.duration_estimate for cue in cues
        ) if cues else 0.0

        return GeneratedNarrationScript(
            title=topic,
            cues=cues,
            total_duration=total_duration,
            audience_level=audience_level
        )

    def _parse_response(self, content: str) -> List[NarrationCueGenerated]:
        """Parse LLM response into narration cues."""
        import json
        import re

        # Try to extract JSON from response
        # Look for JSON array pattern
        json_match = re.search(r'\[[\s\S]*\]', content)
        if not json_match:
            logger.error(f"Could not find JSON in response: {content[:200]}")
            return []

        try:
            data = json.loads(json_match.group())
            cues = []
            for item in data:
                cues.append(NarrationCueGenerated(
                    text=item.get("text", ""),
                    time=float(item.get("time", 0)),
                    duration_estimate=0.0  # Will be calculated
                ))
            return cues
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return []

    def generate_for_equation(
        self,
        equation: str,
        solution_steps: List[str],
        animation_duration: float,
        audience_level: str = "middle school"
    ) -> GeneratedNarrationScript:
        """
        Generate narration specifically for equation-solving animations.

        Args:
            equation: The equation being solved (e.g., "2x + 3 = 7")
            solution_steps: List of solution steps shown in animation
            animation_duration: Total animation length
            audience_level: Target audience

        Returns:
            GeneratedNarrationScript
        """
        # Build visual cues from steps
        visual_cues = []
        step_duration = animation_duration / (len(solution_steps) + 2)  # +2 for intro/outro

        for i, step in enumerate(solution_steps):
            time = (i + 1) * step_duration
            visual_cues.append(f"[{time:.0f}s] {step}")

        animation_description = f"""
This animation teaches how to solve the equation {equation}.

The animation shows:
1. Introduction with the equation displayed
2. Step-by-step solution process:
{chr(10).join(f'   - {step}' for step in solution_steps)}
3. Final answer highlighted with verification
"""

        return self.generate(
            topic=f"Solving {equation}",
            animation_description=animation_description,
            animation_duration=animation_duration,
            audience_level=audience_level,
            visual_cues=visual_cues
        )

    def generate_for_concept(
        self,
        concept: str,
        key_points: List[str],
        animation_duration: float,
        audience_level: str = "middle school"
    ) -> GeneratedNarrationScript:
        """
        Generate narration for concept explanation animations.

        Args:
            concept: Math concept being explained
            key_points: Key points covered in the animation
            animation_duration: Total animation length
            audience_level: Target audience

        Returns:
            GeneratedNarrationScript
        """
        animation_description = f"""
This animation explains the concept of {concept}.

Key points covered:
{chr(10).join(f'- {point}' for point in key_points)}

The animation uses visual representations to help students understand.
"""

        return self.generate(
            topic=concept,
            animation_description=animation_description,
            animation_duration=animation_duration,
            audience_level=audience_level
        )


def convert_script_to_animation_script(
    generated: GeneratedNarrationScript
) -> "AnimationScript":
    """
    Convert a GeneratedNarrationScript to AnimationScript for use with
    NarratedAnimationGenerator.

    Args:
        generated: The LLM-generated script

    Returns:
        AnimationScript compatible with NarratedAnimationGenerator
    """
    from .narrated_animation import AnimationScript

    script = AnimationScript(title=generated.title)

    for cue in generated.cues:
        script.add_cue(text=cue.text, time=cue.time)

    return script
