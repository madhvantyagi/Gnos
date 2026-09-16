# Curated Anti-Patterns & Battle-Tested Fixes

A compilation of frequent errors in generated Manim Community Edition code, with
remedies that preserve the teaching claim. Check these examples against the
installed Manim version and the chosen scene; a visual flourish is not a fix for
an incorrect invariant.

---

## 1. Syntax & API Deprecations

| Anti-Pattern (Wrong) | Correct Fix | Rationale |
| :--- | :--- | :--- |
| `class Scene(Scene): CONFIG = {...}` | Use `__init__` or inline parameters | `CONFIG` was removed in ManimCE v0.2.0+. |
| `ShowCreation(mobject)` | `Create(mobject)` | `ShowCreation` is a legacy ManimGL function. |
| `ApplyMethod(dot.shift, UP)` | `dot.animate.shift(UP)` | Modern syntax uses `.animate` syntax. |
| `TextMobject("Hello")` | `Tex("Hello")` or `Text("Hello")` | `TextMobject` is deprecated. Use `Text` for words and `Tex`/`MathTex` for LaTeX. |
| `axes.get_graph(func)` | `axes.plot(func)` | `get_graph` is deprecated in favor of `plot`. |

---

## 2. LaTeX & String Escapes

### Error: `LaTeX compilation error: undefined control sequence`
- **Cause**: Writing `MathTex("\frac{a}{b}")` without raw string `r"..."`. Python interprets `\f` as an ASCII formfeed character (`\x0c`), producing corrupt LaTeX input.
- **Fix**: Always use raw strings: `MathTex(r"\frac{a}{b}")`.

---

## 3. Positioning & Visual Overlap

### Error: Mobjects Rendered Off-Screen
- **Cause**: The default 16:9 camera view spans from $x \in [-7.11, 7.11]$ and $y \in [-4.0, 4.0]$. Shifting by `RIGHT * 8` moves objects out of frame.
- **Fix**: Keep shifts within magnitude 6 for X and 3.5 for Y, or use `.to_edge(UP, buff=0.5)` and `.to_corner(UR)`.

### Error: Text Elements Overlap
- **Cause**: Adding multiple text items without explicit vertical offsets.
- **Fix**: Use `VGroup(line1, line2, line3).arrange(DOWN, aligned_edge=LEFT, buff=0.35)` to ensure automatic non-overlapping spacing.

---

## 4. Animation Lifecycle & Updaters

### Error: `Transform()` Leaves Ghost Duplicates
- **Cause**: `self.play(Transform(A, B))` transforms A to look like B, but keeps object A in the scene hierarchy while B is discarded. Subsequent operations on B fail.
- **Fix**: Use `self.play(ReplacementTransform(A, B))` when you intend B to become the active mobject.

### Error: Animations Lag or Glitch in Subsequent Scenes
- **Cause**: Active updaters (`add_updater`) continue firing every frame even after the animation finishes.
- **Fix**: Always invoke `mobject.clear_updaters()` before moving to the next section of the scene.

---

## 5. Audio & Voice Synchronization

### Error: Voice Cuts Off Abruptly at Scene End
- **Cause**: A cue-timed scene leaves a clip or authored reflection pause outside
  the scene timeline.
- **Fix**: Call `CuePlayer.finish(...)` after every cue. It waits for the
  measured or authored cue duration and exports the actual timings. Add a final
  wait only when the storyboard deliberately leaves reflection time; do not use
  a universal buffer to mask an unplayed cue.

### Error: Desynchronization Between Dialogue and Action
- **Cause**: Setting a hardcoded animation duration that exceeds its spoken cue,
  or placing a concatenated track over independently paused visuals.
- **Fix**: Route the scene through `CuePlayer.play(cue_id, ...)`; its manifest
  duration is measured for audio and authored for silent previews, and it rejects
  an animation that runs longer than the cue. Use whole-track mux only when the
  track was authored for that exact final video.

---

## 6. Cinematic & exemplar traps

| Anti-Pattern (Wrong) | Correct Fix | Rationale |
| :--- | :--- | :--- |
| `sys.path` pointing at `skills/manim-voice-animation-skill/scripts` | Use `skills/manim-voice-animation/scripts` | The skill was renamed; the stale path breaks every helper import. |
| Hard `from pydub import ...` at scene top | Keep audio wrappers out of scenes, or import them lazily | A silent preview is the choreography check and must render without audio dependencies. |
| Hardcoded tangent endpoints and literal display numbers | Derive endpoints and labels from the same tracker constants (e.g. `X1 = X0 - ETA * DFDX(X0)`) | Displayed values must equal the simulation state; literals drift apart on the next edit. |
| `clear_updaters()` only at scene end | Clear each updater in the cue after its section ends | Lingering updaters fire every frame and lag later cues (extends §4). |
| `run_time` longer than the cue `duration` | Keep every `run_time` inside its cue; let `CuePlayer` hold the remainder | Overflow is rejected for a reason: rewrite the narration or split the choreography (extends §5). |
