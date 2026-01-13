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

**Important Guidelines:**
1. Replace generic examples with {self.name}-themed scenarios
2. Use terminology familiar to {self.name} fans
3. Reference real statistics, scores, or metrics when possible
4. Keep the math rigorous while making context fun and relatable
5. Include at least one fun fact or real-world application
6. Use the basic knowledge above to ensure accuracy
7. Sprinkle in cultural references to make content feel current and relatable
8. Connect historical facts to show math's importance in the field
"""


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
    ]
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
    ]
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
    ]
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
    ]
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
    ]
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
    ]
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
    ]
)

MOVIES_PROFILE = InterestProfile(
    name="movies",
    display_name="Movies & Entertainment",
    description="Movie and film-themed content with box office, ratings, and production stats",
    context_intro="""Make math engaging with examples from Hollywood, box office numbers,
movie ratings, production budgets, and streaming statistics. Reference blockbusters,
Marvel films, and popular franchises.""",
    famous_figures=[
        "Marvel Studios", "Disney", "Christopher Nolan", "Steven Spielberg",
        "Greta Gerwig", "Zendaya", "Timothée Chalamet", "Tom Holland"
    ],
    terminology={
        "variable": "unknown (revenue, budget, rating)",
        "equation": "box office calculation",
        "inequality": "budget vs. revenue comparisons",
    },
    example_scenarios=[
        "Calculating worldwide box office from domestic + international",
        "Finding budget needed for production if profit is known",
        "Computing ROI (return on investment) for a film",
        "Determining ticket sales from revenue and ticket price",
        "Calculating Rotten Tomatoes score from reviews",
    ],
    visual_themes={
        "primary_colors": "GOLD (Oscars), RED (carpet), BLACK (theater)",
        "imagery": "Movie reels, clapboards, theater screens, stars",
    },
    analogies={
        "solving equations": "finding the missing budget or revenue figure",
        "multiplication": "ticket price × number of tickets = revenue",
        "percentages": "Rotten Tomatoes scores, profit margins",
    },
    fun_facts=[
        "Avatar is the highest-grossing film at $2.9 billion worldwide",
        "Avengers: Endgame made $1.2 billion in its opening weekend",
    ]
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
    ]
)

CODING_PROFILE = InterestProfile(
    name="coding",
    display_name="Coding & Technology",
    description="Programming and technology-themed content with algorithms, data, and tech examples",
    context_intro="""Make math relevant for aspiring programmers with examples about
algorithms, data structures, app development, and tech industry statistics.
Reference coding concepts that require mathematical thinking.""",
    famous_figures=[
        "Elon Musk", "Mark Zuckerberg", "Bill Gates", "Ada Lovelace",
        "Grace Hopper", "Satya Nadella", "Tim Cook", "Jensen Huang"
    ],
    terminology={
        "variable": "a value stored in memory",
        "equation": "an algorithm step or formula",
        "inequality": "conditional statements (if x > 5)",
    },
    example_scenarios=[
        "Calculating loop iterations to process data",
        "Finding array index from position",
        "Computing algorithm time complexity (simplified)",
        "Determining storage needed for files",
        "Calculating pixels in a screen resolution",
    ],
    visual_themes={
        "primary_colors": "GREEN (terminal), BLUE (tech), BLACK (code)",
        "imagery": "Code blocks, terminals, circuit patterns, binary",
    },
    analogies={
        "variables": "storing values in memory",
        "solving equations": "debugging to find the error",
        "inequalities": "if-else conditions",
        "order of operations": "how code executes line by line",
    },
    fun_facts=[
        "The first computer bug was an actual moth in a computer",
        "Python is named after Monty Python, not the snake",
    ]
)


# =============================================================================
# HOBBY PROFILES
# =============================================================================

COOKING_PROFILE = InterestProfile(
    name="cooking",
    display_name="Cooking & Baking",
    description="Culinary-themed content with recipes, measurements, and scaling",
    context_intro="""Engage food lovers with examples about recipe scaling, measurement
conversions, cooking times, and nutritional calculations. Make math delicious!""",
    famous_figures=[
        "Gordon Ramsay", "Julia Child", "Anthony Bourdain",
        "Ina Garten", "Matty Matheson", "Joshua Weissman"
    ],
    terminology={
        "variable": "unknown ingredient amount",
        "equation": "recipe formula",
        "ratio": "ingredient proportions",
        "fraction": "measurements (1/2 cup, 3/4 tsp)",
    },
    example_scenarios=[
        "Scaling a recipe from 4 servings to 12 servings",
        "Converting cups to tablespoons to teaspoons",
        "Calculating cooking time for different weights",
        "Finding ingredient ratios for consistent taste",
        "Computing total calories from ingredients",
    ],
    visual_themes={
        "primary_colors": "WARM colors (ORANGE, RED, YELLOW)",
        "imagery": "Measuring cups, scales, ingredients, kitchen items",
    },
    analogies={
        "fractions": "recipe measurements",
        "ratios": "ingredient proportions",
        "multiplication": "scaling recipes up",
        "division": "scaling recipes down",
    },
    fun_facts=[
        "Baking is more precise - it's essentially edible chemistry",
        "The ratio for basic bread: 5 parts flour to 3 parts water",
    ]
)

ART_PROFILE = InterestProfile(
    name="art",
    display_name="Art & Design",
    description="Art and design-themed content with proportions, geometry, and color theory",
    context_intro="""Engage creative students with examples about proportions,
perspective, geometric patterns, color mixing, and design principles.
Show how math underlies beautiful artwork.""",
    famous_figures=[
        "Leonardo da Vinci", "Frida Kahlo", "Banksy", "Yayoi Kusama",
        "KAWS", "Takashi Murakami", "Bob Ross"
    ],
    terminology={
        "ratio": "proportions in artwork",
        "variable": "unknown dimension or value",
    },
    example_scenarios=[
        "Calculating canvas dimensions using the golden ratio",
        "Finding scale factors for enlarging artwork",
        "Computing color mixing ratios",
        "Determining perspective vanishing points",
        "Calculating symmetry and reflection",
    ],
    visual_themes={
        "primary_colors": "Full color palette, golden ratio spirals",
        "imagery": "Canvases, brushes, geometric patterns, color wheels",
    },
    analogies={
        "ratios": "proportions in portraits (golden ratio)",
        "geometry": "shapes and perspectives in artwork",
        "symmetry": "reflection and balance in design",
    },
    fun_facts=[
        "The golden ratio (1.618...) appears throughout nature and art",
        "Leonardo da Vinci used math extensively in his artwork",
    ]
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
    ]
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
    ]
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
    ]
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
