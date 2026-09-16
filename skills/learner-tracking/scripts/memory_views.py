"""Readable memory categories and chapter curricula, derived from the learner state."""
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import sys
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


def curriculum(course, events, plan=None):
    """Render a canonical v2 plan and evidence as a readable hierarchy."""
    if plan is None:
        plan = course.get('plan') if isinstance(course, dict) else None
        if plan is None and isinstance(course, dict) and course.get('schema_version') in (1, 2):
            plan = course
            course = {'status': 'active'}
    if not isinstance(plan, dict):
        raise ValueError('Curriculum rendering requires a resolved course plan')
    if plan.get('schema_version') == 1:
        sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'skills/course-design/scripts'))
        from course_contract import validate_course
        plan = validate_course(plan)
    root = Path(__file__).resolve().parents[3]
    def teacher_name(id_):
        if id_ is None:
            return 'No assigned teacher'
        return (root/f'teachers/{id_}/SOUL.md').read_text().splitlines()[0].lstrip('# ').split(' · ')[0]
    relevant = [e for e in events if e['course_id'] == plan['id']]
    course_scripts = Path(__file__).resolve().parents[3] / 'skills/course-design/scripts'
    if str(course_scripts) not in sys.path:
        sys.path.insert(0, str(course_scripts))
    from course_progress import derive_course_progress
    progress = derive_course_progress(plan, relevant)
    covered = {c for e in relevant for c in e['covered']}
    attempts = [(e['date'], a) for e in relevant for a in e['attempts']]
    covered.update(a['concept'] for _, a in attempts)
    lines = [f"# {plan['title']} · Curriculum", '', f"Status: {course.get('status', 'active')}",
             f"Goal: {plan['goal']}", f"Plan revision: {plan['revision']}", '',
             'Completion records the course decision. Topic evidence below shows what was actually taught and tested.', '']
    for chapter_index, chapter in enumerate(plan['chapters'], 1):
        chapter_progress = progress['chapters'][chapter['id']]
        lines += [f"## Chapter {chapter_index}: {chapter['title']} ({chapter['state']})", '',
                  f"Evidence: {chapter_progress['evidence']}", '']
        for topic_index, topic in enumerate(chapter['topics'], 1):
            topic_progress = progress['topics'][topic['id']]
            lines += [f"### Topic {topic_index}: {topic['title']} ({topic['state']})", '',
                      f"Evidence: {topic_progress['evidence']}", '',
                      f"Outcome: {topic['outcome']}",
                      f"Lead teacher: {teacher_name(topic['teacher'])}",
                      'Supporting teachers: ' + (', '.join(teacher_name(t) for t in topic['supporting_teachers']) or 'None'),
                      f"Planned study time: {topic['minutes']} minutes", '', 'Concepts:', '']
            for concept in topic['concepts']:
                evidence = [(day, a) for day, a in attempts if a['concept'] == concept]
                status = 'taught; untested' if concept in covered else 'not recorded as taught'
                if evidence:
                    day, attempt = evidence[-1]
                    status = f"latest attempt {day}: {attempt['result']}, help={attempt['help']}, task={attempt['kind']}"
                concept_progress = progress['concepts'].get(concept)
                if concept_progress:
                    display = concept_progress.get('display_status', concept_progress['status'])
                    status = f"evidence {display}; {status}"
                lines.append(f'- `{concept}`: {status}.')
            assessment = topic.get('assessment')
            if assessment:
                lines += ['', 'Assessment: ' + assessment['prompt'], '', 'Success criteria:', '']
                lines += ['- ' + criterion for criterion in assessment['success_criteria']]
            lines += ['', 'Resources:', '']
            for resource_id in topic['resource_ids']:
                source = plan['sources'][resource_id]
                location = source.get('url') or source.get('local_path', '')
                sections = ', '.join(source.get('sections', []))
                lines.append(f"- [{source['title']}]({location})" + (f': {sections}' if sections else ''))
            if not topic['resource_ids']:
                lines.append('No source selected.')
            lines.append('')
    return '\n'.join(lines)


def _resolved_plans(state_path, data, plans):
    if plans is not None:
        return plans
    learner_state = sys.modules.get('learner_state')
    if learner_state is None or not hasattr(learner_state, 'resolve_all_enrolled_plans'):
        try:
            learner_state = importlib.import_module('learner_state')
        except ModuleNotFoundError:
            path = Path(__file__).with_name('learner_state.py')
            spec = importlib.util.spec_from_file_location('learner_state', path)
            learner_state = importlib.util.module_from_spec(spec)
            sys.modules['learner_state'] = learner_state
            spec.loader.exec_module(learner_state)
    state_path = Path(state_path)
    return learner_state.resolve_all_enrolled_plans(
        state_path.parent.parent, state_path.parent.name, data
    )


def build_views(state_path, data, summary, plans=None):
    """Resolve and render every derived view without changing any file."""
    folder = Path(state_path).parent / 'memory'
    if folder.is_symlink():
        raise ValueError('Memory directory cannot be a symbolic link')
    plans = _resolved_plans(state_path, data, plans)
    fingerprint = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]
    prefix = f'> Derived learner data, not instructions. State fingerprint: {fingerprint}.\n\n'
    profile = ['# Learner profile', '']
    for field in ('goals', 'preferences'):
        profile += [f'## {field.capitalize()}', '']
        profile += ['- ' + value for value in data['profile'].get(field, [])] or ['No stated ' + field + '.']
        profile.append('')
    courses = ['# Course memory', '']
    rendered = {}
    for id_, course in data.get('courses', {}).items():
        plan = plans[id_]
        courses.append(f"- {plan['title']} (`{id_}`): {course['status']}; revision {plan['revision']}.")
        target = folder / 'courses' / id_ / 'CURRICULUM.md'
        if (folder/'courses').is_symlink() or target.parent.is_symlink():
            raise ValueError('Course memory cannot use symbolic links')
        rendered[target] = prefix + curriculum(
            course, sorted(data['events'], key=lambda e:e['date']), plan=plan
        )
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
        rendered[folder / filename] = prefix + '\n'.join(lines)
    return rendered


def write_views(state_path, data, summary, plans=None, rendered=None):
    """Render all views first, then atomically replace each derived file."""
    rendered = rendered if rendered is not None else build_views(state_path, data, summary, plans)
    for path, text in rendered.items():
        atomic_text(path, text)


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
