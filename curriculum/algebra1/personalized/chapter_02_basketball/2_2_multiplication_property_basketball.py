# Multiplication Property of Equality - Basketball & NBA Edition
# Section 2.2

from manim import *

class MultiplicationPropertyEqualityScene(Scene):
    def construct(self):
        # Title
        title = Text("Multiplication Property of Equality", font_size=36, color=ORANGE)
        subtitle = Text("Solving Basketball Stats with Multiplication", font_size=24, color=BLUE)
        
        self.play(Write(title))
        self.wait(1)
        self.play(Write(subtitle.next_to(title, DOWN, buff=0.3)))
        self.wait(1)
        
        # Move title up
        title_group = VGroup(title, subtitle)
        self.play(title_group.animate.scale(0.7).to_edge(UP))
        
        # Basketball scenario setup
        scenario = Text("Stephen Curry's 3-Point Challenge", font_size=28, color=ORANGE)
        self.play(Write(scenario))
        self.wait(1)
        
        problem_text = Text("Curry makes n three-pointers in 6 games", font_size=20)
        problem_text2 = Text("His total is 90 points from three-pointers", font_size=20)
        problem_text3 = Text("How many three-pointers per game?", font_size=20, color=YELLOW)
        
        problem_group = VGroup(problem_text, problem_text2, problem_text3).arrange(DOWN, buff=0.3)
        problem_group.next_to(scenario, DOWN, buff=0.5)
        
        self.play(Write(problem_text))
        self.wait(1)
        self.play(Write(problem_text2))
        self.wait(1)
        self.play(Write(problem_text3))
        self.wait(2)
        
        # Clear and show equation
        self.play(FadeOut(scenario), FadeOut(problem_group))
        
        # Original equation
        equation_label = Text("Setting up the equation:", font_size=24, color=BLUE)
        equation_label.to_edge(LEFT).shift(UP*2)
        self.play(Write(equation_label))
        
        # n/6 = 15 explanation
        explanation = Text("n ÷ 6 = 15", font_size=32)
        explanation.next_to(equation_label, DOWN, buff=0.5).shift(RIGHT*2)
        self.play(Write(explanation))
        self.wait(1)
        
        # Show what each part means
        n_meaning = Text("n = three-pointers per game", font_size=18, color=GREEN)
        six_meaning = Text("6 = number of games", font_size=18, color=GREEN)
        fifteen_meaning = Text("15 = total three-pointers made", font_size=18, color=GREEN)
        
        meanings = VGroup(n_meaning, six_meaning, fifteen_meaning).arrange(DOWN, buff=0.2)
        meanings.next_to(explanation, DOWN, buff=0.8)
        
        self.play(Write(n_meaning))
        self.wait(0.5)
        self.play(Write(six_meaning))
        self.wait(0.5)
        self.play(Write(fifteen_meaning))
        self.wait(2)
        
        # Clear explanations
        self.play(FadeOut(meanings))
        
        # Show multiplication property
        property_title = Text("Multiplication Property of Equality:", font_size=24, color=ORANGE)
        property_title.move_to(UP*1.5)
        
        property_rule = Text("If we multiply both sides by the same number,", font_size=20)
        property_rule2 = Text("the equation stays balanced!", font_size=20, color=YELLOW)
        
        property_group = VGroup(property_rule, property_rule2).arrange(DOWN, buff=0.2)
        property_group.next_to(property_title, DOWN, buff=0.3)
        
        self.play(ReplacementTransform(equation_label, property_title))
        self.play(Write(property_rule))
        self.play(Write(property_rule2))
        self.wait(2)
        
        # Move equation and show solution steps
        self.play(explanation.animate.move_to(UP*0.5))
        self.play(FadeOut(property_title), FadeOut(property_group))
        
        # Step 1: Original equation
        step1 = Text("Step 1: Original equation", font_size=20, color=BLUE)
        eq1 = Text("n/6 = 15", font_size=28)
        
        step1.move_to(LEFT*3 + UP*0.5)
        eq1.next_to(step1, RIGHT, buff=1)
        
        self.play(ReplacementTransform(explanation, eq1))
        self.play(Write(step1))
        self.wait(1)
        
        # Step 2: Multiply both sides by 6
        step2 = Text("Step 2: Multiply both sides by 6", font_size=20, color=BLUE)
        eq2_left = Text("6 × (n/6)", font_size=28, color=RED)
        eq2_equals = Text("=", font_size=28)
        eq2_right = Text("6 × 15", font_size=28, color=RED)
        
        step2.next_to(step1, DOWN, buff=0.8)
        eq2 = VGroup(eq2_left, eq2_equals, eq2_right).arrange(RIGHT, buff=0.3)
        eq2.next_to(step2, RIGHT, buff=1)
        
        self.play(Write(step2))
        self.play(Write(eq2))
        self.wait(2)
        
        # Highlight the multiplication
        self.play(Indicate(eq2_left), Indicate(eq2_right))
        self.wait(1)
        
        # Step 3: Simplify
        step3 = Text("Step 3: Simplify", font_size=20, color=BLUE)
        eq3_left = Text("n", font_size=28, color=GREEN)
        eq3_equals = Text("=", font_size=28)
        eq3_right = Text("90", font_size=28, color=GREEN)
        
        step3.next_to(step2, DOWN, buff=0.8)
        eq3 = VGroup(eq3_left, eq3_equals, eq3_right).arrange(RIGHT, buff=0.3)
        eq3.next_to(step3, RIGHT, buff=1)
        
        self.play(Write(step3))
        self.play(Write(eq3))
        self.wait(1)
        
        # Show simplification process
        simplify1 = Text("6 × (n/6) = n", font_size=18, color=YELLOW)
        simplify2 = Text("6 × 15 = 90", font_size=18, color=YELLOW)
        
        simplify_group = VGroup(simplify1, simplify2).arrange(DOWN, buff=0.2)
        simplify_group.next_to(eq3, RIGHT, buff=1)
        
        self.play(Write(simplify1))
        self.play(Write(simplify2))
        self.wait(2)
        
        # Clear and show answer
        self.play(FadeOut(VGroup(step1, step2, step3, eq1, eq2, eq3, simplify_group)))
        
        # Final answer
        answer_title = Text("Answer:", font_size=32, color=ORANGE)
        answer_text = Text("Curry makes 90 three-pointers per game", font_size=24, color=GREEN)
        
        answer_group = VGroup(answer_title, answer_text).arrange(DOWN, buff=0.5)
        answer_group.move_to(ORIGIN)
        
        self.play(Write(answer_title))
        self.play(Write(answer_text))
        self.wait(1)
        
        # Fun fact
        fun_fact = Text("Fun Fact: Curry's actual record is 16 three-pointers", font_size=18, color=YELLOW)
        fun_fact2 = Text("in a single game (2016 vs OKC)!", font_size=18, color=YELLOW)
        
        fact_group = VGroup(fun_fact, fun_fact2).arrange(DOWN, buff=0.1)
        fact_group.next_to(answer_group, DOWN, buff=0.8)
        
        self.play(Write(fun_fact))
        self.play(Write(fun_fact2))
        self.wait(2)
        
        # Key takeaway
        takeaway = Text("Key Takeaway: Multiply both sides by the same number", font_size=20, color=BLUE)
        takeaway2 = Text("to maintain equality and solve for the variable!", font_size=20, color=BLUE)
        
        takeaway_group = VGroup(takeaway, takeaway2).arrange(DOWN, buff=0.2)
        takeaway_group.to_edge(DOWN, buff=1)
        
        self.play(Write(takeaway))
        self.play(Write(takeaway2))
        self.wait(3)