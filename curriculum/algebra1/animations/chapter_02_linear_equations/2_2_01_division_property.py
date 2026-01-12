# Division Property of Equality for solving equations
# Generated for Chapter 2 - Section 2.2

from manim import *

class DivisionPropertyEqualityScene(Scene):
    def construct(self):
        # Title
        title = Text("Division Property of Equality", font_size=48, color=BLUE)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Step 1: Show initial equation
        step1_text = Text("Step 1: Start with the equation", font_size=32, color=WHITE)
        step1_text.move_to(UP * 2)
        self.play(Write(step1_text))
        
        equation1 = Text("7x = 91", font_size=48, color=YELLOW)
        equation1.move_to(UP * 0.5)
        self.play(Write(equation1))
        self.wait(2)

        # Step 2: Explain the strategy
        self.play(FadeOut(step1_text))
        step2_text = Text("Step 2: Divide both sides by 7 to isolate x", font_size=32, color=WHITE)
        step2_text.move_to(UP * 2)
        self.play(Write(step2_text))
        self.wait(2)

        # Step 3: Show division setup
        self.play(FadeOut(step2_text))
        step3_text = Text("Step 3: Apply division to both sides", font_size=32, color=WHITE)
        step3_text.move_to(UP * 2)
        self.play(Write(step3_text))

        # Transform equation to show division
        equation2 = Text("7x/7 = 91/7", font_size=48, color=YELLOW)
        equation2.move_to(UP * 0.5)
        self.play(ReplacementTransform(equation1, equation2))
        
        # Highlight the 7's that will cancel
        seven_left = Text("7", font_size=48, color=RED)
        seven_left.move_to(LEFT * 1.8 + UP * 0.5)
        seven_denom_left = Text("7", font_size=48, color=RED)
        seven_denom_left.move_to(LEFT * 1.8 + UP * 0.1)
        
        self.play(
            Indicate(seven_left),
            Indicate(seven_denom_left)
        )
        self.wait(1)

        # Show cancellation with crossing out animation
        cancel_line_left = Line(LEFT * 2.1 + UP * 0.7, LEFT * 1.5 + UP * 0.3, color=RED, stroke_width=6)
        self.play(Create(cancel_line_left))
        self.wait(2)

        # Step 4: Simplify
        self.play(FadeOut(step3_text))
        step4_text = Text("Step 4: Simplify", font_size=32, color=WHITE)
        step4_text.move_to(UP * 2)
        self.play(Write(step4_text))

        equation3 = Text("x = 13", font_size=48, color=GREEN)
        equation3.move_to(UP * 0.5)
        self.play(ReplacementTransform(equation2, equation3))
        self.play(FadeOut(cancel_line_left))
        self.wait(2)

        # Step 5: Verify the solution
        self.play(FadeOut(step4_text))
        step5_text = Text("Step 5: Verify the solution", font_size=32, color=WHITE)
        step5_text.move_to(UP * 2)
        self.play(Write(step5_text))

        # Show verification
        verify_text = Text("Substitute x = 13 back into original equation:", font_size=28, color=WHITE)
        verify_text.move_to(DOWN * 0.5)
        self.play(Write(verify_text))

        verification = Text("7(13) = 91", font_size=40, color=ORANGE)
        verification.move_to(DOWN * 1.3)
        self.play(Write(verification))

        calculation = Text("91 = 91 ✓", font_size=40, color=GREEN)
        calculation.move_to(DOWN * 2)
        self.play(Write(calculation))
        self.wait(2)

        # Summary
        self.play(
            FadeOut(step5_text),
            FadeOut(verify_text),
            FadeOut(verification),
            FadeOut(calculation)
        )

        summary_title = Text("Division Property of Equality:", font_size=36, color=BLUE)
        summary_title.move_to(DOWN * 0.5)
        
        summary_text = Text("If a = b, then a/c = b/c (where c ≠ 0)", font_size=32, color=WHITE)
        summary_text.move_to(DOWN * 1.3)
        
        self.play(Write(summary_title))
        self.play(Write(summary_text))
        
        # Final highlight of solution
        self.play(Indicate(equation3, scale_factor=1.2))
        self.wait(3)