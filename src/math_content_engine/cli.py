#!/usr/bin/env python3
"""
Command-line interface for Math Content Engine.
"""

import argparse
import logging
import sys
from pathlib import Path

from .config import Config, VideoQuality, LLMProvider
from .engine import MathContentEngine


def setup_logging(verbose: bool):
    """Configure logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S"
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate math animations using AI and Manim",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate animation from topic
  math-engine generate "Pythagorean theorem proof"

  # With custom output filename
  math-engine generate "Quadratic formula" -o quadratic

  # Preview code without rendering
  math-engine preview "Unit circle trigonometry"

  # Render existing Manim code
  math-engine render my_scene.py MySceneName

  # High quality output
  math-engine generate "Euler's identity" --quality h
        """
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate animation from topic")
    gen_parser.add_argument("topic", help="Math topic to animate")
    gen_parser.add_argument(
        "-r", "--requirements",
        default="",
        help="Additional requirements or customizations"
    )
    gen_parser.add_argument(
        "-a", "--audience",
        default="high school",
        choices=["elementary", "middle school", "high school", "college"],
        help="Target audience level"
    )
    gen_parser.add_argument(
        "-o", "--output",
        help="Output filename (without extension)"
    )
    gen_parser.add_argument(
        "-q", "--quality",
        choices=["l", "m", "h", "p", "k"],
        default="m",
        help="Video quality: l(ow), m(edium), h(igh), p(roduction), k(4K)"
    )
    gen_parser.add_argument(
        "-f", "--format",
        choices=["mp4", "gif"],
        default="mp4",
        help="Output format"
    )
    gen_parser.add_argument(
        "--provider",
        choices=["claude", "openai"],
        help="LLM provider (defaults to env setting)"
    )

    # Preview command
    preview_parser = subparsers.add_parser("preview", help="Preview generated code without rendering")
    preview_parser.add_argument("topic", help="Math topic")
    preview_parser.add_argument(
        "-r", "--requirements",
        default="",
        help="Additional requirements"
    )
    preview_parser.add_argument(
        "-a", "--audience",
        default="high school",
        help="Target audience level"
    )
    preview_parser.add_argument(
        "--save",
        help="Save code to file"
    )

    # Render command
    render_parser = subparsers.add_parser("render", help="Render existing Manim code")
    render_parser.add_argument("file", help="Python file containing Manim code")
    render_parser.add_argument("scene", help="Scene class name to render")
    render_parser.add_argument(
        "-o", "--output",
        help="Output filename"
    )
    render_parser.add_argument(
        "-q", "--quality",
        choices=["l", "m", "h", "p", "k"],
        default="m",
        help="Video quality"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    setup_logging(args.verbose)

    try:
        if args.command == "generate":
            return cmd_generate(args)
        elif args.command == "preview":
            return cmd_preview(args)
        elif args.command == "render":
            return cmd_render(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        return 130
    except Exception as e:
        logging.error(f"Error: {e}")
        if args.verbose:
            raise
        return 1

    return 0


def cmd_generate(args) -> int:
    """Handle generate command."""
    print(f"Generating animation for: {args.topic}")
    print("-" * 50)

    # Build config
    config = Config()
    config.video_quality = VideoQuality(args.quality)
    config.output_format = args.format

    if args.provider:
        config.llm_provider = LLMProvider(args.provider)

    engine = MathContentEngine(config)

    result = engine.generate(
        topic=args.topic,
        requirements=args.requirements,
        audience_level=args.audience,
        output_filename=args.output,
    )

    if result.success:
        print(f"\n✓ Animation generated successfully!")
        print(f"  Output: {result.video_path}")
        print(f"  Render time: {result.render_time:.2f}s")
        print(f"  Attempts: {result.total_attempts}")
        return 0
    else:
        print(f"\n✗ Generation failed: {result.error_message}")
        print(f"\nGenerated code:\n{'='*40}")
        print(result.code)
        print("="*40)
        return 1


def cmd_preview(args) -> int:
    """Handle preview command."""
    print(f"Generating code for: {args.topic}")
    print("-" * 50)

    engine = MathContentEngine()

    result = engine.preview_code(
        topic=args.topic,
        requirements=args.requirements,
        audience_level=args.audience,
    )

    print(f"\nScene name: {result.scene_name}")
    print(f"Valid: {result.validation.is_valid}")
    print(f"Attempts: {result.attempts}")

    if result.validation.errors:
        print(f"Errors: {result.validation.errors}")
    if result.validation.warnings:
        print(f"Warnings: {result.validation.warnings}")

    print(f"\nGenerated code:\n{'='*50}")
    print(result.code)
    print("="*50)

    if args.save:
        Path(args.save).write_text(result.code)
        print(f"\nCode saved to: {args.save}")

    return 0 if result.validation.is_valid else 1


def cmd_render(args) -> int:
    """Handle render command."""
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {args.file}")
        return 1

    code = file_path.read_text()
    print(f"Rendering {args.scene} from {args.file}")
    print("-" * 50)

    config = Config()
    config.video_quality = VideoQuality(args.quality)

    engine = MathContentEngine(config)

    result = engine.generate_from_code(
        code=code,
        scene_name=args.scene,
        output_filename=args.output,
    )

    if result.success:
        print(f"\n✓ Video rendered successfully!")
        print(f"  Output: {result.video_path}")
        print(f"  Render time: {result.render_time:.2f}s")
        return 0
    else:
        print(f"\n✗ Rendering failed: {result.error_message}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
