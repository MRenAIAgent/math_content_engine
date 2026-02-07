#!/usr/bin/env python3
"""
Simple PDF to Markdown Parser Script.

This script uses Mathpix API to parse PDF textbooks to markdown format.
Use this to check parser results before running the full pipeline.

Usage:
    # Parse entire PDF
    python parse_pdf.py input.pdf output.md

    # Parse specific pages
    python parse_pdf.py input.pdf output.md --page-range "1-50"

    # Parse with verbose output
    python parse_pdf.py input.pdf output.md --page-range "10-30" --verbose
"""

import argparse
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from math_content_engine.personalization import parse_textbook_pdf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Parse PDF textbooks to markdown using Mathpix API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse entire PDF
  python parse_pdf.py textbook.pdf textbook.md

  # Parse first 50 pages
  python parse_pdf.py textbook.pdf chapter1.md --page-range "1-50"

  # Parse pages 20-40
  python parse_pdf.py textbook.pdf chapter2.md --page-range "20-40"

  # Parse from page 10 to end
  python parse_pdf.py textbook.pdf remainder.md --page-range "10-"

Page Range Format:
  "N-M"  : Pages N through M (e.g., "1-50")
  "N-"   : Page N to end (e.g., "10-")
  "-M"   : Start to page M (e.g., "-30")
  "N"    : Single page N (e.g., "25")

Requirements:
  - MATHPIX_APP_ID and MATHPIX_APP_KEY must be set in .env file
  - pip install -e ".[pdf]"
        """
    )

    parser.add_argument(
        "pdf_path",
        type=str,
        help="Path to input PDF file"
    )
    parser.add_argument(
        "output_path",
        type=str,
        help="Path to output markdown file"
    )
    parser.add_argument(
        "--page-range", "-p",
        type=str,
        help="Page range to parse (e.g., '1-50', '10-', '-30')"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate input
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        logger.error(f"PDF file not found: {pdf_path}")
        sys.exit(1)

    if not pdf_path.suffix.lower() == '.pdf':
        logger.error(f"Input file is not a PDF: {pdf_path}")
        sys.exit(1)

    output_path = Path(args.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Parse PDF
    logger.info("=" * 70)
    logger.info("PDF to Markdown Parser (Mathpix)")
    logger.info("=" * 70)
    logger.info(f"Input PDF: {pdf_path}")
    logger.info(f"Output: {output_path}")
    if args.page_range:
        logger.info(f"Page range: {args.page_range}")
    else:
        logger.info("Page range: ALL PAGES")
    logger.info("=" * 70)

    try:
        markdown = parse_textbook_pdf(
            pdf_path=str(pdf_path),
            output_markdown_path=str(output_path),
            page_range=args.page_range
        )

        # Print summary
        logger.info("\n" + "=" * 70)
        logger.info("SUCCESS")
        logger.info("=" * 70)
        logger.info(f"✓ PDF parsed successfully")
        logger.info(f"✓ Output saved to: {output_path}")
        logger.info(f"✓ Markdown size: {len(markdown):,} characters")
        logger.info(f"✓ Lines: {markdown.count(chr(10)):,}")

        # Preview first few lines
        lines = markdown.split('\n')
        logger.info(f"\nFirst 10 lines:")
        logger.info("-" * 70)
        for line in lines[:10]:
            logger.info(line[:100])  # Truncate long lines

        logger.info("\n" + "=" * 70)
        logger.info(f"Check the full output at: {output_path}")
        logger.info("=" * 70)

        sys.exit(0)

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("\nMake sure you have set MATHPIX_APP_ID and MATHPIX_APP_KEY in .env file")
        sys.exit(1)
    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        sys.exit(1)
    except TimeoutError as e:
        logger.error(f"Timeout error: {e}")
        logger.error("PDF conversion took too long. Try a smaller page range.")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Failed to parse PDF: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
