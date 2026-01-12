# CRITICAL RULE: Reversing inequality when dividing by negative
# Generated for Chapter 2 - Section 2.7

from manim import *

class InequalityReversalScene(Scene):
    def construct(self):
        # Title
        title = Text("Critical Rule: Reversing Inequality When Dividing by Negative", font_size=36, color=YELLOW)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Step 1: Show original inequality
        step1_text = Text("Step 1: Start with the inequality", font_size=28, color=WHITE)
        step1_text.move_to(UP * 2.5)
        inequality1 = Text("-2x > 8", font_size=48, color=BLUE)
        inequality1.move_to(UP * 1.5)
        
        self.play(Write(step1_text))
        self.wait(0.5)
        self.play(Write(inequality1))
        self.wait(2)

        # Step 2: Warning about the rule
        warning_box = Rectangle(width=10, height=1.5, color=RED, fill_opacity=0.2)
        warning_box.move_to(ORIGIN)
        warning_text = Text("WARNING: When dividing by NEGATIVE, REVERSE the inequality!", 
                          font_size=32, color=RED)
        warning_text.move_to(ORIGIN)
        
        self.play(Create(warning_box))
        self.play(Write(warning_text))
        self.wait(3)
        
        # Clear warning
        self.play(FadeOut(warning_box), FadeOut(warning_text))

        # Step 3: Show the division and reversal
        step3_text = Text("Step 3: Divide both sides by -2 and FLIP the inequality", 
                         font_size=28, color=WHITE)
        step3_text.move_to(UP * 0.5)
        
        division_step = Text("-2x ÷ (-2) < 8 ÷ (-2)", font_size=40, color=ORANGE)
        division_step.move_to(DOWN * 0.5)
        
        final_answer = Text("x < -4", font_size=48, color=GREEN)
        final_answer.move_to(DOWN * 1.5)
        
        self.play(Write(step3_text))
        self.wait(1)
        self.play(Write(division_step))
        self.wait(2)
        self.play(Write(final_answer))
        self.wait(2)

        # Clear previous content
        self.play(FadeOut(step1_text), FadeOut(inequality1), FadeOut(step3_text), 
                 FadeOut(division_step), FadeOut(final_answer))

        # Step 4: Explanation with example
        explanation_title = Text("Step 4: WHY does this happen?", font_size=32, color=YELLOW)
        explanation_title.move_to(UP * 2)
        
        example_text = Text("Example: Start with a true statement", font_size=28, color=WHITE)
        example_text.move_to(UP * 1)
        
        true_statement = Text("4 > 2", font_size=40, color=GREEN)
        true_statement.move_to(UP * 0.2)
        
        multiply_step = Text("Multiply both sides by -1:", font_size=28, color=WHITE)
        multiply_step.move_to(DOWN * 0.5)
        
        false_if_not_flipped = Text("-4 > -2  ← This is FALSE!", font_size=36, color=RED)
        false_if_not_flipped.move_to(DOWN * 1.2)
        
        correct_flipped = Text("-4 < -2  ← This is TRUE!", font_size=36, color=GREEN)
        correct_flipped.move_to(DOWN * 2)
        
        self.play(Write(explanation_title))
        self.wait(1)
        self.play(Write(example_text))
        self.wait(1)
        self.play(Write(true_statement))
        self.wait(1)
        self.play(Write(multiply_step))
        self.wait(1)
        self.play(Write(false_if_not_flipped))
        self.wait(2)
        self.play(Write(correct_flipped))
        self.wait(3)

        # Clear explanation
        self.play(FadeOut(explanation_title), FadeOut(example_text), FadeOut(true_statement),
                 FadeOut(multiply_step), FadeOut(false_if_not_flipped), FadeOut(correct_flipped))

        # Step 5: Graph the solution
        graph_title = Text("Step 5: Graph the solution x < -4", font_size=32, color=YELLOW)
        graph_title.move_to(UP * 2.5)
        
        # Create number line manually
        line = Line(LEFT * 5, RIGHT * 5, color=WHITE)
        line.move_to(ORIGIN)
        
        # Add tick marks and numbers
        ticks = []
        numbers = []
        for i in range(-8, 3):
            tick = Line(UP * 0.1, DOWN * 0.1, color=WHITE)
            tick.move_to(line.point_from_proportion((i + 8) / 10))
            ticks.append(tick)
            
            if i % 2 == 0:  # Only show even numbers for clarity
                num = Text(str(i), font_size=20, color=WHITE)
                num.next_to(tick, DOWN, buff=0.2)
                numbers.append(num)
        
        # Open circle at -4
        open_circle = Circle(radius=0.15, color=RED, fill_opacity=0)
        open_circle.move_to(line.point_from_proportion((-4 + 8) / 10))
        
        # Arrow pointing left
        arrow_start = line.point_from_proportion((-4 + 8) / 10)
        arrow_end = line.point_from_proportion((-7 + 8) / 10)
        arrow = Arrow(start=arrow_start, end=arrow_end, color=BLUE, buff=0.1, stroke_width=8)
        
        solution_label = Text("x < -4", font_size=28, color=GREEN)
        solution_label.next_to(arrow, DOWN)
        
        self.play(Write(graph_title))
        self.wait(1)
        self.play(Create(line))
        self.play(*[Create(tick) for tick in ticks])
        self.play(*[Write(num) for num in numbers])
        self.wait(1)
        self.play(Create(open_circle))
        self.wait(1)
        self.play(Create(arrow))
        self.wait(1)
        self.play(Write(solution_label))
        self.wait(2)

        # Final summary
        self.play(FadeOut(graph_title), FadeOut(line), *[FadeOut(tick) for tick in ticks],
                 *[FadeOut(num) for num in numbers], FadeOut(open_circle), 
                 FadeOut(arrow), FadeOut(solution_label))
        
        summary_box = Rectangle(width=12, height=3, color=YELLOW, fill_opacity=0.1)
        summary_box.move_to(ORIGIN)
        
        summary_title = Text("KEY TAKEAWAY", font_size=36, color=YELLOW)
        summary_title.move_to(UP * 1)
        
        summary_text1 = Text("When multiplying or dividing an inequality by a NEGATIVE number:", 
                            font_size=28, color=WHITE)
        summary_text1.move_to(UP * 0.2)
        
        summary_text2 = Text("ALWAYS REVERSE the inequality sign!", 
                            font_size=32, color=RED)
        summary_text2.move_to(DOWN * 0.5)
        
        self.play(Create(summary_box))
        self.play(Write(summary_title))
        self.wait(1)
        self.play(Write(summary_text1))
        self.wait(1)
        self.play(Write(summary_text2))
        self.wait(3)