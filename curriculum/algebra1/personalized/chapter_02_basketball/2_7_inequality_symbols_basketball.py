# Introduction to inequality symbols and number line graphs - Basketball & NBA Edition
# Section 2.7

from manim import *

class BasketballInequalityScene(Scene):
    def construct(self):
        # Title
        title = Text("Inequality Symbols & Number Lines", color=ORANGE, font_size=36)
        subtitle = Text("Basketball Scoring Edition", color=BLUE, font_size=24)
        self.play(Write(title))
        self.play(Write(subtitle.next_to(title, DOWN)))
        self.wait(1)
        self.play(title.animate.to_edge(UP), FadeOut(subtitle))
        
        # Introduction with basketball context
        intro = Text("Let's compare NBA player scoring!", color=WHITE, font_size=28)
        self.play(Write(intro))
        self.wait(1)
        self.play(FadeOut(intro))
        
        # Introduce inequality symbols
        symbols_title = Text("Inequality Symbols", color=ORANGE, font_size=32).to_edge(UP, buff=1)
        self.play(Write(symbols_title))
        
        # Create symbol explanations
        less_than = Text("< means 'less than'", color=WHITE, font_size=24)
        greater_than = Text("> means 'greater than'", color=WHITE, font_size=24)
        less_equal = Text("≤ means 'less than or equal to'", color=WHITE, font_size=24)
        greater_equal = Text("≥ means 'greater than or equal to'", color=WHITE, font_size=24)
        
        symbols_group = VGroup(less_than, greater_than, less_equal, greater_equal)
        symbols_group.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        symbols_group.move_to(ORIGIN)
        
        for symbol in symbols_group:
            self.play(Write(symbol))
            self.wait(0.5)
        
        self.wait(1)
        self.play(FadeOut(symbols_group))
        
        # Basketball scoring comparison
        curry_score = Text("Stephen Curry: 42 points", color=BLUE, font_size=28)
        lebron_score = Text("LeBron James: 38 points", color=RED, font_size=28)
        
        curry_score.move_to(UP * 1.5)
        lebron_score.move_to(DOWN * 1.5)
        
        self.play(Write(curry_score), Write(lebron_score))
        self.wait(1)
        
        # Show comparison
        comparison1 = Text("42 > 38", color=ORANGE, font_size=32)
        comparison2 = Text("38 < 42", color=ORANGE, font_size=32)
        
        self.play(Write(comparison1))
        self.wait(1)
        self.play(Transform(comparison1, comparison2))
        self.wait(1)
        
        self.play(FadeOut(curry_score), FadeOut(lebron_score), FadeOut(comparison1))
        
        # Number line introduction
        numberline_title = Text("Number Lines & Inequalities", color=ORANGE, font_size=32).to_edge(UP, buff=1)
        self.play(Transform(symbols_title, numberline_title))
        
        # Create number line
        number_line = NumberLine(
            x_range=[0, 50, 10],
            length=10,
            color=WHITE,
            include_numbers=True,
            numbers_to_include=[0, 10, 20, 30, 40, 50]
        )
        number_line.move_to(ORIGIN)
        
        self.play(Create(number_line))
        
        # Label the number line
        points_label = Text("Points Scored", color=WHITE, font_size=20)
        points_label.next_to(number_line, DOWN, buff=0.5)
        self.play(Write(points_label))
        
        # Show x > 30 (scored more than 30 points)
        inequality1 = Text("Players who scored more than 30 points: x > 30", color=YELLOW, font_size=24)
        inequality1.to_edge(UP, buff=2)
        self.play(Write(inequality1))
        
        # Open circle at 30
        open_circle = Circle(radius=0.1, color=ORANGE, fill_opacity=0).move_to(number_line.n2p(30))
        self.play(Create(open_circle))
        
        # Arrow pointing right
        arrow_right = Arrow(start=number_line.n2p(30), end=number_line.n2p(48), color=ORANGE, buff=0)
        self.play(Create(arrow_right))
        
        self.wait(2)
        
        # Clear and show x ≤ 25
        self.play(FadeOut(inequality1), FadeOut(open_circle), FadeOut(arrow_right))
        
        inequality2 = Text("Players who scored 25 points or fewer: x ≤ 25", color=GREEN, font_size=24)
        inequality2.to_edge(UP, buff=2)
        self.play(Write(inequality2))
        
        # Closed circle at 25
        closed_circle = Circle(radius=0.1, color=GREEN, fill_opacity=1).move_to(number_line.n2p(25))
        self.play(Create(closed_circle))
        
        # Arrow pointing left
        arrow_left = Arrow(start=number_line.n2p(25), end=number_line.n2p(2), color=GREEN, buff=0)
        self.play(Create(arrow_left))
        
        self.wait(2)
        
        # Clear and show final example
        self.play(FadeOut(inequality2), FadeOut(closed_circle), FadeOut(arrow_left))
        
        # Playoff threshold example
        playoff_text = Text("Teams need at least 45 wins for playoffs: w ≥ 45", color=BLUE, font_size=24)
        playoff_text.to_edge(UP, buff=2)
        self.play(Write(playoff_text))
        
        # Adjust number line for wins
        wins_label = Text("Wins in Season", color=WHITE, font_size=20)
        self.play(Transform(points_label, wins_label))
        
        # Closed circle at 45
        playoff_circle = Circle(radius=0.1, color=BLUE, fill_opacity=1).move_to(number_line.n2p(45))
        self.play(Create(playoff_circle))
        
        # Arrow pointing right from 45
        playoff_arrow = Arrow(start=number_line.n2p(45), end=number_line.n2p(48), color=BLUE, buff=0)
        self.play(Create(playoff_arrow))
        
        self.wait(2)
        
        # Summary
        self.play(FadeOut(playoff_text), FadeOut(number_line), FadeOut(points_label), 
                 FadeOut(playoff_circle), FadeOut(playoff_arrow))
        
        summary_title = Text("Key Points:", color=ORANGE, font_size=32)
        summary_title.to_edge(UP, buff=1.5)
        
        point1 = Text("• Open circle (○): does NOT include the number", color=WHITE, font_size=24)
        point2 = Text("• Closed circle (●): INCLUDES the number", color=WHITE, font_size=24)
        point3 = Text("• Arrow shows which direction satisfies inequality", color=WHITE, font_size=24)
        
        summary_group = VGroup(point1, point2, point3)
        summary_group.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        summary_group.move_to(ORIGIN)
        
        self.play(Write(summary_title))
        for point in summary_group:
            self.play(Write(point))
            self.wait(0.5)
        
        # Fun fact
        fun_fact = Text("Fun Fact: Curry once scored 50+ points in 4 consecutive games!", 
                       color=YELLOW, font_size=20)
        fun_fact.to_edge(DOWN)
        self.play(Write(fun_fact))
        
        self.wait(3)