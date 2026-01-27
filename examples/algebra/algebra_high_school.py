#!/usr/bin/env python3
"""
High School Algebra Examples (Grades 9-12)

Topics covered:
- Linear equations and systems
- Quadratic equations and functions
- Polynomials and factoring
- Rational expressions
- Radicals and exponents
- Functions and transformations
- Sequences and series
- Logarithms and exponentials

Usage:
    from examples.algebra_high_school import *

    # Generate a specific animation
    result = quadratic_formula()

    # Or run all examples
    run_all_examples()
"""

import logging
from math_content_engine import MathContentEngine

logging.basicConfig(level=logging.INFO)


# =============================================================================
# LINEAR EQUATIONS AND SYSTEMS (Algebra 1)
# =============================================================================

def slope_intercept_form():
    """Understanding y = mx + b form."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Slope-Intercept Form: y = mx + b",
        requirements="""
        1. Introduce the formula y = mx + b
           - m = slope (steepness)
           - b = y-intercept (where line crosses y-axis)

        2. Show how changing m affects the line:
           - m > 0: line goes up (positive slope)
           - m < 0: line goes down (negative slope)
           - m = 0: horizontal line
           - Animate lines with m = 1, 2, -1, 0.5

        3. Show how changing b shifts the line up/down:
           - Same slope m = 2
           - Show b = 0, b = 3, b = -2

        4. Example: Graph y = 2x + 3
           - Start at (0, 3) - the y-intercept
           - Use slope 2 = 2/1: rise 2, run 1
           - Plot points and draw line

        Animate the line changing as m and b change.
        """,
        audience_level="high school",
        output_filename="hs_slope_intercept"
    )


def point_slope_form():
    """Point-slope form of a linear equation."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Point-Slope Form: y - y₁ = m(x - x₁)",
        requirements="""
        1. Introduce point-slope form: y - y₁ = m(x - x₁)
           - (x₁, y₁) is a point on the line
           - m is the slope

        2. When to use: when you know a point and slope

        3. Example: Write equation of line through (2, 3) with slope 4
           - y - 3 = 4(x - 2)
           - Can convert to slope-intercept: y = 4x - 5

        4. Example: Find equation of line through (1, 2) and (4, 8)
           - First find slope: m = (8-2)/(4-1) = 6/3 = 2
           - Use either point: y - 2 = 2(x - 1)
           - Simplify: y = 2x

        Show the point on the graph and the slope triangle.
        """,
        audience_level="high school",
        output_filename="hs_point_slope"
    )


def systems_substitution():
    """Solving systems of equations by substitution."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Solving Systems by Substitution",
        requirements="""
        Solve the system:
        y = 2x + 1
        3x + y = 11

        Step by step:
        1. One equation is already solved for y
        2. Substitute into the other: 3x + (2x + 1) = 11
        3. Combine like terms: 5x + 1 = 11
        4. Solve: 5x = 10, so x = 2
        5. Substitute back: y = 2(2) + 1 = 5
        6. Solution: (2, 5)
        7. Check in both equations

        Show both lines graphed with intersection point highlighted.
        Animate the substitution process.
        """,
        audience_level="high school",
        output_filename="hs_systems_substitution"
    )


def systems_elimination():
    """Solving systems of equations by elimination."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Solving Systems by Elimination",
        requirements="""
        Solve the system:
        2x + 3y = 12
        4x - 3y = 6

        Step by step:
        1. Notice y-coefficients are opposites (+3 and -3)
        2. Add equations to eliminate y:
           2x + 3y = 12
         + 4x - 3y = 6
           ─────────────
           6x + 0y = 18

        3. Solve: x = 3
        4. Substitute into either equation: 2(3) + 3y = 12
        5. Solve: 3y = 6, y = 2
        6. Solution: (3, 2)

        Show another example where you need to multiply first:
        3x + 2y = 7
        2x + 5y = 12

        Animate the equations being added together.
        """,
        audience_level="high school",
        output_filename="hs_systems_elimination"
    )


def systems_graphing():
    """Visualizing systems of equations graphically."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Systems of Equations - Graphical Interpretation",
        requirements="""
        Show three possible outcomes for two linear equations:

        1. ONE SOLUTION (intersecting lines)
           y = 2x + 1
           y = -x + 4
           Lines cross at one point - show the intersection

        2. NO SOLUTION (parallel lines)
           y = 2x + 1
           y = 2x - 3
           Same slope, different y-intercept - never meet

        3. INFINITE SOLUTIONS (same line)
           y = 2x + 1
           2y = 4x + 2 (same equation!)
           Lines overlap completely

        Graph each case and explain what the solution means geometrically.
        """,
        audience_level="high school",
        output_filename="hs_systems_graphing"
    )


# =============================================================================
# QUADRATIC EQUATIONS (Algebra 1-2)
# =============================================================================

def quadratic_standard_form():
    """Understanding quadratic functions in standard form."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Quadratic Functions: f(x) = ax² + bx + c",
        requirements="""
        1. Introduce the standard form: f(x) = ax² + bx + c

        2. Key features of a parabola:
           - If a > 0: opens upward (smile) ∪
           - If a < 0: opens downward (frown) ∩
           - Vertex: the turning point
           - Axis of symmetry: vertical line through vertex
           - y-intercept: the point (0, c)

        3. Show effect of 'a':
           - f(x) = x² (standard)
           - f(x) = 2x² (narrower)
           - f(x) = 0.5x² (wider)
           - f(x) = -x² (flipped)

        4. Finding vertex: x = -b/(2a)
           Example: f(x) = x² - 4x + 3
           x = -(-4)/(2·1) = 2
           f(2) = 4 - 8 + 3 = -1
           Vertex: (2, -1)

        Animate the parabola changing as 'a' changes.
        """,
        audience_level="high school",
        output_filename="hs_quadratic_standard"
    )


def factoring_quadratics():
    """Factoring quadratic expressions."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Factoring Quadratic Expressions",
        requirements="""
        Factor x² + 5x + 6:

        1. Find two numbers that:
           - Multiply to give 6 (the c term)
           - Add to give 5 (the b term)
           Numbers: 2 and 3

        2. Write as: (x + 2)(x + 3)

        3. Verify using FOIL:
           F: x·x = x²
           O: x·3 = 3x
           I: 2·x = 2x
           L: 2·3 = 6
           Total: x² + 5x + 6 ✓

        More examples:
        - x² - 7x + 12 = (x - 3)(x - 4)
        - x² + 2x - 15 = (x + 5)(x - 3)
        - x² - 9 = (x + 3)(x - 3)  [difference of squares]

        Show the "X method" or diamond method visually.
        """,
        audience_level="high school",
        output_filename="hs_factoring_quadratics"
    )


def quadratic_formula():
    """The quadratic formula and its derivation."""
    engine = MathContentEngine()
    return engine.generate(
        topic="The Quadratic Formula",
        requirements="""
        For ax² + bx + c = 0, the solutions are:
        x = (-b ± √(b² - 4ac)) / (2a)

        1. Show the formula prominently

        2. Derive from completing the square:
           ax² + bx + c = 0
           x² + (b/a)x = -c/a
           x² + (b/a)x + (b/2a)² = -c/a + (b/2a)²
           (x + b/2a)² = (b² - 4ac)/(4a²)
           x + b/2a = ±√(b² - 4ac)/(2a)
           x = (-b ± √(b² - 4ac))/(2a)

        3. Example: Solve 2x² + 5x - 3 = 0
           a = 2, b = 5, c = -3
           x = (-5 ± √(25 + 24))/4
           x = (-5 ± √49)/4
           x = (-5 ± 7)/4
           x = 1/2 or x = -3

        Color code a, b, c in the original and formula.
        """,
        audience_level="high school",
        output_filename="hs_quadratic_formula"
    )


def discriminant():
    """The discriminant and nature of roots."""
    engine = MathContentEngine()
    return engine.generate(
        topic="The Discriminant: b² - 4ac",
        requirements="""
        The discriminant D = b² - 4ac tells us about the solutions:

        1. D > 0: Two distinct real solutions
           Example: x² - 5x + 6 = 0
           D = 25 - 24 = 1 > 0
           Graph: parabola crosses x-axis twice

        2. D = 0: One repeated real solution
           Example: x² - 6x + 9 = 0
           D = 36 - 36 = 0
           Graph: parabola touches x-axis once (vertex on x-axis)

        3. D < 0: No real solutions (two complex solutions)
           Example: x² + x + 1 = 0
           D = 1 - 4 = -3 < 0
           Graph: parabola doesn't touch x-axis

        Show all three cases with their graphs.
        Animate the discriminant calculation for each.
        """,
        audience_level="high school",
        output_filename="hs_discriminant"
    )


def completing_the_square():
    """Completing the square technique."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Completing the Square",
        requirements="""
        Convert x² + 6x + 5 to vertex form (x - h)² + k:

        1. Start: x² + 6x + 5

        2. Focus on first two terms: x² + 6x
           Take half of 6: 6/2 = 3
           Square it: 3² = 9

        3. Add and subtract 9:
           x² + 6x + 9 - 9 + 5

        4. First three terms form perfect square:
           (x + 3)² - 9 + 5
           (x + 3)² - 4

        5. Vertex form: (x + 3)² - 4
           Vertex: (-3, -4)

        Show the geometric meaning: literally completing a square.
        Draw the square with sides x and 3.
        """,
        audience_level="high school",
        output_filename="hs_completing_square"
    )


# =============================================================================
# POLYNOMIALS (Algebra 2)
# =============================================================================

def polynomial_operations():
    """Adding, subtracting, and multiplying polynomials."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Polynomial Operations",
        requirements="""
        1. ADDING POLYNOMIALS:
           (3x² + 2x - 5) + (x² - 4x + 3)
           Combine like terms: 4x² - 2x - 2

        2. SUBTRACTING POLYNOMIALS:
           (3x² + 2x - 5) - (x² - 4x + 3)
           Distribute the negative: 3x² + 2x - 5 - x² + 4x - 3
           Combine: 2x² + 6x - 8

        3. MULTIPLYING POLYNOMIALS:
           (x + 2)(x² - 3x + 4)
           Distribute each term:
           x(x² - 3x + 4) + 2(x² - 3x + 4)
           = x³ - 3x² + 4x + 2x² - 6x + 8
           = x³ - x² - 2x + 8

        Use arrows to show distribution.
        Color code terms being combined.
        """,
        audience_level="high school",
        output_filename="hs_polynomial_operations"
    )


def polynomial_division():
    """Long division and synthetic division of polynomials."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Polynomial Long Division",
        requirements="""
        Divide (2x³ + 3x² - 5x + 4) by (x + 2):

        Step-by-step long division:
        1. Divide leading terms: 2x³ ÷ x = 2x²
        2. Multiply: 2x²(x + 2) = 2x³ + 4x²
        3. Subtract: (2x³ + 3x²) - (2x³ + 4x²) = -x²
        4. Bring down: -x² - 5x
        5. Divide: -x² ÷ x = -x
        6. Multiply: -x(x + 2) = -x² - 2x
        7. Subtract: (-x² - 5x) - (-x² - 2x) = -3x
        8. Bring down: -3x + 4
        9. Divide: -3x ÷ x = -3
        10. Multiply: -3(x + 2) = -3x - 6
        11. Subtract: (-3x + 4) - (-3x - 6) = 10

        Result: 2x² - x - 3 + 10/(x+2)

        Show the long division format step by step.
        """,
        audience_level="high school",
        output_filename="hs_polynomial_division"
    )


def factoring_special_forms():
    """Special factoring patterns."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Special Factoring Patterns",
        requirements="""
        1. DIFFERENCE OF SQUARES:
           a² - b² = (a + b)(a - b)
           Example: x² - 16 = (x + 4)(x - 4)
           Example: 4x² - 9 = (2x + 3)(2x - 3)

        2. PERFECT SQUARE TRINOMIALS:
           a² + 2ab + b² = (a + b)²
           a² - 2ab + b² = (a - b)²
           Example: x² + 6x + 9 = (x + 3)²
           Example: x² - 10x + 25 = (x - 5)²

        3. SUM/DIFFERENCE OF CUBES:
           a³ + b³ = (a + b)(a² - ab + b²)
           a³ - b³ = (a - b)(a² + ab + b²)
           Example: x³ + 8 = (x + 2)(x² - 2x + 4)
           Example: x³ - 27 = (x - 3)(x² + 3x + 9)

        Show each pattern with geometric visualization where possible.
        """,
        audience_level="high school",
        output_filename="hs_special_factoring"
    )


# =============================================================================
# RATIONAL EXPRESSIONS (Algebra 2)
# =============================================================================

def simplifying_rationals():
    """Simplifying rational expressions."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Simplifying Rational Expressions",
        requirements="""
        Simplify: (x² - 9)/(x² + 5x + 6)

        Step by step:
        1. Factor numerator: x² - 9 = (x + 3)(x - 3)
        2. Factor denominator: x² + 5x + 6 = (x + 2)(x + 3)
        3. Rewrite: [(x + 3)(x - 3)] / [(x + 2)(x + 3)]
        4. Cancel common factor (x + 3):
           = (x - 3)/(x + 2)
        5. State restriction: x ≠ -3, x ≠ -2

        Another example: (2x² + 6x)/(x² + 3x)
        = 2x(x + 3) / x(x + 3)
        = 2 (for x ≠ 0, x ≠ -3)

        Show the factoring, then animate cancellation.
        Emphasize domain restrictions.
        """,
        audience_level="high school",
        output_filename="hs_simplifying_rationals"
    )


def multiplying_rationals():
    """Multiplying and dividing rational expressions."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Multiplying and Dividing Rational Expressions",
        requirements="""
        MULTIPLICATION:
        (x² - 4)/(x + 3) × (x + 3)/(x - 2)

        1. Factor: [(x+2)(x-2)]/(x+3) × (x+3)/(x-2)
        2. Multiply: [(x+2)(x-2)(x+3)] / [(x+3)(x-2)]
        3. Cancel: = x + 2

        DIVISION (flip and multiply):
        (x² - 1)/(x + 2) ÷ (x - 1)/(x² + 4x + 4)

        1. Flip second fraction:
           = (x² - 1)/(x + 2) × (x² + 4x + 4)/(x - 1)

        2. Factor everything:
           = [(x+1)(x-1)]/(x+2) × [(x+2)²]/(x-1)

        3. Cancel and simplify:
           = (x + 1)(x + 2)

        Show the "Keep-Change-Flip" for division.
        """,
        audience_level="high school",
        output_filename="hs_mult_div_rationals"
    )


def adding_rationals():
    """Adding and subtracting rational expressions."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Adding and Subtracting Rational Expressions",
        requirements="""
        Add: 3/(x+1) + 2/(x-1)

        1. Find LCD: (x+1)(x-1)

        2. Rewrite each fraction:
           3(x-1)/[(x+1)(x-1)] + 2(x+1)/[(x+1)(x-1)]

        3. Add numerators:
           [3(x-1) + 2(x+1)] / [(x+1)(x-1)]

        4. Expand and simplify:
           [3x - 3 + 2x + 2] / [(x+1)(x-1)]
           = (5x - 1)/(x² - 1)

        Subtract: x/(x+2) - 3/(x-2)
        LCD: (x+2)(x-2)
        = [x(x-2) - 3(x+2)] / [(x+2)(x-2)]
        = (x² - 5x - 6) / (x² - 4)

        Show finding LCD and building equivalent fractions.
        """,
        audience_level="high school",
        output_filename="hs_add_sub_rationals"
    )


# =============================================================================
# RADICALS AND EXPONENTS (Algebra 2)
# =============================================================================

def exponent_rules():
    """Laws of exponents."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Laws of Exponents",
        requirements="""
        The Seven Exponent Rules:

        1. Product Rule: aᵐ · aⁿ = aᵐ⁺ⁿ
           Example: x³ · x⁴ = x⁷

        2. Quotient Rule: aᵐ / aⁿ = aᵐ⁻ⁿ
           Example: x⁵ / x² = x³

        3. Power Rule: (aᵐ)ⁿ = aᵐⁿ
           Example: (x²)³ = x⁶

        4. Zero Exponent: a⁰ = 1 (a ≠ 0)
           Example: 5⁰ = 1

        5. Negative Exponent: a⁻ⁿ = 1/aⁿ
           Example: x⁻² = 1/x²

        6. Product to Power: (ab)ⁿ = aⁿbⁿ
           Example: (2x)³ = 8x³

        7. Quotient to Power: (a/b)ⁿ = aⁿ/bⁿ
           Example: (x/3)² = x²/9

        Show each rule with a visual proof using repeated multiplication.
        """,
        audience_level="high school",
        output_filename="hs_exponent_rules"
    )


def simplifying_radicals():
    """Simplifying radical expressions."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Simplifying Radical Expressions",
        requirements="""
        1. BASIC SIMPLIFICATION:
           √72 = √(36 × 2) = √36 × √2 = 6√2
           √50 = √(25 × 2) = 5√2

        2. VARIABLES:
           √(x⁶) = x³
           √(x⁷) = √(x⁶ · x) = x³√x
           √(18x⁴y³) = √(9 · 2 · x⁴ · y² · y) = 3x²y√(2y)

        3. RATIONALIZING DENOMINATORS:
           5/√3 = (5 × √3)/(√3 × √3) = 5√3/3

           3/(√5 - 2) = 3(√5 + 2)/[(√5 - 2)(√5 + 2)]
                      = 3(√5 + 2)/(5 - 4) = 3√5 + 6

        4. ADDING RADICALS:
           3√2 + 5√2 = 8√2
           √12 + √27 = 2√3 + 3√3 = 5√3

        Show factor trees for finding perfect square factors.
        """,
        audience_level="high school",
        output_filename="hs_simplifying_radicals"
    )


def rational_exponents():
    """Rational (fractional) exponents."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Rational Exponents",
        requirements="""
        Connection between radicals and exponents:

        1. DEFINITION:
           a^(1/n) = ⁿ√a
           a^(m/n) = ⁿ√(aᵐ) = (ⁿ√a)ᵐ

        2. EXAMPLES:
           8^(1/3) = ³√8 = 2
           27^(2/3) = (³√27)² = 3² = 9
           16^(3/4) = (⁴√16)³ = 2³ = 8

        3. NEGATIVE RATIONAL EXPONENTS:
           8^(-2/3) = 1/8^(2/3) = 1/4

        4. SIMPLIFYING:
           x^(1/2) · x^(1/3) = x^(1/2 + 1/3) = x^(5/6)
           (x^(2/3))^(3/4) = x^(2/3 · 3/4) = x^(1/2)

        Show the equivalence between radical and exponential forms.
        Convert between forms in both directions.
        """,
        audience_level="high school",
        output_filename="hs_rational_exponents"
    )


# =============================================================================
# FUNCTIONS (Algebra 2)
# =============================================================================

def function_notation():
    """Understanding function notation."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Function Notation and Evaluation",
        requirements="""
        1. WHAT IS A FUNCTION?
           - Each input has exactly one output
           - f(x) means "f of x" - the output when input is x
           - x is the input, f(x) is the output

        2. EVALUATING FUNCTIONS:
           Given f(x) = 2x² - 3x + 1

           f(2) = 2(2)² - 3(2) + 1 = 8 - 6 + 1 = 3
           f(-1) = 2(-1)² - 3(-1) + 1 = 2 + 3 + 1 = 6
           f(a) = 2a² - 3a + 1

        3. OPERATIONS WITH FUNCTIONS:
           If f(x) = x + 3 and g(x) = x²:
           (f + g)(x) = x + 3 + x² = x² + x + 3
           (f · g)(x) = (x + 3)(x²) = x³ + 3x²
           f(g(x)) = g(x) + 3 = x² + 3

        4. DOMAIN:
           What values of x are allowed?
           f(x) = 1/x, domain: x ≠ 0
           g(x) = √x, domain: x ≥ 0

        Use input-output machine visualization.
        """,
        audience_level="high school",
        output_filename="hs_function_notation"
    )


def function_transformations():
    """Transformations of function graphs."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Function Transformations",
        requirements="""
        Start with parent function f(x) = x²

        1. VERTICAL SHIFTS:
           f(x) + k: shifts UP k units
           f(x) - k: shifts DOWN k units
           Show: x² + 3 (up 3) and x² - 2 (down 2)

        2. HORIZONTAL SHIFTS:
           f(x - h): shifts RIGHT h units
           f(x + h): shifts LEFT h units
           Show: (x - 2)² (right 2) and (x + 3)² (left 3)
           Note: opposite of what you might expect!

        3. REFLECTIONS:
           -f(x): reflects over x-axis
           f(-x): reflects over y-axis
           Show: -x² (flip vertically)

        4. STRETCHES/COMPRESSIONS:
           af(x): vertical stretch (a > 1) or compression (0 < a < 1)
           Show: 2x² (stretch) and 0.5x² (compress)

        Animate each transformation from the original function.
        Show before and after for each transformation.
        """,
        audience_level="high school",
        output_filename="hs_transformations"
    )


def inverse_functions():
    """Finding and graphing inverse functions."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Inverse Functions",
        requirements="""
        1. DEFINITION:
           f⁻¹(x) "undoes" what f(x) does
           If f(a) = b, then f⁻¹(b) = a
           f(f⁻¹(x)) = x and f⁻¹(f(x)) = x

        2. FINDING INVERSE:
           Find inverse of f(x) = 2x + 3:
           Step 1: Write y = 2x + 3
           Step 2: Swap x and y: x = 2y + 3
           Step 3: Solve for y: x - 3 = 2y → y = (x-3)/2
           f⁻¹(x) = (x - 3)/2

        3. VERIFY:
           f(f⁻¹(x)) = 2[(x-3)/2] + 3 = (x-3) + 3 = x ✓

        4. GRAPHING:
           Inverse is reflection over line y = x
           Show f(x) = 2x + 3 and f⁻¹(x) = (x-3)/2
           with line y = x

        5. HORIZONTAL LINE TEST:
           Function has inverse only if one-to-one
           (passes horizontal line test)

        Animate swapping x and y coordinates.
        Show reflection over y = x line.
        """,
        audience_level="high school",
        output_filename="hs_inverse_functions"
    )


# =============================================================================
# EXPONENTIALS AND LOGARITHMS (Algebra 2)
# =============================================================================

def exponential_functions():
    """Introduction to exponential functions."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Exponential Functions: f(x) = aˣ",
        requirements="""
        1. DEFINITION:
           f(x) = aˣ where a > 0, a ≠ 1

        2. GROWTH vs DECAY:
           - a > 1: exponential growth (2ˣ)
           - 0 < a < 1: exponential decay (0.5ˣ)

        3. KEY FEATURES:
           - Always passes through (0, 1)
           - Horizontal asymptote: y = 0
           - Domain: all real numbers
           - Range: y > 0

        4. NATURAL EXPONENTIAL:
           f(x) = eˣ where e ≈ 2.718
           Most important exponential function

        5. TRANSFORMATIONS:
           f(x) = 2ˣ⁺¹ + 3
           - Shift left 1, up 3
           - New asymptote: y = 3

        Graph y = 2ˣ, y = 3ˣ, y = (1/2)ˣ on same axes.
        Show the asymptote and key points.
        """,
        audience_level="high school",
        output_filename="hs_exponential_functions"
    )


def logarithm_introduction():
    """Introduction to logarithms."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Introduction to Logarithms",
        requirements="""
        1. DEFINITION:
           log_a(x) = y means aʸ = x
           "What power of a gives x?"

        2. EXAMPLES:
           log₂(8) = 3 because 2³ = 8
           log₃(81) = 4 because 3⁴ = 81
           log₁₀(1000) = 3 because 10³ = 1000

        3. CONVERTING:
           Exponential ↔ Logarithmic
           2⁵ = 32 ↔ log₂(32) = 5
           10² = 100 ↔ log₁₀(100) = 2

        4. SPECIAL LOGS:
           log(x) = log₁₀(x) (common log)
           ln(x) = log_e(x) (natural log)

        5. KEY VALUES:
           log_a(1) = 0 (because a⁰ = 1)
           log_a(a) = 1 (because a¹ = a)
           log_a(aˣ) = x

        Show log as inverse of exponential graphically.
        Animate converting between forms.
        """,
        audience_level="high school",
        output_filename="hs_logarithms_intro"
    )


def logarithm_properties():
    """Properties of logarithms."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Properties of Logarithms",
        requirements="""
        The Three Main Properties:

        1. PRODUCT RULE:
           log_a(MN) = log_a(M) + log_a(N)
           Example: log₂(8 × 4) = log₂(8) + log₂(4) = 3 + 2 = 5

        2. QUOTIENT RULE:
           log_a(M/N) = log_a(M) - log_a(N)
           Example: log₃(81/9) = log₃(81) - log₃(9) = 4 - 2 = 2

        3. POWER RULE:
           log_a(Mⁿ) = n · log_a(M)
           Example: log₂(4³) = 3 · log₂(4) = 3 × 2 = 6

        EXPANDING:
        log(x²y/z) = log(x²) + log(y) - log(z)
                   = 2log(x) + log(y) - log(z)

        CONDENSING:
        3log(x) + log(y) - 2log(z) = log(x³y/z²)

        Show proofs using exponential definitions.
        Practice expanding and condensing.
        """,
        audience_level="high school",
        output_filename="hs_log_properties"
    )


def solving_exponential_equations():
    """Solving exponential and logarithmic equations."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Solving Exponential and Logarithmic Equations",
        requirements="""
        EXPONENTIAL EQUATIONS:

        1. Same base method:
           2ˣ⁺¹ = 8
           2ˣ⁺¹ = 2³
           x + 1 = 3
           x = 2

        2. Using logarithms:
           5ˣ = 12
           log(5ˣ) = log(12)
           x · log(5) = log(12)
           x = log(12)/log(5) ≈ 1.544

        LOGARITHMIC EQUATIONS:

        1. Convert to exponential:
           log₂(x) = 5
           x = 2⁵ = 32

        2. Using properties:
           log(x) + log(x-3) = 1
           log(x(x-3)) = 1
           x(x-3) = 10
           x² - 3x - 10 = 0
           (x-5)(x+2) = 0
           x = 5 (reject x = -2)

        Show checking for extraneous solutions.
        """,
        audience_level="high school",
        output_filename="hs_solving_exp_log"
    )


# =============================================================================
# SEQUENCES AND SERIES (Algebra 2)
# =============================================================================

def arithmetic_sequences():
    """Arithmetic sequences and series."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Arithmetic Sequences and Series",
        requirements="""
        1. DEFINITION:
           Common difference d between consecutive terms
           Example: 2, 5, 8, 11, 14, ... (d = 3)

        2. EXPLICIT FORMULA:
           aₙ = a₁ + (n-1)d
           Example: a₁ = 2, d = 3
           a₁₀ = 2 + (10-1)(3) = 2 + 27 = 29

        3. SUM FORMULA:
           Sₙ = n(a₁ + aₙ)/2 = n[2a₁ + (n-1)d]/2
           Sum of first 10 terms:
           S₁₀ = 10(2 + 29)/2 = 10(31)/2 = 155

        4. FINDING d and a₁:
           Given a₃ = 7 and a₇ = 19
           a₇ - a₃ = 4d → 19 - 7 = 4d → d = 3
           a₃ = a₁ + 2d → 7 = a₁ + 6 → a₁ = 1

        Visualize adding d to get each term.
        Show the pairing method for sum (Gauss's trick).
        """,
        audience_level="high school",
        output_filename="hs_arithmetic_sequences"
    )


def geometric_sequences():
    """Geometric sequences and series."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Geometric Sequences and Series",
        requirements="""
        1. DEFINITION:
           Common ratio r between consecutive terms
           Example: 3, 6, 12, 24, 48, ... (r = 2)

        2. EXPLICIT FORMULA:
           aₙ = a₁ · rⁿ⁻¹
           Example: a₁ = 3, r = 2
           a₆ = 3 · 2⁵ = 3 · 32 = 96

        3. FINITE SUM:
           Sₙ = a₁(1 - rⁿ)/(1 - r) for r ≠ 1
           Sum of first 5 terms:
           S₅ = 3(1 - 2⁵)/(1 - 2) = 3(-31)/(-1) = 93

        4. INFINITE SUM (|r| < 1):
           S∞ = a₁/(1 - r)
           Example: 1 + 1/2 + 1/4 + 1/8 + ...
           S∞ = 1/(1 - 1/2) = 1/(1/2) = 2

        Show the multiplying pattern visually.
        Demonstrate infinite sum convergence graphically.
        """,
        audience_level="high school",
        output_filename="hs_geometric_sequences"
    )


# =============================================================================
# COMPLEX NUMBERS (Algebra 2)
# =============================================================================

def complex_numbers():
    """Introduction to complex numbers."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Complex Numbers: a + bi",
        requirements="""
        1. THE IMAGINARY UNIT:
           i = √(-1)
           i² = -1
           i³ = -i
           i⁴ = 1 (pattern repeats)

        2. COMPLEX NUMBERS:
           a + bi where a is real part, b is imaginary part
           Examples: 3 + 2i, -1 - 4i, 5i, 7

        3. OPERATIONS:
           Addition: (3 + 2i) + (1 - 4i) = 4 - 2i
           Subtraction: (3 + 2i) - (1 - 4i) = 2 + 6i
           Multiplication: (2 + 3i)(1 - 2i)
                        = 2 - 4i + 3i - 6i²
                        = 2 - i + 6 = 8 - i

        4. COMPLEX CONJUGATE:
           Conjugate of a + bi is a - bi
           (a + bi)(a - bi) = a² + b² (always real!)

        5. DIVISION:
           (3 + 2i)/(1 - i)
           Multiply by conjugate:
           = (3 + 2i)(1 + i)/[(1 - i)(1 + i)]
           = (3 + 3i + 2i + 2i²)/(1 + 1)
           = (1 + 5i)/2 = 1/2 + 5i/2

        Show complex plane visualization (real vs imaginary axis).
        """,
        audience_level="high school",
        output_filename="hs_complex_numbers"
    )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def run_all_examples():
    """Run all high school algebra examples."""
    examples = [
        # Linear Equations
        ("Slope-Intercept Form", slope_intercept_form),
        ("Point-Slope Form", point_slope_form),
        ("Systems - Substitution", systems_substitution),
        ("Systems - Elimination", systems_elimination),
        ("Systems - Graphing", systems_graphing),
        # Quadratics
        ("Quadratic Standard Form", quadratic_standard_form),
        ("Factoring Quadratics", factoring_quadratics),
        ("Quadratic Formula", quadratic_formula),
        ("Discriminant", discriminant),
        ("Completing the Square", completing_the_square),
        # Polynomials
        ("Polynomial Operations", polynomial_operations),
        ("Polynomial Division", polynomial_division),
        ("Special Factoring", factoring_special_forms),
        # Rationals
        ("Simplifying Rationals", simplifying_rationals),
        ("Multiplying Rationals", multiplying_rationals),
        ("Adding Rationals", adding_rationals),
        # Radicals/Exponents
        ("Exponent Rules", exponent_rules),
        ("Simplifying Radicals", simplifying_radicals),
        ("Rational Exponents", rational_exponents),
        # Functions
        ("Function Notation", function_notation),
        ("Transformations", function_transformations),
        ("Inverse Functions", inverse_functions),
        # Exp/Log
        ("Exponential Functions", exponential_functions),
        ("Logarithm Introduction", logarithm_introduction),
        ("Logarithm Properties", logarithm_properties),
        ("Solving Exp/Log Equations", solving_exponential_equations),
        # Sequences
        ("Arithmetic Sequences", arithmetic_sequences),
        ("Geometric Sequences", geometric_sequences),
        # Complex Numbers
        ("Complex Numbers", complex_numbers),
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
    print("High School Algebra Examples (Grades 9-12)")
    print("="*60)
    print("""
Available examples:

LINEAR EQUATIONS (Algebra 1):
  - slope_intercept_form()
  - point_slope_form()
  - systems_substitution()
  - systems_elimination()
  - systems_graphing()

QUADRATIC EQUATIONS (Algebra 1-2):
  - quadratic_standard_form()
  - factoring_quadratics()
  - quadratic_formula()
  - discriminant()
  - completing_the_square()

POLYNOMIALS (Algebra 2):
  - polynomial_operations()
  - polynomial_division()
  - factoring_special_forms()

RATIONAL EXPRESSIONS (Algebra 2):
  - simplifying_rationals()
  - multiplying_rationals()
  - adding_rationals()

RADICALS AND EXPONENTS (Algebra 2):
  - exponent_rules()
  - simplifying_radicals()
  - rational_exponents()

FUNCTIONS (Algebra 2):
  - function_notation()
  - function_transformations()
  - inverse_functions()

EXPONENTIALS AND LOGARITHMS (Algebra 2):
  - exponential_functions()
  - logarithm_introduction()
  - logarithm_properties()
  - solving_exponential_equations()

SEQUENCES AND SERIES (Algebra 2):
  - arithmetic_sequences()
  - geometric_sequences()

COMPLEX NUMBERS (Algebra 2):
  - complex_numbers()

To generate all examples:
  run_all_examples()
""")


if __name__ == "__main__":
    main()
