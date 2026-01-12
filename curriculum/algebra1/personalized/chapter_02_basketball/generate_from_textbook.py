#!/usr/bin/env python3
"""
Generate animations directly from personalized textbook content.

This script reads the basketball-themed textbook and generates animations
that match the exact examples, equations, and context from the textbook.

Usage:
    python generate_from_textbook.py                    # Generate all examples
    python generate_from_textbook.py --section 2.1     # Generate for section 2.1
    python generate_from_textbook.py --preview         # Preview only (no rendering)
    python generate_from_textbook.py --list            # List all available examples
"""

import argparse
import logging
import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parents[4] / "src"))

from math_content_engine import MathContentEngine, Config
from math_content_engine.personalization.textbook_parser import TextbookParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
TEXTBOOK_PATH = Path(__file__).parents[2] / "textbooks" / "chapter_02_linear_equations_basketball.md"
OUTPUT_DIR = Path(__file__).parent


def list_examples(parser: TextbookParser):
    """List all examples from the textbook."""
    chapter = parser.parse()

    print(f"\n{'='*60}")
    print(f"Chapter {chapter.number}: {chapter.title}")
    print(f"Theme: {chapter.theme.upper()}")
    print(f"{'='*60}\n")

    for section in chapter.sections:
        print(f"\nSection {section.number}: {section.title}")
        print("-" * 40)
        for example in section.examples:
            print(f"  Example {example.example_number}: {example.title}")
            print(f"    Equation: {example.equation}")
            print(f"    Context: {example.context[:80]}...")
        print()


def generate_animations(
    parser: TextbookParser,
    output_dir: Path,
    section_filter: str = None,
    preview_only: bool = False
):
    """Generate animations from textbook examples."""

    chapter = parser.parse()
    animation_specs = parser.get_examples_for_animation()

    # Filter by section if specified
    if section_filter:
        animation_specs = [s for s in animation_specs if s['section'] == section_filter]

    if not animation_specs:
        logger.error(f"No examples found for section {section_filter}")
        return

    logger.info(f"Generating {len(animation_specs)} animations from textbook")
    logger.info(f"Theme: {chapter.theme.upper()}")
    logger.info(f"Output: {output_dir}")

    # Initialize engine with the detected theme
    config = Config.from_env()
    config.output_dir = output_dir

    engine = MathContentEngine(config, interest=chapter.theme)

    results = []

    for spec in animation_specs:
        section = spec['section']
        example_num = spec['example_num']
        topic = spec['topic']
        requirements = spec['requirements']

        # Create output filename
        output_name = f"textbook_{section.replace('.', '_')}_ex{example_num}_{chapter.theme}"

        logger.info(f"\n{'='*60}")
        logger.info(f"Generating: {output_name}")
        logger.info(f"Topic: {topic}")
        logger.info(f"Equation: {spec['equation']}")
        logger.info("="*60)

        try:
            if preview_only:
                # Just generate code
                result = engine.preview_code(
                    topic=topic,
                    requirements=requirements,
                    audience_level="high school"
                )

                # Save the code
                code_path = output_dir / f"{output_name}.py"
                with open(code_path, 'w') as f:
                    f.write(f"# Generated from textbook: {topic}\n")
                    f.write(f"# Section {section}, Example {example_num}\n")
                    f.write(f"# Theme: {chapter.theme}\n\n")
                    f.write(result.code)

                logger.info(f"  Code saved: {code_path}")
                results.append((output_name, True, str(code_path)))

            else:
                # Full generation with rendering
                result = engine.generate(
                    topic=topic,
                    requirements=requirements,
                    audience_level="high school",
                    output_filename=output_name
                )

                if result.success:
                    logger.info(f"  SUCCESS: {result.video_path}")
                    logger.info(f"  Duration: {result.render_time:.1f}s")
                    results.append((output_name, True, str(result.video_path)))

                    # Also save the code
                    code_path = output_dir / f"{output_name}.py"
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

    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("GENERATION COMPLETE")
    logger.info("="*60)

    success_count = sum(1 for _, success, _ in results if success)
    logger.info(f"Total: {success_count}/{len(results)} successful")

    for name, success, msg in results:
        status = "✓" if success else "✗"
        logger.info(f"  {status} {name}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Generate animations from personalized textbook content"
    )
    parser.add_argument(
        "--textbook", "-t",
        type=str,
        default=str(TEXTBOOK_PATH),
        help="Path to textbook markdown file"
    )
    parser.add_argument(
        "--section", "-s",
        type=str,
        help="Generate only for specific section (e.g., 2.1)"
    )
    parser.add_argument(
        "--preview", "-p",
        action="store_true",
        help="Preview only - generate code without rendering"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all examples from textbook"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=str(OUTPUT_DIR / "from_textbook"),
        help="Output directory"
    )

    args = parser.parse_args()

    # Check textbook exists
    textbook_path = Path(args.textbook)
    if not textbook_path.exists():
        logger.error(f"Textbook not found: {textbook_path}")
        sys.exit(1)

    # Parse textbook
    tb_parser = TextbookParser(str(textbook_path))

    if args.list:
        list_examples(tb_parser)
        return

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate animations
    generate_animations(
        parser=tb_parser,
        output_dir=output_dir,
        section_filter=args.section,
        preview_only=args.preview
    )


if __name__ == "__main__":
    main()
