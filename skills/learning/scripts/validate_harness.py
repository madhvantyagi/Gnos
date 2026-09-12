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
from course_contract import SUBJECTS, validate_course


def validate():
    errors = []
    skills = sorted((ROOT / 'skills').glob('*/SKILL.md'))
    if len(skills) != 6:
        errors.append(f'Expected six skill entry points; found {len(skills)}')
    for path in skills:
        text = path.read_text()
        parts = text.split('---', 2)
        if len(parts) < 3 or parts[0].strip():
            errors.append(f'{path.relative_to(ROOT)}: missing YAML frontmatter')
        elif not all(re.search(rf'^{field}:\s*\S', parts[1], re.M) for field in ('name', 'description')):
            errors.append(f'{path.relative_to(ROOT)}: missing skill name/description')
    for subject in SUBJECTS:
        for path in [ROOT/f'teachers/{subject}/SOUL.md', ROOT/f'skills/subject/subjects/{subject}.md']:
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
        try: validate_course(json.loads(path.read_text()))
        except (OSError, ValueError) as exc: errors.append(f'{path.relative_to(ROOT)}: {exc}')
    if (ROOT/'scripts').exists():
        errors.append('Scripts must live inside their owning skill; root scripts/ exists')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'Validated {len(skills)} skills, {len(SUBJECTS)} subjects/teachers, links, Python syntax, and example courses.')
    return 0


if __name__ == '__main__':
    raise SystemExit(validate())
