"""Calculus template: secant slope tends to the tangent slope f'(x).

Storyboard notes (replace with course values before use):
- concept ID: calc.derivative.secant-limit (keep the course's notation/ID).
- prereq: function notation, slope of a line, limit intuition.
- hypotheses: f(x) = x^2 / 2 on [0, 4]; f is smooth so the secant limit exists.
- success check: learner predicts f'(3) before the sweep, then explains why
  the secant readout settles onto the tangent value as h shrinks.
- one clear change per cue: c1 draws axes/curve, c2 shows the secant with two
  points, c3 shrinks h so the secant becomes the tangent, c4 sweeps x with the
  tangent and readout following.
- silent preview: give every cue an explicit ``duration``, then run
  ``voice_synthesizer.py --storyboard <storyboard.json> --out <out_dir> --silent``.
  Point GNOS_MANIFEST at the resulting ``timing_manifest.json``.
- aspect 16:9 bounds: frame x in [-7.11, 7.11], y in [-4.0, 4.0]. Axes
  (x_length 7.5, y_length 4.5, shifted DOWN*0.5) span about x +/-3.75 and
  y [-2.75, 1.75]; the readout is pinned to UL so labels stay in frame.
- camera: stable. No camera movement; the secant-to-tangent morph is the only
  structural change so the compared quantity stays visible.
"""
from pathlib import Path
import os
import sys
from manim import *

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "skills/manim-voice-animation/scripts"))
from cue_player import CuePlayer


class CalculusPlotScene(Scene):
    """Secant-to-tangent sweep; readout shares state with the geometry.

    ``x_tracker`` holds the base point and ``h_tracker`` holds the secant
    separation. Both the secant group and the DecimalNumber read
    ``(f(x + h) - f(x)) / h`` from the same trackers, so the displayed slope
    cannot drift from the drawn line. No MathTex is rebuilt per frame.
    """

    def construct(self):
        manifest = Path(
            os.environ.get(
                "GNOS_MANIFEST",
                ROOT / "output/calculus-plot/audio/timing_manifest.json",
            )
        )
        player = CuePlayer(self, manifest, "CalculusPlotScene")

        axes = Axes(
            x_range=[-1, 5, 1],
            y_range=[-1, 9, 2],
            x_length=7.5,
            y_length=4.5,
            axis_config={"color": GREY_B, "stroke_width": 2},
            tips=False,
        ).shift(DOWN * 0.5)
        labels = axes.get_axis_labels(x_label="x", y_label="f(x)")

        # Shared state: f and its derivative; the readout uses the same f.
        f = lambda x: 0.5 * (x**2)
        secant_slope = lambda x, h: (f(x + h) - f(x)) / h if h != 0 else x
        curve = axes.plot(f, x_range=[0, 4], color=BLUE_C, stroke_width=3.5)
        curve_label = axes.get_graph_label(
            curve, label=r"f(x) = \frac{1}{2}x^2", x_val=3.8, direction=UL
        )

        x_tracker = ValueTracker(1.0)
        h_tracker = ValueTracker(0.6)

        x_dot = always_redraw(
            lambda: Dot(
                point=axes.c2p(x_tracker.get_value(), f(x_tracker.get_value())),
                color=RED,
                radius=0.09,
            )
        )
        h_dot = always_redraw(
            lambda: Dot(
                point=axes.c2p(
                    x_tracker.get_value() + h_tracker.get_value(),
                    f(x_tracker.get_value() + h_tracker.get_value()),
                ),
                color=ORANGE,
                radius=0.07,
            )
        )
        secant_group = always_redraw(
            lambda: axes.get_secant_slope_group(
                x=x_tracker.get_value(),
                graph=curve,
                dx=max(h_tracker.get_value(), 0.005),
                secant_line_length=3.5,
                secant_line_color=YELLOW,
            )
        )

        # Numeric glyphs update in place; rebuilding MathTex every frame is
        # slow and can make the label flicker during a sweep.
        slope_value = DecimalNumber(
            secant_slope(1.0, 0.6),
            num_decimal_places=2,
            mob_class=Text,
            color=YELLOW,
            font_size=30,
        )
        slope_value.add_updater(
            lambda mob: mob.set_value(
                secant_slope(x_tracker.get_value(), max(h_tracker.get_value(), 1e-6))
            )
        )
        slope_label = VGroup(
            MathTex(r"f'(x) \approx", color=YELLOW),
            slope_value,
        ).arrange(RIGHT, buff=0.12).to_corner(UL).shift(DOWN * 0.8)

        # c1_axes: establish axes, curve, and label.
        player.play(
            "c1_axes", Create(axes), Write(labels), Create(curve), Write(curve_label),
            run_time=2.0,
        )
        # c2_secant: reveal the secant with two visible points and its slope.
        player.play(
            "c2_secant",
            Create(x_dot),
            Create(h_dot),
            Create(secant_group),
            Write(slope_label),
            run_time=1.5,
        )
        # c3_tangent: shrink h so the secant morphs into the tangent; the
        # readout converges because it reads the same h.
        player.play("c3_tangent", h_tracker.animate.set_value(0.005), run_time=2.5)
        # c4_sweep: move x along the curve; tangent and readout follow together.
        player.play("c4_sweep", x_tracker.animate.set_value(3.5), run_time=3.5)

        slope_value.clear_updaters()
        x_dot.clear_updaters()
        h_dot.clear_updaters()
        secant_group.clear_updaters()
        player.finish(
            os.environ.get(
                "GNOS_TIMELINE_PREFIX", str(ROOT / "output/calculus-plot/lesson")
            )
        )
