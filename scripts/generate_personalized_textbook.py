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
from math_content_engine.api.playground.prompt_builder import (
    _build_personalization_user_prompt,
    _PERSONALIZATION_SYSTEM_PROMPT,
)

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
    """Create the LLM prompt for personalizing textbook content.

    Delegates to the shared prompt builder in
    ``math_content_engine.api.playground.prompt_builder`` so the CLI script
    and the playground UI always use the same prompt.
    """
    return _build_personalization_user_prompt(textbook_content, interest_name)


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
        system_prompt=_PERSONALIZATION_SYSTEM_PROMPT,
        max_tokens=8000,
    )

    return response.content


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
