"""Course contracts and source catalog lookup; no third-party dependencies."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
SUBJECTS = ('math', 'physics', 'history', 'biology', 'economics', 'computer-science')


def slug(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', value) or len(value) > 80:
        raise ValueError(f'Expected a lowercase slug of at most 80 characters: {value!r}')
    return value


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label} must be nonempty text')
    return value


def strings(value, label, required=False):
    if not isinstance(value, list) or (required and not value):
        raise ValueError(f'{label} must be a {"nonempty " if required else ""}list')
    for item in value:
        nonempty(item, label)
    return value


def resources():
    return json.loads((ROOT / 'skills/subject/references/resources.json').read_text())


def validate_course(data):
    if not isinstance(data, dict) or data.get('schema_version') != 1:
        raise ValueError('Course requires schema_version 1')
    slug(data.get('id'))
    for key in ('title', 'goal'):
        nonempty(data.get(key), key)
    revision = data.get('revision')
    if type(revision) is not int or revision < 1:
        raise ValueError('revision must be a positive integer')
    strings(data.get('assumptions'), 'assumptions')
    modules = data.get('modules')
    if not isinstance(modules, list) or not modules:
        raise ValueError('modules must be a nonempty list')
    seen = set()
    known_resources = {r['id'] for r in resources()}
    for module in modules:
        if not isinstance(module, dict):
            raise ValueError('Each module must be an object')
        id_ = slug(module.get('id'))
        if id_ in seen:
            raise ValueError(f'Duplicate module: {id_}')
        for key in ('title', 'outcome'):
            nonempty(module.get(key), f'{id_}.{key}')
        subject = module.get('subject')
        if subject not in SUBJECTS or module.get('teacher') != subject:
            raise ValueError(f'{id_}: lead teacher must match a supplied subject')
        support = strings(module.get('supporting_teachers'), 'supporting_teachers')
        if any(t not in SUBJECTS or t == subject for t in support) or len(support) != len(set(support)):
            raise ValueError(f'{id_}: invalid or duplicate supporting teacher')
        strings(module.get('concepts'), 'concepts', required=True)
        for concept in module['concepts']:
            if not re.fullmatch(r'[a-z][a-z0-9-]*\.[a-z0-9]+(?:[.-][a-z0-9]+)*', concept):
                raise ValueError(f'Invalid concept ID: {concept}')
        topic_titles = module.get('topic_titles', {})
        if not isinstance(topic_titles, dict) or any(k not in module['concepts'] for k in topic_titles):
            raise ValueError(f'{id_}: topic_titles must map module concept IDs to text')
        for value in topic_titles.values():
            nonempty(value, 'topic_titles value')
        prerequisites = strings(module.get('prerequisites'), 'prerequisites')
        if any(p not in seen for p in prerequisites):
            raise ValueError(f'{id_}: prerequisites must refer to earlier modules; found missing, cyclic, or unordered dependency')
        minutes = module.get('minutes')
        if type(minutes) is not int or minutes <= 0:
            raise ValueError(f'{id_}: minutes must be a positive integer')
        assessment = module.get('assessment')
        if not isinstance(assessment, dict):
            raise ValueError(f'{id_}: assessment must be an object')
        nonempty(assessment.get('prompt'), 'assessment.prompt')
        strings(assessment.get('success_criteria'), 'success_criteria', required=True)
        selected = strings(module.get('resources'), 'resources')
        if any(r not in known_resources for r in selected):
            raise ValueError(f'{id_}: unknown resource ID')
        seen.add(id_)
    return data
