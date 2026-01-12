# Addition Property of Equality for solving equations - Basketball & NBA Edition
# Section 2.1

from manim import *

class BasketballAdditionPropertyScene(Scene):
    def construct(self):
        # Title
        title = Text("Addition Property of Equality", font_size=36, color=ORANGE).scale(0.8)
        subtitle = Text("Solving Equations with Basketball Stats", font_size=24, color=WHITE)
        title_group = VGroup(title, subtitle).arrange(DOWN, buff=0.3)
        
        self.play(Write(title))
        self.play(Write(subtitle))
        self.wait(1)
        self.play(title_group.animate.to_edge(UP))

        # Basketball context setup
        context = Text("Stephen Curry's scoring mystery:", font_size=28, color=BLUE)
        context.move_to(UP * 2.5)
        self.play(Write(context))
        self.wait(1)

        # Story setup
        story = Text("Curry scored some points, then lost 28 points due to", font_size=20)
        story2 = Text("technical fouls. His final score was -37 points.", font_size=20)
        story3 = Text("How many points did he start with?", font_size=20, color=YELLOW)
        
        story_group = VGroup(story, story2, story3).arrange(DOWN, buff=0.2)
        story_group.move_to(UP * 1.5)
        
        self.play(Write(story))
        self.play(Write(story2))
        self.play(Write(story3))
        self.wait(2)

        # Clear story, keep context
        self.play(FadeOut(story_group))

        # Show the equation
        equation_label = Text("The equation:", font_size=24, color=WHITE)
        equation_label.move_to(UP * 0.5)
        
        equation = Text("a - 28 = -37", font_size=32, color=ORANGE)
        equation.next_to(equation_label, DOWN, buff=0.3)
        
        self.play(Write(equation_label))
        self.play(Write(equation))
        self.wait(1.5)

        # Basketball court visualization
        court = Rectangle(width=6, height=2, color=ORANGE, stroke_width=3)
        court.move_to(DOWN * 1.5)
        
        left_side = Text("a - 28", font_size=24, color=WHITE)
        left_side.move_to(court.get_left() + RIGHT * 1.2)
        
        equals_sign = Text("=", font_size=32, color=YELLOW)
        equals_sign.move_to(court.get_center())
        
        right_side = Text("-37", font_size=24, color=WHITE)
        right_side.move_to(court.get_right() + LEFT * 1.2)
        
        balance_label = Text("The equation must stay balanced!", font_size=20, color=GREEN)
        balance_label.next_to(court, DOWN, buff=0.3)
        
        self.play(Create(court))
        self.play(Write(left_side), Write(equals_sign), Write(right_side))
        self.play(Write(balance_label))
        self.wait(2)

        # Addition Property explanation
        property_text = Text("Addition Property of Equality:", font_size=24, color=BLUE)
        property_text.move_to(UP * 2)
        
        property_rule = Text("Add the same number to BOTH sides", font_size=20, color=YELLOW)
        property_rule.next_to(property_text, DOWN, buff=0.2)
        
        self.play(ReplacementTransform(context, property_text))
        self.play(Write(property_rule))
        self.wait(1.5)

        # Show adding 28 to both sides
        add_text = Text("Add 28 to both sides:", font_size=22, color=WHITE)
        add_text.move_to(UP * 0.8)
        
        self.play(ReplacementTransform(equation_label, add_text))
        self.wait(1)

        # Animate adding 28
        plus_28_left = Text("+ 28", font_size=20, color=GREEN)
        plus_28_left.next_to(left_side, RIGHT, buff=0.2)
        
        plus_28_right = Text("+ 28", font_size=20, color=GREEN)
        plus_28_right.next_to(right_side, RIGHT, buff=0.2)
        
        self.play(Write(plus_28_left), Write(plus_28_right))
        self.wait(1)

        # Show the simplification
        new_left = Text("a", font_size=24, color=WHITE)
        new_left.move_to(left_side.get_center())
        
        new_right = Text("-9", font_size=24, color=WHITE)
        new_right.move_to(right_side.get_center())
        
        # Highlight the cancellation
        cancel_box = SurroundingRectangle(VGroup(Text("-28", font_size=20), plus_28_left), color=RED)
        self.play(Create(cancel_box))
        self.wait(1)
        self.play(FadeOut(cancel_box))
        
        self.play(
            ReplacementTransform(VGroup(left_side, plus_28_left), new_left),
            ReplacementTransform(VGroup(right_side, plus_28_right), new_right)
        )
        self.wait(1.5)

        # Final answer
        final_equation = Text("a = -9", font_size=32, color=ORANGE)
        final_equation.move_to(equation.get_center())
        
        self.play(ReplacementTransform(equation, final_equation))
        self.wait(1)

        # Basketball interpretation
        interpretation = Text("Curry started with -9 points!", font_size=24, color=YELLOW)
        interpretation.next_to(court, DOWN, buff=0.8)
        
        self.play(ReplacementTransform(balance_label, interpretation))
        self.wait(1)

        # Verification
        verify_text = Text("Let's verify: -9 - 28 = -37 ✓", font_size=22, color=GREEN)
        verify_text.next_to(interpretation, DOWN, buff=0.3)
        
        self.play(Write(verify_text))
        self.wait(1.5)

        # Key takeaway
        takeaway_title = Text("Key Takeaway:", font_size=24, color=BLUE)
        takeaway_title.move_to(UP * 2)
        
        takeaway_text = Text("Whatever you do to one side of an equation,", font_size=20, color=WHITE)
        takeaway_text2 = Text("you must do to the other side to keep it balanced!", font_size=20, color=WHITE)
        
        takeaway_group = VGroup(takeaway_text, takeaway_text2).arrange(DOWN, buff=0.2)
        takeaway_group.next_to(takeaway_title, DOWN, buff=0.3)
        
        self.play(
            ReplacementTransform(VGroup(property_text, property_rule, add_text), takeaway_title),
            FadeOut(court, left_side, equals_sign, right_side, new_left, new_right, final_equation)
        )
        self.play(Write(takeaway_group))
        
        # Fun fact
        fun_fact = Text("Fun Fact: In real NBA games, technical fouls", font_size=18, color=ORANGE)
        fun_fact2 = Text("result in free throws for the opponent, not point deductions!", font_size=18, color=ORANGE)
        fun_fact_group = VGroup(fun_fact, fun_fact2).arrange(DOWN, buff=0.1)
        fun_fact_group.move_to(DOWN * 2)
        
        self.play(Write(fun_fact_group))
        self.wait(3)