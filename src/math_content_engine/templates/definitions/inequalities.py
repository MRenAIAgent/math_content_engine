"""
Inequality templates.

Templates for visualizing:
- Number line inequalities
- Linear inequalities
- Compound inequalities
"""

from ..base import ManimTemplate, ParamSpec, ParamType, TemplateCategory


def compute_inequality_derived(params: dict) -> dict:
    """Compute derived parameters for inequalities."""
    boundary = params.get("boundary", 0)
    operator = params.get("operator", ">")

    # Determine if boundary is included (closed vs open circle)
    is_inclusive = operator in [">=", "<=", "≥", "≤"]

    # Determine direction
    direction = "right" if operator in [">", ">=", "≥"] else "left"

    # Axis range based on boundary
    num_min = min(-2, boundary - 5)
    num_max = max(10, boundary + 5)

    return {
        "is_inclusive": is_inclusive,
        "direction": direction,
        "num_min": int(num_min),
        "num_max": int(num_max),
    }


# =============================================================================
# Inequality on Number Line
# =============================================================================
INEQUALITY_NUMBERLINE_TEMPLATE = '''from manim import *

class InequalityNumberLineScene(Scene):
    """Graph x {operator} {boundary} on a number line."""

    def construct(self):
        # Parameters
        boundary = {boundary}
        operator = "{operator}"
        is_inclusive = {is_inclusive}
        direction = "{direction}"

        # Title
        title = Text(f"Graphing x {operator} {boundary}", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Create number line
        line = Line(LEFT * 5, RIGHT * 5, color=WHITE)
        self.play(Create(line))

        # Add tick marks and labels
        ticks = VGroup()
        labels = VGroup()
        for i in range({num_min}, {num_max} + 1):
            # Position tick at correct location
            pos = LEFT * 5 + RIGHT * (i - {num_min}) * (10 / ({num_max} - {num_min}))
            tick = Line(UP * 0.1, DOWN * 0.1, color=WHITE).move_to(pos)
            ticks.add(tick)
            label = Text(str(i), font_size=18).next_to(tick, DOWN, buff=0.15)
            labels.add(label)

        self.play(Create(ticks), Write(labels))
        self.wait(1)

        # Calculate boundary position
        boundary_pos = LEFT * 5 + RIGHT * (boundary - {num_min}) * (10 / ({num_max} - {num_min}))

        # Show boundary point
        if is_inclusive:
            # Filled circle for ≤ or ≥
            boundary_dot = Dot(boundary_pos, color=RED, radius=0.15)
            boundary_label = Text(f"x = {boundary} (included)", font_size=18, color=RED)
        else:
            # Open circle for < or >
            boundary_dot = Circle(radius=0.15, color=RED, stroke_width=3)
            boundary_dot.move_to(boundary_pos)
            boundary_label = Text(f"x = {boundary} (not included)", font_size=18, color=RED)

        boundary_label.next_to(boundary_dot, UP, buff=0.4)
        self.play(Create(boundary_dot), Write(boundary_label))
        self.wait(1)

        # Shade the solution region
        if direction == "right":
            # x > boundary or x >= boundary
            shade_width = 4.8 - (boundary - {num_min}) * (10 / ({num_max} - {num_min})) + 5
            shade = Rectangle(
                width=shade_width, height=0.3,
                color=GREEN, fill_opacity=0.5,
                stroke_width=0
            )
            shade.move_to(boundary_pos + RIGHT * shade_width / 2)
            arrow = Arrow(
                boundary_pos + RIGHT * 0.2,
                boundary_pos + RIGHT * shade_width,
                color=GREEN, buff=0
            )
        else:
            # x < boundary or x <= boundary
            shade_width = (boundary - {num_min}) * (10 / ({num_max} - {num_min}))
            shade = Rectangle(
                width=shade_width, height=0.3,
                color=GREEN, fill_opacity=0.5,
                stroke_width=0
            )
            shade.move_to(boundary_pos + LEFT * shade_width / 2)
            arrow = Arrow(
                boundary_pos + LEFT * 0.2,
                boundary_pos + LEFT * shade_width,
                color=GREEN, buff=0
            )

        self.play(FadeIn(shade), Create(arrow))
        self.wait(1)

        # Show solution notation
        if direction == "right":
            if is_inclusive:
                notation = f"Solution: x ≥ {boundary} or [{boundary}, ∞)"
            else:
                notation = f"Solution: x > {boundary} or ({boundary}, ∞)"
        else:
            if is_inclusive:
                notation = f"Solution: x ≤ {boundary} or (-∞, {boundary}]"
            else:
                notation = f"Solution: x < {boundary} or (-∞, {boundary})"

        solution = Text(notation, font_size=26, color=GREEN)
        solution.to_edge(DOWN, buff=1)
        self.play(Write(solution))
        self.wait(1)

        # Show test points
        if direction == "right":
            good_x = boundary + 2
            bad_x = boundary - 2
        else:
            good_x = boundary - 2
            bad_x = boundary + 2

        # Calculate positions for test points
        good_pos = LEFT * 5 + RIGHT * (good_x - {num_min}) * (10 / ({num_max} - {num_min}))
        bad_pos = LEFT * 5 + RIGHT * (bad_x - {num_min}) * (10 / ({num_max} - {num_min}))

        test_good = Dot(good_pos, color=YELLOW, radius=0.1)
        test_good_label = Text(f"x={good_x} ✓", font_size=14, color=YELLOW)
        test_good_label.next_to(test_good, DOWN, buff=0.3)

        test_bad = Dot(bad_pos, color=GRAY, radius=0.1)
        test_bad_label = Text(f"x={bad_x} ✗", font_size=14, color=GRAY)
        test_bad_label.next_to(test_bad, DOWN, buff=0.3)

        self.play(Create(test_good), Write(test_good_label))
        self.play(Create(test_bad), Write(test_bad_label))
        self.wait(2)
'''

inequality_numberline = ManimTemplate(
    id="inequality_numberline",
    name="Inequality on Number Line",
    category=TemplateCategory.INEQUALITIES,
    description="Graph a simple inequality on a number line with open/closed circles and shading",
    parameters=[
        ParamSpec(name="boundary", param_type=ParamType.FLOAT, description="Boundary value"),
        ParamSpec(
            name="operator",
            param_type=ParamType.CHOICE,
            description="Inequality operator",
            constraints={"choices": [">", "<", ">=", "<=", "≥", "≤"]}
        ),
        ParamSpec(name="is_inclusive", param_type=ParamType.BOOL, description="Whether boundary is included", derived_from="operator"),
        ParamSpec(name="direction", param_type=ParamType.STRING, description="Direction of shading", derived_from="operator"),
        ParamSpec(name="num_min", param_type=ParamType.INT, required=False, default=-2, description="Number line minimum"),
        ParamSpec(name="num_max", param_type=ParamType.INT, required=False, default=10, description="Number line maximum"),
    ],
    template_code=INEQUALITY_NUMBERLINE_TEMPLATE,
    example_questions=[
        "Graph x > 3",
        "Show x ≤ 5 on a number line",
        "Graph x < -2",
        "Represent x ≥ 0 on number line",
    ],
    tags=["inequality", "number line", "graph", "greater", "less"],
    compute_derived=compute_inequality_derived,
)


# =============================================================================
# Compound Inequality
# =============================================================================
COMPOUND_INEQUALITY_TEMPLATE = '''from manim import *

class CompoundInequalityScene(Scene):
    """Graph {lower} {op1} x {op2} {upper} on a number line."""

    def construct(self):
        # Parameters
        lower, upper = {lower}, {upper}
        op1, op2 = "{op1}", "{op2}"
        lower_inclusive = {lower_inclusive}
        upper_inclusive = {upper_inclusive}

        # Title
        title = Text(f"Graphing {lower} {op1} x {op2} {upper}", font_size=32)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Create number line
        line = Line(LEFT * 5.5, RIGHT * 5.5, color=WHITE)
        self.play(Create(line))

        # Add tick marks and labels
        ticks = VGroup()
        labels = VGroup()
        for i in range({num_min}, {num_max} + 1):
            pos = LEFT * 5.5 + RIGHT * (i - {num_min}) * (11 / ({num_max} - {num_min}))
            tick = Line(UP * 0.1, DOWN * 0.1, color=WHITE).move_to(pos)
            ticks.add(tick)
            label = Text(str(i), font_size=16).next_to(tick, DOWN, buff=0.12)
            labels.add(label)

        self.play(Create(ticks), Write(labels))
        self.wait(1)

        # Calculate positions
        lower_pos = LEFT * 5.5 + RIGHT * (lower - {num_min}) * (11 / ({num_max} - {num_min}))
        upper_pos = LEFT * 5.5 + RIGHT * (upper - {num_min}) * (11 / ({num_max} - {num_min}))

        # Show boundary points
        if lower_inclusive:
            lower_dot = Dot(lower_pos, color=RED, radius=0.12)
        else:
            lower_dot = Circle(radius=0.12, color=RED, stroke_width=3).move_to(lower_pos)

        if upper_inclusive:
            upper_dot = Dot(upper_pos, color=RED, radius=0.12)
        else:
            upper_dot = Circle(radius=0.12, color=RED, stroke_width=3).move_to(upper_pos)

        self.play(Create(lower_dot), Create(upper_dot))
        self.wait(1)

        # Shade between
        shade_width = (upper - lower) * (11 / ({num_max} - {num_min}))
        shade = Rectangle(
            width=shade_width, height=0.25,
            color=GREEN, fill_opacity=0.5,
            stroke_width=0
        )
        shade.move_to((lower_pos + upper_pos) / 2)
        self.play(FadeIn(shade))
        self.wait(1)

        # Solution notation
        left_bracket = "[" if lower_inclusive else "("
        right_bracket = "]" if upper_inclusive else ")"
        notation = f"Solution: {left_bracket}{lower}, {upper}{right_bracket}"
        solution = Text(notation, font_size=28, color=GREEN)
        solution.to_edge(DOWN, buff=1)
        self.play(Write(solution))

        # Explanation
        explanation = Text(f"All values between {lower} and {upper}", font_size=22)
        explanation.next_to(solution, UP, buff=0.3)
        self.play(Write(explanation))
        self.wait(2)
'''

def compute_compound_derived(params: dict) -> dict:
    """Compute derived parameters for compound inequalities."""
    lower = params.get("lower", 0)
    upper = params.get("upper", 5)
    op1 = params.get("op1", "<")
    op2 = params.get("op2", "<")

    lower_inclusive = op1 in ["<=", "≤"]
    upper_inclusive = op2 in ["<=", "≤"]

    num_min = int(min(-2, lower - 3))
    num_max = int(max(10, upper + 3))

    return {
        "lower_inclusive": lower_inclusive,
        "upper_inclusive": upper_inclusive,
        "num_min": num_min,
        "num_max": num_max,
    }


compound_inequality = ManimTemplate(
    id="compound_inequality",
    name="Compound Inequality",
    category=TemplateCategory.INEQUALITIES,
    description="Graph a compound inequality (a < x < b) on a number line",
    parameters=[
        ParamSpec(name="lower", param_type=ParamType.FLOAT, description="Lower bound"),
        ParamSpec(name="upper", param_type=ParamType.FLOAT, description="Upper bound"),
        ParamSpec(
            name="op1",
            param_type=ParamType.CHOICE,
            description="Left inequality operator",
            constraints={"choices": ["<", "<=", "≤"]}
        ),
        ParamSpec(
            name="op2",
            param_type=ParamType.CHOICE,
            description="Right inequality operator",
            constraints={"choices": ["<", "<=", "≤"]}
        ),
        ParamSpec(name="lower_inclusive", param_type=ParamType.BOOL, description="Is lower bound inclusive", derived_from="op1"),
        ParamSpec(name="upper_inclusive", param_type=ParamType.BOOL, description="Is upper bound inclusive", derived_from="op2"),
        ParamSpec(name="num_min", param_type=ParamType.INT, required=False, default=-2, description="Number line minimum"),
        ParamSpec(name="num_max", param_type=ParamType.INT, required=False, default=10, description="Number line maximum"),
    ],
    template_code=COMPOUND_INEQUALITY_TEMPLATE,
    example_questions=[
        "Graph 2 < x < 7",
        "Show -1 ≤ x ≤ 4 on a number line",
        "Graph 0 < x ≤ 5",
    ],
    tags=["compound", "inequality", "number line", "between", "interval"],
    compute_derived=compute_compound_derived,
)


def get_templates() -> list[ManimTemplate]:
    """Return all inequality templates."""
    return [
        inequality_numberline,
        compound_inequality,
    ]
