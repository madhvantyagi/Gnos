"""Browser and downloadable subtitles share measured narration timings."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('cue_player', ROOT / 'skills/manim-voice-animation/scripts/cue_player.py')
cue_player = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cue_player)


class Scene:
    time = 0.0
    def wait(self, duration):
        self.time += duration


class CaptionTimelineTests(unittest.TestCase):
    def test_webvtt_and_srt_follow_measured_cues_and_pause(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = root / 'narration.json'
            manifest.write_text(json.dumps({'scenes': {'example': {'cues': [
                {'cue_id': 'first', 'duration': 1.25, 'pause_after': .5,
                 'text': 'x < y\n\nbecause the boundary matters.'},
                {'cue_id': 'second', 'duration': 2, 'text': 'Explain the change.'}]}}}))
            player = cue_player.CuePlayer(Scene(), manifest, 'example')
            player.play('first')
            player.play('second')
            player.finish(root / 'lesson')
            self.assertEqual(json.loads((root / 'lesson.timing.json').read_text())[1]['start'], 1.75)
            self.assertIn('00:00:01,750 --> 00:00:03,750', (root / 'lesson.srt').read_text())
            self.assertTrue((root / 'lesson.vtt').is_file(), 'native caption companion must be exported')
            vtt = (root / 'lesson.vtt').read_text()
            self.assertTrue(vtt.startswith('WEBVTT\n\n'))
            self.assertIn('00:00:01.750 --> 00:00:03.750', vtt)
            self.assertIn('x &lt; y', vtt)
            self.assertIn('x &lt; y because the boundary matters.', vtt)
            self.assertIn('x < y because the boundary matters.', (root / 'lesson.srt').read_text())
