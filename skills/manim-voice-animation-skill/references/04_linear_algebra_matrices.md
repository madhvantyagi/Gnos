# Linear Algebra & Matrix Transformations

Linear algebra animations rely on geometric transformations of coordinate grids, basis vectors, and area scaling.

Name the representation being taught: a vector as a point, a directed arrow, a
column of coordinates, or a linear combination. Keep the same basis while the
matrix acts, and state the matrix convention (columns map the basis vectors).
Ask for a prediction before applying the transform, then verify one coordinate,
one invariant, or the determinant. The transformed picture is a check on the
algebra, not a proof that the learner can generalize it.

---

## 1. Vector Operations & Linear Combinations

```python
from manim import *

class VectorAdditionScene(Scene):
    def construct(self):
        plane = NumberPlane(
            x_range=[-5, 5, 1],
            y_range=[-4, 4, 1],
            background_line_style={"stroke_color": GREY_D, "stroke_width": 1}
        )
        self.add(plane)

        # Vector v1 = [2, 1], Vector v2 = [1, 2]
        v1 = Vector([2, 1], color=YELLOW)
        v2 = Vector([1, 2], color=TEAL)
        
        v1_label = MathTex(r"\vec{v}_1", color=YELLOW).next_to(v1.get_end(), RIGHT)
        v2_label = MathTex(r"\vec{v}_2", color=TEAL).next_to(v2.get_end(), UP)

        self.play(GrowArrow(v1), Write(v1_label))
        self.play(GrowArrow(v2), Write(v2_label))
        self.wait(1)

        # Tip-to-tail addition: shift v2 to the tip of v1
        self.play(v2.animate.shift(v1.get_end()), v2_label.animate.shift(v1.get_end()))
        
        # Resultant vector v_sum = [3, 3]
        v_sum = Vector([3, 3], color=RED)
        v_sum_label = MathTex(r"\vec{v}_1 + \vec{v}_2", color=RED).next_to(v_sum.get_end(), UR)
        self.play(GrowArrow(v_sum), Write(v_sum_label))
```

---

## 2. Matrix Transformations via `LinearTransformationScene`

Manim provides a dedicated `LinearTransformationScene` that transforms the background coordinate grid and basis vectors:

```python
from manim import *

class MatrixTransformScene(LinearTransformationScene):
    def __init__(self, **kwargs):
        super().__init__(
            show_coordinates=True,
            leave_ghost_vectors=True,
            show_basis_vectors=True,
            **kwargs
        )

    def construct(self):
        # 2x2 Shear Matrix: [[1, 1], [0, 1]]
        matrix = [[1, 1], [0, 1]]
        
        # Display the matrix on screen (pinned to foreground so it doesn't transform)
        matrix_tex = MathTex(r"A = \begin{bmatrix} 1 & 1 \\ 0 & 1 \end{bmatrix}").to_corner(UL)
        self.add_foreground_mobject(matrix_tex)
        
        # Transform the space
        self.apply_matrix(matrix, run_time=3)
        self.wait(1)
```

---

## 3. Determinant as Area Scaling

Visualizing how the unit square formed by basis vectors transforms into a parallelogram with area equal to $|\det(A)|$:

```python
class DeterminantVisualization(LinearTransformationScene):
    def construct(self):
        # Add unit square spanned by i_hat and j_hat
        unit_square = self.get_unit_square(color=BLUE, opacity=0.5)
        det_label = MathTex(r"\text{Area} = \det(A)").to_corner(UR)
        self.add_foreground_mobject(det_label)

        self.add_transformable_mobject(unit_square)
        self.wait(1)

        # Apply transformation with determinant = 2
        matrix = [[2, 1], [0, 1]]
        self.apply_matrix(matrix, run_time=2.5)
```

---

## 4. Eigenvector Invariance

An eigenvector only scales along its original line of span during a matrix transformation:

```python
class EigenvectorScene(LinearTransformationScene):
    def construct(self):
        # Matrix with eigenvector along [1, 0] and [1, 1]
        matrix = [[2, 0], [0, 1]]
        
        eigen_vec = Vector([2, 0], color=GOLD)
        non_eigen = Vector([1, 1], color=PURPLE)
        
        self.add_vector(eigen_vec, animate=True)
        self.add_vector(non_eigen, animate=True)
        self.wait(1)

        # During transformation, eigen_vec stays on the x-axis; non_eigen changes
        # direction because it is not an eigenvector of this matrix.
        self.apply_matrix(matrix, run_time=3)
```

For a foreground formula, pin only the formula that describes the current
operation. Labels attached to a moving vector should either transform with it
or follow it with a lightweight updater; a fixed label that stays behind makes
the geometric claim ambiguous.
