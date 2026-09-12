from manim import *

class LinearAlgebraScene(LinearTransformationScene):
    """
    Template for a linear-algebra target: observe a basis transformation.
    Inherits from LinearTransformationScene to track the grid and basis vectors.
    """
    def __init__(self, **kwargs):
        super().__init__(
            show_coordinates=True,
            leave_ghost_vectors=True,
            show_basis_vectors=True,
            **kwargs
        )

    def construct(self):
        # 1. Formula Header (pinned to viewport foreground)
        title = Title("Linear Transformation: Horizontal Shear", color=WHITE)
        matrix_tex = MathTex(
            r"A = \begin{bmatrix} 1 & 1.5 \\ 0 & 1 \end{bmatrix}"
        ).to_corner(UL).shift(DOWN * 0.5)

        self.add_foreground_mobject(title)
        self.add_foreground_mobject(matrix_tex)
        self.wait(1.0)

        # 2. Add an arbitrary target vector to observe its transformation
        target_vec = Vector([1, 2], color=PURPLE)
        vec_label = MathTex(r"\vec{v} = \begin{bmatrix} 1 \\ 2 \end{bmatrix}", color=PURPLE).next_to(target_vec.get_end(), UR)
        self.add_vector(target_vec, animate=True)
        self.add(vec_label)
        vec_label.add_updater(lambda mob: mob.next_to(target_vec.get_end(), UR))
        self.wait(1.0)

        # 3. Apply 2x2 Shear Matrix: [[1, 1.5], [0, 1]]
        # Notice that basis vector j_hat shears to [1.5, 1], while i_hat stays at [1, 0]
        shear_matrix = [[1, 1.5], [0, 1]]
        self.apply_matrix(shear_matrix, run_time=3.0)
        vec_label.clear_updaters()
        self.wait(2.0)
