"""
illustrations.py — Reusable Cinematic Components for Manim Visualizations

Provides optional, reusable visual assets:
- Glow: Multi-layered bloom halos for emphasized formulas and active nodes.
- GaussianDistribution: Continuous probability density bell curves with shaded advantage regions.
- ParticleStream: Flowing glowing particles representing token streams, data, or gradients.
- NeuralLayerVisualizer: Connected neural network layers with signal pulses.
- AtmosphericGrid: Deep obsidian space with subtle coordinate depth underlay.
"""

from manim import *
import numpy as np


class AtmosphericGrid(VGroup):
    """
    Creates a subtle coordinate-grid underlay.

    This component does not set the scene background; set that explicitly when
    the grid improves contrast for the lesson.
    """
    def __init__(self, x_range=(-7.5, 7.5, 1.0), y_range=(-4.5, 4.5, 1.0), **kwargs):
        super().__init__(**kwargs)
        grid = NumberPlane(
            x_range=x_range,
            y_range=y_range,
            background_line_style={
                "stroke_color": "#1A2030",
                "stroke_width": 1.0,
                "stroke_opacity": 0.4
            },
            faded_line_style={
                "stroke_color": "#121622",
                "stroke_width": 0.5,
                "stroke_opacity": 0.2
            },
            axis_config={
                "stroke_color": "#28344D",
                "stroke_width": 1.5,
                "stroke_opacity": 0.6
            }
        )
        self.add(grid)


class Glow(VGroup):
    """
    Concentric layered blooming glow effect around any Mobject or symbol.
    """
    def __init__(self, mobject: Mobject, color: str = "#00F0FF", num_layers: int = 5, max_opacity: float = 0.25, **kwargs):
        super().__init__(**kwargs)
        for i in range(1, num_layers + 1):
            scale_factor = 1.0 + (i * 0.08)
            layer_opacity = max_opacity / (i ** 1.3)
            layer = mobject.copy()
            layer.set_stroke(color=color, width=layer.get_stroke_width() * scale_factor, opacity=layer_opacity)
            if hasattr(layer, "set_fill"):
                layer.set_fill(color=color, opacity=layer_opacity * 0.5)
            self.add(layer)
        self.add(mobject)


class GaussianDistribution(VGroup):
    """
    Dynamic continuous probability distribution bell curve with mean marker
    and shaded tails (positive reinforcement / negative penalty regions).
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
        self.mean = mean
        self.std = std
        self.curve_color = color
        self.x_range = x_range

        # Probability density function: 1 / (std * sqrt(2*pi)) * exp(-0.5 * ((x - mean)/std)^2)
        pdf = lambda x: (1.0 / (self.std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * (((x - self.mean) / self.std) ** 2))
        self.curve = axes.plot(pdf, x_range=list(x_range), color=color, stroke_width=3.5)

        # Mean vertical marker
        mean_pt_top = axes.c2p(self.mean, pdf(self.mean))
        mean_pt_bot = axes.c2p(self.mean, 0)
        self.mean_line = DashedLine(mean_pt_bot, mean_pt_top, color=YELLOW, stroke_width=2.5)

        self.add(self.curve, self.mean_line)

    def get_shaded_region(self, x_min: float, x_max: float, color: str = "#06D6A0", opacity: float = 0.4):
        """Returns a shaded area under the curve between x_min and x_max."""
        pdf = lambda x: (1.0 / (self.std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * (((x - self.mean) / self.std) ** 2))
        return self.axes.get_area(self.curve, x_range=[x_min, x_max], color=color, opacity=opacity)


class ParticleStream(VGroup):
    """
    Creates an animated stream of glowing particles travelling along a path
    (representing token generations, data streams, or neural signals).
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
        if num_particles < 1:
            raise ValueError("num_particles must be positive")
        self.start = np.array(start_point)
        self.end = np.array(end_point)
        self.num_particles = num_particles

        # Base connecting trace line
        self.line = Line(self.start, self.end, stroke_color=color, stroke_opacity=0.25, stroke_width=1.5)
        self.add(self.line)

        self.particles = VGroup()
        for i in range(num_particles):
            alpha = i / max(1, num_particles - 1)
            pos = self.start + alpha * (self.end - self.start)
            dot = Dot(point=pos, radius=particle_radius, color=color)
            dot.set_stroke(color=WHITE, width=1.0, opacity=0.8)
            self.particles.add(dot)
        self.add(self.particles)

    def create_flow_animation(self, run_time: float = 2.0):
        """Returns an animation group of particles streaming forward."""
        anims = []
        vec = self.end - self.start
        for p in self.particles:
            anims.append(p.animate.shift(vec * 0.3))
        return AnimationGroup(*anims, run_time=run_time, rate_func=linear)


class NeuralLayerVisualizer(VGroup):
    """
    A stylized neural network layer of connected glowing nodes with synaptic edges.
    """
    def __init__(self, num_nodes: int = 4, color: str = "#B537F2", height: float = 3.5, x_pos: float = 0.0, **kwargs):
        super().__init__(**kwargs)
        self.nodes = VGroup()
        y_positions = np.linspace(-height / 2, height / 2, num_nodes)
        for y in y_positions:
            outer = Circle(radius=0.25, color=color, stroke_width=2.5, fill_opacity=0.3, fill_color=color)
            inner = Dot(point=[x_pos, y, 0], radius=0.08, color=WHITE)
            node = VGroup(outer, inner).move_to([x_pos, y, 0])
            self.nodes.add(node)
        self.add(self.nodes)

    def connect_to(self, target_layer: 'NeuralLayerVisualizer', color: str = "#2B3A55") -> VGroup:
        """Draw static synaptic lines between two layers at their current positions."""
        synapses = VGroup()
        for src in self.nodes:
            for dst in target_layer.nodes:
                syn = Line(src.get_center(), dst.get_center(), stroke_color=color, stroke_width=1.0, stroke_opacity=0.35)
                synapses.add(syn)
        return synapses
