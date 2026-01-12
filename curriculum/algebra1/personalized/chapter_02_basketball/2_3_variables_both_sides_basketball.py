# Solving equations with variables on both sides - Basketball & NBA Edition
# Section 2.3

from manim import *

class BasketballEquationScene(Scene):
    def construct(self):
        # Title
        title = Text("Solving Basketball Stats: Variables on Both Sides", font_size=36, color=ORANGE)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Basketball scenario setup
        scenario = Text("Stephen Curry and Luka Dončić scoring comparison:", font_size=28, color=WHITE)
        scenario.next_to(title, DOWN, buff=0.5)
        self.play(Write(scenario))
        self.wait(1)

        # Problem setup
        problem_text = Text("Curry: 5 three-pointers + 8 free throws", font_size=24, color=BLUE)
        problem_text2 = Text("Luka: 3 three-pointers + 14 free throws", font_size=24, color=RED)
        problem_text3 = Text("When do they score the same points?", font_size=24, color=YELLOW)
        
        problem_text.next_to(scenario, DOWN, buff=0.5)
        problem_text2.next_to(problem_text, DOWN, buff=0.3)
        problem_text3.next_to(problem_text2, DOWN, buff=0.3)
        
        self.play(Write(problem_text))
        self.play(Write(problem_text2))
        self.play(Write(problem_text3))
        self.wait(2)

        # Clear and show equation
        self.play(FadeOut(scenario, problem_text, problem_text2, problem_text3))
        
        # Original equation
        equation = Text("5x + 8 = 3x + 14", font_size=48, color=WHITE)
        equation.move_to(ORIGIN + UP)
        
        curry_label = Text("Curry's points", font_size=20, color=BLUE)
        curry_label.next_to(equation, LEFT, buff=1)
        
        luka_label = Text("Luka's points", font_size=20, color=RED)
        luka_label.next_to(equation, RIGHT, buff=1)
        
        self.play(Write(equation))
        self.play(Write(curry_label), Write(luka_label))
        self.wait(2)

        # Step 1: Subtract 3x from both sides
        step1_text = Text("Step 1: Move all x terms to one side", font_size=24, color=YELLOW)
        step1_text.next_to(equation, DOWN, buff=1)
        self.play(Write(step1_text))
        
        # Show subtraction
        subtract_3x = Text("- 3x", font_size=36, color=GREEN)
        subtract_3x_left = subtract_3x.copy().next_to(equation, DOWN + LEFT, buff=0.5)
        subtract_3x_right = subtract_3x.copy().next_to(equation, DOWN + RIGHT, buff=0.5)
        
        self.play(Write(subtract_3x_left), Write(subtract_3x_right))
        self.wait(1)

        # Arrow animations
        arrow_left = Arrow(subtract_3x_left.get_center(), equation.get_left() + DOWN*0.3, color=GREEN)
        arrow_right = Arrow(subtract_3x_right.get_center(), equation.get_right() + DOWN*0.3, color=GREEN)
        
        self.play(Create(arrow_left), Create(arrow_right))
        self.wait(1)

        # New equation after step 1
        equation2 = Text("2x + 8 = 14", font_size=48, color=WHITE)
        equation2.next_to(step1_text, DOWN, buff=0.5)
        
        self.play(Transform(equation, equation2))
        self.play(FadeOut(subtract_3x_left, subtract_3x_right, arrow_left, arrow_right, curry_label, luka_label))
        self.wait(1)

        # Step 2: Subtract 8 from both sides
        step2_text = Text("Step 2: Move constants to the other side", font_size=24, color=YELLOW)
        step2_text.next_to(equation2, DOWN, buff=1)
        self.play(Write(step2_text))
        
        # Show subtraction of 8
        subtract_8 = Text("- 8", font_size=36, color=ORANGE)
        subtract_8_left = subtract_8.copy().next_to(equation2, DOWN + LEFT, buff=0.5)
        subtract_8_right = subtract_8.copy().next_to(equation2, DOWN + RIGHT, buff=0.5)
        
        self.play(Write(subtract_8_left), Write(subtract_8_right))
        self.wait(1)

        # Arrow animations for step 2
        arrow2_left = Arrow(subtract_8_left.get_center(), equation2.get_left() + DOWN*0.3, color=ORANGE)
        arrow2_right = Arrow(subtract_8_right.get_center(), equation2.get_right() + DOWN*0.3, color=ORANGE)
        
        self.play(Create(arrow2_left), Create(arrow2_right))
        self.wait(1)

        # New equation after step 2
        equation3 = Text("2x = 6", font_size=48, color=WHITE)
        equation3.next_to(step2_text, DOWN, buff=0.5)
        
        self.play(Transform(equation, equation3))
        self.play(FadeOut(subtract_8_left, subtract_8_right, arrow2_left, arrow2_right))
        self.wait(1)

        # Step 3: Divide by 2
        step3_text = Text("Step 3: Divide both sides by 2", font_size=24, color=YELLOW)
        step3_text.next_to(equation3, DOWN, buff=1)
        self.play(Write(step3_text))
        
        # Final answer
        final_equation = Text("x = 3", font_size=56, color=GREEN)
        final_equation.next_to(step3_text, DOWN, buff=0.5)
        
        self.play(Transform(equation, final_equation))
        self.wait(1)

        # Basketball interpretation
        interpretation = Text("Answer: Both players score the same with 3 three-pointers!", 
                            font_size=24, color=YELLOW)
        interpretation.next_to(final_equation, DOWN, buff=0.5)
        
        verification = Text("Check: Curry = 5(3) + 8 = 23 points", font_size=20, color=BLUE)
        verification2 = Text("Luka = 3(3) + 14 = 23 points ✓", font_size=20, color=RED)
        
        verification.next_to(interpretation, DOWN, buff=0.3)
        verification2.next_to(verification, DOWN, buff=0.2)
        
        self.play(Write(interpretation))
        self.wait(1)
        self.play(Write(verification))
        self.play(Write(verification2))
        self.wait(2)

        # Key takeaway
        self.play(FadeOut(step1_text, step2_text, step3_text, interpretation, verification, verification2))
        
        takeaway = Text("Key Strategy: Balance the equation like a basketball scoreboard!", 
                       font_size=28, color=ORANGE)
        takeaway.move_to(ORIGIN + DOWN)
        
        self.play(Write(takeaway))
        self.wait(3)