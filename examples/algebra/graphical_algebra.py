"""
Graphical Algebra Examples - Visual representations for better understanding.

These examples show how to visualize algebra concepts using:
1. Coordinate planes (graphs) - line intersections, parabola roots
2. Balance scales (for equations)
3. Number lines with arrows
4. Rise/run triangles for slope

All examples use Text() instead of MathTex() to avoid LaTeX dependency.

Run individual examples:
    manim -pql examples/graphical_algebra.py LinearEquationGraphScene
    manim -pql examples/graphical_algebra.py QuadraticGraphScene
    manim -pql examples/graphical_algebra.py BalanceScaleEquationScene
"""

from manim import *


class LinearEquationGraphScene(Scene):
    """
    Solve 2x + 3 = 7 by showing where y = 2x + 3 intersects y = 7.
    Visual approach: The solution is where the line crosses the horizontal line.
    """
    def construct(self):
        # Title
        title = Text("Solving 2x + 3 = 7 Graphically", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP).scale(0.8))

        # Create coordinate axes (no numbers to avoid LaTeX)
        axes = Axes(
            x_range=[-1, 5, 1],
            y_range=[-1, 10, 2],
            x_length=6,
            y_length=5,
            axis_config={"include_numbers": False},
        ).shift(DOWN * 0.5)

        # Add number labels manually using Text
        x_nums = VGroup(*[
            Text(str(i), font_size=16).next_to(axes.c2p(i, 0), DOWN, buff=0.1)
            for i in range(0, 5)
        ])
        y_nums = VGroup(*[
            Text(str(i), font_size=16).next_to(axes.c2p(0, i), LEFT, buff=0.1)
            for i in range(0, 10, 2)
        ])

        x_label = Text("x", font_size=24).next_to(axes.x_axis, RIGHT)
        y_label = Text("y", font_size=24).next_to(axes.y_axis, UP)

        self.play(Create(axes), Write(x_label), Write(y_label))
        self.play(Write(x_nums), Write(y_nums))
        self.wait(1)

        # Plot y = 2x + 3 (the line)
        line_func = axes.plot(lambda x: 2*x + 3, x_range=[-0.5, 3.5], color=BLUE)
        line_label = Text("y = 2x + 3", font_size=24, color=BLUE)
        line_label.next_to(line_func, RIGHT, buff=0.3)

        self.play(Create(line_func), Write(line_label))
        self.wait(1)

        # Plot y = 7 (horizontal line)
        horizontal_line = axes.plot(lambda x: 7, x_range=[-0.5, 3.5], color=RED)
        horiz_label = Text("y = 7", font_size=24, color=RED)
        horiz_label.next_to(horizontal_line, LEFT, buff=0.3)

        self.play(Create(horizontal_line), Write(horiz_label))
        self.wait(1)

        # Find and highlight intersection point (x=2, y=7)
        intersection_point = Dot(axes.c2p(2, 7), color=YELLOW, radius=0.15)
        intersection_label = Text("(2, 7)", font_size=24, color=YELLOW)
        intersection_label.next_to(intersection_point, UR, buff=0.2)

        self.play(Create(intersection_point), Write(intersection_label))
        self.play(Flash(intersection_point, color=YELLOW))
        self.wait(1)

        # Draw dashed line down to x-axis to show x = 2
        dashed_line = DashedLine(
            axes.c2p(2, 7), axes.c2p(2, 0), color=GREEN
        )
        solution_dot = Dot(axes.c2p(2, 0), color=GREEN, radius=0.12)

        self.play(Create(dashed_line), Create(solution_dot))
        self.wait(0.5)

        # Show the solution
        solution_text = Text("Solution: x = 2", font_size=32, color=GREEN)
        solution_text.to_edge(DOWN)
        self.play(Write(solution_text))
        self.play(Indicate(solution_text, color=GREEN))
        self.wait(2)


class QuadraticGraphScene(Scene):
    """
    Solve x² - 4 = 0 by showing where the parabola crosses the x-axis.
    Visual approach: Solutions are the x-intercepts (roots).
    """
    def construct(self):
        # Title
        title = Text("Solving x² - 4 = 0 Graphically", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP).scale(0.8))

        # Create coordinate axes
        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-5, 6, 2],
            x_length=7,
            y_length=5,
            axis_config={"include_numbers": False},
        ).shift(DOWN * 0.3)

        # Add number labels
        x_nums = VGroup(*[
            Text(str(i), font_size=14).next_to(axes.c2p(i, 0), DOWN, buff=0.1)
            for i in range(-3, 4) if i != 0
        ])
        y_nums = VGroup(*[
            Text(str(i), font_size=14).next_to(axes.c2p(0, i), LEFT, buff=0.1)
            for i in range(-4, 6, 2) if i != 0
        ])

        x_label = Text("x", font_size=24).next_to(axes.x_axis, RIGHT)
        y_label = Text("y", font_size=24).next_to(axes.y_axis, UP)

        self.play(Create(axes), Write(x_label), Write(y_label))
        self.play(Write(x_nums), Write(y_nums))
        self.wait(1)

        # Plot y = x² - 4 (parabola)
        parabola = axes.plot(lambda x: x**2 - 4, x_range=[-3, 3], color=BLUE)
        parabola_label = Text("y = x² - 4", font_size=24, color=BLUE)
        parabola_label.next_to(axes.c2p(2.5, 2), RIGHT)

        self.play(Create(parabola), Write(parabola_label))
        self.wait(1)

        # Highlight x-axis (y = 0)
        x_axis_highlight = axes.plot(lambda x: 0, x_range=[-3.5, 3.5], color=RED, stroke_width=4)
        y_zero_label = Text("y = 0 (x-axis)", font_size=18, color=RED)
        y_zero_label.next_to(axes.c2p(3.5, 0), UP)

        self.play(Create(x_axis_highlight), Write(y_zero_label))
        self.wait(1)

        # Find and highlight intersection points (x = -2 and x = 2)
        root1 = Dot(axes.c2p(-2, 0), color=YELLOW, radius=0.15)
        root2 = Dot(axes.c2p(2, 0), color=YELLOW, radius=0.15)
        root1_label = Text("x = -2", font_size=24, color=YELLOW).next_to(root1, DL)
        root2_label = Text("x = 2", font_size=24, color=YELLOW).next_to(root2, DR)

        self.play(Create(root1), Write(root1_label))
        self.play(Flash(root1, color=YELLOW))
        self.wait(0.5)

        self.play(Create(root2), Write(root2_label))
        self.play(Flash(root2, color=YELLOW))
        self.wait(1)

        # Show the solution
        solution_text = Text("Solutions: x = -2 or x = 2", font_size=32, color=GREEN)
        solution_text.to_edge(DOWN)
        self.play(Write(solution_text))
        self.wait(1)

        # Factor form
        factor_text = Text("Factored: (x + 2)(x - 2) = 0", font_size=26, color=ORANGE)
        factor_text.next_to(solution_text, UP)
        self.play(Write(factor_text))
        self.wait(2)


class BalanceScaleEquationScene(Scene):
    """
    Solve 2x + 3 = 7 using a balance scale visualization.
    Visual approach: Keep the scale balanced by doing the same to both sides.
    """
    def construct(self):
        # Title
        title = Text("Solving Equations: Balance Scale", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP).scale(0.8))

        # Create balance scale base
        base = Rectangle(width=4, height=0.3, color=GRAY, fill_opacity=1)
        base.shift(DOWN * 2.5)

        fulcrum = Triangle(color=GRAY, fill_opacity=1).scale(0.4)
        fulcrum.move_to(base.get_top())

        beam = Rectangle(width=6, height=0.15, color=GOLD, fill_opacity=1)
        beam.move_to(fulcrum.get_top() + UP * 0.1)

        # Left and right pans
        left_pan = Rectangle(width=2, height=0.1, color=WHITE, fill_opacity=0.8)
        left_pan.move_to(beam.get_left() + DOWN * 0.5)
        left_string = Line(beam.get_left(), left_pan.get_top(), color=WHITE)

        right_pan = Rectangle(width=2, height=0.1, color=WHITE, fill_opacity=0.8)
        right_pan.move_to(beam.get_right() + DOWN * 0.5)
        right_string = Line(beam.get_right(), right_pan.get_top(), color=WHITE)

        scale = VGroup(base, fulcrum, beam, left_pan, left_string, right_pan, right_string)
        self.play(Create(scale))
        self.wait(1)

        # Show equation: 2x + 3 = 7
        equation = Text("2x + 3 = 7", font_size=32)
        equation.move_to(UP * 2)
        self.play(Write(equation))
        self.wait(1)

        # Left side: 2 x-boxes + 3 unit squares
        x_box1 = Square(side_length=0.4, color=BLUE, fill_opacity=0.7)
        x_label1 = Text("x", font_size=16, color=WHITE).move_to(x_box1)
        x1 = VGroup(x_box1, x_label1)

        x_box2 = Square(side_length=0.4, color=BLUE, fill_opacity=0.7)
        x_label2 = Text("x", font_size=16, color=WHITE).move_to(x_box2)
        x2 = VGroup(x_box2, x_label2)

        unit1 = Square(side_length=0.3, color=GREEN, fill_opacity=0.7)
        unit2 = Square(side_length=0.3, color=GREEN, fill_opacity=0.7)
        unit3 = Square(side_length=0.3, color=GREEN, fill_opacity=0.7)

        left_items = VGroup(x1, x2, unit1, unit2, unit3).arrange(RIGHT, buff=0.1)
        left_items.move_to(left_pan.get_top() + UP * 0.4)

        # Right side: 7 unit squares
        right_units = VGroup(*[
            Square(side_length=0.3, color=YELLOW, fill_opacity=0.7)
            for _ in range(7)
        ]).arrange_in_grid(rows=2, buff=0.1)
        right_units.move_to(right_pan.get_top() + UP * 0.5)

        self.play(Create(left_items))
        self.play(Create(right_units))
        self.wait(1)

        # Step 1: Remove 3 from both sides
        step1 = Text("Step 1: Remove 3 from both sides", font_size=24, color=ORANGE)
        step1.move_to(UP * 1.2)
        self.play(Write(step1))
        self.wait(1)

        # Animate removing 3 units from each side
        self.play(
            FadeOut(unit1), FadeOut(unit2), FadeOut(unit3),
            FadeOut(right_units[4]), FadeOut(right_units[5]), FadeOut(right_units[6])
        )

        # Rearrange remaining items
        remaining_left = VGroup(x1, x2).arrange(RIGHT, buff=0.2)
        remaining_left.move_to(left_pan.get_top() + UP * 0.4)

        remaining_right = VGroup(right_units[0], right_units[1], right_units[2], right_units[3])
        remaining_right.arrange(RIGHT, buff=0.1)
        remaining_right.move_to(right_pan.get_top() + UP * 0.4)

        self.play(
            x1.animate.move_to(remaining_left[0].get_center()),
            x2.animate.move_to(remaining_left[1].get_center()),
        )
        self.wait(1)

        # Update equation
        equation2 = Text("2x = 4", font_size=32)
        equation2.move_to(equation.get_center())
        self.play(ReplacementTransform(equation, equation2), FadeOut(step1))
        self.wait(1)

        # Step 2: Divide both sides by 2
        step2 = Text("Step 2: Divide both sides by 2", font_size=24, color=ORANGE)
        step2.move_to(UP * 1.2)
        self.play(Write(step2))
        self.wait(1)

        # Show division - group items
        left_group = SurroundingRectangle(VGroup(x1), color=RED, buff=0.1)
        right_group = SurroundingRectangle(
            VGroup(right_units[0], right_units[1]), color=RED, buff=0.1
        )

        self.play(Create(left_group), Create(right_group))
        self.wait(1)

        # Final result
        equation3 = Text("x = 2", font_size=36, color=GREEN)
        equation3.move_to(equation2.get_center())
        self.play(
            ReplacementTransform(equation2, equation3),
            FadeOut(step2), FadeOut(left_group), FadeOut(right_group)
        )
        self.play(Indicate(equation3, scale_factor=1.3, color=GREEN))
        self.wait(2)


class NumberLineAdditionScene(Scene):
    """
    Visualize -3 + 5 = 2 on a number line.
    Shows how negative and positive numbers work with arrows.
    """
    def construct(self):
        # Title
        title = Text("Adding on a Number Line: -3 + 5", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Create number line manually (no LaTeX)
        line = Line(LEFT * 5.5, RIGHT * 5.5, color=WHITE)
        self.play(Create(line))

        # Add tick marks and labels
        ticks = VGroup()
        labels = VGroup()
        for i in range(-5, 6):
            tick = Line(UP * 0.1, DOWN * 0.1, color=WHITE)
            tick.move_to(RIGHT * i)
            ticks.add(tick)
            label = Text(str(i), font_size=20)
            label.next_to(tick, DOWN, buff=0.15)
            labels.add(label)

        self.play(Create(ticks), Write(labels))
        self.wait(1)

        # Start at -3
        dot = Dot(RIGHT * (-3), color=RED, radius=0.15)
        start_label = Text("Start: -3", font_size=24, color=RED)
        start_label.next_to(dot, UP, buff=0.3)

        self.play(Create(dot), Write(start_label))
        self.wait(1)

        # Show +5 movement with curved arrow
        arrow = CurvedArrow(
            RIGHT * (-3) + UP * 0.4,
            RIGHT * 2 + UP * 0.4,
            color=GREEN,
            angle=-TAU/4
        )
        add_label = Text("+5", font_size=28, color=GREEN)
        add_label.next_to(arrow, UP, buff=0.1)

        self.play(Create(arrow), Write(add_label))
        self.wait(1)

        # Animate the dot moving
        self.play(FadeOut(start_label))
        self.play(dot.animate.move_to(RIGHT * 2), run_time=2)
        self.wait(0.5)

        # Show result
        result_label = Text("Result: 2", font_size=24, color=YELLOW)
        result_label.next_to(dot, DOWN, buff=0.4)
        self.play(Write(result_label))
        self.play(Flash(dot, color=YELLOW))
        self.wait(1)

        # Final equation
        final = Text("-3 + 5 = 2", font_size=36, color=WHITE)
        final.to_edge(DOWN)
        self.play(Write(final))
        self.wait(2)


class SlopeVisualizationScene(Scene):
    """
    Visualize slope as rise/run with animated triangles.
    """
    def construct(self):
        # Title
        title = Text("Understanding Slope: Rise over Run", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP).scale(0.8))

        # Create coordinate axes
        axes = Axes(
            x_range=[-1, 7, 1],
            y_range=[-1, 7, 1],
            x_length=6,
            y_length=5,
            axis_config={"include_numbers": False},
        ).shift(DOWN * 0.3 + LEFT * 1)

        # Add labels
        x_nums = VGroup(*[
            Text(str(i), font_size=14).next_to(axes.c2p(i, 0), DOWN, buff=0.1)
            for i in range(0, 7)
        ])
        y_nums = VGroup(*[
            Text(str(i), font_size=14).next_to(axes.c2p(0, i), LEFT, buff=0.1)
            for i in range(0, 7)
        ])

        self.play(Create(axes))
        self.play(Write(x_nums), Write(y_nums))
        self.wait(1)

        # Plot a line y = (2/3)x + 1
        line = axes.plot(lambda x: (2/3)*x + 1, x_range=[0, 6], color=BLUE, stroke_width=3)
        line_label = Text("y = (2/3)x + 1", font_size=24, color=BLUE)
        line_label.to_edge(RIGHT).shift(UP)

        self.play(Create(line), Write(line_label))
        self.wait(1)

        # Show two points on the line
        point1 = Dot(axes.c2p(1.5, 2), color=YELLOW, radius=0.12)
        point2 = Dot(axes.c2p(4.5, 4), color=YELLOW, radius=0.12)

        self.play(Create(point1), Create(point2))
        self.wait(1)

        # Draw rise/run triangle
        # Horizontal line (run)
        run_line = Line(axes.c2p(1.5, 2), axes.c2p(4.5, 2), color=RED, stroke_width=4)
        run_label = Text("Run = 3", font_size=20, color=RED)
        run_label.next_to(run_line, DOWN)

        # Vertical line (rise)
        rise_line = Line(axes.c2p(4.5, 2), axes.c2p(4.5, 4), color=GREEN, stroke_width=4)
        rise_label = Text("Rise = 2", font_size=20, color=GREEN)
        rise_label.next_to(rise_line, RIGHT)

        self.play(Create(run_line), Write(run_label))
        self.wait(1)
        self.play(Create(rise_line), Write(rise_label))
        self.wait(1)

        # Show slope formula
        slope_formula = Text("Slope = Rise / Run = 2/3", font_size=28, color=ORANGE)
        slope_formula.to_edge(DOWN)
        self.play(Write(slope_formula))
        self.wait(1)

        # Animate showing what slope means
        explanation = Text("For every 3 units right, go 2 units up", font_size=22)
        explanation.next_to(slope_formula, UP)
        self.play(Write(explanation))
        self.wait(2)


class InequalityNumberLineScene(Scene):
    """
    Visualize x > 3 on a number line with shading.
    """
    def construct(self):
        # Title
        title = Text("Graphing Inequalities: x > 3", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Create number line manually
        line = Line(LEFT * 5, RIGHT * 5, color=WHITE)
        self.play(Create(line))

        # Add tick marks and labels
        ticks = VGroup()
        labels = VGroup()
        for i in range(-1, 9):
            tick = Line(UP * 0.1, DOWN * 0.1, color=WHITE)
            tick.move_to(LEFT * 4 + RIGHT * i)
            ticks.add(tick)
            label = Text(str(i), font_size=20)
            label.next_to(tick, DOWN, buff=0.15)
            labels.add(label)

        self.play(Create(ticks), Write(labels))
        self.wait(1)

        # Show the boundary point (open circle for >)
        boundary_pos = LEFT * 4 + RIGHT * 4  # x = 3
        boundary = Circle(radius=0.15, color=RED, stroke_width=3)
        boundary.move_to(boundary_pos)

        boundary_label = Text("x = 3 (not included)", font_size=20, color=RED)
        boundary_label.next_to(boundary, UP, buff=0.5)

        self.play(Create(boundary), Write(boundary_label))
        self.wait(1)

        # Shade the region x > 3
        shade = Rectangle(
            width=4.5, height=0.3,
            color=GREEN, fill_opacity=0.5,
            stroke_width=0
        )
        shade.move_to(boundary_pos + RIGHT * 2.4)

        # Arrow pointing right (to infinity)
        arrow = Arrow(
            boundary_pos + RIGHT * 0.2,
            boundary_pos + RIGHT * 4.5,
            color=GREEN, buff=0
        )

        self.play(FadeIn(shade), Create(arrow))
        self.wait(1)

        # Show solution notation
        solution = Text("Solution: x > 3  or  (3, infinity)", font_size=28, color=GREEN)
        solution.to_edge(DOWN)
        self.play(Write(solution))
        self.wait(1)

        # Show test points
        test_good = Dot(LEFT * 4 + RIGHT * 6, color=YELLOW, radius=0.12)  # x = 5
        test_good_label = Text("x=5 (works!)", font_size=16, color=YELLOW)
        test_good_label.next_to(test_good, DOWN, buff=0.3)

        test_bad = Dot(LEFT * 4 + RIGHT * 2, color=GRAY, radius=0.12)  # x = 1
        test_bad_label = Text("x=1 (no)", font_size=16, color=GRAY)
        test_bad_label.next_to(test_bad, DOWN, buff=0.3)

        self.play(Create(test_good), Write(test_good_label))
        self.play(Create(test_bad), Write(test_bad_label))
        self.wait(2)


class SystemOfEquationsGraphScene(Scene):
    """
    Solve a system of equations by finding where two lines intersect.
    y = 2x - 1 and y = -x + 5
    """
    def construct(self):
        # Title
        title = Text("Solving Systems of Equations", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP).scale(0.8))

        # Create axes
        axes = Axes(
            x_range=[-1, 6, 1],
            y_range=[-2, 8, 1],
            x_length=6,
            y_length=5,
            axis_config={"include_numbers": False},
        ).shift(DOWN * 0.3)

        # Add labels
        x_nums = VGroup(*[
            Text(str(i), font_size=14).next_to(axes.c2p(i, 0), DOWN, buff=0.1)
            for i in range(0, 6)
        ])
        y_nums = VGroup(*[
            Text(str(i), font_size=14).next_to(axes.c2p(0, i), LEFT, buff=0.1)
            for i in range(-1, 8, 2)
        ])

        self.play(Create(axes))
        self.play(Write(x_nums), Write(y_nums))
        self.wait(1)

        # Line 1: y = 2x - 1 (steep positive slope)
        line1 = axes.plot(lambda x: 2*x - 1, x_range=[0, 4], color=BLUE, stroke_width=3)
        line1_label = Text("y = 2x - 1", font_size=22, color=BLUE)
        line1_label.next_to(axes.c2p(4, 7), RIGHT)

        self.play(Create(line1), Write(line1_label))
        self.wait(1)

        # Line 2: y = -x + 5 (negative slope)
        line2 = axes.plot(lambda x: -x + 5, x_range=[0, 5.5], color=RED, stroke_width=3)
        line2_label = Text("y = -x + 5", font_size=22, color=RED)
        line2_label.next_to(axes.c2p(0.5, 4.5), LEFT)

        self.play(Create(line2), Write(line2_label))
        self.wait(1)

        # Find intersection: 2x - 1 = -x + 5 => 3x = 6 => x = 2, y = 3
        intersection = Dot(axes.c2p(2, 3), color=YELLOW, radius=0.18)
        int_label = Text("(2, 3)", font_size=24, color=YELLOW)
        int_label.next_to(intersection, UR, buff=0.2)

        self.play(Create(intersection))
        self.play(Flash(intersection, color=YELLOW, line_length=0.3))
        self.play(Write(int_label))
        self.wait(1)

        # Solution
        solution = Text("Solution: x = 2, y = 3", font_size=30, color=GREEN)
        solution.to_edge(DOWN)
        self.play(Write(solution))
        self.play(Indicate(solution, color=GREEN))
        self.wait(2)


# For testing individual scenes
if __name__ == "__main__":
    print("Run with: manim -pql examples/graphical_algebra.py <SceneName>")
    print("\nAvailable scenes:")
    print("  - LinearEquationGraphScene (line intersection)")
    print("  - QuadraticGraphScene (parabola roots)")
    print("  - BalanceScaleEquationScene (balance scale)")
    print("  - NumberLineAdditionScene (number line)")
    print("  - SlopeVisualizationScene (rise/run)")
    print("  - InequalityNumberLineScene (shading)")
    print("  - SystemOfEquationsGraphScene (two lines)")
