#!/usr/bin/env python3
"""Check local animation dependencies. This check is offline; only --voice-test uses the network."""
import argparse
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from render_pipeline import resolve_ffmpeg_exe, run_manim_render


USES = {
    'manim': 'render scenes (render_pipeline.py render)',
    'av': 'measure local clips and inspect media (offline)',
    'imageio_ffmpeg': 'provide a local FFmpeg binary (offline mux)',
    'mutagen': 'lightweight MP3 duration fallback (offline)',
    'edge_tts': 'network synthesis only; not needed for --silent or --audio-dir',
}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test',action='store_true',help='Render a short local scene (offline, needs manim and FFmpeg)')
    parser.add_argument('--voice-test',action='store_true',help='Send a public test sentence to Edge TTS (uses network)')
    args=parser.parse_args()
    print('Offline check only; no network calls unless --voice-test is given.')
    missing=[]
    for name, use in USES.items():
        present=importlib.util.find_spec(name) is not None
        print(f'{name}: {"available" if present else "missing"} ({use})')
        if not present: missing.append(name)
    try: print('FFmpeg:',resolve_ffmpeg_exe())
    except RuntimeError as exc: missing.append('ffmpeg');print(exc)
    print('LaTeX:',shutil.which('latex') or 'not installed; use Text/DecimalNumber or install TeX for MathTex')
    print('Modes: --silent works offline with stdlib only; --audio-dir works offline once clips exist; '
          'synthesis needs edge_tts plus network; render needs manim plus FFmpeg.')
    offline_ok=all(m not in missing for m in ('manim','av','imageio_ffmpeg','mutagen','ffmpeg'))
    if not offline_ok:
        print('Offline note: silent manifests need no audio deps; --audio-dir measuring needs av or mutagen; '
              'mux/concat need FFmpeg.')
    if missing:
        sys.stdout.flush()
        parser.exit(1,'Missing dependencies: '+', '.join(missing)+'\n')
    if args.self_test or args.voice_test:
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            if args.self_test:
                scene=folder/'scene.py'
                scene.write_text('from manim import *\nclass SelfTest(Scene):\n    def construct(self):\n        self.play(Create(Dot()), run_time=0.5)\n')
                print('Rendered:',run_manim_render(scene,'SelfTest',media_dir=folder/'media'))
            if args.voice_test:
                from voice_synthesizer import synthesize_clip
                import asyncio
                asyncio.run(synthesize_clip('This is a GNOS narration test.',folder/'voice.mp3'))
                print('Speech generated and measured.')


if __name__=='__main__': main()
