# Division Property of Equality for solving equations - Basketball & NBA Edition
# Section 2.2

from manim import *

class BasketballDivisionPropertyScene(Scene):
    def construct(self):
        # Title
        title = Text("Division Property of Equality", font_size=48, color=ORANGE).scale(0.8)
        subtitle = Text("Solving Basketball Equations", font_size=36, color=BLUE)
        self.play(Write(title))
        self.wait(1)
        self.play(Write(subtitle.next_to(title, DOWN)))
        self.wait(1)
        self.play(title.animate.to_edge(UP), subtitle.animate.to_edge(UP).shift(DOWN*0.5))
        
        # Setup basketball scenario
        scenario = Text("Stephen Curry scored 7 three-pointers in a game", font_size=32, color=WHITE)
        scenario2 = Text("His total points from three-pointers was 91", font_size=32, color=WHITE)
        scenario3 = Text("Wait... that doesn't seem right! Let's solve:", font_size=32, color=YELLOW)
        
        self.play(Write(scenario))
        self.wait(1)
        self.play(scenario.animate.shift(UP*0.5))
        self.play(Write(scenario2.next_to(scenario, DOWN)))
        self.wait(1)
        self.play(Write(scenario3.next_to(scenario2, DOWN*2)))
        self.wait(2)
        
        self.play(FadeOut(scenario), FadeOut(scenario2), FadeOut(scenario3))
        
        # Show the equation
        equation_text = Text("If Curry made x three-pointers, and each is worth 3 points:", font_size=28)
        equation_text.next_to(title, DOWN*2)
        self.play(Write(equation_text))
        self.wait(1)
        
        # Main equation
        equation = Text("3x = 91", font_size=48, color=ORANGE)
        equation.move_to(ORIGIN)
        self.play(Write(equation))
        self.wait(1)
        
        # Show balance concept
        balance_text = Text("Like a balanced scoreboard - both sides must be equal", font_size=24, color=BLUE)
        balance_text.next_to(equation, DOWN*2)
        self.play(Write(balance_text))
        self.wait(2)
        
        # Division property explanation
        self.play(FadeOut(equation_text), FadeOut(balance_text))
        
        property_text = Text("Division Property of Equality:", font_size=32, color=YELLOW)
        property_text.next_to(equation, UP*2)
        property_rule = Text("If we divide both sides by the same number, equality is maintained", font_size=24)
        property_rule.next_to(property_text, DOWN*0.8)
        
        self.play(Write(property_text))
        self.play(Write(property_rule))
        self.wait(2)
        
        # Show division step
        division_text = Text("Divide both sides by 3:", font_size=32, color=GREEN)
        division_text.next_to(equation, DOWN*1.5)
        self.play(Write(division_text))
        self.wait(1)
        
        # Show the division visually
        left_side = Text("3x", font_size=48, color=ORANGE)
        division_line1 = Line(ORIGIN, RIGHT*0.8, color=WHITE)
        three1 = Text("3", font_size=32, color=WHITE)
        
        equals = Text("=", font_size=48, color=WHITE)
        
        right_side = Text("91", font_size=48, color=ORANGE)
        division_line2 = Line(ORIGIN, RIGHT*0.8, color=WHITE)
        three2 = Text("3", font_size=32, color=WHITE)
        
        # Position elements
        left_side.move_to(LEFT*2.5 + UP*0.3)
        division_line1.next_to(left_side, DOWN*0.3)
        three1.next_to(division_line1, DOWN*0.3)
        
        equals.move_to(ORIGIN)
        
        right_side.move_to(RIGHT*2.5 + UP*0.3)
        division_line2.next_to(right_side, DOWN*0.3)
        three2.next_to(division_line2, DOWN*0.3)
        
        # Transform equation to division form
        self.play(
            ReplacementTransform(equation, VGroup(left_side, equals, right_side)),
            Write(division_line1),
            Write(three1),
            Write(division_line2),
            Write(three2)
        )
        self.wait(2)
        
        # Show cancellation on left side
        cancel_left = Text("x", font_size=48, color=GREEN)
        cancel_left.move_to(left_side.get_center())
        
        cancel_right = Text("30.33...", font_size=32, color=RED)
        cancel_right.move_to(right_side.get_center())
        
        self.play(
            ReplacementTransform(VGroup(left_side, division_line1, three1), cancel_left),
            ReplacementTransform(VGroup(right_side, division_line2, three2), cancel_right)
        )
        self.wait(1)
        
        # Correct the calculation
        correct_calc = Text("91 ÷ 3 = 30.33...", font_size=32, color=YELLOW)
        correct_calc.next_to(equals, DOWN*2)
        self.play(Write(correct_calc))
        self.wait(1)
        
        # Show this doesn't make sense
        reality_check = Text("But you can't score 30.33 three-pointers!", font_size=28, color=RED)
        reality_check.next_to(correct_calc, DOWN)
        self.play(Write(reality_check))
        self.wait(1)
        
        # Clear and show corrected problem
        self.play(FadeOut(VGroup(cancel_left, equals, cancel_right, correct_calc, reality_check, 
                                property_text, property_rule, division_text)))
        
        # Corrected scenario
        correct_text = Text("Let's fix the problem: Curry scored 21 points from three-pointers", font_size=28, color=BLUE)
        correct_text.move_to(UP*2)
        self.play(Write(correct_text))
        
        # New equation
        new_equation = Text("3x = 21", font_size=48, color=ORANGE)
        new_equation.move_to(ORIGIN)
        self.play(Write(new_equation))
        self.wait(1)
        
        # Division step
        div_text2 = Text("Divide both sides by 3:", font_size=32, color=GREEN)
        div_text2.next_to(new_equation, DOWN*1.5)
        self.play(Write(div_text2))
        
        # Final answer
        final_equation = Text("x = 7", font_size=48, color=GREEN)
        final_equation.next_to(new_equation, DOWN*3)
        self.play(Write(final_equation))
        self.wait(1)
        
        # Basketball conclusion
        conclusion = Text("Curry made 7 three-pointers! 🏀", font_size=32, color=YELLOW)
        conclusion.next_to(final_equation, DOWN*1.5)
        self.play(Write(conclusion))
        self.wait(1)
        
        # Key takeaway
        takeaway = Text("Division Property: Divide both sides by the same non-zero number", font_size=24, color=WHITE)
        takeaway.to_edge(DOWN)
        self.play(Write(takeaway))
        
        self.wait(3)