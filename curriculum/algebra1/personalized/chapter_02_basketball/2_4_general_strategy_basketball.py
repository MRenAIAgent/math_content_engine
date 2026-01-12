# 5-step general strategy for solving linear equations - Basketball & NBA Edition
# Section 2.4

from manim import *

class BasketballLinearEquationsScene(Scene):
    def construct(self):
        # Title
        title = Text("5-Step Strategy for Solving Linear Equations", font_size=36, color=ORANGE)
        subtitle = Text("NBA Edition: Finding Curry's Game Stats!", font_size=24, color=BLUE)
        self.play(Write(title))
        self.wait(1)
        self.play(Write(subtitle.next_to(title, DOWN)))
        self.wait(2)
        self.play(title.animate.scale(0.7).to_edge(UP), FadeOut(subtitle))

        # Problem setup
        problem_text = Text("Problem: Curry scored 35 points total", font_size=28, color=WHITE)
        problem_eq = Text("3x + 2(x + 5) = 35", font_size=32, color=YELLOW)
        problem_desc = Text("3-pointers (3x) + 2-pointers (2(x+5)) = Total Points", font_size=20, color=GRAY)
        
        self.play(Write(problem_text))
        self.wait(1)
        self.play(Write(problem_eq.next_to(problem_text, DOWN)))
        self.play(Write(problem_desc.next_to(problem_eq, DOWN)))
        self.wait(2)
        
        # Clear and show strategy
        self.play(FadeOut(problem_text), FadeOut(problem_desc))
        self.play(problem_eq.animate.move_to(UP * 2.5))

        # Step 1: SIMPLIFY
        step1_title = Text("STEP 1: SIMPLIFY", font_size=32, color=ORANGE, weight=BOLD)
        step1_desc = Text("Distribute and combine like terms", font_size=24, color=WHITE)
        
        self.play(Write(step1_title.move_to(UP * 1.5)))
        self.play(Write(step1_desc.next_to(step1_title, DOWN)))
        
        eq1 = Text("3x + 2(x + 5) = 35", font_size=28, color=YELLOW)
        eq2 = Text("3x + 2x + 10 = 35", font_size=28, color=YELLOW)
        eq3 = Text("5x + 10 = 35", font_size=28, color=YELLOW)
        
        eq1.move_to(ORIGIN)
        self.play(Write(eq1))
        self.wait(1)
        self.play(ReplacementTransform(eq1, eq2.move_to(ORIGIN)))
        self.wait(1)
        self.play(ReplacementTransform(eq2, eq3.move_to(ORIGIN)))
        self.wait(2)
        
        self.play(FadeOut(step1_title), FadeOut(step1_desc))

        # Step 2: COLLECT VARIABLES
        step2_title = Text("STEP 2: COLLECT VARIABLES", font_size=32, color=ORANGE, weight=BOLD)
        step2_desc = Text("Get all x terms on one side (already done!)", font_size=24, color=WHITE)
        
        self.play(Write(step2_title.move_to(UP * 1.5)))
        self.play(Write(step2_desc.next_to(step2_title, DOWN)))
        
        highlight_box = SurroundingRectangle(Text("5x", font_size=28).move_to(LEFT * 1.2), color=GREEN, buff=0.1)
        self.play(Create(highlight_box))
        self.wait(2)
        self.play(FadeOut(step2_title), FadeOut(step2_desc), FadeOut(highlight_box))

        # Step 3: COLLECT CONSTANTS
        step3_title = Text("STEP 3: COLLECT CONSTANTS", font_size=32, color=ORANGE, weight=BOLD)
        step3_desc = Text("Get all numbers on the other side", font_size=24, color=WHITE)
        
        self.play(Write(step3_title.move_to(UP * 1.5)))
        self.play(Write(step3_desc.next_to(step3_title, DOWN)))
        
        eq4 = Text("5x + 10 - 10 = 35 - 10", font_size=28, color=YELLOW)
        eq5 = Text("5x = 25", font_size=28, color=YELLOW)
        
        self.play(ReplacementTransform(eq3, eq4.move_to(ORIGIN)))
        self.wait(1)
        self.play(ReplacementTransform(eq4, eq5.move_to(ORIGIN)))
        self.wait(2)
        
        self.play(FadeOut(step3_title), FadeOut(step3_desc))

        # Step 4: ISOLATE
        step4_title = Text("STEP 4: ISOLATE", font_size=32, color=ORANGE, weight=BOLD)
        step4_desc = Text("Divide to get x by itself", font_size=24, color=WHITE)
        
        self.play(Write(step4_title.move_to(UP * 1.5)))
        self.play(Write(step4_desc.next_to(step4_title, DOWN)))
        
        eq6 = Text("5x ÷ 5 = 25 ÷ 5", font_size=28, color=YELLOW)
        eq7 = Text("x = 5", font_size=32, color=GREEN, weight=BOLD)
        
        self.play(ReplacementTransform(eq5, eq6.move_to(ORIGIN)))
        self.wait(1)
        self.play(ReplacementTransform(eq6, eq7.move_to(ORIGIN)))
        self.wait(2)
        
        self.play(FadeOut(step4_title), FadeOut(step4_desc))

        # Step 5: CHECK
        step5_title = Text("STEP 5: CHECK", font_size=32, color=ORANGE, weight=BOLD)
        step5_desc = Text("Substitute back into original equation", font_size=24, color=WHITE)
        
        self.play(Write(step5_title.move_to(UP * 1.5)))
        self.play(Write(step5_desc.next_to(step5_title, DOWN)))
        
        check1 = Text("3(5) + 2(5 + 5) = 35", font_size=28, color=YELLOW)
        check2 = Text("15 + 2(10) = 35", font_size=28, color=YELLOW)
        check3 = Text("15 + 20 = 35 ✓", font_size=28, color=GREEN)
        
        self.play(ReplacementTransform(eq7, check1.move_to(ORIGIN)))
        self.wait(1)
        self.play(ReplacementTransform(check1, check2.move_to(ORIGIN)))
        self.wait(1)
        self.play(ReplacementTransform(check2, check3.move_to(ORIGIN)))
        self.wait(2)
        
        self.play(FadeOut(step5_title), FadeOut(step5_desc))

        # Final answer interpretation
        answer_text = Text("Curry made 5 three-pointers!", font_size=32, color=ORANGE, weight=BOLD)
        breakdown = Text("5 threes (15 pts) + 10 two-pointers (20 pts) = 35 total points", font_size=24, color=WHITE)
        
        self.play(ReplacementTransform(check3, answer_text.move_to(ORIGIN)))
        self.play(Write(breakdown.next_to(answer_text, DOWN)))
        self.wait(2)

        # Summary
        self.play(FadeOut(answer_text), FadeOut(breakdown))
        
        summary_title = Text("THE 5-STEP STRATEGY", font_size=36, color=ORANGE, weight=BOLD)
        steps = VGroup(
            Text("1. SIMPLIFY - Distribute & combine", font_size=24, color=WHITE),
            Text("2. COLLECT VARIABLES - One side", font_size=24, color=WHITE),
            Text("3. COLLECT CONSTANTS - Other side", font_size=24, color=WHITE),
            Text("4. ISOLATE - Get variable alone", font_size=24, color=WHITE),
            Text("5. CHECK - Verify your answer", font_size=24, color=WHITE)
        ).arrange(DOWN, buff=0.3)
        
        self.play(Write(summary_title.move_to(UP * 2)))
        self.play(Write(steps.move_to(DOWN * 0.5)))
        
        fun_fact = Text("Fun Fact: Curry averages 5+ threes per game!", font_size=20, color=YELLOW)
        self.play(Write(fun_fact.to_edge(DOWN)))
        
        self.wait(3)