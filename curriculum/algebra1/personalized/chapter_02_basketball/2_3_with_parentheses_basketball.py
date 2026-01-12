# Solving equations with parentheses using distributive property - Basketball & NBA Edition
# Section 2.3

from manim import *

class BasketballDistributivePropertyScene(Scene):
    def construct(self):
        # Title
        title = Text("Solving Equations with Parentheses", font_size=36, color=ORANGE)
        subtitle = Text("Using the Distributive Property", font_size=28, color=WHITE)
        basketball_theme = Text("🏀 NBA Scoring Edition 🏀", font_size=24, color=BLUE)
        
        self.play(Write(title))
        self.wait(0.5)
        self.play(Write(subtitle.next_to(title, DOWN)))
        self.play(Write(basketball_theme.next_to(subtitle, DOWN)))
        self.wait(1)
        
        # Move title up
        title_group = VGroup(title, subtitle, basketball_theme)
        self.play(title_group.animate.scale(0.7).to_edge(UP))
        
        # Basketball scenario setup
        scenario = Text("Stephen Curry's Scoring Challenge", font_size=32, color=ORANGE)
        self.play(Write(scenario))
        self.wait(1)
        
        story = Text("Curry scores 3 points per three-pointer, minus 5 penalty points per game", 
                    font_size=24, color=WHITE)
        story2 = Text("His total equals 4 points per assist plus 7 bonus points", 
                     font_size=24, color=WHITE)
        
        self.play(Write(story.next_to(scenario, DOWN, buff=0.5)))
        self.play(Write(story2.next_to(story, DOWN, buff=0.3)))
        self.wait(2)
        
        # Clear and show equation
        self.play(FadeOut(scenario), FadeOut(story), FadeOut(story2))
        
        # Original equation
        equation_label = Text("Find x (number of three-pointers/assists):", 
                             font_size=24, color=YELLOW)
        original_eq = Text("3(2x - 5) = 4x + 7", font_size=36, color=WHITE)
        
        self.play(Write(equation_label))
        self.play(Write(original_eq.next_to(equation_label, DOWN, buff=0.5)))
        self.wait(1)
        
        # Move equation up
        eq_group = VGroup(equation_label, original_eq)
        self.play(eq_group.animate.to_edge(LEFT).shift(UP*2))
        
        # Step 1: Distributive Property
        step1_title = Text("Step 1: Use Distributive Property", font_size=28, color=ORANGE)
        step1_title.next_to(eq_group, DOWN, buff=1)
        self.play(Write(step1_title))
        
        # Show distribution visually
        distribute_text = Text("3(2x - 5) = 3·2x - 3·5", font_size=32, color=BLUE)
        distribute_text.next_to(step1_title, DOWN, buff=0.5)
        self.play(Write(distribute_text))
        self.wait(1)
        
        # Result of distribution
        distributed = Text("6x - 15 = 4x + 7", font_size=36, color=GREEN)
        distributed.next_to(distribute_text, DOWN, buff=0.5)
        self.play(Write(distributed))
        self.wait(1)
        
        # Highlight the distributed equation
        box1 = SurroundingRectangle(distributed, color=GREEN, buff=0.2)
        self.play(Create(box1))
        self.wait(1)
        
        # Step 2: Solve for x
        step2_title = Text("Step 2: Solve for x", font_size=28, color=ORANGE)
        step2_title.next_to(distributed, DOWN, buff=1)
        self.play(Write(step2_title))
        
        # Subtract 4x from both sides
        subtract_step = Text("6x - 4x - 15 = 4x - 4x + 7", font_size=28, color=BLUE)
        subtract_step.next_to(step2_title, DOWN, buff=0.3)
        self.play(Write(subtract_step))
        
        simplified1 = Text("2x - 15 = 7", font_size=32, color=WHITE)
        simplified1.next_to(subtract_step, DOWN, buff=0.3)
        self.play(Write(simplified1))
        self.wait(1)
        
        # Add 15 to both sides
        add_step = Text("2x - 15 + 15 = 7 + 15", font_size=28, color=BLUE)
        add_step.next_to(simplified1, DOWN, buff=0.3)
        self.play(Write(add_step))
        
        simplified2 = Text("2x = 22", font_size=32, color=WHITE)
        simplified2.next_to(add_step, DOWN, buff=0.3)
        self.play(Write(simplified2))
        self.wait(1)
        
        # Divide by 2
        divide_step = Text("x = 22 ÷ 2 = 11", font_size=32, color=RED)
        divide_step.next_to(simplified2, DOWN, buff=0.5)
        self.play(Write(divide_step))
        
        # Highlight answer
        answer_box = SurroundingRectangle(divide_step, color=RED, buff=0.3)
        self.play(Create(answer_box))
        self.wait(1)
        
        # Clear for verification
        self.play(FadeOut(VGroup(step1_title, distribute_text, step2_title, 
                                subtract_step, add_step, simplified1, simplified2, box1)))
        
        # Verification
        verify_title = Text("Step 3: Check Our Answer", font_size=28, color=ORANGE)
        verify_title.next_to(distributed, DOWN, buff=0.5)
        self.play(Write(verify_title))
        
        check_left = Text("Left side: 3(2(11) - 5) = 3(22 - 5) = 3(17) = 51", 
                         font_size=24, color=BLUE)
        check_right = Text("Right side: 4(11) + 7 = 44 + 7 = 51", 
                          font_size=24, color=BLUE)
        
        check_left.next_to(verify_title, DOWN, buff=0.3)
        check_right.next_to(check_left, DOWN, buff=0.3)
        
        self.play(Write(check_left))
        self.play(Write(check_right))
        
        checkmark = Text("✓ 51 = 51 ✓", font_size=32, color=GREEN)
        checkmark.next_to(check_right, DOWN, buff=0.3)
        self.play(Write(checkmark))
        self.wait(1)
        
        # Basketball interpretation
        interpretation = Text("Curry needs 11 three-pointers to balance the equation!", 
                            font_size=28, color=ORANGE)
        interpretation.next_to(checkmark, DOWN, buff=0.5)
        self.play(Write(interpretation))
        self.wait(1)
        
        # Final summary
        self.play(FadeOut(VGroup(distributed, verify_title, check_left, check_right, 
                                checkmark, interpretation)))
        
        summary_title = Text("Key Steps for Distributive Property:", font_size=28, color=ORANGE)
        summary_title.move_to(ORIGIN).shift(UP*1.5)
        
        steps = [
            "1. Distribute: multiply outside number by each term inside parentheses",
            "2. Combine like terms on each side",
            "3. Use inverse operations to isolate the variable",
            "4. Always check your answer!"
        ]
        
        step_objects = []
        self.play(Write(summary_title))
        
        for i, step in enumerate(steps):
            step_text = Text(step, font_size=22, color=WHITE)
            step_text.next_to(summary_title, DOWN, buff=0.5 + i*0.6)
            step_objects.append(step_text)
            self.play(Write(step_text))
            self.wait(0.5)
        
        # Keep answer visible
        final_answer = Text("Answer: x = 11", font_size=32, color=RED)
        final_answer.next_to(step_objects[-1], DOWN, buff=0.8)
        self.play(Write(final_answer))
        
        answer_box_final = SurroundingRectangle(final_answer, color=RED, buff=0.3)
        self.play(Create(answer_box_final))
        
        self.wait(3)