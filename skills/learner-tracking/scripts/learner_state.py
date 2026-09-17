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


def _course_contract():
    sys.path.insert(0, str(ROOT / 'skills/course-design/scripts'))
    from course_contract import course_fingerprint, validate_course
    return course_fingerprint, validate_course


def _course_workspace():
    sys.path.insert(0, str(ROOT / 'skills/course-design/scripts'))
    from course_workspace import create_workspace, read_plan, workspace_path, write_plan
    return create_workspace, read_plan, workspace_path, write_plan


def _course_progress():
    sys.path.insert(0, str(ROOT / 'skills/course-design/scripts'))
    from course_progress import derive_course_progress
    return derive_course_progress


def _validate_enrollment(course_id, entry):
    if not isinstance(entry, dict) or entry.get('status') not in ('active', 'completed'):
        raise ValueError('Invalid saved course status')
    if not isinstance(entry.get('completion_history', []), list):
        raise ValueError('completion_history must be a list')
    if 'plan' in entry:
        _, validate_course = _course_contract()
        plan = validate_course(entry.get('plan'))
        if plan['id'] != course_id:
            raise ValueError('Saved course ID mismatch')
        return
    reference = entry.get('plan_ref')
    match = re.fullmatch(r'courses/([a-z0-9]+(?:-[a-z0-9]+)*)/course\.json', reference or '')
    if not match or match.group(1) != course_id:
        raise ValueError('Invalid saved course plan reference')
    revision = entry.get('plan_revision')
    if type(revision) is not int or revision < 1:
        raise ValueError('Invalid saved course plan revision')
    fingerprint = entry.get('plan_fingerprint')
    if not isinstance(fingerprint, str) or not re.fullmatch(r'[0-9a-f]{64}', fingerprint):
        raise ValueError('Invalid saved course plan fingerprint')


def resolve_enrolled_plan(learners_root: Path, learner_id: str, entry: dict) -> dict:
    """Read the canonical plan named by an enrollment and verify its snapshot."""
    _, validate_course = _course_contract()
    if not isinstance(entry, dict):
        raise ValueError('Enrollment must be an object')
    if 'plan' in entry:
        return validate_course(entry['plan'])
    reference = entry.get('plan_ref', '')
    match = re.fullmatch(r'courses/([a-z0-9]+(?:-[a-z0-9]+)*)/course\.json', reference)
    if not match:
        raise ValueError(f'Invalid enrolled course plan reference: {reference!r}')
    course_id = match.group(1)
    if learners_root is None or learner_id is None:
        raise ValueError('Resolving a referenced course plan requires learners_root and learner_id')
    _, read_plan, workspace_path, _ = _course_workspace()
    try:
        plan = read_plan(workspace_path(Path(learners_root), learner_id, course_id))
    except FileNotFoundError as exc:
        raise ValueError(
            f"Stale course plan reference for {course_id!r}: canonical plan is missing"
        ) from exc
    if plan['id'] != course_id:
        raise ValueError(f"Canonical course plan ID mismatch for {course_id!r}")
    actual = _course_contract()[0](plan)
    expected = entry.get('plan_fingerprint')
    if actual != expected or plan['revision'] != entry.get('plan_revision'):
        raise ValueError(
            f"Stale course plan reference for {course_id!r}: "
            f"enrollment expects revision {entry.get('plan_revision')} / {expected}, "
            f"canonical plan is revision {plan['revision']} / {actual}"
        )
    return plan


def resolve_all_enrolled_plans(learners_root: Path, learner_id: str, data: dict) -> dict:
    """Resolve every enrollment before a mutation can be persisted or rendered."""
    courses = data.get('courses', {})
    if not isinstance(courses, dict):
        raise ValueError('courses must be an object')
    plans = {}
    for course_id, entry in courses.items():
        slug(course_id)
        _validate_enrollment(course_id, entry)
        plans[course_id] = resolve_enrolled_plan(learners_root, learner_id, entry)
    return plans


def read_state(root, learner):
    path = state_path(root, learner)
    if not path.exists():
        raise FileNotFoundError(f'No record for {learner}; initialize or record a session first')
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or data.get('schema_version') != 1 or data.get('learner_id') != learner:
        raise ValueError('State version or learner ID mismatch')
    if not isinstance(data.get('profile'), dict) or not isinstance(data.get('events'), list):
        raise ValueError('Malformed learner state')
    courses = data.get('courses', {})
    if not isinstance(courses, dict):
        raise ValueError('courses must be an object')
    if courses:
        sys.path.insert(0, str(ROOT / 'skills/course-design/scripts'))
        for id_, course in courses.items():
            slug(id_)
            _validate_enrollment(id_, course)
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


def summarize(data, course_id=None, learners_root=None, learner_id=None, resolved_plans=None):
    concepts = {}
    events = sorted([e for e in data['events'] if course_id is None or e['course_id'] == course_id], key=lambda e: e['date'])
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
    courses = {}
    for id_, entry in data.get('courses', {}).items():
        plan = (resolved_plans[id_] if resolved_plans is not None
                else resolve_enrolled_plan(learners_root, learner_id, entry))
        courses[id_] = dict(title=plan['title'], status=entry['status'], revision=plan['revision'])
    next_step = latest_event['next_step'] if latest_event else None
    if latest_event and courses.get(latest_event['course_id'], {}).get('status') == 'completed':
        next_step = 'Course completed. Use its curriculum to choose a review target or agree the next goal.'
    result = dict(learner_id=data['learner_id'], profile=data['profile'],
                  session_count=len(events), concepts=concepts, courses=courses,
                  latest_event=latest_event,
                  next_step=next_step)
    if course_id is not None and course_id in courses:
        plan = (resolved_plans[course_id] if resolved_plans is not None
                else resolve_enrolled_plan(learners_root, learner_id,
                                           data['courses'][course_id]))
        result['course_progress'] = _course_progress()(plan, events)
    return result


def record_event(root, learner, event):
    """Record evidence only for a learner's enrolled, canonical course.

    The ordinary ``mutate(..., 'record', ...)`` command remains useful for
    importing historical sessions.  Portal evidence is stricter: it must be
    attached to an enrollment whose canonical plan still matches its saved
    revision and fingerprint before the event is persisted.
    """
    data = read_state(root, learner)
    course_id = event.get('course_id') if isinstance(event, dict) else None
    courses = data.get('courses', {})
    if course_id not in courses:
        raise ValueError(f'Learner {learner!r} is not enrolled in course {course_id!r}')
    resolve_enrolled_plan(root, learner, courses[course_id])
    return mutate(root, learner, 'record', event)


def _prepare_views(path, root, learner, data):
    plans = resolve_all_enrolled_plans(root, learner, data)
    summary = summarize(data, learners_root=root, learner_id=learner,
                        resolved_plans=plans)
    from memory_views import build_views
    rendered = build_views(path, data, summary, plans=plans)
    return plans, summary, rendered


def mutate(root, learner, command, payload=None):
    path = state_path(root, learner)
    with locked(root, learner):
        data = read_state(root, learner) if path.exists() else dict(
            schema_version=1, learner_id=learner, profile={}, courses={}, events=[])
        if command not in ('delete', 'migrate-courses'):
            resolve_all_enrolled_plans(root, learner, data)
        if command == 'enroll':
            course_fingerprint, validate_course = _course_contract()
            create_workspace, _, workspace_path, write_plan = _course_workspace()
            plan = validate_course(payload)
            previous = data.setdefault('courses', {}).get(plan['id'])
            if previous:
                previous_plan = (validate_course(previous['plan']) if 'plan' in previous
                                 else resolve_enrolled_plan(root, learner, previous))
                previous_fingerprint = course_fingerprint(previous_plan)
                if previous_fingerprint != course_fingerprint(plan) and plan['revision'] <= previous_plan['revision']:
                    raise ValueError('A changed course plan requires a higher revision')
                if previous_fingerprint == course_fingerprint(plan) and 'plan' not in previous:
                    return 'Already enrolled; unchanged'
            else:
                previous_plan = None
            # The canonical workspace must exist before the state can refer to it.
            if previous and previous_plan and previous_fingerprint != course_fingerprint(plan):
                workspace = workspace_path(root, learner, plan['id'])
                if (workspace / 'course.json').exists():
                    write_plan(workspace, plan, expected_fingerprint=previous_fingerprint)
                else:
                    create_workspace(root, learner, plan)
            else:
                create_workspace(root, learner, plan)
            completions = list(previous.get('completion_history', [])) if previous else []
            if previous and previous.get('completed_at'):
                completions.append(dict(revision=previous_plan['revision'], completed_at=previous['completed_at']))
            status = previous.get('status', 'active') if previous and previous_plan and previous_plan == plan else 'active'
            entry = dict(status=status,
                         plan_ref=f"courses/{plan['id']}/course.json",
                         plan_revision=plan['revision'],
                         plan_fingerprint=course_fingerprint(plan),
                         completion_history=completions)
            if status == 'completed' and previous and previous.get('completed_at'):
                entry['completed_at'] = previous['completed_at']
            data['courses'][plan['id']] = entry
        elif command == 'migrate-courses':
            course_fingerprint, validate_course = _course_contract()
            create_workspace, _, _, _ = _course_workspace()
            migrations = {}
            for course_id, old in data.get('courses', {}).items():
                if 'plan' not in old:
                    continue
                plan = validate_course(old['plan'])
                if plan['id'] != course_id:
                    raise ValueError('Saved course ID mismatch')
                # Workspace creation is deliberately completed for every plan before
                # the state snapshot is replaced with references.
                create_workspace(root, learner, plan)
                entry = dict(status=old['status'],
                             plan_ref=f"courses/{plan['id']}/course.json",
                             plan_revision=plan['revision'],
                             plan_fingerprint=course_fingerprint(plan),
                             completion_history=list(old.get('completion_history', [])))
                if old.get('completed_at'):
                    entry['completed_at'] = old['completed_at']
                migrations[course_id] = entry
            if migrations:
                data['courses'].update(migrations)
            else:
                return 'No course migrations needed; unchanged'
        elif command == 'complete-course':
            if payload not in data.get('courses', {}):
                raise ValueError('Enroll the course before completing it')
            resolve_enrolled_plan(root, learner, data['courses'][payload])
            data['courses'][payload]['status'] = 'completed'
            data['courses'][payload]['completed_at'] = date.today().isoformat()
        elif command == 'record':
            validate_event(payload)
            previous = next((e for e in data['events'] if e['id'] == payload['id']), None)
            if previous is not None:
                if previous != payload:
                    raise ValueError('Event ID already exists with different content')
                from memory_views import write_views
                plans, summary, rendered = _prepare_views(path, root, learner, data)
                write_views(path, data, summary, plans=plans, rendered=rendered)
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
            from memory_views import delete_views
            delete_views(path, data)
            path.unlink()
            try:
                path.parent.rmdir()
            except OSError:
                pass  # Other files belong to the user; erase only our state.
            return 'Learner state deleted'
        elif command == 'init' and path.exists():
            return 'Already initialized; unchanged'
        plans, summary, rendered = _prepare_views(path, root, learner, data)
        save_state(path, data)
        from memory_views import write_views
        write_views(path, data, summary, plans=plans, rendered=rendered)
        return f'Saved {path}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT / 'learners')
    commands = parser.add_subparsers(dest='command', required=True)
    for command in ('init', 'summary', 'record', 'profile', 'retract', 'delete', 'enroll', 'complete-course', 'migrate-courses'):
        sub = commands.add_parser(command)
        sub.add_argument('learner', nargs='?', default='learner',
                         help='Learner folder name; defaults to %(default)s when no name is given')
        if command == 'summary':
            sub.add_argument('--course-id')
        if command == 'record':
            sub.add_argument('--event', type=Path, required=True)
        if command == 'profile':
            sub.add_argument('--file', type=Path, required=True)
        if command == 'enroll':
            sub.add_argument('--course', type=Path, required=True)
        if command == 'complete-course':
            sub.add_argument('--course-id', required=True)
        if command == 'retract':
            sub.add_argument('--event-id', required=True)
    args = parser.parse_args()
    try:
        if args.command == 'summary':
            print(json.dumps(summarize(read_state(args.root, args.learner), args.course_id,
                                       learners_root=args.root, learner_id=args.learner),
                             indent=2, ensure_ascii=False))
            return
        payload = None
        if args.command in ('record', 'profile'):
            source = args.event if args.command == 'record' else args.file
            payload = json.loads(source.read_text())
        elif args.command == 'enroll':
            payload = json.loads(args.course.read_text())
        elif args.command == 'complete-course':
            payload = args.course_id
        elif args.command == 'retract':
            payload = args.event_id
        print(mutate(args.root, args.learner, args.command, payload))
    except (OSError, ValueError) as exc:
        parser.exit(1, f'Learner record error: {exc}\n')


if __name__ == '__main__':
    main()
