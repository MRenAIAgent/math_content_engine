# Equations with no solution - contradictions
# Generated for Chapter 2 - Section 2.4

from manim import *

class ContradictionEquationScene(Scene):
    def construct(self):
        # Title
        title = Text("Equations with No Solution - Contradictions", font_size=36, color=BLUE)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Original equation
        original_eq = Text("3(x + 2) = 3x + 1", font_size=32)
        original_eq.move_to(UP * 2)
        self.play(Write(original_eq))
        self.wait(1)

        # Step 1: Distribute
        step1_label = Text("Step 1: Distribute", font_size=24, color=GREEN).to_edge(LEFT)
        step1_eq = Text("3x + 6 = 3x + 1", font_size=32)
        step1_eq.next_to(step1_label, RIGHT, buff=1)
        
        self.play(Write(step1_label))
        self.play(Transform(original_eq, step1_eq))
        self.wait(1.5)

        # Step 2: Subtract 3x from both sides
        step2_label = Text("Step 2: Subtract 3x from both sides", font_size=24, color=GREEN)
        step2_label.next_to(step1_label, DOWN, buff=0.5, aligned_edge=LEFT)
        step2_eq = Text("6 = 1", font_size=32, color=RED)
        step2_eq.next_to(step2_label, RIGHT, buff=1)
        
        self.play(Write(step2_label))
        self.play(ReplacementTransform(original_eq, step2_eq))
        self.wait(1)

        # Red X for contradiction
        red_x = Text("✗", font_size=48, color=RED)
        red_x.next_to(step2_eq, RIGHT, buff=0.5)
        self.play(Write(red_x))
        self.wait(1)

        # Step 3: Contradiction explanation
        step3_label = Text("Step 3: This is a CONTRADICTION!", font_size=28, color=RED)
        step3_label.next_to(step2_label, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(Write(step3_label))
        self.wait(1)

        # Step 4: No solution
        step4_label = Text("Step 4: When we get a false statement,", font_size=24, color=ORANGE)
        step4_label.next_to(step3_label, DOWN, buff=0.3, aligned_edge=LEFT)
        step4_conclusion = Text("the equation has NO SOLUTION", font_size=24, color=ORANGE)
        step4_conclusion.next_to(step4_label, DOWN, buff=0.2, aligned_edge=LEFT)
        
        self.play(Write(step4_label))
        self.play(Write(step4_conclusion))
        self.wait(2)

        # Clear previous content
        self.play(FadeOut(step1_label, step2_label, step2_eq, red_x, step3_label, step4_label, step4_conclusion))
        self.wait(0.5)

        # Graphical representation
        graph_title = Text("Graphical Representation", font_size=28, color=BLUE)
        graph_title.move_to(UP * 2.5)
        self.play(Write(graph_title))

        # Create axes
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-2, 8, 2],
            x_length=6,
            y_length=4,
            tips=False
        )
        axes.move_to(DOWN * 0.5)
        
        # Create axis labels manually
        x_label = Text("x", font_size=20).next_to(axes.x_axis, RIGHT)
        y_label = Text("y", font_size=20).next_to(axes.y_axis, UP)
        
        self.play(Create(axes))
        self.play(Write(x_label), Write(y_label))

        # Left side: y = 3x + 6
        line1 = axes.plot(lambda x: 3*x + 6, color=BLUE, x_range=[-3, 0])
        line1_label = Text("y = 3x + 6", font_size=20, color=BLUE)
        line1_label.next_to(axes, UP + LEFT)

        # Right side: y = 3x + 1
        line2 = axes.plot(lambda x: 3*x + 1, color=RED, x_range=[-2, 1])
        line2_label = Text("y = 3x + 1", font_size=20, color=RED)
        line2_label.next_to(line1_label, DOWN, aligned_edge=LEFT)

        self.play(Create(line1))
        self.play(Write(line1_label))
        self.wait(1)
        
        self.play(Create(line2))
        self.play(Write(line2_label))
        self.wait(1)

        # Parallel lines explanation
        parallel_text = Text("Parallel lines never intersect!", font_size=24, color=YELLOW)
        parallel_text.next_to(axes, DOWN)
        self.play(Write(parallel_text))
        self.wait(1)

        no_solution_text = Text("Therefore: NO SOLUTION", font_size=26, color=RED)
        no_solution_text.next_to(parallel_text, DOWN)
        self.play(Write(no_solution_text))
        self.wait(2)

        # Final summary
        self.play(FadeOut(graph_title, axes, x_label, y_label, line1, line2, 
                         line1_label, line2_label, parallel_text, no_solution_text))
        
        summary = Text("Key Takeaway: When solving leads to a false statement\nlike 6 = 1, the equation has NO SOLUTION", 
                      font_size=24, color=WHITE)
        summary.move_to(ORIGIN)
        self.play(Write(summary))
        self.wait(3)