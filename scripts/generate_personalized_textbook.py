#!/usr/bin/env python3
"""
Generate Personalized Textbook Chapters.

This script takes a base textbook chapter and an interest, then uses the LLM
to create a personalized version of the textbook content that engages students
with their specific interests.

Usage:
    # Generate basketball-themed version of a chapter
    python generate_personalized_textbook.py \
        --input curriculum/algebra1/textbooks/chapter_02_linear_equations.md \
        --interest basketball \
        --output curriculum/algebra1/textbooks/chapter_02_linear_equations_basketball.md

    # Generate for multiple interests at once
    python generate_personalized_textbook.py \
        --input curriculum/algebra1/textbooks/chapter_02_linear_equations.md \
        --interest basketball gaming music anime \
        --output-dir curriculum/algebra1/textbooks/personalized/

    # List available interests
    python generate_personalized_textbook.py --list-interests
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from math_content_engine.personalization import (
    get_interest_profile,
    list_available_interests,
)
from math_content_engine.llm import create_llm_client
from math_content_engine.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_personalization_prompt(
    textbook_content: str,
    interest_name: str,
) -> str:
    """
    Create the LLM prompt for personalizing textbook content.

    Args:
        textbook_content: The original textbook markdown content
        interest_name: The interest to personalize for

    Returns:
        The full prompt for the LLM
    """
    profile = get_interest_profile(interest_name)
    if not profile:
        raise ValueError(f"Unknown interest: {interest_name}")

    # Build rich context from the interest profile
    fun_facts = "\n".join(f"- {fact}" for fact in profile.fun_facts[:5])
    cultural_refs = "\n".join(f"- {ref}" for ref in getattr(profile, 'cultural_references', [])[:4])
    historical = "\n".join(f"- {fact}" for fact in getattr(profile, 'historical_trivia', [])[:3])
    quotes = "\n".join(f'- "{quote}"' for quote in getattr(profile, 'motivational_quotes', [])[:2])
    scenarios = "\n".join(f"- {s}" for s in profile.example_scenarios[:6])
    figures = ", ".join(profile.famous_figures[:8])

    prompt = f'''You are an expert math textbook author who specializes in creating engaging,
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
   - Add an appropriate emoji to the title (e.g., 🏀 for basketball)
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
'''
    return prompt


def personalize_textbook(
    textbook_content: str,
    interest_name: str,
    config: Config,
) -> str:
    """
    Use LLM to personalize textbook content.

    Args:
        textbook_content: Original textbook markdown
        interest_name: Interest to personalize for
        config: Configuration with LLM settings

    Returns:
        Personalized textbook markdown content
    """
    profile = get_interest_profile(interest_name)
    if not profile:
        raise ValueError(f"Unknown interest: {interest_name}")

    logger.info(f"Creating personalized content for: {profile.display_name}")

    # Create LLM client
    llm_client = create_llm_client(config)

    # Create the personalization prompt
    prompt = create_personalization_prompt(textbook_content, interest_name)

    # Call the LLM
    logger.info("Sending to LLM for personalization...")
    response = llm_client.generate(
        prompt=prompt,
        system_prompt="You are an expert educational content creator specializing in personalized math textbooks.",
        max_tokens=8000,
    )

    return response


def generate_personalized_textbook(
    input_path: Path,
    interest_name: str,
    output_path: Path,
    config: Config,
) -> bool:
    """
    Generate a personalized textbook chapter.

    Args:
        input_path: Path to input textbook markdown
        interest_name: Interest to personalize for
        output_path: Path to save output
        config: Configuration

    Returns:
        True if successful
    """
    profile = get_interest_profile(interest_name)
    if not profile:
        logger.error(f"Unknown interest: {interest_name}")
        return False

    logger.info(f"Reading input textbook: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        textbook_content = f.read()

    # Personalize the content
    try:
        personalized_content = personalize_textbook(
            textbook_content,
            interest_name,
            config
        )
    except Exception as e:
        logger.exception(f"Failed to personalize textbook: {e}")
        return False

    # Save output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(personalized_content)

    logger.info(f"Personalized textbook saved to: {output_path}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Generate personalized textbook chapters for different student interests"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Path to the input textbook markdown file"
    )
    parser.add_argument(
        "--interest",
        nargs="+",
        help="Interest(s) to personalize for (e.g., basketball, gaming, music)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output path for single interest (or use --output-dir for multiple)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Output directory for multiple interests"
    )
    parser.add_argument(
        "--list-interests", "-l",
        action="store_true",
        help="List all available interests"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without actually calling the LLM"
    )

    args = parser.parse_args()

    # Handle --list-interests
    if args.list_interests:
        print("\nAvailable interests for personalization:")
        print("=" * 60)
        for interest_name in list_available_interests():
            profile = get_interest_profile(interest_name)
            if profile:
                print(f"\n  {interest_name}")
                print(f"    Display: {profile.display_name}")
                print(f"    Description: {profile.description}")
                figures = ", ".join(profile.famous_figures[:3])
                print(f"    Famous figures: {figures}...")

                # Show new diversity fields if available
                if hasattr(profile, 'cultural_references') and profile.cultural_references:
                    print(f"    Cultural refs: {len(profile.cultural_references)} available")
                if hasattr(profile, 'fun_facts') and profile.fun_facts:
                    print(f"    Fun facts: {len(profile.fun_facts)} available")
        print()
        return

    # Validate required arguments
    if not args.input:
        parser.error("--input is required")
    if not args.interest:
        parser.error("--interest is required")

    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)

    # Load configuration
    config = Config.from_env()

    # Determine output path(s)
    interests = args.interest

    if len(interests) == 1 and args.output:
        # Single interest with explicit output path
        outputs = [(interests[0], Path(args.output))]
    elif args.output_dir:
        # Multiple interests with output directory
        output_dir = Path(args.output_dir)
        base_name = input_path.stem
        outputs = [
            (interest, output_dir / f"{base_name}_{interest}.md")
            for interest in interests
        ]
    else:
        # Default: put in same directory as input with interest suffix
        outputs = [
            (interest, input_path.parent / f"{input_path.stem}_{interest}.md")
            for interest in interests
        ]

    # Process each interest
    success_count = 0
    for interest, output_path in outputs:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {interest} -> {output_path}")
        logger.info("=" * 60)

        if args.dry_run:
            profile = get_interest_profile(interest)
            if profile:
                print(f"\n[DRY RUN] Would generate: {output_path}")
                print(f"  Interest: {profile.display_name}")
                print(f"  Input: {input_path}")
            else:
                print(f"\n[DRY RUN] ERROR: Unknown interest '{interest}'")
            continue

        if generate_personalized_textbook(input_path, interest, output_path, config):
            success_count += 1
        else:
            logger.error(f"Failed to generate for interest: {interest}")

    if not args.dry_run:
        logger.info(f"\n{'='*60}")
        logger.info(f"COMPLETE: {success_count}/{len(outputs)} successful")
        logger.info("=" * 60)


if __name__ == "__main__":
    main()
