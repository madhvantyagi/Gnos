#!/usr/bin/env python3
"""Check GNOS's skill entry points, local links, Python syntax, and example courses."""
import ast
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'skills/course-design/scripts'))
from course_contract import SUBJECTS, TEACHERS, validate_course
from lesson_contract import validate_lesson


def validate():
    errors = []
    skills = sorted((ROOT / 'skills').glob('*/SKILL.md'))
    expected = ('course-design', 'course-viewer', 'image-gen', 'learner-tracking',
                'learning-orchestrator', 'manim-voice-animation', 'pdf', 'subject')
    if [path.parent.name for path in skills] != sorted(expected):
        found = [path.parent.name for path in skills]
        errors.append(f'Expected skills {sorted(expected)}; found {sorted(found)}')
    for path in skills:
        text = path.read_text()
        parts = text.split('---', 2)
        if len(parts) < 3 or parts[0].strip():
            errors.append(f'{path.relative_to(ROOT)}: missing YAML frontmatter')
        elif not all(re.search(rf'^{field}:\s*\S', parts[1], re.M) for field in ('name', 'description')):
            errors.append(f'{path.relative_to(ROOT)}: missing skill name/description')
        else:
            name = re.search(r'^name:\s*(\S+)', parts[1], re.M)
            if not name or name.group(1) != path.parent.name:
                errors.append(f'{path.relative_to(ROOT)}: frontmatter name must match folder')
    for subject in SUBJECTS:
        path = ROOT / f'skills/subject/subjects/{subject}.md'
        if not path.is_file():
            errors.append(f'Missing {path.relative_to(ROOT)}')
    for teacher in TEACHERS:
        path = ROOT / f'teachers/{teacher}/SOUL.md'
        if not path.is_file():
            errors.append(f'Missing {path.relative_to(ROOT)}')
    documents = [ROOT/'README.md', ROOT/'AGENTS.md'] + list((ROOT/'skills').rglob('*.md'))
    for path in documents:
        for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)', path.read_text()):
            target = target.split(' "')[0].strip('<>')
            if urlparse(target).scheme or target.startswith('#') or '<' in target:
                continue
            target = unquote(target.split('#')[0])
            if target and not (path.parent / target).exists():
                errors.append(f'{path.relative_to(ROOT)}: missing local link {target}')
    for folder in ('skills', 'examples', 'tests'):
        for path in (ROOT / folder).rglob('*.py'):
            try: ast.parse(path.read_text(), filename=str(path))
            except SyntaxError as exc: errors.append(f'{path.relative_to(ROOT)}: {exc}')
    for path in (ROOT/'examples/courses').glob('*/course.json'):
        try:
            raw_course = json.loads(path.read_text())
            plan = validate_course(raw_course)
            if raw_course.get('schema_version') != 2 or plan['schema_version'] != 2:
                errors.append(f'{path.relative_to(ROOT)}: example must use schema version 2')
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f'{path.relative_to(ROOT)}: {exc}')
    for path in (ROOT/'examples/courses').glob('*/lessons/*.json'):
        try:
            course_path = path.parents[1] / 'course.json'
            plan = validate_course(json.loads(course_path.read_text()))
            validate_lesson(json.loads(path.read_text()), plan)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f'{path.relative_to(ROOT)}: {exc}')
    if (ROOT/'scripts').exists():
        errors.append('Scripts must live inside their owning skill; root scripts/ exists')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'Validated {len(skills)} skills, {len(SUBJECTS)} subjects, {len(TEACHERS)} teachers, '
          'links, Python syntax, version-2 courses, and composed lessons.')
    return 0


if __name__ == '__main__':
    raise SystemExit(validate())
