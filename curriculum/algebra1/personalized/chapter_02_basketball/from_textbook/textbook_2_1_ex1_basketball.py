# Generated from textbook: Curry's Scoring Verification - Solve Equations Using the Subtraction and Addition Properties of Equality
# Section 2.1, Example 1
# Theme: basketball

from manim import *

class CurryScoringVerificationScene(Scene):
    def construct(self):
        # Title
        title = Text("Curry's Scoring Verification", font_size=48, color=ORANGE)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Context setup
        context = Text(
            "Curry averages 6 points per minute of play.\nAfter sitting out 17 points worth of time,\ndid he contribute 13 points in x = 5 minutes?",
            font_size=24,
            color=WHITE
        ).move_to(UP * 2)
        
        self.play(Write(context))
        self.wait(2)

        # Show the equation
        equation_label = Text("Equation to verify:", font_size=28, color=BLUE)
        equation_label.move_to(UP * 0.5)
        
        equation = Text("6x - 17 = 13", font_size=36, color=YELLOW)
        equation.next_to(equation_label, DOWN, buff=0.3)
        
        question = Text("Is x = 5 a solution?", font_size=28, color=RED)
        question.next_to(equation, DOWN, buff=0.5)
        
        self.play(Write(equation_label))
        self.play(Write(equation))
        self.play(Write(question))
        self.wait(2)

        # Clear context and move equation up
        self.play(FadeOut(context))
        equation_group = VGroup(equation_label, equation, question)
        self.play(equation_group.animate.move_to(UP * 2.5))
        
        # Solution steps
        step1_label = Text("Step 1: Substitute x = 5", font_size=24, color=BLUE)
        step1_label.move_to(UP * 1.5)
        
        step1_eq = Text("6(5) - 17 = 13", font_size=32, color=WHITE)
        step1_eq.next_to(step1_label, DOWN, buff=0.3)
        
        self.play(Write(step1_label))
        self.play(Write(step1_eq))
        self.wait(1.5)

        # Step 2
        step2_label = Text("Step 2: Multiply", font_size=24, color=BLUE)
        step2_label.move_to(UP * 0.3)
        
        step2_eq = Text("30 - 17 = 13", font_size=32, color=WHITE)
        step2_eq.next_to(step2_label, DOWN, buff=0.3)
        
        self.play(Write(step2_label))
        self.play(Transform(step1_eq.copy(), step2_eq))
        self.play(Write(step2_eq))
        self.wait(1.5)

        # Step 3
        step3_label = Text("Step 3: Subtract", font_size=24, color=BLUE)
        step3_label.move_to(DOWN * 0.9)
        
        step3_eq = Text("13 = 13", font_size=32, color=GREEN)
        step3_eq.next_to(step3_label, DOWN, buff=0.3)
        
        self.play(Write(step3_label))
        self.play(Transform(step2_eq.copy(), step3_eq))
        self.play(Write(step3_eq))
        self.wait(1)

        # Highlight the verification
        checkmark = Text("✓", font_size=48, color=GREEN)
        checkmark.next_to(step3_eq, RIGHT, buff=0.3)
        self.play(Write(checkmark))
        self.wait(1)

        # Final answer
        answer_box = Rectangle(width=8, height=1.5, color=ORANGE, fill_opacity=0.2)
        answer_box.move_to(DOWN * 2.5)
        
        final_answer = Text(
            "Yes, x = 5 is a solution!\nCurry nailed it! 🎯",
            font_size=28,
            color=ORANGE
        )
        final_answer.move_to(DOWN * 2.5)
        
        self.play(Create(answer_box))
        self.play(Write(final_answer))
        self.wait(1)

        # Basketball fun fact
        fun_fact = Text(
            "Fun Fact: This is like verifying Curry's incredible\nconsistency in clutch moments!",
            font_size=20,
            color=YELLOW
        ).move_to(DOWN * 3.5)
        
        self.play(Write(fun_fact))
        self.wait(3)