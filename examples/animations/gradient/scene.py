"""Why subtract the slope? — GNOS exemplar for cue-driven Manim scenes.

Concept: the sign of f'(x) gives a local descent direction, but the step
size controls the update. Stable camera throughout (movement would add no
structure here); one compared quantity stays visible; every displayed
number is derived from the same tracker constants as the geometry.

Storyboard: examples/animations/gradient/storyboard.json
(Class GradientStep, cues start/slope/step/limit.)

Silent preview (honest choreography check; authored durations, no speech):
    python3 skills/manim-voice-animation/scripts/voice_synthesizer.py \
        --storyboard examples/animations/gradient/storyboard.json \
        --out output/gradient/audio --silent
    GNOS_MANIFEST=output/gradient/audio/timing_manifest.json \
    python3 skills/manim-voice-animation/scripts/render_pipeline.py \
        render examples/animations/gradient/scene.py GradientStep \
        -q l -o output/gradient/preview.mp4

Voiced render: rerun voice_synthesizer without --silent (or --audio-dir
with SceneID_cue-id.mp3 clips), then render with GNOS_MANIFEST pointing
at the measured manifest. CuePlayer attaches each clip at its cue start.

Review checklist (at playback size): first frame builds title, axes,
curve, and the x=2 point with loss 4; transitions keep labels in frame;
the update text matches the tracker math (2 - 0.2*4 = 1.2, loss 1.44);
the ending holds the result plus the eta=1.2 prompt; no updater stays
attached after the step cue. Set GNOS_CINEMATIC=1 to preview the optional
grid underlay; it is off by default so the concept carries the frame.
"""
from pathlib import Path
import os
import sys
from manim import *

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "skills" / "manim-voice-animation" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
COMPONENTS = ROOT / "skills" / "manim-voice-animation" / "components"
if str(COMPONENTS) not in sys.path:
    sys.path.insert(0, str(COMPONENTS))
from cue_player import CuePlayer

try:
    from illustrations import maybe_grid
except ImportError:  # Cinematic underlay stays optional; the lesson never needs it.
    maybe_grid = None

# One state drives geometry, labels, and narration numbers together.
F = lambda x: x * x
DFDX = lambda x: 2 * x
X0 = 2.0
ETA = 0.2
X1 = X0 - ETA * DFDX(X0)  # 1.2; loss falls from 4 to 1.44.
LARGE_ETA = 1.2  # Posed, not taken: x -> 2 - 1.2*4 = -2.8 overshoots.


class GradientStep(Scene):
    def construct(self):
        self.camera.background_color = "#101c27"
        manifest = Path(os.environ.get(
            "GNOS_MANIFEST", ROOT / "output/gradient/audio/timing_manifest.json"))
        player = CuePlayer(self, manifest, "GradientStep")

        # Opt-in depth only; the default frame is a clean diagram.
        if os.environ.get("GNOS_CINEMATIC") and maybe_grid is not None:
            self.add(maybe_grid(enabled=True))

        title = Text("Why subtract the slope?", font_size=32).to_edge(UP, buff=0.35)
        axes = Axes(
            x_range=[-1, 3, 1], y_range=[0, 9, 1], x_length=7, y_length=4.5,
            tips=False, axis_config={"color": GREY_B},
        ).shift(LEFT * 1.8 + DOWN * 0.25)
        curve = axes.plot(F, x_range=[-1, 3], color=TEAL_C)
        label = Text("f(x) = x^2", font_size=24, color=TEAL_C).next_to(axes, UP, buff=0.1)

        # Tracker-backed dot + DecimalNumber: numbers follow the same state
        # as the geometry without rebuilding typeset labels per frame.
        tracker = ValueTracker(X0)

        def follow_curve(mob):
            mob.move_to(axes.c2p(tracker.get_value(), F(tracker.get_value())))

        def follow_loss(mob):
            mob.set_value(F(tracker.get_value()))

        dot = Dot(axes.c2p(X0, F(X0)), color=YELLOW)
        dot.add_updater(follow_curve)
        loss = DecimalNumber(F(X0), mob_class=Text, num_decimal_places=2,
                             font_size=32, color=YELLOW)
        loss.add_updater(follow_loss)
        loss_block = VGroup(
            Text("loss", font_size=24), loss,
        ).arrange(DOWN, buff=0.15).move_to(RIGHT * 4 + UP * 1.3)

        # Tangent derived from the derivative, not hardcoded endpoints.
        half_dx = 0.7
        tangent = Line(
            axes.c2p(X0 - half_dx, F(X0) - DFDX(X0) * half_dx),
            axes.c2p(X0 + half_dx, F(X0) + DFDX(X0) * half_dx),
            color=ORANGE,
        )
        slope = Text(f"initial slope = {DFDX(X0):g}", font_size=20,
                     color=ORANGE).move_to(RIGHT * 4 + DOWN * 0.3)
        update = Text(f"{X0:g} - {ETA:g} x {DFDX(X0):g} = {X1:g}",
                      font_size=25).to_edge(DOWN, buff=0.35)
        prompt = Text(f"What if eta = {LARGE_ETA:g}?", font_size=24,
                      color=TEAL_C).move_to(RIGHT * 4 + DOWN * 1.3)

        # One play per cue, each run_time inside its cue duration; CuePlayer
        # fills the remainder with a hold so narration lands on a still frame.
        player.play("start", Write(title), Create(axes), Create(curve),
                    FadeIn(dot), FadeIn(label), FadeIn(loss_block), run_time=3)
        player.play("slope", Create(tangent), FadeIn(slope), run_time=2.5)
        player.play("step", tracker.animate.set_value(X1), FadeIn(update),
                    FadeOut(tangent), run_time=2)
        # Section over: detach updaters before the reflection cue so no
        # updater fires past its section.
        dot.clear_updaters()
        loss.clear_updaters()
        player.play("limit", FadeIn(prompt), run_time=1)
        # No trailing wait: finish() already holds each cue to its duration
        # and rejects unplayed cues.
        player.finish(os.environ.get(
            "GNOS_TIMELINE_PREFIX", str(ROOT / "output/gradient/lesson")))
