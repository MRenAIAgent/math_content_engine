# Solving equations by combining like terms first
# Generated for Chapter 2 - Section 2.1

from manim import *

class SolvingEquationsByLikeTermsScene(Scene):
    def construct(self):
        # Title
        title = Text("Solving Equations by Combining Like Terms", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Step 1: Show original equation
        step1_text = Text("Step 1: Original Equation", font_size=24).to_edge(LEFT).shift(UP*2)
        self.play(Write(step1_text))
        
        # Create equation with color coding
        eq_parts = [
            Text("9x", color=BLUE, font_size=32),
            Text(" - ", color=WHITE, font_size=32),
            Text("5", color=ORANGE, font_size=32),
            Text(" - ", color=WHITE, font_size=32),
            Text("8x", color=BLUE, font_size=32),
            Text(" - ", color=WHITE, font_size=32),
            Text("6", color=ORANGE, font_size=32),
            Text(" = ", color=WHITE, font_size=32),
            Text("7", color=ORANGE, font_size=32)
        ]
        
        equation = VGroup(*eq_parts).arrange(RIGHT, buff=0.1).shift(UP*1.5)
        self.play(Write(equation))
        self.wait(2)

        # Step 2: Identify like terms with arrows
        step2_text = Text("Step 2: Identify Like Terms", font_size=24).to_edge(LEFT).shift(UP*0.5)
        self.play(Write(step2_text))
        
        # Arrows for variable terms
        var_arrow1 = CurvedArrow(
            eq_parts[0].get_bottom() + DOWN*0.2,
            eq_parts[4].get_bottom() + DOWN*0.2,
            color=BLUE,
            angle=-PI/4
        )
        var_label = Text("Variable terms", color=BLUE, font_size=20).next_to(var_arrow1, DOWN)
        
        # Arrows for constant terms
        const_arrow1 = CurvedArrow(
            eq_parts[2].get_top() + UP*0.2,
            eq_parts[6].get_top() + UP*0.2,
            color=ORANGE,
            angle=PI/4
        )
        const_label = Text("Constant terms", color=ORANGE, font_size=20).next_to(const_arrow1, UP)
        
        self.play(Create(var_arrow1), Write(var_label))
        self.play(Create(const_arrow1), Write(const_label))
        self.wait(2)

        # Step 3: Combine like terms
        step3_text = Text("Step 3: Combine Like Terms", font_size=24).to_edge(LEFT).shift(DOWN*0.5)
        self.play(Write(step3_text))
        
        # Show combination process
        combine_text1 = Text("9x - 8x = 1x = x", color=BLUE, font_size=24).shift(DOWN*1)
        combine_text2 = Text("-5 - 6 = -11", color=ORANGE, font_size=24).next_to(combine_text1, DOWN)
        
        self.play(Write(combine_text1))
        self.play(Write(combine_text2))
        self.wait(1)
        
        # New simplified equation
        new_eq_parts = [
            Text("x", color=BLUE, font_size=32),
            Text(" - ", color=WHITE, font_size=32),
            Text("11", color=ORANGE, font_size=32),
            Text(" = ", color=WHITE, font_size=32),
            Text("7", color=ORANGE, font_size=32)
        ]
        
        new_equation = VGroup(*new_eq_parts).arrange(RIGHT, buff=0.1).shift(DOWN*2.5)
        self.play(Write(new_equation))
        self.wait(2)

        # Clear intermediate steps
        self.play(
            FadeOut(equation),
            FadeOut(var_arrow1), FadeOut(var_label),
            FadeOut(const_arrow1), FadeOut(const_label),
            FadeOut(combine_text1), FadeOut(combine_text2)
        )
        
        # Move simplified equation up
        self.play(new_equation.animate.shift(UP*3.5))

        # Step 4: Solve for x
        step4_text = Text("Step 4: Add 11 to Both Sides", font_size=24).to_edge(LEFT).shift(UP*0.5)
        self.play(Write(step4_text))
        
        # Show adding 11
        add_text = Text("x - 11 + 11 = 7 + 11", font_size=28).shift(DOWN*0.5)
        self.play(Write(add_text))
        self.wait(1)
        
        # Final answer
        final_eq_parts = [
            Text("x", color=BLUE, font_size=32),
            Text(" = ", color=WHITE, font_size=32),
            Text("18", color=GREEN, font_size=32)
        ]
        
        final_equation = VGroup(*final_eq_parts).arrange(RIGHT, buff=0.1).shift(DOWN*1.5)
        self.play(Write(final_equation))
        
        # Highlight the answer
        answer_box = SurroundingRectangle(final_equation, color=GREEN, buff=0.2)
        self.play(Create(answer_box))
        self.wait(2)

        # Step 5: Verify solution
        step5_text = Text("Step 5: Verify Solution", font_size=24).to_edge(LEFT).shift(DOWN*2.5)
        self.play(Write(step5_text))
        
        verify_text = Text("9(18) - 5 - 8(18) - 6 = 162 - 5 - 144 - 6 = 7 ✓", font_size=24, color=GREEN).shift(DOWN*3.2)
        self.play(Write(verify_text))
        self.wait(2)

        # Summary
        summary = Text("Key Steps: Identify → Combine → Solve → Verify", font_size=28, color=YELLOW).shift(DOWN*4)
        self.play(Write(summary))
        self.wait(3)