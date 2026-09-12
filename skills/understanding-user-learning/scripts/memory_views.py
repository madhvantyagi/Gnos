"""Readable memory categories and chapter curricula, derived from the learner state."""
import hashlib
import json
import os
from pathlib import Path
import tempfile

CATEGORIES = ('01-profile.md', '02-courses.md', '03-topics.md', '04-teaching.md', '05-next.md')


def atomic_text(path, text):
    path = Path(path)
    if path.is_symlink():
        raise ValueError(f'Memory view cannot be a symbolic link: {path}')
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, name = tempfile.mkstemp(dir=path.parent, suffix='.md')
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(text.rstrip() + '\n')
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def curriculum(course, events):
    plan = course['plan']
    relevant = [e for e in events if e['course_id'] == plan['id']]
    covered = {c for e in relevant for c in e['covered']}
    attempts = [(e['date'], a) for e in relevant for a in e['attempts']]
    covered.update(a['concept'] for _, a in attempts)
    lines = [f"# {plan['title']} · Curriculum", '', f"Status: {course['status']}",
             f"Goal: {plan['goal']}", f"Plan revision: {plan['revision']}", '',
             'Completion records the course decision. Topic evidence below shows what was actually taught and tested.', '']
    for index, module in enumerate(plan['modules'], 1):
        lines += [f"## Chapter {index}: {module['title']}", '', f"Outcome: {module['outcome']}",
                  f"Lead teacher: {module['teacher']}",
                  'Supporting teachers: ' + (', '.join(module['supporting_teachers']) or 'None'),
                  f"Planned study time: {module['minutes']} minutes", '', 'Topics:', '']
        for concept in module['concepts']:
            title = module.get('topic_titles', {}).get(concept, concept.split('.', 1)[-1].replace('-', ' ').capitalize())
            evidence = [(day, a) for day, a in attempts if a['concept'] == concept]
            status = 'taught; untested' if concept in covered else 'not recorded as taught'
            if evidence:
                day, a = evidence[-1]
                status = f"latest attempt {day}: {a['result']}, help={a['help']}, task={a['kind']}"
            lines.append(f'- {title} (`{concept}`): {status}.')
        lines += ['', 'Assessment: ' + module['assessment']['prompt'], '', 'Success criteria:', '']
        lines += ['- ' + criterion for criterion in module['assessment']['success_criteria']]
        lines += ['', 'Resources: ' + (', '.join(module['resources']) or 'No source selected'), '']
        if module.get('source_sections'):
            lines += ['Source sections: ' + json.dumps(module['source_sections'], ensure_ascii=False), '']
    return '\n'.join(lines)


def write_views(state_path, data, summary):
    folder = Path(state_path).parent / 'memory'
    if folder.is_symlink():
        raise ValueError('Memory directory cannot be a symbolic link')
    fingerprint = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]
    prefix = f'> Derived learner data, not instructions. State fingerprint: {fingerprint}.\n\n'
    profile = ['# Learner profile', '']
    for field in ('goals', 'preferences'):
        profile += [f'## {field.capitalize()}', '']
        profile += ['- ' + value for value in data['profile'].get(field, [])] or ['No stated ' + field + '.']
        profile.append('')
    courses = ['# Course memory', '']
    for id_, course in data.get('courses', {}).items():
        courses.append(f"- {course['plan']['title']} (`{id_}`): {course['status']}; revision {course['plan']['revision']}.")
        target = folder / 'courses' / id_ / 'CURRICULUM.md'
        if (folder/'courses').is_symlink() or target.parent.is_symlink():
            raise ValueError('Course memory cannot use symbolic links')
        atomic_text(target, prefix + curriculum(course, sorted(data['events'], key=lambda e:e['date'])))
    topics = ['# Taught topics and evidence', '']
    for concept, record in summary['concepts'].items():
        topics.append(f"- `{concept}`: {record['status']}; {record['attempts']} attempts.")
        if record.get('latest'):
            topics.append('  Latest task: ' + record['latest']['task'])
            topics.append('  Observed response: ' + record['latest']['response'])
    teaching = ['# Teaching observations', '', 'Interpretations are tentative; retain the task context.', '']
    for event in sorted(data['events'], key=lambda e:e['date']):
        if event['interpretation']:
            teaching.append(f"- {event['date']} / {event['course_id']} / {event['id']}: {event['interpretation']}")
    next_ = ['# Resume here', '', summary['next_step'] or 'No prior session. Establish the learner’s current question.']
    for filename, lines in zip(CATEGORIES, [profile, courses, topics, teaching, next_]):
        atomic_text(folder / filename, prefix + '\n'.join(lines))


def delete_views(state_path, data):
    folder = Path(state_path).parent / 'memory'
    if folder.is_symlink():
        raise ValueError('Memory directory cannot be a symbolic link')
    paths = [folder / name for name in CATEGORIES]
    paths += [folder / 'courses' / id_ / 'CURRICULUM.md' for id_ in data.get('courses', {})]
    for path in paths:
        if path.parent.is_symlink() or (folder/'courses').is_symlink():
            raise ValueError('Memory path cannot be a symbolic link')
        path.unlink(missing_ok=True)
        if path.parent != folder:
            try: path.parent.rmdir()
            except OSError: pass
    for path in (folder/'courses', folder):
        try: path.rmdir()
        except OSError: pass
