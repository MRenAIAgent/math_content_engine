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
)
from ...llm.base import BaseLLMClient
from ...personalization import ContentPersonalizer, get_interest_profile
from .models import PromptPreview

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Personalization prompt (mirrors scripts/generate_personalized_textbook.py)
# ---------------------------------------------------------------------------

_PERSONALIZATION_SYSTEM_PROMPT = (
    "You are an expert educational content creator who specializes in making math "
    "textbooks irresistibly engaging for middle school and high school students. "
    "You have deep domain expertise in every interest topic you personalize for — "
    "you know the rules, the culture, the lingo, and the real-world numbers. "
    "You never make up facts or use unrealistic numbers. Every example you create "
    "could actually happen in real life."
)


def _build_personalization_user_prompt(
    textbook_content: str,
    interest_name: str,
) -> str:
    """Build the personalization prompt using InterestProfile data.

    The prompt is designed to produce output that:
    - Uses realistic, factually accurate examples grounded in the topic
    - Speaks directly to middle/high schoolers in 2nd person ("you")
    - Follows the real-world rules and common sense of the topic
    - Keeps all math content intact while making the context engaging
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

    # Build verified stats section
    verified_stats_str = ""
    if getattr(profile, "verified_stats", None):
        stats_lines = "\n".join(
            f"- {k}: {v}" for k, v in list(profile.verified_stats.items())[:8]
        )
        verified_stats_str = f"""
### Verified Real-World Data (use these exact numbers, never make up stats)
{stats_lines}
"""

    # Build second-person scenarios section
    second_person_str = ""
    if getattr(profile, "second_person_scenarios", None):
        sp_lines = "\n".join(
            f"- {s}" for s in profile.second_person_scenarios[:4]
        )
        second_person_str = f"""
### Example Problems Written in 2nd Person (model your word problems after these)
{sp_lines}
"""

    # Build trending section
    trending_str = ""
    if getattr(profile, "trending_now", None):
        tr_lines = "\n".join(f"- {t}" for t in profile.trending_now[:3])
        trending_str = f"""
### Current/Trending References ({getattr(profile, 'current_season', 'current')})
{tr_lines}
"""

    # Build terminology mapping
    terminology_str = ""
    if profile.terminology:
        term_lines = "\n".join(
            f"- {math_term} = {domain_term}"
            for math_term, domain_term in list(profile.terminology.items())[:6]
        )
        terminology_str = f"""
### Math-to-{profile.display_name} Vocabulary (use these naturally)
{term_lines}
"""

    return f"""Transform the math textbook content below into a {profile.display_name}-themed
version that middle school and high school students will genuinely enjoy reading.

## WHO YOU ARE WRITING FOR

Your readers are 11-18 year old students who are passionate about {profile.name}.
They know the rules, the players, the culture. If you get a detail wrong — like
saying a basketball three-pointer is worth 2 points, or that a soccer game has
4 quarters — they will immediately notice and lose trust. Write like someone who
is a genuine {profile.name} fan AND a great math teacher.

## DOMAIN KNOWLEDGE — READ THIS CAREFULLY

You MUST follow these rules about {profile.display_name} when creating examples.
Getting these wrong makes the content feel fake and kills engagement.

{profile.basic_knowledge if profile.basic_knowledge else "Use common knowledge about " + profile.name + ". Be factually accurate."}
{verified_stats_str}
## CRITICAL RULES FOR REALISTIC EXAMPLES

1. **Numbers must be realistic.** Every number in a word problem should be something
   that could actually happen in real {profile.name}. If you're writing about a
   basketball player's points, use numbers between 0-60 (not 200). If you're
   writing about game scores, use realistic ranges. If you're writing about money,
   use real-world prices. A student who knows {profile.name} should read your
   example and think "yeah, that could happen."

2. **Scenarios must make sense.** Don't just swap in {profile.name} words — the
   entire scenario must logically work. If the math requires dividing something
   into 7 equal groups, find a {profile.name} scenario where dividing into 7
   actually makes sense (not "7 quarters of a basketball game" because there
   are only 4).

3. **Use 2nd person ("you") as the default voice.** Say "You scored 24 points..."
   not "A player scored 24 points..." Make the student the protagonist of the
   story. They are the player, the coach, the team owner, the analyst.

4. **Reference real people and real events.** Use the famous figures listed below
   by name. Reference real stats. Kids love seeing names they recognize.

5. **Match the vibe.** Middle schoolers and high schoolers want content that feels
   like it was written by someone who actually follows {profile.name}, not a
   textbook author who googled it. Use the right slang and cultural references
   naturally — don't force them.

## REFERENCE MATERIAL

### About {profile.display_name}
{profile.context_intro}

### Famous Figures to Reference
{figures}
{terminology_str}
### Example Scenarios for Word Problems (adapt to the math being taught)
{scenarios}
{second_person_str}{trending_str}
### Fun Facts (include 2-3 as "{profile.display_name} Fact!" callout boxes)
{fun_facts}

### Cultural References & Iconic Moments (use naturally for engagement)
{cultural_refs if cultural_refs else "Use current pop culture references related to " + profile.name}

### Historical Context
{historical if historical else "Include relevant historical facts about " + profile.name}

### Motivational Quotes (use for chapter intro or conclusion)
{quotes if quotes else "Use inspiring quotes from notable figures in " + profile.name}

### Visual Theme
- Colors: {profile.visual_themes.get('primary_colors', 'Use thematic colors')}
- Imagery: {profile.visual_themes.get('imagery', 'Use relevant imagery')}

## HOW TO TRANSFORM THE CONTENT

1. **Keep ALL Math Intact**: Every equation, formula, property, theorem, and
   mathematical concept must remain exactly the same. You are changing CONTEXT
   and EXAMPLES only — never the underlying math.

2. **Replace Every Generic Example** with a {profile.name} scenario that:
   - Uses realistic numbers that match the domain
   - Makes logical sense for {profile.name}
   - Addresses the student as "you" where possible
   - References real people, teams, or events

3. **Rewrite Word Problems Completely** — don't just swap a few nouns.
   The entire problem should feel like it naturally belongs in {profile.name}.
   The math stays the same but the story should be new and engaging.

4. **Add Engaging Elements**:
   - 2-3 "{profile.display_name} Fact!" callout boxes with fun facts
   - A motivational quote at the chapter start or end
   - Cultural references students will recognize and enjoy
   - "Think About It" challenge questions that connect math to {profile.name}

5. **Format for Readability**:
   - Use markdown with clear headers
   - Add an emoji to the title
   - Use themed section headers
   - Keep step-by-step solutions clear and easy to follow

## ORIGINAL TEXTBOOK CONTENT TO TRANSFORM

```markdown
{textbook_content}
```

## OUTPUT

Write the complete transformed chapter. Output ONLY the markdown content — no
commentary or explanation. Start with the chapter title.
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

    The system prompt instructs the LLM to purely extract concepts from
    the textbook content — no predefined knowledge graph is used.
    """
    system_prompt = CONCEPT_EXTRACTOR_SYSTEM_PROMPT

    truncated = markdown_content[:MAX_CONTENT_CHARS]
    if len(markdown_content) > MAX_CONTENT_CHARS:
        truncated += "\n\n[Content truncated for analysis]"

    user_prompt = (
        "Analyze this math textbook content and extract all mathematical concepts:\n\n"
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
    preferred_address: Optional[str] = None,
    grade_level: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    favorite_figure: Optional[str] = None,
    favorite_team: Optional[str] = None,
    textbook_content: Optional[str] = None,
) -> PromptPreview:
    """Build animation generation prompts without executing them.

    Uses the same ``get_animation_personalization()`` path as the main
    engine so the playground preview matches actual generation.
    """
    from ...constants import AnimationStyle
    from ...personalization import StudentProfile

    style = AnimationStyle(animation_style) if animation_style else AnimationStyle.DARK
    system_prompt = get_system_prompt(style)

    # Build location string from city/state
    location = None
    if city and state:
        location = f"{city}, {state}"
    elif city:
        location = city
    elif state:
        location = state

    # Build student profile if any student fields provided
    student = None
    if student_name or preferred_address or grade_level or favorite_figure or favorite_team:
        student = StudentProfile(
            name=student_name,
            preferred_address=preferred_address,
            grade_level=grade_level,
            favorite_figure=favorite_figure,
            favorite_team=favorite_team,
        )

    # Resolve display address for the prompt
    display_address = None
    if student:
        addr = student.get_display_address()
        if addr != "you":
            display_address = addr

    # Use the same personalization path as the main engine
    personalization_context = ""
    if interest:
        personalizer = ContentPersonalizer(interest)
        if personalizer.profile:
            personalization_context = personalizer.get_animation_personalization(
                topic, student=student
            )

        # Enrich with engagement-specific data from InterestProfile
        profile = get_interest_profile(interest)
        if profile:
            if getattr(profile, "second_person_scenarios", None):
                personalization_context += "\n## REAL SCENARIOS (use these directly, don't make up generic ones)\n"
                for s in profile.second_person_scenarios[:3]:
                    personalization_context += f"- {s}\n"
            if getattr(profile, "engagement_hooks", None):
                personalization_context += "\n## ENGAGEMENT HOOKS (weave into the animation)\n"
                for h in profile.engagement_hooks[:2]:
                    personalization_context += f"- {h}\n"
            if getattr(profile, "verified_stats", None):
                personalization_context += "\n## VERIFIED STATS (use real numbers, not made-up ones)\n"
                for k, v in list(profile.verified_stats.items())[:4]:
                    personalization_context += f"- {k}: {v}\n"
            if getattr(profile, "trending_now", None):
                personalization_context += "\n## TRENDING NOW (current references)\n"
                for t in profile.trending_now[:2]:
                    personalization_context += f"- {t}\n"

    # Add location context if provided
    if location:
        personalization_context += f"\nStudent location: {location} (use local references when relevant)\n"

    # Include personalized textbook content as context for animation
    textbook_context = ""
    if textbook_content:
        # Truncate to avoid overwhelming the prompt
        max_len = 2000
        truncated = textbook_content[:max_len]
        if len(textbook_content) > max_len:
            truncated += "\n...[truncated]"
        textbook_context = (
            "\n## TEXTBOOK CONTENT (base the animation on this material)\n"
            f"{truncated}\n"
        )

    user_prompt = build_generation_prompt(
        topic=topic,
        requirements=requirements,
        audience_level=audience_level,
        personalization_context=personalization_context,
        student_name=student_name,
        student_address=display_address,
        textbook_context=textbook_context,
    )

    return PromptPreview(
        stage="generate_animation",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )


