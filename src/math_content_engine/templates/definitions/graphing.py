"""
Graphing and coordinate geometry templates.

Templates for visualizing:
- Slope as rise/run
- Slope-intercept form (y = mx + b)
- Plotting points
- Systems of equations
"""

import math
from ..base import ManimTemplate, ParamSpec, ParamType, TemplateCategory


def compute_slope_derived(params: dict) -> dict:
    """Compute derived parameters for slope visualization."""
    x1, y1 = params.get("x1", 1), params.get("y1", 2)
    x2, y2 = params.get("x2", 4), params.get("y2", 5)

    rise = y2 - y1
    run = x2 - x1
    slope = rise / run if run != 0 else float('inf')

    # Format slope as fraction or decimal
    if slope == int(slope):
        slope_display = str(int(slope))
    elif run != 0 and abs(rise) < 20 and abs(run) < 20:
        # Show as fraction
        slope_display = f"{rise}/{run}"
    else:
        slope_display = f"{slope:.2f}"

    x_min = min(-1, x1 - 2, x2 - 2)
    x_max = max(7, x1 + 3, x2 + 3)
    y_min = min(-1, y1 - 2, y2 - 2)
    y_max = max(7, y1 + 3, y2 + 3)

    return {
        "rise": rise,
        "run": run,
        "slope": slope,
        "slope_display": slope_display,
        "x_min": int(x_min),
        "x_max": int(x_max),
        "y_min": int(y_min),
        "y_max": int(y_max),
    }


def compute_slope_intercept_derived(params: dict) -> dict:
    """Compute derived parameters for slope-intercept form."""
    m = params.get("m", 1)
    b = params.get("b", 0)

    # Compute axis ranges
    x_min = -2
    x_max = 6
    y_at_xmin = m * x_min + b
    y_at_xmax = m * x_max + b
    y_min = min(-2, y_at_xmin - 1, b - 2)
    y_max = max(8, y_at_xmax + 1, b + 4)

    return {
        "x_min": x_min,
        "x_max": x_max,
        "y_min": int(y_min),
        "y_max": int(y_max),
    }


def compute_system_derived(params: dict) -> dict:
    """Compute derived parameters for system of equations."""
    m1, b1 = params.get("m1", 2), params.get("b1", -1)
    m2, b2 = params.get("m2", -1), params.get("b2", 5)

    # Solve: m1*x + b1 = m2*x + b2 => x = (b2 - b1) / (m1 - m2)
    if m1 != m2:
        sol_x = (b2 - b1) / (m1 - m2)
        sol_y = m1 * sol_x + b1
        if sol_x == int(sol_x):
            sol_x = int(sol_x)
        if sol_y == int(sol_y):
            sol_y = int(sol_y)
    else:
        sol_x, sol_y = None, None

    x_min = -1
    x_max = 7
    y_vals = [m1 * x_min + b1, m1 * x_max + b1, m2 * x_min + b2, m2 * x_max + b2]
    y_min = min(-2, min(y_vals) - 1)
    y_max = max(8, max(y_vals) + 1)

    return {
        "sol_x": sol_x,
        "sol_y": sol_y,
        "x_min": x_min,
        "x_max": x_max,
        "y_min": int(y_min),
        "y_max": int(y_max),
    }


# =============================================================================
# Slope Visualization - Rise over Run
# =============================================================================
SLOPE_VISUALIZATION_TEMPLATE = '''from manim import *

class SlopeVisualizationScene(Scene):
    """Visualize slope as rise/run between points ({x1}, {y1}) and ({x2}, {y2})."""

    def construct(self):
        # Parameters
        x1, y1 = {x1}, {y1}
        x2, y2 = {x2}, {y2}
        rise, run = {rise}, {run}
        slope_display = "{slope_display}"

        # Title
        title = Text("Understanding Slope: Rise over Run", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP).scale(0.8))

        # Create coordinate axes
        axes = Axes(
            x_range=[{x_min}, {x_max}, 1],
            y_range=[{y_min}, {y_max}, 1],
            x_length=6,
            y_length=5,
            axis_config={{"include_numbers": False}},
        ).shift(DOWN * 0.3 + LEFT * 1)

        # Add labels
        x_nums = VGroup(*[
            Text(str(i), font_size=14).next_to(axes.c2p(i, 0), DOWN, buff=0.1)
            for i in range({x_min} + 1, {x_max})
        ])
        y_nums = VGroup(*[
            Text(str(i), font_size=14).next_to(axes.c2p(0, i), LEFT, buff=0.1)
            for i in range({y_min} + 1, {y_max}) if i != 0
        ])

        self.play(Create(axes))
        self.play(Write(x_nums), Write(y_nums))
        self.wait(1)

        # Plot the line through both points
        if run != 0:
            slope = rise / run
            line = axes.plot(
                lambda x: slope * (x - x1) + y1,
                x_range=[{x_min} + 0.5, {x_max} - 0.5],
                color=BLUE,
                stroke_width=3
            )
            self.play(Create(line))
            self.wait(1)

        # Show two points
        point1 = Dot(axes.c2p(x1, y1), color=YELLOW, radius=0.12)
        point2 = Dot(axes.c2p(x2, y2), color=YELLOW, radius=0.12)
        p1_label = Text(f"({x1}, {y1})", font_size=20).next_to(point1, DL, buff=0.1)
        p2_label = Text(f"({x2}, {y2})", font_size=20).next_to(point2, UR, buff=0.1)

        self.play(Create(point1), Write(p1_label))
        self.play(Create(point2), Write(p2_label))
        self.wait(1)

        # Draw rise/run triangle
        # Horizontal line (run)
        run_line = Line(axes.c2p(x1, y1), axes.c2p(x2, y1), color=RED, stroke_width=4)
        run_label = Text(f"Run = {run}", font_size=18, color=RED)
        run_label.next_to(run_line, DOWN, buff=0.1)

        self.play(Create(run_line), Write(run_label))
        self.wait(1)

        # Vertical line (rise)
        rise_line = Line(axes.c2p(x2, y1), axes.c2p(x2, y2), color=GREEN, stroke_width=4)
        rise_label = Text(f"Rise = {rise}", font_size=18, color=GREEN)
        rise_label.next_to(rise_line, RIGHT, buff=0.1)

        self.play(Create(rise_line), Write(rise_label))
        self.wait(1)

        # Show slope formula
        slope_formula = Text(f"Slope = Rise / Run = {slope_display}", font_size=28, color=ORANGE)
        slope_formula.to_edge(DOWN)
        self.play(Write(slope_formula))
        self.wait(1)

        # Explanation
        explanation = Text(f"For every {abs(run)} units right, go {abs(rise)} units {'up' if rise > 0 else 'down'}", font_size=20)
        explanation.next_to(slope_formula, UP, buff=0.3)
        self.play(Write(explanation))
        self.wait(2)
'''

slope_visualization = ManimTemplate(
    id="slope_visualization",
    name="Slope Visualization - Rise/Run",
    category=TemplateCategory.GRAPHING,
    description="Visualize slope as rise over run between two points",
    parameters=[
        ParamSpec(name="x1", param_type=ParamType.FLOAT, description="X coordinate of first point"),
        ParamSpec(name="y1", param_type=ParamType.FLOAT, description="Y coordinate of first point"),
        ParamSpec(name="x2", param_type=ParamType.FLOAT, description="X coordinate of second point"),
        ParamSpec(name="y2", param_type=ParamType.FLOAT, description="Y coordinate of second point"),
        ParamSpec(name="rise", param_type=ParamType.FLOAT, description="Rise (y2 - y1)", derived_from="y2 - y1"),
        ParamSpec(name="run", param_type=ParamType.FLOAT, description="Run (x2 - x1)", derived_from="x2 - x1"),
        ParamSpec(name="slope_display", param_type=ParamType.STRING, description="Slope as display string", derived_from="rise/run"),
        ParamSpec(name="x_min", param_type=ParamType.INT, required=False, default=-1, description="X axis minimum"),
        ParamSpec(name="x_max", param_type=ParamType.INT, required=False, default=7, description="X axis maximum"),
        ParamSpec(name="y_min", param_type=ParamType.INT, required=False, default=-1, description="Y axis minimum"),
        ParamSpec(name="y_max", param_type=ParamType.INT, required=False, default=7, description="Y axis maximum"),
    ],
    template_code=SLOPE_VISUALIZATION_TEMPLATE,
    example_questions=[
        "Find the slope between (1, 2) and (4, 8)",
        "What is the slope from (0, 1) to (3, 7)?",
        "Calculate slope of line through (2, 3) and (5, 9)",
    ],
    tags=["slope", "rise", "run", "points", "graph", "coordinate"],
    compute_derived=compute_slope_derived,
)


# =============================================================================
# Slope-Intercept Form - y = mx + b
# =============================================================================
SLOPE_INTERCEPT_TEMPLATE = '''from manim import *

class SlopeInterceptScene(Scene):
    """Graph y = {m}x + {b} showing slope and y-intercept."""

    def construct(self):
        # Parameters
        m, b = {m}, {b}

        # Title
        if b >= 0:
            title = Text(f"Graphing y = {m}x + {b}", font_size=36)
        else:
            title = Text(f"Graphing y = {m}x - {abs(b)}", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP).scale(0.8))

        # Create coordinate axes
        axes = Axes(
            x_range=[{x_min}, {x_max}, 1],
            y_range=[{y_min}, {y_max}, 2],
            x_length=6,
            y_length=5,
            axis_config={{"include_numbers": False}},
        ).shift(DOWN * 0.3)

        # Add labels
        x_nums = VGroup(*[
            Text(str(i), font_size=14).next_to(axes.c2p(i, 0), DOWN, buff=0.1)
            for i in range({x_min} + 1, {x_max}) if i != 0
        ])
        y_nums = VGroup(*[
            Text(str(i), font_size=14).next_to(axes.c2p(0, i), LEFT, buff=0.1)
            for i in range({y_min} + 1, {y_max}, 2) if i != 0
        ])

        x_label = Text("x", font_size=24).next_to(axes.x_axis, RIGHT)
        y_label = Text("y", font_size=24).next_to(axes.y_axis, UP)

        self.play(Create(axes), Write(x_label), Write(y_label))
        self.play(Write(x_nums), Write(y_nums))
        self.wait(1)

        # Step 1: Show y-intercept (0, b)
        intercept_label = Text(f"Step 1: Y-intercept at (0, {b})", font_size=22, color=GREEN)
        intercept_label.to_edge(RIGHT).shift(UP * 2)
        self.play(Write(intercept_label))

        y_intercept = Dot(axes.c2p(0, b), color=GREEN, radius=0.15)
        y_int_text = Text(f"(0, {b})", font_size=18, color=GREEN)
        y_int_text.next_to(y_intercept, LEFT, buff=0.2)

        self.play(Create(y_intercept), Write(y_int_text))
        self.play(Flash(y_intercept, color=GREEN))
        self.wait(1)

        # Step 2: Show slope (rise/run from y-intercept)
        slope_label = Text(f"Step 2: Slope m = {m} (rise/run)", font_size=22, color=BLUE)
        slope_label.next_to(intercept_label, DOWN, buff=0.3)
        self.play(Write(slope_label))

        # Draw rise/run from y-intercept
        run_line = Line(axes.c2p(0, b), axes.c2p(1, b), color=RED, stroke_width=3)
        rise_line = Line(axes.c2p(1, b), axes.c2p(1, b + m), color=ORANGE, stroke_width=3)

        run_text = Text("run = 1", font_size=16, color=RED)
        run_text.next_to(run_line, DOWN, buff=0.1)
        rise_text = Text(f"rise = {m}", font_size=16, color=ORANGE)
        rise_text.next_to(rise_line, RIGHT, buff=0.1)

        self.play(Create(run_line), Write(run_text))
        self.play(Create(rise_line), Write(rise_text))

        # Second point
        second_point = Dot(axes.c2p(1, b + m), color=YELLOW, radius=0.12)
        self.play(Create(second_point))
        self.wait(1)

        # Step 3: Draw the line
        step3_label = Text("Step 3: Draw the line", font_size=22, color=PURPLE)
        step3_label.next_to(slope_label, DOWN, buff=0.3)
        self.play(Write(step3_label))

        line = axes.plot(lambda x: m * x + b, x_range=[{x_min} + 0.5, {x_max} - 0.5], color=BLUE, stroke_width=3)
        self.play(Create(line))
        self.wait(1)

        # Equation label
        if b >= 0:
            eq_label = Text(f"y = {m}x + {b}", font_size=28, color=BLUE)
        else:
            eq_label = Text(f"y = {m}x - {abs(b)}", font_size=28, color=BLUE)
        eq_label.to_edge(DOWN)
        self.play(Write(eq_label))
        self.wait(2)
'''

slope_intercept_form = ManimTemplate(
    id="slope_intercept_form",
    name="Slope-Intercept Form",
    category=TemplateCategory.GRAPHING,
    description="Graph a linear equation in y = mx + b form showing slope and y-intercept",
    parameters=[
        ParamSpec(name="m", param_type=ParamType.FLOAT, description="Slope"),
        ParamSpec(name="b", param_type=ParamType.FLOAT, description="Y-intercept"),
        ParamSpec(name="x_min", param_type=ParamType.INT, required=False, default=-2, description="X axis minimum"),
        ParamSpec(name="x_max", param_type=ParamType.INT, required=False, default=6, description="X axis maximum"),
        ParamSpec(name="y_min", param_type=ParamType.INT, required=False, default=-2, description="Y axis minimum"),
        ParamSpec(name="y_max", param_type=ParamType.INT, required=False, default=8, description="Y axis maximum"),
    ],
    template_code=SLOPE_INTERCEPT_TEMPLATE,
    example_questions=[
        "Graph y = 2x + 3",
        "Plot y = -x + 5",
        "Show y = 3x - 2 on a graph",
        "Graph the line y = 0.5x + 1",
    ],
    tags=["slope", "intercept", "graph", "linear", "mx+b"],
    compute_derived=compute_slope_intercept_derived,
)


# =============================================================================
# System of Equations - Intersection
# =============================================================================
SYSTEM_INTERSECTION_TEMPLATE = '''from manim import *

class SystemIntersectionScene(Scene):
    """Solve the system y = {m1}x + {b1} and y = {m2}x + {b2} graphically."""

    def construct(self):
        # Parameters
        m1, b1 = {m1}, {b1}
        m2, b2 = {m2}, {b2}
        sol_x, sol_y = {sol_x}, {sol_y}

        # Title
        title = Text("Solving Systems of Equations", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP).scale(0.8))

        # Show the system
        if b1 >= 0:
            eq1_text = Text(f"y = {m1}x + {b1}", font_size=24, color=BLUE)
        else:
            eq1_text = Text(f"y = {m1}x - {abs(b1)}", font_size=24, color=BLUE)

        if b2 >= 0:
            eq2_text = Text(f"y = {m2}x + {b2}", font_size=24, color=RED)
        else:
            eq2_text = Text(f"y = {m2}x - {abs(b2)}", font_size=24, color=RED)

        system = VGroup(eq1_text, eq2_text).arrange(DOWN, buff=0.2)
        system.to_edge(RIGHT).shift(UP * 1.5)
        self.play(Write(system))
        self.wait(1)

        # Create axes
        axes = Axes(
            x_range=[{x_min}, {x_max}, 1],
            y_range=[{y_min}, {y_max}, 2],
            x_length=5.5,
            y_length=4.5,
            axis_config={{"include_numbers": False}},
        ).shift(DOWN * 0.5 + LEFT * 1)

        # Add labels
        x_nums = VGroup(*[
            Text(str(i), font_size=12).next_to(axes.c2p(i, 0), DOWN, buff=0.1)
            for i in range({x_min} + 1, {x_max}) if i != 0
        ])
        y_nums = VGroup(*[
            Text(str(i), font_size=12).next_to(axes.c2p(0, i), LEFT, buff=0.1)
            for i in range({y_min} + 1, {y_max}, 2) if i != 0
        ])

        self.play(Create(axes))
        self.play(Write(x_nums), Write(y_nums))
        self.wait(1)

        # Line 1
        line1 = axes.plot(lambda x: m1 * x + b1, x_range=[{x_min} + 0.3, {x_max} - 0.3], color=BLUE, stroke_width=3)
        self.play(Create(line1))
        self.wait(0.5)

        # Line 2
        line2 = axes.plot(lambda x: m2 * x + b2, x_range=[{x_min} + 0.3, {x_max} - 0.3], color=RED, stroke_width=3)
        self.play(Create(line2))
        self.wait(1)

        # Intersection point
        intersection = Dot(axes.c2p(sol_x, sol_y), color=YELLOW, radius=0.18)
        int_label = Text(f"({sol_x}, {sol_y})", font_size=22, color=YELLOW)
        int_label.next_to(intersection, UR, buff=0.15)

        self.play(Create(intersection))
        self.play(Flash(intersection, color=YELLOW, line_length=0.25))
        self.play(Write(int_label))
        self.wait(1)

        # Solution
        solution = Text(f"Solution: x = {sol_x}, y = {sol_y}", font_size=28, color=GREEN)
        solution.to_edge(DOWN)
        self.play(Write(solution))
        self.play(Indicate(solution, color=GREEN))
        self.wait(2)
'''

system_intersection = ManimTemplate(
    id="system_intersection",
    name="System of Equations - Graphical",
    category=TemplateCategory.SYSTEMS,
    description="Solve a system of two linear equations by graphing and finding intersection",
    parameters=[
        ParamSpec(name="m1", param_type=ParamType.FLOAT, description="Slope of first line"),
        ParamSpec(name="b1", param_type=ParamType.FLOAT, description="Y-intercept of first line"),
        ParamSpec(name="m2", param_type=ParamType.FLOAT, description="Slope of second line"),
        ParamSpec(name="b2", param_type=ParamType.FLOAT, description="Y-intercept of second line"),
        ParamSpec(name="sol_x", param_type=ParamType.FLOAT, description="X coordinate of solution", derived_from="(b2 - b1) / (m1 - m2)"),
        ParamSpec(name="sol_y", param_type=ParamType.FLOAT, description="Y coordinate of solution", derived_from="m1 * sol_x + b1"),
        ParamSpec(name="x_min", param_type=ParamType.INT, required=False, default=-1, description="X axis minimum"),
        ParamSpec(name="x_max", param_type=ParamType.INT, required=False, default=7, description="X axis maximum"),
        ParamSpec(name="y_min", param_type=ParamType.INT, required=False, default=-2, description="Y axis minimum"),
        ParamSpec(name="y_max", param_type=ParamType.INT, required=False, default=8, description="Y axis maximum"),
    ],
    template_code=SYSTEM_INTERSECTION_TEMPLATE,
    example_questions=[
        "Solve: y = 2x - 1 and y = -x + 5",
        "Find intersection of y = x + 1 and y = -2x + 7",
        "Graph and solve: y = 3x - 2, y = x + 2",
    ],
    tags=["system", "equations", "intersection", "graph", "solve"],
    compute_derived=compute_system_derived,
)


def get_templates() -> list[ManimTemplate]:
    """Return all graphing templates."""
    return [
        slope_visualization,
        slope_intercept_form,
        system_intersection,
    ]
