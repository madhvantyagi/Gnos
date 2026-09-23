"""Place narration on the actual Manim timeline; export matching subtitles."""
import json
import math
from pathlib import Path


def timestamp(seconds):
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    return f'{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}'


class CuePlayer:
    """Timeline boundary: one play() per cue, audio at the actual cue start."""

    def __init__(self, scene, manifest_path, scene_id):
        self.scene = scene
        self.path = Path(manifest_path)
        manifest = json.loads(self.path.read_text())
        try:
            entry = manifest['scenes'][scene_id]
        except (KeyError, TypeError):
            raise ValueError(f'Unknown scene in manifest: {scene_id}') from None
        cues = entry.get('cues')
        if not isinstance(cues, list) or not cues:
            raise ValueError(f'Scene has no narration cues: {scene_id}')
        self.cues = {c['cue_id']: c for c in cues}
        self.timeline = []
        self.used = set()

    def play(self, cue_id, *animations, run_time=None):
        if cue_id not in self.cues:
            raise ValueError(f'Unknown narration cue: {cue_id}')
        if cue_id in self.used:
            raise ValueError(f'Cue already played: {cue_id}')
        cue = self.cues[cue_id]
        duration = float(cue['duration'])
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError('Cue duration must be positive and measured, or explicitly authored for a silent preview')
        runtime = duration if run_time is None else float(run_time)
        if not math.isfinite(runtime) or runtime <= 0 or runtime > duration:
            raise ValueError('Animation duration must be positive and fit inside its narration cue')
        pause = float(cue.get('pause_after', 0))
        if not math.isfinite(pause) or pause < 0:
            raise ValueError('pause_after must be finite and nonnegative')
        # Attach at the actual scene time so earlier pauses cannot drift later
        # words away from their visual events. The recorded start is read fresh
        # here; pause_after is applied after the cue and only shifts the next
        # cue's measured start.
        start = self.scene.time
        if cue.get('audio_file'):
            audio = Path(cue['audio_file'])
            if not audio.is_absolute():
                audio = self.path.parent / audio
            if not audio.is_file():
                raise FileNotFoundError(f'Missing audio for cue {cue_id}: {audio}')
            self.scene.add_sound(str(audio.resolve()))
        if animations:
            self.scene.play(*animations, run_time=runtime)
        elapsed = self.scene.time - start
        if duration > elapsed:
            self.scene.wait(duration - elapsed)
        self.timeline.append(dict(cue_id=cue_id, start=start, end=start + duration, text=cue['text']))
        self.used.add(cue_id)
        if pause:
            self.scene.wait(pause)

    def finish(self, output_prefix):
        missing = set(self.cues) - self.used
        if missing:
            raise ValueError(f'Unplayed narration cues: {sorted(missing)}')
        prefix = Path(output_prefix)
        prefix.parent.mkdir(parents=True, exist_ok=True)
        # Subtitles reuse the same measured cue timings, so SRT and timing
        # JSON cannot drift apart.
        prefix.with_suffix('.timing.json').write_text(json.dumps(self.timeline, indent=2) + '\n')
        parts = [f"{i}\n{timestamp(c['start'])} --> {timestamp(c['end'])}\n{c['text']}\n"
                 for i, c in enumerate(self.timeline, 1)]
        prefix.with_suffix('.srt').write_text('\n'.join(parts) + '\n')
