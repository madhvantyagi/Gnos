"""Linear algebra template: observe one basis transformation (shear).

Storyboard notes (replace with course values before use):
- concept ID: linalg.shear.basis-action (keep the course's notation/ID).
- prereq: vectors as arrows, matrix-times-vector convention (columns image the
  basis vectors), coordinates in the same basis while the matrix acts.
- hypotheses: A = [[1, 1.5], [0, 1]]; i_hat fixed, j_hat -> [1.5, 1]; det = 1.
- success check: learner predicts v' = [4, 2] for v = [1, 2] before the
  transform, then verifies one coordinate and the area invariant after.
- one clear change per cue: c1 shows grid/basis/matrix, c2 shows v with ghosts
  and asks for a prediction, c3 applies the shear, c4 checks the invariant.
- silent preview: give every cue an explicit ``duration``, then run
  ``voice_synthesizer.py --storyboard <storyboard.json> --out <out_dir> --silent``.
  Point GNOS_MANIFEST at the resulting ``timing_manifest.json``.
- aspect 16:9 bounds: frame x in [-7.11, 7.11], y in [-4.0, 4.0]. Plane
  (x_length 13, y_length 7) fills the background; header/readouts use
  to_corner/to_edge with a buff so labels stay in frame. v' = [4, 2] lands
  well inside the frame.
- camera: stable. No camera movement; the grid shear is the only structural
  change so the basis action stays comparable before/after.

Design note: this template subclasses Scene and drives the shear with a
ValueTracker instead of LinearTransformationScene.apply_matrix, because
apply_matrix plays outside the CuePlayer timeline boundary. The explicit
interpolation keeps every animation inside player.play, lets the DecimalNumbers
share the same tracker as the geometry, and keeps the matrix header fixed
(the foreground-pin equivalent: it is never transformed).
"""
from pathlib import Path
import os
import sys
from manim import *

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "skills/manim-voice-animation/scripts"))
from cue_player import CuePlayer


class LinearAlgebraScene(Scene):
    """Shear with shared tracker; readouts cannot drift from the figure.

    ``shear_t`` interpolates M(t) = [[1, 1.5 t], [0, 1]] from identity (t=0)
    to the shear (t=1). Grid-relative arrows, the target vector, the unit
    square, and the DecimalNumbers all read ``shear_t``, so the drawn basis
    action and the displayed coordinate/determinant agree. Labels follow with
    lightweight next_to updaters (no MathTex rebuild per frame).
    """

    def construct(self):
        manifest = Path(
            os.environ.get(
                "GNOS_MANIFEST",
                ROOT / "output/linear-algebra/audio/timing_manifest.json",
            )
        )
        player = CuePlayer(self, manifest, "LinearAlgebraScene")

        K = 1.5
        shear_t = ValueTracker(0.0)

        def apply_shear(vec):
            t = shear_t.get_value()
            x, y = float(vec[0]), float(vec[1])
            return [x + K * t * y, y, 0]

        plane = NumberPlane(
            x_range=[-7, 7, 1],
            y_range=[-4, 4, 1],
            x_length=13,
            y_length=7,
            background_line_style={"stroke_color": GREY_D, "stroke_width": 1},
        )

        title = Title("Linear Transformation: Horizontal Shear", color=WHITE)
        matrix_tex = MathTex(
            r"A = \begin{bmatrix} 1 & 1.5 \\ 0 & 1 \end{bmatrix}"
        ).to_corner(UL).shift(DOWN * 0.6)

        # Ghosts record the pre-image (leave_ghost_vectors equivalent).
        ghost_i = Vector([1, 0], color=GREY_D, stroke_width=2)
        ghost_j = Vector([0, 1], color=GREY_D, stroke_width=2)
        ghost_v = Vector([1, 2], color=GREY_D, stroke_width=2)

        i_arrow = always_redraw(lambda: Vector(apply_shear([1, 0]), color=GREEN))
        j_arrow = always_redraw(lambda: Vector(apply_shear([0, 1]), color=TEAL))
        target = always_redraw(lambda: Vector(apply_shear([1, 2]), color=PURPLE))
        unit_square = always_redraw(
            lambda: Polygon(
                *[plane.c2p(*apply_shear([x, y])[:2]) for x, y in [(0, 0), (1, 0), (1, 1), (0, 1)]],
                color=BLUE, stroke_width=2, fill_opacity=0.35, fill_color=BLUE,
            )
        )

        i_label = MathTex(r"\hat{\imath}", color=GREEN)
        i_label.add_updater(lambda mob: mob.next_to(i_arrow.get_end(), DR, buff=0.15))
        j_label = MathTex(r"\hat{\jmath}", color=TEAL)
        j_label.add_updater(lambda mob: mob.next_to(j_arrow.get_end(), UL, buff=0.15))
        v_label = MathTex(r"\vec{v}", color=PURPLE)
        v_label.add_updater(lambda mob: mob.next_to(target.get_end(), UR, buff=0.15))

        # Displayed values share shear_t with the geometry above.
        x_num = DecimalNumber(1.0, num_decimal_places=1, mob_class=Text, color=PURPLE, font_size=28)
        x_num.add_updater(lambda mob: mob.set_value(1.0 + K * shear_t.get_value() * 2.0))
        coords_row = VGroup(
            MathTex(r"x' =", color=PURPLE), x_num
        ).arrange(RIGHT, buff=0.12).to_corner(UR).shift(DOWN * 0.7)
        det_num = DecimalNumber(1.0, num_decimal_places=2, mob_class=Text, color=BLUE, font_size=28)
        det_num.add_updater(
            lambda mob: mob.set_value(1.0 * 1.0 - K * shear_t.get_value() * 0.0)
        )
        det_row = VGroup(
            MathTex(r"\det(A) =", color=BLUE), det_num
        ).arrange(RIGHT, buff=0.12).next_to(coords_row, DOWN, buff=0.2)
        predict_prompt = Text(
            "Predict: where does v land? Where does j_hat go?",
            font_size=22, color=TEAL_C,
        ).to_edge(DOWN, buff=0.35)

        # c1_setup: grid, basis, and the matrix that will act.
        player.play(
            "c1_setup",
            Create(plane),
            Create(i_arrow),
            Create(j_arrow),
            FadeIn(title),
            FadeIn(matrix_tex),
            run_time=2.0,
        )
        # c2_predict: show v with ghosts and the area patch; ask first.
        player.play(
            "c2_predict",
            FadeIn(ghost_i),
            FadeIn(ghost_j),
            FadeIn(ghost_v),
            Create(target),
            Create(unit_square),
            FadeIn(v_label),
            FadeIn(i_label),
            FadeIn(j_label),
            FadeIn(coords_row),
            FadeIn(det_row),
            FadeIn(predict_prompt),
            run_time=2.0,
        )
        # c3_transform: the one basis change; arrows, square, and numbers move
        # together because they read the same tracker.
        player.play("c3_transform", shear_t.animate.set_value(1.0), run_time=3.0)
        # c4_verify: i_hat never moved and det stayed 1; pose the transfer check.
        player.play("c4_verify", Indicate(i_arrow, color=GREEN), run_time=1.5)

        for mob in (i_label, j_label, v_label, x_num, det_num):
            mob.clear_updaters()
        i_arrow.clear_updaters()
        j_arrow.clear_updaters()
        target.clear_updaters()
        unit_square.clear_updaters()
        player.finish(
            os.environ.get(
                "GNOS_TIMELINE_PREFIX", str(ROOT / "output/linear-algebra/lesson")
            )
        )
