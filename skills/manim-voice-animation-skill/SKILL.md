---
name: manim-voice-animation
description: Create Manim teaching animations with optional measured narration, synchronized cues, subtitles, and verified renders when motion helps explain a concept or a video is requested.
---

# Manim teaching animations

Use Manim when motion exposes a relationship the learner needs to inspect. A
still diagram, runnable example, or source excerpt is the better representation
when nothing meaningful changes.

## Start with GNOS context

Treat the animation as a teaching artifact, not a generic explainer. Before
writing scene code:

1. Identify the learner's target action (derive, predict, implement, or explain)
   and the last step supported by evidence. Do not invent a learner record.
2. Load the selected subject reference and one lead teacher. Read the active
   course only when it sets notation, sequence, or assessment; read the learner
   snapshot only when an identity and relevant evidence are established. A
   supporting subject supplies a named bridge, not a second narrator.
3. State the concept ID, prerequisite assumption, and one observable success
   check in the storyboard notes or adjacent design file. Keep course notation
   and the teacher's voice consistent with the lesson.
4. Choose one change the learner needs to see: for example, a secant tending to
   a tangent, a basis transforming, a force changing motion, or an algorithm
   changing state. Predict → show → explain → vary is useful when it serves the
   target, but is not a universal script.

Write the storyboard before scene code. Each scene needs a concept target, exact
narration, visible objects, and the change each cue reveals. Use
`templates/storyboard_schema.json`; validate IDs and cues before spending time
on narration. Its `duration` is authored timing for a silent preview. Spoken
durations come from measured clips or local recordings.

## Narration and timing

Read [references/02_voiceover_synchronization.md](references/02_voiceover_synchronization.md).
`scripts/cue_player.py` is the timeline boundary: construct it with the scene,
manifest path, and scene ID; call `play(cue_id, *animations, run_time=...)` once
per cue; call `finish(output_prefix)` after all cues. It attaches each local clip
at the current scene time, fills unused cue duration with a wait, applies
`pause_after`, and exports actual cue starts to SRT and timing JSON. Do not reuse
a cue or leave one unplayed. An animation must fit inside its cue.

Check dependencies without network calls:

```bash
python3 skills/manim-voice-animation-skill/scripts/setup_env.py
```

Narration generation uses an external provider only when explicitly requested:

```bash
python3 skills/manim-voice-animation-skill/scripts/voice_synthesizer.py \
  --storyboard path/to/storyboard.json --out output/topic/audio
```

`--silent` creates an honest preview manifest with authored durations and no
speech. `--audio-dir <folder>` uses measured local files named
`SceneID_cue-id.mp3`. Never call silence generated speech, send learner records
to a voice provider, or hide a provider failure. Do not mux again after
cue-timed audio is already in the scene.

## Render and review the artifact

```bash
python3 skills/manim-voice-animation-skill/scripts/linter.py scene.py
python3 skills/manim-voice-animation-skill/scripts/render_pipeline.py \
  render scene.py MyScene -q l -o output/preview.mp4
```

Review the first frame, every conceptual transition, and the ending at actual
playback size. Check that each spoken term points to the corresponding object,
numbers agree with displayed equations and simulation state, labels stay in
frame, and no updater remains attached after its section. Listen for cue drift
when audio exists. A silent render verifies choreography only. Use a higher
quality only after the low-quality preview is correct.

## Visual judgment

Keep the compared quantity visible and use a stable camera unless movement
reveals structure. Prefer `ValueTracker`, `DecimalNumber`, and lightweight
updaters over rebuilding `MathTex` or other expensive objects every frame. Tie
displayed values to the same state as the geometry. Grids, halos, particles,
and camera motion are optional signals; remove them when they compete with the
concept. Check bounds against the chosen aspect ratio and clear updaters when
objects leave the scene.

Read only the reference for the chosen scene:

- [Storyboard](references/01_pedagogical_storyboard.md)
- [Proofs and calculus](references/03_math_proofs_calculus.md)
- [Linear algebra](references/04_linear_algebra_matrices.md)
- [Mechanics and fields](references/05_physics_mechanics_fields.md)
- [Algorithms](references/06_cs_algorithms_graphs.md)
- [3D camera](references/07_3d_surfaces_camera.md)
- [Common failures](references/08_anti_patterns_curated_fixes.md)
- [Optional visual components](references/09_cinematic_depth_and_illustrations.md)

The five subject templates are starting points, not verified lessons for every
input. The runnable GNOS example is `examples/animations/gradient/scene.py`.
