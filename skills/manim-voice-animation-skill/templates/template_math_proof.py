from manim import *

class MathProofScene(Scene):
    """
    Template for Mathematical Theorem & Proof Derivations.
    Demonstrates formula morphing with MathTex and geometric visualization.
    """
    def construct(self):
        # 1. Title Header
        title = Title("The Pythagorean Theorem", color=WHITE)
        self.play(Write(title), run_time=1.0)
        self.wait(0.5)

        # 2. Geometric Right Triangle
        triangle = Polygon(
            [-2, -1, 0], [1, -1, 0], [-2, 1.5, 0],
            color=BLUE, stroke_width=3, fill_opacity=0.2, fill_color=BLUE_E
        )
        right_angle = RightAngle(
            Line([-2, 1.5, 0], [-2, -1, 0]),
            Line([-2, -1, 0], [1, -1, 0]),
            length=0.3, color=YELLOW
        )

        label_a = MathTex("a", color=TEAL).next_to(triangle, LEFT, buff=0.2)
        label_b = MathTex("b", color=GREEN).next_to(triangle, DOWN, buff=0.2)
        label_c = MathTex("c", color=GOLD).move_to([-0.3, 0.4, 0])

        triangle_group = VGroup(triangle, right_angle, label_a, label_b, label_c)
        self.play(Create(triangle), Create(right_angle), run_time=1.5)
        self.play(Write(label_a), Write(label_b), Write(label_c), run_time=1.0)
        self.wait(1.0)

        # 3. Algebraic Relationship
        eq_initial = MathTex(
            r"a^2", r"+", r"b^2", r"=", r"c^2",
            substrings_to_isolate=[r"a^2", r"b^2", r"c^2"]
        ).shift(RIGHT * 3.5 + UP * 0.5)

        eq_initial.set_color_by_tex(r"a^2", TEAL)
        eq_initial.set_color_by_tex(r"b^2", GREEN)
        eq_initial.set_color_by_tex(r"c^2", GOLD)

        self.play(Write(eq_initial), run_time=1.5)
        self.wait(1.0)

        # 4. Solved for Hypotenuse
        eq_solved = MathTex(
            r"c", r"=", r"\sqrt{", r"a^2", r"+", r"b^2", r"}",
            substrings_to_isolate=[r"c", r"a^2", r"b^2"]
        ).shift(RIGHT * 3.5 + UP * 0.5)

        eq_solved.set_color_by_tex(r"c", GOLD)
        eq_solved.set_color_by_tex(r"a^2", TEAL)
        eq_solved.set_color_by_tex(r"b^2", GREEN)

        self.play(
            TransformMatchingTex(eq_initial, eq_solved, transform_mismatches=True),
            run_time=2.0
        )
        self.wait(1.5)
