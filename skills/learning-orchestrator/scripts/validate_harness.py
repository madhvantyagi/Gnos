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


def validate_cursor(errors):
    plugin_path = ROOT / '.cursor-plugin' / 'plugin.json'
    market_path = ROOT / '.cursor-plugin' / 'marketplace.json'
    try:
        plugin = json.loads(plugin_path.read_text())
        market = json.loads(market_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f'Cursor plugin manifest: {exc}')
        return
    if plugin.get('name') != 'gnos':
        errors.append('.cursor-plugin/plugin.json: name must be gnos')
    for field in ('skills', 'mcpServers', 'logo'):
        rel = plugin.get(field)
        if not isinstance(rel, str) or not (ROOT / rel).exists():
            errors.append(f'.cursor-plugin/plugin.json: missing {field} path {rel}')
    entries = market.get('plugins') or []
    if market.get('name') != 'gnos' or [entry.get('name') for entry in entries] != ['gnos']:
        errors.append('.cursor-plugin/marketplace.json: expected the gnos plugin')
    elif entries[0].get('source') != '.':
        errors.append('.cursor-plugin/marketplace.json: source must be the repository root')
    try:
        shared = json.loads((ROOT / '.mcp.json').read_text())
        cursor_mcp = json.loads((ROOT / '.cursor' / 'mcp.json').read_text())
        if cursor_mcp != shared:
            errors.append('.cursor/mcp.json must match .mcp.json')
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f'.cursor/mcp.json: {exc}')
    skills = ROOT / '.cursor' / 'skills'
    if not skills.is_symlink() or skills.resolve() != (ROOT / 'skills').resolve():
        errors.append('.cursor/skills must symlink to ../skills')


def validate():
    errors = []
    skills = sorted((ROOT / 'skills').glob('*/SKILL.md'))
    expected = ('course-design', 'course-viewer', 'excalidraw', 'jsxgraph', 'khan-academy', 'learner-tracking',
                'learning-orchestrator', 'lesson-design', 'manim-voice-animation',
                'pdf', 'pinepaper', 'subject')
    found = {path.parent.name for path in skills}
    # A compatibility entry may route older invocations to the orchestrator.
    optional = {'learning'}
    if set(expected) - found or found - set(expected) - optional:
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
    for required in (
        ('skills/learning-orchestrator/SKILL.md', 'Do you want to see the course now?'),
        ('skills/course-design/SKILL.md', 'Do you want to see the course now?'),
        ('skills/course-design/SKILL.md', 'Do not stop at'),
        ('skills/course-viewer/SKILL.md', '--outline-only'),
        ('skills/learner-tracking/SKILL.md', 'Never render lessons, viewer pages'),
        ('skills/lesson-design/SKILL.md', 'Choose the block type while drafting'),
        ('skills/lesson-design/SKILL.md', 'Only the coordinator'),
    ):
        path = ROOT / required[0]
        if path.is_file() and required[1] not in path.read_text():
            errors.append(f'{required[0]}: missing required workflow sentence')
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
    validate_cursor(errors)
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'Validated {len(skills)} skills, {len(SUBJECTS)} subjects, {len(TEACHERS)} teachers, '
          'links, Python syntax, version-2 courses, and composed lessons.')
    return 0


if __name__ == '__main__':
    raise SystemExit(validate())
