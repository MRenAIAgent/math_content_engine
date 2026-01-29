#!/usr/bin/env python3
"""
Quick Start: Generate video animations from algebra textbook content.

Usage:
    # Generate from a topic
    python scripts/textbook_to_animation.py "Two-step equations"

    # Generate from a specific chapter section
    python scripts/textbook_to_animation.py --section "2.1" --example 1

    # Batch generate top 5 high-impact topics
    python scripts/textbook_to_animation.py --batch-top 5

    # With narration (TTS)
    python scripts/textbook_to_animation.py "Slope-intercept form" --narrate

    # Preview code only (no render)
    python scripts/textbook_to_animation.py "Quadratic formula" --preview
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from math_content_engine.config import Config, VideoQuality
from math_content_engine.engine import MathContentEngine


# =============================================================================
# HIGH-IMPACT TOPICS FROM ALGEBRA 1 CURRICULUM
# =============================================================================
TOP_ANIMATION_TOPICS = [
    {
        "topic": "Solving Two-Step Equations using Balance Method",
        "section": "2.3",
        "description": "Show balance scale model - isolating variables step by step",
        "example": "Solve 2x + 3 = 11 using the balance method",
    },
    {
        "topic": "Slope as Rise over Run",
        "section": "5.1",
        "description": "Animated slope triangles between points on a line",
        "example": "Show slope calculation between (1, 2) and (4, 8)",
    },
    {
        "topic": "Slope-Intercept Form y = mx + b",
        "section": "5.2",
        "description": "How changing m and b affects the line on a graph",
        "example": "Compare y = 2x + 1, y = 2x - 3, and y = -x + 1",
    },
    {
        "topic": "Graphing Systems of Equations",
        "section": "6.1",
        "description": "Two lines intersecting to show the solution point",
        "example": "Graph y = 2x + 1 and y = -x + 4, find intersection",
    },
    {
        "topic": "Solving Systems by Substitution",
        "section": "6.2",
        "description": "Step-by-step replacement animation",
        "example": "Solve y = 2x and 3x + y = 10 by substitution",
    },
    {
        "topic": "Graphing Quadratic Functions (Parabolas)",
        "section": "9.1",
        "description": "Vertex, axis of symmetry, direction of opening",
        "example": "Graph y = x^2 - 4x + 3 showing key features",
    },
    {
        "topic": "The Quadratic Formula Derivation",
        "section": "9.4",
        "description": "Derive quadratic formula from completing the square",
        "example": "Show ax^2 + bx + c = 0 transforms to x = (-b ± √(b²-4ac))/2a",
    },
    {
        "topic": "Completing the Square (Geometric)",
        "section": "9.3",
        "description": "Visual geometric approach with area models",
        "example": "Complete x^2 + 6x + ? = (x + 3)^2 using squares",
    },
    {
        "topic": "Exponential Growth vs Decay",
        "section": "7.3",
        "description": "Side-by-side animation of growth and decay curves",
        "example": "Compare y = 2^x (growth) vs y = (1/2)^x (decay)",
    },
    {
        "topic": "Pythagorean Theorem Visual Proof",
        "section": "10.1",
        "description": "Animated proof with squares on triangle sides",
        "example": "Show a^2 + b^2 = c^2 with area visualization",
    },
]


def generate_animation(
    topic: str,
    requirements: str = "",
    quality: str = "l",
    output_name: Optional[str] = None,
    preview_only: bool = False,
    with_narration: bool = False,
) -> bool:
    """Generate a single animation from a topic."""

    print(f"\n{'='*60}")
    print(f"Topic: {topic}")
    print(f"{'='*60}")

    config = Config.from_env()
    config.video_quality = VideoQuality(quality)

    engine = MathContentEngine(config)

    if preview_only:
        # Preview code without rendering
        result = engine.preview_code(
            topic=topic,
            requirements=requirements,
            audience_level="high school",
        )

        print(f"\nScene: {result.scene_name}")
        print(f"Valid: {result.validation.is_valid}")

        if result.validation.errors:
            print(f"Errors: {result.validation.errors}")

        print(f"\n{'-'*40}\n{result.code}\n{'-'*40}")

        # Save preview
        if output_name:
            preview_path = Path(f"output/{output_name}_preview.py")
            preview_path.parent.mkdir(exist_ok=True)
            preview_path.write_text(result.code)
            print(f"\nSaved to: {preview_path}")

        return result.validation.is_valid

    # Full generation with rendering
    result = engine.generate(
        topic=topic,
        requirements=requirements,
        audience_level="high school",
        output_filename=output_name,
    )

    if result.success:
        print(f"\n✅ Animation generated successfully!")
        print(f"   Video: {result.video_path}")
        print(f"   Render time: {result.render_time:.2f}s")
        print(f"   Attempts: {result.total_attempts}")

        # Add narration if requested
        if with_narration and result.video_path:
            add_narration(result.video_path, topic)

        return True
    else:
        print(f"\n❌ Generation failed: {result.error_message}")
        return False


def add_narration(video_path: Path, topic: str) -> None:
    """Add TTS narration to the generated video."""
    try:
        from math_content_engine.tts import (
            NarratedAnimationGenerator,
            AnimationScript,
        )

        print("\n🎤 Adding narration...")

        generator = NarratedAnimationGenerator()

        # Create simple narration script
        script = AnimationScript(title=topic)
        script.add_intro(f"Let's learn about {topic}.")
        script.add_step("Watch carefully as we break this down step by step.", time=3.0)
        script.add_conclusion("And that's how it works!", time=10.0)

        output_path = video_path.with_name(f"{video_path.stem}_narrated.mp4")

        result = generator.create_narrated_video(
            video_path=video_path,
            script=script,
            output_path=output_path,
        )

        if result.success:
            print(f"   Narrated video: {result.video_path}")
        else:
            print(f"   Narration failed: {result.error_message}")

    except ImportError:
        print("   TTS not installed. Run: pip install -e '.[tts]'")


def batch_generate(count: int, quality: str = "l") -> None:
    """Generate animations for top N high-impact topics."""

    topics = TOP_ANIMATION_TOPICS[:count]

    print(f"\n🎬 Batch generating {count} animations...")
    print("="*60)

    results = {"success": 0, "failed": 0}

    for i, item in enumerate(topics, 1):
        print(f"\n[{i}/{count}] {item['topic']}")

        output_name = f"algebra_{item['section'].replace('.', '_')}_{item['topic'][:20].replace(' ', '_').lower()}"

        success = generate_animation(
            topic=item["topic"],
            requirements=item["example"],
            quality=quality,
            output_name=output_name,
        )

        if success:
            results["success"] += 1
        else:
            results["failed"] += 1

    print(f"\n{'='*60}")
    print(f"Batch complete: {results['success']} succeeded, {results['failed']} failed")


def list_topics() -> None:
    """List all high-impact animation topics."""

    print("\n📚 High-Impact Algebra 1 Animation Topics")
    print("="*60)

    for i, item in enumerate(TOP_ANIMATION_TOPICS, 1):
        print(f"\n{i}. {item['topic']}")
        print(f"   Section: {item['section']}")
        print(f"   Description: {item['description']}")
        print(f"   Example: {item['example']}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate video animations from algebra textbook content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple topic
  python scripts/textbook_to_animation.py "Two-step equations"

  # With specific example
  python scripts/textbook_to_animation.py "Slope" -r "Show slope between (0,0) and (3,6)"

  # Preview code only
  python scripts/textbook_to_animation.py "Quadratic formula" --preview

  # Batch generate top 5
  python scripts/textbook_to_animation.py --batch 5

  # List available topics
  python scripts/textbook_to_animation.py --list
        """
    )

    parser.add_argument(
        "topic",
        nargs="?",
        help="Math topic to animate"
    )

    parser.add_argument(
        "-r", "--requirements",
        default="",
        help="Additional requirements or specific example"
    )

    parser.add_argument(
        "-q", "--quality",
        choices=["l", "m", "h"],
        default="l",
        help="Video quality: l(ow), m(edium), h(igh). Default: l"
    )

    parser.add_argument(
        "-o", "--output",
        help="Output filename (without extension)"
    )

    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview generated code without rendering"
    )

    parser.add_argument(
        "--narrate",
        action="store_true",
        help="Add TTS narration to the video"
    )

    parser.add_argument(
        "--batch",
        type=int,
        metavar="N",
        help="Batch generate top N high-impact topics"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all high-impact animation topics"
    )

    args = parser.parse_args()

    # Handle list command
    if args.list:
        list_topics()
        return 0

    # Handle batch command
    if args.batch:
        batch_generate(args.batch, args.quality)
        return 0

    # Require topic for single generation
    if not args.topic:
        parser.print_help()
        print("\n❌ Error: Please provide a topic or use --list/--batch")
        return 1

    # Single topic generation
    success = generate_animation(
        topic=args.topic,
        requirements=args.requirements,
        quality=args.quality,
        output_name=args.output,
        preview_only=args.preview,
        with_narration=args.narrate,
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
