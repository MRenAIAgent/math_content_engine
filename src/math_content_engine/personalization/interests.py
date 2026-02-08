"""
Interest profiles for content personalization.

Each profile defines context, terminology, examples, and visual themes
that can be used to make math content more engaging for students with
specific interests.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class InterestProfile:
    """
    Profile defining how to personalize content for a specific interest.

    Attributes:
        name: Interest identifier (e.g., "basketball", "gaming")
        display_name: Human-readable name (e.g., "Basketball & NBA")
        description: Brief description of the interest context
        context_intro: Introduction text explaining the personalization
        basic_knowledge: Essential facts about the interest for accurate content
        famous_figures: List of well-known people/characters in this domain
        terminology: Domain-specific terms mapped to math concepts
        example_scenarios: Real-world scenarios for word problems
        visual_themes: Suggested colors, icons, imagery
        analogies: Math concept to domain concept mappings
        fun_facts: Interesting facts to include in content
    """
    name: str
    display_name: str
    description: str
    context_intro: str
    basic_knowledge: str = ""  # Essential facts about the interest
    famous_figures: List[str] = field(default_factory=list)
    terminology: Dict[str, str] = field(default_factory=dict)
    example_scenarios: List[str] = field(default_factory=list)
    visual_themes: Dict[str, str] = field(default_factory=dict)
    analogies: Dict[str, str] = field(default_factory=dict)
    fun_facts: List[str] = field(default_factory=list)
    cultural_references: List[str] = field(default_factory=list)  # Memes, quotes, iconic moments
    historical_trivia: List[str] = field(default_factory=list)  # Historical facts
    real_world_connections: List[str] = field(default_factory=list)  # How math is used in this field
    motivational_quotes: List[str] = field(default_factory=list)  # Inspiring quotes from figures

    # Engagement fields — make content feel current, personal, and interactive
    second_person_scenarios: List[str] = field(default_factory=list)  # "You scored 24 points..."
    engagement_hooks: List[str] = field(default_factory=list)  # Interactive questions/challenges
    verified_stats: Dict[str, str] = field(default_factory=dict)  # Real numbers for accuracy
    trending_now: List[str] = field(default_factory=list)  # Current/recent references
    current_season: str = ""  # Time anchor, e.g. "2024-25 NBA Season"

    def get_personalization_prompt(self) -> str:
        """Generate a prompt section for LLM personalization."""
        figures_str = ", ".join(self.famous_figures[:5]) if self.famous_figures else "relevant figures"
        scenarios_str = "\n".join(f"  - {s}" for s in self.example_scenarios[:5])
        analogies_str = "\n".join(f"  - {k}: {v}" for k, v in list(self.analogies.items())[:5])
        fun_facts_str = "\n".join(f"  - {f}" for f in self.fun_facts[:3]) if self.fun_facts else ""
        cultural_refs_str = "\n".join(f"  - {c}" for c in self.cultural_references[:3]) if self.cultural_references else ""
        trivia_str = "\n".join(f"  - {t}" for t in self.historical_trivia[:2]) if self.historical_trivia else ""
        quotes_str = "\n".join(f"  - \"{q}\"" for q in self.motivational_quotes[:2]) if self.motivational_quotes else ""

        return f"""
## PERSONALIZATION CONTEXT: {self.display_name}

{self.context_intro}

### Basic Knowledge About {self.display_name}:
{self.basic_knowledge}

### Use These Elements to Make Content Engaging:

**Famous Figures to Reference:** {figures_str}

**Example Scenarios for Problems:**
{scenarios_str}

**Math Concept Analogies:**
{analogies_str}

**Visual Theme:**
- Primary colors: {self.visual_themes.get('primary_colors', 'Use appropriate thematic colors')}
- Imagery suggestions: {self.visual_themes.get('imagery', 'Use domain-relevant visuals')}

**Fun Facts to Include (pick one per lesson):**
{fun_facts_str}

**Cultural References & Iconic Moments (use sparingly for humor/engagement):**
{cultural_refs_str}

**Historical Context (for depth):**
{trivia_str}

**Motivational Quotes (use for introduction or conclusion):**
{quotes_str}

{self._format_engagement_section()}

**Important Guidelines:**
1. Replace generic examples with {self.name}-themed scenarios
2. Use terminology familiar to {self.name} fans
3. Reference real statistics, scores, or metrics when possible
4. Keep the math rigorous while making context fun and relatable
5. Include at least one fun fact or real-world application
6. Use the basic knowledge above to ensure accuracy
7. Sprinkle in cultural references to make content feel current and relatable
8. Connect historical facts to show math's importance in the field
9. Address the student as "you" — make it personal, not third-person
"""

    def _format_engagement_section(self) -> str:
        """Format the engagement fields for the personalization prompt."""
        parts = []
        if self.current_season:
            parts.append(f"**Current Context:** {self.current_season}")
        if self.trending_now:
            trending_str = "\n".join(f"  - {t}" for t in self.trending_now[:3])
            parts.append(f"**Trending Now (use for current relevance):**\n{trending_str}")
        if self.second_person_scenarios:
            scenarios_str = "\n".join(f"  - {s}" for s in self.second_person_scenarios[:3])
            parts.append(
                f"**2nd-Person Scenarios (say 'you', not 'a player'):**\n{scenarios_str}"
            )
        if self.engagement_hooks:
            hooks_str = "\n".join(f"  - {h}" for h in self.engagement_hooks[:3])
            parts.append(f"**Engagement Hooks (interactive questions):**\n{hooks_str}")
        if self.verified_stats:
            stats_str = "\n".join(
                f"  - {k}: {v}" for k, v in list(self.verified_stats.items())[:5]
            )
            parts.append(f"**Verified Stats (use these real numbers):**\n{stats_str}")
        return "\n\n".join(parts)


# =============================================================================
# SPORTS PROFILES
# =============================================================================

BASKETBALL_PROFILE = InterestProfile(
    name="basketball",
    display_name="Basketball & NBA",
    description="Basketball and NBA-themed content featuring players, stats, and game scenarios",
    context_intro="""Make all math content relatable to basketball fans by using NBA game scenarios,
player statistics, team comparisons, and basketball terminology. Students who love basketball
will connect with examples about three-pointers, scoring totals, and their favorite players.""",
    basic_knowledge="""
**How Basketball Scoring Works:**
- A free throw is worth 1 point
- A regular shot (inside the three-point line) is worth 2 points
- A shot from behind the three-point line is worth 3 points
- Teams try to score more points than the other team to win

**Game Structure:**
- An NBA game has 4 quarters, each 12 minutes long (48 minutes total)
- College games have two 20-minute halves
- If the score is tied, they play 5-minute overtime periods

**The Court:**
- An NBA court is 94 feet long and 50 feet wide
- The three-point line is about 23-24 feet from the basket
- The free throw line is 15 feet from the basket

**Teams and Seasons:**
- The NBA has 30 teams
- The regular season has 82 games per team
- The best teams go to the playoffs to compete for the championship

**Common Stats:**
- Points: how many points a player scored
- Rebounds: catching the ball after a missed shot
- Assists: passing to a teammate who then scores
- A "double-double" means 10+ in two categories (like 20 points and 12 rebounds)
- A "triple-double" means 10+ in three categories
""",
    famous_figures=[
        # Current Stars kids know (2024-25)
        "Stephen Curry", "LeBron James", "Victor Wembanyama", "Luka Doncic",
        "Jayson Tatum", "Anthony Edwards", "Giannis Antetokounmpo",
        # All-Time Greats kids hear about
        "Michael Jordan", "Kobe Bryant",
    ],
    terminology={
        "variable": "an unknown number (like how many points someone scored)",
        "equation": "a math sentence that shows two things are equal",
        "solution": "the answer that makes the equation true",
        "inequality": "comparing numbers (more than, less than)",
        "coefficient": "the number multiplied by a variable (like 3 in 3x for three-pointers)",
        "constant": "a number that doesn't change (like 1 point for a free throw)",
    },
    example_scenarios=[
        # Simple points calculation
        "Curry scored 36 points. If he made x three-pointers worth 3 points each and 9 two-pointers worth 2 points each, how many three-pointers did he make?",
        # Basic averages
        "LeBron averages 25 points per game. How many total points will he score in 10 games?",
        # Team totals
        "The Lakers scored 112 points. Starters scored 78 points. How many points did the bench players score?",
        # Comparing players
        "Wembanyama is 7 feet 4 inches tall. Curry is 6 feet 2 inches. How much taller is Wembanyama?",
        # Win-loss records
        "A team has won 35 games and lost 20 games. How many total games have they played?",
        # Shooting practice
        "A player makes 7 out of 10 free throws. What fraction did they make? What percentage?",
        # Game tickets
        "If a basketball ticket costs $45 and you buy tickets for 4 friends, how much do you spend?",
        # Season stats
        "A player scored 15, 22, 18, 31, and 24 points in 5 games. What was their average?",
    ],
    visual_themes={
        "primary_colors": "ORANGE (basketball), BLUE (NBA blue), RED (team colors)",
        "imagery": "Basketball court, hoop, scoreboard, basketball",
        "animations": "Ball going through hoop, scoreboard counting up, player shooting",
    },
    analogies={
        "solving equations": "finding a missing stat when you know the total",
        "variables": "unknown numbers we need to figure out (like x = points scored)",
        "addition": "adding up points from different quarters",
        "multiplication": "points per game times number of games",
        "division": "splitting total points to find the average",
        "inequalities": "comparing who scored more points",
    },
    fun_facts=[
        "Stephen Curry has made more three-pointers than anyone in NBA history - over 3,700!",
        "LeBron James has scored more points than any other player ever - over 40,000!",
        "Wilt Chamberlain once scored 100 points in a single game in 1962",
        "A triple-double means getting 10+ in three categories: points, rebounds, and assists",
        "An NBA basketball court is 94 feet long - that's almost as long as a third of a football field!",
        "The three-point line wasn't added to the NBA until 1979 - before that, all shots were worth 2 points!",
        "Victor Wembanyama has the longest wingspan ever measured at the NBA Draft Combine: 8 feet!",
        "The shot clock (24 seconds) was invented in 1954 to make games more exciting",
    ],
    cultural_references=[
        "Steph Curry's 'Night Night' celebration after hitting clutch shots",
        "LeBron's famous 'The Block' in Game 7 of the 2016 Finals",
        "Michael Jordan's 'The Last Dance' documentary and 6 championship rings",
        "'Ball don't lie' - what players say when a missed free throw proves a bad call",
        "The 'Greek Freak' Giannis going from unknown to MVP in just a few years",
        "Kobe's 'Mamba Mentality' - working harder than everyone else",
        "Space Jam movies featuring NBA superstars",
    ],
    historical_trivia=[
        "Basketball was invented in 1891 by James Naismith using a peach basket as the hoop!",
        "The first NBA game was played on November 1, 1946 - almost 80 years ago",
        "The NBA three-point line is 23 feet 9 inches - it was added in 1979",
        "The tallest NBA player ever was Gheorghe Muresan at 7 feet 7 inches",
        "The shortest NBA player was Muggsy Bogues at only 5 feet 3 inches",
    ],
    real_world_connections=[
        "NBA teams use advanced analytics and math to calculate player efficiency ratings",
        "Basketball coaches use probability to decide when to foul at the end of games",
        "Sports betting uses algebra and statistics to set point spreads",
        "Player salaries are calculated using complex formulas involving the salary cap",
        "Shot charts use coordinate geometry to map where players shoot best",
    ],
    motivational_quotes=[
        "I've failed over and over again in my life. And that is why I succeed. - Michael Jordan",
        "Hard work beats talent when talent doesn't work hard. - Kevin Durant",
        "I'm not the next anyone. I'm the first me. - Giannis Antetokounmpo",
        "Excellence is not a singular act, but a habit. You are what you repeatedly do. - Shaquille O'Neal",
        "I can accept failure, everyone fails at something. But I can't accept not trying. - Michael Jordan",
    ],
    current_season="2024-25 NBA Season",
    trending_now=[
        "Victor Wembanyama dominating as a 7'4\" rookie with blocks and three-pointers",
        "Nikola Jokic chasing a third consecutive MVP with historic triple-double numbers",
        "Anthony Edwards emerging as the face of the next generation of NBA stars",
        "The NBA's new in-season tournament (NBA Cup) adding excitement to the schedule",
    ],
    second_person_scenarios=[
        "You just scored 24 points in a game — 8 two-pointers and some three-pointers. Can you figure out how many threes you hit?",
        "Your team's win rate is 0.65 after 40 games. How many games have you won so far?",
        "You're at the free throw line and you've made 7 out of 10 shots tonight. What's your free throw percentage?",
        "You need to average 25 points per game over the next 5 games to win the scoring title. If you scored 22, 28, 30, and 19 so far, how many do you need in the last game?",
        "Your team scored 108 points. You scored one-third of them. How many points did you score?",
        "You're choosing between two sneaker deals: one pays $5,000 plus $2 per pair sold, the other pays $8 per pair with no upfront money. At how many pairs sold do the deals pay the same?",
    ],
    engagement_hooks=[
        "Can you calculate your free throw percentage if you made 7 out of 10?",
        "Imagine you're the coach — your team is down by 6 with 30 seconds left. What's the fastest way to tie it up?",
        "If Steph Curry makes 43% of his three-pointers, how many would he make out of 20 attempts?",
        "You just got drafted! Your contract pays $2 million per year for 4 years. What's the total?",
        "Quick challenge: Is a player who scores 18, 22, 25, 15, and 30 averaging more or less than 20 points per game?",
    ],
    verified_stats={
        "3pt_line_distance": "23 feet 9 inches from the basket",
        "free_throw_distance": "15 feet from the basket",
        "court_dimensions": "94 feet long, 50 feet wide",
        "curry_career_3pt": "3,747+ career three-pointers (all-time record)",
        "lebron_career_points": "40,000+ career points (all-time record)",
        "nba_game_length": "4 quarters of 12 minutes each (48 minutes total)",
        "shot_clock": "24 seconds per possession",
        "wembanyama_height": "7 feet 4 inches tall with 8-foot wingspan",
    },
)

FOOTBALL_PROFILE = InterestProfile(
    name="football",
    display_name="Football & NFL",
    description="American football and NFL-themed content with plays, stats, and game scenarios",
    context_intro="""Make math content engaging for football fans using NFL game scenarios,
touchdown calculations, and team statistics. Use examples about scoring, yards, and
favorite players that middle school students follow.""",
    basic_knowledge="""
**How Football Scoring Works:**
- Touchdown = 6 points (getting the ball into the end zone)
- Extra point (kick after touchdown) = 1 point
- Two-point conversion (running/passing into end zone after TD) = 2 points
- Field goal (kicking through the goal posts) = 3 points
- Safety (tackling opponent in their own end zone) = 2 points

**Game Structure:**
- A game has 4 quarters, each 15 minutes long
- Halftime is between the 2nd and 3rd quarters
- If tied at the end, they play overtime

**The Field:**
- The field is 100 yards long (plus two 10-yard end zones)
- Yard lines are marked every 5 yards
- Teams try to move the ball toward the opponent's end zone

**How Downs Work:**
- A team gets 4 tries (downs) to move the ball 10 yards
- If they get 10 yards, they get a fresh set of 4 downs
- "1st and 10" means 1st down with 10 yards to go
- On 4th down, teams usually punt or try a field goal

**Positions:**
- Quarterback (QB): throws the ball
- Running back (RB): runs with the ball
- Wide receiver (WR): catches passes
- Tight end (TE): blocks and catches passes
- The defense tries to stop the offense from scoring
""",
    famous_figures=[
        # QBs kids know (2024-25)
        "Patrick Mahomes", "Josh Allen", "Lamar Jackson", "Joe Burrow",
        # Skill Players kids follow
        "Travis Kelce", "Tyreek Hill", "Justin Jefferson",
        # Legends
        "Tom Brady",
    ],
    terminology={
        "variable": "an unknown number (like how many touchdowns)",
        "equation": "a math sentence to figure out scores or stats",
        "coefficient": "the number multiplied by something (like 6 for touchdowns)",
        "inequality": "comparing numbers (more yards than, fewer points than)",
        "constant": "numbers that stay the same (like 6 points for every touchdown)",
    },
    example_scenarios=[
        # Simple scoring
        "A team scored 28 points, all from touchdowns (6 points each) and extra points (1 point each). If they made all their extra points, how many touchdowns did they score?",
        # Yards calculation
        "Mahomes threw for 312 yards in the first half and 176 yards in the second half. How many total passing yards?",
        # Field goals
        "A kicker made 4 field goals worth 3 points each. How many points did he score?",
        # Rushing yards
        "A running back gained 15 yards, then 8 yards, then lost 3 yards. What was his total yardage?",
        # Win-loss records
        "The Chiefs have won 11 games and lost 3 games. What fraction of their games have they won?",
        # Simple averages
        "A receiver caught passes for 45, 78, 62, 91, and 54 yards over 5 games. What's his average yards per game?",
        # Ticket prices
        "Super Bowl tickets cost $5,000 each. How much would 2 tickets cost?",
        # Field distance
        "A team starts at their own 20-yard line and needs to reach the end zone at the 100-yard line. How many yards do they need to go?",
    ],
    visual_themes={
        "primary_colors": "GREEN (field), BROWN (football), WHITE (yard lines)",
        "imagery": "Football field, goal posts, scoreboard, football",
        "animations": "Ball moving down field, scoreboard updating, touchdown celebration",
    },
    analogies={
        "solving equations": "figuring out how many touchdowns when you know the final score",
        "variables": "unknown numbers like touchdowns or yards",
        "multiplication": "points per touchdown times number of touchdowns",
        "addition": "adding up yards from different plays",
        "subtraction": "losing yards on a play",
        "division": "finding average yards per game",
    },
    fun_facts=[
        "Tom Brady won 7 Super Bowls - more than any single NFL team!",
        "A football field is 100 yards long (that's 300 feet, or the length of 3 NHL hockey rinks!)",
        "The longest field goal ever made was 66 yards by Justin Tucker in 2021",
        "Patrick Mahomes became the youngest quarterback to win both an MVP award and a Super Bowl",
        "An NFL football is about 11 inches long and weighs about 1 pound",
        "The Super Bowl is watched by over 100 million people - more than any other US TV event!",
        "NFL players run an average of 1.25 miles per game",
        "The fastest NFL player ever ran the 40-yard dash in 4.22 seconds!",
    ],
    cultural_references=[
        "Patrick Mahomes' famous no-look passes that seem impossible",
        "Travis Kelce's relationship with Taylor Swift bringing new fans to football",
        "The 'Philly Special' trick play from Super Bowl LII",
        "'You like that!' - Kirk Cousins' catchphrase after wins",
        "The iconic Gatorade shower coaches get after winning big games",
        "Fantasy Football - millions of fans use math to build their dream teams",
    ],
    historical_trivia=[
        "The first Super Bowl was played on January 15, 1967 - tickets cost just $12!",
        "The forward pass wasn't legal until 1906 - before that, it was all running!",
        "The NFL started in 1920 with just 11 teams, now there are 32",
        "The first NFL draft was in 1936 at a Philadelphia hotel",
    ],
    real_world_connections=[
        "NFL teams use analytics to calculate expected points on every play",
        "Coaches use probability to decide whether to go for it on 4th down",
        "Fantasy Football requires statistical analysis to pick the best players",
        "Sports scientists use biomechanics (physics and math) to prevent injuries",
        "NFL contracts involve complex salary cap math worth hundreds of millions",
    ],
    motivational_quotes=[
        "Success is not forever, and failure is not fatal. - Don Shula",
        "The only way to prove you're a good sport is to lose. - Ernie Banks",
        "It's not whether you get knocked down, it's whether you get up. - Vince Lombardi",
        "Set your goals high, and don't stop till you get there. - Bo Jackson",
    ],
    current_season="2024-25 NFL Season",
    trending_now=[
        "Patrick Mahomes chasing a third consecutive Super Bowl win",
        "Lamar Jackson's dual-threat MVP season with rushing and passing records",
        "The NFL expanding internationally with games in London, Munich, and Brazil",
    ],
    second_person_scenarios=[
        "You're the quarterback and you threw 3 touchdowns (6 points each) plus your kicker made 2 field goals (3 points each). How many total points did your team score from those plays?",
        "You rushed for 85 yards in the first half and 47 yards in the second half. What's your total rushing yards?",
        "Your team is at the 35-yard line. You need to reach the end zone at the 0-yard line. How many yards do you need to go?",
        "You caught 6 passes for a total of 132 yards. What's your average yards per catch?",
    ],
    engagement_hooks=[
        "If your team scores a touchdown, should you go for 1 extra point (almost guaranteed) or 2 points (50% chance)? What's the smarter math move?",
        "Can you figure out how many touchdowns Mahomes needs to break the season record of 55?",
        "You're the coach with 4th and 2 on the opponent's 30-yard line. Go for it or kick the field goal?",
    ],
    verified_stats={
        "field_length": "100 yards (plus two 10-yard end zones)",
        "touchdown_points": "6 points per touchdown",
        "field_goal_points": "3 points per field goal",
        "extra_point": "1 point (kick) or 2 points (conversion)",
        "games_per_season": "18 regular season games per team (since 2021)",
        "mahomes_age_first_mvp": "23 years old (youngest QB MVP at the time)",
    },
)

SOCCER_PROFILE = InterestProfile(
    name="soccer",
    display_name="Soccer & World Football",
    description="Soccer/football themed content with goals, assists, and league statistics",
    context_intro="""Engage soccer fans with examples from the Premier League, World Cup,
and famous players. Use scenarios about goals, assists, and points that middle school
students can relate to from watching games.""",
    basic_knowledge="""
**How Soccer Works:**
- Each team has 11 players on the field (including the goalkeeper)
- The goal is to kick the ball into the opponent's net
- Only the goalkeeper can use their hands (inside the penalty area)
- A goal = 1 point
- The team with more goals wins

**Game Structure:**
- A match has two 45-minute halves (90 minutes total)
- There's a 15-minute halftime break
- The referee can add "stoppage time" for delays during the game
- If tied in a knockout game, they play extra time (two 15-minute periods) and then penalty kicks

**The Field (Pitch):**
- A soccer field is about 110-120 yards long and 70-80 yards wide
- The penalty area is the big box in front of each goal
- A penalty kick is taken from 12 yards away from the goal

**League Points System:**
- Win = 3 points
- Draw (tie) = 1 point
- Loss = 0 points
- Teams are ranked by total points in the standings

**Common Terms:**
- Assist: passing to a teammate who then scores
- Clean sheet: when a goalkeeper doesn't let in any goals
- Hat trick: when one player scores 3 goals in a single game
- Offside: when an attacker is behind all defenders when the ball is passed to them
""",
    famous_figures=[
        # Stars kids know (2024-25)
        "Lionel Messi", "Cristiano Ronaldo", "Kylian Mbappe", "Erling Haaland",
        # Young stars close to their age group
        "Lamine Yamal", "Jude Bellingham",
    ],
    terminology={
        "variable": "an unknown number (like goals scored)",
        "equation": "a math sentence to calculate points or stats",
        "coefficient": "the number multiplied by something (like 3 points for a win)",
        "inequality": "comparing numbers (more goals, fewer points)",
        "constant": "numbers that stay the same (like 3 points for winning a game)",
    },
    example_scenarios=[
        # Simple points
        "In soccer, a win is worth 3 points and a tie is worth 1 point. If a team has 5 wins and 3 ties, how many points do they have?",
        # Goal totals
        "Messi scored 2 goals in the first half and 1 goal in the second half. How many total goals did he score?",
        # Assists
        "A player has 8 goals and 5 assists. How many total goal contributions does he have?",
        # Goal difference
        "Team A scored 45 goals and let in 20 goals. Team B scored 38 goals and let in 15 goals. Which team has the better goal difference?",
        # Games calculation
        "A soccer season has 38 games. If a team has played 24 games, how many games are left?",
        # Shooting practice
        "A player took 20 shots and scored 4 goals. What fraction of shots went in?",
        # Jersey numbers
        "If Messi's jersey costs $120 and Ronaldo's costs $115, how much would both jerseys cost together?",
        # World Cup
        "The World Cup has 32 teams in 8 groups of 4 teams each. How many games are played in your group if every team plays each other once?",
    ],
    visual_themes={
        "primary_colors": "GREEN (field), WHITE (lines and ball), BLACK (goals)",
        "imagery": "Soccer field, goal, ball, scoreboard",
        "animations": "Ball going into goal, scoreboard updating, player kicking",
    },
    analogies={
        "solving equations": "figuring out how many wins a team needs to reach a point total",
        "variables": "unknown numbers like goals or points",
        "multiplication": "3 points times the number of wins",
        "addition": "adding goals from the first and second half",
        "subtraction": "finding goal difference (goals scored minus goals allowed)",
        "fractions": "shots on goal out of total shots",
    },
    fun_facts=[
        "Lionel Messi has won the Ballon d'Or (best player award) 8 times - more than anyone ever!",
        "Cristiano Ronaldo has scored over 900 career goals - that's almost impossible to beat!",
        "Lamine Yamal scored for Spain at the Euro 2024 when he was just 16 years old",
        "A soccer field is about 110-120 yards long - almost the same as a football field",
        "The World Cup is watched by billions of people around the world - more than any other sporting event!",
    ],
    current_season="2024-25 European Football Season",
    trending_now=[
        "Lamine Yamal becoming the youngest-ever Euros goalscorer at just 16",
        "Kylian Mbappe's blockbuster transfer to Real Madrid",
        "Erling Haaland's goal-scoring records in the Premier League",
    ],
    second_person_scenarios=[
        "Your team has 3 wins, 2 draws, and 1 loss. With 3 points for a win and 1 for a draw, how many points do you have?",
        "You scored 2 goals in the first half and your teammate scored 1 in the second half. If the other team scored 2, did your team win?",
        "You took 15 shots in the match and scored 3 goals. What's your shooting percentage?",
        "Your team needs 6 more points to qualify for the playoffs with 3 games left. Is it possible if you only get wins and draws?",
    ],
    engagement_hooks=[
        "Can you figure out how many points your team needs to win the league title?",
        "If Messi scores 0.8 goals per game, how many goals would he score in a 38-game season?",
        "You're the penalty taker — the goalie dives the wrong way 60% of the time. What are your odds of scoring?",
    ],
    verified_stats={
        "pitch_length": "110-120 yards long, 70-80 yards wide",
        "penalty_distance": "12 yards from the goal",
        "win_points": "3 points for a win, 1 for a draw, 0 for a loss",
        "match_length": "Two 45-minute halves (90 minutes total)",
        "messi_ballon_dor": "8 Ballon d'Or awards (most ever)",
        "ronaldo_career_goals": "900+ career goals",
    },
)

TENNIS_PROFILE = InterestProfile(
    name="tennis",
    display_name="Tennis & Grand Slams",
    description="Tennis-themed content with match scoring, rankings, and tournament statistics",
    context_intro="""Make math relatable for tennis fans using tournament scenarios and
famous players. Use examples about sets, games, and match scores that middle school
students can understand from watching tennis.""",
    basic_knowledge="""
**How Tennis Scoring Works:**
- Points in a game go: 0 (love), 15, 30, 40, game
- You need to win by 2 points; if tied at 40-40 (deuce), keep playing until someone wins by 2
- Win 6 games to win a set (must win by 2 games)
- If tied 6-6, play a tiebreak to 7 points (win by 2)
- Win 2 sets (women) or 3 sets (men in Grand Slams) to win the match

**The Court:**
- A tennis court is 78 feet long
- Singles court is 27 feet wide; doubles is 36 feet wide
- The net is 3 feet high in the center

**Types of Shots:**
- Serve: the shot that starts each point (hit from behind the baseline)
- Forehand: hitting the ball with your palm facing forward
- Backhand: hitting with the back of your hand facing forward
- Volley: hitting the ball before it bounces (usually at the net)
- Ace: a serve the opponent can't touch

**The Four Grand Slams (biggest tournaments):**
- Australian Open (January, hard court)
- French Open (May-June, clay court)
- Wimbledon (June-July, grass court)
- US Open (August-September, hard court)

**Common Terms:**
- Break: winning a game when your opponent is serving
- Love: zero points
- Deuce: tied at 40-40
- Match point: one point away from winning the match
""",
    famous_figures=[
        # Current stars kids know (2024-25)
        "Carlos Alcaraz", "Novak Djokovic", "Coco Gauff", "Iga Swiatek",
        # Legends kids hear about
        "Roger Federer", "Rafael Nadal", "Serena Williams",
    ],
    terminology={
        "variable": "an unknown number (like games won)",
        "equation": "a math sentence to figure out scores",
        "inequality": "comparing numbers (more wins, fewer errors)",
        "constant": "numbers that stay the same (like 6 games to win a set)",
    },
    example_scenarios=[
        # Simple set scoring
        "To win a set, you need 6 games (and be ahead by 2). If you've won 4 games, how many more do you need?",
        # Match totals
        "Alcaraz won a match 6-3, 6-4, 7-5. How many total games did he win?",
        # Tournament wins
        "Djokovic has won 24 Grand Slam titles. Federer and Nadal each won 20. How many more does Djokovic have than each of them?",
        # Serving
        "A player served 50 times and got 35 serves in. What fraction of serves went in?",
        # Head-to-head
        "In 10 matches between two players, Player A won 7 times. How many times did Player B win?",
        # Match time
        "A tennis match lasted 2 hours and 45 minutes. How many minutes is that?",
        # Aces
        "A player hit 12 aces in the first set and 8 aces in the second set. How many aces total?",
        # Tournament rounds
        "A tennis tournament starts with 64 players. After each round, half the players are eliminated. How many players are left after 3 rounds?",
    ],
    visual_themes={
        "primary_colors": "GREEN (court), YELLOW (ball), WHITE (lines)",
        "imagery": "Tennis court, net, tennis ball, scoreboard",
        "animations": "Ball going over net, scoreboard updating, player serving",
    },
    analogies={
        "solving equations": "figuring out how many games you need to win the set",
        "variables": "unknown numbers like games or points",
        "addition": "adding up games won in different sets",
        "subtraction": "finding how many more wins one player has",
        "fractions": "serves in compared to total serves",
        "multiplication": "points per round times number of rounds",
    },
    fun_facts=[
        "Novak Djokovic has won 24 Grand Slam titles - more than any man in history!",
        "Serena Williams won 23 Grand Slam titles - one of the greatest athletes ever",
        "Carlos Alcaraz became the world's #1 player when he was only 19 years old",
        "A tennis ball can travel over 150 miles per hour on a fast serve!",
        "The four Grand Slam tournaments are: Australian Open, French Open, Wimbledon, and US Open",
    ],
    current_season="2024-25 ATP/WTA Tennis Season",
    trending_now=[
        "Carlos Alcaraz winning multiple Grand Slams before turning 22",
        "Coco Gauff rising as the face of American women's tennis",
        "Novak Djokovic chasing the all-time Grand Slam record",
    ],
    second_person_scenarios=[
        "You won a match 6-3, 6-4, 7-5. How many total games did you win?",
        "You served 40 times and hit 12 aces. What fraction of your serves were aces?",
        "You're in a tiebreak and the score is 5-4 in your favor. How many more points do you need to win?",
        "You've won 7 matches and lost 3 this season. What's your win percentage?",
    ],
    engagement_hooks=[
        "If Alcaraz serves at 130 mph, how far does the ball travel in 1 second?",
        "You need to win 7 matches to win a Grand Slam. If each match takes about 2 hours, how many hours of tennis is that?",
    ],
    verified_stats={
        "court_length": "78 feet long",
        "singles_width": "27 feet wide (singles), 36 feet (doubles)",
        "net_height": "3 feet high at center",
        "djokovic_grand_slams": "24 Grand Slam titles (men's record)",
        "fastest_serve": "Over 160 mph (John Isner)",
    },
)

VOLLEYBALL_PROFILE = InterestProfile(
    name="volleyball",
    display_name="Volleyball",
    description="Volleyball-themed content with match stats, set scoring, and team dynamics",
    context_intro="""Engage volleyball players and fans with examples about scoring,
serves, and sets. Use scenarios that middle school volleyball players can relate to
from their own games and watching the Olympics.""",
    basic_knowledge="""
**How Volleyball Scoring Works:**
- Rally scoring: every rally (play) results in a point for one team
- First team to 25 points wins the set (must win by 2)
- If tied 24-24, keep playing until one team leads by 2
- The 5th set (if needed) is played to 15 points (win by 2)
- Win 3 sets to win the match (best of 5)

**The Court:**
- Indoor court is 59 feet long and 29.5 feet wide
- The net is about 7 feet 4 inches high for women, 7 feet 11 inches for men
- Beach volleyball court is smaller (52.5 x 26.25 feet)

**Player Positions (Indoor):**
- 6 players on each side
- Front row (3 players): can attack at the net
- Back row (3 players): play defense and pass
- Teams rotate clockwise after winning the serve back
- Libero: defensive specialist who wears a different color jersey

**How to Score Points:**
- Kill: an attack that the other team can't return
- Ace: a serve that the other team can't return
- Block: stopping the ball at the net
- Opponent error: when the other team makes a mistake

**Common Terms:**
- Serve: starting the rally by hitting the ball over the net
- Pass (bump): using forearms to hit the ball
- Set: using fingertips to place the ball for an attacker
- Spike (attack): jumping and hitting the ball down hard
- Dig: saving a hard-hit ball on defense
""",
    famous_figures=[
        # Olympic stars kids might know
        "Kerri Walsh Jennings", "Misty May-Treanor",
        # Current stars
        "Jordan Thompson", "Andrea Drews",
    ],
    terminology={
        "variable": "an unknown number (like points scored)",
        "equation": "a math sentence to figure out scores",
        "inequality": "comparing numbers (more points, fewer errors)",
        "constant": "numbers that stay the same (like 25 points to win a set)",
    },
    example_scenarios=[
        # Set scoring
        "To win a set in volleyball, you need 25 points (and be ahead by 2). If you have 23 points, how many more do you need at minimum?",
        # Simple addition
        "A player got 8 kills in the first set and 6 kills in the second set. How many total kills?",
        # Points in a match
        "Your team won a match 25-20, 25-22, 25-18. How many total points did your team score?",
        # Serving
        "A player served 15 times and got 12 serves in. What fraction of serves went in?",
        # Team rotations
        "A volleyball team has 6 players on the court. After 6 rotations, each player has served once. How many rotations until everyone has served 3 times?",
        # Aces
        "If you serve 10 aces in one game and 8 aces in the next game, how many aces total?",
        # Win by 2
        "The score is 24-24. You win the next 2 points. What's the final score?",
        # Team stats
        "Your team scored 25 points: 14 kills, 4 blocks, 3 aces, and the rest from opponent errors. How many points came from opponent errors?",
    ],
    visual_themes={
        "primary_colors": "BLUE (court), YELLOW/WHITE (ball), ORANGE (libero jersey)",
        "imagery": "Volleyball court, net, volleyball, scoreboard",
        "animations": "Ball going over net, players rotating, scoreboard updating",
    },
    analogies={
        "solving equations": "figuring out how many points you need to win the set",
        "variables": "unknown numbers like kills or aces",
        "addition": "adding up points from kills, blocks, and aces",
        "subtraction": "finding how many more points you need",
        "fractions": "serves in compared to total serves",
        "multiplication": "rotations times number of rounds",
    },
    fun_facts=[
        "Kerri Walsh Jennings and Misty May-Treanor won 3 Olympic gold medals in beach volleyball together!",
        "You have to win a set by 2 points - so a set can go way past 25 points!",
        "The player in the orange jersey is called the libero - they're the best at passing and can't attack at the net",
        "Beach volleyball has only 2 players per side, but indoor has 6 players per side",
        "Volleyball was invented in 1895 in Massachusetts - it's over 125 years old!",
    ],
    current_season="2024-25 Volleyball Season",
    trending_now=[
        "USA volleyball's strong showing at the 2024 Paris Olympics",
        "Volleyball growing as one of the most popular youth sports in the US",
    ],
    second_person_scenarios=[
        "Your team won a set 25-22. How many more points did you score than the other team?",
        "You got 8 kills, 3 blocks, and 2 aces in a match. How many total points did you directly score?",
        "You served 20 times and got 16 serves in bounds. What percentage of your serves were in?",
        "Your team needs to win 3 sets to win the match. You've won 2 and lost 1. How many more sets must you win?",
    ],
    engagement_hooks=[
        "If your team rotates 6 times per set and you play 4 sets, how many total rotations is that?",
        "Can you figure out your hitting percentage if you got 12 kills out of 30 attempts?",
    ],
    verified_stats={
        "court_dimensions": "59 feet long, 29.5 feet wide (indoor)",
        "net_height_women": "7 feet 4 inches",
        "net_height_men": "7 feet 11 inches",
        "points_to_win_set": "25 points (win by 2), 5th set is 15 points",
        "players_per_side": "6 players (indoor), 2 players (beach)",
    },
)


# =============================================================================
# ENTERTAINMENT PROFILES
# =============================================================================

GAMING_PROFILE = InterestProfile(
    name="gaming",
    display_name="Video Games & Esports",
    description="Gaming and esports-themed content with game mechanics, stats, and competitive scenarios",
    context_intro="""Make math engaging for gamers using examples from popular video games
they play. Use scenarios about scores, levels, health points, and game mechanics that
middle school gamers understand from their favorite games.""",
    basic_knowledge="""
**Common Video Game Concepts:**
- Health Points (HP): how much damage you can take before losing
- Experience Points (XP): earned by playing; enough XP levels you up
- Damage: how much HP an attack takes away
- Critical Hit (Crit): a special attack that does extra damage (usually 2x)
- Cooldown: time you have to wait before using an ability again

**Game Currencies:**
- Coins/Gold: in-game money to buy items
- Gems/Diamonds: often premium currency
- Items can have different costs in the in-game shop

**Inventory and Items:**
- Inventory: where you store your items
- Stack: multiple of the same item in one slot (like 64 blocks in Minecraft)
- Slots: spaces in your inventory (limited number)
- Rarity: common, rare, epic, legendary (rarer = usually better)

**Multiplayer Concepts:**
- K/D Ratio: kills divided by deaths
- Win Rate: wins divided by total games (as a percentage)
- Leaderboard: ranking of players by score or skill
- Matchmaking: system that finds players of similar skill

**Popular Games Kids Play:**
- Minecraft: building and survival game with blocks
- Fortnite: battle royale where 100 players compete to be last standing
- Roblox: platform with many different games created by users
- Mario games: classic Nintendo platformers
- Pokémon: catching and battling creatures with different types and stats
""",
    famous_figures=[
        # Games/Characters kids know
        "Mario", "Minecraft Steve", "Fortnite", "Roblox",
        # Streamers/YouTubers kids watch
        "MrBeast Gaming", "Ninja", "Dream",
    ],
    terminology={
        "variable": "an unknown number (like damage or health points)",
        "equation": "a math sentence to calculate damage or scores",
        "coefficient": "a multiplier (like 2x damage for a critical hit)",
        "inequality": "comparing numbers (more health, less damage)",
        "constant": "numbers that stay the same (like base damage)",
    },
    example_scenarios=[
        # Health and damage
        "You have 100 health points. An enemy hits you for 35 damage. How much health do you have left?",
        # XP and leveling
        "You need 500 XP to level up. You have 320 XP. How much more do you need?",
        # Coins and buying
        "An item costs 750 coins. You have 480 coins. How many more coins do you need?",
        # Critical hits
        "Your sword does 20 damage. A critical hit does 2 times the damage. How much damage does a critical hit do?",
        # Win-loss record
        "You've won 45 games and lost 30 games. What fraction of your games have you won?",
        # Inventory space
        "Your inventory has 36 slots. You're using 22 slots. How many empty slots do you have?",
        # Building in Minecraft
        "You need 64 blocks to build a wall. You have 4 stacks of 16 blocks. Do you have enough?",
        # Game timer
        "A game round lasts 10 minutes. If you've been playing for 6 minutes and 30 seconds, how much time is left?",
    ],
    visual_themes={
        "primary_colors": "PURPLE (rare/epic), GOLD (legendary), RED (damage), GREEN (health)",
        "imagery": "Health bars, XP bars, inventory slots, coins, level-up icons",
        "animations": "Damage numbers appearing, XP bar filling up, level up effect",
    },
    analogies={
        "solving equations": "figuring out how much damage you need to defeat an enemy",
        "variables": "unknown numbers like damage or health",
        "addition": "adding up your loot or XP",
        "subtraction": "losing health when you take damage",
        "multiplication": "critical hit multipliers (2x or 3x damage)",
        "division": "splitting coins evenly with teammates",
    },
    fun_facts=[
        "Minecraft has sold over 300 million copies - more than any other video game ever!",
        "The first video game was created in 1958 - it was a simple tennis game",
        "Fortnite has over 500 million players around the world",
        "Professional esports players can make millions of dollars playing video games",
        "Roblox has over 70 million daily active players - that's more than the population of most countries!",
        "The highest-earning esports player has won over $7 million from tournaments!",
        "A Minecraft world can be 8 times larger than the surface of Earth!",
        "The Tetris theme song is actually a 19th-century Russian folk song",
    ],
    cultural_references=[
        "'GG' (good game) - the universal sign of respect in gaming",
        "The 'F to pay respects' meme from Call of Duty",
        "'Victory Royale!' - Fortnite's iconic win screen",
        "Speed running - players use math to find the fastest routes through games",
        "Twitch streamers and YouTubers who make gaming their career",
        "The Ender Dragon fight in Minecraft - the ultimate boss battle",
        "'Clutch' plays - when a player wins against impossible odds",
    ],
    historical_trivia=[
        "Pac-Man was released in 1980 and is still one of the most recognized games ever",
        "Nintendo was founded in 1889 - they made playing cards before video games!",
        "The first gaming console was the Magnavox Odyssey in 1972",
        "Mario's original name was 'Jumpman' and he was a carpenter, not a plumber!",
        "The Game Boy was released in 1989 and sold over 118 million units",
    ],
    real_world_connections=[
        "Game designers use algebra to balance weapon damage and player health",
        "Probability determines loot drops and random encounters",
        "Game physics engines use calculus to simulate realistic movement",
        "Matchmaking systems use statistics to pair players of similar skill",
        "Speedrunners use precise frame calculations (60 FPS = 60 calculations per second)",
    ],
    motivational_quotes=[
        "The best games are those that teach you something without you realizing it. - Game Developers",
        "Every expert was once a beginner. - Gaming Wisdom",
        "Failure is just another step towards victory. - Dark Souls Philosophy",
        "The only limit is your imagination. - Minecraft",
    ],
    current_season="2024-25 Gaming Season",
    trending_now=[
        "Minecraft's 300 million copies sold milestone making it the best-selling game ever",
        "Fortnite's new seasons and collaborations with Marvel, Star Wars, and music artists",
        "Roblox growing to over 70 million daily players worldwide",
    ],
    second_person_scenarios=[
        "You have 100 HP and an enemy hits you for 35 damage. How much health do you have left?",
        "You need 500 XP to level up. You've earned 120 XP from quests and 80 XP from battles. How much more do you need?",
        "Your sword does 15 base damage. With a 2x critical hit multiplier, how much damage does your crit do?",
        "You have 1,200 coins and want to buy an item that costs 750. How many coins will you have left?",
        "You won 45 out of 75 matches this season. What's your win rate as a percentage?",
    ],
    engagement_hooks=[
        "If a loot chest has a 15% chance of dropping a legendary item, how many chests do you need to open to EXPECT one legendary?",
        "Your inventory has 36 slots and each stack holds 64 items. What's the maximum items you can carry?",
        "Can you calculate your K/D ratio if you got 18 eliminations and 6 defeats?",
    ],
    verified_stats={
        "minecraft_copies_sold": "Over 300 million copies (best-selling game ever)",
        "fortnite_players": "Over 500 million registered players",
        "roblox_daily_players": "Over 70 million daily active players",
        "minecraft_stack_size": "64 items per stack",
        "standard_fps": "60 frames per second (60 calculations per second)",
    },
)

MUSIC_PROFILE = InterestProfile(
    name="music",
    display_name="Music & Artists",
    description="Music-themed content with rhythm, charts, streaming stats, and music theory",
    context_intro="""Engage music lovers with examples about streaming numbers, chart positions,
concert ticket sales, tempo/BPM calculations, and music theory concepts. Reference
popular artists and real industry statistics that resonate with middle school students.""",
    basic_knowledge="""
**How Music Charts Work:**
- The Billboard Hot 100 ranks the most popular songs each week
- Rankings are based on streaming, radio play, and sales combined
- Going #1 means being the most popular song that week
- Artists can spend weeks or even months on the chart

**Streaming & Money:**
- Spotify, Apple Music, and YouTube are the biggest streaming platforms
- Artists earn about $0.003-0.005 per stream on Spotify
- 1 million streams = roughly $3,000-$5,000 for the artist
- "Going platinum" means 1 million units sold (or equivalent streams)

**Music Math - Tempo & Time:**
- BPM = Beats Per Minute (how fast a song is)
- Most pop songs are between 100-130 BPM
- Time signatures like 4/4 mean 4 beats per measure
- A typical song is 3-4 minutes long (180-240 seconds)

**Concert & Tour Economics:**
- Concerts sell tickets in sections (floor, lower bowl, upper deck)
- Tour revenue = ticket price × number of seats × number of shows
- Stadium concerts can hold 50,000-80,000 fans
- Arena concerts typically hold 15,000-20,000 fans
""",
    famous_figures=[
        # Pop/Mainstream that kids follow
        "Taylor Swift", "Olivia Rodrigo", "Billie Eilish", "Dua Lipa",
        # Hip-Hop/Rap
        "Drake", "Kendrick Lamar", "Travis Scott", "Doja Cat", "Ice Spice",
        # Global/K-Pop
        "BTS", "Bad Bunny", "Shakira", "NewJeans",
        # Classic references
        "The Weeknd", "Ed Sheeran", "Post Malone", "SZA",
    ],
    terminology={
        "variable": "unknown (streams, sales, BPM)",
        "equation": "calculation of totals or rates",
        "ratio": "streams per day, beats per minute",
        "inequality": "chart position comparisons",
        "coefficient": "multiplier (like royalty rate per stream)",
        "constant": "fixed values (like ticket price, song length)",
    },
    example_scenarios=[
        "Taylor Swift's Eras Tour sold out 52 shows. If each show has 70,000 fans, how many total fans attended?",
        "A song gets 5 million streams per day. How many streams in a week? In a month?",
        "An artist earns $0.004 per stream. How many streams to earn $10,000?",
        "A song is 3 minutes and 24 seconds long. How many seconds total?",
        "If a song has 120 BPM, how many beats in a 3-minute song?",
        "Tickets cost $150 for floor seats and $75 for upper seats. If you buy 2 floor and 3 upper tickets, how much do you spend?",
        "An album has 13 songs. If the average song is 3.5 minutes, how long is the whole album?",
        "A song spent 8 weeks at #1 but needs 16 weeks to break the record. How many more weeks?",
    ],
    visual_themes={
        "primary_colors": "PURPLE, PINK, GOLD, NEON_BLUE (vibrant, concert-like)",
        "imagery": "Sound waves, music notes, charts, streaming icons, concert lights, microphones",
        "animations": "Equalizer bars moving, notes floating, chart positions changing",
    },
    analogies={
        "fractions": "time signatures (4/4 means 4 beats per measure)",
        "ratios": "BPM (beats per minute), streams per day",
        "multiplication": "total streams = daily streams × number of days",
        "division": "finding average song length on an album",
        "inequalities": "comparing chart positions (lower number = better rank)",
        "solving equations": "finding how many streams needed to go platinum",
    },
    fun_facts=[
        "Taylor Swift's Eras Tour grossed over $2 billion - the highest-grossing tour ever!",
        "'Blinding Lights' by The Weeknd spent 90 weeks on the Billboard Hot 100",
        "Artists earn about $0.003-0.005 per Spotify stream",
        "Bad Bunny was the most-streamed artist on Spotify for 3 years in a row!",
        "BTS has over 75 million followers on Spotify - more than any other artist!",
        "The most-streamed song ever has over 4 billion streams",
        "A platinum album requires 1 million equivalent sales",
    ],
    cultural_references=[
        "Taylor Swift's surprise album drops and Easter eggs for fans",
        "Fan 'streaming parties' to help artists reach chart milestones",
        "TikTok making songs go viral overnight",
        "The 'Swifties' and 'BTS Army' fandoms being super dedicated",
        "Artists releasing 'deluxe' editions with bonus tracks",
        "The Spotify Wrapped yearly summary everyone shares",
    ],
    historical_trivia=[
        "The Billboard Hot 100 started in 1958 - over 65 years of tracking hits!",
        "The Beatles hold the record for most #1 hits ever with 20",
        "Music went from vinyl to CDs to MP3s to streaming in just 50 years",
        "MTV launched in 1981 - before that, you couldn't watch music videos at home",
    ],
    real_world_connections=[
        "Record labels use statistics to predict which songs will be hits",
        "Concert promoters use algebra to price tickets for maximum revenue",
        "Music producers use math to mix tracks at the right volume levels",
        "Streaming algorithms use probability to recommend songs you'll like",
        "Sound engineers use frequency equations to create perfect audio",
    ],
    motivational_quotes=[
        "Music can change the world because it can change people. - Bono",
        "I'm not a businessman. I'm a business, man. - Jay-Z",
        "Just be yourself, there is no one better. - Taylor Swift",
        "Music is the universal language of mankind. - Henry Wadsworth Longfellow",
    ],
    current_season="2024-25 Music Season",
    trending_now=[
        "Taylor Swift's Eras Tour becoming the highest-grossing concert tour in history at $2 billion+",
        "Sabrina Carpenter and Chappell Roan breaking out as the biggest new pop stars",
        "Kendrick Lamar and Drake's historic rap beef dominating music headlines",
    ],
    second_person_scenarios=[
        "You're an artist and your song gets 5 million streams per day. At $0.004 per stream, how much do you earn daily?",
        "Your concert has 20,000 seats. If floor tickets cost $150 and upper seats cost $75, and half the seats are each type, what's the total revenue if you sell out?",
        "Your new album has 14 songs averaging 3.5 minutes each. How long is the whole album?",
        "You spent 8 weeks at #3 on the charts. You need 16 weeks at #1 to break the record. How many more #1 weeks do you need?",
    ],
    engagement_hooks=[
        "If Taylor Swift earns $0.004 per Spotify stream and has 1 billion streams on one song, how much did that one song earn?",
        "Can you figure out how many concerts it takes to gross $1 billion if each show earns $13 million?",
        "Your favorite song is 3 minutes 24 seconds long. How many times can you listen to it in one hour?",
    ],
    verified_stats={
        "spotify_pay_per_stream": "$0.003-0.005 per stream",
        "platinum_requirement": "1 million equivalent units (streams count)",
        "eras_tour_gross": "Over $2 billion total (highest-grossing tour ever)",
        "typical_pop_bpm": "100-130 beats per minute",
        "stadium_capacity": "50,000-80,000 fans for stadium concerts",
    },
)

MOVIES_PROFILE = InterestProfile(
    name="movies",
    display_name="Movies & Entertainment",
    description="Movie and film-themed content with box office, ratings, and production stats",
    context_intro="""Make math engaging for movie fans using examples from Hollywood, box office
numbers, movie ratings, production budgets, and streaming statistics. Reference
blockbusters, Marvel films, and popular franchises that middle school students love.""",
    basic_knowledge="""
**Box Office Basics:**
- "Domestic" = money earned in the US and Canada
- "International" or "Worldwide" = money earned everywhere else plus domestic
- A movie's total earnings = domestic + international box office
- A movie is usually considered a hit if it earns 2-3x its production budget

**Movie Ratings:**
- Rotten Tomatoes: percentage of critics who gave a positive review (0-100%)
- IMDb: average user rating on a scale of 1-10
- A "Fresh" Rotten Tomatoes score is 60% or higher
- A "Certified Fresh" score is 75% or higher with at least 80 reviews

**Production & Costs:**
- Production budget: cost to make the movie (actors, sets, effects)
- Marketing budget: cost to advertise (often equals the production budget!)
- A typical blockbuster costs $150-300 million to produce
- Movie tickets average about $11 in the US

**Streaming:**
- Netflix, Disney+, and other platforms pay for streaming rights
- A movie can earn money from theaters AND streaming
- Some movies go straight to streaming without theaters
""",
    famous_figures=[
        # Studios/Franchises kids know
        "Marvel Studios", "Disney/Pixar",
        # Directors kids hear about
        "Christopher Nolan", "Steven Spielberg", "Greta Gerwig",
        # Young actors kids follow
        "Zendaya", "Tom Holland", "Timothée Chalamet", "Florence Pugh",
    ],
    terminology={
        "variable": "an unknown number (like box office revenue or budget)",
        "equation": "a math sentence to calculate revenue or profit",
        "inequality": "comparing numbers (more revenue, less budget)",
        "coefficient": "a multiplier (like ticket price per person)",
        "constant": "numbers that stay the same (like a fixed marketing budget)",
    },
    example_scenarios=[
        "A Marvel movie earned $450 million domestic and $800 million international. What's the worldwide total?",
        "A movie cost $200 million to make. It earned $650 million worldwide. What was the profit?",
        "Movie tickets cost $11 each. If a movie earned $55 million on opening weekend, roughly how many tickets were sold?",
        "A movie has a 92% Rotten Tomatoes score from 150 reviews. How many reviews were positive?",
        "Disney+ has 150 million subscribers paying $8 per month. How much monthly revenue is that?",
        "An animated movie took 4 years to make with 500 animators. How many animator-years of work?",
        "A movie franchise has 6 films averaging $1.2 billion each. What's the franchise total?",
        "If a 2-hour movie has 24 frames per second, how many total frames are in the movie?",
    ],
    visual_themes={
        "primary_colors": "GOLD (Oscars), RED (carpet/curtains), BLACK (theater)",
        "imagery": "Movie reels, clapboards, theater screens, star icons, popcorn",
        "animations": "Curtains opening, spotlight effect, box office counter ticking up",
    },
    analogies={
        "solving equations": "finding the missing budget or revenue figure to balance the books",
        "multiplication": "ticket price times number of tickets equals revenue",
        "percentages": "Rotten Tomatoes scores and profit margins",
        "addition": "adding domestic and international to get worldwide box office",
        "subtraction": "subtracting budget from revenue to find profit",
        "division": "splitting total revenue by number of screens for per-screen average",
    },
    fun_facts=[
        "Avatar is the highest-grossing film ever at $2.9 billion worldwide!",
        "Avengers: Endgame made $1.2 billion in its opening weekend alone",
        "The most expensive movie ever made cost over $400 million to produce",
        "Pixar's first movie, Toy Story, was made with about 800,000 lines of computer code!",
        "The average Hollywood blockbuster uses over 2,000 visual effects shots",
        "A single frame of a Pixar movie can take 24 hours to render on a computer",
    ],
    cultural_references=[
        "Marvel's post-credit scenes that everyone stays to watch",
        "Opening weekend box office battles between blockbusters",
        "The Oscars ceremony and red carpet fashion",
        "Movie trailers going viral on YouTube with millions of views",
        "Fan theories about upcoming movies taking over social media",
    ],
    historical_trivia=[
        "The first movie ever shown to an audience was in 1895 in Paris",
        "The first 'talkie' (movie with sound) was The Jazz Singer in 1927",
        "Star Wars (1977) changed the movie industry forever with special effects",
        "The first fully computer-animated feature film was Toy Story in 1995",
    ],
    real_world_connections=[
        "Movie studios use statistics to predict opening weekend performance",
        "CGI artists use geometry and linear algebra for 3D animation",
        "Film editors calculate pacing using frame rates (24 fps standard)",
        "Marketing teams use data analytics to target movie trailers to audiences",
        "Box office analysts use algebra to forecast total revenue from early trends",
    ],
    motivational_quotes=[
        "All our dreams can come true, if we have the courage to pursue them. - Walt Disney",
        "Every great film should seem new every time you see it. - Roger Ebert",
        "Imagination is more important than knowledge. - Albert Einstein (quoted in many films)",
    ],
    current_season="2024-25 Awards Season",
    trending_now=[
        "Dune: Part Two breaking box office records with $700M+ worldwide",
        "Inside Out 2 becoming the highest-grossing animated film ever at $1.6B",
        "Deadpool & Wolverine setting R-rated movie records",
    ],
    second_person_scenarios=[
        "You're a film producer and your movie cost $150 million to make. It earned $400 million worldwide. What's your profit?",
        "Your favorite streaming service costs $15 per month. How much will you spend in a year?",
        "You're reviewing movies and gave ratings of 8, 9, 7, 10, and 6 out of 10. What's your average rating?",
        "You want to watch all 27 Marvel Cinematic Universe movies. If each movie averages 2.5 hours, how many hours total?",
        "You're calculating Rotten Tomatoes scores: if 85 out of 100 critics gave a positive review, what's the score?",
    ],
    engagement_hooks=[
        "Can you figure out if a movie made money? It cost $200M to make and earned $450M worldwide (hint: marketing usually costs as much as production!)",
        "If you watch 3 movies a week for a year, how many movies is that? Can you beat 150?",
        "Quick math: A movie has 24 frames per second and is 2 hours long. How many total frames?",
    ],
    verified_stats={
        "avatar_box_office": "$2.92 billion worldwide (highest-grossing film ever)",
        "endgame_opening_weekend": "$1.2 billion opening weekend (biggest ever)",
        "film_frame_rate": "24 frames per second (standard for movies)",
        "average_ticket_price": "$11.75 average US ticket price (2024)",
        "pixar_render_time": "Up to 24 hours to render a single frame of animation",
        "imax_screen_size": "Up to 100 feet wide and 70 feet tall",
    },
)


# =============================================================================
# SCIENCE & TECH PROFILES
# =============================================================================

SPACE_PROFILE = InterestProfile(
    name="space",
    display_name="Space & Astronomy",
    description="Space and astronomy-themed content with rockets, planets, and NASA missions",
    context_intro="""Engage space enthusiasts with examples about rocket launches,
orbital mechanics, distances in space, and NASA/SpaceX missions. Use real data
about planets, satellites, and space exploration that sparks wonder and curiosity.""",
    basic_knowledge="""
**Our Solar System:**
- The Sun is at the center, with 8 planets orbiting around it
- Mercury, Venus, Earth, Mars (rocky planets) - then Jupiter, Saturn, Uranus, Neptune (gas giants)
- Earth is about 93 million miles from the Sun (called 1 AU - Astronomical Unit)
- Light travels at 186,000 miles per second (the fastest thing in the universe!)

**Rockets & Space Travel:**
- To leave Earth, rockets need to reach 'escape velocity' - about 25,000 mph!
- The International Space Station orbits Earth at 17,500 mph
- It takes about 3 days to reach the Moon, 7 months to reach Mars
- SpaceX rockets can land and be reused to save money

**Famous Space Distances:**
- Moon: 238,900 miles from Earth (about 1.3 light-seconds)
- Mars: 140 million miles on average (but it changes as planets orbit!)
- The nearest star (Proxima Centauri) is 4.24 light-years away
- Our Milky Way galaxy is 100,000 light-years across!

**Space Measurements:**
- Light-second: distance light travels in 1 second (186,000 miles)
- Light-year: distance light travels in 1 year (5.88 trillion miles!)
- AU (Astronomical Unit): Earth's distance from the Sun
""",
    famous_figures=[
        # Modern figures kids know
        "Elon Musk (SpaceX)", "NASA Artemis astronauts",
        # Historic legends
        "Neil Armstrong", "Buzz Aldrin", "Sally Ride", "Mae Jemison",
        # Science communicators
        "Neil deGrasse Tyson", "Chris Hadfield", "Bill Nye",
    ],
    terminology={
        "variable": "unknown (distance, speed, time)",
        "equation": "orbital calculation, trajectory formula",
        "coefficient": "multiplier for unit conversion",
        "ratio": "comparing distances (like Earth to Moon vs. Earth to Mars)",
        "exponents": "scientific notation for huge numbers",
    },
    example_scenarios=[
        "Light travels at 186,000 miles per second. How far does it travel in 8 minutes?",
        "The Moon is 238,900 miles away. At 25,000 mph, how long to get there?",
        "Mars is 140 million miles away. If a rocket travels at 20,000 mph, how many days to Mars?",
        "A satellite orbits Earth every 90 minutes. How many orbits in one day?",
        "The ISS travels at 17,500 mph. How far does it travel in one hour?",
        "A rocket uses 10,000 gallons of fuel per minute. How much for a 12-minute launch?",
        "Jupiter is 5 times farther from the Sun than Earth. If Earth is 93 million miles away, how far is Jupiter?",
        "An astronaut weighs 150 pounds on Earth but only 25 pounds on the Moon. What's the ratio?",
    ],
    visual_themes={
        "primary_colors": "DARK_BLUE (space), WHITE (stars), ORANGE (rockets), SILVER (spacecraft)",
        "imagery": "Planets, rockets, orbits, stars, astronauts, galaxies, satellites",
        "animations": "Rockets launching, planets orbiting, light beams traveling",
    },
    analogies={
        "solving equations": "calculating rocket trajectory or travel time",
        "large numbers": "astronomical distances require scientific notation",
        "scientific notation": "the only way to write trillion-mile distances",
        "ratios": "comparing planetary sizes or distances",
        "multiplication": "light-years to miles conversion",
        "division": "finding how long a journey takes",
    },
    fun_facts=[
        "Light takes 8 minutes to travel from the Sun to Earth",
        "SpaceX Falcon 9 rockets can land and be reused - saving millions of dollars!",
        "The footprints on the Moon will last for millions of years (no wind to blow them away!)",
        "One day on Venus is longer than one year on Venus (it spins that slowly!)",
        "You could fit 1.3 million Earths inside the Sun",
        "Neutron stars are so dense that a teaspoon would weigh 6 billion tons!",
        "There are more stars in the universe than grains of sand on all of Earth's beaches",
    ],
    cultural_references=[
        "SpaceX rocket landings that look like science fiction becoming real",
        "The Mars Perseverance rover and Ingenuity helicopter making history",
        "NASA's Artemis program planning to put the first woman on the Moon",
        "Star Wars and Star Trek inspiring real scientists and astronauts",
        "Astronauts becoming TikTok and YouTube stars from space",
    ],
    historical_trivia=[
        "The first satellite, Sputnik, was launched in 1957 - starting the Space Race",
        "Neil Armstrong walked on the Moon on July 20, 1969",
        "The Hubble Space Telescope has been in orbit since 1990",
        "The International Space Station has been continuously occupied since 2000",
    ],
    real_world_connections=[
        "Orbital mechanics uses algebra and physics to plot spacecraft trajectories",
        "NASA uses probability to calculate mission success rates",
        "Rocket scientists use calculus to optimize fuel usage",
        "GPS satellites use precise geometry to locate you on Earth",
        "Astronomers use exponential notation for cosmic distances",
    ],
    motivational_quotes=[
        "That's one small step for man, one giant leap for mankind. - Neil Armstrong",
        "The universe is under no obligation to make sense to you. - Neil deGrasse Tyson",
        "I didn't feel like a giant. I felt very, very small. - Neil Armstrong on seeing Earth from space",
        "Earth is the cradle of humanity, but one cannot live in a cradle forever. - Konstantin Tsiolkovsky",
    ],
    current_season="2024-25 Space Exploration Era",
    trending_now=[
        "Artemis program preparing to return humans to the Moon by 2025",
        "SpaceX Starship completing test flights as the most powerful rocket ever built",
        "James Webb Space Telescope revealing stunning images of distant galaxies",
    ],
    second_person_scenarios=[
        "You're planning a trip to Mars. If the distance is 140 million miles and your spacecraft travels at 25,000 mph, how many days will it take?",
        "You're an astronaut on the ISS traveling at 17,500 mph. How far do you travel in one 90-minute orbit?",
        "Your rocket uses 10,000 gallons of fuel per minute during launch. If liftoff to orbit takes 8.5 minutes, how much fuel do you need?",
        "You're sending a signal to a rover on Mars. If radio waves travel at the speed of light (186,000 miles/second), how long until you get a response from 140 million miles away?",
        "You weigh 120 pounds on Earth. On the Moon, gravity is 1/6 as strong. What would you weigh on the Moon?",
    ],
    engagement_hooks=[
        "Can you calculate how long a light-year is in miles? (Hint: light travels 186,000 miles per second, and there are about 31.5 million seconds in a year)",
        "If you could drive a car at 60 mph to the Moon (238,900 miles away), how many days would it take?",
        "Quick challenge: The ISS orbits Earth 16 times per day. How many orbits in a year?",
    ],
    verified_stats={
        "speed_of_light": "186,000 miles per second (299,792 km/s)",
        "earth_to_moon": "238,900 miles average distance",
        "earth_to_sun": "93 million miles (1 Astronomical Unit)",
        "iss_orbital_speed": "17,500 mph (completes orbit in 90 minutes)",
        "escape_velocity": "25,000 mph to leave Earth's gravity",
        "light_year_miles": "5.88 trillion miles",
    },
)

CODING_PROFILE = InterestProfile(
    name="coding",
    display_name="Coding & Technology",
    description="Programming and technology-themed content with algorithms, data, and tech examples",
    context_intro="""Make math relevant for aspiring programmers with examples about
algorithms, data structures, app development, and tech industry statistics.
Reference coding concepts that require mathematical thinking. Show students that
math IS the foundation of all programming.""",
    basic_knowledge="""
**Programming Basics:**
- Code runs line by line, top to bottom (like reading)
- Variables store values: `score = 100` means the variable "score" holds 100
- Loops repeat code a set number of times: `for i in range(10)` runs 10 times
- Conditions check true/false: `if score > 50` only runs when score is above 50

**Data & Storage:**
- 1 byte = 8 bits (a bit is a 0 or 1)
- 1 kilobyte (KB) = 1,024 bytes
- 1 megabyte (MB) = 1,024 KB (about 1 minute of MP3 music)
- 1 gigabyte (GB) = 1,024 MB (about 250 songs)
- 1 terabyte (TB) = 1,024 GB (about 500 hours of video)

**Screen & Graphics:**
- Screen resolution = width x height in pixels (1920 x 1080 = "Full HD")
- Each pixel has 3 color values (Red, Green, Blue) from 0-255
- Frame rate = how many images per second (60 fps is smooth)
- More pixels = more data = more processing power needed

**Internet & Apps:**
- Internet speed is measured in Mbps (megabits per second)
- Apps can have millions of downloads
- Popular websites handle millions of requests per second
- App Store has over 2 million apps
""",
    famous_figures=[
        # Pioneers kids learn about
        "Ada Lovelace (first programmer)", "Grace Hopper (invented compiling)",
        # Modern tech figures
        "Bill Gates", "Mark Zuckerberg", "Jensen Huang (NVIDIA)",
        # Accessible references
        "Tim Berners-Lee (invented the web)", "Linus Torvalds (Linux creator)",
    ],
    terminology={
        "variable": "a named container that stores a value (like `x = 5` in Python)",
        "equation": "an algorithm step or formula the computer solves",
        "inequality": "a conditional statement (like `if x > 5`)",
        "coefficient": "a multiplier in a formula (like the 2 in `2 * width`)",
        "constant": "a value that never changes (like `PI = 3.14159`)",
    },
    example_scenarios=[
        "A loop runs 100 times. Each time it adds 5 to a counter. What's the final value?",
        "A screen is 1920 pixels wide and 1080 tall. How many total pixels?",
        "You have 8 GB of storage. Photos are 4 MB each. How many photos can you store?",
        "A website loads in 2.5 seconds. If you optimize it to be 40% faster, what's the new load time?",
        "An app has 3 million downloads. If 15% of users are active daily, how many daily active users?",
        "A for-loop goes from 0 to 99. How many times does it execute?",
        "A video file is 1.2 GB. Your internet speed is 50 Mbps. How many seconds to download?",
        "RGB color (255, 0, 128) — if each value ranges from 0-255, how many possible colors are there?",
    ],
    visual_themes={
        "primary_colors": "GREEN (terminal/matrix), BLUE (tech/links), BLACK (code background)",
        "imagery": "Code blocks, terminal prompts, circuit patterns, binary digits, pixel grids",
        "animations": "Code typing out line by line, pixel grid filling, data flowing through nodes",
    },
    analogies={
        "variables": "named containers that store values (like boxes labeled x, y, z)",
        "solving equations": "debugging code to find where the error is",
        "inequalities": "if-else conditions that control program flow",
        "order of operations": "how code executes line by line, following operator precedence",
        "functions": "reusable blocks of code (like a recipe you call by name)",
        "multiplication": "nested loops — a loop inside a loop multiplies iterations",
    },
    fun_facts=[
        "The first computer bug was an actual moth stuck in a relay in 1947!",
        "Python is named after the comedy group Monty Python, not the snake",
        "The first programmer was Ada Lovelace in the 1840s — before computers even existed!",
        "There are about 700 programming languages in use today",
        "A Google search uses about 1,000 computers in 0.2 seconds to give you results",
        "The average smartphone has more computing power than the computers that sent astronauts to the Moon",
        "The first website ever created is still online (info.cern.ch)",
    ],
    cultural_references=[
        "GitHub contributions and 'green squares' showing coding streaks",
        "Stack Overflow being every programmer's best friend",
        "'Hello, World!' as the traditional first program everyone writes",
        "Hackathons where teams build apps in 24-48 hours",
        "AI chatbots and how they use math to generate responses",
    ],
    historical_trivia=[
        "The first electronic computer (ENIAC) weighed 30 tons and filled an entire room!",
        "The internet started in 1969 as a military project called ARPANET",
        "The first email was sent in 1971 — the message was 'QWERTYUIOP'",
        "JavaScript was created in just 10 days in 1995",
    ],
    real_world_connections=[
        "Algorithms use algebra to sort, search, and optimize data",
        "Machine learning models use statistics and linear algebra at their core",
        "Encryption that keeps your passwords safe uses prime numbers and modular arithmetic",
        "Game physics engines use calculus to simulate gravity and motion",
        "App developers use coordinate geometry for UI layouts",
    ],
    motivational_quotes=[
        "Everybody should learn to program a computer, because it teaches you how to think. - Steve Jobs",
        "The best way to predict the future is to invent it. - Alan Kay",
        "Code is like humor. When you have to explain it, it's bad. - Cory House",
        "First, solve the problem. Then, write the code. - John Johnson",
    ],
    current_season="2024-25 AI & Tech Boom",
    trending_now=[
        "AI chatbots like ChatGPT and Claude changing how we code and learn",
        "Python becoming the most popular programming language for beginners",
        "Game development with Unity and Unreal Engine more accessible than ever",
    ],
    second_person_scenarios=[
        "You're coding a game loop that runs 60 times per second. If your game runs for 5 minutes, how many loop iterations is that?",
        "Your app has 50,000 users. If 12% are active daily, how many daily active users do you have?",
        "You're storing photos at 4 MB each. Your phone has 64 GB free. How many photos can you store?",
        "Your for-loop counts from 0 to 99. How many times does the code inside run?",
        "You're downloading a 2 GB file at 100 Mbps. How many seconds will it take? (Hint: 1 byte = 8 bits)",
    ],
    engagement_hooks=[
        "Can you figure out how many colors a computer can display? (Hint: RGB values each go from 0-255, so it's 256 x 256 x 256)",
        "If a nested loop runs 10 times inside another loop that runs 10 times, how many total iterations?",
        "Quick coding challenge: What's 2 to the 10th power? (This is how many values 10 bits can represent!)",
    ],
    verified_stats={
        "full_hd_pixels": "1920 x 1080 = 2,073,600 pixels per frame",
        "4k_resolution": "3840 x 2160 = 8,294,400 pixels per frame",
        "rgb_color_count": "256 x 256 x 256 = 16,777,216 possible colors",
        "gigabyte_in_bytes": "1 GB = 1,073,741,824 bytes (2^30)",
        "app_store_apps": "Over 2 million apps on Apple App Store",
        "github_repos": "Over 200 million repositories on GitHub",
    },
)


# =============================================================================
# HOBBY PROFILES
# =============================================================================

COOKING_PROFILE = InterestProfile(
    name="cooking",
    display_name="Cooking & Baking",
    description="Culinary-themed content with recipes, measurements, and scaling",
    context_intro="""Engage food lovers with examples about recipe scaling, measurement
conversions, cooking times, and nutritional calculations. Cooking and baking are
full of fractions, ratios, and proportions — make math delicious!""",
    basic_knowledge="""
**Measurement Basics:**
- 1 tablespoon (tbsp) = 3 teaspoons (tsp)
- 1 cup = 16 tablespoons
- 1 cup = 8 fluid ounces
- 1 pound = 16 ounces
- Recipes use fractions constantly: 1/2 cup, 3/4 tsp, 1/3 cup

**Temperature:**
- Water boils at 212°F (100°C)
- Most cookies bake at 350°F (177°C)
- To convert: °F = (°C × 9/5) + 32

**Recipe Scaling:**
- To double a recipe, multiply every ingredient by 2
- To halve a recipe, divide every ingredient by 2
- Scaling from 4 servings to 6 servings: multiply by 6/4 = 1.5
- Baking is more precise than cooking — measurements matter more!

**Nutrition Labels:**
- Calories measure energy in food
- Serving size tells you what the numbers are based on
- % Daily Value is based on a 2,000-calorie diet
""",
    famous_figures=[
        "Gordon Ramsay", "Julia Child", "Joshua Weissman",
        "Matty Matheson", "Ina Garten", "Salt Bae",
    ],
    terminology={
        "variable": "an unknown ingredient amount (like how much flour you need)",
        "equation": "a recipe formula (like total = servings × calories per serving)",
        "ratio": "ingredient proportions (like 2 parts flour to 1 part sugar)",
        "fraction": "measurements (1/2 cup, 3/4 tsp, 1/3 cup)",
        "constant": "a fixed value (like 3 teaspoons in a tablespoon)",
    },
    example_scenarios=[
        "A recipe for 4 people needs 2 cups of flour. How much flour for 10 people?",
        "You need 3/4 cup of sugar but only have a 1/4 cup measure. How many scoops?",
        "A cake recipe needs 350°F. Convert to Celsius using C = (F - 32) × 5/9.",
        "One cookie has 150 calories. A batch makes 24 cookies. How many total calories?",
        "A recipe uses a 2:1 ratio of flour to sugar. If you use 3 cups of flour, how much sugar?",
        "Bread dough needs to rise for 1.5 hours. If you start at 2:15 PM, when is it ready?",
        "A pizza needs 8 minutes per pound to cook. How long for a 3.5-pound pizza?",
        "You're making lunch for 30 students. If each sandwich needs 2 slices of bread, how many slices total?",
    ],
    visual_themes={
        "primary_colors": "ORANGE (warmth), RED (heat), YELLOW (butter/golden), GREEN (fresh herbs)",
        "imagery": "Measuring cups, kitchen scales, ingredients, mixing bowls, timers",
        "animations": "Ingredients pouring, timer counting, recipe scaling up/down",
    },
    analogies={
        "fractions": "recipe measurements (half a cup, quarter teaspoon)",
        "ratios": "ingredient proportions (like 2:1 flour to sugar)",
        "multiplication": "scaling recipes up for more servings",
        "division": "scaling recipes down for fewer servings",
        "addition": "combining ingredients to get total amounts",
        "unit conversion": "converting between cups, tablespoons, and teaspoons",
    },
    fun_facts=[
        "Baking is essentially edible chemistry — precision matters more than in cooking!",
        "The basic bread ratio is 5 parts flour to 3 parts water — a simple ratio creates magic!",
        "A chef's hat traditionally has 100 pleats, representing 100 ways to cook an egg",
        "The world's largest pizza was over 13,000 square feet — that's a LOT of math to figure out the ingredients!",
        "Chocolate chip cookies were invented by accident in 1938",
        "Professional bakers weigh ingredients in grams instead of using cups — it's more precise!",
    ],
    cultural_references=[
        "Cooking competition shows like MasterChef and Chopped",
        "YouTube cooking channels with millions of subscribers",
        "TikTok recipe trends going viral overnight",
        "Gordon Ramsay's famous 'It's RAW!' reactions",
        "The Great British Bake Off making baking cool for everyone",
    ],
    historical_trivia=[
        "The first cookbook was written around 1700 BC in ancient Mesopotamia!",
        "Ice cream was invented in China around 200 BC using snow and milk",
        "The microwave oven was invented by accident in 1945 when a candy bar melted near radar equipment",
    ],
    real_world_connections=[
        "Professional bakers use ratios (baker's percentages) where every ingredient is relative to flour weight",
        "Nutritionists use algebra to calculate meal plans that meet daily calorie goals",
        "Restaurant managers use multiplication and division to scale recipes for large groups",
        "Food scientists use chemistry (which is applied math!) to develop new products",
        "Supply chain math determines how much food to order for restaurants and cafeterias",
    ],
    motivational_quotes=[
        "Cooking is like love. It should be entered into with abandon or not at all. - Julia Child",
        "The only time to eat diet food is while waiting for the steak to cook. - Julia Child",
        "People who love to eat are always the best people. - Julia Child",
    ],
    current_season="2024-25 Food Trends",
    trending_now=[
        "Air fryer recipes taking over TikTok and YouTube cooking channels",
        "Viral baked feta pasta and other one-pot social media recipes",
        "Home sourdough baking continuing to be popular since the pandemic",
    ],
    second_person_scenarios=[
        "You're baking cookies for your class of 28 students. If each batch makes 12 cookies, how many batches do you need so everyone gets at least 2?",
        "Your recipe serves 4 people, but you're cooking for 10. If the original calls for 2 cups of flour, how much do you need now?",
        "You're making lemonade with a ratio of 1 part lemon juice to 4 parts water. If you use 2 cups of lemon juice, how much water?",
        "Your oven is set to 350 degrees F. What's that in Celsius? (Use: C = (F - 32) x 5/9)",
        "You need 3/4 cup of sugar but only have a 1/4 cup measuring cup. How many scoops?",
    ],
    engagement_hooks=[
        "Can you convert this recipe? It needs 2 cups of flour for 8 servings. How much for 20 servings?",
        "Quick math: If 1 tablespoon = 3 teaspoons and you need 6 tablespoons, how many teaspoons is that?",
        "Challenge: A pizza bakes for 8 minutes per pound. Your pizza weighs 2.5 pounds. How long should you bake it?",
    ],
    verified_stats={
        "tablespoon_to_teaspoon": "1 tablespoon = 3 teaspoons",
        "cup_to_tablespoon": "1 cup = 16 tablespoons",
        "water_boiling_point": "212 degrees F (100 degrees C)",
        "cookie_baking_temp": "350-375 degrees F (175-190 degrees C)",
        "bread_flour_ratio": "5 parts flour to 3 parts water (by weight)",
        "egg_substitute": "1 egg = 1/4 cup applesauce or mashed banana",
    },
)

ART_PROFILE = InterestProfile(
    name="art",
    display_name="Art & Design",
    description="Art and design-themed content with proportions, geometry, and color theory",
    context_intro="""Engage creative students with examples about proportions,
perspective, geometric patterns, color mixing, and design principles.
Show how math underlies beautiful artwork — geometry, ratios, and symmetry
are the secret tools of every great artist.""",
    basic_knowledge="""
**The Golden Ratio:**
- The golden ratio is approximately 1.618 (often called "phi")
- Rectangles with sides in ratio 1:1.618 are considered visually pleasing
- Found in nature (shells, flowers) and famous art (Mona Lisa, Parthenon)

**Color Theory:**
- Primary colors: Red, Blue, Yellow (can't be mixed from other colors)
- Secondary colors: Orange (R+Y), Green (B+Y), Purple (R+B)
- RGB color model: Red 0-255, Green 0-255, Blue 0-255 = 16.7 million colors!
- Complementary colors are opposite on the color wheel

**Perspective & Proportion:**
- Vanishing point: where parallel lines appear to meet in a drawing
- Scale factor: how much bigger or smaller a copy is compared to the original
- Human body proportions: approximately 7-8 head-heights tall
- One-point perspective uses a single vanishing point on the horizon

**Symmetry:**
- Line symmetry: one half mirrors the other (like a butterfly)
- Rotational symmetry: shape looks the same after rotation (like a star)
- Tessellations: patterns that tile a surface with no gaps (like M.C. Escher's work)
""",
    famous_figures=[
        "Leonardo da Vinci", "Frida Kahlo", "Banksy", "Yayoi Kusama",
        "KAWS", "Takashi Murakami", "Bob Ross",
    ],
    terminology={
        "variable": "an unknown dimension or value (like canvas width)",
        "ratio": "proportions in artwork (like the golden ratio 1:1.618)",
        "equation": "a formula for calculating dimensions or color values",
        "symmetry": "mathematical balance and reflection in design",
        "geometry": "shapes, angles, and perspectives in artwork",
    },
    example_scenarios=[
        "A canvas is 24 inches wide. Using the golden ratio (1:1.618), how tall should it be?",
        "You want to enlarge a 4x6 inch drawing to fit a 12-inch-wide frame. What's the scale factor and new height?",
        "To mix orange paint, you use 2 parts red and 1 part yellow. How much of each for 12 ounces total?",
        "A hexagonal pattern has 6 equal sides. If each side is 3 cm, what's the perimeter?",
        "A mural is 8 feet wide and 5 feet tall. If paint covers 50 sq ft per gallon, how many gallons needed?",
        "An artist's color palette uses RGB. If red=200, green=100, blue=50, what percentage of max (255) is each?",
        "A tile pattern repeats every 6 inches. How many tiles fit across a 4-foot wall?",
        "A perspective drawing has lines meeting at a vanishing point. If two lines start 10 inches apart and converge at 20 inches away, what angle do they form?",
    ],
    visual_themes={
        "primary_colors": "Full rainbow palette, GOLD (golden ratio), PURPLE (creativity)",
        "imagery": "Canvases, brushes, geometric patterns, color wheels, spirals",
        "animations": "Golden spiral drawing, color wheel mixing, symmetry reflections",
    },
    analogies={
        "ratios": "proportions in portraits and the golden ratio",
        "geometry": "shapes, angles, and perspectives in artwork",
        "symmetry": "reflection and balance in design",
        "fractions": "mixing paint colors in exact proportions",
        "multiplication": "scaling artwork up using a scale factor",
        "area": "calculating how much canvas or paint is needed",
    },
    fun_facts=[
        "The golden ratio (1.618...) appears in sunflowers, seashells, galaxies, and famous paintings!",
        "Leonardo da Vinci filled over 7,000 pages with notes combining art, math, and science",
        "The Mona Lisa uses the golden ratio in the proportions of her face",
        "M.C. Escher created impossible mathematical illusions using geometry and tessellations",
        "Pixar animators use mathematical curves called 'splines' to create smooth character movements",
        "A standard color display can show 16.7 million colors — that's 256 × 256 × 256!",
    ],
    cultural_references=[
        "Bob Ross's 'happy little trees' and his calm painting tutorials",
        "Digital art and Procreate/Photoshop becoming as popular as traditional art",
        "NFT digital art selling for millions of dollars",
        "Street art and murals transforming neighborhoods",
        "TikTok art timelapses going viral with millions of views",
    ],
    historical_trivia=[
        "Ancient Egyptians used mathematical proportions to build pyramids and create art",
        "The Renaissance (1400s-1600s) was when artists first used mathematical perspective in paintings",
        "Islamic art uses complex geometric patterns because of cultural emphasis on mathematics",
        "The color wheel was invented by Isaac Newton in 1666",
    ],
    real_world_connections=[
        "Graphic designers use coordinate grids and alignment math daily",
        "Architects use geometry and scale drawings to design buildings",
        "Fashion designers use proportions and measurement math for patterns",
        "Video game artists use 3D coordinate systems (x, y, z) for digital worlds",
        "UI/UX designers use golden ratio and grids for beautiful app layouts",
    ],
    motivational_quotes=[
        "Art is not what you see, but what you make others see. - Edgar Degas",
        "Where the spirit does not work with the hand, there is no art. - Leonardo da Vinci",
        "Creativity takes courage. - Henri Matisse",
        "Every artist was first an amateur. - Ralph Waldo Emerson",
    ],
    current_season="2024-25 Digital Art Era",
    trending_now=[
        "Procreate and digital art tablets making illustration accessible to everyone",
        "AI art tools sparking debates about creativity and copyright",
        "Street art and murals gaining mainstream recognition in galleries",
    ],
    second_person_scenarios=[
        "You're painting a mural that's 8 feet wide. Using the golden ratio (1:1.618), how tall should it be for perfect proportions?",
        "You want to enlarge your 4x6 inch sketch to fit a 16-inch wide frame. What's the scale factor, and how tall will it be?",
        "You're mixing paint: 2 parts blue to 1 part yellow makes green. If you need 9 ounces of green, how much blue and yellow?",
        "Your digital canvas is 1920x1080 pixels. If you want to print it at 300 DPI, how many inches wide will the print be?",
        "You're tiling a mosaic with hexagons. Each hexagon has 6 sides of 2 inches each. What's the perimeter of one hexagon?",
    ],
    engagement_hooks=[
        "Can you calculate how many colors your screen displays? (Hint: each pixel has RGB values from 0-255)",
        "Challenge: A canvas is 24 inches wide. Using the golden ratio (1.618), what height makes it most pleasing to the eye?",
        "Quick math: If paint covers 50 square feet per gallon, how many gallons for a 10-foot by 12-foot wall?",
    ],
    verified_stats={
        "golden_ratio": "1.618 (approximately) - appears in nature and famous artwork",
        "rgb_color_range": "256 x 256 x 256 = 16.7 million possible colors",
        "mona_lisa_size": "30 inches x 21 inches (77 cm x 53 cm)",
        "standard_canvas_sizes": "8x10, 11x14, 16x20, 18x24 inches (common)",
        "print_resolution": "300 DPI (dots per inch) for high-quality prints",
        "color_wheel_colors": "12 colors on the traditional color wheel",
    },
)


# =============================================================================
# ANIME & MANGA PROFILE
# =============================================================================

ANIME_PROFILE = InterestProfile(
    name="anime",
    display_name="Anime & Manga",
    description="Anime and manga-themed content with references to popular series, characters, and Japanese culture",
    context_intro="""Engage anime and manga fans with examples from popular series,
character power levels, episode counts, and manga volume sales. Reference beloved
shows that middle school students watch and discuss with friends.""",
    basic_knowledge="""
**What is Anime & Manga?**
- Anime: Japanese animated shows and movies
- Manga: Japanese comic books (read right to left!)
- Episodes air weekly in "seasons" or "cours" (about 12-24 episodes)
- Popular series can run for hundreds of episodes

**Streaming & Watching:**
- Crunchyroll and Netflix are popular anime streaming services
- New episodes often release on specific days of the week
- "Simulcast" means episodes air in Japan and internationally at the same time

**Power Levels & Stats:**
- Many anime feature characters with measurable power levels
- Characters often have stats for strength, speed, intelligence, etc.
- Training "arcs" show characters getting stronger over time

**Manga Sales:**
- Best-selling manga sell millions of copies worldwide
- Manga is released in weekly magazines, then collected into "volumes"
- One Piece has sold over 500 million copies - more than any other manga!

**Common Terms:**
- Shonen: action anime aimed at young boys (Naruto, Dragon Ball, My Hero Academia)
- Shojo: anime aimed at young girls (Sailor Moon, Fruits Basket)
- OVA: Original Video Animation (special episodes)
- Filler: episodes not from the original manga story
""",
    famous_figures=[
        # Series/Characters everyone knows
        "Naruto", "Goku (Dragon Ball)", "Luffy (One Piece)", "Deku (My Hero Academia)",
        "Tanjiro (Demon Slayer)", "Gojo (Jujutsu Kaisen)", "Eren (Attack on Titan)",
        # More recent hits
        "Anya (Spy x Family)", "Denji (Chainsaw Man)", "Frieren",
        # Classic references
        "Pikachu (Pokemon)", "Sailor Moon", "Totoro",
    ],
    terminology={
        "variable": "unknown value (like a character's hidden power level)",
        "equation": "calculating total power or episode count",
        "inequality": "comparing power levels between characters",
        "exponents": "power-ups that multiply strength",
        "ratio": "win-loss ratios in battles",
    },
    example_scenarios=[
        "Naruto has 720 episodes total. If you watch 5 episodes per day, how many days to finish?",
        "Goku's power level is 9,000. After training, it multiplies by 50. What's his new power level?",
        "One Piece has 1,100 chapters. If each chapter takes 10 minutes to read, how many hours total?",
        "A manga sells 2 million copies per volume. With 25 volumes, how many total copies?",
        "Demon Slayer Season 1 has 26 episodes at 24 minutes each. How many hours total?",
        "If a character's speed stat is 85 and strength is 92, what's their average stat?",
        "A weekly manga releases 52 chapters per year. How many chapters in 5 years?",
        "Two characters have power levels of 8,500 and 12,000. What's the difference?",
    ],
    visual_themes={
        "primary_colors": "VIBRANT colors - RED, BLUE, GOLD, BLACK (action style)",
        "imagery": "Speed lines, power auras, manga panels, character silhouettes",
        "animations": "Power-up effects, dramatic reveals, action sequences",
    },
    analogies={
        "solving equations": "calculating how many episodes to reach a goal",
        "variables": "unknown power levels to discover",
        "multiplication": "power multipliers when characters transform",
        "division": "splitting training time across skills",
        "inequalities": "comparing power levels between heroes and villains",
        "exponents": "power levels going from 9,000 to 9 million through transformations",
    },
    fun_facts=[
        "One Piece has sold over 500 million manga copies - it's the best-selling manga ever!",
        "Demon Slayer became the highest-grossing anime film ever in 2020",
        "Dragon Ball Z's 'Over 9000!' line is one of the most famous anime memes",
        "Pokemon is the highest-grossing media franchise in the world - worth $100+ billion!",
        "Naruto's creator drew over 700 chapters by hand over 15 years",
        "Attack on Titan's finale was watched by millions worldwide simultaneously",
        "Studio Ghibli films (like Spirited Away) have won Academy Awards",
    ],
    cultural_references=[
        "The 'Plus Ultra!' motto from My Hero Academia (means 'Go Beyond!')",
        "Goku's iconic Kamehameha attack and transformation screams",
        "Naruto running pose that fans imitate (running with arms back)",
        "The 'Talk no Jutsu' joke about Naruto convincing villains to be good",
        "'Believe it!' - Naruto's famous catchphrase",
        "Jujutsu Kaisen's 'Domain Expansion' being everyone's favorite move",
    ],
    historical_trivia=[
        "Astro Boy (1963) was one of the first anime TV series ever made",
        "Dragon Ball started in 1984 and is still making new content!",
        "Pokemon released in 1996 and became a worldwide phenomenon",
        "Anime became globally popular through VHS tapes shared by fans in the 1990s",
    ],
    real_world_connections=[
        "Animators use geometry to create perspective and movement",
        "Manga artists calculate panel layouts using ratios and proportions",
        "Streaming platforms use algorithms to recommend shows you'll like",
        "Game developers balance character stats using algebra",
        "Voice actors record at specific frame rates (24 frames per second)",
    ],
    motivational_quotes=[
        "Believe it! - Naruto Uzumaki",
        "Plus Ultra! - My Hero Academia",
        "Power comes in response to a need, not a desire. - Goku",
        "If you don't like the hand fate dealt you, fight for a new one. - Naruto",
        "I'll take a potato chip... and eat it! - Light Yagami (Death Note)",
    ],
    current_season="Winter 2025 Anime Season",
    trending_now=[
        "Solo Leveling anime adaptation breaking streaming records",
        "Jujutsu Kaisen Season 2 dominating social media discussions",
        "Frieren: Beyond Journey's End winning anime of the year awards",
    ],
    second_person_scenarios=[
        "You want to watch all of Naruto (720 episodes). If you watch 4 episodes per day, how many days will it take?",
        "Your favorite character's power level starts at 5,000 and doubles after each training arc. After 3 arcs, what's the power level?",
        "You're collecting manga volumes at $10 each. If a series has 25 volumes, how much to collect them all?",
        "An anime episode is 24 minutes. If you binge-watch 12 episodes, how many hours is that?",
        "You're rating anime: you gave scores of 9, 8, 10, 7, and 8. What's your average score?",
    ],
    engagement_hooks=[
        "Can you calculate how long it takes to finish One Piece? (1,100+ chapters at 10 minutes each)",
        "If Goku's power level is 9,000 and it multiplies by 50 when he goes Super Saiyan, what's his new level?",
        "Quick challenge: A weekly manga releases 52 chapters per year. How many years for 500 chapters?",
    ],
    verified_stats={
        "one_piece_volumes": "107+ volumes, 500+ million copies sold worldwide",
        "naruto_episodes": "720 total episodes (220 original + 500 Shippuden)",
        "demon_slayer_movie": "$504 million box office (highest-grossing anime film)",
        "pokemon_franchise_value": "$100+ billion (highest-grossing media franchise ever)",
        "anime_frame_rate": "24 frames per second (standard animation)",
        "weekly_shonen_jump": "Weekly magazine with 2+ million circulation",
    },
)


# =============================================================================
# ANIMALS & NATURE PROFILE
# =============================================================================

ANIMALS_PROFILE = InterestProfile(
    name="animals",
    display_name="Animals & Wildlife",
    description="Animal and nature-themed content with fascinating creatures, conservation, and biology",
    context_intro="""Engage animal lovers with examples about wildlife populations,
animal speeds, habitats, and conservation. Use real data about favorite animals
that sparks curiosity about the natural world.""",
    basic_knowledge="""
**Animal Speeds:**
- Cheetah: 70 mph (fastest land animal)
- Peregrine falcon: 240 mph diving (fastest animal ever!)
- Sailfish: 68 mph (fastest fish)
- Human: ~28 mph (Usain Bolt's top speed)

**Animal Sizes:**
- Blue whale: 100 feet long, 200 tons (largest animal ever!)
- Elephant: 13 feet tall, 6 tons (largest land animal)
- Giraffe: 18 feet tall (tallest animal)
- Hummingbird: 2-3 inches (one of the smallest birds)

**Animal Lifespans:**
- Mayfly: 24 hours
- Dog: 10-13 years
- Elephant: 70 years
- Tortoise: 100+ years
- Some jellyfish: potentially immortal!

**Conservation Numbers:**
- Endangered means fewer than 2,500 adults remain
- Many species have recovered from near extinction
- Zoos and sanctuaries help protect rare animals
- Wildlife populations have declined 69% since 1970

**Population & Groups:**
- A group of wolves is called a "pack" (5-10 wolves)
- A group of fish is called a "school" (can be millions!)
- A group of birds is called a "flock"
""",
    famous_figures=[
        # Animals kids love
        "Lions", "Tigers", "Elephants", "Dolphins", "Wolves",
        "Pandas", "Penguins", "Sharks", "Whales", "Dogs", "Cats",
        # Famous individual animals or mascots
        "David Attenborough (nature documentaries)",
        "Steve Irwin (Crocodile Hunter)",
        "Jane Goodall (chimpanzee researcher)",
    ],
    terminology={
        "variable": "unknown (population count, speed, distance)",
        "equation": "calculating animal populations or distances",
        "ratio": "comparing sizes or speeds of different animals",
        "inequality": "comparing populations (endangered vs. thriving)",
        "average": "typical lifespan or speed",
    },
    example_scenarios=[
        "A cheetah runs at 70 mph. How far can it run in 30 seconds?",
        "A blue whale is 100 feet long. A human is 6 feet. How many humans equal one whale?",
        "A wolf pack has 8 wolves. If 3 packs live in the forest, how many wolves total?",
        "Elephants drink 50 gallons of water per day. How much in a week?",
        "A penguin colony has 5,000 penguins. If 200 new chicks are born each month, how many after 6 months?",
        "A sea turtle swims 35 miles per day. How far in 2 weeks?",
        "If a species has 2,000 animals and the population grows by 5% per year, how many next year?",
        "A hummingbird beats its wings 80 times per second. How many beats in one minute?",
    ],
    visual_themes={
        "primary_colors": "GREEN (nature), BROWN (earth), BLUE (ocean), ORANGE (wildlife)",
        "imagery": "Animals, habitats, nature scenes, paw prints, wildlife photography",
        "animations": "Animals running, birds flying, fish swimming, population graphs",
    },
    analogies={
        "solving equations": "calculating how many animals in a population",
        "variables": "unknown population counts to discover",
        "multiplication": "growth rates for animal populations",
        "division": "sharing territory or resources among animals",
        "ratios": "comparing sizes of different species",
        "inequalities": "endangered vs. stable populations",
    },
    fun_facts=[
        "A blue whale's heart is the size of a small car!",
        "Octopuses have three hearts and blue blood",
        "A group of flamingos is called a 'flamboyance'",
        "Crows can remember human faces and hold grudges!",
        "A shrimp's heart is in its head",
        "Elephants are the only animals that can't jump",
        "A cheetah can accelerate faster than most sports cars",
        "Dolphins sleep with one eye open (half their brain stays awake!)",
    ],
    cultural_references=[
        "Planet Earth and nature documentaries everyone watches",
        "Viral animal videos on social media",
        "Zoo and aquarium visits as popular family activities",
        "Animal crossing (the game!) and virtual pet games",
        "Wildlife conservation efforts and 'adopt an animal' programs",
    ],
    historical_trivia=[
        "Dinosaurs went extinct 65 million years ago",
        "The dodo bird went extinct in the 1600s due to hunting",
        "Bald eagles were nearly extinct but have recovered thanks to conservation",
        "The first zoo opened in Vienna in 1752",
    ],
    real_world_connections=[
        "Wildlife biologists use statistics to track animal populations",
        "Conservation efforts use math to predict species survival",
        "Veterinarians calculate medicine doses based on animal weight",
        "Ecologists use ratios to measure biodiversity",
        "Migration patterns are tracked using GPS and math",
    ],
    motivational_quotes=[
        "The greatness of a nation can be judged by the way its animals are treated. - Mahatma Gandhi",
        "Look deep into nature, and you will understand everything better. - Albert Einstein",
        "In the end, we will conserve only what we love. - Baba Dioum",
        "The wildlife and its habitat cannot speak, so we must. - Theodore Roosevelt",
    ],
    current_season="2024-25 Wildlife Conservation Year",
    trending_now=[
        "Giant panda population recovering thanks to conservation efforts",
        "Whale migration tracking apps letting anyone follow ocean journeys",
        "Wildlife camera traps capturing amazing footage shared on social media",
    ],
    second_person_scenarios=[
        "You're tracking a wolf pack with 12 wolves. If 3 pups are born each spring, how many wolves after 2 years?",
        "You're a marine biologist and spot a blue whale that's 90 feet long. A school bus is 45 feet. How many buses long is the whale?",
        "Your local zoo has 250 animals. If 15% are endangered species, how many endangered animals are there?",
        "You're timing a cheetah that runs 70 mph. How many feet does it cover in 5 seconds? (1 mile = 5,280 feet)",
        "You're counting birds for a survey. You count 45, 38, 52, 41, and 49 birds over 5 days. What's the average per day?",
    ],
    engagement_hooks=[
        "Can you figure out how many times a hummingbird's wings beat in one minute if they beat 80 times per second?",
        "If a sea turtle swims 35 miles per day, how far does it travel during a 60-day migration?",
        "Quick challenge: An elephant drinks 50 gallons of water per day. How many gallons in a week?",
    ],
    verified_stats={
        "cheetah_speed": "70 mph top speed (fastest land animal)",
        "blue_whale_length": "Up to 100 feet long (largest animal ever)",
        "hummingbird_wingbeats": "Up to 80 beats per second",
        "elephant_daily_water": "50 gallons of water per day",
        "peregrine_falcon_dive": "240 mph diving speed (fastest animal)",
        "ant_strength": "Can lift 50 times their body weight",
    },
)


# =============================================================================
# FASHION & BEAUTY PROFILE
# =============================================================================

FASHION_PROFILE = InterestProfile(
    name="fashion",
    display_name="Fashion & Style",
    description="Fashion and style-themed content with design, measurements, and industry math",
    context_intro="""Engage fashion enthusiasts with examples about clothing measurements,
fabric calculations, pricing, and runway show statistics. Connect math to the
creative world of design and personal style.""",
    basic_knowledge="""
**Clothing Sizes & Measurements:**
- Sizes vary by brand and country (US, EU, UK all different!)
- Common measurements: bust, waist, hips, inseam
- Tailoring uses precise measurements in inches or centimeters

**Fabric & Materials:**
- Fabric is sold by the yard or meter
- Pattern pieces show how to cut fabric efficiently
- Fabric width is typically 45 or 60 inches

**Fashion Industry Numbers:**
- Fashion Week happens 4 times per year (2 main + 2 resort/pre-fall)
- A typical runway show features 30-50 looks
- The fashion industry is worth $1.7 trillion globally

**Discounts & Pricing:**
- Sales often offer 20%, 30%, 50% off
- Original price × (1 - discount rate) = sale price
- Designer items have high markups over production cost
""",
    famous_figures=[
        "Coco Chanel", "Virgil Abloh", "Rihanna (Fenty)", "Zendaya",
        "Pharrell Williams", "Nike", "Adidas", "Shein", "Fashion Nova",
    ],
    terminology={
        "variable": "unknown (price, measurements, quantity)",
        "equation": "calculating sale prices or fabric needed",
        "ratio": "proportions for patterns and sizing",
        "percentage": "discounts and markups",
    },
    example_scenarios=[
        "A dress costs $80 and is 25% off. What's the sale price?",
        "You need 3 yards of fabric at $12 per yard. What's the total cost?",
        "A designer sells 500 shirts at $45 each. What's the total revenue?",
        "Your waist measures 28 inches. What size are you in a brand where size 6 = 27-29 inches?",
        "A runway show has 40 looks. If each model wears 5 looks, how many models are needed?",
        "You're budgeting $200 for clothes. If jeans cost $65 and tops average $35, how many of each can you buy?",
    ],
    visual_themes={
        "primary_colors": "BLACK, WHITE, PINK, GOLD (elegant, stylish)",
        "imagery": "Clothing racks, runway, measuring tape, fabric swatches",
    },
    analogies={
        "percentages": "calculating discounts and sale prices",
        "ratios": "proportions for body measurements",
        "multiplication": "fabric needed × price per yard",
        "budgeting": "planning outfits within a spending limit",
    },
    fun_facts=[
        "Coco Chanel popularized the 'little black dress' in the 1920s",
        "Sneakers are now considered fashion - the resale market is worth billions!",
        "The average American buys 68 pieces of clothing per year",
        "Fashion Week shows in New York, London, Milan, and Paris attract thousands",
    ],
    cultural_references=[
        "TikTok fashion hauls and outfit of the day (OOTD) videos",
        "Thrift flipping - buying cheap clothes and restyling them",
        "Sneaker culture and limited-edition drops",
        "Sustainable fashion and upcycling trends",
    ],
    historical_trivia=[
        "Blue jeans were invented in 1873 for miners and workers",
        "The first Fashion Week was held in New York in 1943",
        "Sneakers were originally called 'plimsolls' in the 1800s",
    ],
    real_world_connections=[
        "Fashion designers use geometry for pattern making",
        "Retailers use statistics to predict trending styles",
        "Fabric cutting optimizes material usage (minimal waste)",
        "Inventory management uses algebra for stock levels",
    ],
    motivational_quotes=[
        "Fashion is about dressing according to what's fashionable. Style is more about being yourself. - Oscar de la Renta",
        "Give a girl the right shoes, and she can conquer the world. - Marilyn Monroe",
        "Style is a way to say who you are without having to speak. - Rachel Zoe",
    ],
    current_season="Spring/Summer 2025 Fashion Season",
    trending_now=[
        "Y2K fashion making a comeback with low-rise jeans and butterfly clips",
        "Sustainable thrifting and vintage shopping becoming mainstream",
        "Sneaker culture and limited-edition drops selling out in seconds",
    ],
    second_person_scenarios=[
        "You found a jacket that's normally $120, but it's 35% off. What's the sale price?",
        "You're making a skirt and need 2.5 yards of fabric at $8 per yard. What's your fabric cost?",
        "Your clothing budget is $150. If jeans cost $45 and tops cost $25, how many of each can you buy to use exactly $150?",
        "You're organizing your closet and have 48 items. If 25% are pants, how many pants do you have?",
        "A runway show has 36 looks. If each model walks 4 times, how many models are needed?",
    ],
    engagement_hooks=[
        "Can you calculate the real price? A $80 dress is 40% off, but then there's 8% sales tax on the sale price.",
        "Quick math: If you buy 3 shirts at 2-for-1 pricing ($30 each), how much do you actually pay?",
        "Challenge: Your waist is 26 inches. If size Small = 25-27 inches and Medium = 28-30 inches, which size?",
    ],
    verified_stats={
        "fashion_industry_value": "$1.7 trillion global industry",
        "average_clothing_per_year": "68 pieces bought by average American annually",
        "fashion_week_shows": "400+ shows during New York Fashion Week alone",
        "fabric_width_standard": "45 or 60 inches (most common fabric widths)",
        "runway_show_length": "10-15 minutes average for a fashion show",
        "sneaker_resale_market": "$6+ billion annual sneaker resale market",
    },
)


# =============================================================================
# REGISTRY
# =============================================================================

INTEREST_PROFILES: Dict[str, InterestProfile] = {
    # Sports
    "basketball": BASKETBALL_PROFILE,
    "nba": BASKETBALL_PROFILE,  # alias
    "football": FOOTBALL_PROFILE,
    "nfl": FOOTBALL_PROFILE,  # alias
    "soccer": SOCCER_PROFILE,
    "tennis": TENNIS_PROFILE,
    "volleyball": VOLLEYBALL_PROFILE,

    # Entertainment
    "gaming": GAMING_PROFILE,
    "esports": GAMING_PROFILE,  # alias
    "videogames": GAMING_PROFILE,  # alias
    "music": MUSIC_PROFILE,
    "movies": MOVIES_PROFILE,
    "film": MOVIES_PROFILE,  # alias

    # Science & Tech
    "space": SPACE_PROFILE,
    "astronomy": SPACE_PROFILE,  # alias
    "coding": CODING_PROFILE,
    "programming": CODING_PROFILE,  # alias
    "tech": CODING_PROFILE,  # alias

    # Hobbies
    "cooking": COOKING_PROFILE,
    "baking": COOKING_PROFILE,  # alias
    "art": ART_PROFILE,
    "design": ART_PROFILE,  # alias

    # Pop Culture
    "anime": ANIME_PROFILE,
    "manga": ANIME_PROFILE,  # alias
    "otaku": ANIME_PROFILE,  # alias

    # Nature
    "animals": ANIMALS_PROFILE,
    "wildlife": ANIMALS_PROFILE,  # alias
    "nature": ANIMALS_PROFILE,  # alias
    "pets": ANIMALS_PROFILE,  # alias

    # Fashion
    "fashion": FASHION_PROFILE,
    "style": FASHION_PROFILE,  # alias
    "clothes": FASHION_PROFILE,  # alias
}


def get_interest_profile(interest: str) -> Optional[InterestProfile]:
    """
    Get an interest profile by name.

    Args:
        interest: Interest name (case-insensitive)

    Returns:
        InterestProfile if found, None otherwise
    """
    return INTEREST_PROFILES.get(interest.lower().strip())


def list_available_interests() -> List[str]:
    """
    Get list of available interest names (excluding aliases).

    Returns:
        List of unique interest names
    """
    # Return unique profiles by checking identity
    seen = set()
    unique = []
    for name, profile in INTEREST_PROFILES.items():
        if id(profile) not in seen:
            seen.add(id(profile))
            unique.append(name)
    return sorted(unique)
