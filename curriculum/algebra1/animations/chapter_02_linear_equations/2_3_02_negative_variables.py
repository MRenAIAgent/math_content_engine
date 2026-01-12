# Solving with negative variable terms
# Generated for Chapter 2 - Section 2.3

from manim import *

class SolvingNegativeVariableTermsScene(Scene):
    def construct(self):
        # Title
        title = Text("Solving Equations with Negative Variable Terms", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Step 1: Show the equation
        step1_text = Text("Step 1: Start with the equation", font_size=24).to_edge(LEFT).shift(UP*2.5)
        equation1 = Text("12 - 5y = 2y - 9", font_size=32).next_to(step1_text, DOWN, buff=0.5)
        
        self.play(Write(step1_text))
        self.play(Write(equation1))
        self.wait(2)

        # Step 2: Collect y terms
        step2_text = Text("Step 2: Collect y terms - subtract 2y from both sides", font_size=24).next_to(step1_text, DOWN, buff=2)
        equation2a = Text("12 - 5y - 2y = 2y - 9 - 2y", font_size=28).next_to(step2_text, DOWN, buff=0.5)
        
        self.play(Write(step2_text))
        self.play(ReplacementTransform(equation1.copy(), equation2a))
        self.wait(1)

        # Highlight the terms being combined
        highlight_left = SurroundingRectangle(Text("-5y - 2y", font_size=28).move_to(equation2a).shift(LEFT*1.2), color=YELLOW)
        highlight_right = SurroundingRectangle(Text("2y - 2y", font_size=28).move_to(equation2a).shift(RIGHT*1.8), color=YELLOW)
        
        self.play(Create(highlight_left), Create(highlight_right))
        self.wait(1)
        self.play(FadeOut(highlight_left), FadeOut(highlight_right))

        # Step 3: Simplified equation
        step3_text = Text("Step 3: Simplify", font_size=24).next_to(step2_text, DOWN, buff=1.5)
        equation3 = Text("12 - 7y = -9", font_size=32).next_to(step3_text, DOWN, buff=0.5)
        
        self.play(Write(step3_text))
        self.play(ReplacementTransform(equation2a, equation3))
        self.wait(2)

        # Step 4: Collect constants
        step4_text = Text("Step 4: Collect constants - subtract 12 from both sides", font_size=24).next_to(step3_text, DOWN, buff=1.5)
        equation4a = Text("12 - 7y - 12 = -9 - 12", font_size=28).next_to(step4_text, DOWN, buff=0.5)
        
        self.play(Write(step4_text))
        self.play(ReplacementTransform(equation3.copy(), equation4a))
        self.wait(1)

        # Highlight constants being combined
        highlight_const = SurroundingRectangle(Text("12 - 12", font_size=28).move_to(equation4a).shift(LEFT*1.5), color=GREEN)
        self.play(Create(highlight_const))
        self.wait(1)
        self.play(FadeOut(highlight_const))

        # Step 5: Simplified equation
        step5_text = Text("Step 5: Simplify", font_size=24).next_to(step4_text, DOWN, buff=1.5)
        equation5 = Text("-7y = -21", font_size=32).next_to(step5_text, DOWN, buff=0.5)
        
        self.play(Write(step5_text))
        self.play(ReplacementTransform(equation4a, equation5))
        self.wait(2)

        # Clear screen for final steps
        self.play(
            FadeOut(step1_text), FadeOut(step2_text), FadeOut(step3_text), 
            FadeOut(step4_text), FadeOut(step5_text)
        )

        # Move equation to center
        self.play(equation5.animate.move_to(ORIGIN).shift(UP*1))

        # Step 6: Divide by -7
        step6_text = Text("Step 6: Divide both sides by -7", font_size=28).next_to(equation5, DOWN, buff=1)
        division_step = Text("y = -21 ÷ (-7)", font_size=28).next_to(step6_text, DOWN, buff=0.5)
        final_answer = Text("y = 3", font_size=36, color=GREEN).next_to(division_step, DOWN, buff=0.5)
        
        self.play(Write(step6_text))
        self.play(Write(division_step))
        self.wait(1)
        self.play(Write(final_answer))
        self.play(Circumscribe(final_answer, color=GREEN))
        self.wait(2)

        # Step 7: Verification
        self.play(FadeOut(equation5), FadeOut(step6_text), FadeOut(division_step))
        
        verify_text = Text("Step 7: Verify the solution", font_size=28).to_edge(UP).shift(DOWN*0.5)
        original_eq = Text("12 - 5y = 2y - 9", font_size=24).next_to(verify_text, DOWN, buff=1)
        substitute = Text("Substitute y = 3:", font_size=24).next_to(original_eq, DOWN, buff=0.5)
        left_side = Text("12 - 5(3) = 12 - 15 = -3", font_size=24).next_to(substitute, DOWN, buff=0.5)
        right_side = Text("2(3) - 9 = 6 - 9 = -3", font_size=24).next_to(left_side, DOWN, buff=0.3)
        check_mark = Text("✓ Both sides equal -3", font_size=24, color=GREEN).next_to(right_side, DOWN, buff=0.5)
        
        self.play(final_answer.animate.to_edge(RIGHT))
        self.play(Write(verify_text))
        self.play(Write(original_eq))
        self.play(Write(substitute))
        self.play(Write(left_side))
        self.play(Write(right_side))
        self.play(Write(check_mark))
        self.wait(2)

        # Strategy summary
        self.play(FadeOut(VGroup(verify_text, original_eq, substitute, left_side, right_side, check_mark, final_answer)))
        
        strategy_title = Text("Key Strategy:", font_size=32, color=BLUE).to_edge(UP).shift(DOWN*0.5)
        strategy1 = Text("1. Gather all variable terms on one side", font_size=24).next_to(strategy_title, DOWN, buff=1)
        strategy2 = Text("2. Gather all constant terms on the other side", font_size=24).next_to(strategy1, DOWN, buff=0.5)
        strategy3 = Text("3. Divide by the coefficient of the variable", font_size=24).next_to(strategy2, DOWN, buff=0.5)
        strategy4 = Text("4. Always verify your solution!", font_size=24, color=YELLOW).next_to(strategy3, DOWN, buff=0.5)
        
        self.play(Write(strategy_title))
        self.play(Write(strategy1))
        self.play(Write(strategy2))
        self.play(Write(strategy3))
        self.play(Write(strategy4))
        self.wait(3)