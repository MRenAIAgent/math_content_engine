# Verifying a solution to a linear equation - Basketball & NBA Edition
# Section 2.1

from manim import *

class BasketballLinearEquationVerificationScene(Scene):
    def construct(self):
        # Title
        title = Text("Verifying Solutions to Linear Equations", font_size=36, color=ORANGE)
        subtitle = Text("Stephen Curry's Scoring Challenge", font_size=24, color=BLUE)
        
        self.play(Write(title))
        self.wait(1)
        self.play(Write(subtitle.next_to(title, DOWN)))
        self.wait(1)
        self.play(title.animate.to_edge(UP), subtitle.animate.to_edge(UP).shift(DOWN*0.5))
        
        # Basketball scenario setup
        scenario = Text("Curry scored 6 points per quarter minus 17 penalty points", font_size=20)
        scenario2 = Text("His final score was 13 points. Did he play 5 quarters?", font_size=20)
        scenario.next_to(subtitle, DOWN, buff=0.8)
        scenario2.next_to(scenario, DOWN, buff=0.3)
        
        self.play(Write(scenario))
        self.play(Write(scenario2))
        self.wait(2)
        
        # Clear scenario text
        self.play(FadeOut(scenario), FadeOut(scenario2))
        
        # Step 1: Original equation
        step1_title = Text("Step 1: Write the Original Equation", font_size=24, color=ORANGE)
        step1_title.to_edge(LEFT).shift(UP*2)
        
        equation = Text("6x - 17 = 13", font_size=32)
        equation.next_to(step1_title, DOWN, buff=0.5).shift(RIGHT*2)
        
        explanation1 = Text("where x = number of quarters played", font_size=18, color=GRAY)
        explanation1.next_to(equation, DOWN, buff=0.3)
        
        self.play(Write(step1_title))
        self.play(Write(equation))
        self.play(Write(explanation1))
        self.wait(2)
        
        # Step 2: Substitute x = 5
        step2_title = Text("Step 2: Substitute x = 5", font_size=24, color=ORANGE)
        step2_title.next_to(step1_title, DOWN, buff=1.5)
        
        substitution = Text("6(5) - 17 = 13", font_size=32, color=BLUE)
        substitution.next_to(step2_title, DOWN, buff=0.5).shift(RIGHT*2)
        
        arrow = Arrow(equation.get_center(), substitution.get_center(), color=YELLOW)
        
        self.play(Write(step2_title))
        self.play(Create(arrow))
        self.play(Transform(equation.copy(), substitution))
        self.wait(2)
        
        # Step 3: Calculate left side
        step3_title = Text("Step 3: Calculate the Left Side", font_size=24, color=ORANGE)
        step3_title.next_to(step2_title, DOWN, buff=1.5)
        
        calc1 = Text("6(5) - 17", font_size=28)
        calc2 = Text("= 30 - 17", font_size=28, color=GREEN)
        calc3 = Text("= 13", font_size=28, color=RED)
        
        calc1.next_to(step3_title, DOWN, buff=0.5).shift(RIGHT*1)
        calc2.next_to(calc1, RIGHT, buff=0.5)
        calc3.next_to(calc2, RIGHT, buff=0.5)
        
        self.play(Write(step3_title))
        self.play(Write(calc1))
        self.wait(1)
        self.play(Write(calc2))
        self.wait(1)
        self.play(Write(calc3))
        self.wait(2)
        
        # Step 4: Compare both sides
        step4_title = Text("Step 4: Compare Both Sides", font_size=24, color=ORANGE)
        step4_title.next_to(step3_title, DOWN, buff=1.5)
        
        comparison = Text("13 = 13", font_size=32, color=GREEN)
        comparison.next_to(step4_title, DOWN, buff=0.5).shift(RIGHT*2)
        
        checkmark = Text("✓", font_size=48, color=GREEN)
        checkmark.next_to(comparison, RIGHT, buff=0.5)
        
        self.play(Write(step4_title))
        self.play(Write(comparison))
        self.play(Write(checkmark))
        self.wait(2)
        
        # Step 5: Conclusion
        step5_title = Text("Step 5: Conclusion", font_size=24, color=ORANGE)
        step5_title.next_to(step4_title, DOWN, buff=1.5)
        
        conclusion = Text("x = 5 IS a solution!", font_size=28, color=GREEN)
        conclusion.next_to(step5_title, DOWN, buff=0.5).shift(RIGHT*1.5)
        
        basketball_conclusion = Text("Curry played 5 quarters to score 13 points!", font_size=20, color=BLUE)
        basketball_conclusion.next_to(conclusion, DOWN, buff=0.3)
        
        self.play(Write(step5_title))
        self.play(Write(conclusion))
        self.play(Write(basketball_conclusion))
        
        # Final celebration
        big_checkmark = Text("✓", font_size=72, color=GREEN)
        big_checkmark.move_to(ORIGIN)
        
        self.play(FadeIn(big_checkmark, scale=2))
        self.play(big_checkmark.animate.scale(0.5))
        self.wait(1)
        self.play(FadeOut(big_checkmark))
        
        # Summary
        summary_title = Text("Key Takeaway", font_size=28, color=ORANGE)
        summary_title.to_edge(DOWN, buff=2)
        
        summary_text = Text("To verify a solution: substitute, calculate, and check if both sides are equal!", 
                           font_size=20, color=WHITE)
        summary_text.next_to(summary_title, DOWN, buff=0.3)
        
        self.play(Write(summary_title))
        self.play(Write(summary_text))
        self.wait(3)