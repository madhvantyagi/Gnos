#!/usr/bin/env python3
"""Create measured narration cues, or an explicitly silent preview manifest.

Only storyboard cue text is ever sent to the speech provider. Never point
--storyboard at learners/ records; the script refuses such paths. Provider
failures are loud: the failing run writes no manifest, so the previous
successful manifest and its clips stay usable.
"""
import argparse
import asyncio
import json
import math
import os
from pathlib import Path
import re
import tempfile

VOICE_PRESETS = {
    'explainer-male': 'en-US-ChristopherNeural',
    'explainer-female': 'en-US-AvaNeural',
    'british-female': 'en-GB-SoniaNeural',
    'british-male': 'en-GB-RyanNeural',
    'casual-male': 'en-US-GuyNeural',
    'casual-female': 'en-US-JennyNeural',
}
DEFAULT_VOICE = VOICE_PRESETS['explainer-male']


def refuse_learner_paths(path):
    """Never send private learner records to an external voice provider."""
    resolved = Path(path).resolve()
    if 'learners' in resolved.parts:
        raise ValueError(f'Refusing storyboard inside learners/: {path}. Only storyboard cue text may be synthesized.')


def srt_timestamp(seconds):
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    return f'{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}'


def preview_srt_lines(cues):
    """Planned subtitles from the same cue timings stored in the manifest."""
    lines = []
    start = 0.0
    for index, cue in enumerate(cues, 1):
        end = start + float(cue['duration'])
        lines.append(f"{index}\n{srt_timestamp(start)} --> {srt_timestamp(end)}\n{cue['text']}\n")
        start = end + float(cue.get('pause_after', 0))
    return '\n'.join(lines) + '\n'


def validate_storyboard(data):
    if not isinstance(data, dict) or not isinstance(data.get('title'), str) or not data['title'].strip():
        raise ValueError('Storyboard requires a title')
    if not isinstance(data.get('scenes'), list) or not data['scenes']:
        raise ValueError('Storyboard requires scenes')
    if data.get('aspect_ratio', '16:9') not in ('16:9', '9:16', '1:1'):
        raise ValueError('Unsupported aspect ratio')
    seen = set()
    for scene in data['scenes']:
        id_ = scene.get('id', '')
        if not isinstance(id_, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', id_):
            raise ValueError('Scene IDs must be safe Python class names')
        if id_ in seen:
            raise ValueError(f'Duplicate scene ID: {id_}')
        seen.add(id_)
        cues = scene.get('narration_cues')
        if not isinstance(cues, list) or not cues:
            raise ValueError(f'{id_}: narration_cues must be nonempty')
        cue_ids = set()
        for cue in cues:
            cid = cue.get('cue_id', '')
            if not isinstance(cid, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', cid):
                raise ValueError('Cue IDs may use letters, digits, underscore, hyphen')
            if cid in cue_ids:
                raise ValueError(f'Duplicate cue ID: {id_}/{cid}')
            cue_ids.add(cid)
            if not isinstance(cue.get('text'), str) or not cue['text'].strip():
                raise ValueError(f'{id_}/{cid}: narration must be nonempty')
            for key in ('duration', 'pause_after'):
                if key in cue:
                    value = cue[key]
                    if type(value) not in (int, float) or not math.isfinite(value) or value < 0 or (key == 'duration' and value == 0):
                        raise ValueError(f'{key} must be finite and {"positive" if key == "duration" else "nonnegative"}')
    return data


def audio_duration(path):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f'Missing local narration clip: {path}. Expected SceneID_cue-id.mp3 in --audio-dir.')
    try:
        from render_pipeline import media_info
        info = media_info(path)
    except ImportError:
        # Offline fallback when PyAV is unavailable; local clips are MP3.
        from mutagen.mp3 import MP3
        length = float(MP3(str(path)).info.length)
        if not math.isfinite(length) or length <= 0:
            raise ValueError(f'Cannot measure a positive duration: {path}')
        return length
    if not any(s['type'] == 'audio' for s in info['streams']):
        raise ValueError(f'No audio stream in {path}')
    return info['duration']


async def synthesize_clip(text, output_path, voice=DEFAULT_VOICE, rate='+0%'):
    import edge_tts
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(suffix='.mp3', dir=output_path.parent)
    os.close(fd)
    try:
        await asyncio.wait_for(edge_tts.Communicate(text=text, voice=voice, rate=rate).save(temporary), timeout=60)
        duration = audio_duration(temporary)
        os.replace(temporary, output_path)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return dict(text=text, audio_file=str(output_path.resolve()), duration=duration)


async def process_storyboard(storyboard_path, output_dir, voice=None, rate='+0%', silent=False, audio_dir=None):
    refuse_learner_paths(storyboard_path)
    data = validate_storyboard(json.loads(Path(storyboard_path).read_text()))
    chosen_voice = voice or data.get('voice', 'explainer-male')
    chosen_voice = VOICE_PRESETS.get(chosen_voice, chosen_voice)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if audio_dir is not None and not Path(audio_dir).is_dir():
        raise FileNotFoundError(f'Missing --audio-dir folder: {audio_dir}')
    manifest = dict(schema_version=1, project=data['title'], default_voice=chosen_voice,
                    aspect_ratio=data.get('aspect_ratio', '16:9'),
                    mode='silent-preview' if silent else ('local-audio' if audio_dir else 'edge-tts'),
                    silent=bool(silent), scenes={})
    # Each run uses a distinct audio directory, so a failed rerun cannot corrupt
    # clips referenced by the last successful manifest. The manifest is written
    # atomically at the end, so a provider failure leaves the previous manifest
    # usable and the error stays loud in main().
    clip_dir = Path(tempfile.mkdtemp(prefix='clips-', dir=output_dir)) if not silent and not audio_dir else output_dir
    for scene in data['scenes']:
        cues = []
        for cue in scene['narration_cues']:
            cid = cue['cue_id']
            if silent:
                # Honest preview: authored durations only, no speech, no network.
                if 'duration' not in cue:
                    raise ValueError('Silent previews require an explicit duration for each cue')
                result = dict(text=cue['text'], audio_file=None, duration=cue['duration'])
            elif audio_dir:
                path = Path(audio_dir) / f"{scene['id']}_{cid}.mp3"
                if not path.is_file():
                    raise FileNotFoundError(
                        f"Missing local clip {scene['id']}_{cid}.mp3 at {path}; "
                        'record or place every SceneID_cue-id.mp3 before using --audio-dir.')
                result = dict(text=cue['text'], audio_file=str(path.resolve()), duration=audio_duration(path))
            else:
                # Only the storyboard cue text is synthesized; learner records
                # are never read here and never sent to the provider.
                cue_voice = cue.get('voice', chosen_voice)
                result = await synthesize_clip(cue['text'], clip_dir / f"{scene['id']}_{cid}.mp3",
                                               VOICE_PRESETS.get(cue_voice, cue_voice), rate)
            result.update(cue_id=cid, sync_target=cue.get('sync_target', ''), pause_after=cue.get('pause_after', 0))
            cues.append(result)
        manifest['scenes'][scene['id']] = dict(title=scene.get('title', scene['id']), cues=cues,
            total_duration=sum(c['duration'] + c['pause_after'] for c in cues))
    target = output_dir / 'timing_manifest.json'
    fd, temporary = tempfile.mkstemp(suffix='.json', dir=output_dir)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(manifest, stream, indent=2)
        os.replace(temporary, target)
    finally:
        Path(temporary).unlink(missing_ok=True)
    # Feed measured (or authored silent) durations back to preview subtitles
    # from the same cue timings stored in the manifest. These planned starts
    # include pause_after; the rendered SRT from CuePlayer.finish() records
    # actual scene.time starts and is authoritative for the video.
    for scene_id, entry in manifest['scenes'].items():
        (output_dir / f'{scene_id}.srt').write_text(preview_srt_lines(entry['cues']))
    print(target.resolve())
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument('--storyboard', '-s', type=Path, help='Storyboard JSON; only its cue text is synthesized')
    source.add_argument('--text', '-t')
    parser.add_argument('--out', '-o', type=Path, default=Path('audio_out'))
    parser.add_argument('--voice', '-v')
    parser.add_argument('--rate', '-r', default='+0%')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--silent', action='store_true',
                      help='Offline preview: authored durations, audio_file null, mode silent-preview, no network')
    mode.add_argument('--audio-dir', type=Path,
                      help='Offline local clips named SceneID_cue-id.mp3; durations are measured, missing files fail loudly')
    parser.add_argument('--list-voices', action='store_true')
    args = parser.parse_args()
    try:
        if args.list_voices:
            print(json.dumps(VOICE_PRESETS, indent=2))
        elif args.storyboard:
            asyncio.run(process_storyboard(args.storyboard, args.out, args.voice, args.rate, args.silent, args.audio_dir))
        elif args.text:
            if args.silent or args.audio_dir:
                raise ValueError('--silent and --audio-dir require --storyboard')
            path = args.out if args.out.suffix else args.out / 'voiceover.mp3'
            result = asyncio.run(synthesize_clip(args.text, path, VOICE_PRESETS.get(args.voice, args.voice) or DEFAULT_VOICE, args.rate))
            print(json.dumps(result, indent=2))
        else:
            parser.error('Supply --storyboard, --text, or --list-voices')
    except Exception as exc:
        parser.exit(1, f'Voice generation failed: {exc}\n')


if __name__ == '__main__':
    main()
