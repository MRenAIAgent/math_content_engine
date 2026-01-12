#!/usr/bin/env python3
"""
Middle School Algebra Examples (Grades 6-8)

Topics covered:
- Variables and expressions
- One-step and two-step equations
- Inequalities
- Order of operations
- Integer operations
- Proportions and ratios
- Introduction to linear equations
- Coordinate plane basics

Usage:
    from examples.algebra_middle_school import *

    # Generate a specific animation
    result = variables_introduction()

    # Or run all examples
    run_all_examples()
"""

import logging
from math_content_engine import MathContentEngine

logging.basicConfig(level=logging.INFO)


# =============================================================================
# VARIABLES AND EXPRESSIONS (Grade 6)
# =============================================================================

def variables_introduction():
    """Introduction to variables - what they are and why we use them."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Introduction to variables in algebra",
        requirements="""
        1. Start with a mystery box concept - "what number is inside?"
        2. Show that we use letters (like x) to represent unknown numbers
        3. Give simple examples:
           - If x = 3, what is x + 2?
           - If n = 5, what is 2n?
        4. Show how variables help us write general rules
        5. Use friendly colors and simple animations
        Keep it visual and intuitive for 6th graders.
        """,
        audience_level="middle school",
        output_filename="ms_variables_intro"
    )


def evaluating_expressions():
    """Evaluating algebraic expressions by substituting values."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Evaluating algebraic expressions",
        requirements="""
        Show step-by-step how to evaluate expressions:
        1. Start with expression: 3x + 5 when x = 4
        2. Show substitution: 3(4) + 5
        3. Show multiplication: 12 + 5
        4. Show final answer: 17

        Then show another example: 2a + 3b when a = 2, b = 3
        Use color coding - highlight the variable being replaced.
        """,
        audience_level="middle school",
        output_filename="ms_evaluating_expressions"
    )


def writing_expressions():
    """Translating words to algebraic expressions."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Writing algebraic expressions from words",
        requirements="""
        Show common phrases and their algebraic translations:
        1. "5 more than a number" → n + 5
        2. "twice a number" → 2x
        3. "a number decreased by 3" → x - 3
        4. "the quotient of a number and 4" → n/4
        5. "3 less than twice a number" → 2x - 3

        Show the words first, then animate the transformation to algebra.
        Use a table format for clarity.
        """,
        audience_level="middle school",
        output_filename="ms_writing_expressions"
    )


# =============================================================================
# ONE-STEP EQUATIONS (Grade 6-7)
# =============================================================================

def one_step_addition():
    """Solving one-step equations with addition/subtraction."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Solving one-step equations: addition and subtraction",
        requirements="""
        Use the balance scale concept:
        1. Show equation x + 5 = 12 as a balanced scale
        2. Explain: "What we do to one side, we must do to the other"
        3. Subtract 5 from both sides (animate the balance)
        4. Show: x + 5 - 5 = 12 - 5
        5. Simplify: x = 7
        6. Check: 7 + 5 = 12 ✓

        Then show: y - 3 = 8 (add 3 to both sides)
        Use a visual balance scale animation.
        """,
        audience_level="middle school",
        output_filename="ms_one_step_add_sub"
    )


def one_step_multiplication():
    """Solving one-step equations with multiplication/division."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Solving one-step equations: multiplication and division",
        requirements="""
        1. Show equation 3x = 15
        2. Explain: "3 times what equals 15?"
        3. Divide both sides by 3
        4. Show: 3x/3 = 15/3
        5. Result: x = 5
        6. Check: 3(5) = 15 ✓

        Then show: x/4 = 6 (multiply both sides by 4)

        Use inverse operations concept.
        Color code the operation being "undone".
        """,
        audience_level="middle school",
        output_filename="ms_one_step_mult_div"
    )


# =============================================================================
# TWO-STEP EQUATIONS (Grade 7)
# =============================================================================

def two_step_equations():
    """Solving two-step equations."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Solving two-step equations",
        requirements="""
        Solve: 2x + 5 = 13

        Step-by-step:
        1. Identify the operations: multiply by 2, then add 5
        2. Undo in reverse order (UNDO addition first)
        3. Subtract 5 from both sides: 2x + 5 - 5 = 13 - 5
        4. Simplify: 2x = 8
        5. Divide both sides by 2: 2x/2 = 8/2
        6. Result: x = 4
        7. Check: 2(4) + 5 = 8 + 5 = 13 ✓

        Use arrows to show the "peeling away" of operations.
        Show another example: 3y - 7 = 14
        """,
        audience_level="middle school",
        output_filename="ms_two_step_equations"
    )


def equations_with_negatives():
    """Solving equations involving negative numbers."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Solving equations with negative numbers",
        requirements="""
        1. Review: adding/subtracting negatives on a number line
        2. Solve: x + (-3) = 7
           - This is the same as x - 3 = 7
           - Add 3 to both sides: x = 10

        3. Solve: -2x = 10
           - Divide both sides by -2
           - x = -5
           - Check: -2(-5) = 10 ✓

        4. Solve: -x + 4 = 9
           - Subtract 4: -x = 5
           - Multiply by -1: x = -5

        Show number line for visualization.
        """,
        audience_level="middle school",
        output_filename="ms_equations_negatives"
    )


# =============================================================================
# INEQUALITIES (Grade 7)
# =============================================================================

def inequality_introduction():
    """Introduction to inequalities and their symbols."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Introduction to inequalities",
        requirements="""
        1. Introduce inequality symbols:
           - < less than
           - > greater than
           - ≤ less than or equal to
           - ≥ greater than or equal to

        2. Show examples on a number line:
           - x > 3 (open circle at 3, arrow right)
           - x ≤ 5 (closed circle at 5, arrow left)

        3. Explain open vs closed circles

        4. Real-world example: "You must be at least 48 inches tall"
           → h ≥ 48

        Use number line animations with shading.
        """,
        audience_level="middle school",
        output_filename="ms_inequality_intro"
    )


def solving_inequalities():
    """Solving one-step inequalities."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Solving one-step inequalities",
        requirements="""
        1. Solve: x + 4 > 7
           - Subtract 4 from both sides
           - x > 3
           - Graph on number line

        2. Solve: 3x ≤ 12
           - Divide both sides by 3
           - x ≤ 4
           - Graph on number line

        3. IMPORTANT: When multiplying/dividing by negative, FLIP the sign!
           - Solve: -2x > 6
           - Divide by -2 AND flip: x < -3
           - Explain why with a simple example: if 2 > 1, then -2 < -1

        Animate the inequality sign flipping for negative division.
        """,
        audience_level="middle school",
        output_filename="ms_solving_inequalities"
    )


# =============================================================================
# ORDER OF OPERATIONS (Grade 6)
# =============================================================================

def order_of_operations():
    """PEMDAS / Order of Operations."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Order of Operations - PEMDAS",
        requirements="""
        1. Introduce PEMDAS:
           P - Parentheses
           E - Exponents
           M/D - Multiplication and Division (left to right)
           A/S - Addition and Subtraction (left to right)

        2. Example: 3 + 4 × 2
           - Wrong: 3 + 4 = 7, 7 × 2 = 14 ✗
           - Right: 4 × 2 = 8, 3 + 8 = 11 ✓

        3. Example: 2 + 3² × (4 - 1)
           - Parentheses: (4-1) = 3
           - Exponents: 3² = 9
           - Multiply: 9 × 3 = 27
           - Add: 2 + 27 = 29

        Highlight each step being performed.
        Use colors for each operation type.
        """,
        audience_level="middle school",
        output_filename="ms_pemdas"
    )


# =============================================================================
# PROPORTIONS AND RATIOS (Grade 6-7)
# =============================================================================

def ratios_introduction():
    """Introduction to ratios."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Introduction to ratios",
        requirements="""
        1. What is a ratio? Comparing two quantities

        2. Three ways to write ratios:
           - 3 to 4
           - 3:4
           - 3/4

        3. Visual example: In a bag of 3 red and 4 blue marbles
           - Ratio of red to blue: 3:4
           - Ratio of blue to red: 4:3
           - Ratio of red to total: 3:7

        4. Equivalent ratios: 3:4 = 6:8 = 9:12
           (multiply both parts by the same number)

        Show visual representations with colored objects.
        """,
        audience_level="middle school",
        output_filename="ms_ratios_intro"
    )


def solving_proportions():
    """Solving proportions using cross multiplication."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Solving proportions with cross multiplication",
        requirements="""
        1. What is a proportion? Two equal ratios: a/b = c/d

        2. Cross multiplication: a × d = b × c

        3. Example: Solve x/6 = 4/8
           - Cross multiply: 8x = 6 × 4
           - 8x = 24
           - x = 3
           - Check: 3/6 = 4/8 = 1/2 ✓

        4. Word problem: If 3 apples cost $2, how much do 9 apples cost?
           - Set up: 3/2 = 9/x
           - Cross multiply: 3x = 18
           - x = 6 dollars

        Show the cross pattern with arrows.
        """,
        audience_level="middle school",
        output_filename="ms_proportions"
    )


# =============================================================================
# COORDINATE PLANE (Grade 6)
# =============================================================================

def coordinate_plane_intro():
    """Introduction to the coordinate plane."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Introduction to the coordinate plane",
        requirements="""
        1. Draw x-axis (horizontal) and y-axis (vertical)
        2. Label the origin (0, 0)
        3. Explain ordered pairs (x, y) - "x comes first like in alphabet"
        4. Plot several points:
           - (3, 2) - go right 3, up 2
           - (-2, 4) - go left 2, up 4
           - (1, -3) - go right 1, down 3
           - (-3, -2) - go left 3, down 2
        5. Name the four quadrants (I, II, III, IV)
        6. Show movement from origin to each point with arrows

        Animate plotting each point step by step.
        """,
        audience_level="middle school",
        output_filename="ms_coordinate_plane"
    )


def graphing_linear_equations():
    """Graphing linear equations by plotting points."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Graphing linear equations using a table of values",
        requirements="""
        Graph y = 2x + 1:

        1. Create a table of values:
           x | y = 2x + 1 | (x, y)
           -1| 2(-1)+1=-1 | (-1, -1)
           0 | 2(0)+1=1   | (0, 1)
           1 | 2(1)+1=3   | (1, 3)
           2 | 2(2)+1=5   | (2, 5)

        2. Plot each point on the coordinate plane
        3. Connect the points with a straight line
        4. Extend the line with arrows on both ends
        5. Point out that this is a LINE (linear equation)

        Animate the table being filled, then points appearing,
        then the line being drawn through them.
        """,
        audience_level="middle school",
        output_filename="ms_graphing_linear"
    )


# =============================================================================
# INTEGER OPERATIONS (Grade 7)
# =============================================================================

def adding_integers():
    """Adding positive and negative integers."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Adding integers using a number line",
        requirements="""
        1. Same signs - add and keep the sign:
           - 3 + 5 = 8 (both positive)
           - (-3) + (-5) = -8 (both negative)

        2. Different signs - subtract and take sign of larger:
           - 5 + (-3) = 2 (start at 5, move left 3)
           - (-7) + 4 = -3 (start at -7, move right 4)

        3. Show each on a number line with jumping animation

        4. Think of it as money:
           - Positive = earning money
           - Negative = owing money

        Use arrows on number line to show direction of movement.
        """,
        audience_level="middle school",
        output_filename="ms_adding_integers"
    )


def multiplying_integers():
    """Rules for multiplying and dividing integers."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Multiplying and dividing integers",
        requirements="""
        The Sign Rules:

        1. Positive × Positive = Positive
           3 × 4 = 12

        2. Negative × Negative = Positive
           (-3) × (-4) = 12
           Think: "Two wrongs make a right" or direction change

        3. Positive × Negative = Negative
           3 × (-4) = -12

        4. Negative × Positive = Negative
           (-3) × 4 = -12

        Same rules for division!

        Create a simple chart:
        (+)(+) = +
        (−)(−) = +
        (+)(−) = −
        (−)(+) = −

        "Same signs = Positive, Different signs = Negative"
        """,
        audience_level="middle school",
        output_filename="ms_multiplying_integers"
    )


# =============================================================================
# DISTRIBUTIVE PROPERTY (Grade 7)
# =============================================================================

def distributive_property():
    """The distributive property."""
    engine = MathContentEngine()
    return engine.generate(
        topic="The Distributive Property",
        requirements="""
        a(b + c) = ab + ac

        1. Visual explanation with rectangles:
           - Draw rectangle with width 3 and length (4 + 2)
           - Show it equals rectangle 3×4 plus rectangle 3×2
           - Area: 3(4+2) = 3(6) = 18
           - Same as: 3×4 + 3×2 = 12 + 6 = 18

        2. Examples:
           - 5(x + 3) = 5x + 15
           - 2(3y - 4) = 6y - 8
           - -3(2x + 5) = -6x - 15 (watch the signs!)

        3. "Backwards" - Factoring:
           - 6x + 12 = 6(x + 2)

        Show arrows from the outside number to each term inside.
        """,
        audience_level="middle school",
        output_filename="ms_distributive"
    )


def combining_like_terms():
    """Combining like terms to simplify expressions."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Combining like terms",
        requirements="""
        1. What are "like terms"?
           - Same variable raised to same power
           - Like: 3x and 5x, 2y² and 7y²
           - NOT like: 3x and 3y, x and x²

        2. Simplify: 3x + 5x + 2y + 4y
           - Group like terms: (3x + 5x) + (2y + 4y)
           - Combine: 8x + 6y

        3. Simplify: 4a + 3b - 2a + 5b
           - Rearrange: (4a - 2a) + (3b + 5b)
           - Combine: 2a + 8b

        4. More complex: 2x² + 3x + 5 + x² - x + 2
           - Group: (2x² + x²) + (3x - x) + (5 + 2)
           - Simplify: 3x² + 2x + 7

        Use color coding - same color for like terms.
        """,
        audience_level="middle school",
        output_filename="ms_like_terms"
    )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def run_all_examples():
    """Run all middle school algebra examples."""
    examples = [
        ("Variables Introduction", variables_introduction),
        ("Evaluating Expressions", evaluating_expressions),
        ("Writing Expressions", writing_expressions),
        ("One-Step Addition/Subtraction", one_step_addition),
        ("One-Step Multiplication/Division", one_step_multiplication),
        ("Two-Step Equations", two_step_equations),
        ("Equations with Negatives", equations_with_negatives),
        ("Inequality Introduction", inequality_introduction),
        ("Solving Inequalities", solving_inequalities),
        ("Order of Operations (PEMDAS)", order_of_operations),
        ("Ratios Introduction", ratios_introduction),
        ("Solving Proportions", solving_proportions),
        ("Coordinate Plane", coordinate_plane_intro),
        ("Graphing Linear Equations", graphing_linear_equations),
        ("Adding Integers", adding_integers),
        ("Multiplying Integers", multiplying_integers),
        ("Distributive Property", distributive_property),
        ("Combining Like Terms", combining_like_terms),
    ]

    results = []
    for name, func in examples:
        print(f"\n{'='*60}")
        print(f"Generating: {name}")
        print('='*60)
        try:
            result = func()
            results.append((name, result.success, result.video_path))
            if result.success:
                print(f"✓ Success: {result.video_path}")
            else:
                print(f"✗ Failed: {result.error_message}")
        except Exception as e:
            print(f"✗ Error: {e}")
            results.append((name, False, None))

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    successful = sum(1 for _, success, _ in results if success)
    print(f"Successful: {successful}/{len(results)}")

    return results


def main():
    """Display available examples."""
    print("Middle School Algebra Examples")
    print("="*60)
    print("""
Available examples:

VARIABLES AND EXPRESSIONS (Grade 6):
  - variables_introduction()
  - evaluating_expressions()
  - writing_expressions()

ONE-STEP EQUATIONS (Grade 6-7):
  - one_step_addition()
  - one_step_multiplication()

TWO-STEP EQUATIONS (Grade 7):
  - two_step_equations()
  - equations_with_negatives()

INEQUALITIES (Grade 7):
  - inequality_introduction()
  - solving_inequalities()

ORDER OF OPERATIONS (Grade 6):
  - order_of_operations()

PROPORTIONS AND RATIOS (Grade 6-7):
  - ratios_introduction()
  - solving_proportions()

COORDINATE PLANE (Grade 6):
  - coordinate_plane_intro()
  - graphing_linear_equations()

INTEGER OPERATIONS (Grade 7):
  - adding_integers()
  - multiplying_integers()

ALGEBRAIC EXPRESSIONS (Grade 7):
  - distributive_property()
  - combining_like_terms()

To generate all examples:
  run_all_examples()
""")


if __name__ == "__main__":
    main()
