# Equations with infinitely many solutions - identities
# Generated for Chapter 2 - Section 2.4

from manim import *

class IdentityEquationScene(Scene):
    def construct(self):
        # Title
        title = Text("Equations with Infinitely Many Solutions - Identities", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Original equation
        original_eq = Text("2(x + 3) = 2x + 6", font_size=40).move_to(UP * 2)
        self.play(Write(original_eq))
        self.wait(2)

        # Step 1: Distribute
        step1_label = Text("Step 1: Distribute", font_size=32, color=BLUE).move_to(UP * 0.5)
        self.play(Write(step1_label))
        
        distributed_eq = Text("2x + 6 = 2x + 6", font_size=40).move_to(ORIGIN)
        self.play(Transform(original_eq.copy(), distributed_eq))
        self.wait(2)

        # Step 2: Both sides identical
        step2_label = Text("Step 2: Both sides are IDENTICAL", font_size=32, color=BLUE).move_to(DOWN * 0.8)
        self.play(Write(step2_label))
        
        # Highlight identical parts
        left_side = Text("2x + 6", font_size=40, color=GREEN).move_to(LEFT * 1.5)
        equals = Text("=", font_size=40).move_to(ORIGIN)
        right_side = Text("2x + 6", font_size=40, color=GREEN).move_to(RIGHT * 1.5)
        
        identical_eq = VGroup(left_side, equals, right_side).move_to(DOWN * 1.8)
        self.play(Write(identical_eq))
        self.wait(2)

        # Clear previous steps
        self.play(FadeOut(step1_label), FadeOut(step2_label), FadeOut(distributed_eq))

        # Step 3: Subtract 2x from both sides
        step3_label = Text("Step 3: Subtract 2x from both sides", font_size=32, color=BLUE).move_to(UP * 0.5)
        self.play(Write(step3_label))
        
        result_eq = Text("6 = 6", font_size=50, color=GREEN).move_to(ORIGIN)
        self.play(Transform(identical_eq, result_eq))
        
        true_statement = Text("TRUE for ALL x!", font_size=36, color=RED).move_to(DOWN * 0.8)
        self.play(Write(true_statement))
        
        # Green checkmark
        checkmark = Text("✓", font_size=60, color=GREEN).next_to(result_eq, RIGHT)
        self.play(Write(checkmark))
        self.wait(2)

        # Step 4: Identity
        step4_label = Text("Step 4: This is called an IDENTITY", font_size=32, color=BLUE).move_to(DOWN * 1.8)
        self.play(Write(step4_label))
        self.wait(2)

        # Step 5: Infinitely many solutions
        self.play(FadeOut(step3_label), FadeOut(step4_label), FadeOut(true_statement))
        
        step5_label = Text("Step 5: Every real number is a solution", font_size=32, color=BLUE).move_to(UP * 0.5)
        self.play(Write(step5_label))
        
        infinity_symbol = Text("∞", font_size=80, color=YELLOW).move_to(DOWN * 0.5)
        infinity_text = Text("Infinitely Many Solutions", font_size=36, color=YELLOW).move_to(DOWN * 1.5)
        
        self.play(Write(infinity_symbol))
        self.play(Write(infinity_text))
        self.wait(2)

        # Clear for graph
        self.play(FadeOut(VGroup(original_eq, result_eq, checkmark, step5_label, infinity_symbol, infinity_text)))

        # Graph section
        graph_title = Text("Graphical Representation", font_size=36, color=BLUE).move_to(UP * 3)
        self.play(Write(graph_title))

        # Create axes
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-2, 8, 2],
            x_length=6,
            y_length=4,
            tips=False
        ).move_to(DOWN * 0.5)
        
        self.play(Create(axes))

        # Axis labels
        x_label = Text("x", font_size=24).next_to(axes.x_axis, RIGHT)
        y_label = Text("y", font_size=24).next_to(axes.y_axis, UP)
        self.play(Write(x_label), Write(y_label))

        # Draw the line y = 2x + 6
        line = axes.plot(lambda x: 2*x + 6, x_range=[-3, 1], color=GREEN)
        
        # Labels for left and right sides
        left_equation = Text("Left: y = 2(x + 3)", font_size=28, color=GREEN).move_to(UP * 1.5 + LEFT * 3)
        right_equation = Text("Right: y = 2x + 6", font_size=28, color=GREEN).move_to(UP * 1.5 + RIGHT * 3)
        
        self.play(Write(left_equation))
        self.play(Write(right_equation))
        self.play(Create(line))
        
        # Same line explanation
        same_line_text = Text("SAME LINE!", font_size=36, color=RED).move_to(DOWN * 2.5)
        self.play(Write(same_line_text))
        self.wait(2)

        # Final summary
        self.play(FadeOut(VGroup(axes, line, x_label, y_label, left_equation, right_equation, same_line_text, graph_title)))
        
        summary_title = Text("Key Takeaway", font_size=40, color=YELLOW).move_to(UP * 2)
        summary1 = Text("When an equation simplifies to a TRUE statement", font_size=32).move_to(UP * 0.5)
        summary2 = Text("like 6 = 6, it's called an IDENTITY", font_size=32).move_to(ORIGIN)
        summary3 = Text("and has INFINITELY MANY solutions!", font_size=32, color=GREEN).move_to(DOWN * 0.8)
        
        final_infinity = Text("∞", font_size=60, color=YELLOW).move_to(DOWN * 2)
        
        self.play(Write(summary_title))
        self.play(Write(summary1))
        self.play(Write(summary2))
        self.play(Write(summary3))
        self.play(Write(final_infinity))
        self.wait(3)