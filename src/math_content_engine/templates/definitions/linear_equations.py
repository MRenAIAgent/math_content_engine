"""
Linear equation templates.

Templates for visualizing linear equation solving:
- Graphical method (line intersection)
- Balance scale method
- Step-by-step algebraic
"""

from ..base import ManimTemplate, ParamSpec, ParamType, TemplateCategory


def compute_linear_derived(params: dict) -> dict:
    """Compute derived parameters for linear equations."""
    a = params.get("a", 1)
    b = params.get("b", 0)
    c = params.get("c", 0)

    # Compute solution: ax + b = c => x = (c - b) / a
    if a != 0:
        solution = (c - b) / a
        # Use integer if it's a whole number
        if solution == int(solution):
            solution = int(solution)
    else:
        solution = None

    # Compute axis ranges based on values
    x_min = min(-2, int(solution) - 2 if solution else -2)
    x_max = max(6, int(solution) + 4 if solution else 6)
    y_min = min(-2, b - 2, c - 2)
    y_max = max(c + 4, abs(a) * x_max + b + 2)

    return {
        "solution": solution,
        "x_min": x_min,
        "x_max": x_max,
        "y_min": int(y_min),
        "y_max": int(y_max),
    }


# =============================================================================
# Linear Equation - Graphical Method
# =============================================================================
LINEAR_EQUATION_GRAPH_TEMPLATE = '''from manim import *

class LinearEquationGraphScene(Scene):
    """Solve {a}x + {b} = {c} by showing where y = {a}x + {b} intersects y = {c}."""

    def construct(self):
        # Parameters
        a, b, c = {a}, {b}, {c}
        solution = {solution}

        # Title
        if b >= 0:
            title = Text(f"Solving {a}x + {b} = {c} Graphically", font_size=36)
        else:
            title = Text(f"Solving {a}x - {abs(b)} = {c} Graphically", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP).scale(0.8))

        # Create coordinate axes
        axes = Axes(
            x_range=[{x_min}, {x_max}, 1],
            y_range=[{y_min}, {y_max}, 2],
            x_length=6,
            y_length=5,
            axis_config={{"include_numbers": False}},
        ).shift(DOWN * 0.5)

        # Add number labels manually
        x_nums = VGroup(*[
            Text(str(i), font_size=16).next_to(axes.c2p(i, 0), DOWN, buff=0.1)
            for i in range({x_min} + 1, {x_max})
        ])
        y_nums = VGroup(*[
            Text(str(i), font_size=16).next_to(axes.c2p(0, i), LEFT, buff=0.1)
            for i in range({y_min} + 1, {y_max}, 2) if i != 0
        ])

        x_label = Text("x", font_size=24).next_to(axes.x_axis, RIGHT)
        y_label = Text("y", font_size=24).next_to(axes.y_axis, UP)

        self.play(Create(axes), Write(x_label), Write(y_label))
        self.play(Write(x_nums), Write(y_nums))
        self.wait(1)

        # Plot y = ax + b (the line)
        line_func = axes.plot(lambda x: a*x + b, x_range=[{x_min} + 0.5, {x_max} - 0.5], color=BLUE)
        if b >= 0:
            line_label = Text(f"y = {a}x + {b}", font_size=24, color=BLUE)
        else:
            line_label = Text(f"y = {a}x - {abs(b)}", font_size=24, color=BLUE)
        line_label.next_to(line_func, RIGHT, buff=0.3)

        self.play(Create(line_func), Write(line_label))
        self.wait(1)

        # Plot y = c (horizontal line)
        horizontal_line = axes.plot(lambda x: c, x_range=[{x_min} + 0.5, {x_max} - 0.5], color=RED)
        horiz_label = Text(f"y = {c}", font_size=24, color=RED)
        horiz_label.next_to(horizontal_line, LEFT, buff=0.3)

        self.play(Create(horizontal_line), Write(horiz_label))
        self.wait(1)

        # Find and highlight intersection point
        intersection_point = Dot(axes.c2p(solution, c), color=YELLOW, radius=0.15)
        intersection_label = Text(f"({solution}, {c})", font_size=24, color=YELLOW)
        intersection_label.next_to(intersection_point, UR, buff=0.2)

        self.play(Create(intersection_point), Write(intersection_label))
        self.play(Flash(intersection_point, color=YELLOW))
        self.wait(1)

        # Draw dashed line down to x-axis
        dashed_line = DashedLine(
            axes.c2p(solution, c), axes.c2p(solution, 0), color=GREEN
        )
        solution_dot = Dot(axes.c2p(solution, 0), color=GREEN, radius=0.12)

        self.play(Create(dashed_line), Create(solution_dot))
        self.wait(0.5)

        # Show the solution
        solution_text = Text(f"Solution: x = {solution}", font_size=32, color=GREEN)
        solution_text.to_edge(DOWN)
        self.play(Write(solution_text))
        self.play(Indicate(solution_text, color=GREEN))
        self.wait(2)
'''

linear_equation_graph = ManimTemplate(
    id="linear_equation_graph",
    name="Linear Equation - Graphical Method",
    category=TemplateCategory.LINEAR_EQUATIONS,
    description="Solve linear equations ax + b = c by finding where y = ax + b intersects y = c",
    parameters=[
        ParamSpec(
            name="a",
            param_type=ParamType.FLOAT,
            description="Coefficient of x",
            constraints={"min": -20, "max": 20},
        ),
        ParamSpec(
            name="b",
            param_type=ParamType.FLOAT,
            description="Constant term on left side",
            constraints={"min": -50, "max": 50},
        ),
        ParamSpec(
            name="c",
            param_type=ParamType.FLOAT,
            description="Right side of equation",
            constraints={"min": -50, "max": 50},
        ),
        ParamSpec(
            name="solution",
            param_type=ParamType.FLOAT,
            description="Solution value x",
            derived_from="(c - b) / a",
        ),
        ParamSpec(
            name="x_min",
            param_type=ParamType.INT,
            description="Minimum x-axis value",
            required=False,
            default=-2,
        ),
        ParamSpec(
            name="x_max",
            param_type=ParamType.INT,
            description="Maximum x-axis value",
            required=False,
            default=6,
        ),
        ParamSpec(
            name="y_min",
            param_type=ParamType.INT,
            description="Minimum y-axis value",
            required=False,
            default=-2,
        ),
        ParamSpec(
            name="y_max",
            param_type=ParamType.INT,
            description="Maximum y-axis value",
            required=False,
            default=12,
        ),
    ],
    template_code=LINEAR_EQUATION_GRAPH_TEMPLATE,
    example_questions=[
        "Solve 2x + 3 = 7",
        "Find x: 3x - 5 = 10",
        "Solve 4x + 2 = 18 graphically",
        "Graph to solve 5x - 3 = 12",
    ],
    tags=["linear", "equation", "graph", "intersection", "solve"],
    compute_derived=compute_linear_derived,
)


# =============================================================================
# Linear Equation - Balance Scale Method
# =============================================================================
LINEAR_EQUATION_BALANCE_TEMPLATE = '''from manim import *

class LinearEquationBalanceScene(Scene):
    """Solve {a}x + {b} = {c} using a balance scale visualization."""

    def construct(self):
        # Parameters
        a, b, c = {a}, {b}, {c}
        solution = {solution}

        # Title
        if b >= 0:
            title = Text(f"Solving {a}x + {b} = {c} with Balance Scale", font_size=32)
        else:
            title = Text(f"Solving {a}x - {abs(b)} = {c} with Balance Scale", font_size=32)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP).scale(0.8))

        # Create balance scale
        base = Rectangle(width=3, height=0.25, color=GRAY, fill_opacity=1)
        base.shift(DOWN * 2.5)

        fulcrum = Triangle(color=GRAY, fill_opacity=1).scale(0.35)
        fulcrum.move_to(base.get_top())

        beam = Rectangle(width=5.5, height=0.12, color=GOLD, fill_opacity=1)
        beam.move_to(fulcrum.get_top() + UP * 0.08)

        left_pan = Rectangle(width=1.8, height=0.08, color=WHITE, fill_opacity=0.8)
        left_pan.move_to(beam.get_left() + DOWN * 0.45)
        left_string = Line(beam.get_left(), left_pan.get_top(), color=WHITE)

        right_pan = Rectangle(width=1.8, height=0.08, color=WHITE, fill_opacity=0.8)
        right_pan.move_to(beam.get_right() + DOWN * 0.45)
        right_string = Line(beam.get_right(), right_pan.get_top(), color=WHITE)

        scale = VGroup(base, fulcrum, beam, left_pan, left_string, right_pan, right_string)
        self.play(Create(scale))
        self.wait(1)

        # Show equation
        if b >= 0:
            equation = Text(f"{a}x + {b} = {c}", font_size=28)
        else:
            equation = Text(f"{a}x - {abs(b)} = {c}", font_size=28)
        equation.move_to(UP * 1.8)
        self.play(Write(equation))
        self.wait(1)

        # Left side: a x-boxes + b unit squares
        x_boxes = VGroup()
        for i in range(a):
            box = Square(side_length=0.35, color=BLUE, fill_opacity=0.7)
            label = Text("x", font_size=14, color=WHITE).move_to(box)
            x_boxes.add(VGroup(box, label))

        units_left = VGroup()
        for i in range(abs(b)):
            unit = Square(side_length=0.25, color=GREEN if b > 0 else RED, fill_opacity=0.7)
            units_left.add(unit)

        left_items = VGroup(*x_boxes, *units_left).arrange(RIGHT, buff=0.08)
        left_items.move_to(left_pan.get_top() + UP * 0.35)

        # Right side: c unit squares
        units_right = VGroup()
        for i in range(c):
            unit = Square(side_length=0.25, color=YELLOW, fill_opacity=0.7)
            units_right.add(unit)
        units_right.arrange_in_grid(rows=2, buff=0.08)
        units_right.move_to(right_pan.get_top() + UP * 0.4)

        self.play(Create(left_items))
        self.play(Create(units_right))
        self.wait(1)

        # Step 1: Remove b from both sides
        if b != 0:
            step1 = Text(f"Step 1: Remove {abs(b)} from both sides", font_size=22, color=ORANGE)
            step1.move_to(UP * 1.2)
            self.play(Write(step1))
            self.wait(1)

            # Fade out b units from left and right
            left_units_to_remove = list(units_left)
            right_units_to_remove = list(units_right)[-abs(b):]

            self.play(
                *[FadeOut(u) for u in left_units_to_remove],
                *[FadeOut(u) for u in right_units_to_remove]
            )

            # Update remaining items
            remaining_right = VGroup(*list(units_right)[:-abs(b)])
            remaining_right.arrange(RIGHT, buff=0.08)
            remaining_right.move_to(right_pan.get_top() + UP * 0.35)

            x_boxes.arrange(RIGHT, buff=0.1)
            x_boxes.move_to(left_pan.get_top() + UP * 0.35)

            self.play(
                x_boxes.animate.move_to(left_pan.get_top() + UP * 0.35),
            )
            self.wait(1)

            # Update equation
            equation2 = Text(f"{a}x = {c - b}", font_size=28)
            equation2.move_to(equation.get_center())
            self.play(ReplacementTransform(equation, equation2), FadeOut(step1))
            equation = equation2
            self.wait(1)

        # Step 2: Divide both sides by a
        step2 = Text(f"Step 2: Divide both sides by {a}", font_size=22, color=ORANGE)
        step2.move_to(UP * 1.2)
        self.play(Write(step2))
        self.wait(1)

        # Show division with grouping
        if a > 1:
            left_group = SurroundingRectangle(x_boxes[0], color=RED, buff=0.08)
            self.play(Create(left_group))
            self.wait(1)
            self.play(FadeOut(left_group))

        # Final result
        equation3 = Text(f"x = {solution}", font_size=32, color=GREEN)
        equation3.move_to(equation.get_center())
        self.play(
            ReplacementTransform(equation, equation3),
            FadeOut(step2)
        )
        self.play(Indicate(equation3, scale_factor=1.2, color=GREEN))
        self.wait(2)
'''

linear_equation_balance = ManimTemplate(
    id="linear_equation_balance",
    name="Linear Equation - Balance Scale",
    category=TemplateCategory.LINEAR_EQUATIONS,
    description="Solve linear equations using a visual balance scale analogy",
    parameters=[
        ParamSpec(
            name="a",
            param_type=ParamType.INT,
            description="Coefficient of x (positive integer for visual clarity)",
            constraints={"min": 1, "max": 5},
        ),
        ParamSpec(
            name="b",
            param_type=ParamType.INT,
            description="Constant term on left side",
            constraints={"min": -10, "max": 10},
        ),
        ParamSpec(
            name="c",
            param_type=ParamType.INT,
            description="Right side of equation",
            constraints={"min": 1, "max": 20},
        ),
        ParamSpec(
            name="solution",
            param_type=ParamType.INT,
            description="Solution value x",
            derived_from="(c - b) / a",
        ),
    ],
    template_code=LINEAR_EQUATION_BALANCE_TEMPLATE,
    example_questions=[
        "Solve 2x + 3 = 7 using balance",
        "Use balance scale to solve 3x + 2 = 11",
        "Show 4x - 2 = 10 on a balance",
    ],
    tags=["linear", "equation", "balance", "visual", "solve", "algebra"],
    compute_derived=compute_linear_derived,
)


# =============================================================================
# Two-Step Equation - Step by Step
# =============================================================================
TWO_STEP_EQUATION_TEMPLATE = '''from manim import *

class TwoStepEquationScene(Scene):
    """Solve {a}x + {b} = {c} step by step with algebraic notation."""

    def construct(self):
        # Parameters
        a, b, c = {a}, {b}, {c}
        solution = {solution}

        # Title
        title = Text("Solving Two-Step Equations", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP).scale(0.8))
        self.wait(1)

        # Original equation
        if b >= 0:
            eq1 = Text(f"{a}x + {b} = {c}", font_size=40)
        else:
            eq1 = Text(f"{a}x - {abs(b)} = {c}", font_size=40)
        eq1.move_to(UP * 0.5)
        self.play(Write(eq1))
        self.wait(1)

        # Step 1: Subtract b from both sides
        step1_label = Text(f"Step 1: Subtract {b} from both sides", font_size=24, color=BLUE)
        step1_label.next_to(eq1, DOWN, buff=0.5)
        self.play(Write(step1_label))
        self.wait(1)

        # Show the operation
        if b >= 0:
            op1 = Text(f"- {b}        - {b}", font_size=28, color=BLUE)
        else:
            op1 = Text(f"+ {abs(b)}        + {abs(b)}", font_size=28, color=BLUE)
        op1.next_to(step1_label, DOWN, buff=0.3)
        self.play(Write(op1))
        self.wait(1)

        # Result after step 1
        eq2 = Text(f"{a}x = {c - b}", font_size=40)
        eq2.next_to(op1, DOWN, buff=0.5)
        self.play(Write(eq2))
        self.wait(1)

        # Clear for step 2
        self.play(
            FadeOut(eq1), FadeOut(step1_label), FadeOut(op1),
            eq2.animate.move_to(UP * 0.5)
        )
        self.wait(0.5)

        # Step 2: Divide both sides by a
        step2_label = Text(f"Step 2: Divide both sides by {a}", font_size=24, color=GREEN)
        step2_label.next_to(eq2, DOWN, buff=0.5)
        self.play(Write(step2_label))
        self.wait(1)

        # Show the operation
        op2 = Text(f"÷ {a}      ÷ {a}", font_size=28, color=GREEN)
        op2.next_to(step2_label, DOWN, buff=0.3)
        self.play(Write(op2))
        self.wait(1)

        # Final result
        eq3 = Text(f"x = {solution}", font_size=44, color=YELLOW)
        eq3.next_to(op2, DOWN, buff=0.5)
        self.play(Write(eq3))
        self.play(Indicate(eq3, scale_factor=1.2, color=YELLOW))
        self.wait(1)

        # Verification
        verify_title = Text("Check:", font_size=28, color=ORANGE)
        verify_title.to_edge(DOWN, buff=1.5)
        self.play(Write(verify_title))

        if b >= 0:
            verify = Text(f"{a}({solution}) + {b} = {a * solution + b} ✓", font_size=24)
        else:
            verify = Text(f"{a}({solution}) - {abs(b)} = {a * solution + b} ✓", font_size=24)
        verify.next_to(verify_title, DOWN, buff=0.2)
        self.play(Write(verify))
        self.wait(2)
'''

two_step_equation = ManimTemplate(
    id="two_step_equation",
    name="Two-Step Equation - Algebraic",
    category=TemplateCategory.LINEAR_EQUATIONS,
    description="Solve two-step equations with step-by-step algebraic notation",
    parameters=[
        ParamSpec(
            name="a",
            param_type=ParamType.INT,
            description="Coefficient of x",
            constraints={"min": 1, "max": 10},
        ),
        ParamSpec(
            name="b",
            param_type=ParamType.INT,
            description="Constant term",
            constraints={"min": -20, "max": 20},
        ),
        ParamSpec(
            name="c",
            param_type=ParamType.INT,
            description="Right side value",
            constraints={"min": -30, "max": 30},
        ),
        ParamSpec(
            name="solution",
            param_type=ParamType.INT,
            description="Solution value x",
            derived_from="(c - b) / a",
        ),
    ],
    template_code=TWO_STEP_EQUATION_TEMPLATE,
    example_questions=[
        "Solve 2x + 3 = 7",
        "Find x in 5x - 10 = 15",
        "What is x if 3x + 6 = 21?",
    ],
    tags=["linear", "equation", "two-step", "algebraic", "solve"],
    compute_derived=compute_linear_derived,
)


def get_templates() -> list[ManimTemplate]:
    """Return all linear equation templates."""
    return [
        linear_equation_graph,
        linear_equation_balance,
        two_step_equation,
    ]
