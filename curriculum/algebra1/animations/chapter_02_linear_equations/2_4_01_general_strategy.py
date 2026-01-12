# 5-step general strategy for solving linear equations
# Generated for Chapter 2 - Section 2.4

from manim import *

class LinearEquationStrategyScene(Scene):
    def construct(self):
        # Title
        title = Text("5-Step Strategy for Solving Linear Equations", font_size=36, color=BLUE)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Create the 5 steps with icons
        steps = VGroup()
        
        # Step 1: SIMPLIFY
        step1_icon = Circle(radius=0.3, color=GREEN).set_fill(GREEN, opacity=0.3)
        step1_num = Text("1", font_size=20, color=WHITE).move_to(step1_icon.get_center())
        step1_title = Text("SIMPLIFY", font_size=24, color=GREEN, weight=BOLD)
        step1_desc = Text("Distribute and combine like terms", font_size=16)
        step1 = VGroup(step1_icon, step1_num, step1_title, step1_desc)
        step1.arrange(RIGHT, buff=0.3)
        step1_desc.next_to(step1_title, DOWN, aligned_edge=LEFT)
        
        # Step 2: COLLECT VARIABLES
        step2_icon = Circle(radius=0.3, color=YELLOW).set_fill(YELLOW, opacity=0.3)
        step2_num = Text("2", font_size=20, color=BLACK).move_to(step2_icon.get_center())
        step2_title = Text("COLLECT VARIABLES", font_size=24, color=YELLOW, weight=BOLD)
        step2_desc = Text("Get all variable terms on one side", font_size=16)
        step2 = VGroup(step2_icon, step2_num, step2_title, step2_desc)
        step2.arrange(RIGHT, buff=0.3)
        step2_desc.next_to(step2_title, DOWN, aligned_edge=LEFT)
        
        # Step 3: COLLECT CONSTANTS
        step3_icon = Circle(radius=0.3, color=ORANGE).set_fill(ORANGE, opacity=0.3)
        step3_num = Text("3", font_size=20, color=WHITE).move_to(step3_icon.get_center())
        step3_title = Text("COLLECT CONSTANTS", font_size=24, color=ORANGE, weight=BOLD)
        step3_desc = Text("Get all constants on the other side", font_size=16)
        step3 = VGroup(step3_icon, step3_num, step3_title, step3_desc)
        step3.arrange(RIGHT, buff=0.3)
        step3_desc.next_to(step3_title, DOWN, aligned_edge=LEFT)
        
        # Step 4: ISOLATE
        step4_icon = Circle(radius=0.3, color=RED).set_fill(RED, opacity=0.3)
        step4_num = Text("4", font_size=20, color=WHITE).move_to(step4_icon.get_center())
        step4_title = Text("ISOLATE", font_size=24, color=RED, weight=BOLD)
        step4_desc = Text("Divide or multiply to get variable alone", font_size=16)
        step4 = VGroup(step4_icon, step4_num, step4_title, step4_desc)
        step4.arrange(RIGHT, buff=0.3)
        step4_desc.next_to(step4_title, DOWN, aligned_edge=LEFT)
        
        # Step 5: CHECK
        step5_icon = Circle(radius=0.3, color=PURPLE).set_fill(PURPLE, opacity=0.3)
        step5_num = Text("5", font_size=20, color=WHITE).move_to(step5_icon.get_center())
        step5_title = Text("CHECK", font_size=24, color=PURPLE, weight=BOLD)
        step5_desc = Text("Substitute solution into original equation", font_size=16)
        step5 = VGroup(step5_icon, step5_num, step5_title, step5_desc)
        step5.arrange(RIGHT, buff=0.3)
        step5_desc.next_to(step5_title, DOWN, aligned_edge=LEFT)
        
        # Arrange all steps vertically
        steps = VGroup(step1, step2, step3, step4, step5)
        steps.arrange(DOWN, buff=0.8, aligned_edge=LEFT)
        steps.move_to(ORIGIN).shift(DOWN * 0.5)
        
        # Animate each step appearing
        for i, step in enumerate(steps):
            self.play(FadeIn(step))
            self.wait(0.5)
        
        self.wait(2)
        
        # Clear screen for example
        self.play(FadeOut(steps))
        
        # Example equation
        example_title = Text("Example: Solve 3(2x - 4) + 5 = 2x + 7", font_size=28, color=BLUE)
        example_title.to_edge(UP, buff=1)
        self.play(Write(example_title))
        
        # Step by step solution
        original = Text("3(2x - 4) + 5 = 2x + 7", font_size=24)
        original.move_to(UP * 2)
        self.play(Write(original))
        self.wait(1)
        
        # Step 1: Simplify
        step1_label = Text("Step 1: SIMPLIFY", font_size=20, color=GREEN).to_edge(LEFT, buff=1).shift(UP * 1)
        self.play(Write(step1_label))
        
        simplified = Text("6x - 12 + 5 = 2x + 7", font_size=24)
        simplified.next_to(original, DOWN, buff=0.5)
        self.play(Write(simplified))
        
        simplified2 = Text("6x - 7 = 2x + 7", font_size=24)
        simplified2.next_to(simplified, DOWN, buff=0.3)
        self.play(Write(simplified2))
        self.wait(1)
        
        # Step 2: Collect variables
        step2_label = Text("Step 2: COLLECT VARIABLES", font_size=20, color=YELLOW).to_edge(LEFT, buff=1)
        self.play(Transform(step1_label, step2_label))
        
        collect_vars = Text("6x - 2x = 7 + 7", font_size=24)
        collect_vars.next_to(simplified2, DOWN, buff=0.5)
        self.play(Write(collect_vars))
        
        collect_vars2 = Text("4x = 14", font_size=24)
        collect_vars2.next_to(collect_vars, DOWN, buff=0.3)
        self.play(Write(collect_vars2))
        self.wait(1)
        
        # Step 4: Isolate (combining steps 3 and 4)
        step4_label = Text("Step 4: ISOLATE", font_size=20, color=RED).to_edge(LEFT, buff=1)
        self.play(Transform(step1_label, step4_label))
        
        isolate = Text("x = 14/4 = 3.5", font_size=24)
        isolate.next_to(collect_vars2, DOWN, buff=0.5)
        self.play(Write(isolate))
        self.wait(1)
        
        # Step 5: Check
        step5_label = Text("Step 5: CHECK", font_size=20, color=PURPLE).to_edge(LEFT, buff=1)
        self.play(Transform(step1_label, step5_label))
        
        check = Text("3(2(3.5) - 4) + 5 = 2(3.5) + 7", font_size=20)
        check.next_to(isolate, DOWN, buff=0.5)
        self.play(Write(check))
        
        check_result = Text("10 = 10 ✓", font_size=24, color=GREEN)
        check_result.next_to(check, DOWN, buff=0.3)
        self.play(Write(check_result))
        self.wait(2)
        
        # Final message
        final_msg = Text("Remember: SIMPLIFY → COLLECT → ISOLATE → CHECK", 
                        font_size=24, color=BLUE, weight=BOLD)
        final_msg.to_edge(DOWN, buff=1)
        self.play(Write(final_msg))
        self.wait(3)