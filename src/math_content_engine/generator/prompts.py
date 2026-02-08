"""
Prompt templates for Manim code generation.

The system prompts share a common base (rules, patterns, pitfalls) with
style-specific overrides for DARK vs LIGHT backgrounds.  The generation
template separates concerns into clearly prioritised sections so that the
LLM never sacrifices math correctness for theming.
"""

from typing import Optional

# Import centralized enums
from ..constants import AnimationStyle


# =============================================================================
# SHARED BASE PROMPT (rules, patterns, pitfalls)
# =============================================================================
_BASE_SYSTEM_PROMPT = """You are an expert Manim animation developer. Your task is to generate high-quality, educational math animations using ManimCE (Manim Community Edition).

## Priority Order (ALWAYS follow this ranking)
1. **Mathematical correctness** - equations, formulas, and concepts MUST be accurate
2. **Working code** - the code MUST run without errors on the first try
3. **Visual clarity** - elements must be readable and well-positioned
4. **Engagement** - theming and personalization are nice-to-have, never at the cost of #1-#3

## Rules
1. Always use `from manim import *` at the top
2. Create a single Scene class with a descriptive name (e.g., `QuadraticFormulaScene`)
3. The class MUST have a `construct(self)` method
4. Use MathTex for LaTeX equations, Text for regular text labels
5. Include `self.play()` for all animations
6. Add `self.wait()` between major steps (1-2 seconds)
7. Keep total animation under 60 seconds
8. Position elements clearly using `.to_edge()`, `.next_to()`, `.move_to()`
9. Include a title at the top of the scene
10. Keep code under 120 lines — simpler scenes render more reliably

## Scene Pacing Guide
- Title display: ~3 seconds
- Concept buildup: 15-20 seconds
- Main content / key visuals: 20-30 seconds
- Summary / key takeaway: 5-10 seconds

## Animation Patterns
- `Write()` - for text/equation appearance
- `Create()` - for shapes and graphs
- `Transform()` - for morphing one object to another
- `ReplacementTransform()` - for replacing objects
- `FadeIn()` / `FadeOut()` - for smooth transitions
- `Indicate()` - to highlight important elements
- `Circumscribe()` - to draw attention to parts

## LaTeX Tips
- Use raw strings for LaTeX: `r"\\frac{{a}}{{b}}"` (double braces inside f-strings, single in plain strings)
- In a plain raw string: `MathTex(r"\\frac{a}{b}")` is correct
- For multi-line equations, use align environment
- Color specific parts with MathTex substrings

## IMPORTANT: Avoid LaTeX Dependency Issues
- Prefer Text() over MathTex() for simple labels and non-math text
- Use MathTex() ONLY for actual mathematical expressions that need proper typesetting
- Do NOT use `axes.get_axis_labels()` — it uses LaTeX internally and can fail
- Instead, create axis labels manually with Text():
  ```python
  x_label = Text("x", font_size=24).next_to(axes.x_axis, RIGHT)
  y_label = Text("y", font_size=24).next_to(axes.y_axis, UP)
  ```

## Common Pitfalls to AVOID
- Do NOT create more than ~10-12 Mobjects on screen simultaneously — it causes clutter
- Do NOT use deprecated APIs (`ShowCreation` → use `Create`, `ShowPassingFlash` → use `ShowPassingFlashWithThinningStrokeWidth`)
- Do NOT forget `self.play()` — adding Mobjects with `self.add()` alone makes them appear instantly without animation
- Do NOT use `NumberPlane` when you mean `NumberLine`, or vice versa
- Do NOT animate the same Mobject in two parallel animations — use `AnimationGroup` sequentially instead
- Do NOT rely on `always_redraw` for complex updater logic — prefer simple `add_updater` functions
- ALWAYS call `self.wait()` at least once at the end so the final frame is visible
- NEVER import external packages beyond `manim` — they may not be available

Return ONLY valid Python code, no explanations. The code must be immediately executable with Manim."""


# =============================================================================
# DARK BACKGROUND STYLE (Default Manim)
# =============================================================================
_DARK_STYLE_SECTION = """
## VISUAL STYLE - DARK BACKGROUND (Default)

### Color Palette
- Background: default Manim dark background (do NOT set background_color)
- Use appropriate colors from Manim's palette: BLUE, RED, GREEN, YELLOW, WHITE, etc.
- Title: WHITE or BLUE, centered at top

### Code Structure Template
```python
from manim import *

class [SceneName](Scene):
    def construct(self):
        # Title
        title = Text("[Topic]").scale(0.8)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))

        # Main content
        # ... your animation code ...

        # Conclusion
        self.wait(2)
```"""

DARK_SYSTEM_PROMPT = _BASE_SYSTEM_PROMPT + _DARK_STYLE_SECTION


# =============================================================================
# LIGHT BACKGROUND STYLE
# =============================================================================
_LIGHT_STYLE_SECTION = """
## VISUAL STYLE - LIGHT/WHITE BACKGROUND

### Color Palette
- Background: WHITE (set `self.camera.background_color = WHITE` at the start of `construct()`)
- Primary text: BLACK or DARK_GRAY
- Equations: BLUE_E or DARK_BLUE
- Highlights/emphasis: ORANGE or GOLD
- Positive values: GREEN_E or DARK_GREEN
- Negative values: RED_E or MAROON
- Shapes/lines: BLUE, PURPLE, TEAL
- **Avoid**: WHITE, YELLOW, LIGHT_GRAY (poor contrast on white background)

### Typography & Layout
- Title: BLACK or DARK_BLUE, centered at top
- Equations: BLUE_E for visibility
- Labels: BLACK or DARK_GRAY
- Use darker color variants (_E, _D, DARK_) for contrast

### Code Structure Template
```python
from manim import *

class [SceneName](Scene):
    def construct(self):
        # IMPORTANT: Set light background
        self.camera.background_color = WHITE

        # Title (use dark colors)
        title = Text("[Topic]", color=BLACK).scale(0.8)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))

        # Equations (use dark blue for contrast)
        equation = MathTex(r"...", color=BLUE_E)
        self.play(Write(equation))

        # Shapes (use visible colors)
        shape = Circle(color=BLUE, fill_opacity=0.3)
        self.play(Create(shape))

        self.wait(2)
```"""

LIGHT_SYSTEM_PROMPT = _BASE_SYSTEM_PROMPT + _LIGHT_STYLE_SECTION


# =============================================================================
# GENERATION PROMPT TEMPLATE
# =============================================================================
GENERATION_PROMPT_TEMPLATE = """Create a Manim animation for the following math topic:

TOPIC: {topic}

AUDIENCE LEVEL: {audience_level}

## TOPIC-SPECIFIC GUIDANCE
{topic_guidance}

## ADDITIONAL REQUIREMENTS
{requirements}

## ENGAGEMENT STYLE
- Address the viewer directly: use "you", "your", "let's figure this out together"
- Open with a relatable hook or scenario, not a dry definition
- Use real, specific numbers (not "some points" — say "24 points")
- Include at least one "challenge moment" where the viewer can pause and think
- End with a satisfying payoff or "aha!" moment
{personalization_section}

## OUTPUT INSTRUCTIONS

Generate complete, working Manim code that creates an educational animation explaining this concept.

The animation MUST:
1. Start with a clear title
2. Build up the concept step by step with appropriate pacing
3. Include visual representations where appropriate (shapes, graphs, arrows)
4. Show key equations/formulas with proper MathTex rendering
5. End with a summary or key takeaway

Constraints:
- Keep total code under 120 lines
- No more than 10-12 visible Mobjects on screen at once
- Total animation duration: 30-60 seconds
- MUST run error-free on the first try

Return ONLY the Python code, no additional text or explanations."""


# =============================================================================
# TOPIC TEMPLATES (ordered from most specific to least specific)
# =============================================================================
TOPIC_TEMPLATES = {
    # Most specific first to avoid substring collision
    "linear_algebra": """Focus on:
- Vector arrow representations
- Matrix transformations
- Basis vector animations
- Eigenvalue visualizations""",

    "linear_equations": """Focus on:
- Step-by-step equation solving
- Balance/equality visualization (both sides)
- Color-coding terms that move or change
- Showing inverse operations clearly""",

    "quadratic": """Focus on:
- Parabola graphing with Axes
- Vertex and roots identification
- Factoring or completing the square steps
- Discriminant visualization""",

    "trigonometry": """Focus on:
- Unit circle references
- Wave function animations
- Triangle relationships (SOH-CAH-TOA)
- Angle visualizations with arcs""",

    "calculus": """Focus on:
- Limit approaching animations (values converging)
- Area under curve visualization (Riemann sums)
- Derivative as slope of tangent line
- Integral as accumulation of area""",

    "statistics": """Focus on:
- Data visualization (BarChart, dot plots)
- Distribution curves (normal, skewed)
- Mean/median/mode markers on number line
- Probability representations (area models, tree diagrams)""",

    "probability": """Focus on:
- Sample space visualization (grids, trees)
- Event outcomes highlighted with color
- Fraction/percentage representations
- Complementary events and intersections""",

    "geometry": """Focus on:
- Clear shape construction with Create()
- Angle and side labels with MathTex
- Step-by-step proofs with highlighting
- Transformation visualizations (rotate, reflect, translate)""",

    "exponent": """Focus on:
- Repeated multiplication visualization
- Growth curves on Axes
- Exponent rules shown step-by-step
- Comparing exponential vs linear growth""",

    "logarithm": """Focus on:
- Inverse of exponentiation visualization
- Log scale number line
- Log rules shown step-by-step
- Connection between log and exponential graphs""",

    "ratio": """Focus on:
- Visual part-to-part and part-to-whole models
- Equivalent ratio tables
- Scaling up/down animations
- Real-world proportion scenarios""",

    "fraction": """Focus on:
- Area models (rectangles, circles divided)
- Number line placement
- Equivalent fractions by subdividing
- Operations shown with visual models""",

    "function": """Focus on:
- Input-output machine visualization
- Mapping diagrams (arrows from domain to range)
- Graph construction point by point
- Domain and range highlighted on axes""",

    "sequence": """Focus on:
- Term-by-term buildup on number line
- Pattern recognition with color coding
- Arithmetic vs geometric comparison
- Partial sums visualization""",

    "algebra": """Focus on:
- Variable manipulation
- Equation solving steps (show both sides)
- Balance/equality visualization
- Color-coding different terms""",
}


def get_system_prompt(style: Optional[AnimationStyle] = None) -> str:
    """
    Get the system prompt for the specified animation style.

    Args:
        style: Animation style preset. Defaults to DARK.

    Returns:
        System prompt string for the LLM.
    """
    if style is None:
        style = AnimationStyle.DARK

    style_prompts = {
        AnimationStyle.DARK: DARK_SYSTEM_PROMPT,
        AnimationStyle.LIGHT: LIGHT_SYSTEM_PROMPT,
    }

    return style_prompts.get(style, DARK_SYSTEM_PROMPT)


def get_topic_specific_guidance(topic: str) -> str:
    """Get topic-specific guidance for the generation prompt.

    Templates are checked from most specific to least specific so that
    e.g. ``linear_equations`` is matched before the generic ``algebra``.

    Both underscored keys (``linear_algebra``) and spaced input
    (``linear algebra``) are handled by normalising to underscores.
    """
    topic_normalised = topic.lower().replace(" ", "_")
    for key, guidance in TOPIC_TEMPLATES.items():
        if key in topic_normalised:
            return guidance
    return "Focus on clear step-by-step visualization with appropriate mathematical notation."


def build_generation_prompt(
    topic: str,
    requirements: str = "",
    audience_level: str = "high school",
    personalization_context: str = "",
    student_name: Optional[str] = None,
    student_address: Optional[str] = None,
) -> str:
    """
    Build a complete generation prompt for the given topic.

    Personalization context is placed in its own clearly delineated section
    so the LLM can distinguish between must-have math requirements and
    nice-to-have theming.

    Args:
        topic: Math topic to animate
        requirements: Additional requirements from user
        audience_level: Target audience (elementary, middle school, high school, college)
        personalization_context: Optional personalization prompt from ContentPersonalizer
        student_name: Optional student name for direct address in animations
        student_address: Optional preferred way to address the student.
            Falls back to student_name, then omitted.

    Returns:
        Formatted prompt string
    """
    topic_guidance = get_topic_specific_guidance(topic)

    # Resolve display address: preferred_address → name
    display_address = student_address or student_name

    # Build personalization as a separate, optional section
    personalization_section = ""
    if personalization_context:
        student_line = ""
        if display_address:
            student_line = (
                f"\nStudent's name: {display_address} "
                "(address them directly in the title and key moments)\n"
            )
        personalization_section = (
            "\n## PERSONALIZATION (nice-to-have — never sacrifice math "
            "correctness or code reliability for theming)\n"
            f"{student_line}"
            f"{personalization_context}"
        )

    return GENERATION_PROMPT_TEMPLATE.format(
        topic=topic,
        topic_guidance=topic_guidance,
        requirements=requirements if requirements else "None",
        audience_level=audience_level,
        personalization_section=personalization_section,
    )
