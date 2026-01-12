# Generated from textbook: Calculating Plus/Minus - Solve Equations Using the Subtraction and Addition Properties of Equality
# Section 2.1, Example 4
# Theme: basketball

from manim import *

class BasketballPlusMinusScene(Scene):
    def construct(self):
        # Title
        title = Text("Calculating Plus/Minus", font_size=48, color=ORANGE)
        subtitle = Text("Solving Equations with Addition & Subtraction", font_size=32, color=WHITE)
        self.play(Write(title))
        self.wait(1)
        self.play(Write(subtitle.next_to(title, DOWN)))
        self.wait(2)
        
        # Move title up
        self.play(
            title.animate.scale(0.7).to_edge(UP),
            FadeOut(subtitle)
        )
        
        # Basketball context
        context = Text("Basketball Plus/Minus Problem", font_size=36, color=ORANGE)
        story = Text("A player's plus/minus is calculated from multiple quarters.", font_size=28)
        story2 = Text("In a game: 9x - 5 - 8x - 6 = 7", font_size=28, color=BLUE)
        story3 = Text("where x represents a scoring factor", font_size=24, color=GRAY)
        
        self.play(Write(context))
        self.wait(1)
        self.play(context.animate.to_edge(UP, buff=1.2))
        
        self.play(Write(story.move_to(UP * 1.5)))
        self.wait(1)
        self.play(Write(story2.next_to(story, DOWN, buff=0.3)))
        self.wait(1)
        self.play(Write(story3.next_to(story2, DOWN, buff=0.2)))
        self.wait(2)
        
        # Clear context
        self.play(FadeOut(story), FadeOut(story2), FadeOut(story3))
        
        # Show the equation prominently
        equation_title = Text("Equation to Solve:", font_size=32, color=ORANGE)
        equation = Text("9x - 5 - 8x - 6 = 7", font_size=40, color=WHITE)
        
        self.play(Write(equation_title.move_to(UP * 1)))
        self.play(Write(equation.next_to(equation_title, DOWN, buff=0.5)))
        self.wait(2)
        
        # Move equation up for solution steps
        self.play(
            equation_title.animate.scale(0.8).move_to(UP * 2),
            equation.animate.scale(0.9).move_to(UP * 1.3)
        )
        
        # Solution steps
        steps_title = Text("Solution Steps:", font_size=32, color=ORANGE)
        self.play(Write(steps_title.move_to(UP * 0.3)))
        
        # Step 1
        step1_label = Text("Step 1:", font_size=28, color=BLUE)
        step1_eq = Text("9x - 5 - 8x - 6 = 7", font_size=32)
        step1_group = VGroup(step1_label, step1_eq).arrange(RIGHT, buff=0.3).move_to(DOWN * 0.3)
        
        self.play(Write(step1_group))
        self.wait(2)
        
        # Step 2
        step2_label = Text("Step 2:", font_size=28, color=BLUE)
        step2_eq = Text("x - 11 = 7", font_size=32)
        step2_note = Text("(Combine like terms: 9x - 8x = x, -5 - 6 = -11)", font_size=20, color=GRAY)
        step2_group = VGroup(step2_label, step2_eq).arrange(RIGHT, buff=0.3).next_to(step1_group, DOWN, buff=0.3)
        
        self.play(Write(step2_group))
        self.play(Write(step2_note.next_to(step2_group, DOWN, buff=0.1)))
        self.wait(2)
        
        # Step 3
        step3_label = Text("Step 3:", font_size=28, color=BLUE)
        step3_eq = Text("x - 11 + 11 = 7 + 11", font_size=32)
        step3_note = Text("(Add 11 to both sides)", font_size=20, color=GRAY)
        step3_group = VGroup(step3_label, step3_eq).arrange(RIGHT, buff=0.3).next_to(step2_note, DOWN, buff=0.3)
        
        self.play(Write(step3_group))
        self.play(Write(step3_note.next_to(step3_group, DOWN, buff=0.1)))
        self.wait(2)
        
        # Step 4 - Final answer
        step4_label = Text("Step 4:", font_size=28, color=BLUE)
        step4_eq = Text("x = 18", font_size=36, color=GREEN)
        step4_group = VGroup(step4_label, step4_eq).arrange(RIGHT, buff=0.3).next_to(step3_note, DOWN, buff=0.3)
        
        self.play(Write(step4_group))
        
        # Highlight the answer
        answer_box = SurroundingRectangle(step4_eq, color=GREEN, buff=0.1)
        self.play(Create(answer_box))
        self.wait(2)
        
        # Clear for verification
        self.play(FadeOut(VGroup(steps_title, step1_group, step2_group, step2_note, step3_group, step3_note, answer_box)))
        
        # Verification
        verify_title = Text("Verification:", font_size=32, color=ORANGE)
        verify_text = Text("Check: 9(18) - 5 - 8(18) - 6", font_size=28)
        verify_calc = Text("= 162 - 5 - 144 - 6", font_size=28)
        verify_result = Text("= 7 ✓", font_size=32, color=GREEN)
        
        verify_group = VGroup(verify_title, verify_text, verify_calc, verify_result).arrange(DOWN, buff=0.3).move_to(DOWN * 0.5)
        
        self.play(Write(verify_title))
        self.wait(1)
        self.play(Write(verify_text))
        self.wait(1)
        self.play(Write(verify_calc))
        self.wait(1)
        self.play(Write(verify_result))
        
        # Highlight verification
        check_box = SurroundingRectangle(verify_result, color=GREEN, buff=0.1)
        self.play(Create(check_box))
        self.wait(2)
        
        # Final answer highlight
        final_answer = Text("Final Answer: x = 18", font_size=40, color=GREEN)
        self.play(
            FadeOut(verify_group),
            FadeOut(check_box),
            FadeOut(step4_group)
        )
        self.play(Write(final_answer))
        
        # Basketball conclusion
        conclusion = Text("The scoring factor equals 18!", font_size=28, color=ORANGE)
        basketball_fact = Text("Just like balancing a basketball scoreboard,", font_size=24)
        basketball_fact2 = Text("both sides of an equation must stay equal!", font_size=24)
        
        self.play(Write(conclusion.next_to(final_answer, DOWN, buff=0.5)))
        self.wait(1)
        self.play(Write(basketball_fact.next_to(conclusion, DOWN, buff=0.3)))
        self.play(Write(basketball_fact2.next_to(basketball_fact, DOWN, buff=0.1)))
        
        self.wait(3)