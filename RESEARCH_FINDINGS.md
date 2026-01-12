# Math Content Animation Technology Research

## Executive Summary

After researching VideoTutor, Khan Academy, Desmos, GeoGebra, Manim, and other technologies, the **best approach for building an automated math animation system** is:

**Primary Recommendation: Manim + LLM Pipeline**

This combines:
1. **Manim Community Edition** - The most mature, highest-quality math animation renderer
2. **LLM (GPT-4/Claude)** - For converting text descriptions to Manim code
3. **Multi-agent architecture** - For iterative refinement and error correction

---

## Technology Comparison

| Technology | Type | Best For | Automated Generation | Quality |
|------------|------|----------|---------------------|---------|
| **Manim** | Python library | Video animations | ⭐⭐⭐⭐⭐ (with LLM) | Highest |
| **Desmos** | Web API | Interactive graphs | ⭐⭐ (limited) | High |
| **GeoGebra** | Web/Desktop | Interactive geometry | ⭐⭐ (scripting) | High |
| **Khan Academy (Mafs/KaTeX)** | Web libraries | Web rendering | ⭐⭐ | Medium |
| **MathBox** | WebGL library | 3D web visualization | ⭐⭐ | High |
| **JSXGraph** | JavaScript | 2D interactive geometry | ⭐⭐ | Medium |

---

## 1. VideoTutor (Current State-of-the-Art)

**What they do:** AI-powered platform generating animated teaching videos from text/screenshots in 60-90 seconds.

**Tech Stack:**
- Custom Manim-based animation engine (rewritten for precise positioning)
- LLM layer (Claude + Gemini dual-verification)
- Proprietary geometric analyzer for parsing visual figures
- MiniMax-Speech-02 for voice synthesis

**Key Innovation:** LLM + Manim hybrid (NOT diffusion-based video generation)

**Learnings for our system:**
- Manim is the right choice for structured math content
- Dual-model verification improves accuracy
- Custom layout manager needed for complex equations

---

## 2. Khan Academy

**Open Source Tools:**
- **KaTeX** - Fast LaTeX math rendering (MIT license)
- **Perseus** - Exercise framework with interactive widgets
- **Mafs** - React-based interactive graphing (adopted from Steven Petryk)

**Relevant Tech:**
```javascript
// KaTeX example
katex.render("c = \\pm\\sqrt{a^2 + b^2}", element);

// Mafs example
<Mafs>
  <Coordinates.Cartesian />
  <Plot.OfX y={(x) => Math.sin(x)} />
</Mafs>
```

**Limitations:** Not designed for video animation generation; focused on interactive web content.

---

## 3. Desmos

**API Capabilities:**
```javascript
var calculator = Desmos.GraphingCalculator(element);
calculator.setExpression({ latex: 'y = mx + b' });
calculator.setExpression({
  id: 'm',
  latex: 'm = 2',
  sliderBounds: { min: '-5', max: '5' }
});
```

**Animation Features:**
- Slider animations with loop modes
- Ticker system for frame-by-frame control
- GIF export via GIFsmos tool

**Limitations:**
- Proprietary, requires API key for production
- Limited programmatic animation control
- Not designed for video generation

---

## 4. GeoGebra

**Tech Stack:**
- Java (95% of codebase) compiled to JavaScript via GWT
- Giac CAS (computer algebra system) via WebAssembly
- GeoGebraScript for animations

**API Example:**
```javascript
ggbApplet.evalCommand("f(x) = x^2");
ggbApplet.setAnimating("slider1", true);
ggbApplet.startAnimation();
```

**Limitations:**
- Complex licensing (EUPL v1.2, commercial restrictions)
- Heavy runtime (800MB deployed)
- Better for interactive content than video generation

---

## 5. Manim (Recommended Core Technology)

**Why Manim:**
- Highest quality output (3Blue1Brown standard)
- Programmatic control over every element
- Strong community (453+ contributors)
- Well-documented API
- Python-based (easy LLM code generation)

**Basic Example:**
```python
from manim import *

class QuadraticFormula(Scene):
    def construct(self):
        formula = MathTex(r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}")
        self.play(Write(formula))
        self.wait()
```

**Rendering:**
- Cairo backend (2D vector)
- OpenGL backend (3D accelerated)
- FFmpeg for video encoding

---

## 6. AI-Powered Generation (Key Innovation)

### Existing Solutions

| Project | Approach | Models Used |
|---------|----------|-------------|
| **Generative Manim** | Single LLM code generation | GPT-4o, Claude Sonnet |
| **Math-To-Manim** | 6-agent swarm pipeline | Gemini, Claude, Kimi K2 |
| **VideoTutor** | Proprietary hybrid | Claude + Gemini |
| **MathGPT** | Solver + video generation | Custom |

### Math-To-Manim Pipeline (Best Open Source)

```
Text Input → ConceptAnalyzer → PrerequisiteExplorer → MathematicalEnricher
         → VisualDesigner → NarrativeComposer → CodeGenerator → Manim Render
```

**Six Agents:**
1. **ConceptAnalyzer** - Parse topic, audience, domain
2. **PrerequisiteExplorer** - Build knowledge graph
3. **MathematicalEnricher** - Add LaTeX, equations, theorems
4. **VisualDesigner** - Specify colors, transitions, timing
5. **NarrativeComposer** - Generate verbose prompt
6. **CodeGenerator** - Output executable Manim code

---

## Recommended Architecture for Our System

```
┌─────────────────────────────────────────────────────────────┐
│                    Math Content Engine                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Text Input  │───▶│  LLM Agent   │───▶│ Manim Code   │  │
│  │  (Problem)   │    │  Pipeline    │    │ Generator    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                             │                    │          │
│                             ▼                    ▼          │
│                    ┌──────────────┐    ┌──────────────┐    │
│                    │  Validator   │◀───│   Manim CE   │    │
│                    │  (Error Fix) │    │   Renderer   │    │
│                    └──────────────┘    └──────────────┘    │
│                                               │             │
│                                               ▼             │
│                                      ┌──────────────┐      │
│                                      │  MP4/GIF     │      │
│                                      │  Output      │      │
│                                      └──────────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Components to Build

1. **Input Parser**
   - Accept text descriptions of math problems
   - Extract equations, concepts, visual requirements

2. **LLM Code Generator**
   - Use Claude/GPT-4 with Manim-specific prompts
   - Include few-shot examples for common patterns
   - RAG with Manim documentation for accuracy

3. **Manim Renderer**
   - ManimCE for stable rendering
   - Support both video and GIF output
   - Configurable quality settings

4. **Error Handler**
   - Catch rendering errors
   - Feed back to LLM for code fixes
   - Max 5 retry attempts

5. **Optional: Voice Synthesis**
   - ElevenLabs or MiniMax for narration
   - Sync audio with animation timing

---

## Tech Stack Recommendation

| Component | Technology | Reason |
|-----------|------------|--------|
| Animation Engine | **Manim Community Edition** | Best quality, Python-based |
| LLM | **Claude Sonnet 4** or **GPT-4o** | Best code generation |
| Math Rendering | **LaTeX** (via Manim's MathTex) | Professional quality |
| Web Graphs | **Desmos API** or **Mafs** | If interactive needed |
| Voice | **ElevenLabs** or **MiniMax-Speech** | Natural narration |

---

## Quick Start Code Examples

### Basic Manim Animation

```python
from manim import *

class PythagoreanTheorem(Scene):
    def construct(self):
        # Title
        title = Text("Pythagorean Theorem").scale(0.8)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))

        # Triangle
        triangle = Polygon(
            [-2, -1, 0], [2, -1, 0], [-2, 2, 0],
            color=BLUE
        )

        # Labels
        a_label = MathTex("a").next_to(triangle, LEFT)
        b_label = MathTex("b").next_to(triangle, DOWN)
        c_label = MathTex("c").move_to([0.5, 0.8, 0])

        self.play(Create(triangle))
        self.play(Write(a_label), Write(b_label), Write(c_label))

        # Formula
        formula = MathTex("a^2 + b^2 = c^2").scale(1.2)
        formula.to_edge(DOWN)
        self.play(Write(formula))
        self.wait(2)
```

### LLM Prompt Template

```python
MANIM_SYSTEM_PROMPT = """
You are a Manim animation expert. Generate Python code using ManimCE
to create educational math animations.

Rules:
1. Always use `from manim import *`
2. Create a Scene class with construct() method
3. Use MathTex for equations, Text for regular text
4. Include self.play() for animations
5. Add self.wait() between major steps
6. Keep animations under 60 seconds

Example patterns:
- Write() for text/equation appearance
- Create() for shapes
- Transform() for morphing
- FadeIn/FadeOut for transitions
"""
```

---

## Next Steps

1. **Set up Manim CE environment**
   ```bash
   pip install manim
   ```

2. **Create LLM integration**
   - Anthropic Claude API or OpenAI GPT-4
   - Design prompt templates for math topics

3. **Build error feedback loop**
   - Catch Manim errors
   - Retry with error context

4. **Add topic-specific templates**
   - Algebra, geometry, calculus patterns
   - Pre-built animation components

5. **Optional: Web interface**
   - Accept text input
   - Display rendered videos

---

## Resources

### Documentation
- [Manim Community Docs](https://docs.manim.community/)
- [Desmos API](https://www.desmos.com/api)
- [GeoGebra API](https://geogebra.github.io/docs/)
- [KaTeX](https://katex.org/)

### Open Source Projects
- [Math-To-Manim](https://github.com/HarleyCoops/Math-To-Manim)
- [Generative Manim](https://github.com/marcelo-earth/generative-manim)
- [MathBox](https://github.com/unconed/mathbox)
- [JSXGraph](https://github.com/jsxgraph/jsxgraph)

### Commercial Platforms
- [VideoTutor](https://videotutor.ai/)
- [MathGPT](https://math-gpt.org/)
