"""
Quadratic equation templates.

Templates for visualizing:
- Quadratic graphs (parabolas)
- Quadratic formula
- Factoring
- Completing the square
"""

import math
from ..base import ManimTemplate, ParamSpec, ParamType, TemplateCategory


def compute_quadratic_derived(params: dict) -> dict:
    """Compute derived parameters for quadratic equations."""
    a = params.get("a", 1)
    b = params.get("b", 0)
    c = params.get("c", 0)

    # Discriminant
    discriminant = b * b - 4 * a * c

    # Roots
    if discriminant > 0:
        root1 = (-b + math.sqrt(discriminant)) / (2 * a)
        root2 = (-b - math.sqrt(discriminant)) / (2 * a)
        if root1 == int(root1):
            root1 = int(root1)
        if root2 == int(root2):
            root2 = int(root2)
        num_roots = 2
    elif discriminant == 0:
        root1 = -b / (2 * a)
        root2 = root1
        if root1 == int(root1):
            root1 = int(root1)
            root2 = root1
        num_roots = 1
    else:
        root1, root2 = None, None
        num_roots = 0

    # Vertex
    vertex_x = -b / (2 * a)
    vertex_y = a * vertex_x * vertex_x + b * vertex_x + c
    if vertex_x == int(vertex_x):
        vertex_x = int(vertex_x)
    if vertex_y == int(vertex_y):
        vertex_y = int(vertex_y)

    # Axis ranges
    x_min = int(min(-3, vertex_x - 4, (root1 - 2) if root1 else -3, (root2 - 2) if root2 else -3))
    x_max = int(max(5, vertex_x + 4, (root1 + 2) if root1 else 5, (root2 + 2) if root2 else 5))
    y_min = int(min(-3, vertex_y - 2))
    y_max = int(max(8, vertex_y + 4, c + 2))

    return {
        "discriminant": discriminant,
        "root1": root1,
        "root2": root2,
        "num_roots": num_roots,
        "vertex_x": vertex_x,
        "vertex_y": vertex_y,
        "x_min": x_min,
        "x_max": x_max,
        "y_min": y_min,
        "y_max": y_max,
    }


# =============================================================================
# Quadratic Graph - Parabola with roots
# =============================================================================
QUADRATIC_GRAPH_TEMPLATE = '''from manim import *

class QuadraticGraphScene(Scene):
    """Graph y = {a}x² + {b}x + {c} showing vertex and roots."""

    def construct(self):
        # Parameters
        a, b, c = {a}, {b}, {c}
        vertex_x, vertex_y = {vertex_x}, {vertex_y}
        root1, root2 = {root1}, {root2}
        num_roots = {num_roots}

        # Title - build equation string
        if b >= 0 and c >= 0:
            eq_str = f"y = {a}x² + {b}x + {c}"
        elif b >= 0 and c < 0:
            eq_str = f"y = {a}x² + {b}x - {abs(c)}"
        elif b < 0 and c >= 0:
            eq_str = f"y = {a}x² - {abs(b)}x + {c}"
        else:
            eq_str = f"y = {a}x² - {abs(b)}x - {abs(c)}"

        title = Text(f"Graphing {eq_str}", font_size=32)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP).scale(0.8))

        # Create axes
        axes = Axes(
            x_range=[{x_min}, {x_max}, 1],
            y_range=[{y_min}, {y_max}, 2],
            x_length=6,
            y_length=5,
            axis_config={{"include_numbers": False}},
        ).shift(DOWN * 0.3)

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

        # Plot the parabola
        parabola = axes.plot(
            lambda x: a * x * x + b * x + c,
            x_range=[{x_min} + 0.5, {x_max} - 0.5],
            color=BLUE,
            stroke_width=3
        )
        self.play(Create(parabola), run_time=2)
        self.wait(1)

        # Show vertex
        vertex = Dot(axes.c2p(vertex_x, vertex_y), color=GREEN, radius=0.12)
        vertex_label = Text(f"Vertex: ({vertex_x}, {vertex_y})", font_size=18, color=GREEN)
        vertex_label.next_to(vertex, UP if a > 0 else DOWN, buff=0.2)

        self.play(Create(vertex), Write(vertex_label))
        self.play(Flash(vertex, color=GREEN))
        self.wait(1)

        # Show roots (x-intercepts)
        if num_roots > 0:
            root_label = Text("Roots (x-intercepts):", font_size=20, color=YELLOW)
            root_label.to_edge(RIGHT).shift(UP * 1)
            self.play(Write(root_label))

            if root1 is not None:
                r1_dot = Dot(axes.c2p(root1, 0), color=YELLOW, radius=0.12)
                r1_text = Text(f"x = {root1}", font_size=16, color=YELLOW)
                r1_text.next_to(r1_dot, DOWN, buff=0.2)
                self.play(Create(r1_dot), Write(r1_text))
                self.play(Flash(r1_dot, color=YELLOW))

            if num_roots == 2 and root2 is not None and root1 != root2:
                r2_dot = Dot(axes.c2p(root2, 0), color=YELLOW, radius=0.12)
                r2_text = Text(f"x = {root2}", font_size=16, color=YELLOW)
                r2_text.next_to(r2_dot, DOWN, buff=0.2)
                self.play(Create(r2_dot), Write(r2_text))
                self.play(Flash(r2_dot, color=YELLOW))

        else:
            no_roots = Text("No real roots", font_size=20, color=ORANGE)
            no_roots.to_edge(RIGHT).shift(UP * 1)
            self.play(Write(no_roots))

        self.wait(2)
'''

quadratic_graph = ManimTemplate(
    id="quadratic_graph",
    name="Quadratic Graph - Parabola",
    category=TemplateCategory.QUADRATICS,
    description="Graph a quadratic equation showing parabola, vertex, and roots",
    parameters=[
        ParamSpec(name="a", param_type=ParamType.FLOAT, description="Coefficient of x²", constraints={"min": -10, "max": 10}),
        ParamSpec(name="b", param_type=ParamType.FLOAT, description="Coefficient of x", constraints={"min": -20, "max": 20}),
        ParamSpec(name="c", param_type=ParamType.FLOAT, description="Constant term", constraints={"min": -20, "max": 20}),
        ParamSpec(name="vertex_x", param_type=ParamType.FLOAT, description="X coordinate of vertex", derived_from="-b/(2a)"),
        ParamSpec(name="vertex_y", param_type=ParamType.FLOAT, description="Y coordinate of vertex", derived_from="a*vertex_x²+b*vertex_x+c"),
        ParamSpec(name="root1", param_type=ParamType.FLOAT, description="First root", required=False, derived_from="quadratic formula"),
        ParamSpec(name="root2", param_type=ParamType.FLOAT, description="Second root", required=False, derived_from="quadratic formula"),
        ParamSpec(name="num_roots", param_type=ParamType.INT, description="Number of real roots", derived_from="discriminant"),
        ParamSpec(name="x_min", param_type=ParamType.INT, required=False, default=-4, description="X axis minimum"),
        ParamSpec(name="x_max", param_type=ParamType.INT, required=False, default=6, description="X axis maximum"),
        ParamSpec(name="y_min", param_type=ParamType.INT, required=False, default=-5, description="Y axis minimum"),
        ParamSpec(name="y_max", param_type=ParamType.INT, required=False, default=10, description="Y axis maximum"),
    ],
    template_code=QUADRATIC_GRAPH_TEMPLATE,
    example_questions=[
        "Graph y = x² - 4",
        "Plot y = x² - 5x + 6",
        "Graph the parabola y = 2x² - 4x - 6",
        "Show y = -x² + 4x - 3",
    ],
    tags=["quadratic", "parabola", "graph", "vertex", "roots"],
    compute_derived=compute_quadratic_derived,
)


# =============================================================================
# Quadratic Formula Visualization
# =============================================================================
QUADRATIC_FORMULA_TEMPLATE = '''from manim import *

class QuadraticFormulaScene(Scene):
    """Solve {a}x² + {b}x + {c} = 0 using the quadratic formula."""

    def construct(self):
        # Parameters
        a, b, c = {a}, {b}, {c}
        discriminant = {discriminant}
        root1, root2 = {root1}, {root2}

        # Title
        title = Text("The Quadratic Formula", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Show the formula
        formula = Text("x = (-b ± √(b² - 4ac)) / 2a", font_size=32, color=BLUE)
        formula.move_to(UP * 1.5)
        self.play(Write(formula))
        self.wait(1)

        # Show the equation to solve
        if b >= 0 and c >= 0:
            eq_str = f"{a}x² + {b}x + {c} = 0"
        elif b >= 0:
            eq_str = f"{a}x² + {b}x - {abs(c)} = 0"
        elif c >= 0:
            eq_str = f"{a}x² - {abs(b)}x + {c} = 0"
        else:
            eq_str = f"{a}x² - {abs(b)}x - {abs(c)} = 0"

        equation = Text(f"Solve: {eq_str}", font_size=28)
        equation.move_to(UP * 0.5)
        self.play(Write(equation))
        self.wait(1)

        # Identify a, b, c
        values = Text(f"a = {a}, b = {b}, c = {c}", font_size=24, color=GREEN)
        values.move_to(ORIGIN)
        self.play(Write(values))
        self.wait(1)

        # Calculate discriminant
        disc_text = Text(f"b² - 4ac = {b}² - 4({a})({c}) = {b*b} - {4*a*c} = {discriminant}", font_size=22, color=ORANGE)
        disc_text.move_to(DOWN * 0.7)
        self.play(Write(disc_text))
        self.wait(1)

        # Show solutions based on discriminant
        if discriminant > 0:
            import math
            sqrt_disc = math.sqrt(discriminant)
            sol_text = Text(f"x = ({-b} ± {sqrt_disc:.2f}) / {2*a}", font_size=24)
            sol_text.move_to(DOWN * 1.5)
            self.play(Write(sol_text))
            self.wait(1)

            solutions = Text(f"x = {root1} or x = {root2}", font_size=32, color=YELLOW)
            solutions.move_to(DOWN * 2.3)
            self.play(Write(solutions))
            self.play(Indicate(solutions, scale_factor=1.2, color=YELLOW))

        elif discriminant == 0:
            sol_text = Text(f"x = {-b} / {2*a} = {root1}", font_size=28)
            sol_text.move_to(DOWN * 1.5)
            self.play(Write(sol_text))

            solutions = Text(f"One solution: x = {root1}", font_size=32, color=YELLOW)
            solutions.move_to(DOWN * 2.3)
            self.play(Write(solutions))
            self.play(Indicate(solutions, color=YELLOW))

        else:
            no_real = Text("Discriminant < 0: No real solutions", font_size=28, color=RED)
            no_real.move_to(DOWN * 1.5)
            self.play(Write(no_real))

        self.wait(2)
'''

quadratic_formula = ManimTemplate(
    id="quadratic_formula",
    name="Quadratic Formula",
    category=TemplateCategory.QUADRATICS,
    description="Solve a quadratic equation using the quadratic formula step by step",
    parameters=[
        ParamSpec(name="a", param_type=ParamType.FLOAT, description="Coefficient of x²", constraints={"min": -10, "max": 10}),
        ParamSpec(name="b", param_type=ParamType.FLOAT, description="Coefficient of x", constraints={"min": -20, "max": 20}),
        ParamSpec(name="c", param_type=ParamType.FLOAT, description="Constant term", constraints={"min": -30, "max": 30}),
        ParamSpec(name="discriminant", param_type=ParamType.FLOAT, description="b² - 4ac", derived_from="b*b - 4*a*c"),
        ParamSpec(name="root1", param_type=ParamType.FLOAT, description="First root", required=False, derived_from="quadratic formula"),
        ParamSpec(name="root2", param_type=ParamType.FLOAT, description="Second root", required=False, derived_from="quadratic formula"),
    ],
    template_code=QUADRATIC_FORMULA_TEMPLATE,
    example_questions=[
        "Use the quadratic formula to solve x² - 5x + 6 = 0",
        "Solve 2x² + 3x - 5 = 0",
        "Find x using quadratic formula: x² + 4x + 4 = 0",
    ],
    tags=["quadratic", "formula", "solve", "discriminant", "roots"],
    compute_derived=compute_quadratic_derived,
)


def get_templates() -> list[ManimTemplate]:
    """Return all quadratic templates."""
    return [
        quadratic_graph,
        quadratic_formula,
    ]
