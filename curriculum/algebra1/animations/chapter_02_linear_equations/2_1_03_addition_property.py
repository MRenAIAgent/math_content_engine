# Addition Property of Equality for solving equations
# Generated for Chapter 2 - Section 2.1

from manim import *

class AdditionPropertyEqualityScene(Scene):
    def construct(self):
        # Title
        title = Text("Addition Property of Equality", font_size=48, color=BLUE)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Step 1: Show the equation
        step1_text = Text("Step 1: Given equation", font_size=32, color=WHITE)
        step1_text.move_to(UP * 2.5)
        equation1 = Text("a - 28 = -37", font_size=40, color=YELLOW)
        equation1.move_to(UP * 1.5)
        
        self.play(Write(step1_text))
        self.play(Write(equation1))
        self.wait(2)

        # Create balance scale
        scale_base = Rectangle(width=0.3, height=0.1, color=WHITE).move_to(DOWN * 0.5)
        scale_beam = Rectangle(width=4, height=0.05, color=WHITE).move_to(DOWN * 0.3)
        left_pan = Circle(radius=0.3, color=WHITE).move_to(LEFT * 1.5 + DOWN * 0.1)
        right_pan = Circle(radius=0.3, color=WHITE).move_to(RIGHT * 1.5 + DOWN * 0.1)
        
        left_content = Text("a - 28", font_size=24).move_to(LEFT * 1.5 + DOWN * 0.1)
        right_content = Text("-37", font_size=24).move_to(RIGHT * 1.5 + DOWN * 0.1)
        
        scale_group = VGroup(scale_base, scale_beam, left_pan, right_pan, left_content, right_content)
        
        self.play(Create(scale_group))
        self.wait(2)

        # Step 2: Explain addition property
        self.play(FadeOut(step1_text))
        step2_text = Text("Step 2: Add 28 to both sides to isolate a", font_size=28, color=WHITE)
        step2_text.move_to(UP * 2.5)
        self.play(Write(step2_text))
        self.wait(2)

        # Step 3: Show adding 28 to both sides
        self.play(FadeOut(step2_text))
        step3_text = Text("Step 3: Apply addition property", font_size=32, color=WHITE)
        step3_text.move_to(UP * 2.5)
        
        equation2 = Text("a - 28 + 28 = -37 + 28", font_size=36, color=YELLOW)
        equation2.move_to(UP * 1.5)
        
        # Highlight the +28 in green
        plus28_left = Text("+28", font_size=36, color=GREEN).move_to(UP * 1.5 + LEFT * 0.8)
        plus28_right = Text("+28", font_size=36, color=GREEN).move_to(UP * 1.5 + RIGHT * 0.8)
        
        self.play(Write(step3_text))
        self.play(Transform(equation1, equation2))
        self.play(Write(plus28_left), Write(plus28_right))
        self.wait(2)

        # Update balance scale
        new_left_content = Text("a - 28 + 28", font_size=20).move_to(LEFT * 1.5 + DOWN * 0.1)
        new_right_content = Text("-37 + 28", font_size=20).move_to(RIGHT * 1.5 + DOWN * 0.1)
        
        green_28_left = Text("+28", font_size=20, color=GREEN).move_to(LEFT * 1.5 + DOWN * 0.4)
        green_28_right = Text("+28", font_size=20, color=GREEN).move_to(RIGHT * 1.5 + DOWN * 0.4)
        
        self.play(
            Transform(left_content, new_left_content),
            Transform(right_content, new_right_content)
        )
        self.play(Write(green_28_left), Write(green_28_right))
        self.wait(2)

        # Step 4: Simplify
        self.play(FadeOut(step3_text), FadeOut(plus28_left), FadeOut(plus28_right))
        step4_text = Text("Step 4: Simplify both sides", font_size=32, color=WHITE)
        step4_text.move_to(UP * 2.5)
        
        equation3 = Text("a = -9", font_size=40, color=YELLOW)
        equation3.move_to(UP * 1.5)
        
        self.play(Write(step4_text))
        self.play(Transform(equation1, equation3))
        self.wait(1)

        # Update balance scale to show final result
        final_left_content = Text("a", font_size=24).move_to(LEFT * 1.5 + DOWN * 0.1)
        final_right_content = Text("-9", font_size=24).move_to(RIGHT * 1.5 + DOWN * 0.1)
        
        self.play(
            Transform(left_content, final_left_content),
            Transform(right_content, final_right_content),
            FadeOut(green_28_left), FadeOut(green_28_right)
        )
        self.wait(2)

        # Step 5: Verify the solution
        self.play(FadeOut(step4_text))
        step5_text = Text("Step 5: Verify by substituting a = -9", font_size=28, color=WHITE)
        step5_text.move_to(UP * 2.5)
        
        verification = Text("(-9) - 28 = -37 ✓", font_size=36, color=GREEN)
        verification.move_to(UP * 1.5)
        
        self.play(Write(step5_text))
        self.play(Transform(equation1, verification))
        self.wait(2)

        # Key takeaway
        self.play(FadeOut(step5_text), FadeOut(scale_group))
        takeaway = Text("Key Point: Whatever you do to one side,\nyou must do to the other side!", 
                       font_size=32, color=BLUE)
        takeaway.move_to(DOWN * 1)
        
        self.play(Write(takeaway))
        self.wait(3)