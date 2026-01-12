#!/usr/bin/env python3
"""
Regenerate Chapter 2 personalized textbook and animations using Claude Opus.

This script:
1. Reads the original Chapter 2 textbook content
2. Uses Claude Opus to generate a personalized (basketball-themed) version
3. Saves the personalized textbook
4. Generates animations from the textbook examples

Usage:
    python regenerate_chapter2_opus.py                  # Full regeneration
    python regenerate_chapter2_opus.py --textbook-only  # Only regenerate textbook
    python regenerate_chapter2_opus.py --animations-only # Only regenerate animations
    python regenerate_chapter2_opus.py --preview        # Preview animations (no render)
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add src path
sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from anthropic import Anthropic

from math_content_engine import MathContentEngine, Config
from math_content_engine.personalization import get_interest_profile
from math_content_engine.personalization.textbook_parser import TextbookParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
CURRICULUM_DIR = Path(__file__).parent
TEXTBOOKS_DIR = CURRICULUM_DIR / "textbooks"
ORIGINAL_TEXTBOOK = TEXTBOOKS_DIR / "chapter_02_linear_equations.md"
OUTPUT_DIR = CURRICULUM_DIR / "personalized" / "chapter_02_basketball"

# Opus model
OPUS_MODEL = "claude-opus-4-20250514"


def generate_personalized_textbook(interest: str = "basketball") -> str:
    """Generate a personalized textbook using Claude Opus."""

    logger.info(f"Generating personalized textbook for interest: {interest}")
    logger.info(f"Using model: {OPUS_MODEL}")

    # Read original textbook
    with open(ORIGINAL_TEXTBOOK, 'r') as f:
        original_content = f.read()

    # Get interest profile for context
    profile = get_interest_profile(interest)
    if not profile:
        raise ValueError(f"Unknown interest: {interest}")

    personalization_context = profile.get_personalization_prompt()

    # Create prompt for Opus
    prompt = f"""You are an expert math curriculum writer creating personalized educational content for 6th-8th grade students (ages 11-14).

Your task is to rewrite this Algebra 1 Chapter 2 textbook with a {interest.upper()} theme.

{personalization_context}

## ORIGINAL TEXTBOOK CONTENT:

{original_content}

## YOUR TASK:

Rewrite the entire chapter with the following requirements:

1. **Keep all math content identical** - same equations, same solutions, same mathematical concepts
2. **Replace all word problems and contexts** with {interest}-themed scenarios
3. **Use famous figures** from the interest area in examples
4. **Add themed section titles** while keeping section numbers
5. **Include fun facts** related to {interest} that connect to the math
6. **Use age-appropriate language** for middle school students (grades 6-8)
7. **Add a themed subtitle** to the chapter (e.g., "NBA Edition")
8. **Keep the structure**: Learning Objectives, Key Concepts, Examples, Practice Problems

For each example:
- Create a realistic {interest} scenario that uses the EXACT SAME equation
- Show the complete solution with all steps
- Include a "Check" step to verify the answer
- Add a brief themed conclusion

Make sure:
- All numbers and equations are MATHEMATICALLY CORRECT
- The context makes sense (e.g., points, yards, goals should be realistic)
- Language is engaging and relatable to middle schoolers

Write the complete personalized chapter in markdown format.
"""

    # Call Claude Opus with streaming for long requests
    client = Anthropic()

    logger.info("Calling Claude Opus API (streaming)...")

    personalized_content = ""
    with client.messages.stream(
        model=OPUS_MODEL,
        max_tokens=16000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    ) as stream:
        for text in stream.text_stream:
            personalized_content += text
            print(".", end="", flush=True)  # Progress indicator

    print()  # Newline after progress dots
    logger.info("API call complete")

    # Save the personalized textbook
    output_path = TEXTBOOKS_DIR / f"chapter_02_linear_equations_{interest}.md"
    with open(output_path, 'w') as f:
        f.write(personalized_content)

    logger.info(f"Personalized textbook saved to: {output_path}")

    return str(output_path)


def generate_animations_from_textbook(
    textbook_path: str,
    output_dir: Path,
    preview_only: bool = False,
    interest: str = "basketball"
):
    """Generate animations from the personalized textbook."""

    logger.info(f"Generating animations from: {textbook_path}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Preview only: {preview_only}")

    # Parse textbook
    parser = TextbookParser(textbook_path)
    chapter = parser.parse()
    animation_specs = parser.get_examples_for_animation()

    if not animation_specs:
        logger.warning("No examples found in textbook!")
        return []

    logger.info(f"Found {len(animation_specs)} examples to animate")

    # Create output directory
    animations_dir = output_dir / "from_textbook"
    animations_dir.mkdir(parents=True, exist_ok=True)

    # Configure engine with Opus model
    os.environ["MATH_ENGINE_CLAUDE_MODEL"] = OPUS_MODEL
    config = Config.from_env()
    config.output_dir = animations_dir

    engine = MathContentEngine(config, interest=interest)

    results = []

    for i, spec in enumerate(animation_specs, 1):
        section = spec['section']
        example_num = spec['example_num']
        topic = spec['topic']
        requirements = spec['requirements']

        output_name = f"textbook_{section.replace('.', '_')}_ex{example_num}_{interest}"

        logger.info(f"\n{'='*60}")
        logger.info(f"[{i}/{len(animation_specs)}] Generating: {output_name}")
        logger.info(f"Topic: {topic}")
        logger.info(f"Equation: {spec.get('equation', 'N/A')}")
        logger.info("="*60)

        try:
            if preview_only:
                # Generate code only
                result = engine.preview_code(
                    topic=topic,
                    requirements=requirements,
                    audience_level="middle school"
                )

                code_path = animations_dir / f"{output_name}.py"
                with open(code_path, 'w') as f:
                    f.write(f"# Generated from textbook: {topic}\n")
                    f.write(f"# Section {section}, Example {example_num}\n")
                    f.write(f"# Theme: {interest}\n")
                    f.write(f"# Model: {OPUS_MODEL}\n\n")
                    f.write(result.code)

                logger.info(f"  Code saved: {code_path}")
                results.append((output_name, True, str(code_path)))

            else:
                # Full generation with rendering
                result = engine.generate(
                    topic=topic,
                    requirements=requirements,
                    audience_level="middle school",
                    output_filename=output_name
                )

                if result.success:
                    logger.info(f"  SUCCESS: {result.video_path}")
                    logger.info(f"  Render time: {result.render_time:.1f}s")
                    results.append((output_name, True, str(result.video_path)))

                    # Save code too
                    code_path = animations_dir / f"{output_name}.py"
                    with open(code_path, 'w') as f:
                        f.write(f"# Generated from textbook: {topic}\n")
                        f.write(f"# Section {section}, Example {example_num}\n\n")
                        f.write(result.code)
                else:
                    logger.error(f"  FAILED: {result.error_message}")
                    results.append((output_name, False, result.error_message))

        except Exception as e:
            logger.exception(f"  ERROR: {e}")
            results.append((output_name, False, str(e)))

    # Print summary
    logger.info(f"\n{'='*60}")
    logger.info("ANIMATION GENERATION COMPLETE")
    logger.info("="*60)

    success_count = sum(1 for _, success, _ in results if success)
    logger.info(f"Results: {success_count}/{len(results)} successful")

    for name, success, msg in results:
        status = "[OK]" if success else "[FAIL]"
        logger.info(f"  {status} {name}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Regenerate Chapter 2 with personalization using Claude Opus"
    )
    parser.add_argument(
        "--interest", "-i",
        type=str,
        default="basketball",
        help="Interest theme (default: basketball)"
    )
    parser.add_argument(
        "--textbook-only",
        action="store_true",
        help="Only regenerate the textbook, skip animations"
    )
    parser.add_argument(
        "--animations-only",
        action="store_true",
        help="Only regenerate animations from existing textbook"
    )
    parser.add_argument(
        "--preview", "-p",
        action="store_true",
        help="Preview animations (generate code only, no rendering)"
    )

    args = parser.parse_args()

    interest = args.interest.lower()

    # Determine textbook path
    textbook_path = TEXTBOOKS_DIR / f"chapter_02_linear_equations_{interest}.md"

    logger.info("="*60)
    logger.info("CHAPTER 2 REGENERATION WITH CLAUDE OPUS")
    logger.info("="*60)
    logger.info(f"Interest: {interest.upper()}")
    logger.info(f"Model: {OPUS_MODEL}")
    logger.info(f"Textbook only: {args.textbook_only}")
    logger.info(f"Animations only: {args.animations_only}")
    logger.info(f"Preview mode: {args.preview}")
    logger.info("="*60)

    # Step 1: Generate personalized textbook (unless animations-only)
    if not args.animations_only:
        logger.info("\n" + "="*60)
        logger.info("STEP 1: Generating Personalized Textbook")
        logger.info("="*60)

        textbook_path = generate_personalized_textbook(interest)
        logger.info(f"Textbook generated: {textbook_path}")
    else:
        if not textbook_path.exists():
            logger.error(f"Textbook not found: {textbook_path}")
            logger.error("Run without --animations-only first to generate the textbook")
            sys.exit(1)
        logger.info(f"Using existing textbook: {textbook_path}")

    # Step 2: Generate animations (unless textbook-only)
    if not args.textbook_only:
        logger.info("\n" + "="*60)
        logger.info("STEP 2: Generating Animations from Textbook")
        logger.info("="*60)

        output_dir = CURRICULUM_DIR / "personalized" / f"chapter_02_{interest}"
        output_dir.mkdir(parents=True, exist_ok=True)

        results = generate_animations_from_textbook(
            textbook_path=str(textbook_path),
            output_dir=output_dir,
            preview_only=args.preview,
            interest=interest
        )

        logger.info(f"\nAnimations saved to: {output_dir / 'from_textbook'}")

    logger.info("\n" + "="*60)
    logger.info("REGENERATION COMPLETE")
    logger.info("="*60)


if __name__ == "__main__":
    main()
