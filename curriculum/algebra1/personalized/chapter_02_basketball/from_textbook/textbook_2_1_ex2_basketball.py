# Generated from textbook: LeBron's Points Needed - Solve Equations Using the Subtraction and Addition Properties of Equality
# Section 2.1, Example 2
# Theme: basketball

from manim import *

class LeBronPointsNeededScene(Scene):
    def construct(self):
        # Title
        title = Text("LeBron's Points Needed", font_size=48, color=ORANGE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        self.wait(1)
        
        # Basketball context
        context = Text(
            "LeBron James has scored y points so far this season.\n"
            "Combined with the 37 points he scored in his last game,\n"
            "his total is actually 13 points behind last year.",
            font_size=28,
            color=WHITE
        ).next_to(title, DOWN, buff=0.8)
        self.play(Write(context))
        self.wait(2)
        
        # Show the equation
        equation_label = Text("Equation to solve:", font_size=24, color=BLUE)
        equation_label.to_edge(LEFT, buff=1).shift(UP*0.5)
        
        equation = Text("y + 37 = -13", font_size=36, color=ORANGE)
        equation.next_to(equation_label, RIGHT, buff=0.5)
        
        self.play(Write(equation_label))
        self.play(Write(equation))
        self.wait(2)
        
        # Clear context to make room for solution steps
        self.play(FadeOut(context))
        
        # Solution steps
        steps_title = Text("Solution Steps:", font_size=28, color=BLUE)
        steps_title.next_to(equation, DOWN, buff=1).to_edge(LEFT, buff=1)
        self.play(Write(steps_title))
        
        # Step 1
        step1 = Text("Step 1: y + 37 = -13", font_size=24, color=WHITE)
        step1.next_to(steps_title, DOWN, buff=0.5).to_edge(LEFT, buff=1.5)
        self.play(Write(step1))
        self.wait(1)
        
        # Step 2
        step2_text = Text("Step 2: Subtract 37 from both sides", font_size=24, color=GREEN)
        step2_text.next_to(step1, DOWN, buff=0.3).to_edge(LEFT, buff=1.5)
        self.play(Write(step2_text))
        
        step2_eq = Text("y + 37 - 37 = -13 - 37", font_size=24, color=WHITE)
        step2_eq.next_to(step2_text, DOWN, buff=0.3).to_edge(LEFT, buff=2)
        self.play(Write(step2_eq))
        self.wait(2)
        
        # Step 3
        step3_text = Text("Step 3: Simplify", font_size=24, color=GREEN)
        step3_text.next_to(step2_eq, DOWN, buff=0.3).to_edge(LEFT, buff=1.5)
        self.play(Write(step3_text))
        
        step3_eq = Text("y = -50", font_size=32, color=YELLOW)
        step3_eq.next_to(step3_text, DOWN, buff=0.3).to_edge(LEFT, buff=2)
        self.play(Write(step3_eq))
        
        # Highlight the answer
        answer_box = SurroundingRectangle(step3_eq, color=ORANGE, buff=0.2)
        self.play(Create(answer_box))
        self.wait(2)
        
        # Verification
        verify_title = Text("Verification:", font_size=28, color=BLUE)
        verify_title.next_to(step3_eq, DOWN, buff=1).to_edge(LEFT, buff=1)
        self.play(Write(verify_title))
        
        verify_text = Text("Check: -50 + 37 = -13 ✓", font_size=24, color=GREEN)
        verify_text.next_to(verify_title, DOWN, buff=0.3).to_edge(LEFT, buff=1.5)
        self.play(Write(verify_text))
        self.wait(2)
        
        # Conclusion
        conclusion = Text(
            "LeBron scored -50 points compared to this point\n"
            "last season before his 37-point game!",
            font_size=24,
            color=ORANGE
        ).next_to(verify_text, DOWN, buff=1)
        self.play(Write(conclusion))
        
        # Basketball visual element
        basketball = Circle(radius=0.3, color=ORANGE, fill_opacity=0.8)
        basketball.to_corner(DR, buff=0.5)
        lines = VGroup(
            Line(basketball.get_left(), basketball.get_right(), color=BLACK),
            Arc(radius=0.3, start_angle=PI/2, angle=PI, color=BLACK).move_to(basketball),
            Arc(radius=0.3, start_angle=-PI/2, angle=PI, color=BLACK).move_to(basketball)
        )
        basketball_group = VGroup(basketball, lines)
        self.play(Create(basketball_group))
        
        self.wait(3)