#!/usr/bin/env python3
"""
Generate all animations for Chapter 2: Solving Linear Equations and Inequalities

This script generates educational Manim animations for each section of Chapter 2,
based on the OpenStax Elementary Algebra 2e curriculum.

Usage:
    python generate_chapter_02_animations.py [--section SECTION_NUM]

Sections:
    2.1 - Addition and Subtraction Properties of Equality
    2.2 - Division and Multiplication Properties of Equality
    2.3 - Variables on Both Sides
    2.4 - General Strategy for Solving Linear Equations
    2.7 - Linear Inequalities
"""

import argparse
import logging
import sys
from pathlib import Path

# Add parent path to import math_content_engine
sys.path.insert(0, str(Path(__file__).parents[4] / "src"))

from math_content_engine import MathContentEngine, Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Output directory
OUTPUT_DIR = Path(__file__).parent


# =============================================================================
# ANIMATION DEFINITIONS FOR CHAPTER 2
# =============================================================================

CHAPTER_2_ANIMATIONS = {
    "2.1": {
        "title": "Addition and Subtraction Properties of Equality",
        "animations": [
            {
                "name": "2_1_01_verify_solution",
                "topic": "Verifying a solution to a linear equation",
                "requirements": """
                Show how to verify if x = 5 is a solution to 6x - 17 = 13.
                Step 1: Write the original equation
                Step 2: Substitute x = 5 into the equation
                Step 3: Calculate the left side: 6(5) - 17 = 30 - 17 = 13
                Step 4: Compare with right side: 13 = 13 ✓
                Step 5: Conclude x = 5 IS a solution
                Use green checkmark for correct, highlight each step clearly.
                """,
                "audience": "high school"
            },
            {
                "name": "2_1_02_subtraction_property",
                "topic": "Subtraction Property of Equality for solving equations",
                "requirements": """
                Demonstrate solving y + 37 = -13 using subtraction property.
                Step 1: Show the equation y + 37 = -13
                Step 2: Explain: "Subtract 37 from both sides to isolate y"
                Step 3: Show: y + 37 - 37 = -13 - 37
                Step 4: Simplify: y = -50
                Step 5: Verify by substituting back
                Use balance scale visual metaphor - show both sides stay equal.
                Color the -37 being subtracted in red on both sides.
                """,
                "audience": "high school"
            },
            {
                "name": "2_1_03_addition_property",
                "topic": "Addition Property of Equality for solving equations",
                "requirements": """
                Demonstrate solving a - 28 = -37 using addition property.
                Step 1: Show the equation a - 28 = -37
                Step 2: Explain: "Add 28 to both sides to isolate a"
                Step 3: Show: a - 28 + 28 = -37 + 28
                Step 4: Simplify: a = -9
                Step 5: Verify the solution
                Use visual balance scale showing equality maintained.
                Highlight the +28 being added to both sides in green.
                """,
                "audience": "high school"
            },
            {
                "name": "2_1_04_combine_like_terms",
                "topic": "Solving equations by combining like terms first",
                "requirements": """
                Solve 9x - 5 - 8x - 6 = 7 by first simplifying.
                Step 1: Show original equation
                Step 2: Identify like terms (9x and -8x, -5 and -6)
                Step 3: Combine: x - 11 = 7
                Step 4: Add 11 to both sides: x = 18
                Step 5: Verify solution
                Use color coding: variable terms in blue, constants in orange.
                Show arrows grouping like terms.
                """,
                "audience": "high school"
            },
        ]
    },
    "2.2": {
        "title": "Division and Multiplication Properties of Equality",
        "animations": [
            {
                "name": "2_2_01_division_property",
                "topic": "Division Property of Equality for solving equations",
                "requirements": """
                Solve 7x = 91 using division.
                Step 1: Show equation 7x = 91
                Step 2: Explain: "Divide both sides by 7 to isolate x"
                Step 3: Show: 7x/7 = 91/7
                Step 4: Simplify: x = 13
                Step 5: Verify: 7(13) = 91 ✓
                Show visually dividing both sides, use animation to show 7's canceling.
                """,
                "audience": "high school"
            },
            {
                "name": "2_2_02_negative_coefficient",
                "topic": "Solving equations with negative coefficients",
                "requirements": """
                Solve -12p = 48 using division by a negative.
                Step 1: Show equation -12p = 48
                Step 2: Divide both sides by -12
                Step 3: Show: -12p/(-12) = 48/(-12)
                Step 4: Result: p = -4
                Step 5: Verify: -12(-4) = 48 ✓
                Emphasize: dividing by negative gives negative quotient.
                Use color to highlight sign changes.
                """,
                "audience": "high school"
            },
            {
                "name": "2_2_03_multiplication_property",
                "topic": "Multiplication Property of Equality",
                "requirements": """
                Solve n/6 = 15 using multiplication.
                Step 1: Show equation n/6 = 15
                Step 2: Explain: "Multiply both sides by 6"
                Step 3: Show: 6 · (n/6) = 6 · 15
                Step 4: The 6's cancel: n = 90
                Step 5: Verify: 90/6 = 15 ✓
                Show the multiplication on both sides visually.
                """,
                "audience": "high school"
            },
            {
                "name": "2_2_04_fraction_coefficient",
                "topic": "Solving equations with fraction coefficients using reciprocals",
                "requirements": """
                Solve (2/3)x = 18 using reciprocal multiplication.
                Step 1: Show equation (2/3)x = 18
                Step 2: Explain: "Multiply both sides by the reciprocal 3/2"
                Step 3: Show: (3/2) · (2/3)x = (3/2) · 18
                Step 4: Simplify left side: the fractions multiply to 1
                Step 5: Calculate right side: (3/2) · 18 = 27
                Step 6: Result: x = 27
                Show fraction multiplication visually, highlight reciprocal cancellation.
                """,
                "audience": "high school"
            },
        ]
    },
    "2.3": {
        "title": "Variables on Both Sides",
        "animations": [
            {
                "name": "2_3_01_variables_both_sides",
                "topic": "Solving equations with variables on both sides",
                "requirements": """
                Solve 5x + 8 = 3x + 14 step by step.
                Step 1: Show equation 5x + 8 = 3x + 14
                Step 2: Subtract 3x from both sides to get variables on left
                Step 3: Show: 2x + 8 = 14
                Step 4: Subtract 8 from both sides
                Step 5: 2x = 6
                Step 6: Divide by 2: x = 3
                Step 7: Verify: 5(3) + 8 = 3(3) + 14 → 23 = 23 ✓
                Use arrows showing terms moving across equals sign.
                Color variables in blue, constants in orange.
                """,
                "audience": "high school"
            },
            {
                "name": "2_3_02_negative_variables",
                "topic": "Solving with negative variable terms",
                "requirements": """
                Solve 12 - 5y = 2y - 9.
                Step 1: Show the equation
                Step 2: Collect y terms: subtract 2y from both sides
                Step 3: 12 - 7y = -9
                Step 4: Collect constants: subtract 12 from both sides
                Step 5: -7y = -21
                Step 6: Divide by -7: y = 3
                Step 7: Verify the solution
                Show the strategy: gather variables on one side, constants on other.
                """,
                "audience": "high school"
            },
            {
                "name": "2_3_03_with_parentheses",
                "topic": "Solving equations with parentheses using distributive property",
                "requirements": """
                Solve 3(2x - 5) = 4x + 7 using distribution first.
                Step 1: Show original equation
                Step 2: Distribute the 3: 6x - 15 = 4x + 7
                Step 3: Subtract 4x: 2x - 15 = 7
                Step 4: Add 15: 2x = 22
                Step 5: Divide by 2: x = 11
                Step 6: Verify: 3(2(11) - 5) = 4(11) + 7 → 3(17) = 51 ✓
                Animate the distribution with arrows, color each term.
                """,
                "audience": "high school"
            },
        ]
    },
    "2.4": {
        "title": "General Strategy for Linear Equations",
        "animations": [
            {
                "name": "2_4_01_general_strategy",
                "topic": "5-step general strategy for solving linear equations",
                "requirements": """
                Present the 5-step strategy for solving ANY linear equation:
                1. SIMPLIFY: Distribute and combine like terms on each side
                2. COLLECT VARIABLES: Get all variable terms on one side
                3. COLLECT CONSTANTS: Get all constants on the other side
                4. ISOLATE: Divide or multiply to get the variable alone
                5. CHECK: Substitute solution into original equation

                Use a visual flowchart or numbered steps.
                Show each step with an icon or visual.
                Make it memorable like a recipe.
                """,
                "audience": "high school"
            },
            {
                "name": "2_4_02_complex_example",
                "topic": "Applying general strategy to complex equation",
                "requirements": """
                Solve 5(2x - 1) - 3(x + 4) = 2x - 7 using the 5-step method.
                Step 1: SIMPLIFY - Distribute: 10x - 5 - 3x - 12 = 2x - 7
                        Combine like terms: 7x - 17 = 2x - 7
                Step 2: COLLECT VARIABLES - Subtract 2x: 5x - 17 = -7
                Step 3: COLLECT CONSTANTS - Add 17: 5x = 10
                Step 4: ISOLATE - Divide by 5: x = 2
                Step 5: CHECK - Substitute and verify

                Label each step with its name from the strategy.
                Use different colors for each step.
                """,
                "audience": "high school"
            },
            {
                "name": "2_4_03_no_solution",
                "topic": "Equations with no solution - contradictions",
                "requirements": """
                Show that 3(x + 2) = 3x + 1 has NO SOLUTION.
                Step 1: Distribute: 3x + 6 = 3x + 1
                Step 2: Subtract 3x from both sides
                Step 3: Result: 6 = 1 (FALSE!)
                Step 4: Explain: This is a CONTRADICTION
                Step 5: When you get a false statement, there is NO SOLUTION

                Use red X or warning symbol for the contradiction.
                Show graphically that these are parallel lines that never intersect.
                """,
                "audience": "high school"
            },
            {
                "name": "2_4_04_infinite_solutions",
                "topic": "Equations with infinitely many solutions - identities",
                "requirements": """
                Show that 2(x + 3) = 2x + 6 has INFINITELY MANY solutions.
                Step 1: Distribute: 2x + 6 = 2x + 6
                Step 2: Both sides are IDENTICAL
                Step 3: Result: 6 = 6 (TRUE for ALL x!)
                Step 4: This is called an IDENTITY
                Step 5: Every real number is a solution

                Use green checkmark and infinity symbol.
                Show graphically that these are the SAME LINE.
                """,
                "audience": "high school"
            },
        ]
    },
    "2.7": {
        "title": "Linear Inequalities",
        "animations": [
            {
                "name": "2_7_01_inequality_symbols",
                "topic": "Introduction to inequality symbols and number line graphs",
                "requirements": """
                Introduce the four inequality symbols:
                < (less than) - open circle, arrow left
                > (greater than) - open circle, arrow right
                ≤ (less than or equal) - closed circle, arrow left
                ≥ (greater than or equal) - closed circle, arrow right

                Show each symbol with a number line example.
                Emphasize: open circle = not included, closed circle = included.
                Use animations to draw the circles and arrows.
                """,
                "audience": "high school"
            },
            {
                "name": "2_7_02_solve_basic_inequality",
                "topic": "Solving and graphing basic linear inequalities",
                "requirements": """
                Solve x + 4 > 9 and graph the solution.
                Step 1: Show inequality x + 4 > 9
                Step 2: Subtract 4 from both sides: x > 5
                Step 3: Graph on number line:
                   - Draw number line with point at 5
                   - Open circle at 5 (not included)
                   - Arrow pointing right (all numbers > 5)
                Step 4: Express in interval notation: (5, ∞)

                Animate the number line drawing.
                """,
                "audience": "high school"
            },
            {
                "name": "2_7_03_negative_division_rule",
                "topic": "CRITICAL RULE: Reversing inequality when dividing by negative",
                "requirements": """
                Solve -2x > 8 and explain why inequality reverses!
                Step 1: Show -2x > 8
                Step 2: IMPORTANT: When dividing by NEGATIVE, REVERSE the sign!
                Step 3: Divide by -2 and FLIP: x < -4
                Step 4: Explain WHY with example: 4 > 2, but -4 < -2
                Step 5: Graph: open circle at -4, arrow pointing LEFT

                Use WARNING colors (red/yellow) for the rule.
                Show counter-example to prove why reversal is needed.
                Make this rule MEMORABLE - it's a common mistake!
                """,
                "audience": "high school"
            },
            {
                "name": "2_7_04_multistep_inequality",
                "topic": "Multi-step linear inequalities",
                "requirements": """
                Solve 5 - 3x ≥ 17 step by step.
                Step 1: Subtract 5: -3x ≥ 12
                Step 2: Divide by -3 AND REVERSE: x ≤ -4
                Step 3: Graph: CLOSED circle at -4 (≤ means included)
                Step 4: Arrow pointing left

                Emphasize the closed vs open circle distinction.
                Show the sign reversal happening clearly.
                """,
                "audience": "high school"
            },
        ]
    }
}


def generate_animation(engine: MathContentEngine, section: str, anim_info: dict, output_dir: Path) -> bool:
    """Generate a single animation and save it."""
    name = anim_info["name"]
    topic = anim_info["topic"]
    requirements = anim_info["requirements"]
    audience = anim_info["audience"]

    logger.info(f"\n{'='*60}")
    logger.info(f"Generating: {name}")
    logger.info(f"Topic: {topic}")
    logger.info(f"{'='*60}")

    try:
        result = engine.generate(
            topic=topic,
            requirements=requirements,
            audience_level=audience,
            output_filename=name
        )

        if result.success:
            logger.info(f"✓ SUCCESS: {result.video_path}")
            logger.info(f"  Render time: {result.render_time:.2f}s")
            logger.info(f"  Attempts: {result.total_attempts}")

            # Save the generated code for reference
            code_path = output_dir / f"{name}.py"
            with open(code_path, 'w') as f:
                f.write(f"# {topic}\n")
                f.write(f"# Generated for Chapter 2 - Section {section}\n\n")
                f.write(result.code)
            logger.info(f"  Code saved: {code_path}")

            return True
        else:
            logger.error(f"✗ FAILED: {result.error_message}")

            # Save failed code for debugging
            failed_code_path = output_dir / f"{name}_FAILED.py"
            with open(failed_code_path, 'w') as f:
                f.write(f"# FAILED: {topic}\n")
                f.write(f"# Error: {result.error_message}\n\n")
                f.write(result.code)

            return False

    except Exception as e:
        logger.exception(f"Exception generating {name}: {e}")
        return False


def generate_section(engine: MathContentEngine, section_num: str, output_dir: Path):
    """Generate all animations for a specific section."""
    if section_num not in CHAPTER_2_ANIMATIONS:
        logger.error(f"Unknown section: {section_num}")
        return

    section = CHAPTER_2_ANIMATIONS[section_num]
    logger.info(f"\n{'#'*60}")
    logger.info(f"# Section {section_num}: {section['title']}")
    logger.info(f"{'#'*60}")

    results = []
    for anim_info in section["animations"]:
        success = generate_animation(engine, section_num, anim_info, output_dir)
        results.append((anim_info["name"], success))

    # Summary
    logger.info(f"\nSection {section_num} Summary:")
    for name, success in results:
        status = "✓" if success else "✗"
        logger.info(f"  {status} {name}")

    return results


def generate_all(engine: MathContentEngine, output_dir: Path):
    """Generate animations for all sections in Chapter 2."""
    all_results = {}

    for section_num in CHAPTER_2_ANIMATIONS:
        results = generate_section(engine, section_num, output_dir)
        all_results[section_num] = results

    # Final summary
    logger.info(f"\n{'='*60}")
    logger.info("CHAPTER 2 GENERATION COMPLETE")
    logger.info("="*60)

    total = 0
    success_count = 0
    for section_num, results in all_results.items():
        section_title = CHAPTER_2_ANIMATIONS[section_num]["title"]
        section_success = sum(1 for _, s in results if s)
        total += len(results)
        success_count += section_success
        logger.info(f"Section {section_num}: {section_success}/{len(results)} successful")

    logger.info(f"\nTotal: {success_count}/{total} animations generated successfully")

    return all_results


def main():
    parser = argparse.ArgumentParser(description="Generate Chapter 2 animations")
    parser.add_argument("--section", "-s", type=str, help="Specific section to generate (e.g., 2.1)")
    parser.add_argument("--list", "-l", action="store_true", help="List available animations")
    parser.add_argument("--output", "-o", type=str, default=str(OUTPUT_DIR), help="Output directory")

    args = parser.parse_args()

    if args.list:
        print("Chapter 2: Solving Linear Equations and Inequalities")
        print("="*60)
        for section_num, section in CHAPTER_2_ANIMATIONS.items():
            print(f"\nSection {section_num}: {section['title']}")
            for anim in section["animations"]:
                print(f"  - {anim['name']}: {anim['topic']}")
        return

    # Initialize engine
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    config = Config.from_env()
    config.output_dir = output_dir

    engine = MathContentEngine(config)

    if args.section:
        generate_section(engine, args.section, output_dir)
    else:
        generate_all(engine, output_dir)


if __name__ == "__main__":
    main()
