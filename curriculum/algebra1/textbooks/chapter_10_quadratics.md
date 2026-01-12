# Chapter 10: Quadratic Equations

Source: OpenStax Elementary Algebra 2e (CC BY 4.0)

---

## 10.1 Solve Quadratic Equations Using the Square Root Property

### Learning Objectives
- Solve quadratic equations using the Square Root Property
- Solve applications

### Square Root Property

If x² = k, then x = √k or x = −√k (written x = ±√k)

### Examples

**Example 1:** Solve x² = 49
```
x² = 49
x = ±√49
x = ±7
Solutions: x = 7 or x = −7
```

**Example 2:** Solve x² = 12
```
x² = 12
x = ±√12
x = ±2√3
Solutions: x = 2√3 or x = −2√3
```

**Example 3:** Solve (x − 3)² = 25
```
(x − 3)² = 25
x − 3 = ±5
x = 3 + 5 = 8  or  x = 3 − 5 = −2
Solutions: x = 8 or x = −2
```

**Example 4:** Solve (2x + 1)² = 18
```
(2x + 1)² = 18
2x + 1 = ±√18
2x + 1 = ±3√2
2x = −1 ± 3√2
x = (−1 ± 3√2)/2
```

### Practice Problems

1. Solve:
   a) x² = 81
   b) x² = 20
   c) y² − 36 = 0
   d) 3x² = 75

2. Solve:
   a) (x + 4)² = 16
   b) (x − 5)² = 9
   c) (2x − 3)² = 49
   d) (x + 2)² = 12

---

## 10.2 Solve Quadratic Equations by Completing the Square

### Learning Objectives
- Complete the square of a binomial expression
- Solve quadratic equations by completing the square

### Completing the Square Method

To complete the square for x² + bx:
1. Take half of b: b/2
2. Square it: (b/2)²
3. Add and subtract: x² + bx + (b/2)² = (x + b/2)²

### Solving by Completing the Square

1. Move constant to right side
2. If a ≠ 1, divide all terms by a
3. Complete the square on left (add (b/2)² to both sides)
4. Factor left side as a perfect square
5. Apply Square Root Property
6. Solve for x

### Examples

**Example 1:** Complete the square: x² + 8x + ___
```
b = 8
b/2 = 4
(b/2)² = 16

x² + 8x + 16 = (x + 4)²
```

**Example 2:** Solve x² + 6x = 7
```
x² + 6x = 7
x² + 6x + 9 = 7 + 9      (add (6/2)² = 9 to both sides)
(x + 3)² = 16
x + 3 = ±4
x = −3 + 4 = 1  or  x = −3 − 4 = −7

Solutions: x = 1 or x = −7
```

**Example 3:** Solve x² − 10x + 14 = 0
```
x² − 10x = −14
x² − 10x + 25 = −14 + 25    (add (−10/2)² = 25)
(x − 5)² = 11
x − 5 = ±√11
x = 5 ± √11

Solutions: x = 5 + √11 or x = 5 − √11
```

**Example 4:** Solve 2x² + 8x − 5 = 0
```
2x² + 8x = 5
x² + 4x = 5/2              (divide by 2)
x² + 4x + 4 = 5/2 + 4      (add (4/2)² = 4)
(x + 2)² = 13/2
x + 2 = ±√(13/2)
x = −2 ± √(13/2)
x = −2 ± (√26)/2
```

### Geometric Interpretation

Completing the square can be visualized geometrically:
```
x² + 6x + ? = (x + 3)²

[x][x] + [x][3] + [3][x] + [3][3]
= x² + 3x + 3x + 9
= x² + 6x + 9
```

### Practice Problems

1. Complete the square:
   a) x² + 10x + ___
   b) x² − 4x + ___
   c) x² + 7x + ___

2. Solve by completing the square:
   a) x² + 4x = 12
   b) x² − 8x + 7 = 0
   c) x² + 3x − 5 = 0
   d) 2x² + 12x + 10 = 0

---

## 10.3 Solve Quadratic Equations Using the Quadratic Formula

### Learning Objectives
- Solve quadratic equations using the Quadratic Formula
- Use the discriminant to predict the number of solutions

### The Quadratic Formula

For ax² + bx + c = 0 (where a ≠ 0):

$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$

### Steps to Use the Formula

1. Write equation in standard form: ax² + bx + c = 0
2. Identify a, b, and c
3. Substitute into the formula
4. Simplify
5. Check solutions

### Examples

**Example 1:** Solve x² + 5x + 6 = 0
```
a = 1, b = 5, c = 6

x = (−5 ± √(25 − 24))/2
x = (−5 ± √1)/2
x = (−5 ± 1)/2

x = (−5 + 1)/2 = −2  or  x = (−5 − 1)/2 = −3
```

**Example 2:** Solve 2x² − 7x + 3 = 0
```
a = 2, b = −7, c = 3

x = (7 ± √(49 − 24))/4
x = (7 ± √25)/4
x = (7 ± 5)/4

x = 12/4 = 3  or  x = 2/4 = 1/2
```

**Example 3:** Solve x² − 4x − 2 = 0
```
a = 1, b = −4, c = −2

x = (4 ± √(16 + 8))/2
x = (4 ± √24)/2
x = (4 ± 2√6)/2
x = 2 ± √6
```

**Example 4:** Solve x² + 2x + 5 = 0
```
a = 1, b = 2, c = 5

x = (−2 ± √(4 − 20))/2
x = (−2 ± √(−16))/2

No real solutions (negative under the radical)
```

### The Discriminant

The discriminant is b² − 4ac. It tells us the number of solutions:

| Discriminant | Number of Solutions | Type |
|-------------|---------------------|------|
| b² − 4ac > 0 | Two | Real and distinct |
| b² − 4ac = 0 | One | Real (repeated) |
| b² − 4ac < 0 | None | No real solutions |

### Examples Using Discriminant

**Example:** Determine the number of solutions for 3x² + 4x + 2 = 0
```
b² − 4ac = 16 − 24 = −8 < 0
No real solutions.
```

**Example:** Determine the number of solutions for x² − 6x + 9 = 0
```
b² − 4ac = 36 − 36 = 0
One real solution.
```

### Practice Problems

1. Solve using the quadratic formula:
   a) x² + 7x + 10 = 0
   b) 2x² + 3x − 2 = 0
   c) x² − 6x + 4 = 0
   d) 3x² + 2x − 5 = 0

2. Use the discriminant to determine the number of solutions:
   a) x² + 4x + 4 = 0
   b) 2x² + 3x + 5 = 0
   c) x² − 5x + 2 = 0

---

## 10.4 Solve Applications Modeled by Quadratic Equations

### Common Application Types

**1. Area Problems**

**Example:** A rectangle has length 4 cm more than its width. Area is 45 cm². Find dimensions.
```
Let w = width, w + 4 = length
w(w + 4) = 45
w² + 4w − 45 = 0
(w + 9)(w − 5) = 0
w = 5 (reject w = −9)

Width = 5 cm, Length = 9 cm
```

**2. Projectile Motion**

Height of an object: h = −16t² + v₀t + h₀

**Example:** A ball is thrown upward from 6 feet with initial velocity 80 ft/s.
When does it hit the ground?
```
h = −16t² + 80t + 6 = 0

Using quadratic formula:
t = (−80 ± √(6400 + 384))/(−32)
t = (−80 ± √6784)/(−32)
t ≈ 5.07 seconds (reject negative answer)
```

**3. Number Problems**

**Example:** The sum of a number and its square is 72. Find the number.
```
n + n² = 72
n² + n − 72 = 0
(n + 9)(n − 8) = 0
n = 8 or n = −9

Two solutions: 8 or −9
```

**4. Pythagorean Theorem**

**Example:** A ladder leans against a wall. The bottom is 5 feet from the wall.
The ladder reaches 12 feet up the wall. How long is the ladder?
```
5² + 12² = c²
25 + 144 = c²
c² = 169
c = 13 feet
```

### Practice Problems

1. A rectangle's length is twice its width. Area is 32 sq meters. Find dimensions.

2. A ball is dropped from 144 feet. When does it hit the ground? (h = 144 − 16t²)

3. The product of two consecutive odd integers is 143. Find them.

4. One leg of a right triangle is 2 feet longer than the other. The hypotenuse is 10 feet. Find the legs.

---

## 10.5 Graphing Quadratic Equations in Two Variables

### Learning Objectives
- Recognize the graph of a quadratic equation (parabola)
- Find the vertex, axis of symmetry, and intercepts
- Graph quadratic equations

### Key Features of a Parabola

**Standard Form:** y = ax² + bx + c

**Vertex:** The highest or lowest point
- x-coordinate: x = −b/(2a)
- y-coordinate: substitute x into the equation

**Axis of Symmetry:** x = −b/(2a) (vertical line through vertex)

**Direction:**
- If a > 0, parabola opens UP (minimum)
- If a < 0, parabola opens DOWN (maximum)

**y-intercept:** (0, c)

**x-intercepts:** Set y = 0 and solve ax² + bx + c = 0

### Examples

**Example 1:** Graph y = x² − 4x + 3

```
a = 1, b = −4, c = 3

Vertex:
x = −(−4)/(2·1) = 2
y = (2)² − 4(2) + 3 = 4 − 8 + 3 = −1
Vertex: (2, −1)

Axis of symmetry: x = 2

Opens UP (a > 0)

y-intercept: (0, 3)

x-intercepts: x² − 4x + 3 = 0
(x − 1)(x − 3) = 0
x = 1 or x = 3
Points: (1, 0) and (3, 0)
```

**Example 2:** Graph y = −x² + 6x − 5

```
a = −1, b = 6, c = −5

Vertex:
x = −6/(2·−1) = 3
y = −(3)² + 6(3) − 5 = −9 + 18 − 5 = 4
Vertex: (3, 4)

Axis of symmetry: x = 3

Opens DOWN (a < 0)

y-intercept: (0, −5)

x-intercepts: −x² + 6x − 5 = 0
x² − 6x + 5 = 0
(x − 1)(x − 5) = 0
x = 1 or x = 5
```

### Vertex Form

y = a(x − h)² + k

- Vertex: (h, k)
- Opens up if a > 0, down if a < 0

**Example:** y = 2(x − 3)² + 1
- Vertex: (3, 1)
- Opens UP
- Axis of symmetry: x = 3

### Practice Problems

1. Find vertex, axis of symmetry, and direction:
   a) y = x² + 2x − 3
   b) y = −x² + 4x
   c) y = 2x² − 8x + 6

2. Find all intercepts:
   a) y = x² − 5x + 4
   b) y = x² + 4x + 4
   c) y = x² + 1 (note: no x-intercepts)

3. Graph each parabola:
   a) y = x² − 2x − 8
   b) y = −x² + 2x + 3
   c) y = (x − 1)² − 4

---

## Summary: Methods for Solving Quadratic Equations

| Method | Best Used When |
|--------|----------------|
| Factoring | Equation factors easily |
| Square Root Property | No linear term (x² = k) |
| Completing the Square | Leading coefficient is 1, or for deriving formula |
| Quadratic Formula | Always works; use when factoring is difficult |

### Choosing a Method

1. **First**, can you factor easily? → Factor
2. **Is it** x² = k or (x + a)² = k? → Square Root Property
3. **Otherwise** → Quadratic Formula (most reliable)
