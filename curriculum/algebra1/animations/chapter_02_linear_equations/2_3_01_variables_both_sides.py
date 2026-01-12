# Solving equations with variables on both sides
# Generated for Chapter 2 - Section 2.3

from manim import *

class SolvingEquationsScene(Scene):
    def construct(self):
        # Title
        title = Text("Solving Equations with Variables on Both Sides", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Step 1: Show initial equation
        step1_text = Text("Step 1: Start with the equation", font_size=24).next_to(title, DOWN, buff=0.5)
        equation1 = Text("5x + 8 = 3x + 14", font_size=32)
        equation1.next_to(step1_text, DOWN, buff=0.8)
        
        self.play(Write(step1_text))
        self.play(Write(equation1))
        self.wait(2)

        # Step 2: Subtract 3x from both sides
        step2_text = Text("Step 2: Subtract 3x from both sides", font_size=24)
        step2_text.next_to(equation1, DOWN, buff=1)
        self.play(Write(step2_text))
        
        # Show the operation
        subtract_3x = Text("-3x        -3x", font_size=24, color=RED)
        subtract_3x.next_to(step2_text, DOWN, buff=0.3)
        
        self.play(Write(subtract_3x))
        self.wait(1)

        # Step 3: Show result
        step3_text = Text("Step 3: Simplify", font_size=24)
        equation2 = Text("2x + 8 = 14", font_size=32, color=BLUE)
        
        # Position step 3
        step3_text.next_to(subtract_3x, DOWN, buff=0.8)
        equation2.next_to(step3_text, DOWN, buff=0.5)
        
        self.play(Write(step3_text))
        self.play(Write(equation2))
        self.wait(2)

        # Clear previous work
        self.play(FadeOut(step1_text), FadeOut(equation1), FadeOut(step2_text), 
                 FadeOut(subtract_3x), FadeOut(step3_text))
        self.play(equation2.animate.move_to(ORIGIN + UP))

        # Step 4: Subtract 8 from both sides
        step4_text = Text("Step 4: Subtract 8 from both sides", font_size=24)
        step4_text.next_to(equation2, DOWN, buff=1)
        self.play(Write(step4_text))
        
        subtract_8 = Text("-8        -8", font_size=24, color=RED)
        subtract_8.next_to(step4_text, DOWN, buff=0.3)
        
        self.play(Write(subtract_8))
        self.wait(1)

        # Step 5: Show result
        step5_text = Text("Step 5: Simplify", font_size=24)
        equation3 = Text("2x = 6", font_size=32, color=BLUE)
        
        step5_text.next_to(subtract_8, DOWN, buff=0.8)
        equation3.next_to(step5_text, DOWN, buff=0.5)
        
        self.play(Write(step5_text))
        self.play(Write(equation3))
        self.wait(2)

        # Clear previous work
        self.play(FadeOut(step4_text), FadeOut(subtract_8), FadeOut(step5_text))
        self.play(equation3.animate.move_to(ORIGIN))

        # Step 6: Divide by 2
        step6_text = Text("Step 6: Divide both sides by 2", font_size=24)
        step6_text.next_to(equation3, DOWN, buff=1)
        self.play(Write(step6_text))
        
        divide_2 = Text("÷2      ÷2", font_size=24, color=RED)
        divide_2.next_to(step6_text, DOWN, buff=0.3)
        
        self.play(Write(divide_2))
        self.wait(1)

        # Final answer
        final_text = Text("Final Answer:", font_size=24, color=GREEN)
        final_equation = Text("x = 3", font_size=48, color=GREEN)
        
        final_text.next_to(divide_2, DOWN, buff=0.8)
        final_equation.next_to(final_text, DOWN, buff=0.5)
        
        self.play(Write(final_text))
        self.play(Write(final_equation))
        self.wait(2)

        # Clear for verification
        self.play(FadeOut(equation2), FadeOut(equation3), FadeOut(step6_text), 
                 FadeOut(divide_2), FadeOut(final_text))
        self.play(final_equation.animate.move_to(ORIGIN + UP * 2))

        # Step 7: Verification
        verify_text = Text("Step 7: Verify the solution", font_size=24, color=YELLOW)
        verify_text.next_to(final_equation, DOWN, buff=1)
        self.play(Write(verify_text))

        # Show verification
        verify_eq = Text("5(3) + 8 = 3(3) + 14", font_size=28)
        verify_eq.next_to(verify_text, DOWN, buff=0.5)
        
        self.play(Write(verify_eq))
        self.wait(1)

        # Show calculation
        calc_eq = Text("15 + 8 = 9 + 14", font_size=28)
        calc_eq.next_to(verify_eq, DOWN, buff=0.5)
        self.play(Write(calc_eq))
        self.wait(1)

        # Final verification
        final_verify = Text("23 = 23 ✓", font_size=32, color=GREEN)
        final_verify.next_to(calc_eq, DOWN, buff=0.5)
        
        self.play(Write(final_verify))
        self.play(Indicate(final_verify))
        self.wait(2)

        # Summary
        summary = Text("Solution verified! x = 3", font_size=28, color=GREEN)
        summary.to_edge(DOWN)
        self.play(Write(summary))
        self.wait(3)