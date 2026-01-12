# Solving and graphing basic linear inequalities
# Generated for Chapter 2 - Section 2.7

from manim import *

class LinearInequalityScene(Scene):
    def construct(self):
        # Title
        title = Text("Solving Linear Inequalities", font_size=36, color=BLUE)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Step 1: Show the inequality
        step1_label = Text("Step 1: Given inequality", font_size=24, color=YELLOW).to_edge(LEFT).shift(UP*2)
        inequality1 = Text("x + 4 > 9", font_size=32).next_to(step1_label, RIGHT, buff=1)
        
        self.play(Write(step1_label))
        self.play(Write(inequality1))
        self.wait(2)

        # Step 2: Subtract 4 from both sides
        step2_label = Text("Step 2: Subtract 4 from both sides", font_size=24, color=YELLOW).next_to(step1_label, DOWN, aligned_edge=LEFT, buff=0.5)
        
        # Show the work
        subtract_line = Text("x + 4 - 4 > 9 - 4", font_size=28).next_to(step2_label, RIGHT, buff=1)
        solution = Text("x > 5", font_size=32, color=GREEN).next_to(subtract_line, DOWN, buff=0.5)
        
        self.play(Write(step2_label))
        self.play(Write(subtract_line))
        self.wait(1)
        self.play(Write(solution))
        self.play(Indicate(solution))
        self.wait(2)

        # Step 3: Graph on number line
        step3_label = Text("Step 3: Graph on number line", font_size=24, color=YELLOW).next_to(step2_label, DOWN, aligned_edge=LEFT, buff=1)
        self.play(Write(step3_label))
        self.wait(1)

        # Create number line manually
        line = Line(LEFT*4, RIGHT*4, color=WHITE).shift(DOWN*1.5)
        self.play(Create(line))
        
        # Add tick marks and numbers
        tick_marks = VGroup()
        numbers = VGroup()
        for i in range(-2, 11):
            tick_pos = line.get_start() + RIGHT * (i + 2) * 8/12
            tick = Line(UP*0.1, DOWN*0.1, color=WHITE).move_to(tick_pos)
            tick_marks.add(tick)
            
            if i >= 0 and i <= 9:
                number = Text(str(i), font_size=16).next_to(tick, DOWN, buff=0.1)
                numbers.add(number)
        
        self.play(Create(tick_marks))
        self.play(Write(numbers))
        self.wait(1)

        # Mark point 5 with open circle
        point_5_pos = line.get_start() + RIGHT * 7 * 8/12
        open_circle = Circle(radius=0.08, color=RED, fill_opacity=0).move_to(point_5_pos)
        
        self.play(Create(open_circle))
        
        # Add label for the open circle
        circle_label = Text("Open circle at 5\n(not included)", font_size=16, color=RED).next_to(open_circle, UP, buff=0.3)
        self.play(Write(circle_label))
        self.wait(1)

        # Draw arrow pointing right
        arrow_start = point_5_pos
        arrow_end = line.get_start() + RIGHT * 11.5 * 8/12
        arrow = Arrow(arrow_start, arrow_end, color=BLUE, buff=0.1, stroke_width=6)
        
        self.play(Create(arrow))
        
        # Add label for the arrow
        arrow_label = Text("All numbers > 5", font_size=16, color=BLUE).next_to(arrow, UP, buff=0.2)
        self.play(Write(arrow_label))
        self.wait(2)

        # Step 4: Interval notation
        step4_label = Text("Step 4: Interval notation", font_size=24, color=YELLOW).next_to(step3_label, DOWN, aligned_edge=LEFT, buff=1)
        interval_notation = Text("(5, ∞)", font_size=32, color=PURPLE).next_to(step4_label, RIGHT, buff=1)
        
        self.play(Write(step4_label))
        self.play(Write(interval_notation))
        self.wait(1)

        # Explanation of interval notation
        explanation = Text("Parenthesis means 5 is NOT included", font_size=18, color=GRAY).next_to(interval_notation, DOWN, buff=0.3)
        self.play(Write(explanation))
        self.wait(2)

        # Summary box
        summary_box = Rectangle(width=6, height=1.5, color=GREEN, fill_opacity=0.1).to_edge(DOWN, buff=0.5)
        summary_title = Text("Summary", font_size=20, color=GREEN, weight=BOLD).move_to(summary_box.get_top()).shift(DOWN*0.2)
        summary_text = Text("Solution: x > 5\nGraph: Open circle at 5, arrow right\nInterval: (5, ∞)", 
                           font_size=16, color=WHITE).move_to(summary_box.get_center()).shift(DOWN*0.1)
        
        self.play(Create(summary_box))
        self.play(Write(summary_title))
        self.play(Write(summary_text))
        self.wait(3)