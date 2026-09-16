# Cinematic Depth, Lighting & Visual Metaphors

Use visual depth only when it makes the learner's target relationship easier to
follow. The components in this reference are optional recipes, not a house
style or a quality requirement. A clear diagram with no atmosphere is a valid
teaching artifact.

---

## 1. Choose the representation

Do not add decorative boxes or paragraphs when a symbol, diagram, or state
transition carries the claim. Conversely, use a compact label or table when it
is the most direct way to name an object. Let the subject reference, teacher,
and learner target decide the representation.

| Concept Type | Bad (Slide Syndrome) | Good (Cinematic Metaphor) |
| :--- | :--- | :--- |
| **Probability / Sampling** | A rectangle with text "Output Probability = 0.8" | A continuous Gaussian bell curve with dynamic shifting mean and shaded integral regions. |
| **Token Generation / Data Flow** | An arrow pointing between two text boxes | A glowing stream of particle dots (`ParticleStream`) moving along curved Bezier trajectories. |
| **Neural Network / Model** | A box labeled "Actor Model (π_θ)" | Connected layers of glowing synaptic nodes (`NeuralLayerVisualizer`) that pulse on forward passes. |
| **Optimization / Gradient** | Text showing "Loss = 0.05" | A 3D saddle or paraboloid surface with a ball rolling down the gradient trajectory. |
| **Vector Space / Transform** | A list of numbers representing coordinates | A deformed coordinate grid (`NumberPlane` / `LinearTransformationScene`) with rotating basis vectors. |

---

## 2. Atmospheric Depth & Canvas Lighting

If a dark underlay improves contrast, create depth using:

1. **Atmospheric Coordinate Underlay**:
   Use `AtmosphericGrid()` from `components.illustrations` as a grid underlay.
   It does not set the scene background by itself; choose the background in the
   scene and verify contrast at playback size.
2. **Neon Bloom / Glowing Halos**:
   Highlight active formulas or nodes using concentric layered bloom (`Glow`):
   ```python
   from components.illustrations import Glow
   formula = Text("A_i = (r_i - μ) / σ", font_size=28, color="#00F0FF")
   glowing_formula = Glow(formula, color="#00F0FF", num_layers=4)
   self.play(Create(glowing_formula), run_time=1.5)
   ```
3. **Curated Cinema Palette**:
   - **Obsidian Space**: `#0B0E14` (Canvas)
   - **Neon Cyan**: `#00F0FF` (Primary variables & prompt inputs)
   - **Electric Violet**: `#B537F2` (Neural layers & transformers)
   - **Warm Gold**: `#FFD166` (Mathematical constants & baselines)
   - **Emerald Green**: `#06D6A0` (Positive rewards, success, convergence)
   - **Coral Crimson**: `#EF476F` (Penalties, errors, loss)

---

## 3. Camera choreography (`MovingCameraScene`)

Use dynamic framing only when scale or viewpoint is part of the inference. A
stable camera is often easier for a learner to inspect:

```python
from manim import *

class CinematicScene(MovingCameraScene):
    def construct(self):
        # 1. Wide Shot: establish the broad architecture
        self.camera.frame.save_state()
        
        # 2. Focus on an important formula when scale is part of the explanation
        target_formula = Text("E = mc²", font_size=36).shift(RIGHT * 3 + UP * 1)
        self.add(target_formula)
        
        self.play(
            self.camera.frame.animate.set(width=target_formula.width * 2.5).move_to(target_formula),
            run_time=2.0,
            rate_func=smooth
        )
        self.wait(1.0)

        # 3. Pull Back: return to wide canvas for the global picture
        self.play(Restore(self.camera.frame), run_time=1.8, rate_func=smooth)
```

---

## 4. Signals and pacing

- **Staggered Reveals (`LaggedStart`)**: Use a short stagger when order matters;
  simultaneous creation is fine when the objects form one unit.
- **Emphasis Signals**:
  When the narrator mentions a specific term:
  - `self.play(Indicate(mob, color=YELLOW, scale_factor=1.15))`
  - `self.play(Circumscribe(mob, color=CYAN, shape=Circle))`
  - `self.play(Wiggle(mob, rotation_angle=0.05 * TAU))`
- **Easing**: Choose a rate function that matches the claim. `smooth` suits a
  focus change; `linear` is useful for constant-rate motion or a parameter
  sweep. Do not let easing imply a physical law the model does not state.

Before keeping a glow, particle stream, or camera move, ask what the learner
should infer from it and whether the same inference survives in a still frame.
Remove the effect when it competes with notation, labels, or the active state.

---

## 5. Opt-in discipline (safe defaults)

The helpers in `components.illustrations` are off by default: a scene with
no grid, glow, particle, or camera move is the baseline, and at most one
effect should be active per cue. The exemplar
`examples/animations/gradient/scene.py` renders a clean diagram with every
helper unset.

- **Grid / halo**: `maybe_grid(enabled=False)` adds nothing unless enabled;
  `optional_glow(mob, enabled=False)` returns the mobject untouched unless
  enabled. Construct `Glow` once up front, never inside an updater.
- **Particles**: drive motion with `start_flow()` / `stop_flow()` (one
  looping updater over prebuilt dots, bounded count, wraps in place) rather
  than per-dot updaters or repeated one-shot nudges.
- **Distributions**: step between discrete states with
  `GaussianDistribution.update_to(...)`; do not re-plot the curve every frame.
- **Camera**: pair every `push_in(...)` with `pull_back(...)` and play the
  returned animation inside its cue with a `smooth` rate; plain scenes keep
  a stable camera and raise on these helpers.
- **Cleanup**: end each effect in the section that introduced it —
  `stop_flow()`, `FadeOut` the halo or grid, `clear_cinematic_updaters(...)`
  on section-local mobjects, `pull_back(...)` for the camera.
