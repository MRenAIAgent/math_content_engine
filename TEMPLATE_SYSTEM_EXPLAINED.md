# Parameterized Video Template System - Complete Guide

## Overview

The parameterized template system allows you to create **reusable, customizable math animation templates** that can generate videos from simple questions like "Solve 3x + 5 = 14" without needing to write any Manim code.

### Key Concept
Instead of generating Manim code with an LLM every time (slow, expensive, unpredictable), you define templates once with placeholders, then fill them in with parsed parameters (fast, cheap, reliable).

---

## Architecture

```
User Question: "Solve 3x + 5 = 14"
        ↓
┌───────────────────────────────────────┐
│  1. Question Parser                   │
│  - Regex Parser (fast)                │
│  - LLM Parser (flexible)              │
│  Result: {template_id, params}        │
└───────────────┬───────────────────────┘
                ↓
        {template_id: "linear_equation_graph",
         params: {a: 3, b: 5, c: 14}}
                ↓
┌───────────────────────────────────────┐
│  2. Template Renderer                 │
│  - Get template from registry         │
│  - Compute derived params             │
│  - Validate parameters                │
│  - Render code (placeholder → value)  │
└───────────────┬───────────────────────┘
                ↓
        Generated Manim Code
                ↓
┌───────────────────────────────────────┐
│  3. Manim Renderer                    │
│  - Validate code                      │
│  - Execute Manim subprocess           │
│  - Output video file                  │
└───────────────┬───────────────────────┘
                ↓
        Video: linear_equation.mp4
```

---

## Core Components

### 1. **ParamSpec** - Parameter Definition

Defines what inputs a template accepts:

```python
from math_content_engine.templates.base import ParamSpec, ParamType

# Example: Define parameter 'a' (coefficient of x)
param_a = ParamSpec(
    name="a",                           # Used in {a} placeholders
    param_type=ParamType.FLOAT,         # Type validation
    description="Coefficient of x",     # Human-readable
    required=True,                      # Must be provided
    constraints={"min": -20, "max": 20} # Valid range
)

# Example: Define derived parameter (computed automatically)
param_solution = ParamSpec(
    name="solution",
    param_type=ParamType.FLOAT,
    description="Solution x-value",
    required=False,
    derived_from="(c - b) / a"          # Formula for computation
)
```

**Supported Types:**
- `INT` - Integers
- `FLOAT` - Decimals
- `STRING` - Text
- `BOOL` - True/False
- `LIST_INT` - List of integers
- `LIST_FLOAT` - List of floats
- `CHOICE` - One of specific values

### 2. **ManimTemplate** - Template Definition

A complete animation template with placeholders:

```python
from math_content_engine.templates.base import ManimTemplate, TemplateCategory

# Define the template
template = ManimTemplate(
    id="linear_equation_graph",
    name="Linear Equation - Graphical Method",
    category=TemplateCategory.LINEAR_EQUATIONS,
    description="Solve ax + b = c graphically",

    # Parameters it accepts
    parameters=[
        ParamSpec(name="a", param_type=ParamType.FLOAT, ...),
        ParamSpec(name="b", param_type=ParamType.FLOAT, ...),
        ParamSpec(name="c", param_type=ParamType.FLOAT, ...),
        ParamSpec(name="solution", ..., derived_from="(c - b) / a"),
    ],

    # Template code with {placeholders}
    template_code='''from manim import *

class LinearEquationScene(Scene):
    def construct(self):
        # Parameters filled in automatically
        a, b, c = {a}, {b}, {c}
        solution = {solution}

        # Use parameters to create animation
        equation = MathTex(f"{a}x + {b} = {c}")
        self.play(Write(equation))
        # ... rest of animation code
''',

    # Example questions this template handles
    example_questions=[
        "Solve 3x + 5 = 14",
        "What is 2x - 7 = 11?",
        "Find x: -x + 3 = 8"
    ],

    # Function to compute derived parameters
    compute_derived=compute_linear_derived,

    # Tags for search
    tags=["algebra", "linear", "equation", "graph"]
)
```

### 3. **Template Registry** - Central Storage

Stores and retrieves templates:

```python
from math_content_engine.templates.registry import get_registry

# Get the global registry
registry = get_registry()

# Register a template
registry.register(my_template)

# Find templates
template = registry.get("linear_equation_graph")
linear_templates = registry.get_by_category(TemplateCategory.LINEAR_EQUATIONS)
matching = registry.search("solve equation")
```

### 4. **Template Renderer** - Code Generation

Takes parameters and generates Manim code:

```python
from math_content_engine.templates.renderer import TemplateRenderer

renderer = TemplateRenderer()

# Render with parameters
code = renderer.render(
    template_id="linear_equation_graph",
    params={"a": 3, "b": 5, "c": 14}
)

# Result:
# - Validates parameters
# - Computes derived params (solution = (14-5)/3 = 3)
# - Replaces {a} → 3, {b} → 5, {c} → 14, {solution} → 3
# - Returns complete Manim code
```

### 5. **Question Parser** - Extract Parameters

Two options:

#### A. **SimpleQuestionParser** (Regex-based, fast)
```python
from math_content_engine.templates.question_parser import SimpleQuestionParser

parser = SimpleQuestionParser()
result = parser.parse("Solve 3x + 5 = 14")

# result.success = True
# result.template_id = "linear_equation_graph"
# result.parameters = {"a": 3, "b": 5, "c": 14}
# result.confidence = 0.95
```

Patterns it recognizes:
- Linear equations: `3x + 5 = 14`, `2x - 7 = 11`
- Slope calculations: `slope between (1,2) and (3,8)`
- Inequalities: `x > 5`, `2x + 3 ≤ 10`

#### B. **QuestionParserAgent** (LLM-based, flexible)
```python
from math_content_engine.templates.question_parser import QuestionParserAgent

parser = QuestionParserAgent(llm_client=my_llm)
result = parser.parse("What's the x when 3x plus 5 equals 14?")

# More flexible, handles natural language variations
# Uses LLM to understand intent and extract parameters
```

### 6. **Template Engine** - Complete Orchestration

Combines everything:

```python
from math_content_engine.templates.engine import TemplateEngine

# Initialize
engine = TemplateEngine(
    use_simple_parser=True,  # or False for LLM parser
    video_quality=VideoQuality.HIGH,
    output_dir=Path("./videos")
)

# Generate video from question
result = engine.generate_from_question(
    question="Solve 3x + 5 = 14",
    output_filename="my_equation"
)

if result.success:
    print(f"Video: {result.video_path}")
    print(f"Template: {result.template_id}")
    print(f"Parameters: {result.parameters}")
else:
    print(f"Error: {result.error_message}")
```

---

## Complete Example: Creating a Template

Let's create a template for solving quadratic equations:

### Step 1: Define Parameter Computation

```python
def compute_quadratic_derived(params: dict) -> dict:
    """Compute roots and other derived values."""
    a = params["a"]
    b = params["b"]
    c = params["c"]

    # Discriminant
    discriminant = b**2 - 4*a*c

    # Roots
    if discriminant >= 0:
        sqrt_d = discriminant ** 0.5
        root1 = (-b + sqrt_d) / (2*a)
        root2 = (-b - sqrt_d) / (2*a)
    else:
        root1 = root2 = None

    return {
        "discriminant": discriminant,
        "root1": root1,
        "root2": root2,
        "num_roots": 2 if discriminant > 0 else (1 if discriminant == 0 else 0)
    }
```

### Step 2: Define the Template

```python
QUADRATIC_TEMPLATE = '''from manim import *

class QuadraticScene(Scene):
    def construct(self):
        # Parameters
        a, b, c = {a}, {b}, {c}
        discriminant = {discriminant}

        # Show equation
        equation = MathTex(f"{a}x^2 + {b}x + {c} = 0")
        self.play(Write(equation))
        self.wait(1)

        # Show quadratic formula
        formula = MathTex(r"x = \\frac{{-b \\pm \\sqrt{{b^2 - 4ac}}}}{{2a}}")
        formula.next_to(equation, DOWN, buff=1)
        self.play(Write(formula))
        self.wait(1)

        # Calculate discriminant
        disc_calc = MathTex(f"\\Delta = {b}^2 - 4({a})({c}) = {discriminant}")
        disc_calc.next_to(formula, DOWN, buff=1)
        self.play(Write(disc_calc))
        self.wait(1)

        # Show roots
        if {num_roots} == 2:
            root1_text = MathTex(f"x_1 = {root1}")
            root2_text = MathTex(f"x_2 = {root2}")
            roots = VGroup(root1_text, root2_text).arrange(RIGHT, buff=1)
            roots.next_to(disc_calc, DOWN, buff=1)
            self.play(Write(roots))
        elif {num_roots} == 1:
            root_text = MathTex(f"x = {root1}")
            root_text.next_to(disc_calc, DOWN, buff=1)
            self.play(Write(root_text))
        else:
            no_roots = Text("No real roots", color=RED)
            no_roots.next_to(disc_calc, DOWN, buff=1)
            self.play(Write(no_roots))

        self.wait(2)
'''

quadratic_template = ManimTemplate(
    id="quadratic_formula",
    name="Quadratic Equation Solver",
    category=TemplateCategory.QUADRATICS,
    description="Solve ax² + bx + c = 0 using quadratic formula",
    parameters=[
        ParamSpec("a", ParamType.FLOAT, "Coefficient of x²", required=True),
        ParamSpec("b", ParamType.FLOAT, "Coefficient of x", required=True),
        ParamSpec("c", ParamType.FLOAT, "Constant term", required=True),
        ParamSpec("discriminant", ParamType.FLOAT, "b² - 4ac",
                  required=False, derived_from="b**2 - 4*a*c"),
        ParamSpec("root1", ParamType.FLOAT, "First root", required=False),
        ParamSpec("root2", ParamType.FLOAT, "Second root", required=False),
        ParamSpec("num_roots", ParamType.INT, "Number of real roots", required=False),
    ],
    template_code=QUADRATIC_TEMPLATE,
    compute_derived=compute_quadratic_derived,
    example_questions=[
        "Solve x² - 5x + 6 = 0",
        "Find roots of 2x² + 3x - 2 = 0"
    ],
    tags=["algebra", "quadratic", "roots", "formula"]
)
```

### Step 3: Register and Use

```python
# Register
from math_content_engine.templates.registry import get_registry
get_registry().register(quadratic_template)

# Use with engine
from math_content_engine.templates.engine import TemplateEngine

engine = TemplateEngine()
result = engine.generate_from_question(
    question="Solve x² - 5x + 6 = 0",
    output_filename="quadratic_example"
)

print(result.video_path)  # ./output/quadratic_example.mp4
```

---

## Benefits

### 1. **Speed**
- No LLM call for code generation
- Instant parameter substitution
- 10-100x faster than full LLM generation

### 2. **Reliability**
- Pre-validated template code
- Consistent output every time
- No syntax errors from LLM

### 3. **Cost**
- Only uses LLM for question parsing (optional)
- Can use regex parser (free)
- Huge cost savings vs full generation

### 4. **Customization**
- Easy to modify templates
- Add derived parameters
- Extend with new question patterns

### 5. **Quality Control**
- Human-reviewed templates
- Consistent visual style
- Educational best practices

---

## Current Templates

The system includes templates for:

### Linear Equations
- `linear_equation_graph` - Graphical intersection method
- `linear_equation_balance` - Balance scale method
- `linear_equation_steps` - Step-by-step algebra

### Graphing
- `slope_from_points` - Calculate and visualize slope
- `slope_intercept_graph` - Graph from y = mx + b

### Inequalities
- `inequality_number_line` - Show solution on number line
- `inequality_graph` - Graph inequality region

### Quadratics
- `quadratic_formula` - Solve using formula
- `quadratic_graph` - Parabola with roots

---

## How Parameters Flow

```
1. User Question
   "Solve 3x + 5 = 14"

2. Parser Extracts
   {
     "a": 3,
     "b": 5,
     "c": 14
   }

3. Compute Derived
   compute_linear_derived({a: 3, b: 5, c: 14})
   → {
       "solution": 3,        # (14-5)/3
       "x_min": -2,
       "x_max": 7,
       "y_min": -2,
       "y_max": 25
     }

4. All Parameters
   {
     "a": 3,
     "b": 5,
     "c": 14,
     "solution": 3,
     "x_min": -2,
     "x_max": 7,
     "y_min": -2,
     "y_max": 25
   }

5. Validation
   - Check 'a' is float, -20 ≤ a ≤ 20 ✓
   - Check 'b' is float, -20 ≤ b ≤ 20 ✓
   - Check 'c' is float, -20 ≤ c ≤ 20 ✓

6. Template Rendering
   {a} → 3
   {b} → 5
   {c} → 14
   {solution} → 3
   {x_min} → -2
   ...

7. Generated Code
   class LinearEquationGraphScene(Scene):
       def construct(self):
           a, b, c = 3, 5, 14
           solution = 3
           axes = Axes(x_range=[-2, 7, 1], ...)
           ...
```

---

## Advanced Features

### 1. **Constraints**
```python
ParamSpec(
    name="slope",
    param_type=ParamType.FLOAT,
    constraints={
        "min": -10,
        "max": 10,
        "not_zero": True  # Custom constraint
    }
)
```

### 2. **Choices**
```python
ParamSpec(
    name="method",
    param_type=ParamType.CHOICE,
    constraints={
        "choices": ["graphical", "algebraic", "balance"]
    }
)
```

### 3. **Lists**
```python
ParamSpec(
    name="points",
    param_type=ParamType.LIST_FLOAT,
    description="List of x-coordinates",
    constraints={"min_length": 2, "max_length": 10}
)
```

### 4. **Complex Derived Parameters**
```python
def compute_complex_derived(params):
    # Multiple derived values
    result = {}

    # Compute multiple related values
    result["vertex_x"] = -params["b"] / (2 * params["a"])
    result["vertex_y"] = params["a"] * result["vertex_x"]**2 + ...
    result["axis_of_symmetry"] = result["vertex_x"]

    # Conditional logic
    if params["a"] > 0:
        result["opens"] = "upward"
    else:
        result["opens"] = "downward"

    return result
```

---

## Testing

```python
# tests/test_templates.py shows examples

def test_template_rendering():
    """Test that template renders correctly."""
    template = linear_equation_graph
    code = template.render({"a": 3, "b": 5, "c": 14, "solution": 3})

    assert "a, b, c = 3, 5, 14" in code
    assert "solution = 3" in code
    assert "LinearEquationGraphScene" in code

def test_parameter_validation():
    """Test parameter validation."""
    template = linear_equation_graph
    valid, errors = template.validate_params({"a": 3, "b": 5, "c": 14})
    assert valid

    valid, errors = template.validate_params({"a": "not a number"})
    assert not valid
    assert "must be" in errors[0]
```

---

## Summary

The parameterized template system provides:

✅ **Fast** - Instant code generation
✅ **Reliable** - Pre-validated templates
✅ **Flexible** - Support many question types
✅ **Extensible** - Easy to add new templates
✅ **Cost-effective** - Minimal LLM usage
✅ **Educational** - Consistent quality

Perfect for generating hundreds of similar videos with different parameters!
