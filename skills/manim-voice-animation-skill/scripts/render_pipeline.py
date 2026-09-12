#!/usr/bin/env python3
"""Render fresh Manim outputs, mux without truncation, and concatenate matching scenes."""
import argparse
from functools import lru_cache
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


@lru_cache(maxsize=1)
def resolve_ffmpeg_exe():
    candidates = [shutil.which('ffmpeg')]
    try:
        import imageio_ffmpeg
        candidates.append(imageio_ffmpeg.get_ffmpeg_exe())
    except ImportError:
        pass
    for candidate in candidates:
        if candidate:
            try:
                if subprocess.run([candidate, '-version'], capture_output=True, timeout=5).returncode == 0:
                    return candidate
            except (OSError, subprocess.TimeoutExpired):
                pass
    raise RuntimeError('No working FFmpeg. Install imageio-ffmpeg in this Python environment.')


def run(command):
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-6000:] or result.stdout[-6000:])
    return result


def media_info(path):
    import av
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    with av.open(str(path)) as container:
        duration = container.duration / av.time_base if container.duration else 0
        streams = []
        for stream in container.streams:
            context = stream.codec_context
            item = dict(type=stream.type, codec=context.name, time_base=str(stream.time_base))
            if stream.type == 'video':
                item.update(width=context.width, height=context.height, rate=str(stream.average_rate),
                            format=context.format.name if context.format else None)
            elif stream.type == 'audio':
                item.update(rate=context.sample_rate, layout=context.layout.name)
            streams.append(item)
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError(f'Cannot measure a positive duration: {path}')
        return dict(duration=duration, streams=streams)


def distinct_output(inputs, output):
    output = Path(output).resolve()
    if any(Path(p).resolve() == output for p in inputs):
        raise ValueError('Output must differ from every input')
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def run_manim_render(script_path, scene_name, quality='l', media_dir=None,
                     save_last_frame=False, transparent=False, custom_args=None):
    script_path = Path(script_path).resolve()
    if not script_path.is_file():
        raise FileNotFoundError(script_path)
    parent = Path(media_dir or 'media').resolve()
    parent.mkdir(parents=True, exist_ok=True)
    # A fresh run directory prevents returning an older or partial scene on success.
    folder = Path(tempfile.mkdtemp(prefix='run-', dir=parent))
    command = [sys.executable, '-m', 'manim', f'-q{quality}', str(script_path), scene_name,
               '--media_dir', str(folder)]
    if save_last_frame:
        command.append('-s')
    if transparent:
        command.append('-t')
    command.extend(custom_args or [])
    run(command)
    suffix = '.png' if save_last_frame else ('.mov' if transparent else '.mp4')
    candidates = [p for p in folder.rglob(scene_name + suffix) if 'partial_movie_files' not in p.parts]
    if len(candidates) != 1:
        raise RuntimeError(f'Expected one fresh {scene_name}{suffix}; found {len(candidates)} in {folder}')
    return candidates[0]


def mux_audio_video(video_path, audio_path, output_path):
    output = distinct_output([video_path, audio_path], output_path)
    visual, audio = media_info(video_path), media_info(audio_path)
    if not any(s['type'] == 'video' for s in visual['streams']):
        raise ValueError('Video input has no video stream')
    if not any(s['type'] == 'audio' for s in audio['streams']):
        raise ValueError('Audio input has no audio stream')
    duration = max(visual['duration'], audio['duration'])
    pad = max(0, duration - visual['duration'])
    command = [resolve_ffmpeg_exe(), '-v', 'error', '-y', '-i', str(video_path), '-i', str(audio_path),
               '-map', '0:v:0', '-map', '1:a:0']
    if pad:
        command += ['-vf', f'tpad=stop_mode=clone:stop_duration={pad}', '-c:v', 'libx264', '-pix_fmt', 'yuv420p']
    else:
        command += ['-c:v', 'copy']
    command += ['-af', 'apad', '-c:a', 'aac', '-b:a', '192k', '-t', str(duration), str(output)]
    run(command)
    return output


def concat_scenes(video_files, output_file):
    if not video_files:
        raise ValueError('Supply at least one scene')
    output = distinct_output(video_files, output_file)
    profiles = [media_info(p)['streams'] for p in video_files]
    if any(p != profiles[0] for p in profiles[1:]):
        raise ValueError('Scene stream formats differ; render at matching quality/audio settings before lossless concat')
    fd, name = tempfile.mkstemp(suffix='.txt', dir=output.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            for path in video_files:
                path = str(Path(path).resolve())
                if '\n' in path or '\r' in path:
                    raise ValueError('Newlines are not supported in media paths')
                escaped = path.replace("'", "'\\''")
                stream.write(f"file '{escaped}'\n")
        run([resolve_ffmpeg_exe(), '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', name,
             '-c', 'copy', str(output)])
    finally:
        Path(name).unlink(missing_ok=True)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    render = subs.add_parser('render')
    render.add_argument('script', type=Path); render.add_argument('scene')
    render.add_argument('-q', '--quality', choices=['l', 'm', 'h', 'k'], default='l')
    render.add_argument('--media-dir', type=Path, default=Path('media'))
    render.add_argument('-s', '--save-last-frame', action='store_true')
    render.add_argument('-t', '--transparent', action='store_true')
    render.add_argument('--voice', type=Path)
    render.add_argument('-o', '--output', type=Path)
    mux = subs.add_parser('mux')
    mux.add_argument('video', type=Path); mux.add_argument('audio', type=Path)
    mux.add_argument('-o', '--output', type=Path, required=True)
    concat = subs.add_parser('concat')
    concat.add_argument('videos', nargs='+', type=Path)
    concat.add_argument('-o', '--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'render':
            if args.voice and (args.save_last_frame or args.transparent):
                raise ValueError('--voice requires an opaque video render')
            result = run_manim_render(args.script, args.scene, args.quality, args.media_dir,
                                      args.save_last_frame, args.transparent)
            if args.voice:
                result = mux_audio_video(result, args.voice, args.output or result.with_name(args.scene + '_voiced.mp4'))
            elif args.output:
                target = distinct_output([args.script], args.output)
                if result.resolve() != target:
                    shutil.copy2(result, target)
                result = target
        elif args.command == 'mux':
            result = mux_audio_video(args.video, args.audio, args.output)
        else:
            result = concat_scenes(args.videos, args.output)
        print(result)
    except (OSError, ValueError, RuntimeError, ImportError) as exc:
        parser.exit(1, f'Media operation failed: {exc}\n')


if __name__ == '__main__':
    main()
