#!/usr/bin/env python3
"""
PDF to Personalized Textbook and Animation Pipeline.

This script implements the complete pipeline:
1. Parse PDF textbook using Mathpix (extract to markdown)
2. Generate personalized versions for student interests
3. Parse personalized textbooks to extract examples
4. Generate Manim animations for each example

Usage:
    # Full pipeline from PDF
    python pdf_to_personalized_pipeline.py \
        --pdf curriculum/textbooks/us/openstax_elementary_algebra_2e.pdf \
        --interest basketball gaming \
        --output-dir output/personalized_algebra \
        --page-range "1-50"

    # PDF to markdown only (no personalization)
    python pdf_to_personalized_pipeline.py \
        --pdf textbook.pdf \
        --output-markdown textbook.md \
        --page-range "10-30"

    # Skip PDF parsing (use existing markdown)
    python pdf_to_personalized_pipeline.py \
        --markdown textbook.md \
        --interest basketball \
        --output-dir output/basketball_textbook
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from math_content_engine.config import Config
from math_content_engine.personalization import (
    MathpixPDFParser,
    parse_textbook_pdf,
    get_interest_profile,
    list_available_interests,
)

# Import the existing personalized content pipeline
sys.path.insert(0, str(Path(__file__).parent))
from personalized_content_pipeline import run_pipeline, print_summary, PipelineResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_pdf_to_markdown(
    pdf_path: Path,
    output_markdown_path: Path,
    page_range: Optional[str] = None,
) -> bool:
    """
    Parse PDF textbook to markdown using Mathpix.

    Args:
        pdf_path: Path to PDF file
        output_markdown_path: Where to save markdown
        page_range: Optional page range (e.g., "1-50")

    Returns:
        True if successful
    """
    logger.info(f"\n{'='*70}")
    logger.info("STEP 1: PDF to Markdown Conversion (Mathpix)")
    logger.info("=" * 70)
    logger.info(f"PDF: {pdf_path}")
    logger.info(f"Output: {output_markdown_path}")
    if page_range:
        logger.info(f"Page range: {page_range}")

    try:
        parse_textbook_pdf(
            pdf_path=str(pdf_path),
            output_markdown_path=str(output_markdown_path),
            page_range=page_range
        )
        logger.info(f"✓ PDF successfully converted to markdown")
        return True
    except Exception as e:
        logger.exception(f"Failed to parse PDF: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Complete pipeline: PDF -> Markdown -> Personalized Textbook -> Animations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline from PDF to animations
  python pdf_to_personalized_pipeline.py \\
      --pdf textbook.pdf \\
      --interest basketball gaming \\
      --output-dir output/ \\
      --page-range "1-50"

  # PDF to markdown only
  python pdf_to_personalized_pipeline.py \\
      --pdf textbook.pdf \\
      --output-markdown textbook.md

  # Use existing markdown (skip PDF parsing)
  python pdf_to_personalized_pipeline.py \\
      --markdown textbook.md \\
      --interest basketball \\
      --output-dir output/

  # Preview mode (generate code only, no video rendering)
  python pdf_to_personalized_pipeline.py \\
      --pdf textbook.pdf \\
      --interest gaming \\
      --output-dir output/ \\
      --preview \\
      --max-examples 3
        """
    )

    # PDF Input
    parser.add_argument(
        "--pdf",
        type=str,
        help="Path to PDF textbook to parse"
    )
    parser.add_argument(
        "--page-range",
        type=str,
        help="Page range to parse from PDF (e.g., '1-50', '10-', '-30')"
    )
    parser.add_argument(
        "--output-markdown",
        type=str,
        help="Where to save parsed markdown (for PDF-only mode)"
    )

    # Markdown Input (alternative to PDF)
    parser.add_argument(
        "--markdown", "-m",
        type=str,
        help="Path to existing markdown textbook (skips PDF parsing)"
    )

    # Personalization
    parser.add_argument(
        "--interest", "-i",
        nargs="+",
        help="Interest(s) to personalize for (e.g., basketball, gaming, music)"
    )

    # Output
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        help="Output directory for personalized content and animations"
    )

    # Animation Options
    parser.add_argument(
        "--preview", "-p",
        action="store_true",
        help="Preview mode: generate code only, skip video rendering"
    )
    parser.add_argument(
        "--max-examples",
        type=int,
        help="Maximum number of examples to animate (default: all)"
    )

    # Utility
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
        print()
        return

    # Validate arguments
    if not args.pdf and not args.markdown:
        parser.error("Either --pdf or --markdown is required")

    if args.pdf and args.markdown:
        parser.error("Use either --pdf or --markdown, not both")

    # PDF-only mode: just convert to markdown
    if args.pdf and args.output_markdown and not args.interest:
        pdf_path = Path(args.pdf)
        if not pdf_path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            sys.exit(1)

        output_md = Path(args.output_markdown)
        success = parse_pdf_to_markdown(pdf_path, output_md, args.page_range)
        sys.exit(0 if success else 1)

    # Full pipeline mode: require interest and output-dir
    if not args.interest:
        parser.error("--interest is required for personalization/animation pipeline")
    if not args.output_dir:
        parser.error("--output-dir is required for full pipeline")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Parse PDF to markdown (if needed)
    if args.pdf:
        pdf_path = Path(args.pdf)
        if not pdf_path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            sys.exit(1)

        # Save markdown to output directory
        markdown_path = output_dir / f"{pdf_path.stem}.md"
        success = parse_pdf_to_markdown(pdf_path, markdown_path, args.page_range)

        if not success:
            logger.error("PDF parsing failed. Exiting.")
            sys.exit(1)

        textbook_path = markdown_path
    else:
        # Use existing markdown
        textbook_path = Path(args.markdown)
        if not textbook_path.exists():
            logger.error(f"Markdown file not found: {textbook_path}")
            sys.exit(1)

    # Step 2-4: Run personalization and animation pipeline
    logger.info(f"\n{'#'*70}")
    logger.info("STEP 2-4: Personalization and Animation Pipeline")
    logger.info("#" * 70)

    config = Config.from_env()
    results: List[PipelineResult] = []

    for interest in args.interest:
        logger.info(f"\n{'='*70}")
        logger.info(f"Processing interest: {interest}")
        logger.info("=" * 70)

        result = run_pipeline(
            textbook_path=textbook_path,
            personalized_textbook_path=None,
            interest=interest,
            output_dir=output_dir,
            config=config,
            preview_only=args.preview,
            max_examples=args.max_examples,
        )
        results.append(result)

    # Print final summary
    print_summary(results)

    # Exit with appropriate code
    any_errors = any(len(r.errors) > 0 for r in results)
    sys.exit(1 if any_errors else 0)


if __name__ == "__main__":
    main()
