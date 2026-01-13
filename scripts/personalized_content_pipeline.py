#!/usr/bin/env python3
"""
Personalized Content Pipeline.

This script implements the full pipeline for creating personalized math content:
1. Take a base textbook chapter and student interest
2. Generate a personalized textbook chapter
3. Parse the personalized textbook to extract examples
4. Generate Manim animations for each example

Usage:
    # Full pipeline: textbook -> personalized textbook -> animations
    python personalized_content_pipeline.py \
        --textbook curriculum/algebra1/textbooks/chapter_02_linear_equations.md \
        --interest basketball \
        --output-dir output/basketball_chapter_02

    # Use an existing personalized textbook (skip personalization step)
    python personalized_content_pipeline.py \
        --personalized-textbook curriculum/algebra1/textbooks/chapter_02_linear_equations_basketball.md \
        --output-dir output/basketball_chapter_02

    # Preview mode (generate code only, no video rendering)
    python personalized_content_pipeline.py \
        --textbook curriculum/algebra1/textbooks/chapter_02_linear_equations.md \
        --interest gaming \
        --output-dir output/gaming_chapter_02 \
        --preview

    # Generate for multiple interests
    python personalized_content_pipeline.py \
        --textbook curriculum/algebra1/textbooks/chapter_02_linear_equations.md \
        --interest basketball gaming music \
        --output-dir output/personalized

    # List available interests
    python personalized_content_pipeline.py --list-interests
"""

import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from math_content_engine import (
    MathContentEngine,
    Config,
)
from math_content_engine.personalization import (
    TextbookParser,
    get_interest_profile,
    list_available_interests,
)
from math_content_engine.llm import create_llm_client

# Import the textbook generator
from generate_personalized_textbook import (
    generate_personalized_textbook,
    personalize_textbook,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Result from the pipeline execution."""
    interest: str
    personalized_textbook_path: Optional[Path]
    animations_generated: int
    animations_successful: int
    animation_results: List[dict]
    errors: List[str]


def run_pipeline(
    textbook_path: Optional[Path],
    personalized_textbook_path: Optional[Path],
    interest: str,
    output_dir: Path,
    config: Config,
    preview_only: bool = False,
    max_examples: Optional[int] = None,
) -> PipelineResult:
    """
    Run the full personalized content pipeline.

    Args:
        textbook_path: Path to base textbook (will be personalized)
        personalized_textbook_path: Path to already personalized textbook (skip step 1)
        interest: Interest to personalize for
        output_dir: Output directory for all generated content
        config: Configuration
        preview_only: If True, only generate code without rendering
        max_examples: Maximum number of examples to process (None = all)

    Returns:
        PipelineResult with details of what was generated
    """
    errors = []
    animation_results = []

    # Validate interest
    profile = get_interest_profile(interest)
    if not profile:
        return PipelineResult(
            interest=interest,
            personalized_textbook_path=None,
            animations_generated=0,
            animations_successful=0,
            animation_results=[],
            errors=[f"Unknown interest: {interest}"]
        )

    logger.info(f"\n{'#'*70}")
    logger.info(f"# PERSONALIZED CONTENT PIPELINE")
    logger.info(f"# Interest: {profile.display_name}")
    logger.info(f"{'#'*70}\n")

    # Create output directory
    interest_output_dir = output_dir / interest
    interest_output_dir.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # STEP 1: Generate or use personalized textbook
    # =========================================================================
    logger.info("=" * 60)
    logger.info("STEP 1: Personalized Textbook")
    logger.info("=" * 60)

    if personalized_textbook_path:
        # Use existing personalized textbook
        if not personalized_textbook_path.exists():
            errors.append(f"Personalized textbook not found: {personalized_textbook_path}")
            return PipelineResult(
                interest=interest,
                personalized_textbook_path=None,
                animations_generated=0,
                animations_successful=0,
                animation_results=[],
                errors=errors
            )
        final_textbook_path = personalized_textbook_path
        logger.info(f"Using existing personalized textbook: {final_textbook_path}")
    else:
        # Generate personalized textbook
        if not textbook_path or not textbook_path.exists():
            errors.append(f"Base textbook not found: {textbook_path}")
            return PipelineResult(
                interest=interest,
                personalized_textbook_path=None,
                animations_generated=0,
                animations_successful=0,
                animation_results=[],
                errors=errors
            )

        final_textbook_path = interest_output_dir / f"textbook_{interest}.md"
        logger.info(f"Generating personalized textbook from: {textbook_path}")
        logger.info(f"Output will be saved to: {final_textbook_path}")

        try:
            success = generate_personalized_textbook(
                input_path=textbook_path,
                interest_name=interest,
                output_path=final_textbook_path,
                config=config
            )
            if not success:
                errors.append("Failed to generate personalized textbook")
                return PipelineResult(
                    interest=interest,
                    personalized_textbook_path=None,
                    animations_generated=0,
                    animations_successful=0,
                    animation_results=[],
                    errors=errors
                )
        except Exception as e:
            errors.append(f"Textbook generation error: {str(e)}")
            logger.exception("Failed to generate personalized textbook")
            return PipelineResult(
                interest=interest,
                personalized_textbook_path=None,
                animations_generated=0,
                animations_successful=0,
                animation_results=[],
                errors=errors
            )

    logger.info(f"Personalized textbook ready: {final_textbook_path}")

    # =========================================================================
    # STEP 2: Parse textbook to extract examples
    # =========================================================================
    logger.info("\n" + "=" * 60)
    logger.info("STEP 2: Parsing Textbook for Animation Examples")
    logger.info("=" * 60)

    try:
        parser = TextbookParser(str(final_textbook_path))
        chapter = parser.parse()
        animation_specs = parser.get_examples_for_animation()
    except Exception as e:
        errors.append(f"Textbook parsing error: {str(e)}")
        logger.exception("Failed to parse textbook")
        return PipelineResult(
            interest=interest,
            personalized_textbook_path=final_textbook_path,
            animations_generated=0,
            animations_successful=0,
            animation_results=[],
            errors=errors
        )

    logger.info(f"Found {len(animation_specs)} examples for animation")
    for spec in animation_specs[:5]:  # Show first 5
        logger.info(f"  - Section {spec['section']}: {spec['topic'][:50]}...")

    if max_examples:
        animation_specs = animation_specs[:max_examples]
        logger.info(f"Limiting to first {max_examples} examples")

    # =========================================================================
    # STEP 3: Generate animations for each example
    # =========================================================================
    logger.info("\n" + "=" * 60)
    logger.info("STEP 3: Generating Animations")
    logger.info("=" * 60)

    # Initialize the engine with personalization
    config.output_dir = interest_output_dir / "videos"
    config.output_dir.mkdir(parents=True, exist_ok=True)

    engine = MathContentEngine(config, interest=interest)

    animations_generated = 0
    animations_successful = 0

    for i, spec in enumerate(animation_specs, 1):
        section = spec['section']
        example_num = spec.get('example_num', i)
        topic = spec['topic']
        requirements = spec['requirements']

        output_name = f"section_{section.replace('.', '_')}_example_{example_num}_{interest}"

        logger.info(f"\n{'─'*50}")
        logger.info(f"Animation {i}/{len(animation_specs)}: {topic[:50]}...")
        logger.info(f"Output: {output_name}")
        logger.info("─" * 50)

        try:
            if preview_only:
                # Generate code only
                result = engine.preview_code(
                    topic=topic,
                    requirements=requirements,
                    audience_level="high school"
                )

                # Save the generated code
                code_dir = interest_output_dir / "code"
                code_dir.mkdir(parents=True, exist_ok=True)
                code_path = code_dir / f"{output_name}.py"

                with open(code_path, 'w') as f:
                    f.write(f"# {topic}\n")
                    f.write(f"# Section {section}, Example {example_num}\n")
                    f.write(f"# Interest: {profile.display_name}\n\n")
                    f.write(result.code)

                logger.info(f"  Code saved: {code_path}")
                animations_generated += 1
                animations_successful += 1
                animation_results.append({
                    'name': output_name,
                    'success': True,
                    'path': str(code_path),
                    'type': 'code'
                })
            else:
                # Full generation and rendering
                result = engine.generate(
                    topic=topic,
                    requirements=requirements,
                    audience_level="high school",
                    output_filename=output_name
                )

                animations_generated += 1

                if result.success:
                    logger.info(f"  SUCCESS: {result.video_path}")
                    animations_successful += 1
                    animation_results.append({
                        'name': output_name,
                        'success': True,
                        'path': str(result.video_path),
                        'type': 'video'
                    })
                else:
                    logger.error(f"  FAILED: {result.error_message}")
                    animation_results.append({
                        'name': output_name,
                        'success': False,
                        'error': result.error_message,
                        'type': 'video'
                    })
                    errors.append(f"Animation failed for {output_name}: {result.error_message}")

        except Exception as e:
            logger.exception(f"  ERROR: {e}")
            animations_generated += 1
            animation_results.append({
                'name': output_name,
                'success': False,
                'error': str(e),
                'type': 'unknown'
            })
            errors.append(f"Exception for {output_name}: {str(e)}")

    return PipelineResult(
        interest=interest,
        personalized_textbook_path=final_textbook_path,
        animations_generated=animations_generated,
        animations_successful=animations_successful,
        animation_results=animation_results,
        errors=errors
    )


def print_summary(results: List[PipelineResult]):
    """Print a summary of all pipeline results."""
    print("\n" + "=" * 70)
    print("PIPELINE SUMMARY")
    print("=" * 70)

    total_generated = 0
    total_successful = 0

    for result in results:
        print(f"\n{result.interest.upper()}")
        print("-" * 40)
        print(f"  Textbook: {result.personalized_textbook_path or 'FAILED'}")
        print(f"  Animations: {result.animations_successful}/{result.animations_generated} successful")

        total_generated += result.animations_generated
        total_successful += result.animations_successful

        if result.errors:
            print(f"  Errors: {len(result.errors)}")
            for error in result.errors[:3]:
                print(f"    - {error[:60]}...")

    print("\n" + "=" * 70)
    print(f"TOTAL: {total_successful}/{total_generated} animations successful")
    print(f"       across {len(results)} interest(s)")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Full pipeline: textbook -> personalization -> animations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline with base textbook
  python personalized_content_pipeline.py \\
      --textbook chapter_02.md --interest basketball --output-dir output/

  # Use existing personalized textbook
  python personalized_content_pipeline.py \\
      --personalized-textbook chapter_02_basketball.md --output-dir output/

  # Preview mode (code only, no video rendering)
  python personalized_content_pipeline.py \\
      --textbook chapter_02.md --interest gaming --preview --output-dir output/

  # Multiple interests at once
  python personalized_content_pipeline.py \\
      --textbook chapter_02.md --interest basketball gaming music --output-dir output/
        """
    )

    parser.add_argument(
        "--textbook", "-t",
        type=str,
        help="Path to base textbook markdown file (will be personalized)"
    )
    parser.add_argument(
        "--personalized-textbook",
        type=str,
        help="Path to already personalized textbook (skips personalization step)"
    )
    parser.add_argument(
        "--interest", "-i",
        nargs="+",
        help="Interest(s) to personalize for (e.g., basketball, gaming, music)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        required=True,
        help="Output directory for all generated content"
    )
    parser.add_argument(
        "--preview", "-p",
        action="store_true",
        help="Preview mode: generate code only, skip video rendering"
    )
    parser.add_argument(
        "--max-examples",
        type=int,
        help="Maximum number of examples to process (default: all)"
    )
    parser.add_argument(
        "--list-interests", "-l",
        action="store_true",
        help="List all available interests and exit"
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

                # Show diversity stats
                stats = []
                if hasattr(profile, 'fun_facts') and profile.fun_facts:
                    stats.append(f"{len(profile.fun_facts)} fun facts")
                if hasattr(profile, 'cultural_references') and profile.cultural_references:
                    stats.append(f"{len(profile.cultural_references)} cultural refs")
                if hasattr(profile, 'motivational_quotes') and profile.motivational_quotes:
                    stats.append(f"{len(profile.motivational_quotes)} quotes")
                if stats:
                    print(f"    Content: {', '.join(stats)}")
        print()
        return

    # Validate arguments
    if not args.personalized_textbook and not args.textbook:
        parser.error("Either --textbook or --personalized-textbook is required")

    if args.personalized_textbook and args.textbook:
        parser.error("Use either --textbook or --personalized-textbook, not both")

    if args.textbook and not args.interest:
        parser.error("--interest is required when using --textbook")

    # Determine interests to process
    if args.personalized_textbook:
        # When using existing personalized textbook, detect interest from filename or use default
        textbook_name = Path(args.personalized_textbook).stem
        detected_interest = None
        for interest_name in list_available_interests():
            if interest_name in textbook_name.lower():
                detected_interest = interest_name
                break
        interests = [detected_interest] if detected_interest else ['general']
    else:
        interests = args.interest

    # Load configuration
    config = Config.from_env()

    # Process pipeline for each interest
    results = []
    output_dir = Path(args.output_dir)

    for interest in interests:
        logger.info(f"\n{'#'*70}")
        logger.info(f"# Processing interest: {interest}")
        logger.info(f"{'#'*70}\n")

        result = run_pipeline(
            textbook_path=Path(args.textbook) if args.textbook else None,
            personalized_textbook_path=Path(args.personalized_textbook) if args.personalized_textbook else None,
            interest=interest,
            output_dir=output_dir,
            config=config,
            preview_only=args.preview,
            max_examples=args.max_examples,
        )
        results.append(result)

    # Print final summary
    print_summary(results)


if __name__ == "__main__":
    main()
