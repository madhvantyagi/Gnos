"""Math proof template: one proof step per cue with a measured numeric check.

Storyboard notes (replace with course values before use):
- concept ID: math.pythagoras.implication (keep the course's notation/ID).
- prereq: right-triangle vocabulary, squares and square roots.
- hypotheses: right angle at C; legs a, b; hypotenuse c; Euclidean plane.
- success check: learner predicts c for 5-12-13 or explains why
  ``c = sqrt(a^2 + b^2)`` follows from ``a^2 + b^2 = c^2``.
- one clear change per cue: c1 draws the triangle, c2 states the relation,
  c3 morphs to the solved form, c4 instantiates 3-4-5 and measures c.
- silent preview: give every cue an explicit ``duration``, then run
  ``voice_synthesizer.py --storyboard <storyboard.json> --out <out_dir> --silent``.
  Measured clips (``--audio-dir`` or synthesis) replace those durations.
  Point GNOS_MANIFEST at the resulting ``timing_manifest.json``.
- aspect 16:9 bounds: frame x in [-7.11, 7.11], y in [-4.0, 4.0]. All shifts
  below stay under 6 (X) and 3.5 (Y); title/equations/check row use
  to_edge/to_corner/next_to with a buff so labels stay in frame.
- camera: stable. No camera movement; motion is limited to the proof reveal
  and the hypotenuse measure so attention stays on the implication.
"""
from pathlib import Path
import os
import sys
from manim import *

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "skills/manim-voice-animation/scripts"))
from cue_player import CuePlayer


class MathProofScene(Scene):
    """Stepwise Pythagoras reveal; numbers share state with the geometry.

    The triangle legs are built from A_LEN/B_LEN and C_LEN is derived from
    the same constants, so the displayed 3-4-5 check cannot drift from the
    figure. The only per-frame work is a Dot sliding along the hypotenuse
    and one DecimalNumber driven by the same tracker; equations morph once
    via TransformMatchingTex (no MathTex rebuild per frame).
    """

    def construct(self):
        manifest = Path(
            os.environ.get(
                "GNOS_MANIFEST",
                ROOT / "output/math-proof/audio/timing_manifest.json",
            )
        )
        player = CuePlayer(self, manifest, "MathProofScene")

        # Shared numeric state: geometry and readouts derive from these.
        A_LEN, B_LEN = 3.0, 4.0
        C_LEN = (A_LEN**2 + B_LEN**2) ** 0.5  # 5.0
        SCALE = 0.6
        corner = LEFT * 3.0 + DOWN * 1.2
        end_b = corner + RIGHT * B_LEN * SCALE
        end_a = corner + UP * A_LEN * SCALE

        title = Title("The Pythagorean Theorem", color=WHITE)

        triangle = Polygon(
            corner, end_b, end_a,
            color=BLUE, stroke_width=3, fill_opacity=0.2, fill_color=BLUE_E,
        )
        right_angle = RightAngle(
            Line(corner, end_a),
            Line(corner, end_b),
            length=0.3, color=YELLOW,
        )
        label_a = MathTex(r"a", color=TEAL).next_to(
            Line(corner, end_a), LEFT, buff=0.25
        )
        label_b = MathTex(r"b", color=GREEN).next_to(
            Line(corner, end_b), DOWN, buff=0.25
        )
        label_c = MathTex(r"c", color=GOLD).move_to(
            (end_a + end_b) / 2 + UR * 0.35
        )

        eq_initial = MathTex(
            r"a^2", r"+", r"b^2", r"=", r"c^2",
            substrings_to_isolate=[r"a^2", r"b^2", r"c^2"],
        ).shift(RIGHT * 3.2 + UP * 0.6)
        eq_initial.set_color_by_tex(r"a^2", TEAL)
        eq_initial.set_color_by_tex(r"b^2", GREEN)
        eq_initial.set_color_by_tex(r"c^2", GOLD)

        eq_solved = MathTex(
            r"c", r"=", r"\sqrt{", r"a^2", r"+", r"b^2", r"}",
            substrings_to_isolate=[r"c", r"a^2", r"b^2"],
        ).shift(RIGHT * 3.2 + UP * 0.6)
        eq_solved.set_color_by_tex(r"c", GOLD)
        eq_solved.set_color_by_tex(r"a^2", TEAL)
        eq_solved.set_color_by_tex(r"b^2", GREEN)

        # Numeric check shares A_LEN/B_LEN/C_LEN with the triangle above.
        check_eq = MathTex(
            r"3^2 + 4^2 = 5^2", color=GREY_A
        ).shift(RIGHT * 3.2 + DOWN * 0.7)
        trace = ValueTracker(0.0)
        travel_num = DecimalNumber(
            0.0, num_decimal_places=1, mob_class=Text, color=GOLD, font_size=30,
        )
        travel_num.add_updater(lambda mob: mob.set_value(trace.get_value() * C_LEN))
        measure_row = VGroup(
            MathTex(r"c =", color=GOLD), travel_num
        ).arrange(RIGHT, buff=0.15).next_to(check_eq, DOWN, buff=0.2)
        hyp_dot = Dot(point=end_b, color=GOLD, radius=0.08)
        hyp_dot.add_updater(
            lambda mob: mob.move_to(end_b * (1.0 - trace.get_value()) + end_a * trace.get_value())
        )
        vary_prompt = Text(
            "Try 5-12-13: predict c before computing.", font_size=22, color=TEAL_C
        ).to_edge(DOWN, buff=0.35)

        # c1_setup: establish the right triangle and its labels.
        player.play(
            "c1_setup",
            Write(title),
            Create(triangle),
            Create(right_angle),
            Write(label_a),
            Write(label_b),
            Write(label_c),
            run_time=2.5,
        )
        # c2_state: state the algebraic relation once.
        player.play("c2_state", Write(eq_initial), run_time=1.5)
        # c3_solve: morph to the solved form; shared substrings carry over.
        player.play(
            "c3_solve",
            TransformMatchingTex(eq_initial, eq_solved, transform_mismatches=True),
            run_time=2.0,
        )
        # c4_check: instantiate 3-4-5; the dot and the readout share `trace`,
        # so the measured length and the geometry cannot disagree.
        self.add(hyp_dot)
        player.play(
            "c4_check",
            FadeIn(check_eq),
            FadeIn(measure_row),
            FadeIn(vary_prompt),
            trace.animate.set_value(1.0),
            run_time=3.0,
        )
        hyp_dot.clear_updaters()
        travel_num.clear_updaters()
        player.finish(
            os.environ.get(
                "GNOS_TIMELINE_PREFIX", str(ROOT / "output/math-proof/lesson")
            )
        )
