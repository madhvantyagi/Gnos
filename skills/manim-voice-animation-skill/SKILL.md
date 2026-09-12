---
name: manim-voice-animation
description: Create Manim teaching animations with optional measured narration, synchronized cues, subtitles, and verified renders when motion helps explain a concept or a video is requested.
---

# Manim teaching animations

Choose one change the learner needs to see: a secant approaching a tangent,
a basis transformation, a force changing motion, or an algorithm changing state.
A good still diagram is preferable when nothing needs to move.

## Build around a teaching question

Write a storyboard before scene code. Each scene needs a concept target, exact
narration, visible objects, and the change each cue reveals. Keep notation
consistent with the course. Predict → show → explain → vary the case is a useful
sequence, not a mandatory script for every video.

Use `templates/storyboard_schema.json`; validate IDs and cues with the voice
script before spending time on narration. The storyboard's duration field is
only an authored silent-preview timing. Spoken durations are measured from audio.

## Narration and timing

Commands below run from the repository root in an environment with Manim,
edge-tts, PyAV, and imageio-ffmpeg. Check dependencies without network calls:

```bash
python3 skills/manim-voice-animation-skill/scripts/setup_env.py
```

Generate narration from a storyboard:

```bash
python3 skills/manim-voice-animation-skill/scripts/voice_synthesizer.py \
  --storyboard examples/animations/gradient/storyboard.json \
  --out output/gradient/audio
```

This uses the external Edge TTS service; only the narration text is sent. Do not
send learner records or unrelated personal context. Availability and voice names
can change. For an offline preview use `--silent`; for pre-recorded local MP3s use
`--audio-dir <folder>` with filenames `SceneID_cue-id.mp3`. Do not label silence
as generated speech. A provider error must remain visible.

Read [references/02_voiceover_synchronization.md](references/02_voiceover_synchronization.md).
Use `scripts/cue_player.py` to attach each clip at the actual scene time and
export subtitles. A teacher's deliberate pause can then stay between cues.
Do not mux again after a scene already includes audio.

## Render and inspect

```bash
python3 skills/manim-voice-animation-skill/scripts/linter.py scene.py
python3 skills/manim-voice-animation-skill/scripts/render_pipeline.py \
  render scene.py MyScene -q l -o output/preview.mp4
```

Inspect the beginning, each conceptual transition, and the ending; listen for
pronunciation and early/late narration. Check numbers against the equations and
inspect text at actual playback size. Low quality means lower resolution, not
a shorter video. Use `-q h` only after the preview is correct.

For an already-aligned whole-scene audio track, the `mux` command preserves the
longer duration by adding silence or holding the last frame. That prevents
truncation; it does not repair semantic misalignment. Lossless `concat` requires
matching stream formats and reports mismatches.

## Visual judgment

Use a stable camera unless movement reveals useful structure. Keep the quantity
being compared visible. Prefer continuous updates to re-creating expensive text
or LaTeX every frame. Tie displayed values to the same state as the geometry.
Check bounds against the actual frame/aspect ratio. Clear active updaters when
objects leave the scene. Grids, halos, particles, and camera motion are optional;
they should clarify a relationship, not compete for attention.

Read only the reference for the chosen scene:

- [Storyboard](references/01_pedagogical_storyboard.md)
- [Proofs and calculus](references/03_math_proofs_calculus.md)
- [Linear algebra](references/04_linear_algebra_matrices.md)
- [Mechanics and fields](references/05_physics_mechanics_fields.md)
- [Algorithms](references/06_cs_algorithms_graphs.md)
- [3D camera](references/07_3d_surfaces_camera.md)
- [Common failures](references/08_anti_patterns_curated_fixes.md)
- [Optional visual components](references/09_cinematic_depth_and_illustrations.md)

The five subject templates remain starting points, not verified lessons for all
inputs. The runnable GNOS example is `examples/animations/gradient/scene.py`.
