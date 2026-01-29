#!/usr/bin/env python3
"""
Quick Start: Use Math-To-Manim style pipeline to generate animations.

This script uses the multi-agent approach from Math-To-Manim:
https://github.com/HarleyCoops/Math-To-Manim

Usage:
    # Simple topic
    python scripts/math_to_manim_quickstart.py "Pythagorean theorem"

    # From textbook section
    python scripts/math_to_manim_quickstart.py --section "2.3"

    # With verbose pedagogical prompt
    python scripts/math_to_manim_quickstart.py "Quadratic formula" --verbose

    # Preview only (no render)
    python scripts/math_to_manim_quickstart.py "Slope" --preview
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

try:
    from anthropic import Anthropic
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Please install: pip install anthropic python-dotenv")
    sys.exit(1)


# =============================================================================
# MATH-TO-MANIM STYLE MULTI-AGENT PROMPTS
# =============================================================================

CONCEPT_ANALYZER_PROMPT = """You are the Concept Analyzer agent. Your role is to parse the user's request and identify:

1. Core mathematical/scientific topic
2. Target audience level (elementary, high school, undergraduate, graduate)
3. Key subtopics that need visualization
4. Mathematical notation requirements (LaTeX, symbols)
5. Suggested visual elements (graphs, shapes, transformations)

Analyze this topic: {topic}

Additional context: {context}

Output a structured analysis in this format:
TOPIC: [main topic]
AUDIENCE: [level]
SUBTOPICS: [comma-separated list]
NOTATION: [required mathematical notation]
VISUALS: [suggested visual elements]
DURATION: [suggested animation length in seconds]
"""

PREREQUISITE_EXPLORER_PROMPT = """You are the Prerequisite Explorer agent. Your role is to build a "reverse knowledge tree" - identifying what concepts must be understood BEFORE the main topic.

Main topic: {topic}
Analysis: {analysis}

List prerequisites in order from most fundamental to most advanced:
1. What basic concepts does this build upon?
2. What notation/symbols should the viewer already know?
3. What simpler examples should be shown first?

Output format:
PREREQUISITES:
1. [most fundamental concept]
2. [next concept]
...
N. [most advanced prerequisite]

LEARNING_PATH: [suggested order to introduce concepts in animation]
"""

MATHEMATICAL_ENRICHER_PROMPT = """You are the Mathematical Enricher agent. Your role is to add rigorous mathematical content:

Topic: {topic}
Prerequisites: {prerequisites}

Provide:
1. Precise mathematical definitions
2. Key theorems/properties with proper LaTeX
3. Step-by-step derivations or proofs
4. Common misconceptions to address
5. Edge cases or special conditions

Output format:
DEFINITIONS:
- [definition 1 with LaTeX]

THEOREMS:
- [theorem with LaTeX]

DERIVATION:
[step-by-step with LaTeX]

MISCONCEPTIONS:
- [common mistake 1]
"""

VISUAL_DESIGNER_PROMPT = """You are the Visual Designer agent. Your role is to specify the visual presentation:

Topic: {topic}
Math content: {math_content}

Design specifications for Manim animation:
1. Color scheme (which colors for which elements)
2. Camera movements (zoom, pan, focus)
3. Animation timing (when to pause, speed of transforms)
4. Layout (where to position equations, graphs, labels)
5. Transitions between steps

Output format:
COLOR_SCHEME:
- Primary text: [color]
- Equations: [color]
- Highlights: [color]
- Graphs/shapes: [colors]

LAYOUT:
- Title position: [position]
- Main content: [position]
- Supporting visuals: [position]

TIMING:
- Introduction: [seconds]
- Each major step: [seconds]
- Conclusion: [seconds]

TRANSITIONS:
- Between steps: [animation type]
- Emphasis: [animation type]
"""

NARRATIVE_COMPOSER_PROMPT = """You are the Narrative Composer agent. Your role is to create a detailed, pedagogically-sound narrative for the animation.

Topic: {topic}
Visual design: {visual_design}
Math content: {math_content}

Create a 2000+ token verbose prompt that:
1. Flows naturally from fundamental to advanced
2. Connects each visual element to the concept
3. Anticipates viewer questions
4. Builds intuition before formalism
5. Ends with reinforcement of key insights

Output a detailed narrative script with timing cues:
[0:00] Introduction - [what to show and say]
[0:XX] Step 1 - [content]
...
"""

CODE_GENERATOR_PROMPT = """You are the Code Generator agent. Generate complete, working ManimCE Python code.

Narrative and specifications:
{narrative}

Requirements:
1. Use `from manim import *`
2. Create a single Scene class with construct() method
3. Follow the timing and visual specifications exactly
4. Use proper LaTeX formatting for all equations
5. Include self.wait() between animations
6. Add comments explaining each section

Generate ONLY valid Python code that can be run with:
manim -pql output.py SceneName

```python
from manim import *

class [SceneName](Scene):
    def construct(self):
        # Your implementation here
        pass
```
"""


# =============================================================================
# TEXTBOOK CONTENT (from your curriculum)
# =============================================================================

TEXTBOOK_SECTIONS = {
    "2.1": {
        "title": "Solving Equations with Addition/Subtraction",
        "content": "Solve equations using the Subtraction and Addition Properties of Equality. If a = b, then a - c = b - c and a + c = b + c.",
        "examples": ["y + 37 = -13", "a - 28 = -37", "9x - 5 - 8x - 6 = 7"],
    },
    "2.2": {
        "title": "Solving Equations with Multiplication/Division",
        "content": "Division Property: if a = b, then a/c = b/c. Multiplication Property: if a = b, then ac = bc.",
        "examples": ["7x = 91", "-12p = 48", "n/6 = 15", "(2/3)x = 18"],
    },
    "2.3": {
        "title": "Two-Step Equations",
        "content": "Combine addition/subtraction and multiplication/division to solve equations like 2x + 3 = 11.",
        "examples": ["2x + 3 = 11", "3y - 7 = 14", "(x/4) + 5 = 9"],
    },
    "5.1": {
        "title": "Slope of a Line",
        "content": "Slope = rise/run = (y2 - y1)/(x2 - x1). Positive slope goes up, negative goes down.",
        "examples": ["Find slope between (1,2) and (4,8)", "Slope of y = 2x + 3"],
    },
    "5.2": {
        "title": "Slope-Intercept Form",
        "content": "y = mx + b where m is slope and b is y-intercept. Changing m changes steepness, changing b shifts up/down.",
        "examples": ["y = 2x + 1", "y = -x + 4", "Compare y = 2x + 1 vs y = 2x - 3"],
    },
    "6.1": {
        "title": "Systems of Equations - Graphing",
        "content": "Solution is the intersection point of two lines. Graph both lines and find where they cross.",
        "examples": ["y = 2x + 1 and y = -x + 4"],
    },
    "9.1": {
        "title": "Graphing Quadratic Functions",
        "content": "Parabola y = ax^2 + bx + c. Vertex, axis of symmetry, opens up (a>0) or down (a<0).",
        "examples": ["y = x^2 - 4x + 3", "y = -x^2 + 2x + 1"],
    },
    "9.3": {
        "title": "Completing the Square",
        "content": "Rewrite ax^2 + bx + c in form a(x-h)^2 + k. Add (b/2)^2 to complete the square.",
        "examples": ["x^2 + 6x + ? = (x + 3)^2"],
    },
    "9.4": {
        "title": "Quadratic Formula",
        "content": "x = (-b ± √(b²-4ac)) / 2a derived from completing the square on ax^2 + bx + c = 0.",
        "examples": ["Solve x^2 + 5x + 6 = 0", "Solve 2x^2 - 4x - 6 = 0"],
    },
}


class MathToManimPipeline:
    """Multi-agent pipeline inspired by Math-To-Manim."""

    def __init__(self, model: str = "claude-sonnet-4-20250514", verbose: bool = False):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.verbose = verbose

    def _call_agent(self, system: str, prompt: str, agent_name: str) -> str:
        """Call a single agent in the pipeline."""
        if self.verbose:
            print(f"\n🤖 [{agent_name}] Processing...")

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        result = response.content[0].text

        if self.verbose:
            print(f"   ✓ {agent_name} complete ({len(result)} chars)")

        return result

    def run_full_pipeline(self, topic: str, context: str = "") -> dict:
        """Run the full 6-stage Math-To-Manim pipeline."""

        print(f"\n{'='*60}")
        print(f"🎬 Math-To-Manim Pipeline: {topic}")
        print(f"{'='*60}")

        # Stage 1: Concept Analyzer
        analysis = self._call_agent(
            "You are a mathematical concept analyzer.",
            CONCEPT_ANALYZER_PROMPT.format(topic=topic, context=context),
            "Concept Analyzer"
        )

        # Stage 2: Prerequisite Explorer
        prerequisites = self._call_agent(
            "You are a prerequisite knowledge explorer.",
            PREREQUISITE_EXPLORER_PROMPT.format(topic=topic, analysis=analysis),
            "Prerequisite Explorer"
        )

        # Stage 3: Mathematical Enricher
        math_content = self._call_agent(
            "You are a mathematical content enricher.",
            MATHEMATICAL_ENRICHER_PROMPT.format(topic=topic, prerequisites=prerequisites),
            "Mathematical Enricher"
        )

        # Stage 4: Visual Designer
        visual_design = self._call_agent(
            "You are a visual design specialist for math animations.",
            VISUAL_DESIGNER_PROMPT.format(topic=topic, math_content=math_content),
            "Visual Designer"
        )

        # Stage 5: Narrative Composer
        narrative = self._call_agent(
            "You are a pedagogical narrative composer.",
            NARRATIVE_COMPOSER_PROMPT.format(
                topic=topic,
                visual_design=visual_design,
                math_content=math_content
            ),
            "Narrative Composer"
        )

        # Stage 6: Code Generator
        code_response = self._call_agent(
            "You are a Manim code generation expert.",
            CODE_GENERATOR_PROMPT.format(narrative=narrative),
            "Code Generator"
        )

        # Extract Python code
        code_match = re.search(r"```python\s*(.*?)```", code_response, re.DOTALL)
        code = code_match.group(1) if code_match else code_response

        return {
            "topic": topic,
            "analysis": analysis,
            "prerequisites": prerequisites,
            "math_content": math_content,
            "visual_design": visual_design,
            "narrative": narrative,
            "code": code,
        }

    def run_simple_pipeline(self, topic: str, context: str = "") -> str:
        """Run simplified single-call pipeline (faster, cheaper)."""

        print(f"\n🎬 Quick generation: {topic}")

        prompt = f"""Create a Manim animation for: {topic}

Additional context: {context}

Requirements:
1. Start with prerequisites/fundamentals
2. Build up step by step pedagogically
3. Use proper LaTeX for all equations
4. Include visual elements (graphs, shapes, transformations)
5. Add timing with self.wait() between steps
6. Keep total duration under 60 seconds

Generate complete, working ManimCE Python code:
```python
from manim import *

class [SceneName](Scene):
    def construct(self):
        # Implementation
        pass
```"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        content = response.content[0].text
        code_match = re.search(r"```python\s*(.*?)```", content, re.DOTALL)
        return code_match.group(1) if code_match else content


def extract_scene_name(code: str) -> Optional[str]:
    """Extract Scene class name from code."""
    match = re.search(r"class\s+(\w+)\s*\(\s*Scene\s*\)", code)
    return match.group(1) if match else None


def render_animation(code: str, output_file: str, quality: str = "l") -> bool:
    """Render the generated Manim code."""

    # Save code to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(code)

    # Extract scene name
    scene_name = extract_scene_name(code)
    if not scene_name:
        print("❌ No Scene class found in generated code")
        return False

    # Render with manim
    cmd = f"manim -pq{quality} {output_file} {scene_name}"
    print(f"\n🎥 Rendering: {cmd}")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ Render complete!")
        return True
    else:
        print(f"❌ Render failed:\n{result.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate Manim animations using Math-To-Manim style pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Simple topic (quick mode)
    python scripts/math_to_manim_quickstart.py "Pythagorean theorem"

    # Full 6-agent pipeline (verbose)
    python scripts/math_to_manim_quickstart.py "Quadratic formula" --full --verbose

    # From textbook section
    python scripts/math_to_manim_quickstart.py --section 2.3

    # Preview only
    python scripts/math_to_manim_quickstart.py "Slope" --preview

    # List sections
    python scripts/math_to_manim_quickstart.py --list
        """
    )

    parser.add_argument("topic", nargs="?", help="Math topic to animate")
    parser.add_argument("--section", help="Textbook section (e.g., 2.3, 5.1)")
    parser.add_argument("--full", action="store_true", help="Use full 6-agent pipeline")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show pipeline progress")
    parser.add_argument("--preview", action="store_true", help="Preview code only, no render")
    parser.add_argument("--quality", "-q", choices=["l", "m", "h"], default="l", help="Video quality")
    parser.add_argument("--output", "-o", help="Output filename")
    parser.add_argument("--list", action="store_true", help="List textbook sections")

    args = parser.parse_args()

    # List sections
    if args.list:
        print("\n📚 Available Textbook Sections")
        print("="*60)
        for key, section in TEXTBOOK_SECTIONS.items():
            print(f"\n{key}: {section['title']}")
            print(f"   {section['content'][:80]}...")
        return 0

    # Get topic from section or argument
    if args.section:
        if args.section not in TEXTBOOK_SECTIONS:
            print(f"❌ Unknown section: {args.section}")
            print(f"   Available: {', '.join(TEXTBOOK_SECTIONS.keys())}")
            return 1
        section = TEXTBOOK_SECTIONS[args.section]
        topic = section["title"]
        context = f"{section['content']}\nExamples: {', '.join(section['examples'])}"
    elif args.topic:
        topic = args.topic
        context = ""
    else:
        parser.print_help()
        return 1

    # Initialize pipeline
    pipeline = MathToManimPipeline(verbose=args.verbose)

    # Run pipeline
    if args.full:
        result = pipeline.run_full_pipeline(topic, context)
        code = result["code"]

        if args.verbose:
            print(f"\n📋 Pipeline Summary:")
            print(f"   Prerequisites: {len(result['prerequisites'])} chars")
            print(f"   Math content: {len(result['math_content'])} chars")
            print(f"   Narrative: {len(result['narrative'])} chars")
    else:
        code = pipeline.run_simple_pipeline(topic, context)

    # Output filename
    output_file = args.output or f"output/math_to_manim_{topic[:30].replace(' ', '_').lower()}.py"

    # Preview or render
    if args.preview:
        print(f"\n{'='*60}")
        print(f"Generated Code:")
        print(f"{'='*60}")
        print(code)
        print(f"{'='*60}")

        # Save to file
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        Path(output_file).write_text(code)
        print(f"\n📁 Saved to: {output_file}")
        print(f"   Render with: manim -pql {output_file} {extract_scene_name(code)}")
    else:
        success = render_animation(code, output_file, args.quality)
        return 0 if success else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
