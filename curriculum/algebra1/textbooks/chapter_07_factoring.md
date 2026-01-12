# Chapter 7: Factoring

Source: OpenStax Elementary Algebra 2e (CC BY 4.0)

---

## 7.1 Greatest Common Factor and Factor by Grouping

### Learning Objectives
- Find the greatest common factor (GCF) of two or more expressions
- Factor out the GCF from a polynomial
- Factor by grouping

### Key Concepts

**Greatest Common Factor (GCF)**
The largest factor that divides evenly into all terms.

### Examples

**Example 1:** Find GCF of 12x³ and 18x²
```
12x³ = 2² · 3 · x³
18x² = 2 · 3² · x²

GCF = 2 · 3 · x² = 6x²
```

**Example 2:** Factor 15x³ − 25x² + 10x
```
GCF = 5x
15x³ − 25x² + 10x = 5x(3x² − 5x + 2)
```

**Example 3:** Factor by grouping: x³ + 3x² + 2x + 6
```
Group: (x³ + 3x²) + (2x + 6)
Factor each group: x²(x + 3) + 2(x + 3)
Factor common binomial: (x + 3)(x² + 2)
```

### Practice Problems

1. Find the GCF:
   a) 24x⁴ and 36x²
   b) 15a³b² and 25a²b³
   c) 12x²y, 18xy², 30xy

2. Factor out the GCF:
   a) 8x³ − 12x²
   b) 5y⁴ + 15y³ − 10y²
   c) 6a²b − 9ab² + 3ab

3. Factor by grouping:
   a) x³ + 2x² + 4x + 8
   b) 3x³ − 6x² + 5x − 10
   c) 2y³ + y² + 6y + 3

---

## 7.2 Factor Trinomials of the Form x² + bx + c

### Learning Objectives
- Factor trinomials of the form x² + bx + c

### Method

To factor x² + bx + c:
1. Find two numbers that multiply to c
2. AND add up to b
3. Write as (x + m)(x + n) where m·n = c and m + n = b

### Examples

**Example 1:** Factor x² + 7x + 12
```
Need: m · n = 12 and m + n = 7
Try: 3 · 4 = 12 and 3 + 4 = 7 ✓

x² + 7x + 12 = (x + 3)(x + 4)
```

**Example 2:** Factor x² − 5x + 6
```
Need: m · n = 6 and m + n = −5
Both must be negative (positive product, negative sum)
Try: (−2)(−3) = 6 and −2 + (−3) = −5 ✓

x² − 5x + 6 = (x − 2)(x − 3)
```

**Example 3:** Factor x² + 2x − 15
```
Need: m · n = −15 and m + n = 2
One positive, one negative (negative product)
Try: 5 · (−3) = −15 and 5 + (−3) = 2 ✓

x² + 2x − 15 = (x + 5)(x − 3)
```

**Example 4:** Factor x² − 3x − 18
```
Need: m · n = −18 and m + n = −3
Try: 3 · (−6) = −18 and 3 + (−6) = −3 ✓

x² − 3x − 18 = (x + 3)(x − 6)
```

### Sign Pattern Guide

| c sign | b sign | Factor signs |
|--------|--------|--------------|
| + | + | (x + )(x + ) |
| + | − | (x − )(x − ) |
| − | + | (x + )(x − ), larger is + |
| − | − | (x + )(x − ), larger is − |

### Practice Problems

1. Factor:
   a) x² + 8x + 15
   b) x² + 10x + 24
   c) x² − 9x + 20
   d) x² − 11x + 28
   e) x² + 3x − 10
   f) x² − 2x − 35
   g) x² − x − 42
   h) x² + 4x − 21

---

## 7.3 Factor Trinomials of the Form ax² + bx + c

### Learning Objectives
- Factor trinomials using trial and error
- Factor trinomials using the "ac" method

### Method 1: Trial and Error

For ax² + bx + c = (px + m)(qx + n):
- p · q = a
- m · n = c
- Check: outer + inner = b

### Method 2: AC Method

1. Multiply a · c
2. Find factors of ac that add to b
3. Rewrite middle term using these factors
4. Factor by grouping

### Examples

**Example 1:** Factor 2x² + 7x + 3 (Trial and Error)
```
Factors of 2: 1, 2
Factors of 3: 1, 3

Try (2x + 1)(x + 3):
Check: 2x · 3 + 1 · x = 6x + x = 7x ✓

2x² + 7x + 3 = (2x + 1)(x + 3)
```

**Example 2:** Factor 3x² + 10x + 8 (AC Method)
```
a · c = 3 · 8 = 24
Find factors of 24 that add to 10: 4 + 6 = 10 ✓

Rewrite: 3x² + 4x + 6x + 8
Group: (3x² + 4x) + (6x + 8)
Factor: x(3x + 4) + 2(3x + 4)
Result: (3x + 4)(x + 2)
```

**Example 3:** Factor 6x² − 11x + 4
```
a · c = 6 · 4 = 24
Find factors of 24 that add to −11: −3 + (−8) = −11 ✓

Rewrite: 6x² − 3x − 8x + 4
Group: 3x(2x − 1) − 4(2x − 1)
Result: (2x − 1)(3x − 4)
```

### Practice Problems

1. Factor:
   a) 2x² + 5x + 3
   b) 3x² + 7x + 2
   c) 5x² + 13x + 6
   d) 4x² − 11x + 6
   e) 6x² + x − 12
   f) 8x² − 14x + 3

---

## 7.4 Factor Special Products

### Learning Objectives
- Factor perfect square trinomials
- Factor differences of squares
- Factor sums and differences of cubes

### Special Factoring Patterns

**Perfect Square Trinomials**
```
a² + 2ab + b² = (a + b)²
a² − 2ab + b² = (a − b)²
```

**Difference of Squares**
```
a² − b² = (a + b)(a − b)
```

**Sum and Difference of Cubes**
```
a³ + b³ = (a + b)(a² − ab + b²)
a³ − b³ = (a − b)(a² + ab + b²)
```

### Examples

**Example 1:** Factor x² + 10x + 25
```
Check: Is this a perfect square?
√25 = 5, and 2 · x · 5 = 10x ✓

x² + 10x + 25 = (x + 5)²
```

**Example 2:** Factor 4x² − 12x + 9
```
√4x² = 2x, √9 = 3
2 · 2x · 3 = 12x ✓

4x² − 12x + 9 = (2x − 3)²
```

**Example 3:** Factor x² − 49
```
x² − 49 = x² − 7²
= (x + 7)(x − 7)
```

**Example 4:** Factor 25x² − 16
```
25x² − 16 = (5x)² − 4²
= (5x + 4)(5x − 4)
```

**Example 5:** Factor x³ + 8
```
x³ + 8 = x³ + 2³
= (x + 2)(x² − 2x + 4)
```

**Example 6:** Factor 27x³ − 64
```
27x³ − 64 = (3x)³ − 4³
= (3x − 4)(9x² + 12x + 16)
```

### Practice Problems

1. Factor perfect square trinomials:
   a) x² + 6x + 9
   b) x² − 14x + 49
   c) 9x² + 24x + 16

2. Factor difference of squares:
   a) x² − 36
   b) 4x² − 25
   c) 16x² − 81

3. Factor sum/difference of cubes:
   a) x³ + 27
   b) x³ − 125
   c) 8x³ + 1

---

## 7.5 General Strategy for Factoring Polynomials

### Factoring Strategy

1. **Factor out GCF first** (always!)
2. **Count the terms:**
   - 4 terms → try grouping
   - 3 terms → trinomial methods
   - 2 terms → check special patterns

3. **For trinomials:**
   - x² + bx + c → find factors of c that add to b
   - ax² + bx + c → trial/error or AC method
   - Check for perfect square

4. **For binomials:**
   - a² − b² → difference of squares
   - a³ + b³ → sum of cubes
   - a³ − b³ → difference of cubes

5. **Check:** Is each factor completely factored?

### Examples

**Example 1:** Factor 3x³ − 12x
```
GCF: 3x
= 3x(x² − 4)
= 3x(x + 2)(x − 2)    (difference of squares)
```

**Example 2:** Factor 2x² + 10x − 28
```
GCF: 2
= 2(x² + 5x − 14)
= 2(x + 7)(x − 2)
```

**Example 3:** Factor x⁴ − 16
```
= (x²)² − 4²
= (x² + 4)(x² − 4)
= (x² + 4)(x + 2)(x − 2)
```

### Practice Problems

Factor completely:
1. 5x² − 45
2. 2x³ + 4x² − 6x
3. x⁴ − 81
4. 3x³ + 6x² + 3x
5. 18x² − 50

---

## 7.6 Quadratic Equations

### Learning Objectives
- Solve quadratic equations using the Zero Product Property
- Solve quadratic equations by factoring
- Solve applications modeled by quadratic equations

### Key Concepts

**Quadratic Equation Standard Form**
ax² + bx + c = 0, where a ≠ 0

**Zero Product Property**
If ab = 0, then a = 0 or b = 0 (or both).

### Solving by Factoring

1. Write equation in standard form (= 0)
2. Factor the left side
3. Apply Zero Product Property
4. Solve each equation
5. Check solutions

### Examples

**Example 1:** Solve (x + 3)(x − 5) = 0
```
x + 3 = 0  or  x − 5 = 0
x = −3  or  x = 5
```

**Example 2:** Solve x² − 7x + 12 = 0
```
Factor: (x − 3)(x − 4) = 0
x − 3 = 0  or  x − 4 = 0
x = 3  or  x = 4
```

**Example 3:** Solve 2x² + 5x = 3
```
Standard form: 2x² + 5x − 3 = 0
Factor: (2x − 1)(x + 3) = 0
2x − 1 = 0  or  x + 3 = 0
x = 1/2  or  x = −3
```

**Example 4:** Solve x² = 9x
```
Standard form: x² − 9x = 0
Factor: x(x − 9) = 0
x = 0  or  x = 9
```

**Example 5:** Solve 25x² = 49
```
25x² − 49 = 0
(5x + 7)(5x − 7) = 0
x = −7/5  or  x = 7/5
```

### Word Problem Applications

**Example: Consecutive Integers**
```
The product of two consecutive positive integers is 132.
Find the integers.

Let n = first integer, n + 1 = second integer
n(n + 1) = 132
n² + n − 132 = 0
(n + 12)(n − 11) = 0
n = −12 (reject, need positive) or n = 11

The integers are 11 and 12.
```

**Example: Rectangle Dimensions**
```
A rectangle has length 3 feet more than its width.
Area is 40 square feet. Find dimensions.

Let w = width, w + 3 = length
w(w + 3) = 40
w² + 3w − 40 = 0
(w + 8)(w − 5) = 0
w = −8 (reject) or w = 5

Width = 5 ft, Length = 8 ft
```

**Example: Pythagorean Theorem**
```
One leg of a right triangle is 7 cm less than the other.
Hypotenuse is 13 cm. Find the legs.

Let x = longer leg, x − 7 = shorter leg
x² + (x − 7)² = 13²
x² + x² − 14x + 49 = 169
2x² − 14x − 120 = 0
x² − 7x − 60 = 0
(x − 12)(x + 5) = 0
x = 12 (x = −5 rejected)

Legs are 12 cm and 5 cm.
```

### Practice Problems

1. Solve:
   a) (x − 4)(x + 2) = 0
   b) x² + 5x + 6 = 0
   c) x² − 8x + 15 = 0
   d) 3x² − 10x + 8 = 0
   e) x² = 5x
   f) 4x² − 25 = 0

2. Word problems:
   a) The product of two consecutive even integers is 168. Find them.
   b) A rectangle's length is 5 more than twice its width. Area is 63 sq ft. Find dimensions.
   c) One leg of a right triangle is 1 foot more than the other leg. The hypotenuse is √41 feet. Find the legs.
