"""Prompt introspection — builds the exact prompts each pipeline stage would send.

This module reconstructs prompts *without* calling the LLM so that the UI
can display and let the user edit them before execution.

It does NOT import from ``scripts/`` — the personalization prompt template
is replicated here using the same library functions that the script uses.
"""

import logging
from typing import Optional

from ...config import Config
from ...generator.prompts import build_generation_prompt, get_system_prompt
from ...knowledge_graph.concept_extractor import (
    CONCEPT_EXTRACTOR_SYSTEM_PROMPT,
    MAX_CONTENT_CHARS,
    ConceptExtractor,
)
from ...llm.base import BaseLLMClient, LLMResponse
from ...personalization import ContentPersonalizer, get_interest_profile
from .models import PromptPreview

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Personalization prompt (mirrors scripts/generate_personalized_textbook.py)
# ---------------------------------------------------------------------------

_PERSONALIZATION_SYSTEM_PROMPT = (
    "You are an expert educational content creator "
    "specializing in personalized math textbooks."
)


def _build_personalization_user_prompt(
    textbook_content: str,
    interest_name: str,
) -> str:
    """Replicate the personalization prompt from
    ``scripts/generate_personalized_textbook.py::create_personalization_prompt``.

    Uses the same ``InterestProfile`` data — just avoids importing from
    ``scripts/``.
    """
    profile = get_interest_profile(interest_name)
    if not profile:
        return f"[ERROR: Unknown interest '{interest_name}']"

    fun_facts = "\n".join(f"- {fact}" for fact in profile.fun_facts[:5])
    cultural_refs = "\n".join(
        f"- {ref}" for ref in getattr(profile, "cultural_references", [])[:4]
    )
    historical = "\n".join(
        f"- {fact}" for fact in getattr(profile, "historical_trivia", [])[:3]
    )
    quotes = "\n".join(
        f'- "{quote}"' for quote in getattr(profile, "motivational_quotes", [])[:2]
    )
    scenarios = "\n".join(f"- {s}" for s in profile.example_scenarios[:6])
    figures = ", ".join(profile.famous_figures[:8])

    return f"""You are an expert math textbook author who specializes in creating engaging,
personalized educational content. Your task is to transform a generic math textbook chapter
into a personalized version themed around {profile.display_name}.

## PERSONALIZATION GUIDELINES

### About {profile.display_name}
{profile.context_intro}

### Basic Knowledge (use this to ensure accuracy)
{profile.basic_knowledge if profile.basic_knowledge else "Use common knowledge about " + profile.name}

### Famous Figures to Reference
{figures}

### Example Scenarios for Word Problems (adapt math problems to these themes)
{scenarios}

### Fun Facts to Sprinkle Throughout (pick 2-3 to include)
{fun_facts}

### Cultural References & Iconic Moments (use sparingly for engagement)
{cultural_refs if cultural_refs else "Use current pop culture references related to " + profile.name}

### Historical Context (for depth and interest)
{historical if historical else "Include relevant historical facts about " + profile.name}

### Motivational Quotes (use for chapter intro or conclusion)
{quotes if quotes else "Use inspiring quotes from notable figures in " + profile.name}

### Visual Theme
- Colors: {profile.visual_themes.get('primary_colors', 'Use thematic colors')}
- Imagery: {profile.visual_themes.get('imagery', 'Use relevant imagery')}

## TRANSFORMATION RULES

1. **Keep ALL Math Content Intact**: Every equation, formula, property, and mathematical concept
   must remain exactly the same. Only change the CONTEXT and EXAMPLES around the math.

2. **Replace Generic Examples**: Transform word problems to use {profile.name} scenarios.
   - Original: "If x + 5 = 12, find x"
   - Personalized: "If Curry has scored x three-pointers plus 5 free throws for 12 total points, find x"

3. **Use Domain Terminology**: Replace generic terms with {profile.name}-specific language.
   - "number" -> "score", "points", "stats" (for sports)
   - "unknown" -> "mystery damage", "hidden XP" (for gaming)

4. **Add Engaging Elements**:
   - Include 2-3 fun facts as "Did You Know?" boxes
   - Reference famous {profile.name} figures in examples
   - Add a motivational quote at the start or end
   - Include cultural references students will recognize

5. **Maintain Educational Quality**:
   - Keep learning objectives clear
   - Preserve step-by-step solution methods
   - Include practice problems with the same difficulty
   - Add real-world {profile.name} applications

6. **Format the Output**:
   - Use markdown formatting
   - Add an appropriate emoji to the title
   - Include themed section headers
   - Mark fun facts and special content clearly

## ORIGINAL TEXTBOOK CONTENT TO TRANSFORM

```markdown
{textbook_content}
```

## YOUR TASK

Transform the above textbook content into a {profile.display_name}-themed version.
Keep all mathematical content identical but change all examples, contexts, and
word problems to use {profile.name} themes.

Output ONLY the transformed markdown content - no explanations or commentary.
Start with the chapter title.
"""


# ---------------------------------------------------------------------------
# Public preview functions
# ---------------------------------------------------------------------------


def preview_personalization_prompts(
    textbook_content: str,
    interest: str,
) -> PromptPreview:
    """Build the personalization prompts without executing them."""
    return PromptPreview(
        stage="personalize",
        system_prompt=_PERSONALIZATION_SYSTEM_PROMPT,
        user_prompt=_build_personalization_user_prompt(textbook_content, interest),
    )


def preview_concept_extraction_prompts(
    markdown_content: str,
    config: Optional[Config] = None,
) -> PromptPreview:
    """Build concept extraction prompts without executing them.

    Instantiates a lightweight ``ConceptExtractor`` to populate the concept
    list portion of the system prompt.
    """
    # We need a minimal LLM client just to construct the extractor (it never
    # calls generate). Use a stub so we don't need real API keys for preview.
    stub_client = _StubLLMClient()
    extractor = ConceptExtractor(llm_client=stub_client)

    concept_list = extractor._build_concept_list_prompt()
    system_prompt = CONCEPT_EXTRACTOR_SYSTEM_PROMPT.format(concept_list=concept_list)

    truncated = markdown_content[:MAX_CONTENT_CHARS]
    if len(markdown_content) > MAX_CONTENT_CHARS:
        truncated += "\n\n[Content truncated for analysis]"

    user_prompt = (
        "Analyze this math textbook content and identify concepts:\n\n"
        f"{truncated}"
    )

    return PromptPreview(
        stage="extract_concepts",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )


def preview_animation_prompts(
    topic: str,
    requirements: str = "",
    audience_level: str = "high school",
    interest: Optional[str] = None,
    animation_style: str = "dark",
    student_name: Optional[str] = None,
) -> PromptPreview:
    """Build animation generation prompts without executing them.

    Uses the same ``get_animation_personalization()`` path as the main
    engine so the playground preview matches actual generation.
    """
    from ...constants import AnimationStyle
    from ...personalization import StudentProfile

    style = AnimationStyle(animation_style) if animation_style else AnimationStyle.DARK
    system_prompt = get_system_prompt(style)

    # Build student profile if name provided
    student = StudentProfile(name=student_name) if student_name else None

    # Use the same personalization path as the main engine
    personalization_context = ""
    if interest:
        personalizer = ContentPersonalizer(interest)
        if personalizer.profile:
            personalization_context = personalizer.get_animation_personalization(
                topic, student=student
            )

    user_prompt = build_generation_prompt(
        topic=topic,
        requirements=requirements,
        audience_level=audience_level,
        personalization_context=personalization_context,
        student_name=student_name,
    )

    return PromptPreview(
        stage="generate_animation",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


class _StubLLMClient(BaseLLMClient):
    """Minimal LLM client stub — used only to construct a ConceptExtractor
    for prompt preview (no API call is ever made)."""

    def __init__(self) -> None:
        # Skip the parent __init__ validation (it checks for API keys)
        self.api_key = "stub"
        self.model = "stub"
        self.temperature = 0.0
        self.max_tokens = 0

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> LLMResponse:  # type: ignore[override]
        raise RuntimeError("StubLLMClient.generate() should never be called")

    def generate_with_retry(self, prompt: str, system_prompt: Optional[str] = None, error_context: Optional[str] = None) -> LLMResponse:
        raise RuntimeError("StubLLMClient.generate_with_retry() should never be called")
