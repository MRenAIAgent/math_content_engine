# Equations with no solution - contradictions - Basketball & NBA Edition
# Section 2.4

from manim import *

class BasketballContradictionScene(Scene):
    def construct(self):
        # Title
        title = Text("Equations with NO Solution", font_size=48, color=ORANGE)
        subtitle = Text("Basketball Contradiction Example", font_size=32, color=WHITE)
        self.play(Write(title))
        self.wait(1)
        self.play(Write(subtitle.next_to(title, DOWN)))
        self.wait(1)
        self.play(title.animate.scale(0.6).to_edge(UP), FadeOut(subtitle))

        # Basketball scenario setup
        scenario = Text("Scenario: Curry's 3-pointer Challenge", font_size=36, color=BLUE)
        scenario.to_edge(LEFT).shift(UP*2)
        self.play(Write(scenario))
        self.wait(1)

        # Problem statement
        problem_text = Text("If Curry makes 3 shots worth (x + 2) points each,", font_size=28)
        problem_text2 = Text("and this equals 3x + 1 total points...", font_size=28)
        problem_text.next_to(scenario, DOWN, buff=0.5).to_edge(LEFT)
        problem_text2.next_to(problem_text, DOWN, buff=0.3).to_edge(LEFT)
        
        self.play(Write(problem_text))
        self.wait(1)
        self.play(Write(problem_text2))
        self.wait(2)

        # Show the equation
        equation = Text("3(x + 2) = 3x + 1", font_size=40, color=YELLOW)
        equation.move_to(ORIGIN)
        self.play(Write(equation))
        self.wait(2)

        # Step 1: Distribute
        step1_label = Text("Step 1: Distribute the 3", font_size=24, color=GREEN)
        step1_label.to_edge(RIGHT).shift(UP*2)
        self.play(Write(step1_label))

        equation_step1 = Text("3x + 6 = 3x + 1", font_size=40, color=YELLOW)
        equation_step1.move_to(equation.get_center())
        self.play(Transform(equation, equation_step1))
        self.wait(2)

        # Step 2: Subtract 3x from both sides
        step2_label = Text("Step 2: Subtract 3x from both sides", font_size=24, color=GREEN)
        step2_label.next_to(step1_label, DOWN, buff=0.5)
        self.play(Write(step2_label))

        equation_step2 = Text("6 = 1", font_size=40, color=RED)
        equation_step2.move_to(equation.get_center())
        self.play(Transform(equation, equation_step2))
        self.wait(2)

        # Highlight the contradiction
        contradiction_box = SurroundingRectangle(equation, color=RED, buff=0.3)
        self.play(Create(contradiction_box))
        
        false_statement = Text("FALSE STATEMENT!", font_size=36, color=RED)
        false_statement.next_to(equation, DOWN, buff=1)
        self.play(Write(false_statement))
        self.wait(2)

        # Clear for explanation
        self.play(FadeOut(step1_label), FadeOut(step2_label), FadeOut(problem_text), 
                 FadeOut(problem_text2), FadeOut(scenario))

        # Explanation
        explanation = Text("What does this mean?", font_size=32, color=ORANGE)
        explanation.next_to(false_statement, DOWN, buff=1)
        self.play(Write(explanation))
        self.wait(1)

        no_solution = Text("NO SOLUTION EXISTS!", font_size=28, color=WHITE)
        no_solution.next_to(explanation, DOWN, buff=0.5)
        self.play(Write(no_solution))
        self.wait(2)

        # Clear for graphical representation
        self.play(FadeOut(equation), FadeOut(contradiction_box), FadeOut(false_statement),
                 FadeOut(explanation), FadeOut(no_solution))

        # Graphical representation
        graph_title = Text("Graphical View: Parallel Lines", font_size=32, color=BLUE)
        graph_title.move_to(UP*2.5)
        self.play(Write(graph_title))

        # Create coordinate system
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-2, 8, 1],
            x_length=6,
            y_length=5,
            axis_config={"color": WHITE}
        )
        axes.move_to(DOWN*0.5)
        self.play(Create(axes))

        # Add axis labels manually
        x_label = Text("x", font_size=24).next_to(axes.x_axis, RIGHT)
        y_label = Text("y", font_size=24).next_to(axes.y_axis, UP)
        self.play(Write(x_label), Write(y_label))

        # Plot the lines
        line1 = axes.plot(lambda x: 3*x + 6, color=BLUE, x_range=[-3, 3])
        line2 = axes.plot(lambda x: 3*x + 1, color=RED, x_range=[-3, 3])

        line1_label = Text("y = 3x + 6", font_size=20, color=BLUE)
        line1_label.next_to(axes, RIGHT).shift(UP*1)
        line2_label = Text("y = 3x + 1", font_size=20, color=RED)
        line2_label.next_to(line1_label, DOWN, buff=0.3)

        self.play(Create(line1), Write(line1_label))
        self.wait(1)
        self.play(Create(line2), Write(line2_label))
        self.wait(2)

        # Highlight parallel nature
        parallel_text = Text("Same slope (3), different y-intercepts", font_size=24, color=YELLOW)
        parallel_text.next_to(axes, DOWN, buff=0.5)
        self.play(Write(parallel_text))

        never_meet = Text("Parallel lines NEVER intersect = NO SOLUTION", font_size=24, color=ORANGE)
        never_meet.next_to(parallel_text, DOWN, buff=0.3)
        self.play(Write(never_meet))
        self.wait(2)

        # Basketball analogy
        basketball_analogy = Text("Like Curry and LeBron running parallel lanes - they never meet!", 
                                font_size=20, color=GREEN)
        basketball_analogy.next_to(never_meet, DOWN, buff=0.5)
        self.play(Write(basketball_analogy))
        self.wait(3)

        # Final summary
        self.play(FadeOut(VGroup(*self.mobjects)))
        
        summary_title = Text("Key Takeaway", font_size=40, color=ORANGE)
        summary_title.to_edge(UP)
        self.play(Write(summary_title))

        summary1 = Text("When solving leads to a FALSE statement (like 6 = 1),", font_size=28)
        summary2 = Text("the equation has NO SOLUTION", font_size=28, color=RED)
        summary3 = Text("Graphically: Parallel lines that never intersect", font_size=28, color=BLUE)
        
        summary1.next_to(summary_title, DOWN, buff=1)
        summary2.next_to(summary1, DOWN, buff=0.5)
        summary3.next_to(summary2, DOWN, buff=0.5)
        
        self.play(Write(summary1))
        self.wait(1)
        self.play(Write(summary2))
        self.wait(1)
        self.play(Write(summary3))
        self.wait(3)