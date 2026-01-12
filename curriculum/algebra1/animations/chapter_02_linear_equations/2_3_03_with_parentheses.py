# Solving equations with parentheses using distributive property
# Generated for Chapter 2 - Section 2.3

from manim import *

class DistributivePropertyScene(Scene):
    def construct(self):
        # Title
        title = Text("Solving Equations with Distributive Property", font_size=36, color=BLUE)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Step 1: Show original equation
        step1_text = Text("Step 1: Original equation", font_size=24, color=YELLOW).to_edge(LEFT).shift(UP*2.5)
        equation1 = Text("3(2x - 5) = 4x + 7", font_size=32).next_to(step1_text, DOWN, buff=0.5)
        
        self.play(Write(step1_text))
        self.play(Write(equation1))
        self.wait(2)

        # Step 2: Distribute the 3
        step2_text = Text("Step 2: Distribute the 3", font_size=24, color=YELLOW).next_to(step1_text, DOWN, buff=2)
        
        # Show distribution with arrows and colors
        left_side = Text("3(2x - 5)", font_size=32, color=WHITE)
        arrow1 = Arrow(start=ORIGIN, end=DOWN*0.8, color=RED, stroke_width=3)
        arrow2 = Arrow(start=ORIGIN, end=DOWN*0.8, color=GREEN, stroke_width=3)
        
        term1 = Text("3 × 2x", font_size=24, color=RED)
        term2 = Text("3 × (-5)", font_size=24, color=GREEN)
        
        left_side.move_to(LEFT*3 + UP*0.5)
        arrow1.next_to(left_side, DOWN, buff=0.3).shift(LEFT*0.8)
        arrow2.next_to(left_side, DOWN, buff=0.3).shift(RIGHT*0.8)
        term1.next_to(arrow1, DOWN, buff=0.2)
        term2.next_to(arrow2, DOWN, buff=0.2)
        
        self.play(Write(step2_text))
        self.play(Write(left_side))
        self.play(Create(arrow1), Create(arrow2))
        self.play(Write(term1), Write(term2))
        self.wait(1)
        
        result1 = Text("6x", font_size=24, color=RED)
        result2 = Text("-15", font_size=24, color=GREEN)
        result1.move_to(term1.get_center())
        result2.move_to(term2.get_center())
        
        self.play(Transform(term1, result1), Transform(term2, result2))
        self.wait(1)
        
        equation2 = Text("6x - 15 = 4x + 7", font_size=32).next_to(step2_text, DOWN, buff=1.5)
        self.play(Write(equation2))
        self.wait(2)
        
        # Clear distribution visualization
        self.play(FadeOut(left_side), FadeOut(arrow1), FadeOut(arrow2), FadeOut(term1), FadeOut(term2))

        # Step 3: Subtract 4x
        step3_text = Text("Step 3: Subtract 4x from both sides", font_size=24, color=YELLOW).next_to(step2_text, DOWN, buff=3)
        equation3 = Text("2x - 15 = 7", font_size=32, color=ORANGE).next_to(step3_text, DOWN, buff=0.5)
        
        self.play(Write(step3_text))
        self.play(Write(equation3))
        self.wait(2)

        # Step 4: Add 15
        step4_text = Text("Step 4: Add 15 to both sides", font_size=24, color=YELLOW).next_to(step3_text, DOWN, buff=2)
        equation4 = Text("2x = 22", font_size=32, color=PURPLE).next_to(step4_text, DOWN, buff=0.5)
        
        self.play(Write(step4_text))
        self.play(Write(equation4))
        self.wait(2)

        # Step 5: Divide by 2
        step5_text = Text("Step 5: Divide both sides by 2", font_size=24, color=YELLOW).next_to(step4_text, DOWN, buff=2)
        equation5 = Text("x = 11", font_size=36, color=GREEN).next_to(step5_text, DOWN, buff=0.5)
        
        self.play(Write(step5_text))
        self.play(Write(equation5))
        self.play(Circumscribe(equation5, color=GREEN, stroke_width=3))
        self.wait(2)

        # Clear previous content for verification
        self.play(FadeOut(step1_text), FadeOut(equation1), FadeOut(step2_text), FadeOut(equation2),
                  FadeOut(step3_text), FadeOut(equation3), FadeOut(step4_text), FadeOut(equation4),
                  FadeOut(step5_text))

        # Step 6: Verification
        verify_title = Text("Step 6: Verification", font_size=28, color=YELLOW).move_to(UP*2)
        verify_text = Text("Substitute x = 11 back into original equation:", font_size=20).next_to(verify_title, DOWN, buff=0.5)
        
        original = Text("3(2x - 5) = 4x + 7", font_size=24).next_to(verify_text, DOWN, buff=0.5)
        substitute = Text("3(2(11) - 5) = 4(11) + 7", font_size=24, color=BLUE).next_to(original, DOWN, buff=0.3)
        simplify1 = Text("3(22 - 5) = 44 + 7", font_size=24, color=ORANGE).next_to(substitute, DOWN, buff=0.3)
        simplify2 = Text("3(17) = 51", font_size=24, color=PURPLE).next_to(simplify1, DOWN, buff=0.3)
        final_check = Text("51 = 51 ✓", font_size=28, color=GREEN).next_to(simplify2, DOWN, buff=0.3)
        
        self.play(equation5.animate.move_to(UP*3 + RIGHT*4))
        self.play(Write(verify_title))
        self.play(Write(verify_text))
        self.play(Write(original))
        self.wait(1)
        self.play(Write(substitute))
        self.wait(1)
        self.play(Write(simplify1))
        self.wait(1)
        self.play(Write(simplify2))
        self.wait(1)
        self.play(Write(final_check))
        self.play(Circumscribe(final_check, color=GREEN, stroke_width=3))
        self.wait(2)

        # Summary
        summary = Text("Solution: x = 11", font_size=32, color=GREEN).move_to(DOWN*2.5)
        self.play(Write(summary))
        self.play(Indicate(summary, color=GREEN))
        self.wait(3)