# Narration on the scene timeline

Use the measured clip duration and attach each clip at the time its visual cue
actually begins. Guessing pause duration from punctuation is unreliable.

```python
from cue_player import CuePlayer

player = CuePlayer(self, manifest_path, "MyScene")
player.play("first", Create(curve), run_time=1.5)
self.wait(0.8)  # Reflection time; the next clip starts after this pause.
player.play("second", dot.animate.move_to(destination))
player.finish("output/my-scene")
```

Import the helper by adding this skill's `scripts/` to the scene's Python import
path. See the runnable example for resolving paths relative to the scene file.

`play` places audio using Manim's `Scene.add_sound`, starts the animation, and
waits for any remaining clip time. It rejects animation durations longer than the
cue; rewrite the narration or divide the choreography rather than silently
cutting speech. `pause_after` adds authored reflection time. `finish` rejects
unplayed cues and exports actual cue starts to SRT and timing JSON.

Frames quantize visual durations. Expect sub-frame rounding, not a promise of
perfect sample-level alignment. Inspect the rendered artifact. Sentence-internal
synchronization needs shorter cues or a verified bookmark-capable provider; do
not infer word timestamps from total clip duration.

Silent-preview manifests use explicitly supplied durations and `audio_file:
null`. They exercise the same visual sequence without claiming speech exists.
Local recordings are measured from the real files. Synthesized recordings use
fresh per-run directories; a failed synthesis leaves the previous successful
manifest and its clips usable.

Whole-track mux is only for an audio track authored for that exact video
sequence. Padding the shorter stream avoids truncation but cannot move words
back onto their visual events. Never mux a concatenation of clips over a video
with extra pauses unless those pauses are also represented in the audio.

API reference: [Manim Scene](https://docs.manim.community/en/stable/reference/manim.scene.scene.Scene.html),
including `add_sound`; checked against the installed Manim 0.21.0 in this build.
