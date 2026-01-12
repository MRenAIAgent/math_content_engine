# Multi-step linear inequalities
# Generated for Chapter 2 - Section 2.7

from manim import *

class MultiStepLinearInequalityScene(Scene):
    def construct(self):
        # Title
        title = Text("Multi-Step Linear Inequalities", font_size=36, color=BLUE)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Original inequality
        original = Text("Solve: 5 - 3x >= 17", font_size=32)
        original.move_to(UP * 2)
        self.play(Write(original))
        self.wait(2)

        # Step 1
        step1_label = Text("Step 1: Subtract 5 from both sides", font_size=24, color=YELLOW)
        step1_label.move_to(UP * 0.5)
        self.play(Write(step1_label))
        
        step1_eq = Text("5 - 3x - 5 >= 17 - 5", font_size=28)
        step1_eq.move_to(ORIGIN)
        self.play(Write(step1_eq))
        self.wait(1)
        
        step1_result = Text("-3x >= 12", font_size=28, color=GREEN)
        step1_result.move_to(DOWN * 0.5)
        self.play(Write(step1_result))
        self.wait(2)

        # Clear for step 2
        self.play(FadeOut(step1_label), FadeOut(step1_eq))

        # Step 2
        step2_label = Text("Step 2: Divide by -3 AND REVERSE the inequality", font_size=24, color=YELLOW)
        step2_label.move_to(UP * 0.5)
        self.play(Write(step2_label))
        
        # Emphasize the reversal
        warning = Text("IMPORTANT: When dividing by negative, flip the sign!", font_size=20, color=RED)
        warning.move_to(ORIGIN)
        self.play(Write(warning))
        self.wait(2)
        
        step2_eq = Text("-3x / (-3) <= 12 / (-3)", font_size=28)
        step2_eq.move_to(DOWN * 0.2)
        self.play(ReplacementTransform(warning, step2_eq))
        self.wait(1)
        
        step2_result = Text("x <= -4", font_size=28, color=GREEN)
        step2_result.move_to(DOWN * 0.8)
        self.play(Write(step2_result))
        
        # Highlight the sign change
        arrow = Arrow(start=step1_result.get_center() + RIGHT * 0.3, 
                     end=step2_result.get_center() + RIGHT * 0.3, color=RED)
        sign_change = Text(">= becomes <=", font_size=18, color=RED)
        sign_change.next_to(arrow, RIGHT)
        self.play(Create(arrow), Write(sign_change))
        self.wait(3)

        # Clear for graphing
        self.play(FadeOut(step1_result), FadeOut(step2_label), FadeOut(step2_eq), 
                 FadeOut(arrow), FadeOut(sign_change))

        # Step 3: Graph setup
        graph_label = Text("Step 3: Graph x <= -4", font_size=24, color=YELLOW)
        graph_label.move_to(UP * 0.5)
        self.play(Write(graph_label))

        # Create number line manually
        line = Line(LEFT * 4, RIGHT * 4, color=WHITE)
        line.move_to(DOWN * 1.5)
        self.play(Create(line))
        
        # Add tick marks and numbers
        ticks = VGroup()
        numbers = VGroup()
        for i in range(-8, 3):
            tick_pos = line.get_start() + RIGHT * (i + 8) * 0.8
            tick = Line(tick_pos + UP * 0.1, tick_pos + DOWN * 0.1, color=WHITE)
            ticks.add(tick)
            if i % 2 == 0:
                num = Text(str(i), font_size=16).next_to(tick, DOWN, buff=0.2)
                numbers.add(num)
        
        self.play(Create(ticks), Write(numbers))
        
        # Add closed circle at -4
        closed_circle_pos = line.get_start() + RIGHT * (-4 + 8) * 0.8
        closed_circle = Dot(closed_circle_pos, color=BLUE, radius=0.1)
        self.play(Create(closed_circle))
        
        circle_label = Text("Closed circle: -4 is included (<=)", font_size=18, color=BLUE)
        circle_label.next_to(closed_circle, UP)
        self.play(Write(circle_label))
        self.wait(2)

        # Step 4: Arrow pointing left
        step4_label = Text("Step 4: Arrow points left (x is less than or equal to -4)", 
                          font_size=20, color=YELLOW)
        step4_label.move_to(DOWN * 3)
        self.play(Write(step4_label))
        
        # Create arrow pointing left from -4
        arrow_start = closed_circle_pos
        arrow_end = line.get_start() + RIGHT * (-7 + 8) * 0.8
        arrow_left = Arrow(start=arrow_start, end=arrow_end, color=GREEN, stroke_width=6)
        self.play(Create(arrow_left))
        self.wait(2)

        # Key distinction
        self.play(FadeOut(graph_label), FadeOut(step4_label), FadeOut(circle_label))
        
        distinction = Text("Key: <= or >= use CLOSED circles\n< or > use OPEN circles", 
                          font_size=20, color=RED)
        distinction.move_to(UP * 0.8)
        self.play(Write(distinction))
        
        # Show comparison
        open_circle_pos = line.get_start() + RIGHT * (-2 + 8) * 0.8
        open_circle = Circle(radius=0.1, color=WHITE).move_to(open_circle_pos)
        open_label = Text("Open", font_size=16).next_to(open_circle, UP)
        closed_label2 = Text("Closed", font_size=16).next_to(closed_circle, DOWN)
        
        self.play(Create(open_circle), Write(open_label), Write(closed_label2))
        self.wait(3)

        # Final answer
        final_answer = Text("Solution: x <= -4", font_size=32, color=GREEN)
        final_answer.move_to(DOWN * 3.5)
        self.play(Write(final_answer))
        
        # Highlight the final result
        self.play(Indicate(step2_result), Indicate(final_answer))
        self.wait(3)