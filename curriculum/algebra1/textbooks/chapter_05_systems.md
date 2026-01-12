# Chapter 5: Systems of Linear Equations

Source: OpenStax Elementary Algebra 2e (CC BY 4.0)

---

## 5.1 Solve Systems of Equations by Graphing

### Learning Objectives
- Determine whether an ordered pair is a solution of a system
- Solve a system of linear equations by graphing
- Determine the number of solutions of a linear system
- Solve applications of systems by graphing

### Key Concepts

**System of Linear Equations**
Two or more linear equations considered together.
```
Example:
x + y = 7
x − y = 3
```

**Solution of a System**
An ordered pair (x, y) that satisfies ALL equations in the system.

### Types of Systems

| Graph Appearance | Number of Solutions | System Type |
|-----------------|---------------------|-------------|
| Lines intersect | One solution | Consistent & Independent |
| Lines are parallel | No solution | Inconsistent |
| Lines are the same | Infinitely many | Consistent & Dependent |

### Examples

**Example 1:** Determine if (2, 5) is a solution of the system:
```
x + y = 7
x − y = −3

Check first equation: 2 + 5 = 7 ✓
Check second equation: 2 − 5 = −3 ✓
Yes, (2, 5) is a solution.
```

**Example 2:** Solve by graphing:
```
y = 2x + 1
y = −x + 4

Graph both lines:
Line 1: slope 2, y-intercept (0, 1)
Line 2: slope −1, y-intercept (0, 4)

Intersection point: (1, 3)

Check: 3 = 2(1) + 1 ✓ and 3 = −1 + 4 ✓
Solution: (1, 3)
```

**Example 3:** System with no solution (parallel lines):
```
y = 2x + 3
y = 2x − 1

Same slope (m = 2), different y-intercepts.
Lines are parallel → No solution.
```

**Example 4:** System with infinitely many solutions:
```
y = 3x − 2
6x − 2y = 4

Rewrite second equation: y = 3x − 2
Same line! Infinitely many solutions.
```

### Practice Problems

1. Determine if the ordered pair is a solution:
   a) (3, 4) for x + y = 7 and 2x − y = 2
   b) (−1, 5) for 3x + y = 2 and x − y = −6
   c) (2, −1) for x + 2y = 0 and 3x − y = 7

2. Solve by graphing:
   a) y = x + 1 and y = −x + 5
   b) y = 2x − 3 and y = 2x + 1
   c) x + y = 4 and 2x + 2y = 8

---

## 5.2 Solve Systems of Equations by Substitution

### Learning Objectives
- Solve a system of equations by substitution
- Solve applications using substitution

### Substitution Method Steps

1. Solve one equation for one variable
2. Substitute that expression into the other equation
3. Solve for the remaining variable
4. Substitute back to find the other variable
5. Check in BOTH original equations

### Examples

**Example 1:** Solve the system:
```
y = 3x − 5
2x + y = 10

Substitute y = 3x − 5 into second equation:
2x + (3x − 5) = 10
5x − 5 = 10
5x = 15
x = 3

Find y: y = 3(3) − 5 = 4

Solution: (3, 4)

Check: 4 = 3(3) − 5 = 4 ✓
       2(3) + 4 = 10 ✓
```

**Example 2:** Solve:
```
3x + y = 7
5x − 2y = 8

Solve first equation for y:
y = 7 − 3x

Substitute:
5x − 2(7 − 3x) = 8
5x − 14 + 6x = 8
11x = 22
x = 2

Find y: y = 7 − 3(2) = 1

Solution: (2, 1)
```

**Example 3:** No solution:
```
2x + y = 6
2x + y = 10

Solve for y: y = 6 − 2x

Substitute:
2x + (6 − 2x) = 10
6 = 10 (FALSE!)

No solution.
```

### Practice Problems

1. Solve by substitution:
   a) y = 2x − 1 and 3x + y = 9
   b) x = y + 3 and 2x + 3y = 11
   c) x + 2y = 7 and 3x − y = 7

---

## 5.3 Solve Systems of Equations by Elimination

### Learning Objectives
- Solve a system of equations by elimination
- Solve applications using elimination

### Elimination Method Steps

1. Write both equations in standard form (Ax + By = C)
2. Make the coefficients of one variable opposites
3. Add the equations to eliminate that variable
4. Solve for the remaining variable
5. Substitute back to find the other variable
6. Check in both original equations

### Examples

**Example 1:** Solve (opposites already):
```
x + y = 5
x − y = 1

Add equations:
2x = 6
x = 3

Substitute: 3 + y = 5 → y = 2

Solution: (3, 2)
```

**Example 2:** Solve (need to multiply one equation):
```
3x + 2y = 16
x + y = 6

Multiply second equation by −2:
3x + 2y = 16
−2x − 2y = −12

Add:
x = 4

Substitute: 4 + y = 6 → y = 2

Solution: (4, 2)
```

**Example 3:** Solve (need to multiply both equations):
```
2x + 3y = 11
3x + 2y = 9

Multiply first by 3: 6x + 9y = 33
Multiply second by −2: −6x − 4y = −18

Add:
5y = 15
y = 3

Substitute: 2x + 3(3) = 11 → x = 1

Solution: (1, 3)
```

### Practice Problems

1. Solve by elimination:
   a) x + y = 10 and x − y = 2
   b) 2x + y = 7 and x − y = 2
   c) 3x + 4y = 10 and 2x − 3y = 1

---

## 5.4 Solve Applications with Systems of Equations

### Common Application Types

**1. Number Problems**
```
The sum of two numbers is 25. One number is 5 more than the other.

Let x = first number, y = second number
x + y = 25
x = y + 5

Substitute: (y + 5) + y = 25
2y = 20, y = 10, x = 15
```

**2. Ticket/Coin Problems**
```
Adult tickets cost $8, child tickets cost $5.
Total 200 tickets sold for $1300.

Let a = adult tickets, c = child tickets
a + c = 200
8a + 5c = 1300

Multiply first by −5: −5a − 5c = −1000
Add: 3a = 300, a = 100

So: 100 adult tickets, 100 child tickets
```

**3. Mixture Problems**
```
How much of 20% solution and 50% solution
needed to make 30 liters of 40% solution?

Let x = liters of 20%, y = liters of 50%
x + y = 30           (total volume)
0.20x + 0.50y = 0.40(30)   (concentration)

Solve: x = 10 liters (20%), y = 20 liters (50%)
```

**4. Distance/Rate/Time Problems**
```
A boat travels 36 miles downstream in 2 hours.
The return trip upstream takes 3 hours.
Find the speed of the boat and current.

Let b = boat speed, c = current speed
Downstream: 2(b + c) = 36 → b + c = 18
Upstream: 3(b − c) = 36 → b − c = 12

Add: 2b = 30, b = 15 mph
Current: c = 3 mph
```

### Practice Problems

1. The sum of two numbers is 84. Their difference is 16. Find the numbers.

2. Concert tickets cost $25 for adults and $15 for students. If 400 tickets were sold for $8000, how many of each type were sold?

3. A plane flies 600 miles with the wind in 2 hours. The return trip against the wind takes 3 hours. Find the speed of the plane and the wind.

---

## 5.6 Graphing Systems of Linear Inequalities

### Learning Objectives
- Determine whether an ordered pair is a solution
- Graph a system of linear inequalities
- Solve applications involving systems of inequalities

### Graphing Steps

1. Graph each inequality separately
2. The solution is the intersection (overlap) of all shaded regions
3. Check a point in the intersection to verify

### Examples

**Example 1:** Graph the system:
```
y ≤ 2x + 3
y > −x + 1

1. Graph y = 2x + 3 (solid line), shade below
2. Graph y = −x + 1 (dashed line), shade above
3. Solution is the overlapping region
```

**Example 2:** Graph the system:
```
x + y ≤ 6
x ≥ 1
y ≥ 0

Solution is a triangular region bounded by:
- The line x + y = 6
- The vertical line x = 1
- The x-axis (y = 0)
```

### Practice Problems

1. Graph the system:
   a) y < x + 3 and y ≥ −2x + 1
   b) x + y ≤ 5 and x − y < 3
   c) y > 0 and x > 0 and x + y ≤ 4
