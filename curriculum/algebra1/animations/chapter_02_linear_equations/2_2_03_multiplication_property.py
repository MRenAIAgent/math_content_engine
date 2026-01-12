# Multiplication Property of Equality
# Generated for Chapter 2 - Section 2.2

from manim import *

class MultiplicationPropertyEqualityScene(Scene):
    def construct(self):
        # Title
        title = Text("Multiplication Property of Equality", font_size=36, color=BLUE)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Step 1: Show initial equation
        step1_text = Text("Step 1: Start with the equation", font_size=24, color=WHITE)
        step1_text.next_to(title, DOWN, buff=0.8)
        self.play(Write(step1_text))
        
        equation1 = Text("n/6 = 15", font_size=32, color=YELLOW)
        equation1.next_to(step1_text, DOWN, buff=0.5)
        self.play(Write(equation1))
        self.wait(2)

        # Step 2: Explain multiplication property
        step2_text = Text("Step 2: Multiply both sides by 6", font_size=24, color=WHITE)
        step2_text.next_to(equation1, DOWN, buff=0.8)
        self.play(Write(step2_text))
        
        explanation = Text("(To isolate n, we need to cancel the division by 6)", font_size=18, color=GRAY)
        explanation.next_to(step2_text, DOWN, buff=0.3)
        self.play(Write(explanation))
        self.wait(2)

        # Step 3: Show multiplication on both sides
        step3_text = Text("Step 3: Apply multiplication to both sides", font_size=24, color=WHITE)
        step3_text.next_to(explanation, DOWN, buff=0.8)
        self.play(Write(step3_text))
        
        # Create visual representation
        left_side = Text("6 × (n/6)", font_size=28, color=GREEN)
        equals = Text("=", font_size=28, color=WHITE)
        right_side = Text("6 × 15", font_size=28, color=GREEN)
        
        equation2 = VGroup(left_side, equals, right_side).arrange(RIGHT, buff=0.5)
        equation2.next_to(step3_text, DOWN, buff=0.5)
        
        self.play(Write(equation2))
        
        # Highlight the 6's being multiplied
        six_left = Text("6", font_size=28, color=RED)
        six_left.move_to(left_side.get_left() + RIGHT * 0.15)
        six_right = Text("6", font_size=28, color=RED)
        six_right.move_to(right_side.get_left() + RIGHT * 0.15)
        
        self.play(
            Indicate(six_left, color=RED),
            Indicate(six_right, color=RED)
        )
        self.wait(2)

        # Step 4: Show cancellation
        step4_text = Text("Step 4: The 6's cancel on the left side", font_size=24, color=WHITE)
        step4_text.next_to(equation2, DOWN, buff=0.8)
        self.play(Write(step4_text))
        
        # Show cancellation with strikethrough effect
        cancel_line1 = Line(
            left_side.get_corner(UL) + LEFT * 0.1,
            left_side.get_corner(DR) + RIGHT * 0.1,
            color=RED, stroke_width=3
        )
        
        self.play(Create(cancel_line1))
        
        # Show simplified equation
        simplified_left = Text("n", font_size=28, color=YELLOW)
        simplified_equals = Text("=", font_size=28, color=WHITE)
        simplified_right = Text("90", font_size=28, color=YELLOW)
        
        equation3 = VGroup(simplified_left, simplified_equals, simplified_right).arrange(RIGHT, buff=0.5)
        equation3.next_to(step4_text, DOWN, buff=0.5)
        
        self.play(Write(equation3))
        
        # Show the calculation 6 × 15 = 90
        calculation = Text("6 × 15 = 90", font_size=20, color=GRAY)
        calculation.next_to(equation3, RIGHT, buff=1)
        self.play(Write(calculation))
        self.wait(2)

        # Step 5: Verification
        step5_text = Text("Step 5: Verify the solution", font_size=24, color=WHITE)
        step5_text.next_to(equation3, DOWN, buff=0.8)
        self.play(Write(step5_text))
        
        verification = Text("90/6 = 15 ✓", font_size=28, color=GREEN)
        verification.next_to(step5_text, DOWN, buff=0.5)
        self.play(Write(verification))
        
        checkmark = Text("✓", font_size=40, color=GREEN)
        checkmark.next_to(verification, RIGHT, buff=0.3)
        self.play(Write(checkmark))
        self.wait(2)

        # Summary
        summary_box = Rectangle(width=10, height=1.5, color=BLUE, fill_opacity=0.1)
        summary_text = Text(
            "Key Point: When we multiply both sides of an equation by the same number,\nthe equation remains balanced and true.",
            font_size=20,
            color=WHITE
        )
        
        summary_group = VGroup(summary_box, summary_text)
        summary_group.next_to(verification, DOWN, buff=1)
        
        self.play(
            Create(summary_box),
            Write(summary_text)
        )
        self.wait(3)