# Subtraction Property of Equality for solving equations - Basketball & NBA Edition
# Section 2.1

from manim import *

class SubtractionPropertyBasketballScene(Scene):
    def construct(self):
        # Title
        title = Text("Subtraction Property of Equality", font_size=36, color=ORANGE)
        subtitle = Text("Solving Basketball Equations", font_size=24, color=BLUE)
        self.play(Write(title))
        self.wait(0.5)
        self.play(Write(subtitle.next_to(title, DOWN)))
        self.play(title.animate.to_edge(UP), subtitle.animate.to_edge(UP).shift(DOWN*0.5))
        
        # Basketball context setup
        context = Text("Stephen Curry's total points in a game:", font_size=28, color=WHITE)
        context.move_to(UP*2.5)
        self.play(Write(context))
        self.wait(1)
        
        # Initial equation
        equation_text = Text("Points from free throws + 37 points from 3-pointers = -13", font_size=20)
        equation_text.next_to(context, DOWN, buff=0.5)
        self.play(Write(equation_text))
        self.wait(1)
        
        # Show the equation mathematically
        equation = Text("y + 37 = -13", font_size=32, color=YELLOW)
        equation.move_to(UP*1)
        self.play(Write(equation))
        self.wait(1)
        
        # Explain the problem
        problem_text = Text("Wait... negative points? Let's solve this!", font_size=24, color=RED)
        problem_text.next_to(equation, DOWN, buff=0.5)
        self.play(Write(problem_text))
        self.wait(1)
        
        # Clear and focus on equation
        self.play(FadeOut(context), FadeOut(equation_text), FadeOut(problem_text))
        self.play(equation.animate.move_to(UP*1.5))
        
        # Balance concept with basketball scales
        balance_text = Text("Balance Principle: Like a fair basketball trade", font_size=24, color=ORANGE)
        balance_text.move_to(UP*0.5)
        self.play(Write(balance_text))
        
        # Create visual balance/scale
        left_side = Rectangle(width=2, height=0.5, color=BLUE, fill_opacity=0.3)
        right_side = Rectangle(width=2, height=0.5, color=RED, fill_opacity=0.3)
        left_side.move_to(LEFT*2.5)
        right_side.move_to(RIGHT*2.5)
        
        left_label = Text("y + 37", font_size=20).move_to(left_side)
        right_label = Text("-13", font_size=20).move_to(right_side)
        
        equals_sign = Text("=", font_size=32).move_to(ORIGIN)
        
        self.play(Create(left_side), Create(right_side))
        self.play(Write(left_label), Write(right_label), Write(equals_sign))
        self.wait(1)
        
        # Show subtraction property
        property_text = Text("Subtract 37 from BOTH sides", font_size=26, color=GREEN)
        property_text.move_to(DOWN*1)
        self.play(Write(property_text))
        self.wait(1)
        
        # Show the subtraction happening
        subtract_left = Text("- 37", font_size=20, color=GREEN)
        subtract_right = Text("- 37", font_size=20, color=GREEN)
        subtract_left.next_to(left_side, DOWN, buff=0.3)
        subtract_right.next_to(right_side, DOWN, buff=0.3)
        
        self.play(Write(subtract_left), Write(subtract_right))
        self.wait(1)
        
        # Transform to simplified form
        new_left = Text("y", font_size=20).move_to(left_side)
        new_right = Text("-50", font_size=20).move_to(right_side)
        
        self.play(
            Transform(left_label, new_left),
            Transform(right_label, new_right),
            FadeOut(subtract_left),
            FadeOut(subtract_right)
        )
        self.wait(1)
        
        # Show final answer
        final_equation = Text("y = -50", font_size=36, color=YELLOW)
        final_equation.move_to(DOWN*2.5)
        self.play(Write(final_equation))
        self.wait(1)
        
        # Basketball interpretation
        interpretation = Text("Curry had -50 points from free throws?", font_size=20, color=WHITE)
        reality_check = Text("This means our original equation was unrealistic!", font_size=20, color=RED)
        interpretation.move_to(DOWN*3.5)
        reality_check.next_to(interpretation, DOWN, buff=0.3)
        
        self.play(Write(interpretation))
        self.wait(1)
        self.play(Write(reality_check))
        self.wait(1)
        
        # Clear for summary
        self.play(
            FadeOut(balance_text), FadeOut(left_side), FadeOut(right_side),
            FadeOut(left_label), FadeOut(right_label), FadeOut(equals_sign),
            FadeOut(property_text), FadeOut(interpretation), FadeOut(reality_check)
        )
        
        # Summary
        summary_title = Text("Key Takeaway:", font_size=28, color=ORANGE)
        summary_title.move_to(UP*1)
        
        summary_points = [
            "• Subtraction Property: Subtract same value from both sides",
            "• Keeps the equation balanced (like a fair trade)",
            "• Always check if your answer makes sense!",
            "• In basketball: negative free throw points = impossible!"
        ]
        
        summary_text = Text("\n".join(summary_points), font_size=20, color=WHITE)
        summary_text.next_to(summary_title, DOWN, buff=0.5)
        
        self.play(Write(summary_title))
        self.wait(0.5)
        self.play(Write(summary_text))
        
        # Keep final equation visible
        final_equation.move_to(DOWN*2)
        
        self.wait(3)