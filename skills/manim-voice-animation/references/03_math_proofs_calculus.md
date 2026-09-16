# Mathematics: Proofs, Calculus & LaTeX

Mathematical visualizations require strict formula typesetting, clean morphing transformations, and dynamic coordinate geometry.

Choose the smallest derivation that repairs the learner's missing implication.
State hypotheses beside the scene plan (domain, differentiability, interval,
or sign restrictions); a polished equation cannot supply a missing condition.
Keep the teacher's notation and the course's concept ID, and finish with a
changed value or counterexample that tests transfer.

---

## 1. LaTeX & Formula Derivations (`MathTex`)

### Raw String Requirement
Always prefix LaTeX strings with `r"..."`. Failing to do so causes Python escape sequence errors:

```python
# CORRECT
formula = MathTex(r"\int_{a}^{b} f(x) \, dx = F(b) - F(a)")

# INCORRECT (causes syntax warnings or LaTeX render failure)
formula = MathTex("\int_{a}^{b} f(x) \, dx")
```

### Isolating Substrings for Formula Morphing
When transitioning equations, use `substrings_to_isolate` to enable component-level colorization and morphing via `TransformMatchingTex`:

```python
# Step 1: Define initial and subsequent equation with shared keys
eq1 = MathTex(r"a^2", r"+", r"b^2", r"=", r"c^2", substrings_to_isolate=[r"a^2", r"b^2", r"c^2"])
eq2 = MathTex(r"a^2", r"=", r"c^2", r"-", r"b^2", substrings_to_isolate=[r"a^2", r"b^2", r"c^2"])

eq1.set_color_by_tex(r"a^2", BLUE)
eq1.set_color_by_tex(r"b^2", GREEN)
eq1.set_color_by_tex(r"c^2", RED)

self.play(Write(eq1))
self.wait(1)

# Morphing transformation preserves isolated components
self.play(TransformMatchingTex(eq1, eq2, transform_mismatches=True), run_time=2)
```

---

## 2. Coordinate Geometry & Function Plotting (`Axes`)

```python
axes = Axes(
    x_range=[-1, 5, 1],
    y_range=[-1, 10, 2],
    x_length=7,
    y_length=4.5,
    axis_config={"color": GREY_B, "include_numbers": True},
    tips=False
).to_edge(DOWN)

# Plotting smooth mathematical functions
curve = axes.plot(lambda x: x**2 - 2*x + 2, x_range=[0, 4], color=YELLOW)
curve_label = axes.get_graph_label(curve, label=r"f(x) = x^2 - 2x + 2", x_val=3.5, direction=UR)

self.play(Create(axes), run_time=1.5)
self.play(Create(curve), Write(curve_label), run_time=2)
```

---

## 3. Dynamic Tangent Line with `ValueTracker` & `always_redraw`

```python
# Tracker for x-coordinate along the curve
x_val = ValueTracker(1.0)

# Dot pinned to the function curve
dot = always_redraw(lambda: Dot(
    point=axes.c2p(x_val.get_value(), (lambda x: x**2 - 2*x + 2)(x_val.get_value())),
    color=RED
))

# Tangent line updated dynamically as x_val animates
tangent_line = always_redraw(lambda: axes.get_secant_slope_group(
    x=x_val.get_value(),
    graph=curve,
    dx=0.001,
    secant_line_length=4,
    secant_line_color=BLUE_C
))

self.add(dot, tangent_line)
# Move the tangent line smoothly along the curve from x=1 to x=3.5
self.play(x_val.animate.set_value(3.5), run_time=3.5, rate_func=linear)
```

`always_redraw` is appropriate for geometric objects whose shape genuinely
changes. Do not put a new `MathTex` call in that callback. For a changing
number, create one `DecimalNumber` (or a `Text`-backed numeric display) and
update its value; clear its updater after the sweep.

---

## 4. Riemann Sum Convergence

```python
# Initial coarse Riemann sum (dx = 1.0)
rects_1 = axes.get_riemann_rectangles(curve, x_range=[0, 3], dx=1.0, color=BLUE, stroke_width=1)
self.play(Create(rects_1))
self.wait(1)

# Refined Riemann sum (dx = 0.25)
rects_2 = axes.get_riemann_rectangles(curve, x_range=[0, 3], dx=0.25, color=TEAL, stroke_width=0.5)
self.play(ReplacementTransform(rects_1, rects_2), run_time=2)

# True continuous area under curve
area = axes.get_area(curve, x_range=[0, 3], color=GREEN, opacity=0.4)
self.play(ReplacementTransform(rects_2, area), run_time=2)
```

Review: check that the displayed function, rectangle sample points, interval,
and `dx` agree. A rectangle count becoming larger is not by itself convergence;
show the approximation error or state the assumption that the learner is meant
to notice.

---

## 5. Narrated-scene checklist (timeline, camera, cleanup)

- Route every animation through `CuePlayer.play(cue_id, ...)` once per cue and
  call `finish(...)` after the last cue; do not pad cues with bare `self.wait`
  (use `pause_after` in the manifest for inspection time).
- Keep the camera stable; the secant-to-tangent morph is the change, not camera
  motion. Check bounds for 16:9 (frame x in [-7.11, 7.11], y in [-4.0, 4.0]):
  keep shifts under 6 (X) / 3.5 (Y) and pin readouts with `to_corner`/`to_edge`
  so labels stay in frame.
- Drive secants, tangents, and `DecimalNumber` readouts from the same
  `ValueTracker` state; never construct `MathTex` per frame. Clear all updaters
  (geometry redraws and numeric updaters) before `finish` so later sections do
  not lag.
