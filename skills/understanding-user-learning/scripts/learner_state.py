#!/usr/bin/env python3
"""Private local learner records with atomic updates and evidence-derived summaries."""
import argparse
from contextlib import contextmanager
from datetime import date
import json
import os
from pathlib import Path
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]


def slug(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', value) or len(value) > 80:
        raise ValueError('Expected a lowercase slug of at most 80 characters')
    return value


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label} must be nonempty text')


def strings(value, label):
    if not isinstance(value, list):
        raise ValueError(f'{label} must be a list')
    for item in value:
        nonempty(item, label)


def validate_event(event):
    if not isinstance(event, dict):
        raise ValueError('Event must be an object')
    slug(event.get('id'))
    slug(event.get('course_id'))
    when = event.get('date')
    if not isinstance(when, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', when):
        raise ValueError('Event date must be YYYY-MM-DD')
    if date.fromisoformat(when) > date.today():
        raise ValueError('Event date cannot be in the future')
    strings(event.get('covered'), 'covered')
    for concept in event['covered']:
        validate_concept(concept)
    nonempty(event.get('next_step'), 'next_step')
    if not isinstance(event.get('interpretation'), str):
        raise ValueError('interpretation must be text (may be empty)')
    attempts = event.get('attempts')
    if not isinstance(attempts, list):
        raise ValueError('attempts must be a list')
    for attempt in attempts:
        if not isinstance(attempt, dict):
            raise ValueError('Attempt must be an object')
        validate_concept(attempt.get('concept'))
        for field in ('task', 'response'):
            nonempty(attempt.get(field), field)
        for field, choices in [('result', ('correct', 'partial', 'incorrect')),
                               ('help', ('none', 'hint', 'worked-example')),
                               ('kind', ('application', 'retrieval', 'transfer'))]:
            if attempt.get(field) not in choices:
                raise ValueError(f'{field} must be one of {choices}')
    return event


def validate_concept(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-z][a-z0-9-]*\.[a-z0-9]+(?:[.-][a-z0-9]+)*', value):
        raise ValueError(f'Invalid concept ID: {value!r}')


def state_path(root, learner):
    slug(learner)
    root = Path(root).resolve()
    folder = root / learner
    path = folder / 'state.json'
    if folder.is_symlink() or path.is_symlink():
        raise ValueError('Learner directories and state files cannot be symbolic links')
    return path


def read_state(root, learner):
    path = state_path(root, learner)
    if not path.exists():
        raise FileNotFoundError(f'No record for {learner}; initialize or record a session first')
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or data.get('schema_version') != 1 or data.get('learner_id') != learner:
        raise ValueError('State version or learner ID mismatch')
    if not isinstance(data.get('profile'), dict) or not isinstance(data.get('events'), list):
        raise ValueError('Malformed learner state')
    ids = set()
    for event in data['events']:
        validate_event(event)
        if event['id'] in ids:
            raise ValueError('Duplicate event IDs in saved state')
        ids.add(event['id'])
    return data


@contextmanager
def locked(root, learner):
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = root / f'.{slug(learner)}.lock'
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError(f'Record is locked: {lock}; inspect the active writer before retrying')
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(str(os.getpid()))
        yield
    finally:
        lock.unlink()


def save_state(path, data):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, name = tempfile.mkstemp(prefix='.state-', suffix='.json', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(data, stream, indent=2, ensure_ascii=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def summarize(data):
    concepts = {}
    events = sorted(data['events'], key=lambda e: e['date'])
    history = {}
    for event in events:
        for concept in event['covered']:
            concepts.setdefault(concept, dict(status='exposed', attempts=0))
        for attempt in event['attempts']:
            concept = attempt['concept']
            entry = concepts.setdefault(concept, dict(status='exposed', attempts=0))
            entry['attempts'] += 1
            success = attempt['result'] == 'correct' and attempt['help'] == 'none'
            earlier_success = any(day < event['date'] for day in history.get(concept, []))
            status = 'practicing'
            if success:
                status = 'retained' if earlier_success and attempt['kind'] in ('retrieval', 'transfer') else 'demonstrated'
                history.setdefault(concept, []).append(event['date'])
            entry.update(status=status, last_date=event['date'], latest=attempt)
    latest_event = events[-1] if events else None
    return dict(learner_id=data['learner_id'], profile=data['profile'],
                session_count=len(events), concepts=concepts,
                latest_event=latest_event,
                next_step=latest_event['next_step'] if latest_event else None)


def mutate(root, learner, command, payload=None):
    path = state_path(root, learner)
    with locked(root, learner):
        data = read_state(root, learner) if path.exists() else dict(
            schema_version=1, learner_id=learner, profile={}, events=[])
        if command == 'record':
            validate_event(payload)
            previous = next((e for e in data['events'] if e['id'] == payload['id']), None)
            if previous is not None:
                if previous != payload:
                    raise ValueError('Event ID already exists with different content')
                return 'Already recorded; unchanged'
            data['events'].append(payload)
        elif command == 'profile':
            if not isinstance(payload, dict) or set(payload) - {'goals', 'preferences'}:
                raise ValueError('Profile accepts only goals and preferences lists')
            for key, value in payload.items():
                strings(value, key)
            data['profile'] = dict(payload, updated_at=date.today().isoformat())
        elif command == 'retract':
            if not any(e['id'] == payload for e in data['events']):
                raise ValueError('No event with that ID')
            data['events'] = [e for e in data['events'] if e['id'] != payload]
        elif command == 'delete':
            if not path.exists():
                raise ValueError('No learner record to delete')
            path.unlink()
            try:
                path.parent.rmdir()
            except OSError:
                pass  # Other files belong to the user; erase only our state.
            return 'Learner state deleted'
        elif command == 'init' and path.exists():
            return 'Already initialized; unchanged'
        save_state(path, data)
        return f'Saved {path}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT / 'learners')
    commands = parser.add_subparsers(dest='command', required=True)
    for command in ('init', 'summary', 'record', 'profile', 'retract', 'delete'):
        sub = commands.add_parser(command)
        sub.add_argument('learner')
        if command == 'record':
            sub.add_argument('--event', type=Path, required=True)
        if command == 'profile':
            sub.add_argument('--file', type=Path, required=True)
        if command == 'retract':
            sub.add_argument('--event-id', required=True)
    args = parser.parse_args()
    try:
        if args.command == 'summary':
            print(json.dumps(summarize(read_state(args.root, args.learner)), indent=2, ensure_ascii=False))
            return
        payload = None
        if args.command in ('record', 'profile'):
            source = args.event if args.command == 'record' else args.file
            payload = json.loads(source.read_text())
        elif args.command == 'retract':
            payload = args.event_id
        print(mutate(args.root, args.learner, args.command, payload))
    except (OSError, ValueError) as exc:
        parser.exit(1, f'Learner record error: {exc}\n')


if __name__ == '__main__':
    main()
