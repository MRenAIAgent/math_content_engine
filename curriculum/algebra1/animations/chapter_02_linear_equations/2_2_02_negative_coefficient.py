# Solving equations with negative coefficients
# Generated for Chapter 2 - Section 2.2

from manim import *

class SolvingNegativeCoefficientScene(Scene):
    def construct(self):
        # Title
        title = Text("Solving Equations with Negative Coefficients", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Step 1: Show initial equation
        step1_text = Text("Step 1: Start with the equation", font_size=24).to_edge(LEFT).shift(UP*2)
        equation1 = Text("-12p = 48", font_size=48).next_to(step1_text, DOWN, buff=0.5)
        
        self.play(Write(step1_text))
        self.play(Write(equation1))
        self.wait(2)

        # Step 2: Divide both sides by -12
        step2_text = Text("Step 2: Divide both sides by -12", font_size=24).next_to(step1_text, DOWN, buff=2)
        
        self.play(Write(step2_text))
        self.wait(1)

        # Step 3: Show division process
        step3_text = Text("Step 3: Apply division to both sides", font_size=24).next_to(step2_text, DOWN, buff=1.5)
        division_eq = Text("(-12p)/(-12) = 48/(-12)", font_size=40).next_to(step3_text, DOWN, buff=0.5)
        
        self.play(Write(step3_text))
        self.play(Write(division_eq))
        self.wait(2)

        # Highlight the negative signs
        self.play(Indicate(division_eq, color=RED))
        self.wait(1)

        # Step 4: Show result
        step4_text = Text("Step 4: Simplify", font_size=24).next_to(division_eq, DOWN, buff=1.5)
        result_eq = Text("p = -4", font_size=48, color=BLUE).next_to(step4_text, DOWN, buff=0.5)
        
        self.play(Write(step4_text))
        self.play(Write(result_eq))
        self.wait(2)

        # Key insight box
        insight_box = Rectangle(width=8, height=1.5, color=YELLOW).shift(DOWN*2)
        insight_text = Text("Key Insight: Negative ÷ Negative = Positive", font_size=20, color=BLACK).move_to(insight_box)
        insight_detail = Text("48 ÷ (-12) = -4", font_size=18, color=BLACK).next_to(insight_text, DOWN, buff=0.2)
        
        self.play(Create(insight_box))
        self.play(Write(insight_text))
        self.play(Write(insight_detail))
        self.wait(2)

        # Clear for verification
        self.play(
            FadeOut(step1_text), FadeOut(equation1),
            FadeOut(step2_text), FadeOut(step3_text), 
            FadeOut(division_eq), FadeOut(step4_text),
            FadeOut(insight_box), FadeOut(insight_text), FadeOut(insight_detail)
        )
        
        # Step 5: Verification
        verify_title = Text("Step 5: Verify the solution", font_size=28).shift(UP*2)
        verify_eq = Text("-12(-4) = 48", font_size=40).next_to(verify_title, DOWN, buff=1)
        
        self.play(Write(verify_title))
        self.play(Write(verify_eq))
        self.wait(1)

        # Show multiplication step by step
        mult_step = Text("(-12) × (-4) = +48", font_size=36).next_to(verify_eq, DOWN, buff=1)
        mult_step.set_color(RED)
        
        self.play(Write(mult_step))
        self.wait(1)

        # Final verification
        check_mark = Text("48 = 48 ✓", font_size=36, color=GREEN).next_to(mult_step, DOWN, buff=1)
        self.play(Write(check_mark))
        self.wait(2)

        # Move result to center and emphasize
        self.play(
            FadeOut(verify_title), FadeOut(verify_eq), 
            FadeOut(mult_step), FadeOut(check_mark)
        )
        
        final_result = Text("p = -4", font_size=60, color=BLUE).move_to(ORIGIN)
        self.play(ReplacementTransform(result_eq, final_result))
        
        # Summary
        summary = Text("Remember: When dividing by a negative number,", font_size=20).shift(DOWN*2)
        summary2 = Text("the sign of the quotient changes!", font_size=20, color=RED).next_to(summary, DOWN, buff=0.3)
        
        self.play(Write(summary))
        self.play(Write(summary2))
        self.wait(3)