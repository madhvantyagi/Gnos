"""
illustrations.py — Reusable Cinematic Components for Manim Visualizations

Optional, opt-in visual assets. A scene with none of these is the baseline:
construct a helper only when its signal carries the teaching claim, keep at
most one effect per cue, and clean it up in the same section (stop flows,
fade out halos/grids, clear updaters, restore the camera).

Performance rule: never rebuild a Glow, plot, or typeset label inside a
per-frame updater. Drive motion with a ValueTracker, show numbers with
DecimalNumber, move prebuilt dots, and take discrete steps with update_to().

Full-potential rule: use Manim's own primitives (ValueTracker, TracedPath,
LaggedStart, Indicate/Circumscribe, TransformMatchingTex, smooth/linear
easing, MovingCamera frame, ThreeD axes) through these helpers so the
timeline stays cue-timed. Helpers return animations; the caller plays them
inside player.play(cue_id, ...) and cleans up in the same cue.

Provides:
- PALETTE: single-source cinema palette (matches 09 reference).
- AtmosphericGrid / maybe_grid: subtle coordinate underlay (opt-in).
- Glow / optional_glow: layered halo for an active formula or node.
- GaussianDistribution: bell curve with a mean marker and shaded regions.
- ParticleStream: dots flowing along a segment or Bezier path (one updater).
- NeuralLayerVisualizer: glowing node column with synapses and a pulse.
- push_in / pull_back: MovingCameraScene focus helpers with restore.
- clear_cinematic_updaters: explicit updater cleanup for section ends.
"""

from manim import *
import numpy as np

__all__ = [
    "PALETTE",
    "AtmosphericGrid",
    "maybe_grid",
    "Glow",
    "optional_glow",
    "GaussianDistribution",
    "ParticleStream",
    "NeuralLayerVisualizer",
    "push_in",
    "pull_back",
    "clear_cinematic_updaters",
]

#: Single-source cinema palette (mirrors 09 reference §2). Templates use
#: Manim named colors by default; reach for these hexes only when the dark
#: underlay needs guaranteed contrast. All helpers default to these values.
PALETTE = {
    "obsidian": "#0B0E14",
    "cyan": "#00F0FF",
    "violet": "#B537F2",
    "gold": "#FFD166",
    "emerald": "#06D6A0",
    "coral": "#EF476F",
}

#: Upper bound for halo layers and stream particles; beyond this the extra
#: draw cost buys no teaching signal at playback size.
_MAX_LAYERS = 8
_MAX_PARTICLES = 64


class AtmosphericGrid(VGroup):
    """
    Subtle coordinate-grid underlay.

    Does not set the scene background; set that explicitly when the grid
    improves contrast. Add it first so lesson content draws on top, and
    FadeOut/remove it when its section ends. Prefer maybe_grid() at call
    sites so the effect stays visibly opt-in.

    Defaults are clamped to the 16:9 frame (x ±7.11, y ±4.0) so no lines
    draw off-frame. For 9:16 / 1:1 storyboards pass narrower ranges or
    aspect="vertical"/"square".
    """
    def __init__(self, x_range=(-7.11, 7.11, 1.0), y_range=(-4.0, 4.0, 1.0),
                 show_axes=False, base_opacity=0.4, aspect="16:9", **kwargs):
        super().__init__(**kwargs)
        # Aspect hint: vertical/square storyboards need narrower grids.
        if aspect in ("9:16", "vertical") and x_range == (-7.11, 7.11, 1.0):
            x_range = (-4.0, 4.0, 1.0)
        if aspect in ("1:1", "square") and x_range == (-7.11, 7.11, 1.0):
            x_range = (-4.0, 4.0, 1.0)
        self.aspect = aspect
        self.show_axes = show_axes
        self.grid = NumberPlane(
            x_range=x_range,
            y_range=y_range,
            background_line_style={
                "stroke_color": "#1A2030",
                "stroke_width": 1.0,
                "stroke_opacity": base_opacity,
            },
            faded_line_style={
                "stroke_color": "#121622",
                "stroke_width": 0.5,
                "stroke_opacity": base_opacity * 0.5,
            },
            axis_config={
                "stroke_color": "#28344D",
                "stroke_width": 1.5,
                "stroke_opacity": 0.6,
                "include_ticks": show_axes,
                "include_numbers": False,
            },
        )
        # Subtle underlay should not add axis noise unless asked.
        if not show_axes:
            try:
                self.grid.axes.set_stroke(opacity=0.0)
            except Exception:
                pass
        self.add(self.grid)


def maybe_grid(enabled=False, **kwargs):
    """Return an AtmosphericGrid when enabled, else an empty VGroup.

    Keeps call sites honest: ``self.add(maybe_grid(enabled=False))`` adds
    no clutter by default and previews depth with ``enabled=True``.
    """
    if not enabled:
        return VGroup()
    return AtmosphericGrid(**kwargs)


class Glow(VGroup):
    """
    Concentric layered halo around any Mobject.

    Built once up front; do not reconstruct it inside an updater. To end
    the emphasis, ``self.play(FadeOut(glow))`` in the same section.
    For text groups prefer ``Write``/``FadeIn`` over ``Create`` on the glow:
    ``Create`` strokes every halo layer and looks heavy at playback size.
    Halo layers sit behind the source (source added last); keep z_index
    default unless the scene explicitly layers foreground labels.
    """
    def __init__(self, mobject: Mobject, color: str = "#00F0FF", num_layers: int = 5,
                 max_opacity: float = 0.25, include_source: bool = True, **kwargs):
        super().__init__(**kwargs)
        if not isinstance(num_layers, int) or not 1 <= num_layers <= _MAX_LAYERS:
            raise ValueError(f"num_layers must be an integer in 1..{_MAX_LAYERS}")
        if max_opacity <= 0:
            raise ValueError("max_opacity must be positive")
        self.source = mobject
        for i in range(1, num_layers + 1):
            scale_factor = 1.0 + (i * 0.08)
            layer_opacity = max_opacity / (i ** 1.3)
            layer = mobject.copy()
            base_width = layer.get_stroke_width() or 0.0
            # Texts and fills can report a zero stroke width; floor the halo
            # so the emphasis stays visible at playback size.
            layer.set_stroke(color=color, width=max(base_width * scale_factor, 3.0),
                             opacity=layer_opacity)
            if hasattr(layer, "set_fill"):
                layer.set_fill(color=color, opacity=layer_opacity * 0.5)
            self.add(layer)
        if include_source:
            self.add(mobject)


def optional_glow(mobject: Mobject, enabled=False, **kwargs):
    """Return a Glow around mobject when enabled, else mobject untouched.

    Lets a scene keep ``Create(optional_glow(formula))`` while rendering
    the plain formula by default.
    """
    if not enabled:
        return mobject
    return Glow(mobject, **kwargs)


class GaussianDistribution(VGroup):
    """
    Probability density bell curve with a mean marker.

    Move between discrete lesson states with update_to(); do not rebuild
    the curve every frame. Shaded regions are one-shot areas under the
    current curve.
    """
    def __init__(
        self,
        axes: Axes,
        mean: float = 0.0,
        std: float = 1.0,
        color: str = "#00F0FF",
        x_range: tuple = (-3.5, 3.5),
        **kwargs
    ):
        super().__init__(**kwargs)
        if std <= 0:
            raise ValueError("std must be positive")
        if len(x_range) != 2 or x_range[0] >= x_range[1]:
            raise ValueError("x_range must be an increasing (min, max) pair")
        self.axes = axes
        self.mean = float(mean)
        self.std = float(std)
        self.curve_color = color
        self.x_range = x_range

        self.curve = axes.plot(self.pdf, x_range=list(x_range), color=color, stroke_width=3.5)
        self.mean_line = self._mean_line()
        self.add(self.curve, self.mean_line)

    def pdf(self, x):
        """Density at x; accepts scalars and numpy arrays (for axes.plot)."""
        z = (np.asarray(x, dtype=float) - self.mean) / self.std
        return (1.0 / (self.std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * z ** 2)

    def _mean_line(self):
        top = self.axes.c2p(self.mean, float(self.pdf(self.mean)))
        bottom = self.axes.c2p(self.mean, 0)
        return DashedLine(bottom, top, color=YELLOW, stroke_width=2.5)

    def update_to(self, mean=None, std=None):
        """Step to a new discrete state, reusing this group (no updater)."""
        if mean is not None:
            self.mean = float(mean)
        if std is not None:
            if std <= 0:
                raise ValueError("std must be positive")
            self.std = float(std)
        curve = self.axes.plot(self.pdf, x_range=list(self.x_range),
                               color=self.curve_color, stroke_width=3.5)
        mean_line = self._mean_line()
        self.remove(self.curve, self.mean_line)
        self.curve, self.mean_line = curve, mean_line
        self.add(curve, mean_line)
        return self

    def get_shaded_region(self, x_min: float, x_max: float, color: str = "#06D6A0", opacity: float = 0.4):
        """Returns a shaded area under the current curve between x_min and x_max."""
        return self.axes.get_area(self.curve, x_range=[x_min, x_max], color=color, opacity=opacity)


class ParticleStream(VGroup):
    """
    Glowing particles travelling along a straight segment.

    Run motion with start_flow()/stop_flow(): a single updater moves the
    prebuilt dots and wraps them around, so nothing is allocated per frame
    and nothing drifts off-path. create_flow_animation() is a one-shot
    nudge kept for backward compatibility. Always stop_flow() (or
    clear_cinematic_updaters) when the section ends.
    """
    def __init__(
        self,
        start_point: np.ndarray,
        end_point: np.ndarray,
        num_particles: int = 8,
        color: str = "#00F0FF",
        particle_radius: float = 0.07,
        **kwargs
    ):
        super().__init__(**kwargs)
        if not isinstance(num_particles, int) or not 1 <= num_particles <= _MAX_PARTICLES:
            raise ValueError(f"num_particles must be an integer in 1..{_MAX_PARTICLES}")
        self.start = np.array(start_point, dtype=float)
        self.end = np.array(end_point, dtype=float)
        if self.start.shape != self.end.shape:
            raise ValueError("start_point and end_point must have matching shapes")
        self.num_particles = num_particles
        self.particle_color = color

        # Base connecting trace line
        self.line = Line(self.start, self.end, stroke_color=color, stroke_opacity=0.25, stroke_width=1.5)
        self.add(self.line)

        self._alphas = [i / max(1, num_particles - 1) if num_particles > 1 else 0.0
                        for i in range(num_particles)]
        self.particles = VGroup()
        for alpha in self._alphas:
            pos = self.start + alpha * (self.end - self.start)
            dot = Dot(point=pos, radius=particle_radius, color=color)
            dot.set_stroke(color=WHITE, width=1.0, opacity=0.8)
            self.particles.add(dot)
        self.add(self.particles)

    def start_flow(self, rate: float = 0.2, direction: int = 1):
        """Attach one looping updater: rate is path-fractions per second."""
        if rate <= 0:
            raise ValueError("rate must be positive")
        if direction not in (1, -1):
            raise ValueError("direction must be 1 or -1")
        vec = self.end - self.start
        alphas = list(self._alphas)
        state = {"phase": 0.0}
        self.stop_flow()

        def _advance(mob, dt):
            state["phase"] = (state["phase"] + direction * rate * dt) % 1.0
            for dot, alpha in zip(mob, alphas):
                t = (alpha + state["phase"]) % 1.0
                dot.move_to(self.start + t * vec)

        self.particles.add_updater(_advance)
        return self

    def stop_flow(self):
        """Detach the flow updater; call when the section ends."""
        self.particles.clear_updaters()
        return self

    def create_flow_animation(self, run_time: float = 2.0):
        """One-shot nudge of the prebuilt dots (legacy helper)."""
        anims = []
        vec = self.end - self.start
        for p in self.particles:
            anims.append(p.animate.shift(vec * 0.3))
        return AnimationGroup(*anims, run_time=run_time, rate_func=linear)


class NeuralLayerVisualizer(VGroup):
    """
    A stylized neural network layer of connected glowing nodes.

    Position each layer before calling connect_to(): synapses snapshot the
    current node centers. Pulse with pulse() instead of rebuilding nodes.
    """
    def __init__(self, num_nodes: int = 4, color: str = "#B537F2", height: float = 3.5, x_pos: float = 0.0, **kwargs):
        super().__init__(**kwargs)
        if not isinstance(num_nodes, int) or num_nodes < 1:
            raise ValueError("num_nodes must be a positive integer")
        self.node_color = color
        self.nodes = VGroup()
        y_positions = np.linspace(-height / 2, height / 2, num_nodes)
        for y in y_positions:
            outer = Circle(radius=0.25, color=color, stroke_width=2.5, fill_opacity=0.3, fill_color=color)
            inner = Dot(point=[x_pos, y, 0], radius=0.08, color=WHITE)
            node = VGroup(outer, inner).move_to([x_pos, y, 0])
            self.nodes.add(node)
        self.add(self.nodes)

    def connect_to(self, target_layer: 'NeuralLayerVisualizer', color: str = "#2B3A55") -> VGroup:
        """Draw static synaptic lines between two positioned layers."""
        if not isinstance(target_layer, NeuralLayerVisualizer):
            raise TypeError("connect_to expects another NeuralLayerVisualizer")
        synapses = VGroup()
        for src in self.nodes:
            for dst in target_layer.nodes:
                syn = Line(src.get_center(), dst.get_center(), stroke_color=color, stroke_width=1.0, stroke_opacity=0.35)
                synapses.add(syn)
        return synapses

    def pulse(self, color=None, scale_factor: float = 1.12, run_time: float = 0.6):
        """Return a staggered emphasis over the existing nodes."""
        return AnimationGroup(
            *[Indicate(node, color=color or self.node_color, scale_factor=scale_factor)
              for node in self.nodes],
            lag_ratio=0.15,
            run_time=run_time,
        )


def push_in(scene, target: Mobject, margin: float = 2.5):
    """Save the wide shot and return a focus animation for target.

    Play the returned animation inside its cue, then pair with pull_back().
    Raises TypeError on a plain Scene (stable camera is the default there).
    """
    frame = getattr(getattr(scene, "camera", None), "frame", None)
    if frame is None:
        raise TypeError("push_in needs a MovingCameraScene; plain scenes keep a stable camera")
    if margin <= 1.0:
        raise ValueError("margin must exceed 1.0 so the target keeps context")
    frame.save_state()
    return frame.animate.set(width=target.width * margin).move_to(target)


def pull_back(scene):
    """Return the wide-shot restore saved by push_in(); play it in its cue."""
    frame = getattr(getattr(scene, "camera", None), "frame", None)
    if frame is None:
        raise TypeError("pull_back needs a MovingCameraScene; plain scenes keep a stable camera")
    return Restore(frame)


def clear_cinematic_updaters(*mobjects):
    """Detach updaters from section-local mobjects; None entries are skipped."""
    for mob in mobjects:
        if mob is None:
            continue
        if not hasattr(mob, "clear_updaters"):
            raise TypeError(f"Expected a Mobject with clear_updaters, got {type(mob).__name__}")
        mob.clear_updaters()
