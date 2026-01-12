# Solving equations with fraction coefficients using reciprocals
# Generated for Chapter 2 - Section 2.2

from manim import *

class FractionCoefficientScene(Scene):
    def construct(self):
        # Title
        title = Text("Solving Equations with Fraction Coefficients", font_size=36, color=BLUE)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Step 1: Show initial equation
        step1_text = Text("Step 1: Start with the equation", font_size=24, color=WHITE)
        step1_text.move_to(UP * 2)
        self.play(Write(step1_text))
        
        equation1 = Text("(2/3)x = 18", font_size=48)
        equation1.move_to(UP * 1)
        self.play(Write(equation1))
        self.wait(2)

        # Step 2: Explain reciprocal multiplication
        step2_text = Text("Step 2: Multiply both sides by the reciprocal 3/2", font_size=24, color=WHITE)
        step2_text.move_to(ORIGIN)
        self.play(Write(step2_text))
        
        # Highlight the fraction coefficient
        fraction_highlight = SurroundingRectangle(equation1[:5], color=YELLOW, buff=0.1)
        self.play(Create(fraction_highlight))
        
        reciprocal = Text("3/2", font_size=36, color=GREEN)
        reciprocal.next_to(equation1, RIGHT, buff=1)
        reciprocal_label = Text("Reciprocal", font_size=20, color=GREEN)
        reciprocal_label.next_to(reciprocal, DOWN)
        
        self.play(Write(reciprocal), Write(reciprocal_label))
        self.wait(2)

        # Clear and move to step 3
        self.play(FadeOut(step1_text), FadeOut(step2_text), FadeOut(fraction_highlight), 
                 FadeOut(reciprocal), FadeOut(reciprocal_label))
        self.play(equation1.animate.move_to(UP * 2))

        # Step 3: Show multiplication by reciprocal
        step3_text = Text("Step 3: Multiply both sides by 3/2", font_size=24, color=WHITE)
        step3_text.move_to(UP * 1)
        self.play(Write(step3_text))

        equation2 = Text("(3/2) × (2/3)x = (3/2) × 18", font_size=42)
        equation2.move_to(ORIGIN)
        self.play(Write(equation2))
        self.wait(2)

        # Step 4: Show reciprocal cancellation
        step4_text = Text("Step 4: The fractions multiply to 1", font_size=24, color=WHITE)
        step4_text.move_to(DOWN * 1)
        self.play(Write(step4_text))

        # Highlight the reciprocal multiplication
        left_fractions = SurroundingRectangle(equation2[:12], color=YELLOW, buff=0.1)
        self.play(Create(left_fractions))

        # Show the cancellation
        cancel_eq = Text("(3/2) × (2/3) = (3×2)/(2×3) = 6/6 = 1", font_size=32, color=GREEN)
        cancel_eq.move_to(DOWN * 2)
        self.play(Write(cancel_eq))
        self.wait(3)

        # Clear and show simplified left side
        self.play(FadeOut(step3_text), FadeOut(step4_text), FadeOut(left_fractions), FadeOut(cancel_eq))

        equation3 = Text("1 × x = (3/2) × 18", font_size=42)
        equation3.move_to(ORIGIN)
        self.play(ReplacementTransform(equation2, equation3))
        self.wait(1)

        equation4 = Text("x = (3/2) × 18", font_size=42)
        equation4.move_to(ORIGIN)
        self.play(ReplacementTransform(equation3, equation4))
        self.wait(2)

        # Step 5: Calculate right side
        step5_text = Text("Step 5: Calculate the right side", font_size=24, color=WHITE)
        step5_text.move_to(DOWN * 1)
        self.play(Write(step5_text))

        calculation = Text("(3/2) × 18 = (3×18)/2 = 54/2 = 27", font_size=32, color=GREEN)
        calculation.move_to(DOWN * 2)
        self.play(Write(calculation))
        self.wait(3)

        # Step 6: Final result
        self.play(FadeOut(step5_text), FadeOut(calculation))
        
        step6_text = Text("Step 6: Final Answer", font_size=24, color=WHITE)
        step6_text.move_to(DOWN * 1)
        self.play(Write(step6_text))

        final_equation = Text("x = 27", font_size=48, color=GREEN)
        final_equation.move_to(DOWN * 2)
        self.play(ReplacementTransform(equation4, final_equation))
        
        # Highlight the answer
        answer_box = SurroundingRectangle(final_equation, color=GREEN, buff=0.2)
        self.play(Create(answer_box))
        self.wait(2)

        # Summary
        summary = Text("Key Takeaway: Multiply by the reciprocal to eliminate fraction coefficients", 
                      font_size=20, color=YELLOW)
        summary.move_to(DOWN * 3.5)
        self.play(Write(summary))
        self.wait(3)