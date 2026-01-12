#!/usr/bin/env python3
"""
Generate personalized chapter content for different student interests.

This script demonstrates how to use the personalization system to create
math content that is tailored to specific student interests like basketball,
gaming, music, etc.

Usage:
    # Generate basketball-themed Chapter 2 content
    python generate_personalized_chapter.py --chapter 2 --interest basketball

    # Generate gaming-themed content
    python generate_personalized_chapter.py --chapter 2 --interest gaming

    # List available interests
    python generate_personalized_chapter.py --list-interests

    # Generate for multiple interests
    python generate_personalized_chapter.py --chapter 2 --interest basketball gaming music
"""

import argparse
import logging
import sys
from pathlib import Path

# Add parent path to import math_content_engine
sys.path.insert(0, str(Path(__file__).parents[3] / "src"))

from math_content_engine import (
    MathContentEngine,
    Config,
    ContentPersonalizer,
    list_available_interests,
    get_interest_profile,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# =============================================================================
# CHAPTER CONTENT DEFINITIONS
# =============================================================================

CHAPTER_CONTENT = {
    2: {
        "title": "Solving Linear Equations and Inequalities",
        "sections": [
            {
                "section": "2.1",
                "title": "Addition and Subtraction Properties of Equality",
                "topics": [
                    {
                        "name": "verify_solution",
                        "topic": "Verifying a solution to a linear equation",
                        "requirements": """
                        Show how to verify if x = 5 is a solution to 6x - 17 = 13.
                        Step 1: Write the original equation
                        Step 2: Substitute x = 5 into the equation
                        Step 3: Calculate the left side: 6(5) - 17 = 30 - 17 = 13
                        Step 4: Compare with right side: 13 = 13
                        Step 5: Conclude x = 5 IS a solution
                        Use visual confirmation (checkmark) for correct answer.
                        """,
                    },
                    {
                        "name": "subtraction_property",
                        "topic": "Subtraction Property of Equality for solving equations",
                        "requirements": """
                        Demonstrate solving y + 37 = -13 using subtraction property.
                        Show the balance concept - what you do to one side, do to the other.
                        Visualize the subtraction happening on both sides simultaneously.
                        """,
                    },
                    {
                        "name": "addition_property",
                        "topic": "Addition Property of Equality for solving equations",
                        "requirements": """
                        Demonstrate solving a - 28 = -37 using addition property.
                        Show balance/equality being maintained.
                        Visualize adding to both sides.
                        """,
                    },
                ]
            },
            {
                "section": "2.2",
                "title": "Division and Multiplication Properties of Equality",
                "topics": [
                    {
                        "name": "division_property",
                        "topic": "Division Property of Equality for solving equations",
                        "requirements": """
                        Solve 7x = 91 using division.
                        Show dividing both sides and the cancellation visually.
                        """,
                    },
                    {
                        "name": "multiplication_property",
                        "topic": "Multiplication Property of Equality",
                        "requirements": """
                        Solve n/6 = 15 using multiplication.
                        Show multiplying both sides to isolate variable.
                        """,
                    },
                    {
                        "name": "fraction_coefficient",
                        "topic": "Solving equations with fraction coefficients using reciprocals",
                        "requirements": """
                        Solve (2/3)x = 18 using reciprocal multiplication.
                        Show how multiplying by the reciprocal cancels the fraction.
                        """,
                    },
                ]
            },
            {
                "section": "2.3",
                "title": "Variables on Both Sides",
                "topics": [
                    {
                        "name": "variables_both_sides",
                        "topic": "Solving equations with variables on both sides",
                        "requirements": """
                        Solve 5x + 8 = 3x + 14 step by step.
                        Show moving variable terms to one side, constants to other.
                        Use arrows and color coding to show the movement.
                        """,
                    },
                    {
                        "name": "with_parentheses",
                        "topic": "Solving equations with parentheses using distributive property",
                        "requirements": """
                        Solve 3(2x - 5) = 4x + 7.
                        Show distribution first, then solving.
                        """,
                    },
                ]
            },
            {
                "section": "2.4",
                "title": "General Strategy for Linear Equations",
                "topics": [
                    {
                        "name": "general_strategy",
                        "topic": "5-step general strategy for solving linear equations",
                        "requirements": """
                        Present the 5-step strategy:
                        1. SIMPLIFY: Distribute and combine like terms
                        2. COLLECT VARIABLES: Get all variables on one side
                        3. COLLECT CONSTANTS: Get all constants on other side
                        4. ISOLATE: Divide or multiply to get variable alone
                        5. CHECK: Verify the solution
                        Make it memorable and visual.
                        """,
                    },
                    {
                        "name": "no_solution",
                        "topic": "Equations with no solution - contradictions",
                        "requirements": """
                        Show that 3(x + 2) = 3x + 1 has NO solution.
                        End up with false statement like 6 = 1.
                        Explain what this means graphically (parallel lines).
                        """,
                    },
                ]
            },
            {
                "section": "2.7",
                "title": "Linear Inequalities",
                "topics": [
                    {
                        "name": "inequality_symbols",
                        "topic": "Introduction to inequality symbols and number line graphs",
                        "requirements": """
                        Introduce <, >, ≤, ≥ symbols.
                        Show open circles vs closed circles on number line.
                        Show direction of arrows.
                        """,
                    },
                    {
                        "name": "negative_division_rule",
                        "topic": "CRITICAL: Reversing inequality when dividing by negative",
                        "requirements": """
                        Solve -2x > 8 and explain why inequality reverses!
                        This is a common mistake - make it memorable.
                        Show counter-example to prove the rule.
                        """,
                    },
                ]
            },
        ]
    }
}


def generate_personalized_animations(
    chapter_num: int,
    interest: str,
    output_dir: Path,
    preview_only: bool = False
):
    """Generate all animations for a chapter with personalization."""

    if chapter_num not in CHAPTER_CONTENT:
        logger.error(f"Chapter {chapter_num} not found")
        return

    profile = get_interest_profile(interest)
    if not profile:
        logger.error(f"Interest '{interest}' not found. Available: {list_available_interests()}")
        return

    chapter = CHAPTER_CONTENT[chapter_num]
    logger.info(f"Generating Chapter {chapter_num}: {chapter['title']}")
    logger.info(f"Personalization: {profile.display_name}")

    # Create output directory
    interest_output = output_dir / f"chapter_{chapter_num:02d}_{interest}"
    interest_output.mkdir(parents=True, exist_ok=True)

    # Initialize engine with personalization
    config = Config.from_env()
    config.output_dir = interest_output

    engine = MathContentEngine(config, interest=interest)

    results = []

    for section in chapter["sections"]:
        section_num = section["section"]
        section_title = section["title"]

        logger.info(f"\n{'='*60}")
        logger.info(f"Section {section_num}: {section_title}")
        logger.info("="*60)

        for topic_info in section["topics"]:
            name = topic_info["name"]
            topic = topic_info["topic"]
            requirements = topic_info["requirements"]

            output_name = f"{section_num.replace('.', '_')}_{name}_{interest}"

            logger.info(f"\nGenerating: {output_name}")
            logger.info(f"Topic: {topic}")

            try:
                if preview_only:
                    # Just generate code, don't render
                    result = engine.preview_code(
                        topic=topic,
                        requirements=requirements,
                        audience_level="high school"
                    )

                    # Save the code
                    code_path = interest_output / f"{output_name}.py"
                    with open(code_path, 'w') as f:
                        f.write(f"# {topic} - {profile.display_name} Edition\n")
                        f.write(f"# Section {section_num}\n\n")
                        f.write(result.code)

                    logger.info(f"  Code saved: {code_path}")
                    results.append((output_name, True, "Code generated"))
                else:
                    # Full generation and rendering
                    result = engine.generate(
                        topic=topic,
                        requirements=requirements,
                        audience_level="high school",
                        output_filename=output_name
                    )

                    if result.success:
                        logger.info(f"  SUCCESS: {result.video_path}")
                        results.append((output_name, True, str(result.video_path)))
                    else:
                        logger.error(f"  FAILED: {result.error_message}")
                        results.append((output_name, False, result.error_message))

            except Exception as e:
                logger.exception(f"  ERROR: {e}")
                results.append((output_name, False, str(e)))

    # Summary
    logger.info(f"\n{'='*60}")
    logger.info(f"GENERATION COMPLETE - {profile.display_name}")
    logger.info("="*60)

    success_count = sum(1 for _, success, _ in results if success)
    logger.info(f"Total: {success_count}/{len(results)} successful")

    for name, success, msg in results:
        status = "✓" if success else "✗"
        logger.info(f"  {status} {name}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Generate personalized math content for different student interests"
    )
    parser.add_argument(
        "--chapter", "-c",
        type=int,
        help="Chapter number to generate"
    )
    parser.add_argument(
        "--interest", "-i",
        nargs="+",
        help="Interest(s) to personalize for (e.g., basketball, gaming, music)"
    )
    parser.add_argument(
        "--list-interests", "-l",
        action="store_true",
        help="List available interests"
    )
    parser.add_argument(
        "--preview", "-p",
        action="store_true",
        help="Only generate code, don't render videos"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=str(Path(__file__).parent / "personalized"),
        help="Output directory"
    )

    args = parser.parse_args()

    if args.list_interests:
        print("\nAvailable interests for personalization:")
        print("="*50)
        for interest_name in list_available_interests():
            profile = get_interest_profile(interest_name)
            if profile:
                print(f"\n  {interest_name}")
                print(f"    Display: {profile.display_name}")
                print(f"    Description: {profile.description}")
                print(f"    Famous figures: {', '.join(profile.famous_figures[:3])}...")
        print()
        return

    if not args.chapter:
        parser.error("--chapter is required (use --list-interests to see available interests)")

    if not args.interest:
        parser.error("--interest is required (use --list-interests to see options)")

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate for each interest
    for interest in args.interest:
        logger.info(f"\n{'#'*60}")
        logger.info(f"# Generating for interest: {interest}")
        logger.info("#"*60 + "\n")

        generate_personalized_animations(
            chapter_num=args.chapter,
            interest=interest,
            output_dir=output_dir,
            preview_only=args.preview
        )


if __name__ == "__main__":
    main()
