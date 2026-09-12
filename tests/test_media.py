"""Real FFmpeg regressions: no silent truncation, missing input, or guessed outputs."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/'skills/manim-voice-animation-skill/scripts'
sys.path.insert(0,str(SCRIPTS))
import render_pipeline as pipeline


@unittest.skipUnless(importlib.util.find_spec('av') and importlib.util.find_spec('imageio_ffmpeg'),'Requires media dependencies')
class MediaTests(unittest.TestCase):
    def run_ffmpeg(self,*args):
        subprocess.run([pipeline.resolve_ffmpeg_exe(),'-v','error','-y',*args],check=True,capture_output=True)

    def duration(self,path):
        import av
        with av.open(str(path)) as container:
            return container.duration / av.time_base


    def test_short_narration_preserves_full_visual_duration(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            self.run_ffmpeg('-f','lavfi','-i','color=c=black:s=160x90:r=15:d=2','-c:v','libx264',str(folder/'v.mp4'))
            self.run_ffmpeg('-f','lavfi','-i','sine=frequency=440:duration=0.5',str(folder/'a.wav'))
            pipeline.mux_audio_video(folder/'v.mp4',folder/'a.wav',folder/'out.mp4')
            self.assertAlmostEqual(self.duration(folder/'out.mp4'),2,delta=.15)

    def test_long_narration_is_not_cut_off(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            self.run_ffmpeg('-f','lavfi','-i','color=c=black:s=160x90:r=15:d=0.5','-c:v','libx264',str(folder/'v.mp4'))
            self.run_ffmpeg('-f','lavfi','-i','sine=frequency=440:duration=2',str(folder/'a.wav'))
            pipeline.mux_audio_video(folder/'v.mp4',folder/'a.wav',folder/'out.mp4')
            self.assertAlmostEqual(self.duration(folder/'out.mp4'),2,delta=.15)

    def test_concat_accepts_spaces_and_apostrophe_in_filename(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            source=folder/"learner's scene.mp4"
            self.run_ffmpeg('-f','lavfi','-i','color=c=black:s=160x90:r=15:d=1','-c:v','libx264',str(source))
            pipeline.concat_scenes([source,source],folder/'out.mp4')
            self.assertAlmostEqual(self.duration(folder/'out.mp4'),2,delta=.15)


class StoryboardTests(unittest.TestCase):
    def test_duplicate_scene_ids_are_rejected_before_synthesis(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp); source=folder/'storyboard.json'
            scene=dict(id='SceneOne',title='One',narration_cues=[dict(cue_id='first',text='Example',duration=1)])
            source.write_text(json.dumps(dict(title='Demo',scenes=[scene,scene])))
            result=subprocess.run([sys.executable,str(SCRIPTS/'voice_synthesizer.py'),
                                   '--storyboard',str(source),'--out',str(folder/'audio'),'--silent'],
                                  capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('Duplicate scene',result.stderr)


if __name__=='__main__': unittest.main()
