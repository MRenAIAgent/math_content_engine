# Generated from textbook: Team Scoring Deficit - Solve Equations Using the Subtraction and Addition Properties of Equality
# Section 2.1, Example 3
# Theme: basketball

from manim import *

class TeamScoringDeficitScene(Scene):
    def construct(self):
        # Title
        title = Text("Team Scoring Deficit", font_size=48, color=ORANGE)
        title.set_stroke(BLACK, 2)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Context setup
        context = Text("The Warriors are down by some points (a).", font_size=36, color=BLUE)
        context.move_to(UP * 2)
        self.play(Write(context))
        self.wait(1)

        context2 = Text("After giving up 28 points in a quarter,", font_size=36, color=BLUE)
        context2.move_to(UP * 1)
        self.play(Write(context2))
        self.wait(1)

        context3 = Text("they're now down by 37 points.", font_size=36, color=BLUE)
        context3.move_to(UP * 0)
        self.play(Write(context3))
        self.wait(2)

        # Clear context and show equation
        self.play(FadeOut(context), FadeOut(context2), FadeOut(context3))

        # Original equation
        equation_label = Text("Equation to solve:", font_size=32, color=WHITE)
        equation_label.move_to(UP * 2)
        self.play(Write(equation_label))

        equation1 = Text("a - 28 = -37", font_size=48, color=ORANGE)
        equation1.move_to(UP * 1)
        self.play(Write(equation1))
        self.wait(2)

        # Solution steps
        steps_title = Text("Solution Steps:", font_size=32, color=WHITE)
        steps_title.move_to(UP * 0.5)
        self.play(Write(steps_title))
        self.wait(1)

        # Step 1
        step1_label = Text("Step 1:", font_size=28, color=YELLOW)
        step1_label.move_to(LEFT * 4 + DOWN * 0.5)
        step1_eq = Text("a - 28 = -37", font_size=36, color=WHITE)
        step1_eq.move_to(RIGHT * 1 + DOWN * 0.5)
        
        self.play(Write(step1_label), Write(step1_eq))
        self.wait(1)

        # Step 2
        step2_label = Text("Step 2:", font_size=28, color=YELLOW)
        step2_label.move_to(LEFT * 4 + DOWN * 1.5)
        step2_eq = Text("a - 28 + 28 = -37 + 28", font_size=36, color=WHITE)
        step2_eq.move_to(RIGHT * 1 + DOWN * 1.5)
        
        self.play(Write(step2_label), Write(step2_eq))
        
        # Highlight addition property
        addition_note = Text("(Add 28 to both sides)", font_size=24, color=GREEN)
        addition_note.move_to(RIGHT * 1 + DOWN * 2)
        self.play(Write(addition_note))
        self.wait(2)

        # Step 3
        step3_label = Text("Step 3:", font_size=28, color=YELLOW)
        step3_label.move_to(LEFT * 4 + DOWN * 3)
        step3_eq = Text("a = -9", font_size=36, color=RED)
        step3_eq.move_to(RIGHT * 1 + DOWN * 3)
        
        self.play(Write(step3_label), Write(step3_eq))
        
        # Highlight final answer
        answer_box = SurroundingRectangle(step3_eq, color=RED, buff=0.1)
        self.play(Create(answer_box))
        self.wait(2)

        # Clear previous content
        self.play(FadeOut(VGroup(equation_label, equation1, steps_title, step1_label, step1_eq, 
                                step2_label, step2_eq, addition_note, step3_label, step3_eq, answer_box)))

        # Verification
        verify_title = Text("Verification:", font_size=36, color=ORANGE)
        verify_title.move_to(UP * 1.5)
        self.play(Write(verify_title))

        verify_text = Text("Check: -9 - 28 = -37", font_size=40, color=WHITE)
        verify_text.move_to(UP * 0.5)
        self.play(Write(verify_text))

        checkmark = Text("✓", font_size=48, color=GREEN)
        checkmark.move_to(DOWN * 0.5)
        self.play(Write(checkmark))
        self.wait(2)

        # Conclusion
        self.play(FadeOut(verify_title), FadeOut(verify_text), FadeOut(checkmark))

        conclusion = Text("The Warriors were down by 9 points", font_size=36, color=BLUE)
        conclusion.move_to(UP * 0.5)
        conclusion2 = Text("before giving up 28 more points!", font_size=36, color=BLUE)
        conclusion2.move_to(DOWN * 0.5)
        
        self.play(Write(conclusion))
        self.play(Write(conclusion2))
        
        # Basketball visual
        basketball = Circle(radius=0.3, color=ORANGE, fill_opacity=0.8)
        basketball.move_to(DOWN * 2)
        basketball_lines1 = Line(basketball.get_top(), basketball.get_bottom(), color=BLACK)
        basketball_lines2 = Line(basketball.get_left(), basketball.get_right(), color=BLACK)
        basketball_arc1 = Arc(radius=0.3, start_angle=0, angle=PI, color=BLACK)
        basketball_arc1.move_to(basketball.get_center())
        basketball_arc2 = Arc(radius=0.3, start_angle=PI, angle=PI, color=BLACK)
        basketball_arc2.move_to(basketball.get_center())
        
        basketball_group = VGroup(basketball, basketball_lines1, basketball_lines2, basketball_arc1, basketball_arc2)
        
        self.play(Create(basketball_group))
        self.wait(3)