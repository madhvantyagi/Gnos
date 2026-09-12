#!/usr/bin/env python3
"""Check local animation dependencies. Rendering and network speech are explicit options."""
import argparse
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from render_pipeline import resolve_ffmpeg_exe, run_manim_render


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test',action='store_true',help='Render a short local scene')
    parser.add_argument('--voice-test',action='store_true',help='Send a public test sentence to Edge TTS')
    args=parser.parse_args()
    missing=[]
    for name in ('manim','av','imageio_ffmpeg','edge_tts'):
        present=importlib.util.find_spec(name) is not None
        print(f'{name}: {"available" if present else "missing"}')
        if not present: missing.append(name)
    try: print('FFmpeg:',resolve_ffmpeg_exe())
    except RuntimeError as exc: missing.append('ffmpeg');print(exc)
    print('LaTeX:',shutil.which('latex') or 'not installed; use Text/DecimalNumber or install TeX for MathTex')
    if missing: parser.exit(1,'Missing dependencies: '+', '.join(missing)+'\n')
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
