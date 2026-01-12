#!/usr/bin/env python3
"""
Topic-specific examples for Math Content Engine.

This file demonstrates generating animations for various math topics
across different educational levels.
"""

import logging
from math_content_engine import MathContentEngine

logging.basicConfig(level=logging.INFO)


# =============================================================================
# ALGEBRA EXAMPLES
# =============================================================================

def algebra_linear_equations():
    """Solving linear equations."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Solving linear equations: 2x + 5 = 13",
        requirements="""
        Show step-by-step solution:
        1. Start with the equation
        2. Subtract 5 from both sides
        3. Divide by 2
        4. Show final answer x = 4
        5. Verify by substitution
        Use color coding for operations on each side.
        """,
        audience_level="middle school",
        output_filename="algebra_linear_eq"
    )


def algebra_factoring():
    """Factoring quadratic expressions."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Factoring x² + 5x + 6",
        requirements="""
        Show the FOIL method in reverse.
        Find factors of 6 that sum to 5.
        Demonstrate (x + 2)(x + 3) expansion to verify.
        """,
        audience_level="high school",
        output_filename="algebra_factoring"
    )


# =============================================================================
# GEOMETRY EXAMPLES
# =============================================================================

def geometry_triangle_angles():
    """Sum of angles in a triangle."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Prove that angles in a triangle sum to 180°",
        requirements="""
        Draw a triangle with labeled angles α, β, γ.
        Draw a parallel line through one vertex.
        Use alternate angles to show the proof.
        Animate the angles coming together to form a straight line.
        """,
        audience_level="middle school",
        output_filename="geometry_triangle_angles"
    )


def geometry_circle_theorems():
    """Inscribed angle theorem."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Inscribed angle theorem: angle at center is twice angle at circumference",
        requirements="""
        Draw a circle with center O.
        Show an arc and both the central angle and inscribed angle.
        Animate to show the 2:1 relationship.
        Include the formula.
        """,
        audience_level="high school",
        output_filename="geometry_inscribed_angle"
    )


# =============================================================================
# CALCULUS EXAMPLES
# =============================================================================

def calculus_limits():
    """Introduction to limits."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Understanding limits: lim(x→2) (x² - 4)/(x - 2)",
        requirements="""
        Show the function graph with a hole at x=2.
        Animate points approaching x=2 from both sides.
        Show the table of values getting closer.
        Reveal the limit equals 4.
        Factor to show (x+2)(x-2)/(x-2) = x+2.
        """,
        audience_level="college",
        output_filename="calculus_limits"
    )


def calculus_area_under_curve():
    """Riemann sums and integration."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Area under a curve using Riemann sums",
        requirements="""
        Show f(x) = x² from 0 to 2.
        Start with 4 rectangles.
        Animate increasing to 8, then 16 rectangles.
        Show the sum converging to the integral.
        Display ∫₀² x² dx = 8/3.
        """,
        audience_level="college",
        output_filename="calculus_riemann"
    )


# =============================================================================
# TRIGONOMETRY EXAMPLES
# =============================================================================

def trig_identities():
    """Pythagorean identity."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Pythagorean identity: sin²θ + cos²θ = 1",
        requirements="""
        Start with unit circle.
        Show a point at angle θ.
        Draw the right triangle with legs sin(θ) and cos(θ).
        Apply Pythagorean theorem.
        Show the identity holds for multiple angles.
        """,
        audience_level="high school",
        output_filename="trig_pythagorean"
    )


def trig_graphs():
    """Graphing trigonometric functions."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Comparing sine, cosine, and tangent graphs",
        requirements="""
        Show all three functions on the same coordinate plane.
        Use different colors: sin=blue, cos=red, tan=green.
        Mark key points: zeros, maxima, minima.
        Show period and amplitude for each.
        Highlight asymptotes for tangent.
        """,
        audience_level="high school",
        output_filename="trig_graphs"
    )


# =============================================================================
# STATISTICS EXAMPLES
# =============================================================================

def stats_normal_distribution():
    """Normal distribution and standard deviation."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Normal distribution and the 68-95-99.7 rule",
        requirements="""
        Draw the bell curve.
        Mark mean (μ) at center.
        Show 1σ, 2σ, 3σ regions with different colors.
        Display percentages: 68%, 95%, 99.7%.
        Animate shading each region.
        """,
        audience_level="high school",
        output_filename="stats_normal"
    )


# =============================================================================
# LINEAR ALGEBRA EXAMPLES
# =============================================================================

def linalg_vectors():
    """Vector addition."""
    engine = MathContentEngine()
    return engine.generate(
        topic="Vector addition: geometric interpretation",
        requirements="""
        Show two vectors u and v in 2D.
        Demonstrate head-to-tail method.
        Show parallelogram method.
        Display u + v = v + u (commutativity).
        Include component form calculation.
        """,
        audience_level="college",
        output_filename="linalg_vectors"
    )


def linalg_matrix_transform():
    """Matrix transformations."""
    engine = MathContentEngine()
    return engine.generate(
        topic="2D matrix transformations: rotation and scaling",
        requirements="""
        Start with a square.
        Show rotation matrix and animate rotation.
        Show scaling matrix and animate scaling.
        Combine transformations.
        Display the matrices being applied.
        """,
        audience_level="college",
        output_filename="linalg_transform"
    )


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Run selected topic examples."""
    print("Math Content Engine - Topic Examples")
    print("="*60)
    print("\nAvailable examples by category:")
    print("\nALGEBRA:")
    print("  - algebra_linear_equations()")
    print("  - algebra_factoring()")
    print("\nGEOMETRY:")
    print("  - geometry_triangle_angles()")
    print("  - geometry_circle_theorems()")
    print("\nCALCULUS:")
    print("  - calculus_limits()")
    print("  - calculus_area_under_curve()")
    print("\nTRIGONOMETRY:")
    print("  - trig_identities()")
    print("  - trig_graphs()")
    print("\nSTATISTICS:")
    print("  - stats_normal_distribution()")
    print("\nLINEAR ALGEBRA:")
    print("  - linalg_vectors()")
    print("  - linalg_matrix_transform()")
    print("\n" + "="*60)
    print("Import this module and call any function to generate that animation.")
    print("Example:")
    print("  from examples.topic_examples import calculus_limits")
    print("  result = calculus_limits()")
    print("="*60)


if __name__ == "__main__":
    main()
