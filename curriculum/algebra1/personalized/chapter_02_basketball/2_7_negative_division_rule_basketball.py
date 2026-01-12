# CRITICAL: Reversing inequality when dividing by negative - Basketball & NBA Edition
# Section 2.7

from manim import *

class InequalityReversalScene(Scene):
    def construct(self):
        # Title
        title = Text("Reversing Inequalities: A Basketball Lesson", font_size=36, color=ORANGE)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Setup scenario
        scenario = Text("Scenario: LeBron's scoring streak is in trouble!", font_size=24, color=WHITE)
        scenario.next_to(title, DOWN, buff=0.5)
        self.play(Write(scenario))
        self.wait(1)

        # Initial inequality
        problem_text = Text("Games left until streak ends:", font_size=20, color=BLUE)
        problem_text.to_edge(LEFT).shift(UP*2)
        self.play(Write(problem_text))

        inequality = Text("-2x > 8", font_size=32, color=YELLOW)
        inequality.next_to(problem_text, DOWN, buff=0.3)
        self.play(Write(inequality))
        self.wait(2)

        # Step 1: Show what we're solving for
        step1_text = Text("Step 1: We need to isolate x", font_size=20, color=GREEN)
        step1_text.next_to(inequality, DOWN, buff=0.5)
        self.play(Write(step1_text))
        self.wait(1)

        # Step 2: Divide both sides by -2
        step2_text = Text("Step 2: Divide both sides by -2", font_size=20, color=GREEN)
        step2_text.next_to(step1_text, DOWN, buff=0.3)
        self.play(Write(step2_text))

        division_show = Text("(-2x) ÷ (-2)    >    8 ÷ (-2)", font_size=28, color=WHITE)
        division_show.next_to(step2_text, DOWN, buff=0.3)
        self.play(Write(division_show))
        self.wait(2)

        # CRITICAL MOMENT: Show the reversal
        warning = Text("WAIT! When dividing by negative, flip the inequality!", 
                      font_size=24, color=RED, weight=BOLD)
        warning.next_to(division_show, DOWN, buff=0.5)
        self.play(Write(warning))
        
        # Highlight the inequality sign
        highlight_box = Rectangle(width=0.3, height=0.3, color=RED, stroke_width=3)
        highlight_box.move_to(division_show[16])  # Position over the > sign
        self.play(Create(highlight_box))
        self.wait(1)

        # Show the correct result
        correct_result = Text("x < -4", font_size=32, color=ORANGE)
        correct_result.next_to(warning, DOWN, buff=0.5)
        self.play(Write(correct_result))
        self.wait(2)

        # Clear for counter-example
        self.play(FadeOut(scenario, problem_text, inequality, step1_text, step2_text, 
                         division_show, warning, highlight_box, correct_result))

        # Counter-example to prove the rule
        counter_title = Text("Why does the inequality flip? Let's test it!", 
                           font_size=24, color=BLUE)
        counter_title.to_edge(LEFT).shift(UP*2.5)
        self.play(Write(counter_title))

        # Show a simple example
        example_text = Text("Simple example: -2 > -6 (True)", font_size=20, color=WHITE)
        example_text.next_to(counter_title, DOWN, buff=0.5)
        self.play(Write(example_text))

        # Divide both sides by -2 WITHOUT flipping
        wrong_way = Text("If we DON'T flip: (-2)÷(-2) > (-6)÷(-2)", font_size=18, color=RED)
        wrong_way.next_to(example_text, DOWN, buff=0.3)
        self.play(Write(wrong_way))

        wrong_result = Text("1 > 3 (FALSE!)", font_size=20, color=RED)
        wrong_result.next_to(wrong_way, DOWN, buff=0.3)
        self.play(Write(wrong_result))
        self.wait(2)

        # Show correct way
        right_way = Text("If we DO flip: (-2)÷(-2) < (-6)÷(-2)", font_size=18, color=GREEN)
        right_way.next_to(wrong_result, DOWN, buff=0.5)
        self.play(Write(right_way))

        right_result = Text("1 < 3 (TRUE!)", font_size=20, color=GREEN)
        right_result.next_to(right_way, DOWN, buff=0.3)
        self.play(Write(right_result))
        self.wait(2)

        # Basketball analogy
        self.play(FadeOut(counter_title, example_text, wrong_way, wrong_result, right_way, right_result))

        analogy_title = Text("Basketball Analogy: The Scoreboard Effect", 
                           font_size=24, color=ORANGE)
        analogy_title.to_edge(LEFT).shift(UP*2)
        self.play(Write(analogy_title))

        analogy_text1 = Text("Lakers: 100 points, Warriors: 90 points", font_size=18, color=WHITE)
        analogy_text1.next_to(analogy_title, DOWN, buff=0.5)
        self.play(Write(analogy_text1))

        analogy_text2 = Text("Lakers > Warriors (Lakers winning)", font_size=18, color=BLUE)
        analogy_text2.next_to(analogy_text1, DOWN, buff=0.3)
        self.play(Write(analogy_text2))

        analogy_text3 = Text("Now subtract 200 from BOTH teams:", font_size=18, color=YELLOW)
        analogy_text3.next_to(analogy_text2, DOWN, buff=0.5)
        self.play(Write(analogy_text3))

        analogy_text4 = Text("Lakers: -100, Warriors: -110", font_size=18, color=WHITE)
        analogy_text4.next_to(analogy_text3, DOWN, buff=0.3)
        self.play(Write(analogy_text4))

        analogy_text5 = Text("Now Warriors > Lakers! (-110 is less than -100)", 
                           font_size=18, color=RED)
        analogy_text5.next_to(analogy_text4, DOWN, buff=0.3)
        self.play(Write(analogy_text5))
        self.wait(3)

        # Final summary
        self.play(FadeOut(analogy_title, analogy_text1, analogy_text2, analogy_text3, 
                         analogy_text4, analogy_text5))

        summary_title = Text("Key Takeaway", font_size=28, color=ORANGE, weight=BOLD)
        summary_title.shift(UP*1)
        self.play(Write(summary_title))

        summary_text = Text("When multiplying or dividing an inequality by a negative number,\nFLIP the inequality sign!", 
                          font_size=20, color=WHITE)
        summary_text.next_to(summary_title, DOWN, buff=0.5)
        self.play(Write(summary_text))

        # Final example
        final_example = Text("Remember: -2x > 8  →  x < -4", font_size=24, color=YELLOW)
        final_example.next_to(summary_text, DOWN, buff=0.8)
        self.play(Write(final_example))

        # Fun fact
        fun_fact = Text("Fun Fact: Curry's 3-point percentage would be negative\nif we counted misses as negative points!", 
                       font_size=16, color=BLUE)
        fun_fact.to_edge(DOWN)
        self.play(Write(fun_fact))

        self.wait(3)