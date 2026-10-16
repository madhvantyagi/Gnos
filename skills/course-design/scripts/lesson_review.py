"""Private lesson review packets and evidence-backed continuation receipts.

The host tutor diagnoses and authors repairs. These scripts preserve its decision
and reject stale inputs, unreviewed work, and unsupported claims of readiness.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

from course_contract import course_content_fingerprint, course_topics, slug
import course_workspace
from lesson_contract import lesson_fingerprint, task_fingerprint, exercise_fingerprint, validate_lesson
import portal_interactions as interactions
from manage_interaction import evidence_matches_review, resolved_evidence_events

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'skills/learner-tracking/scripts'))
import learner_state


def _fingerprint(value):
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def _learner_data(workspace):
    root, learner, course = workspace.parent.parent.parent, workspace.parts[-3], workspace.name
    try:
        state = learner_state.read_state(root, learner)
    except FileNotFoundError:
        return {}, []
    enrollment = state.get('courses', {}).get(course)
    if enrollment is None:
        return {}, []
    learner_state.resolve_enrolled_plan(root, learner, enrollment)
    summary = learner_state.summarize(state, course, learners_root=root, learner_id=learner)
    return summary, resolved_evidence_events(workspace, [e for e in state['events'] if e['course_id'] == course])


def _current_lessons(workspace, plan):
    lessons = []
    root = workspace / 'lessons'
    if not root.is_dir():
        return lessons
    for directory in sorted(root.iterdir()):
        path = directory / 'lesson.json'
        if directory.is_symlink() or path.is_symlink():
            raise ValueError('Lesson review cannot follow symbolic links')
        if not directory.is_dir() or not path.is_file():
            continue
        lesson = course_workspace._read_json(path)
        if lesson.get('topic_id') != plan['current']['topic_id'] or lesson.get('publication') == 'archived':
            continue
        try:
            validate_lesson(lesson, plan)
        except ValueError as exc:
            # The tutor needs the failed draft/stale lesson to repair it.
            lesson = dict(lesson, validation_error=str(exc))
        lessons.append(lesson)
    return lessons


def build_review_context(workspace: Path) -> dict:
    """Load scoped teaching and actual responses as private, untrusted data."""
    workspace = interactions._workspace(workspace)
    plan = course_workspace.read_plan(workspace)
    topic = next(t for t in course_topics(plan) if t['id'] == plan['current']['topic_id'])
    summary, events = _learner_data(workspace)
    events_by_id = {event['id']: event for event in events}
    attempts, earlier_pending = [], []
    for stored in interactions.read_attempts(workspace):
        attempt = deepcopy(stored)
        try:
            context = interactions.attempt_context(workspace, stored)
            attempt['assessment_context'] = context
            current = context['topic_id'] == topic['id']
            error = None
            if stored.get('review'):
                try:
                    interactions.validate_attempt_review(workspace, stored, stored['review'])
                    event = events_by_id.get(stored.get('evidence_event_id'))
                    if event is not None and not evidence_matches_review(workspace, stored, event):
                        raise ValueError('Linked evidence conflicts with the stored response, review, or source versions')
                except ValueError as exc:
                    error = str(exc)
        except ValueError as exc:
            error = str(exc)
            # Preserve unresolved legacy work; do not silently discard it.
            current = stored['exercise_id'] in topic.get('exercise_ids', [])
        if error:
            attempt['review_error'] = error
        attempt['needs_review'] = bool(error or stored.get('status') != 'reviewed'
                                       or stored.get('evidence_event_id') not in events_by_id)
        if current:
            attempts.append(attempt)
        elif attempt['needs_review']:
            earlier_pending.append(attempt)
    lessons = _current_lessons(workspace, plan)
    fingerprint = _fingerprint(dict(course=course_content_fingerprint(plan), lessons=lessons,
                                    attempts=attempts, events=events))
    continuation = dict(decision='review-required', next_step='Review the saved work and current lesson before continuing.')
    review_root = workspace / 'lesson-reviews'
    if review_root.is_symlink():
        raise ValueError('Lesson review directory cannot use symbolic links')
    if review_root.is_dir():
        matching = []
        receipt_context = dict(lessons=lessons, attempts=attempts, topic=topic,
                               concept_evidence=summary.get('concepts', {}), evidence_events=events,
                               context_fingerprint=fingerprint)
        for path in sorted(review_root.glob('*.json')):
            try:
                record = interactions._read_record(path)
                if record.get('context_fingerprint') != fingerprint:
                    continue
                _validate_saved_receipt(record, receipt_context)
                matching.append(record)
            except (ValueError, KeyError, TypeError):
                # Bad receipts grant no authorization; a normal retry can replace them.
                continue
        if matching:
            last = max(matching, key=lambda r: (r['created_at'], r['id']))
            continuation = {key: last[key] for key in ('id', 'decision', 'reason', 'next_step')}
            continuation['criterion_reviews'] = deepcopy(last.get('criterion_reviews', []))
    assessment = topic.get('assessment', {})
    supported = {r['criterion_id'] for r in continuation.get('criterion_reviews', [])}
    criteria = assessment.get('criteria', [])
    return dict(course_id=plan['id'], current=deepcopy(plan['current']), topic=deepcopy(topic),
                lessons=lessons, attempts=attempts, earlier_pending_attempts=earlier_pending,
                concept_evidence=summary.get('concepts', {}), evidence_events=events,
                assessment_review=dict(required_criteria=deepcopy(criteria),
                    legacy_success_criteria=deepcopy(assessment.get('success_criteria', [])),
                    unsupported_criterion_ids=[c['id'] for c in criteria if c['id'] not in supported]),
                context_fingerprint=fingerprint,
                continuation=continuation)


def _ids(value, label):
    if not isinstance(value, list) or any(not isinstance(v, str) for v in value) or len(value) != len(set(value)):
        raise ValueError(f'{label} must be a list of unique IDs')
    for item in value:
        slug(item)
    return value


def _validate_repairs(repairs, lesson, attempts, advance):
    if not isinstance(repairs, list):
        raise ValueError('repairs must be a list')
    blocks = {block['id']: block for block in lesson['blocks']}
    for repair in repairs:
        if not isinstance(repair, dict) or set(repair) != {
            'attempt_ids', 'block_ids', 'diagnosis', 'change', 'verification_attempt_ids'
        }:
            raise ValueError('Each repair requires attempt_ids, block_ids, diagnosis, change, verification_attempt_ids')
        for field in ('diagnosis', 'change'):
            interactions._nonempty_text(repair[field], field)
        for field in ('attempt_ids', 'block_ids', 'verification_attempt_ids'):
            _ids(repair[field], field)
        if not repair['attempt_ids'] or not repair['block_ids']:
            raise ValueError('A repair must identify source attempts and changed blocks')
        if any(id_ not in blocks for id_ in repair['block_ids']):
            raise ValueError('Repair block_ids must belong to the reviewed lesson')
        if any(id_ not in attempts for id_ in repair['attempt_ids'] + repair['verification_attempt_ids']):
            raise ValueError('Repair attempts must belong to the current topic')
        sources = [attempts[id_] for id_ in repair['attempt_ids']]
        for source in sources:
            snapshot = source.get('assessment_context', {})
            old_blocks = {b['id']: b for b in snapshot.get('teaching_blocks', [])}
            if (snapshot.get('lesson_id') != lesson['id'] or not old_blocks or
                    not any(blocks[id_] != old_blocks.get(id_) for id_ in repair['block_ids'])):
                raise ValueError('Repair needs changed teaching blocks with an original submission snapshot')
        if advance:
            required = {c for source in sources for c in source['assessment_context']['exercise']['concepts']}
            verified = set()
            for id_ in repair['verification_attempt_ids']:
                attempt = attempts[id_]
                snapshot = attempt.get('assessment_context', {})
                review = attempt.get('review', {})
                if (attempt['needs_review'] or review.get('help') != 'none'
                        or snapshot.get('lesson_fingerprint') != lesson_fingerprint(lesson)
                        or any(attempt['submitted_at'] <= source['submitted_at'] for source in sources)
                        or any(task_fingerprint(snapshot['exercise']) == task_fingerprint(source['assessment_context']['exercise'])
                               for source in sources)):
                    raise ValueError('Repair verification must use fresh independent work after the changed lesson')
                verified.update(c for c in snapshot['exercise']['concepts']
                                if review.get('concept_results', {}).get(c, review.get('result')) == 'correct')
            if not required.issubset(verified):
                raise ValueError('Repair needs independent verification for every affected concept')


_DECISION_FIELDS = {'lesson_id', 'context_fingerprint', 'decision', 'reason', 'next_step', 'reviewed_attempt_ids', 'repairs'}
_OPTIONAL_DECISION_FIELDS = {'learner_override', 'criterion_reviews'}


def _current_attempt_concepts(attempt, lessons):
    snapshot = attempt.get('assessment_context', {})
    review = attempt.get('review', {})
    lesson = next((l for l in lessons if l['id'] == snapshot.get('lesson_id')
                   and l.get('publication') == 'ready' and not l.get('validation_error')), None)
    if (not lesson or attempt['needs_review'] or review.get('help') != 'none'
            or snapshot.get('lesson_fingerprint') != lesson_fingerprint(lesson)):
        return set()
    if not any(exercise_fingerprint(e) == snapshot.get('exercise_fingerprint') for e in lesson['exercises']):
        return set()
    return {c for c in snapshot['exercise']['concepts']
            if review.get('concept_results', {}).get(c, review.get('result')) == 'correct'}


def _validate_criterion_reviews(review, context):
    criteria = {c['id']: c for c in context['topic'].get('assessment', {}).get('criteria', [])}
    entries = review.get('criterion_reviews', [])
    if not isinstance(entries, list):
        raise ValueError('criterion_reviews must be a list')
    attempts = {a['id']: a for a in context['attempts']}
    events = {e['id']: e for e in context.get('evidence_events', [])}
    reviewed = set()
    supported_concepts = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {'criterion_id', 'attempt_ids', 'event_ids', 'explanation'}:
            raise ValueError('Each criterion review requires criterion_id, attempt_ids, event_ids, explanation')
        slug(entry['criterion_id'])
        criterion = criteria.get(entry['criterion_id'])
        if criterion is None or entry['criterion_id'] in reviewed:
            raise ValueError('criterion_reviews must identify distinct declared criteria')
        reviewed.add(entry['criterion_id'])
        interactions._nonempty_text(entry['explanation'], 'criterion review explanation')
        _ids(entry['attempt_ids'], 'criterion attempt_ids')
        _ids(entry['event_ids'], 'criterion event_ids')
        if not entry['attempt_ids'] and not entry['event_ids']:
            raise ValueError('A criterion review needs actual evidence IDs')
        demonstrated = set()
        for id_ in entry['attempt_ids']:
            if id_ not in attempts:
                raise ValueError('Criterion attempt must belong to the current topic')
            concepts = _current_attempt_concepts(attempts[id_], context['lessons'])
            if not concepts:
                raise ValueError('Criterion evidence needs independent correct work on the current lesson version')
            demonstrated.update(concepts)
        for id_ in entry['event_ids']:
            event = events.get(id_)
            if event is None:
                raise ValueError('Criterion event must exist in this course')
            # Portal-derived events cannot bypass snapshot/version checks through
            # the chat evidence route. Authentic chat work has no portal source.
            if event.get('source') or id_.startswith('portal-'):
                attempt = next((a for a in attempts.values() if a.get('evidence_event_id') == id_), None)
                concepts = _current_attempt_concepts(attempt, context['lessons']) if attempt else set()
            else:
                concepts = {a['concept'] for a in event['attempts']
                            if a['result'] == 'correct' and a['help'] == 'none'}
                if not concepts.issubset(context['topic']['concepts']):
                    # A real chat event may include several topics; only actual
                    # current-topic observations support this criterion.
                    concepts &= set(context['topic']['concepts'])
            if not concepts:
                raise ValueError('Criterion event needs independent correct current-topic evidence')
            demonstrated.update(concepts)
        required = set(criterion.get('concepts', context['topic']['concepts']))
        if not required.issubset(demonstrated):
            raise ValueError('Criterion evidence must cover its declared concepts')
        supported_concepts.update(demonstrated)
    if review['decision'] == 'advance' and set(criteria) != reviewed:
        raise ValueError('Advance requires explicit criterion reviews for every declared assessment criterion')
    return supported_concepts


def _validate_decision(review, context):
    if not isinstance(review, dict) or not _DECISION_FIELDS.issubset(review) or set(review) - (_DECISION_FIELDS | _OPTIONAL_DECISION_FIELDS):
        raise ValueError('Lesson review requires lesson_id, context_fingerprint, decision, reason, next_step, reviewed_attempt_ids, repairs')
    if not isinstance(review['decision'], str) or review['decision'] not in {'advance', 'practice', 'repair-prerequisite', 'skip'}:
        raise ValueError('Invalid lesson continuation decision')
    for field in ('reason', 'next_step'):
        interactions._nonempty_text(review[field], field)
    if review['decision'] == 'skip':
        interactions._nonempty_text(review.get('learner_override'), 'learner_override')
    elif 'learner_override' in review:
        raise ValueError('learner_override belongs only to an explicit skip')
    _ids(review['reviewed_attempt_ids'], 'reviewed_attempt_ids')
    if review['lesson_id'] is None and review['decision'] == 'skip' and not context['lessons']:
        lesson = None
        if review['repairs'] != []:
            raise ValueError('An unauthored-topic skip cannot claim lesson repairs')
    else:
        slug(review['lesson_id'])
        lesson = next((l for l in context['lessons'] if l['id'] == review['lesson_id']), None)
        if lesson is None:
            raise ValueError('Review lesson must belong to the current topic')
    reviewed = {a['id'] for a in context['attempts'] if not a['needs_review']}
    if set(review['reviewed_attempt_ids']) != reviewed:
        raise ValueError('reviewed_attempt_ids must identify all linked current-topic reviews')
    if review['decision'] != 'skip' and any(a['needs_review'] for a in context['attempts']):
        raise ValueError('Review and link all current-topic attempts before deciding continuation')
    criterion_concepts = _validate_criterion_reviews(review, context)
    if lesson is None:
        return None
    advance = review['decision'] == 'advance'
    if advance:
        if lesson.get('publication') != 'ready' or lesson.get('validation_error'):
            raise ValueError('Advance requires a valid ready lesson')
        if any(context['concept_evidence'].get(c, {}).get('status') not in {'demonstrated', 'retained'}
               for c in context['topic']['concepts']):
            raise ValueError('Advance requires independent evidence for every current-topic concept')
        # Changing teaching cannot reuse an old response by omitting repairs.
        if context['attempts']:
            applicable = set(criterion_concepts)
            for attempt in context['attempts']:
                applicable.update(_current_attempt_concepts(attempt, context['lessons']))
            if not set(context['topic']['concepts']).issubset(applicable):
                raise ValueError('Advance needs independent verification against the current lesson and exercise versions')
    _validate_repairs(review['repairs'], lesson, {a['id']: a for a in context['attempts']}, advance)
    return lesson


def _validate_saved_receipt(record, context):
    payload = {key: record[key] for key in _DECISION_FIELDS if key in record}
    for key in _OPTIONAL_DECISION_FIELDS:
        if key in record:
            payload[key] = record[key]
    lesson = _validate_decision(payload, context)
    slug(record.get('id'))
    timestamp = interactions._nonempty_text(record.get('created_at'), 'created_at')
    if not timestamp.endswith('Z'):
        raise ValueError('Receipt created_at must be a UTC timestamp')
    interactions.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    expected = lesson_fingerprint(lesson) if lesson is not None else None
    if record.get('lesson_fingerprint') != expected:
        raise ValueError('Stored lesson review fingerprint does not match')


def record_lesson_review(workspace: Path, review: dict) -> dict:
    """Store a scoped continuation decision; never advance the plan implicitly."""
    workspace = interactions._workspace(workspace)
    if not isinstance(review, dict):
        raise ValueError('Lesson review must be an object')
    with course_workspace._workspace_lock(workspace):
        context = build_review_context(workspace)
        if review.get('context_fingerprint') != context['context_fingerprint']:
            raise course_workspace.ConflictError('Lesson, answers, or evidence changed; reload the review packet')
        lesson = _validate_decision(review, context)
        root = interactions._safe_directory(workspace / 'lesson-reviews')
        for path in sorted(root.glob('*.json')):
            try:
                prior = interactions._read_record(path)
                if all(prior.get(key) == value for key, value in review.items()):
                    _validate_saved_receipt(prior, context)
                    return prior
            except (ValueError, KeyError, TypeError):
                continue
        receipt = dict(deepcopy(review), id=interactions.new_slugged_id('lesson-review'),
                       created_at=interactions.utc_now(), lesson_fingerprint=lesson_fingerprint(lesson) if lesson is not None else None,
                       pending_attempt_ids=[a['id'] for a in context['attempts'] if a['needs_review']])
        interactions._write_new(root / (receipt['id'] + '.json'), receipt)
    return receipt


def require_continuation(workspace: Path) -> None:
    """Protect an enrolled topic transition without changing un-enrolled blueprints."""
    workspace = interactions._workspace(workspace)
    summary, _ = _learner_data(workspace)
    if summary and build_review_context(workspace)['continuation']['decision'] not in {'advance', 'skip'}:
        raise ValueError('Topic transition requires a current advance or explicit-skip continuation review')
