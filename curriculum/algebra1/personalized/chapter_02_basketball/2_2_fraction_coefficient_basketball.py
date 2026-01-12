# Solving equations with fraction coefficients using reciprocals - Basketball & NBA Edition
# Section 2.2

from manim import *

class BasketballFractionEquationsScene(Scene):
    def construct(self):
        # Title
        title = Text("Solving Equations with Fraction Coefficients", font_size=36, color=ORANGE)
        subtitle = Text("Using Basketball Stats & Reciprocals", font_size=24, color=WHITE)
        self.play(Write(title))
        self.wait(0.5)
        self.play(Write(subtitle.next_to(title, DOWN)))
        self.wait(1)
        self.play(title.animate.scale(0.7).to_edge(UP), FadeOut(subtitle))

        # Basketball scenario setup
        scenario = Text("Stephen Curry's Three-Point Challenge", font_size=28, color=ORANGE)
        scenario.move_to(UP * 2.5)
        self.play(Write(scenario))
        
        problem_text = Text("If Curry makes 2/3 of his three-point attempts,", font_size=20)
        problem_text2 = Text("and he scored 18 points from three-pointers,", font_size=20)
        problem_text3 = Text("how many shots did he attempt?", font_size=20)
        
        problem_group = VGroup(problem_text, problem_text2, problem_text3).arrange(DOWN, buff=0.3)
        problem_group.next_to(scenario, DOWN, buff=0.5)
        
        self.play(Write(problem_text))
        self.wait(0.5)
        self.play(Write(problem_text2))
        self.wait(0.5)
        self.play(Write(problem_text3))
        self.wait(1.5)

        # Set up the equation
        equation_setup = Text("Let x = number of three-point attempts", font_size=18, color=BLUE)
        equation_setup.next_to(problem_group, DOWN, buff=0.8)
        self.play(Write(equation_setup))
        self.wait(1)

        # Show the equation
        equation = Text("(2/3) × x = 18", font_size=32, color=WHITE)
        equation.next_to(equation_setup, DOWN, buff=0.5)
        self.play(Write(equation))
        self.wait(1)

        # Clear previous content
        self.play(FadeOut(scenario), FadeOut(problem_group), FadeOut(equation_setup))
        
        # Move equation to center
        self.play(equation.animate.move_to(UP * 1.5))

        # Explain the reciprocal concept
        reciprocal_title = Text("The Reciprocal Method", font_size=24, color=ORANGE)
        reciprocal_title.next_to(equation, DOWN, buff=0.8)
        self.play(Write(reciprocal_title))

        reciprocal_explain = Text("Multiply both sides by the reciprocal of 2/3", font_size=18)
        reciprocal_explain.next_to(reciprocal_title, DOWN, buff=0.3)
        self.play(Write(reciprocal_explain))

        # Show the reciprocal
        reciprocal_show = Text("Reciprocal of 2/3 is 3/2", font_size=20, color=YELLOW)
        reciprocal_show.next_to(reciprocal_explain, DOWN, buff=0.3)
        self.play(Write(reciprocal_show))
        self.wait(1.5)

        # Clear explanation text
        self.play(FadeOut(reciprocal_title), FadeOut(reciprocal_explain), FadeOut(reciprocal_show))

        # Step-by-step solution
        step1 = Text("Step 1: Multiply both sides by 3/2", font_size=18, color=BLUE)
        step1.move_to(UP * 0.5)
        self.play(Write(step1))

        equation_step1 = Text("(3/2) × (2/3) × x = 18 × (3/2)", font_size=24)
        equation_step1.next_to(step1, DOWN, buff=0.3)
        self.play(Write(equation_step1))
        self.wait(1.5)

        # Highlight the cancellation
        step2 = Text("Step 2: Simplify the left side", font_size=18, color=BLUE)
        step2.next_to(equation_step1, DOWN, buff=0.5)
        self.play(Write(step2))

        # Show cancellation
        cancel_text = Text("(3/2) × (2/3) = 1", font_size=20, color=GREEN)
        cancel_text.next_to(step2, DOWN, buff=0.3)
        self.play(Write(cancel_text))

        equation_step2 = Text("1 × x = 18 × (3/2)", font_size=24)
        equation_step2.next_to(cancel_text, DOWN, buff=0.3)
        self.play(Write(equation_step2))
        self.wait(1.5)

        # Final calculation
        step3 = Text("Step 3: Calculate the right side", font_size=18, color=BLUE)
        step3.next_to(equation_step2, DOWN, buff=0.5)
        self.play(Write(step3))

        calc_show = Text("18 × (3/2) = 18 × 1.5 = 27", font_size=20, color=GREEN)
        calc_show.next_to(step3, DOWN, buff=0.3)
        self.play(Write(calc_show))

        final_equation = Text("x = 27", font_size=28, color=ORANGE)
        final_equation.next_to(calc_show, DOWN, buff=0.3)
        self.play(Write(final_equation))
        self.wait(1.5)

        # Clear all steps
        self.play(FadeOut(step1), FadeOut(equation_step1), FadeOut(step2), 
                 FadeOut(cancel_text), FadeOut(equation_step2), FadeOut(step3), 
                 FadeOut(calc_show))

        # Move final answer up
        self.play(final_equation.animate.move_to(UP * 0.5))

        # Basketball interpretation
        interpretation = Text("Curry attempted 27 three-point shots!", font_size=24, color=ORANGE)
        interpretation.next_to(final_equation, DOWN, buff=0.8)
        self.play(Write(interpretation))

        # Verification
        verify_title = Text("Let's verify:", font_size=20, color=BLUE)
        verify_title.next_to(interpretation, DOWN, buff=0.5)
        self.play(Write(verify_title))

        verify_calc = Text("(2/3) × 27 = 18 ✓", font_size=18, color=GREEN)
        verify_calc.next_to(verify_title, DOWN, buff=0.2)
        self.play(Write(verify_calc))
        self.wait(1.5)

        # Key takeaway
        self.play(FadeOut(equation), FadeOut(final_equation), FadeOut(interpretation), 
                 FadeOut(verify_title), FadeOut(verify_calc))

        takeaway_title = Text("Key Strategy", font_size=28, color=ORANGE)
        takeaway_title.move_to(UP * 1)
        self.play(Write(takeaway_title))

        takeaway1 = Text("When solving (a/b)x = c:", font_size=20)
        takeaway2 = Text("Multiply both sides by b/a", font_size=20, color=YELLOW)
        takeaway3 = Text("The fractions cancel: (b/a) × (a/b) = 1", font_size=20)
        takeaway4 = Text("This isolates x immediately!", font_size=20, color=GREEN)

        takeaway_group = VGroup(takeaway1, takeaway2, takeaway3, takeaway4)
        takeaway_group.arrange(DOWN, buff=0.4)
        takeaway_group.next_to(takeaway_title, DOWN, buff=0.5)

        for takeaway in takeaway_group:
            self.play(Write(takeaway))
            self.wait(0.8)

        # Fun fact
        fun_fact = Text("Fun Fact: Curry's career 3-point percentage is about 42.6%!", 
                       font_size=16, color=ORANGE)
        fun_fact.to_edge(DOWN)
        self.play(Write(fun_fact))

        self.wait(3)