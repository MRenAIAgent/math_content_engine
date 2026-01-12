# Verifying a solution to a linear equation
# Generated for Chapter 2 - Section 2.1

from manim import *

class VerifyLinearSolutionScene(Scene):
    def construct(self):
        # Title
        title = Text("Verifying a Solution to a Linear Equation", font_size=36, color=BLUE)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Problem statement
        problem = Text("Check if x = 5 is a solution to 6x - 17 = 13", font_size=28)
        problem.next_to(title, DOWN, buff=0.8)
        self.play(Write(problem))
        self.wait(2)

        # Step 1: Original equation
        step1_title = Text("Step 1: Write the original equation", font_size=24, color=YELLOW)
        step1_title.next_to(problem, DOWN, buff=1)
        self.play(Write(step1_title))
        
        equation1 = Text("6x - 17 = 13", font_size=32, color=WHITE)
        equation1.next_to(step1_title, DOWN, buff=0.5)
        self.play(Write(equation1))
        self.wait(2)

        # Step 2: Substitute x = 5
        step2_title = Text("Step 2: Substitute x = 5", font_size=24, color=YELLOW)
        step2_title.next_to(equation1, DOWN, buff=1)
        self.play(Write(step2_title))
        
        equation2 = Text("6(5) - 17 = 13", font_size=32, color=WHITE)
        equation2.next_to(step2_title, DOWN, buff=0.5)
        
        # Highlight the substitution
        x_highlight = SurroundingRectangle(equation1[0], color=RED, buff=0.1)
        five_highlight = SurroundingRectangle(equation2[2], color=RED, buff=0.1)
        
        self.play(Create(x_highlight))
        self.play(Transform(x_highlight, five_highlight), Write(equation2))
        self.play(FadeOut(x_highlight))
        self.wait(2)

        # Step 3: Calculate left side
        step3_title = Text("Step 3: Calculate the left side", font_size=24, color=YELLOW)
        step3_title.next_to(equation2, DOWN, buff=1)
        self.play(Write(step3_title))
        
        calc1 = Text("6(5) - 17", font_size=28, color=WHITE)
        calc1.next_to(step3_title, DOWN, buff=0.5)
        self.play(Write(calc1))
        
        arrow1 = Text("→", font_size=28, color=GREEN)
        arrow1.next_to(calc1, RIGHT, buff=0.3)
        
        calc2 = Text("30 - 17", font_size=28, color=WHITE)
        calc2.next_to(arrow1, RIGHT, buff=0.3)
        
        self.play(Write(arrow1), Write(calc2))
        
        arrow2 = Text("→", font_size=28, color=GREEN)
        arrow2.next_to(calc2, RIGHT, buff=0.3)
        
        calc3 = Text("13", font_size=28, color=GREEN)
        calc3.next_to(arrow2, RIGHT, buff=0.3)
        
        self.play(Write(arrow2), Write(calc3))
        self.wait(2)

        # Step 4: Compare with right side
        step4_title = Text("Step 4: Compare with right side", font_size=24, color=YELLOW)
        step4_title.next_to(calc1, DOWN, buff=1)
        self.play(Write(step4_title))
        
        comparison = Text("13 = 13", font_size=32, color=GREEN)
        comparison.next_to(step4_title, DOWN, buff=0.5)
        self.play(Write(comparison))
        
        # Add checkmark
        checkmark = Text("✓", font_size=48, color=GREEN)
        checkmark.next_to(comparison, RIGHT, buff=0.5)
        self.play(Write(checkmark))
        self.play(Indicate(checkmark, scale_factor=1.5))
        self.wait(2)

        # Step 5: Conclusion
        step5_title = Text("Step 5: Conclusion", font_size=24, color=YELLOW)
        step5_title.next_to(comparison, DOWN, buff=1)
        self.play(Write(step5_title))
        
        conclusion = Text("x = 5 IS a solution!", font_size=28, color=GREEN)
        conclusion.next_to(step5_title, DOWN, buff=0.5)
        self.play(Write(conclusion))
        
        # Final highlight
        final_box = SurroundingRectangle(conclusion, color=GREEN, buff=0.3)
        self.play(Create(final_box))
        self.play(Indicate(conclusion, scale_factor=1.2))
        
        self.wait(3)