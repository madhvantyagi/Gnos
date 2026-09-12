# Physics, Mechanics & Dynamic Fields

Simulating physical processes requires an explicit state, parameters, and a
numerical update via `add_updater(dt)`, vector fields, or particle trails. Name
the model's assumptions (for example, no air drag, small-angle motion, or a
two-dimensional projection) before showing a trajectory. A rendered path is a
model result, not measured evidence.

---

## 1. Projectile Motion with Dynamic Trail (`TracedPath`)

```python
from manim import *

class ProjectileScene(Scene):
    def construct(self):
        axes = Axes(x_range=[0, 10, 2], y_range=[0, 6, 1], x_length=8, y_length=4.5).to_corner(DL)
        self.add(axes)

        # Initial physics parameters
        v0 = 8.0          # Initial velocity (m/s)
        angle = PI / 4    # 45 degrees
        g = 9.8           # Gravity (m/s^2)
        vx = v0 * np.cos(angle)
        vy = v0 * np.sin(angle)
        
        t_tracker = ValueTracker(0.0)
        t_max = (2 * vy) / g

        # Moving projectile ball
        ball = always_redraw(lambda: Dot(
            point=axes.c2p(
                vx * t_tracker.get_value(),
                max(0, vy * t_tracker.get_value() - 0.5 * g * (t_tracker.get_value() ** 2))
            ),
            color=RED,
            radius=0.12
        ))

        # Trail following the ball trajectory
        trail = TracedPath(ball.get_center, stroke_color=YELLOW, stroke_width=2.5)

        self.add(trail, ball)
        self.play(t_tracker.animate.set_value(t_max), run_time=3.0, rate_func=linear)
        self.wait(1)
```

---

## 2. Harmonic Oscillator / Simple Pendulum via `add_updater`

Using discrete time-step integration (`dt`) to simulate a physical pendulum:

```python
class PendulumSimulation(Scene):
    def construct(self):
        pivot = UP * 2.5
        pivot_dot = Dot(pivot, color=WHITE)
        
        # State variables: [theta, omega]
        length = 3.0
        g = 9.8
        state = {"theta": PI / 3, "omega": 0.0}

        bob = Dot(radius=0.2, color=BLUE)
        rod = always_redraw(lambda: Line(pivot, bob.get_center(), stroke_width=3, color=GREY_A))

        def update_physics(mob, dt):
            # Non-linear pendulum: alpha = -(g/L) * sin(theta)
            alpha = -(g / length) * np.sin(state["theta"])
            state["omega"] += alpha * dt
            state["theta"] += state["omega"] * dt
            
            # Position bob based on angle
            x = pivot[0] + length * np.sin(state["theta"])
            y = pivot[1] - length * np.cos(state["theta"])
            mob.move_to([x, y, 0])

        # Position initial bob
        bob.move_to([pivot[0] + length * np.sin(state["theta"]), pivot[1] - length * np.cos(state["theta"]), 0])
        bob.add_updater(update_physics)

        self.add(pivot_dot, rod, bob)
        self.wait(4.0)  # Runs the physics simulation for 4 seconds

        # IMPORTANT: Always clear updaters before subsequent transitions
        bob.clear_updaters()
```

Review the units and invariant that the learner should inspect: energy for a
conservative oscillator, the sign of acceleration, or the field direction.
Use a small enough effective time step for the chosen model, and never leave a
simulation updater active while presenting a later conceptual state.

---

## 3. Vector Fields & Electric Field Lines (`ArrowVectorField`)

```python
class VectorFieldScene(Scene):
    def construct(self):
        # 2D Dipole field or vortex field: F(x, y) = [-y, x] / (x^2 + y^2 + 0.1)
        func = lambda pos: np.array([
            -pos[1] / (pos[0]**2 + pos[1]**2 + 0.2),
             pos[0] / (pos[0]**2 + pos[1]**2 + 0.2),
             0
        ])

        field = ArrowVectorField(
            func,
            x_range=[-4, 4, 0.8],
            y_range=[-3, 3, 0.8],
            length_func=lambda norm: 0.4 * sigmoid(norm)
        )

        stream_lines = StreamLines(
            func,
            x_range=[-4, 4, 0.5],
            y_range=[-3, 3, 0.5],
            stroke_width=1.5,
            virtual_time=2
        )

        self.play(Create(field), run_time=2)
        self.play(stream_lines.create(), run_time=2)
        self.wait(1)
```
