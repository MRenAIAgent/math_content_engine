# Introduction to inequality symbols and number line graphs
# Generated for Chapter 2 - Section 2.7

from manim import *

class InequalitySymbolsScene(Scene):
    def construct(self):
        # Title
        title = Text("Introduction to Inequality Symbols", font_size=36).set_color(BLUE)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Introduction text
        intro = Text("Four inequality symbols and their number line representations", font_size=24)
        intro.next_to(title, DOWN, buff=0.5)
        self.play(Write(intro))
        self.wait(2)
        self.play(FadeOut(intro))

        # Create number line function
        def create_number_line():
            line = Line(LEFT * 4, RIGHT * 4, color=WHITE)
            numbers = VGroup()
            for i in range(-3, 4):
                tick = Line(UP * 0.1, DOWN * 0.1, color=WHITE)
                tick.move_to(line.get_start() + RIGHT * (i + 3) * 8/6)
                num = Text(str(i), font_size=20)
                num.next_to(tick, DOWN, buff=0.1)
                numbers.add(tick, num)
            return VGroup(line, numbers)

        # Less than (<)
        less_than_title = Text("< (less than)", font_size=28, color=RED)
        less_than_title.to_edge(LEFT).shift(UP * 2)
        self.play(Write(less_than_title))

        example1 = Text("x < 2", font_size=24)
        example1.next_to(less_than_title, DOWN, buff=0.3)
        self.play(Write(example1))

        number_line1 = create_number_line()
        number_line1.next_to(example1, DOWN, buff=0.5)
        self.play(Create(number_line1))

        # Open circle at 2
        open_circle1 = Circle(radius=0.08, color=RED, fill_opacity=0)
        open_circle1.move_to(number_line1[0].get_start() + RIGHT * 5 * 8/6)
        self.play(Create(open_circle1))

        # Arrow pointing left
        arrow1 = Arrow(start=open_circle1.get_center() + LEFT * 0.2, 
                      end=open_circle1.get_center() + LEFT * 2, 
                      color=RED, buff=0)
        self.play(Create(arrow1))

        note1 = Text("Open circle: 2 is NOT included", font_size=18, color=YELLOW)
        note1.next_to(number_line1, DOWN, buff=0.3)
        self.play(Write(note1))
        self.wait(2)

        # Clear for next symbol
        self.play(FadeOut(VGroup(less_than_title, example1, number_line1, open_circle1, arrow1, note1)))

        # Greater than (>)
        greater_than_title = Text("> (greater than)", font_size=28, color=GREEN)
        greater_than_title.to_edge(LEFT).shift(UP * 2)
        self.play(Write(greater_than_title))

        example2 = Text("x > -1", font_size=24)
        example2.next_to(greater_than_title, DOWN, buff=0.3)
        self.play(Write(example2))

        number_line2 = create_number_line()
        number_line2.next_to(example2, DOWN, buff=0.5)
        self.play(Create(number_line2))

        # Open circle at -1
        open_circle2 = Circle(radius=0.08, color=GREEN, fill_opacity=0)
        open_circle2.move_to(number_line2[0].get_start() + RIGHT * 2 * 8/6)
        self.play(Create(open_circle2))

        # Arrow pointing right
        arrow2 = Arrow(start=open_circle2.get_center() + RIGHT * 0.2, 
                      end=open_circle2.get_center() + RIGHT * 2, 
                      color=GREEN, buff=0)
        self.play(Create(arrow2))

        note2 = Text("Open circle: -1 is NOT included", font_size=18, color=YELLOW)
        note2.next_to(number_line2, DOWN, buff=0.3)
        self.play(Write(note2))
        self.wait(2)

        # Clear for next symbol
        self.play(FadeOut(VGroup(greater_than_title, example2, number_line2, open_circle2, arrow2, note2)))

        # Less than or equal (≤)
        less_equal_title = Text("≤ (less than or equal)", font_size=28, color=PURPLE)
        less_equal_title.to_edge(LEFT).shift(UP * 2)
        self.play(Write(less_equal_title))

        example3 = Text("x ≤ 1", font_size=24)
        example3.next_to(less_equal_title, DOWN, buff=0.3)
        self.play(Write(example3))

        number_line3 = create_number_line()
        number_line3.next_to(example3, DOWN, buff=0.5)
        self.play(Create(number_line3))

        # Closed circle at 1
        closed_circle1 = Circle(radius=0.08, color=PURPLE, fill_opacity=1)
        closed_circle1.move_to(number_line3[0].get_start() + RIGHT * 4 * 8/6)
        self.play(Create(closed_circle1))

        # Arrow pointing left
        arrow3 = Arrow(start=closed_circle1.get_center() + LEFT * 0.2, 
                      end=closed_circle1.get_center() + LEFT * 2, 
                      color=PURPLE, buff=0)
        self.play(Create(arrow3))

        note3 = Text("Closed circle: 1 IS included", font_size=18, color=YELLOW)
        note3.next_to(number_line3, DOWN, buff=0.3)
        self.play(Write(note3))
        self.wait(2)

        # Clear for next symbol
        self.play(FadeOut(VGroup(less_equal_title, example3, number_line3, closed_circle1, arrow3, note3)))

        # Greater than or equal (≥)
        greater_equal_title = Text("≥ (greater than or equal)", font_size=28, color=ORANGE)
        greater_equal_title.to_edge(LEFT).shift(UP * 2)
        self.play(Write(greater_equal_title))

        example4 = Text("x ≥ 0", font_size=24)
        example4.next_to(greater_equal_title, DOWN, buff=0.3)
        self.play(Write(example4))

        number_line4 = create_number_line()
        number_line4.next_to(example4, DOWN, buff=0.5)
        self.play(Create(number_line4))

        # Closed circle at 0
        closed_circle2 = Circle(radius=0.08, color=ORANGE, fill_opacity=1)
        closed_circle2.move_to(number_line4[0].get_start() + RIGHT * 3 * 8/6)
        self.play(Create(closed_circle2))

        # Arrow pointing right
        arrow4 = Arrow(start=closed_circle2.get_center() + RIGHT * 0.2, 
                      end=closed_circle2.get_center() + RIGHT * 2, 
                      color=ORANGE, buff=0)
        self.play(Create(arrow4))

        note4 = Text("Closed circle: 0 IS included", font_size=18, color=YELLOW)
        note4.next_to(number_line4, DOWN, buff=0.3)
        self.play(Write(note4))
        self.wait(2)

        # Clear for summary
        self.play(FadeOut(VGroup(greater_equal_title, example4, number_line4, closed_circle2, arrow4, note4)))

        # Summary
        summary_title = Text("Key Points to Remember", font_size=32, color=BLUE)
        summary_title.shift(UP * 1.5)
        self.play(Write(summary_title))

        summary_points = VGroup(
            Text("• Open circle (○): value NOT included", font_size=24),
            Text("• Closed circle (●): value IS included", font_size=24),
            Text("• Arrow shows direction of inequality", font_size=24)
        )
        summary_points.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        summary_points.next_to(summary_title, DOWN, buff=0.8)

        for point in summary_points:
            self.play(Write(point))
            self.wait(1)

        self.wait(3)