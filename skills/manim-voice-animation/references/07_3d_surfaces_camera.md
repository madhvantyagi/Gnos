# 3D Visualizations, Surfaces & Camera Control

Rendering in 3D requires `ThreeDScene`, explicit polar camera angles (`phi`,
`theta`), surface definitions, and fixed-frame 2D overlays. Use 3D only when a
third dimension changes the learner's inference; otherwise a 2D projection is
easier to read. State the parameter domain, scale, and any occlusion the camera
introduces.

---

## 1. 3D Camera Angles & Ambient Rotation

```python
from manim import *

class ThreeDExploration(ThreeDScene):
    def construct(self):
        # Setup 3D coordinate axes
        axes = ThreeDAxes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            z_range=[-2, 2, 1],
            x_length=6,
            y_length=6,
            z_length=4
        )
        self.add(axes)

        # Initial camera view: phi = vertical tilt (75 deg), theta = azimuth (-45 deg)
        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)

        # Optional camera orbit: keep it only if depth or a changing view is the
        # concept being taught.
        self.begin_ambient_camera_rotation(rate=0.2)  # radians per second
        self.wait(3.0)
        self.stop_ambient_camera_rotation()

        # Dynamic camera angle shift
        self.move_camera(phi=45 * DEGREES, theta=30 * DEGREES, run_time=2.0)
```

---

## 2. 3D Parametric Surfaces (`Surface`)

```python
class ParametricSurfaceScene(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)
        self.add(axes)

        # Hyperbolic Paraboloid (Saddle Surface): z = x^2 - y^2
        surface = Surface(
            lambda u, v: axes.c2p(u, v, 0.5 * (u**2 - v**2)),
            u_range=[-2, 2],
            v_range=[-2, 2],
            resolution=(24, 24),
            should_make_jagged=False
        )
        surface.set_style(fill_opacity=0.7, stroke_color=GREY_C, stroke_width=0.5)
        surface.set_fill_by_value(axes=axes, colors=[BLUE, TEAL, YELLOW, RED], axis=2)

        self.play(Create(surface), run_time=3.0)
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(2.5)
```

Review the same surface from the intended playback view and verify that labels
remain readable. Stop ambient rotation and clear any object updaters before a
new explanatory state; camera motion should not be used to hide a scale or
sign error.

---

## 4. Teaching checklist: camera restraint, bounds, overlays, cleanup, cues

- Move the camera only to reveal structure: one `set_camera_orientation` to
  establish the view, then at most one motivated `move_camera` (for example,
  showing the saddle curving both ways). Prefer a still camera when a 2D
  projection already carries the inference; never orbit through the caption.
- Keep bounds and aspect safe: declare the parameter domain and scale, keep the
  full surface inside the `ThreeDAxes` ranges at 16:9, and re-check the opening
  and closing frames at playback size so axes and labels stay in frame.
- Pin 2D text with `add_fixed_in_frame_mobjects` so titles, legends, and the
  compared quantity do not rotate with the scene. Keep overlays short while
  narration carries the explanation.
- Clean up before the next state: call `stop_ambient_camera_rotation()` and
  `clear_updaters()` before presenting a new explanatory state or the changed
  case. Map each template block to one narration cue and keep every camera
  move inside its cue duration.

---

## 3. Fixed 2D Overlays in 3D Scenes (`add_fixed_in_frame_mobjects`)

Titles, legends, and math labels should not rotate with the 3D camera. Pin them to the viewport using `add_fixed_in_frame_mobjects`:

```python
class FixedOverlayScene(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES)
        self.add(axes)

        # 2D Screen Header (remains stationary regardless of 3D camera rotation)
        title = Title("3D Saddle Surface: $z = x^2 - y^2$", color=WHITE)
        self.add_fixed_in_frame_mobjects(title)

        self.begin_ambient_camera_rotation(rate=0.3)
        self.wait(3.0)
```
