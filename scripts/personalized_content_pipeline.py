#!/usr/bin/env python3
"""
Personalized Content Pipeline.

Full E2E pipeline: PDF -> Markdown -> Concept Extraction -> Personalization -> Animation.
Each stage can be run independently via CLI flags.

Usage:
    # Full E2E with concept extraction
    python personalized_content_pipeline.py \\
        --pdf textbook.pdf --interest basketball --output-dir output/ \\
        --extract-concepts --page-range "1-50"

    # Markdown -> personalize -> animate (default full pipeline)
    python personalized_content_pipeline.py \\
        --textbook chapter_02.md --interest basketball --output-dir output/

    # PDF to markdown only
    python personalized_content_pipeline.py \\
        --pdf textbook.pdf --pdf-only --output-markdown textbook.md

    # Extract concepts only (view what's in a chapter)
    python personalized_content_pipeline.py \\
        --textbook chapter_02.md --concepts-only

    # Personalize only (no animation)
    python personalized_content_pipeline.py \\
        --textbook chapter_02.md --interest basketball --output-dir output/ \\
        --skip-animation

    # Re-run animation from previous output (tuning)
    python personalized_content_pipeline.py \\
        --personalized-textbook output/basketball/03_personalized/textbook_basketball.md \\
        --output-dir output/v2/ --max-examples 3

    # Animate without personalization
    python personalized_content_pipeline.py \\
        --textbook chapter_02.md --skip-personalize --output-dir output/

    # List available interests
    python personalized_content_pipeline.py --list-interests
"""

import argparse
import json
import logging
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from math_content_engine import MathContentEngine, Config
from math_content_engine.knowledge_graph import ConceptExtractor, ConceptExtractionResult
from math_content_engine.llm import create_llm_client
from math_content_engine.personalization import (
    TextbookParser,
    get_interest_profile,
    list_available_interests,
    parse_textbook_pdf,
)

# Import the textbook generator
from generate_personalized_textbook import (
    generate_personalized_textbook,
    personalize_textbook,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PIPELINE_VERSION = "2.0"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class PipelineResult:
    """Result from the pipeline execution."""

    interest: str
    pdf_path: Optional[Path] = None
    markdown_path: Optional[Path] = None
    personalized_textbook_path: Optional[Path] = None
    animations_generated: int = 0
    animations_successful: int = 0
    animation_results: List[dict] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    concept_extraction: Optional[ConceptExtractionResult] = None
    manifest_path: Optional[Path] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log_step(num: int, title: str):
    """Log a pipeline step header."""
    logger.info(f"\n{'=' * 60}")
    logger.info(f"STEP {num}: {title}")
    logger.info("=" * 60)


def write_manifest(output_dir: Path, config: Config, interest: str, steps: dict):
    """Write provenance manifest.json."""
    manifest = {
        "pipeline_version": PIPELINE_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "config": {
            "llm_provider": config.llm_provider.value,
            "model": config.get_model(),
            "video_quality": config.video_quality.value,
            "animation_style": config.animation_style.value,
        },
        "interest": interest,
        "steps": steps,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    logger.info(f"Manifest saved: {manifest_path}")
    return manifest_path


# ---------------------------------------------------------------------------
# Pipeline steps
# ---------------------------------------------------------------------------

def parse_pdf_step(
    pdf_path: Path,
    output_markdown_path: Path,
    page_range: Optional[str] = None,
) -> bool:
    """Parse PDF to markdown using Mathpix. Returns True on success."""
    log_step(0, "PDF to Markdown (Mathpix)")
    logger.info(f"PDF: {pdf_path}")
    logger.info(f"Output: {output_markdown_path}")
    if page_range:
        logger.info(f"Page range: {page_range}")

    try:
        parse_textbook_pdf(
            pdf_path=str(pdf_path),
            output_markdown_path=str(output_markdown_path),
            page_range=page_range,
        )
        logger.info("PDF successfully converted to markdown")
        return True
    except Exception as e:
        logger.exception(f"Failed to parse PDF: {e}")
        return False


def extract_concepts_step(
    markdown_path: Path,
    config: Config,
    output_path: Optional[Path] = None,
) -> tuple:
    """
    Extract concepts from markdown via LLM + knowledge graph.

    Returns:
        (ConceptExtractionResult, errors_list)
    """
    log_step(1, "Concept Extraction (Knowledge Graph)")
    logger.info(f"Analyzing: {markdown_path}")

    errors = []
    try:
        llm_client = create_llm_client(config)
        extractor = ConceptExtractor(llm_client=llm_client)

        content = markdown_path.read_text(encoding="utf-8")
        result = extractor.extract_concepts(content)

        # Display results
        logger.info(f"\n{result.display()}")

        # Save to JSON if output path provided
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                json.dumps(result.to_dict(), indent=2), encoding="utf-8"
            )
            logger.info(f"Concepts saved: {output_path}")

        if result.error:
            errors.append(f"Concept extraction warning: {result.error}")

        return result, errors
    except Exception as e:
        logger.exception("Concept extraction failed")
        errors.append(f"Concept extraction error: {str(e)}")
        return ConceptExtractionResult(error=str(e)), errors


def personalize_step(
    textbook_path: Path,
    interest: str,
    output_path: Path,
    config: Config,
) -> tuple:
    """
    Personalize textbook for an interest.

    Returns:
        (output_path or None, errors_list)
    """
    log_step(2, f"Personalize Textbook ({interest})")
    logger.info(f"Input: {textbook_path}")
    logger.info(f"Output: {output_path}")

    errors = []
    try:
        success = generate_personalized_textbook(
            input_path=textbook_path,
            interest_name=interest,
            output_path=output_path,
            config=config,
        )
        if not success:
            errors.append("Failed to generate personalized textbook")
            return None, errors
        logger.info(f"Personalized textbook saved: {output_path}")
        return output_path, errors
    except Exception as e:
        logger.exception("Personalization failed")
        errors.append(f"Personalization error: {str(e)}")
        return None, errors


def parse_examples_step(textbook_path: Path) -> tuple:
    """
    Parse textbook to extract animation examples.

    Returns:
        (animation_specs_list, errors_list)
    """
    log_step(3, "Parse Textbook for Animation Examples")
    logger.info(f"Parsing: {textbook_path}")

    errors = []
    try:
        parser = TextbookParser(str(textbook_path))
        parser.parse()
        specs = parser.get_examples_for_animation()
        logger.info(f"Found {len(specs)} examples for animation")
        for spec in specs[:5]:
            logger.info(f"  - Section {spec['section']}: {spec['topic'][:50]}...")
        return specs, errors
    except Exception as e:
        logger.exception("Textbook parsing failed")
        errors.append(f"Textbook parsing error: {str(e)}")
        return [], errors


def animate_step(
    animation_specs: List[dict],
    interest: str,
    output_dir: Path,
    config: Config,
    preview_only: bool = False,
    max_examples: Optional[int] = None,
) -> tuple:
    """
    Generate animations from specs.

    Returns:
        (generated_count, successful_count, results_list, errors_list)
    """
    log_step(4, "Generate Animations")

    profile = get_interest_profile(interest) if interest else None
    display_name = profile.display_name if profile else "general"

    if max_examples:
        animation_specs = animation_specs[:max_examples]
        logger.info(f"Limiting to {max_examples} examples")

    # Set up engine output dirs
    code_dir = output_dir / "code"
    video_dir = output_dir / "videos"
    code_dir.mkdir(parents=True, exist_ok=True)
    video_dir.mkdir(parents=True, exist_ok=True)

    config.output_dir = video_dir

    engine = MathContentEngine(config, interest=interest)

    generated = 0
    successful = 0
    results = []
    errors = []

    for i, spec in enumerate(animation_specs, 1):
        section = spec["section"]
        example_num = spec.get("example_num", i)
        topic = spec["topic"]
        requirements = spec["requirements"]
        suffix = f"_{interest}" if interest else ""
        output_name = f"section_{section.replace('.', '_')}_example_{example_num}{suffix}"

        logger.info(f"\nAnimation {i}/{len(animation_specs)}: {topic[:50]}...")

        try:
            if preview_only:
                result = engine.preview_code(
                    topic=topic, requirements=requirements, audience_level="high school"
                )
                code_path = code_dir / f"{output_name}.py"
                code_path.write_text(
                    f"# {topic}\n# Section {section}, Example {example_num}\n"
                    f"# Interest: {display_name}\n\n{result.code}",
                    encoding="utf-8",
                )
                logger.info(f"  Code saved: {code_path}")
                generated += 1
                successful += 1
                results.append({"name": output_name, "success": True, "path": str(code_path), "type": "code"})
            else:
                result = engine.generate(
                    topic=topic, requirements=requirements,
                    audience_level="high school", output_filename=output_name,
                )
                generated += 1
                if result.success:
                    logger.info(f"  SUCCESS: {result.video_path}")
                    successful += 1
                    results.append({"name": output_name, "success": True, "path": str(result.video_path), "type": "video"})
                else:
                    logger.error(f"  FAILED: {result.error_message}")
                    results.append({"name": output_name, "success": False, "error": result.error_message, "type": "video"})
                    errors.append(f"Animation failed: {output_name}")
        except Exception as e:
            logger.exception(f"  ERROR: {e}")
            generated += 1
            results.append({"name": output_name, "success": False, "error": str(e), "type": "unknown"})
            errors.append(f"Exception: {output_name}: {str(e)}")

    return generated, successful, results, errors


# ---------------------------------------------------------------------------
# Main pipeline orchestrator
# ---------------------------------------------------------------------------

def run_pipeline(
    pdf_path: Optional[Path],
    textbook_path: Optional[Path],
    personalized_textbook_path: Optional[Path],
    interest: str,
    output_dir: Path,
    config: Config,
    preview_only: bool = False,
    max_examples: Optional[int] = None,
    page_range: Optional[str] = None,
    extract_concepts: bool = False,
    skip_personalize: bool = False,
    skip_animation: bool = False,
) -> PipelineResult:
    """Run the personalized content pipeline with configurable stages."""
    result = PipelineResult(interest=interest, pdf_path=pdf_path)
    manifest_steps = {}

    profile = get_interest_profile(interest) if interest else None
    if interest and not profile and not skip_personalize:
        result.errors.append(f"Unknown interest: {interest}")
        return result

    interest_label = interest or "general"
    interest_output_dir = output_dir / interest_label
    interest_output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"\n{'#' * 70}")
    logger.info(f"# PERSONALIZED CONTENT PIPELINE")
    if profile:
        logger.info(f"# Interest: {profile.display_name}")
    logger.info(f"# Output:   {interest_output_dir}")
    logger.info(f"{'#' * 70}\n")

    # -- Copy source to 00_source/ for reference --
    source_dir = interest_output_dir / "00_source"
    source_dir.mkdir(parents=True, exist_ok=True)
    source_file = textbook_path or personalized_textbook_path
    if source_file and source_file.exists():
        shutil.copy2(source_file, source_dir / source_file.name)

    # -- STEP 0: Parse PDF to markdown (if PDF provided) --
    if pdf_path:
        parsed_dir = interest_output_dir / "01_parsed"
        parsed_dir.mkdir(parents=True, exist_ok=True)
        parsed_md = parsed_dir / f"{pdf_path.stem}.md"

        if not parse_pdf_step(pdf_path, parsed_md, page_range):
            result.errors.append("Failed to parse PDF to markdown")
            return result

        result.markdown_path = parsed_md
        textbook_path = parsed_md
        manifest_steps["parse_pdf"] = {
            "input": str(pdf_path),
            "page_range": page_range,
            "output": str(parsed_md),
        }

    # -- STEP 1: Concept extraction (optional) --
    if extract_concepts and textbook_path:
        concepts_dir = interest_output_dir / "02_concepts"
        concepts_json = concepts_dir / "concepts.json"

        concept_result, concept_errors = extract_concepts_step(
            markdown_path=textbook_path, config=config, output_path=concepts_json,
        )
        result.concept_extraction = concept_result
        result.errors.extend(concept_errors)

        manifest_steps["extract_concepts"] = {
            "input": str(textbook_path),
            "matched": len(concept_result.matched_concepts),
            "new": len(concept_result.new_concepts),
            "output": str(concepts_json),
        }

    # -- STEP 2: Personalize textbook --
    if personalized_textbook_path:
        if not personalized_textbook_path.exists():
            result.errors.append(f"Personalized textbook not found: {personalized_textbook_path}")
            return result
        final_textbook = personalized_textbook_path
        logger.info(f"Using existing personalized textbook: {final_textbook}")
    elif skip_personalize:
        if not textbook_path or not textbook_path.exists():
            result.errors.append(f"Textbook not found: {textbook_path}")
            return result
        final_textbook = textbook_path
        logger.info(f"Skipping personalization, using: {final_textbook}")
    else:
        if not textbook_path or not textbook_path.exists():
            result.errors.append(f"Base textbook not found: {textbook_path}")
            return result

        pers_dir = interest_output_dir / "03_personalized"
        pers_dir.mkdir(parents=True, exist_ok=True)
        pers_output = pers_dir / f"textbook_{interest_label}.md"

        pers_path, pers_errors = personalize_step(
            textbook_path, interest, pers_output, config,
        )
        result.errors.extend(pers_errors)
        if not pers_path:
            return result

        final_textbook = pers_path
        manifest_steps["personalize"] = {
            "input": str(textbook_path),
            "interest": interest,
            "output": str(pers_output),
        }

    result.personalized_textbook_path = final_textbook

    if skip_animation:
        result.manifest_path = write_manifest(
            interest_output_dir, config, interest_label, manifest_steps,
        )
        return result

    # -- STEP 3: Parse examples --
    specs, parse_errors = parse_examples_step(final_textbook)
    result.errors.extend(parse_errors)
    if not specs:
        result.manifest_path = write_manifest(
            interest_output_dir, config, interest_label, manifest_steps,
        )
        return result

    # -- STEP 4: Generate animations --
    anim_dir = interest_output_dir / "04_animations"
    generated, successful, anim_results, anim_errors = animate_step(
        animation_specs=specs,
        interest=interest,
        output_dir=anim_dir,
        config=config,
        preview_only=preview_only,
        max_examples=max_examples,
    )
    result.animations_generated = generated
    result.animations_successful = successful
    result.animation_results = anim_results
    result.errors.extend(anim_errors)

    manifest_steps["animate"] = {
        "examples_found": len(specs),
        "generated": generated,
        "successful": successful,
        "preview_only": preview_only,
        "output_dir": str(anim_dir),
    }

    result.manifest_path = write_manifest(
        interest_output_dir, config, interest_label, manifest_steps,
    )
    return result


# ---------------------------------------------------------------------------
# Summary display
# ---------------------------------------------------------------------------

def print_summary(results: List[PipelineResult]):
    """Print a summary of all pipeline results with artifact paths."""
    print(f"\n{'=' * 70}")
    print("PIPELINE SUMMARY")
    print("=" * 70)

    total_generated = 0
    total_successful = 0

    for r in results:
        print(f"\n{r.interest.upper()}")
        print("-" * 40)

        if r.markdown_path:
            print(f"  Parsed MD:    {r.markdown_path}")
        if r.concept_extraction and r.concept_extraction.matched_concepts:
            matched = len(r.concept_extraction.matched_concepts)
            new = len(r.concept_extraction.new_concepts)
            print(f"  Concepts:     {matched} matched, {new} new")
        if r.personalized_textbook_path:
            print(f"  Textbook:     {r.personalized_textbook_path}")
        if r.animations_generated > 0:
            print(f"  Animations:   {r.animations_successful}/{r.animations_generated} successful")
        if r.manifest_path:
            print(f"  Manifest:     {r.manifest_path}")

        total_generated += r.animations_generated
        total_successful += r.animations_successful

        if r.errors:
            print(f"  Errors ({len(r.errors)}):")
            for err in r.errors[:3]:
                print(f"    - {err[:70]}...")

    print(f"\n{'=' * 70}")
    if total_generated > 0:
        print(f"TOTAL: {total_successful}/{total_generated} animations across {len(results)} interest(s)")
    else:
        print(f"Pipeline completed for {len(results)} interest(s)")
    print("=" * 70)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        description="E2E pipeline: PDF -> Markdown -> Concepts -> Personalization -> Animation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full E2E with concept extraction
  python personalized_content_pipeline.py \\
      --pdf textbook.pdf --interest basketball --output-dir output/ \\
      --extract-concepts --page-range "1-50"

  # PDF to markdown only
  python personalized_content_pipeline.py \\
      --pdf textbook.pdf --pdf-only --output-markdown textbook.md

  # Extract concepts only (inspect a chapter)
  python personalized_content_pipeline.py \\
      --textbook chapter_02.md --concepts-only

  # Personalize only (no animation)
  python personalized_content_pipeline.py \\
      --textbook chapter_02.md --interest basketball \\
      --output-dir output/ --skip-animation

  # Re-run animation from previous output
  python personalized_content_pipeline.py \\
      --personalized-textbook output/basketball/03_personalized/textbook_basketball.md \\
      --output-dir output/v2/ --max-examples 3

  # Multiple interests
  python personalized_content_pipeline.py \\
      --textbook chapter_02.md --interest basketball gaming music --output-dir output/
        """,
    )

    # Input sources
    inp = parser.add_argument_group("Input sources (use one)")
    inp.add_argument("--pdf", type=str, help="PDF textbook (parsed via Mathpix)")
    inp.add_argument("--textbook", "-t", type=str, help="Markdown textbook file")
    inp.add_argument("--personalized-textbook", type=str, help="Pre-personalized textbook (skip personalization)")

    # Stage control
    stages = parser.add_argument_group("Stage control")
    stages.add_argument("--pdf-only", action="store_true", help="Stop after PDF -> markdown")
    stages.add_argument("--concepts-only", action="store_true", help="Stop after concept extraction")
    stages.add_argument("--extract-concepts", action="store_true", help="Enable concept extraction step")
    stages.add_argument("--skip-personalize", action="store_true", help="Skip personalization, use raw markdown")
    stages.add_argument("--skip-animation", action="store_true", help="Stop after personalization (no video)")

    # Tuning
    tuning = parser.add_argument_group("Tuning parameters")
    tuning.add_argument("--interest", "-i", nargs="+", help="Interest(s) for personalization")
    tuning.add_argument("--output-dir", "-o", type=str, help="Root output directory")
    tuning.add_argument("--output-markdown", type=str, help="Explicit markdown output path (for --pdf-only)")
    tuning.add_argument("--preview", "-p", action="store_true", help="Code only, skip video rendering")
    tuning.add_argument("--max-examples", type=int, help="Max examples to animate")
    tuning.add_argument("--page-range", type=str, help="PDF page range (e.g., '1-50')")

    # Info
    parser.add_argument("--list-interests", "-l", action="store_true", help="List available interests")

    return parser


def handle_list_interests():
    """Print available interests and exit."""
    print("\nAvailable interests for personalization:")
    print("=" * 60)
    for name in list_available_interests():
        profile = get_interest_profile(name)
        if profile:
            print(f"\n  {name}")
            print(f"    Display: {profile.display_name}")
            print(f"    Description: {profile.description}")
            stats = []
            if hasattr(profile, "fun_facts") and profile.fun_facts:
                stats.append(f"{len(profile.fun_facts)} fun facts")
            if hasattr(profile, "cultural_references") and profile.cultural_references:
                stats.append(f"{len(profile.cultural_references)} cultural refs")
            if hasattr(profile, "motivational_quotes") and profile.motivational_quotes:
                stats.append(f"{len(profile.motivational_quotes)} quotes")
            if stats:
                print(f"    Content: {', '.join(stats)}")
    print()


def handle_pdf_only(args):
    """PDF-only mode: parse to markdown and exit."""
    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        logger.error(f"PDF file not found: {pdf_path}")
        sys.exit(1)

    output_md = Path(args.output_markdown) if args.output_markdown else Path(f"{pdf_path.stem}.md")
    success = parse_pdf_step(pdf_path, output_md, args.page_range)
    sys.exit(0 if success else 1)


def handle_concepts_only(args):
    """Concepts-only mode: extract concepts and display/save."""
    md_path = Path(args.textbook) if args.textbook else None
    if args.pdf:
        # Parse PDF first, then extract concepts
        pdf_path = Path(args.pdf)
        if not pdf_path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            sys.exit(1)
        md_path = Path(args.output_markdown) if args.output_markdown else Path(f"{pdf_path.stem}.md")
        if not parse_pdf_step(pdf_path, md_path, args.page_range):
            sys.exit(1)

    if not md_path or not md_path.exists():
        logger.error(f"Markdown file not found: {md_path}")
        sys.exit(1)

    config = Config.from_env()

    # Determine output path for concepts JSON
    concepts_output = None
    if args.output_dir:
        concepts_dir = Path(args.output_dir) / "02_concepts"
        concepts_output = concepts_dir / "concepts.json"

    concept_result, errors = extract_concepts_step(md_path, config, concepts_output)

    print(f"\n{'=' * 60}")
    print("CONCEPT EXTRACTION RESULTS")
    print("=" * 60)
    print(concept_result.display())

    if errors:
        for err in errors:
            logger.warning(err)

    sys.exit(0 if not concept_result.error else 1)


def main():
    parser = build_parser()
    args = parser.parse_args()

    # -- Info modes --
    if args.list_interests:
        handle_list_interests()
        return

    # -- PDF-only mode --
    if args.pdf_only or (args.pdf and args.output_markdown and not args.interest and not args.concepts_only):
        if not args.pdf:
            parser.error("--pdf is required with --pdf-only")
        handle_pdf_only(args)
        return

    # -- Concepts-only mode --
    if args.concepts_only:
        if not args.pdf and not args.textbook:
            parser.error("--pdf or --textbook is required with --concepts-only")
        handle_concepts_only(args)
        return

    # -- Full pipeline validation --
    if not args.pdf and not args.personalized_textbook and not args.textbook:
        parser.error("One of --pdf, --textbook, or --personalized-textbook is required")

    if sum([bool(args.pdf), bool(args.textbook), bool(args.personalized_textbook)]) > 1:
        parser.error("Use only one of: --pdf, --textbook, or --personalized-textbook")

    if not args.skip_personalize and not args.personalized_textbook and not args.interest:
        parser.error("--interest is required (or use --skip-personalize / --personalized-textbook)")

    if not args.output_dir:
        parser.error("--output-dir is required for the full pipeline")

    # Resolve paths
    pdf_path = Path(args.pdf) if args.pdf else None
    textbook_path = Path(args.textbook) if args.textbook else None
    personalized_path = Path(args.personalized_textbook) if args.personalized_textbook else None

    # Validate files exist
    for label, p in [("PDF", pdf_path), ("Textbook", textbook_path), ("Personalized textbook", personalized_path)]:
        if p and not p.exists():
            logger.error(f"{label} file not found: {p}")
            sys.exit(1)

    # Determine interests
    if personalized_path:
        name = personalized_path.stem.lower()
        detected = next((i for i in list_available_interests() if i in name), None)
        interests = [detected] if detected else ["general"]
    elif args.skip_personalize:
        interests = args.interest or ["general"]
    else:
        interests = args.interest

    config = Config.from_env()
    output_dir = Path(args.output_dir)

    # Enable concept extraction when explicitly requested or via --extract-concepts
    do_extract = args.extract_concepts

    results = []
    for interest in interests:
        logger.info(f"\n{'#' * 70}")
        logger.info(f"# Processing interest: {interest}")
        logger.info(f"{'#' * 70}\n")

        result = run_pipeline(
            pdf_path=pdf_path,
            textbook_path=textbook_path,
            personalized_textbook_path=personalized_path,
            interest=interest,
            output_dir=output_dir,
            config=config,
            preview_only=args.preview,
            max_examples=args.max_examples,
            page_range=args.page_range,
            extract_concepts=do_extract,
            skip_personalize=args.skip_personalize,
            skip_animation=args.skip_animation,
        )
        results.append(result)

    print_summary(results)


if __name__ == "__main__":
    main()
