# Chapter 2: Solving Linear Equations and Inequalities - Animations

This folder contains educational Manim animations for Chapter 2 of the Algebra 1 curriculum, based on OpenStax Elementary Algebra 2e.

## Animation Summary

**Total: 19 animations across 5 sections**

### Section 2.1: Addition and Subtraction Properties of Equality (4 animations)

| File | Description | Duration |
|------|-------------|----------|
| `2_1_01_verify_solution.mp4` | Verifying a solution to a linear equation | ~12s |
| `2_1_02_subtraction_property.mp4` | Subtraction Property of Equality | ~13s |
| `2_1_03_addition_property.mp4` | Addition Property of Equality | ~11s |
| `2_1_04_combine_like_terms.mp4` | Combining like terms before solving | ~12s |

### Section 2.2: Division and Multiplication Properties of Equality (4 animations)

| File | Description | Duration |
|------|-------------|----------|
| `2_2_01_division_property.mp4` | Division Property of Equality | ~11s |
| `2_2_02_negative_coefficient.mp4` | Solving with negative coefficients | ~13s |
| `2_2_03_multiplication_property.mp4` | Multiplication Property of Equality | ~12s |
| `2_2_04_fraction_coefficient.mp4` | Using reciprocals to solve | ~14s |

### Section 2.3: Variables on Both Sides (3 animations)

| File | Description | Duration |
|------|-------------|----------|
| `2_3_01_variables_both_sides.mp4` | Variables on both sides of equation | ~14s |
| `2_3_02_negative_variables.mp4` | Negative variable terms | ~20s |
| `2_3_03_with_parentheses.mp4` | Distributive property and solving | ~17s |

### Section 2.4: General Strategy for Linear Equations (4 animations)

| File | Description | Duration |
|------|-------------|----------|
| `2_4_01_general_strategy.mp4` | 5-step solving strategy overview | ~25s |
| `2_4_02_complex_example.mp4` | Complex equation walkthrough | ~17s |
| `2_4_03_no_solution.mp4` | Equations with no solution (contradictions) | ~13s |
| `2_4_04_infinite_solutions.mp4` | Infinitely many solutions (identities) | ~17s |

### Section 2.7: Linear Inequalities (4 animations)

| File | Description | Duration |
|------|-------------|----------|
| `2_7_01_inequality_symbols.mp4` | Introduction to inequality symbols | ~15s |
| `2_7_02_solve_basic_inequality.mp4` | Basic inequality solving | ~12s |
| `2_7_03_negative_division_rule.mp4` | Reversing inequality with negatives | ~21s |
| `2_7_04_multistep_inequality.mp4` | Multi-step inequalities | ~13s |

## File Structure

```
chapter_02_linear_equations/
├── README.md                           # This file
├── generate_chapter_02_animations.py   # Generation script
├── 2_1_01_verify_solution.mp4         # Video
├── 2_1_01_verify_solution.py          # Source code
├── ...
```

## Usage

### Regenerate All Animations

```bash
cd /Users/minren/code/math_content_engine
source venv/bin/activate
export $(cat .env | grep -v '^#' | xargs)
python curriculum/algebra1/animations/chapter_02_linear_equations/generate_chapter_02_animations.py
```

### Regenerate Specific Section

```bash
python generate_chapter_02_animations.py --section 2.1
```

### List Available Animations

```bash
python generate_chapter_02_animations.py --list
```

## Technical Details

- **Engine**: Math Content Engine with Claude Sonnet 4
- **Renderer**: Manim Community Edition
- **Quality**: 720p (medium)
- **Format**: MP4
- **Style**: Dark background (Manim default)

## License

Content based on OpenStax Elementary Algebra 2e (CC BY 4.0)
