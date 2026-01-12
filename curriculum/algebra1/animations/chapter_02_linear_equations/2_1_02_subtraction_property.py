# Subtraction Property of Equality for solving equations
# Generated for Chapter 2 - Section 2.1

from manim import *

class SubtractionPropertyEqualityScene(Scene):
    def construct(self):
        # Title
        title = Text("Subtraction Property of Equality", font_size=36, color=BLUE)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Step 1: Show the equation
        step1_text = Text("Step 1: Start with the equation", font_size=24, color=WHITE)
        step1_text.next_to(title, DOWN, buff=0.5)
        self.play(Write(step1_text))
        
        equation1 = Text("y + 37 = -13", font_size=32, color=YELLOW)
        equation1.next_to(step1_text, DOWN, buff=0.5)
        self.play(Write(equation1))
        self.wait(2)

        # Balance scale visual
        scale_base = Rectangle(width=0.5, height=0.1, color=WHITE, fill_opacity=1)
        scale_base.move_to(DOWN * 1.5)
        
        left_plate = Rectangle(width=2, height=0.1, color=WHITE, fill_opacity=1)
        left_plate.move_to(LEFT * 2 + DOWN * 1.5)
        
        right_plate = Rectangle(width=2, height=0.1, color=WHITE, fill_opacity=1)
        right_plate.move_to(RIGHT * 2 + DOWN * 1.5)
        
        left_support = Line(scale_base.get_center(), left_plate.get_center(), color=WHITE)
        right_support = Line(scale_base.get_center(), right_plate.get_center(), color=WHITE)
        
        scale = VGroup(scale_base, left_plate, right_plate, left_support, right_support)
        self.play(Create(scale))
        
        # Add equation parts to scale
        left_side = Text("y + 37", font_size=24, color=GREEN)
        left_side.next_to(left_plate, UP, buff=0.2)
        
        right_side = Text("-13", font_size=24, color=GREEN)
        right_side.next_to(right_plate, UP, buff=0.2)
        
        self.play(Write(left_side), Write(right_side))
        self.wait(2)

        # Step 2: Explain the strategy
        self.play(FadeOut(step1_text))
        step2_text = Text("Step 2: Subtract 37 from both sides to isolate y", font_size=24, color=WHITE)
        step2_text.next_to(title, DOWN, buff=0.5)
        self.play(Write(step2_text))
        self.wait(2)

        # Step 3: Show subtraction on both sides
        self.play(FadeOut(step2_text))
        step3_text = Text("Step 3: Apply subtraction property", font_size=24, color=WHITE)
        step3_text.next_to(title, DOWN, buff=0.5)
        self.play(Write(step3_text))

        # Transform equation to show subtraction
        equation2 = Text("y + 37 - 37 = -13 - 37", font_size=28, color=YELLOW)
        equation2.next_to(step3_text, DOWN, buff=0.5)
        self.play(ReplacementTransform(equation1, equation2))
        
        # Highlight the -37 in red on both sides
        minus_37_left = Text("- 37", font_size=24, color=RED)
        minus_37_left.next_to(left_plate, DOWN, buff=0.2)
        
        minus_37_right = Text("- 37", font_size=24, color=RED)
        minus_37_right.next_to(right_plate, DOWN, buff=0.2)
        
        self.play(Write(minus_37_left), Write(minus_37_right))
        self.wait(2)

        # Step 4: Simplify
        self.play(FadeOut(step3_text))
        step4_text = Text("Step 4: Simplify both sides", font_size=24, color=WHITE)
        step4_text.next_to(title, DOWN, buff=0.5)
        self.play(Write(step4_text))

        equation3 = Text("y = -50", font_size=32, color=YELLOW)
        equation3.next_to(step4_text, DOWN, buff=0.5)
        self.play(ReplacementTransform(equation2, equation3))
        
        # Update scale
        new_left = Text("y", font_size=24, color=GREEN)
        new_left.next_to(left_plate, UP, buff=0.2)
        
        new_right = Text("-50", font_size=24, color=GREEN)
        new_right.next_to(right_plate, UP, buff=0.2)
        
        self.play(
            ReplacementTransform(left_side, new_left),
            ReplacementTransform(right_side, new_right),
            FadeOut(minus_37_left),
            FadeOut(minus_37_right)
        )
        self.wait(2)

        # Step 5: Verification
        self.play(FadeOut(step4_text))
        step5_text = Text("Step 5: Verify by substituting back", font_size=24, color=WHITE)
        step5_text.next_to(title, DOWN, buff=0.5)
        self.play(Write(step5_text))

        verify_eq = Text("(-50) + 37 = -13", font_size=28, color=ORANGE)
        verify_eq.next_to(step5_text, DOWN, buff=0.5)
        self.play(Write(verify_eq))
        
        verify_result = Text("-13 = -13 ✓", font_size=28, color=GREEN)
        verify_result.next_to(verify_eq, DOWN, buff=0.3)
        self.play(Write(verify_result))
        self.wait(2)

        # Key takeaway
        self.play(
            FadeOut(step5_text),
            FadeOut(verify_eq),
            FadeOut(verify_result),
            FadeOut(scale),
            FadeOut(new_left),
            FadeOut(new_right)
        )
        
        takeaway_title = Text("Key Takeaway:", font_size=28, color=BLUE)
        takeaway_title.next_to(title, DOWN, buff=0.8)
        
        takeaway_text = Text(
            "The Subtraction Property of Equality states:\nWhatever you subtract from one side of an equation,\nyou must subtract from the other side to keep it balanced.",
            font_size=20,
            color=WHITE
        )
        takeaway_text.next_to(takeaway_title, DOWN, buff=0.5)
        
        final_solution = Text("Solution: y = -50", font_size=32, color=YELLOW)
        final_solution.next_to(takeaway_text, DOWN, buff=0.8)
        
        self.play(Write(takeaway_title))
        self.play(Write(takeaway_text))
        self.play(Write(final_solution))
        self.play(ReplacementTransform(equation3, final_solution))
        
        self.wait(3)