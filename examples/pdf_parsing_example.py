#!/usr/bin/env python3
"""
Example: PDF Parsing with Mathpix

This example demonstrates how to parse PDF textbooks using the Mathpix API
and integrate with the personalization pipeline.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from math_content_engine.personalization import (
    MathpixPDFParser,
    parse_textbook_pdf,
    TextbookParser,
)
from math_content_engine import MathContentEngine, Config


def example_1_simple_parsing():
    """Example 1: Simple PDF to markdown conversion."""
    print("\n" + "="*70)
    print("Example 1: Simple PDF Parsing")
    print("="*70)

    # Parse PDF to markdown (convenience function)
    markdown = parse_textbook_pdf(
        pdf_path="curriculum/textbooks/us/openstax_elementary_algebra_2e.pdf",
        output_markdown_path="output/algebra_textbook.md",
        page_range="1-50"  # Only first 50 pages
    )

    print(f"✓ Parsed {len(markdown)} characters of markdown")
    print(f"✓ Saved to: output/algebra_textbook.md")


def example_2_advanced_parsing():
    """Example 2: Advanced parsing with custom options."""
    print("\n" + "="*70)
    print("Example 2: Advanced Parsing Options")
    print("="*70)

    # Initialize parser from environment
    parser = MathpixPDFParser.from_env()

    # Parse with custom options
    result = parser.parse_pdf(
        pdf_path="curriculum/textbooks/us/openstax_elementary_algebra_2e.pdf",
        page_range="10-30",
        conversion_formats={
            "md": True,      # Markdown
            "docx": True,    # MS Word
        },
        enable_tables_fallback=True,
        enable_spell_check=True,
        output_dir="output/parsed"
    )

    print(f"✓ Conversion status: {result['status']}")
    print(f"✓ Markdown URL: {result.get('md', 'N/A')}")
    print(f"✓ DOCX URL: {result.get('docx', 'N/A')}")


def example_3_full_pipeline():
    """Example 3: PDF to personalized animations pipeline."""
    print("\n" + "="*70)
    print("Example 3: Full Pipeline (PDF → Personalization → Animations)")
    print("="*70)

    # Step 1: Parse PDF to markdown
    print("\n[1/4] Parsing PDF to markdown...")
    markdown_path = "output/textbook.md"
    parse_textbook_pdf(
        pdf_path="curriculum/textbooks/us/openstax_elementary_algebra_2e.pdf",
        output_markdown_path=markdown_path,
        page_range="20-30"  # One chapter
    )
    print("✓ PDF parsed to markdown")

    # Step 2: Parse textbook structure
    print("\n[2/4] Parsing textbook structure...")
    parser = TextbookParser(markdown_path)
    chapter = parser.parse()
    print(f"✓ Found chapter: {chapter.title}")
    print(f"✓ Sections: {len(chapter.sections)}")

    # Step 3: Get animation specs
    print("\n[3/4] Extracting animation examples...")
    animation_specs = parser.get_examples_for_animation()
    print(f"✓ Found {len(animation_specs)} examples for animation")

    # Step 4: Generate animations (just first 2 examples)
    print("\n[4/4] Generating personalized animations...")
    config = Config.from_env()
    engine = MathContentEngine(config, interest="basketball")

    for i, spec in enumerate(animation_specs[:2], 1):
        print(f"\n  Generating animation {i}/2: {spec['topic']}")
        result = engine.generate(
            topic=spec['topic'],
            requirements=spec['requirements'],
            output_filename=f"basketball_example_{i}"
        )

        if result.success:
            print(f"  ✓ Success: {result.video_path}")
        else:
            print(f"  ✗ Failed: {result.error_message}")


def example_4_batch_processing():
    """Example 4: Batch process multiple chapters."""
    print("\n" + "="*70)
    print("Example 4: Batch Processing Multiple Chapters")
    print("="*70)

    chapters = [
        ("Chapter 1", "1-20"),
        ("Chapter 2", "21-40"),
        ("Chapter 3", "41-60"),
    ]

    parser = MathpixPDFParser.from_env()

    for chapter_name, page_range in chapters:
        print(f"\nProcessing {chapter_name} (pages {page_range})...")

        output_path = f"output/{chapter_name.lower().replace(' ', '_')}.md"

        try:
            markdown = parser.parse_pdf_to_markdown(
                pdf_path="curriculum/textbooks/us/openstax_elementary_algebra_2e.pdf",
                page_range=page_range,
                save_to_file=output_path
            )
            print(f"✓ {chapter_name} saved to {output_path}")
        except Exception as e:
            print(f"✗ Failed: {e}")


def example_5_error_handling():
    """Example 5: Proper error handling."""
    print("\n" + "="*70)
    print("Example 5: Error Handling")
    print("="*70)

    parser = MathpixPDFParser.from_env()

    try:
        result = parser.parse_pdf(
            pdf_path="nonexistent.pdf",
            page_range="1-10"
        )
    except FileNotFoundError as e:
        print(f"✗ File error: {e}")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
    except TimeoutError as e:
        print(f"✗ Timeout: {e}")
    except RuntimeError as e:
        print(f"✗ Conversion failed: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def main():
    """Run examples."""
    print("\n" + "="*70)
    print("PDF Parsing Examples with Mathpix")
    print("="*70)
    print("\nNOTE: These examples require:")
    print("  1. MATHPIX_APP_ID and MATHPIX_APP_KEY in .env")
    print("  2. Valid PDF files in curriculum/textbooks/")
    print("  3. pip install -e '.[pdf]'")

    examples = [
        ("Simple parsing", example_1_simple_parsing),
        ("Advanced options", example_2_advanced_parsing),
        ("Full pipeline", example_3_full_pipeline),
        ("Batch processing", example_4_batch_processing),
        ("Error handling", example_5_error_handling),
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nRun with: python examples/pdf_parsing_example.py")
    print("Or edit this file to run specific examples")

    # Uncomment to run examples:
    # example_1_simple_parsing()
    # example_2_advanced_parsing()
    # example_3_full_pipeline()
    # example_4_batch_processing()
    # example_5_error_handling()


if __name__ == "__main__":
    main()
