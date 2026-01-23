#!/usr/bin/env python3
"""
Example usage of the parameterized template system.

This demonstrates how to:
1. Parse math questions and extract parameters
2. Generate personalized animation code
3. Render videos from templates

Run this script:
    python examples/template_usage.py
"""

from math_content_engine.templates import TemplateEngine


def demo_simple_parsing():
    """Demonstrate parsing questions without rendering."""
    print("=" * 60)
    print("Demo 1: Parsing Math Questions")
    print("=" * 60)

    # Use simple (regex-based) parser - no API key needed
    engine = TemplateEngine(use_simple_parser=True)

    questions = [
        "Solve 3x + 5 = 14",
        "Find the slope between (1, 2) and (4, 8)",
        "Graph y = 2x - 3",
        "Graph x > 5",
        "Solve 2x - 4 = 10",
    ]

    for question in questions:
        print(f"\nQuestion: {question}")
        parse_result = engine.parse_question(question)

        if parse_result.success:
            print(f"  Template: {parse_result.template_id}")
            print(f"  Parameters: {parse_result.parameters}")
            print(f"  Confidence: {parse_result.confidence}")
        else:
            print(f"  Failed: {parse_result.error_message}")


def demo_code_generation():
    """Demonstrate generating Manim code without rendering."""
    print("\n" + "=" * 60)
    print("Demo 2: Generating Manim Code")
    print("=" * 60)

    engine = TemplateEngine(use_simple_parser=True)

    question = "Solve 4x + 8 = 20"
    print(f"\nQuestion: {question}")

    code, parse_result = engine.preview_code(question)

    print(f"\nParsed as: {parse_result.template_id}")
    print(f"Parameters: {parse_result.parameters}")
    print("\nGenerated Code (first 50 lines):")
    print("-" * 40)
    lines = code.split('\n')
    for line in lines[:50]:
        print(line)
    if len(lines) > 50:
        print(f"... ({len(lines) - 50} more lines)")


def demo_list_templates():
    """List all available templates."""
    print("\n" + "=" * 60)
    print("Demo 3: Available Templates")
    print("=" * 60)

    engine = TemplateEngine(use_simple_parser=True)
    templates = engine.list_templates()

    print(f"\nFound {len(templates)} templates:\n")
    for t in templates:
        print(f"  {t.id}")
        print(f"    Name: {t.name}")
        print(f"    Category: {t.category.value}")
        print(f"    Required params: {t.get_required_params()}")
        if t.example_questions:
            print(f"    Example: {t.example_questions[0]}")
        print()


def demo_direct_template_usage():
    """Use templates directly with explicit parameters."""
    print("\n" + "=" * 60)
    print("Demo 4: Direct Template Usage")
    print("=" * 60)

    from math_content_engine.templates import TemplateRenderer, get_registry
    from math_content_engine.templates.definitions.linear_equations import compute_linear_derived

    registry = get_registry()
    renderer = TemplateRenderer(registry)

    # Define parameters directly
    params = {"a": 5, "b": -3, "c": 12}

    # Compute derived values (solution, axis ranges, etc.)
    derived = compute_linear_derived(params)
    params.update(derived)

    print(f"\nTemplate: linear_equation_graph")
    print(f"Parameters: {params}")
    print(f"Solution: x = {params['solution']}")

    # Render the code
    code, scene_name = renderer.render("linear_equation_graph", params)
    print(f"\nScene name: {scene_name}")
    print(f"Code length: {len(code)} characters")


def demo_personalized_problems():
    """Show how the same template works for different problems."""
    print("\n" + "=" * 60)
    print("Demo 5: Personalized Problems")
    print("=" * 60)

    engine = TemplateEngine(use_simple_parser=True)

    # Different linear equations - same template, different parameters
    problems = [
        "Solve 2x + 3 = 7",      # Solution: x = 2
        "Solve 5x - 10 = 15",    # Solution: x = 5
        "Solve 3x + 9 = 0",      # Solution: x = -3
        "Solve 4x - 8 = 12",     # Solution: x = 5
    ]

    print("\nAll these problems use the same template with different parameters:\n")

    for problem in problems:
        code, result = engine.preview_code(problem)
        if result.success:
            print(f"  {problem}")
            print(f"    -> Parameters: a={result.parameters['a']}, "
                  f"b={result.parameters['b']}, c={result.parameters['c']}")
            print(f"    -> Solution: x = {result.parameters['solution']}")
        print()


def demo_full_video_generation():
    """
    Generate actual videos (requires Manim to be installed).

    Uncomment to run - this will create video files!
    """
    print("\n" + "=" * 60)
    print("Demo 6: Full Video Generation (commented out)")
    print("=" * 60)
    print("""
To generate actual videos, uncomment the code below.
This requires Manim to be installed:
    pip install manim

Example code:

    engine = TemplateEngine(use_simple_parser=True)

    result = engine.generate_from_question(
        question="Solve 3x + 5 = 14",
        output_filename="my_linear_equation"
    )

    if result.success:
        print(f"Video saved to: {result.video_path}")
        print(f"Render time: {result.render_time:.2f}s")
    else:
        print(f"Failed: {result.error_message}")
""")

    # Uncomment to actually generate videos:
    # engine = TemplateEngine(use_simple_parser=True)
    # result = engine.generate_from_question(
    #     question="Solve 3x + 5 = 14",
    #     output_filename="my_linear_equation"
    # )
    # if result.success:
    #     print(f"Video saved to: {result.video_path}")


if __name__ == "__main__":
    demo_simple_parsing()
    demo_code_generation()
    demo_list_templates()
    demo_direct_template_usage()
    demo_personalized_problems()
    demo_full_video_generation()

    print("\n" + "=" * 60)
    print("All demos completed!")
    print("=" * 60)
