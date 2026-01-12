# Applying general strategy to complex equation
# Generated for Chapter 2 - Section 2.4

from manim import *

class ComplexEquationSolvingScene(Scene):
    def construct(self):
        # Title
        title = Text("Solving Complex Equations: 5-Step Method", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Original equation
        original_eq = Text("5(2x - 1) - 3(x + 4) = 2x - 7", font_size=32)
        self.play(Write(original_eq))
        self.wait(1)
        self.play(original_eq.animate.shift(UP * 2))

        # Step 1: SIMPLIFY
        step1_title = Text("STEP 1: SIMPLIFY", color=RED, font_size=28).to_edge(LEFT)
        self.play(Write(step1_title))
        
        distribute = Text("Distribute:", font_size=24, color=RED).next_to(step1_title, DOWN, aligned_edge=LEFT)
        self.play(Write(distribute))
        
        distributed = Text("10x - 5 - 3x - 12 = 2x - 7", font_size=28, color=RED).next_to(distribute, DOWN, aligned_edge=LEFT)
        self.play(Write(distributed))
        self.wait(1)
        
        combine = Text("Combine like terms:", font_size=24, color=RED).next_to(distributed, DOWN, aligned_edge=LEFT)
        self.play(Write(combine))
        
        simplified = Text("7x - 17 = 2x - 7", font_size=28, color=RED).next_to(combine, DOWN, aligned_edge=LEFT)
        self.play(Write(simplified))
        self.wait(2)
        
        # Clear step 1
        self.play(FadeOut(step1_title), FadeOut(distribute), FadeOut(distributed), FadeOut(combine))
        self.play(simplified.animate.move_to(ORIGIN).shift(UP))

        # Step 2: COLLECT VARIABLES
        step2_title = Text("STEP 2: COLLECT VARIABLES", color=BLUE, font_size=28).to_edge(LEFT)
        self.play(Write(step2_title))
        
        subtract_2x = Text("Subtract 2x from both sides:", font_size=24, color=BLUE).next_to(step2_title, DOWN, aligned_edge=LEFT)
        self.play(Write(subtract_2x))
        
        variables_collected = Text("5x - 17 = -7", font_size=28, color=BLUE).next_to(subtract_2x, DOWN, aligned_edge=LEFT)
        self.play(Write(variables_collected))
        self.wait(2)
        
        # Clear step 2
        self.play(FadeOut(step2_title), FadeOut(subtract_2x), FadeOut(simplified))
        self.play(variables_collected.animate.move_to(ORIGIN).shift(UP))

        # Step 3: COLLECT CONSTANTS
        step3_title = Text("STEP 3: COLLECT CONSTANTS", color=GREEN, font_size=28).to_edge(LEFT)
        self.play(Write(step3_title))
        
        add_17 = Text("Add 17 to both sides:", font_size=24, color=GREEN).next_to(step3_title, DOWN, aligned_edge=LEFT)
        self.play(Write(add_17))
        
        constants_collected = Text("5x = 10", font_size=28, color=GREEN).next_to(add_17, DOWN, aligned_edge=LEFT)
        self.play(Write(constants_collected))
        self.wait(2)
        
        # Clear step 3
        self.play(FadeOut(step3_title), FadeOut(add_17), FadeOut(variables_collected))
        self.play(constants_collected.animate.move_to(ORIGIN).shift(UP))

        # Step 4: ISOLATE
        step4_title = Text("STEP 4: ISOLATE", color=YELLOW, font_size=28).to_edge(LEFT)
        self.play(Write(step4_title))
        
        divide_5 = Text("Divide both sides by 5:", font_size=24, color=YELLOW).next_to(step4_title, DOWN, aligned_edge=LEFT)
        self.play(Write(divide_5))
        
        solution = Text("x = 2", font_size=32, color=YELLOW).next_to(divide_5, DOWN, aligned_edge=LEFT)
        self.play(Write(solution))
        self.wait(2)
        
        # Clear step 4
        self.play(FadeOut(step4_title), FadeOut(divide_5), FadeOut(constants_collected))
        self.play(solution.animate.move_to(ORIGIN))

        # Step 5: CHECK
        step5_title = Text("STEP 5: CHECK", color=PURPLE, font_size=28).to_edge(LEFT)
        self.play(Write(step5_title))
        
        substitute = Text("Substitute x = 2 into original equation:", font_size=24, color=PURPLE).next_to(step5_title, DOWN, aligned_edge=LEFT)
        self.play(Write(substitute))
        
        check_left = Text("Left side: 5(2(2) - 1) - 3(2 + 4) = 5(3) - 3(6) = 15 - 18 = -3", font_size=20, color=PURPLE).next_to(substitute, DOWN, aligned_edge=LEFT)
        self.play(Write(check_left))
        
        check_right = Text("Right side: 2(2) - 7 = 4 - 7 = -3", font_size=20, color=PURPLE).next_to(check_left, DOWN, aligned_edge=LEFT)
        self.play(Write(check_right))
        
        verified = Text("✓ Solution verified!", font_size=24, color=PURPLE).next_to(check_right, DOWN, aligned_edge=LEFT)
        self.play(Write(verified))
        self.wait(2)

        # Final answer highlight
        self.play(FadeOut(step5_title), FadeOut(substitute), FadeOut(check_left), FadeOut(check_right), FadeOut(verified))
        self.play(solution.animate.scale(1.5).set_color(WHITE))
        
        final_text = Text("Final Answer: x = 2", font_size=36, color=WHITE).next_to(solution, DOWN, buff=1)
        self.play(Write(final_text))
        
        self.wait(3)