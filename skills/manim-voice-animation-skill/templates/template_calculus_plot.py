from manim import *

class CalculusPlotScene(Scene):
    """
    Template for a calculus target: connect a tangent slope to f'(x).
    Replace the target and add the course/learner cue plan before use.
    """
    def construct(self):
        # 1. Setup Axes
        axes = Axes(
            x_range=[-1, 5, 1],
            y_range=[-1, 9, 2],
            x_length=7.5,
            y_length=4.5,
            axis_config={"color": GREY_B, "stroke_width": 2},
            tips=False
        ).shift(DOWN * 0.5)

        labels = axes.get_axis_labels(x_label="x", y_label="f(x)")
        self.play(Create(axes), Write(labels), run_time=1.5)

        # 2. Quadratic Curve: f(x) = x^2 / 2
        f = lambda x: 0.5 * (x ** 2)
        curve = axes.plot(f, x_range=[0, 4], color=BLUE_C, stroke_width=3.5)
        curve_label = axes.get_graph_label(curve, label=r"f(x) = \frac{1}{2}x^2", x_val=3.8, direction=UL)
        
        self.play(Create(curve), Write(curve_label), run_time=1.5)
        self.wait(0.5)

        # 3. Dynamic Moving Tangent Point
        x_tracker = ValueTracker(1.0)

        point_on_curve = always_redraw(lambda: Dot(
            point=axes.c2p(x_tracker.get_value(), f(x_tracker.get_value())),
            color=RED,
            radius=0.09
        ))

        tangent_group = always_redraw(lambda: axes.get_secant_slope_group(
            x=x_tracker.get_value(),
            graph=curve,
            dx=0.005,
            secant_line_length=3.5,
            secant_line_color=YELLOW
        ))

        # Update the numeric glyphs in place; rebuilding MathTex every frame is
        # slow and can make the label flicker during a sweep.
        slope_value = DecimalNumber(
            x_tracker.get_value(),
            num_decimal_places=1,
            mob_class=Text,
            color=YELLOW,
            font_size=30,
        )
        slope_label = VGroup(
            MathTex(r"f'(x) =", color=YELLOW),
            slope_value,
        ).arrange(RIGHT, buff=0.12).to_corner(UL).shift(DOWN * 0.8)
        slope_value.add_updater(
            lambda mob: mob.set_value(x_tracker.get_value())
        )

        self.play(Create(point_on_curve), Create(tangent_group), Write(slope_label), run_time=1.0)
        self.wait(0.5)

        # 4. Sweep x along the curve from 1.0 to 3.5
        self.play(
            x_tracker.animate.set_value(3.5),
            run_time=3.5,
            rate_func=linear
        )
        slope_value.clear_updaters()
        self.wait(1.5)
