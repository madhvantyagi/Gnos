"""Private, append-only persistence for the local course portal.

This module is deliberately separate from :mod:`portal_views`.  It resolves
exercise IDs through validated ready lessons, keeps evaluation data on the
server side, and never invokes a model or executes submitted code.
"""

from copy import deepcopy
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import uuid

from artifact_manifest import read_manifest, ready_artifacts
from course_contract import slug
import course_workspace
from course_workspace import atomic_json, read_plan
from lesson_contract import exercise_fingerprint, task_fingerprint, lesson_fingerprint, validate_lesson


_TEXT_LIMIT = 200_000
_CONTEXT_IDS = (
    "course_id", "chapter_id", "topic_id", "lesson_id", "block_id",
    "artifact_id", "exercise_id", "attempt_id",
)
_REVIEW_FIELDS = ("result", "help", "kind", "interpretation", "next_step")
_REVIEW_ENUMS = {
    "result": {"correct", "partial", "incorrect"},
    "help": {"none", "hint", "worked-example"},
    "kind": {"application", "retrieval", "transfer"},
}
_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def utc_now() -> str:
    """Keep rapid successive attempts ordered with a precise UTC timestamp."""
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def new_slugged_id(prefix: str) -> str:
    """Create a safe, opaque ID suitable for a workspace filename."""
    slug(prefix)
    return f"{prefix}-{uuid.uuid4().hex}"


def _workspace(path: Path) -> Path:
    checked = course_workspace._workspace_path_for_operation(Path(path))
    if not checked.is_dir():
        raise ValueError("Course workspace does not exist")
    return checked


def _safe_directory(path: Path) -> Path:
    if path.is_symlink():
        raise ValueError("Interaction directories cannot use symbolic links")
    path.mkdir(parents=True, exist_ok=True)
    if path.is_symlink() or not path.is_dir():
        raise ValueError("Interaction directory is not a regular directory")
    return path


def _read_record(path: Path) -> dict:
    if path.is_symlink():
        raise ValueError("Interaction snapshots cannot use symbolic links")
    value = course_workspace._read_json(path)
    if not isinstance(value, dict):
        raise ValueError("Interaction snapshot must be an object")
    return value


def _write_new(path: Path, record: dict) -> None:
    if path.is_symlink() or path.exists():
        raise FileExistsError(path)
    atomic_json(path, record)


def _write_replace(path: Path, record: dict) -> None:
    if path.is_symlink():
        raise ValueError("Interaction snapshots cannot use symbolic links")
    atomic_json(path, record)


def _json_equal(left, right) -> bool:
    return json.dumps(left, sort_keys=True, ensure_ascii=False, separators=(",", ":")) == json.dumps(
        right, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    )


def _nonempty_text(value, label, limit=_TEXT_LIMIT) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f"{label} must be nonempty text")
    if "\x00" in value:
        raise ValueError(f"{label} contains NUL")
    return value


def attempt_context(workspace: Path, attempt: dict) -> dict:
    """Resolve original assessment data; explicitly identify legacy fallbacks."""
    snapshot = attempt.get('exercise_snapshot')
    if snapshot is None:
        found = _find_exercise(workspace, attempt['exercise_id'])
        return dict(course_id=found['plan']['id'], chapter_id=found['chapter']['id'],
                    topic_id=found['topic']['id'], lesson_id=found['lesson']['id'],
                    exercise=deepcopy(found['exercise']), snapshot_source='legacy-current-exercise')
    if not isinstance(snapshot, dict) or snapshot.get('schema_version') != 1:
        raise ValueError('Invalid exercise snapshot')
    for field in ('course_id', 'chapter_id', 'topic_id', 'lesson_id'):
        slug(snapshot.get(field))
    exercise = snapshot.get('exercise')
    if (not isinstance(exercise, dict) or exercise.get('id') != attempt.get('exercise_id')
            or snapshot.get('exercise_fingerprint') != exercise_fingerprint(exercise)
            or snapshot['course_id'] != read_plan(workspace)['id']):
        raise ValueError('Exercise snapshot does not match its attempt or course')
    _validate_response(exercise, attempt['response'])
    return dict(deepcopy(snapshot), snapshot_source='submission')


def _hint_records(workspace: Path, exercise_id: str):
    root = workspace / 'exercises' / slug(exercise_id) / 'hints'
    if any(p.is_symlink() for p in (root, root.parent, root.parent.parent)):
        raise ValueError('Hint directories cannot use symbolic links')
    if root.is_dir():
        for path in sorted(root.glob('*.json')):
            yield _read_record(path)


def hint_records_for_task(workspace: Path, exercise_id: str, task: str, before: str | None = None):
    """Fingerprint-bearing assistance follows a task across exercise renames."""
    root = workspace / 'exercises'
    if root.is_symlink() or not root.is_dir():
        return
    for directory in sorted(root.iterdir()):
        if directory.is_symlink() or not directory.is_dir() or not _ID_RE.fullmatch(directory.name):
            continue
        for record in _hint_records(workspace, directory.name):
            recorded_task = record.get('task_fingerprint')
            if recorded_task != task and not (recorded_task is None and directory.name == exercise_id):
                continue
            if before is not None and not (record.get('requested_at', '') and record['requested_at'] < before):
                continue
            yield record


def validate_attempt_review(workspace: Path, attempt: dict, review: dict) -> dict:
    """Keep recorded assistance and concept scope consistent with the review."""
    checked = _validate_review(review)
    context = attempt_context(workspace, attempt)
    concepts = set(context['exercise']['concepts'])
    results = checked.get('concept_results', {})
    if results and set(results) != concepts:
        raise ValueError('concept_results must cover exactly the exercise concepts')
    if len(concepts) > 1 and checked['result'] == 'partial' and not results:
        raise ValueError('A partial multi-concept review requires concept_results')
    solution_seen = attempt.get('solution_seen_before_submission', False)
    task = task_fingerprint(context['exercise'])
    hint_seen = attempt.get('hint_requested_before_submission', False) or any(
        hint_records_for_task(workspace, attempt['exercise_id'], task, attempt.get('submitted_at', '')))
    if solution_seen and checked['help'] != 'worked-example':
        raise ValueError('Recorded solution assistance requires help=worked-example')
    if hint_seen and checked['help'] == 'none':
        raise ValueError('Recorded hint assistance cannot use help=none')
    return checked


def _finite_number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise ValueError(f"{label} must be a finite number")
    return value


def _lesson_candidates(workspace: Path, plan: dict):
    lessons_root = workspace / "lessons"
    if lessons_root.is_symlink():
        raise ValueError("Lessons directory cannot use symbolic links")
    if not lessons_root.is_dir():
        return
    for chapter in plan.get("chapters", []):
        for topic in chapter.get("topics", []):
            for lesson_id in topic.get("lesson_ids", []):
                slug(lesson_id)
                lesson_dir = lessons_root / lesson_id
                lesson_path = lesson_dir / "lesson.json"
                if lesson_dir.is_symlink() or lesson_path.is_symlink() or not lesson_path.is_file():
                    continue
                lesson = course_workspace._read_json(lesson_path)
                validate_lesson(lesson, plan)
                if lesson.get("publication") != "ready":
                    continue
                yield chapter, topic, lesson


def _find_exercise(workspace: Path, exercise_id: str) -> dict:
    slug(exercise_id)
    plan = read_plan(workspace)
    for chapter, topic, lesson in _lesson_candidates(workspace, plan):
        if exercise_id not in topic.get("exercise_ids", []):
            continue
        for exercise in lesson.get("exercises", []):
            if exercise.get("id") == exercise_id:
                return {
                    "plan": plan,
                    "chapter": chapter,
                    "topic": topic,
                    "lesson": lesson,
                    "exercise": exercise,
                }
    raise ValueError(f"Unknown ready exercise ID: {exercise_id}")


def _validate_response(exercise: dict, response):
    if not isinstance(response, dict):
        raise ValueError("response must be an object")
    response_type = exercise["response_type"]
    if response_type in {"short-text", "long-text", "code-text"}:
        if set(response) != {"text"}:
            raise ValueError(f"{response_type} response must contain only text")
        return {"text": _nonempty_text(response["text"], "response.text")}
    if response_type == "multiple-choice":
        if set(response) != {"value"} or not isinstance(response["value"], str):
            raise ValueError("multiple-choice response must contain one string value")
        options = exercise["evaluation"].get("options", [])
        if response["value"] not in options:
            raise ValueError("response.value is not one of the exercise options")
        return {"value": response["value"]}
    if response_type == "numeric":
        if set(response) != {"value"}:
            raise ValueError("numeric response must contain one value")
        return {"value": _finite_number(response["value"], "response.value")}
    raise ValueError(f"Unsupported response type: {response_type}")


def _evaluate(exercise: dict, response: dict):
    mode = exercise["evaluation"]["mode"]
    if mode == "manual":
        return "awaiting-review", None
    answer = exercise["evaluation"]["answer"]
    if mode == "choice":
        correct = response["value"] == answer
    elif mode == "numeric":
        correct = abs(float(response["value"]) - float(answer)) <= float(exercise["evaluation"]["tolerance"])
    else:
        raise ValueError(f"Unsupported evaluation mode: {mode}")
    # Never include the expected answer, tolerance, or solution in a portal record.
    return "checked", "Correct." if correct else "Not yet; review the explanation and try again."


def _attempt_path(workspace: Path, exercise_id: str, attempt_id: str) -> Path:
    slug(exercise_id)
    if not isinstance(attempt_id, str) or not _ID_RE.fullmatch(attempt_id):
        raise ValueError("attempt_id must be a lowercase slug")
    return workspace / "submissions" / exercise_id / f"{attempt_id}.json"


def _attempt_files(workspace: Path):
    root = workspace / "submissions"
    if root.is_symlink() or not root.is_dir():
        return
    for path in sorted(root.glob("*.json")):
        if not path.is_symlink() and path.is_file():
            yield path
    for exercise_dir in sorted(root.iterdir(), key=lambda item: item.name):
        if exercise_dir.is_symlink() or not exercise_dir.is_dir():
            continue
        for path in sorted(exercise_dir.glob("*.json")):
            if not path.is_symlink() and path.is_file():
                yield path


def read_attempts(workspace: Path, exercise_id: str | None = None) -> list[dict]:
    """Read stored attempts, optionally limited to a validated exercise."""
    workspace = _workspace(workspace)
    if exercise_id is not None:
        slug(exercise_id)
    records = []
    for path in _attempt_files(workspace) or ():
        try:
            record = _read_record(path)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        if "exercise_id" not in record or "id" not in record:
            continue
        if exercise_id is None or record["exercise_id"] == exercise_id:
            records.append(record)
    return sorted(records, key=lambda item: (item.get("submitted_at", ""), item["id"]))


def read_attempt(workspace: Path, attempt_id: str) -> dict:
    if not isinstance(attempt_id, str) or not _ID_RE.fullmatch(attempt_id):
        raise ValueError("attempt_id must be a lowercase slug")
    for record in read_attempts(workspace):
        if record.get("id") == attempt_id:
            return deepcopy(record)
    raise ValueError(f"Unknown attempt ID: {attempt_id}")


def _with_attempt_alias(record: dict) -> dict:
    result = deepcopy(record)
    result["attempt_id"] = result["id"]
    return result


def _draft_path(workspace: Path, exercise_id: str) -> Path:
    slug(exercise_id)
    return workspace / 'exercises' / exercise_id / 'draft.json'


def _read_draft(workspace: Path, exercise_id: str):
    path = _draft_path(workspace, exercise_id)
    if any(parent.is_symlink() for parent in (path.parent, path.parent.parent)):
        raise ValueError('Draft directories cannot use symbolic links')
    return _read_record(path) if path.exists() or path.is_symlink() else None


def _displayed_versions(found, exercise_version, lesson_version):
    if (exercise_version is None) != (lesson_version is None):
        raise ValueError('Displayed exercise and lesson versions must be supplied together')
    if exercise_version is not None and (exercise_version != exercise_fingerprint(found['exercise']) or
            lesson_version != lesson_fingerprint(found['lesson'])):
        raise course_workspace.ConflictError('Lesson or exercise changed; re-render and reload before saving')


def _draft_response(exercise, response):
    field = 'text' if exercise['response_type'] in {'short-text', 'long-text', 'code-text'} else 'value'
    if not isinstance(response, dict) or set(response) != {field}:
        raise ValueError(f'draft response must contain only {field}')
    value = response[field]
    if isinstance(value, str):
        if len(value) > _TEXT_LIMIT or '\x00' in value:
            raise ValueError('Draft text is too large or contains NUL')
    elif field != 'value' or isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('Draft answer must be editable text or a finite number')
    if exercise['response_type'] == 'multiple-choice' and value not in ['', *exercise['evaluation'].get('options', [])]:
        raise ValueError('Draft choice is not an exercise option')
    return {field: value}


def save_draft(workspace: Path, exercise_id: str, response: dict, expected_revision: int | None = None,
               expected_exercise_fingerprint: str | None = None,
               expected_lesson_fingerprint: str | None = None, base_attempt_id: str | None = None) -> dict:
    workspace = _workspace(workspace)
    if expected_revision is not None and (type(expected_revision) is not int or expected_revision < 0):
        raise ValueError('expected_revision must be a nonnegative integer')
    with course_workspace._workspace_lock(workspace):
        found = _find_exercise(workspace, exercise_id)
        _displayed_versions(found, expected_exercise_fingerprint, expected_lesson_fingerprint)
        _validate_attempt_reference(workspace, exercise_id, base_attempt_id)
        previous = _read_draft(workspace, exercise_id)
        revision = previous.get('revision', 0) if previous else 0
        checked_response = _draft_response(found['exercise'], response)
        if expected_revision is not None and expected_revision != revision:
            if (previous and previous.get('status') == 'draft' and revision == expected_revision + 1 and
                    previous.get('base_attempt_id') == base_attempt_id and
                    previous.get('exercise_fingerprint') == exercise_fingerprint(found['exercise']) and
                    previous.get('lesson_fingerprint') == lesson_fingerprint(found['lesson']) and
                    _json_equal(previous.get('response'), checked_response)):
                return deepcopy(previous)
            raise course_workspace.ConflictError('A newer draft exists. Your current text is still on this page; copy it before reloading.')
        record = dict(exercise_id=exercise_id, saved_at=utc_now(), status='draft', revision=revision + 1,
            response=checked_response, base_attempt_id=base_attempt_id,
            exercise_fingerprint=exercise_fingerprint(found['exercise']),
            lesson_fingerprint=lesson_fingerprint(found['lesson']))
        _safe_directory(workspace / 'exercises')
        _safe_directory(_draft_path(workspace, exercise_id).parent)
        _write_replace(_draft_path(workspace, exercise_id), record)
    return deepcopy(record)


def submit_attempt(workspace: Path, exercise_id: str, response: dict, attempt_id: str | None = None,
                   expected_exercise_fingerprint: str | None = None,
                   expected_lesson_fingerprint: str | None = None, draft_revision: int | None = None) -> dict:
    workspace = _workspace(workspace)
    found = _find_exercise(workspace, exercise_id)
    if (expected_exercise_fingerprint is None) != (expected_lesson_fingerprint is None):
        raise ValueError('Displayed exercise and lesson versions must be supplied together')
    if expected_exercise_fingerprint is not None and expected_exercise_fingerprint != exercise_fingerprint(found['exercise']):
        raise course_workspace.ConflictError('Exercise changed; re-render and reload before saving')
    if expected_lesson_fingerprint is not None and expected_lesson_fingerprint != lesson_fingerprint(found['lesson']):
        raise course_workspace.ConflictError('Lesson changed; re-render and reload before saving')
    checked_response = _validate_response(found["exercise"], response)
    attempt_id = attempt_id or new_slugged_id("attempt")
    target = _attempt_path(workspace, exercise_id, attempt_id)
    status, feedback = _evaluate(found["exercise"], checked_response)
    record = {
        "id": attempt_id,
        "exercise_id": exercise_id,
        "submitted_at": utc_now(),
        "response": checked_response,
        "status": status,
        "feedback": feedback,
        "evidence_event_id": None,
        "exercise_snapshot": {
            "schema_version": 1, "course_id": found["plan"]["id"],
            "chapter_id": found["chapter"]["id"], "topic_id": found["topic"]["id"],
            "lesson_id": found["lesson"]["id"],
            "lesson_fingerprint": lesson_fingerprint(found["lesson"]),
            "exercise_fingerprint": exercise_fingerprint(found["exercise"]),
            "exercise": deepcopy(found["exercise"]),
            "teaching_blocks": [deepcopy(b) for b in found["lesson"]["blocks"]
                                if set(b["concepts"]) & set(found["exercise"]["concepts"])],
        },
    }
    with course_workspace._workspace_lock(workspace):
        # Attempt IDs are global so accidental cross-exercise reuse cannot hide work.
        existing = next((item for item in read_attempts(workspace) if item.get("id") == attempt_id), None)
        if existing is not None:
            if existing.get("exercise_id") == exercise_id and _json_equal(existing.get("response"), checked_response):
                return _with_attempt_alias(existing)
            raise ValueError("Attempt ID is already used for different content")
        # Recheck the lesson under the same lock used by lesson publication.
        current = _find_exercise(workspace, exercise_id)
        if lesson_fingerprint(current["lesson"]) != record["exercise_snapshot"]["lesson_fingerprint"]:
            raise course_workspace.ConflictError("Exercise changed; reload before saving")
        task = task_fingerprint(found['exercise'])
        record["solution_seen_before_submission"] = any(
            item.get("solution_revealed_at") and (
                (not item.get('exercise_snapshot') and item['exercise_id'] == exercise_id) or
                (item.get('exercise_snapshot') and task_fingerprint(item['exercise_snapshot']['exercise']) == task))
            for item in read_attempts(workspace))
        record["hint_requested_before_submission"] = any(
            hint_records_for_task(workspace, exercise_id, task, record['submitted_at']))
        _safe_directory(target.parent)
        _write_new(target, record)
        draft = _read_draft(workspace, exercise_id)
        if (draft is not None and type(draft_revision) is int and draft.get('revision') == draft_revision and
                draft.get('exercise_fingerprint') == record['exercise_snapshot']['exercise_fingerprint'] and
                draft.get('lesson_fingerprint') == record['exercise_snapshot']['lesson_fingerprint']):
            # Keep a revision tombstone so a delayed pre-submit autosave cannot resurrect it.
            _write_replace(_draft_path(workspace, exercise_id), dict(status='cleared',
                exercise_id=exercise_id, revision=draft_revision + 1, saved_at=utc_now()))
    return _with_attempt_alias(record)


def exercise_state(workspace: Path, exercise_id: str) -> dict:
    """Return the latest saved response without disclosing the worked answer."""
    workspace = _workspace(workspace)
    found = _find_exercise(workspace, exercise_id)
    exercise = found['exercise']
    from portal_views import _public_attempt
    attempts = read_attempts(workspace, exercise_id)
    version = exercise_fingerprint(exercise)
    lesson_version = lesson_fingerprint(found['lesson'])
    draft = _read_draft(workspace, exercise_id)
    matching_draft = draft if draft and draft.get('status') == 'draft' and (
        draft.get('exercise_fingerprint') == version and draft.get('lesson_fingerprint') == lesson_version) else None
    current = [a for a in attempts if not a.get('exercise_snapshot') or
               (a['exercise_snapshot'].get('exercise_fingerprint') == version and
                a['exercise_snapshot'].get('lesson_fingerprint') == lesson_version)]
    latest = current[-1] if current else None
    history = []
    for attempt in attempts:
        item = _public_attempt(attempt)
        try:
            item['prompt'] = attempt_context(workspace, attempt)['exercise']['prompt']
        except ValueError:
            item['prompt'] = 'Original question unavailable for this older attempt.'
        history.append(item)
    result = _public_attempt(latest) if latest else None
    if result:
        result['evidence_recorded'] = bool(latest.get('evidence_event_id'))
        for key in ('solution_revealed_at', 'solution_seen_before_submission'):
            if key in latest:
                result[key] = latest[key]
    return {
        'attempt': result, 'history': history,
        'draft': matching_draft, 'draft_revision': draft.get('revision', 0) if draft else 0,
        'stale_draft': bool(draft and draft.get('status') == 'draft' and not matching_draft),
        'exercise_fingerprint': version, 'lesson_fingerprint': lesson_version,
        'solution_available': bool(exercise.get('solution')) or 'answer' in exercise['evaluation'],
    }


def reveal_solution(workspace: Path, exercise_id: str, attempt_id: str) -> dict:
    """Reveal an authored solution only after an attempt was persisted for this exercise."""
    workspace = _workspace(workspace)
    target = _attempt_path(workspace, exercise_id, attempt_id)
    _validate_attempt_reference(workspace, exercise_id, attempt_id)
    exercise = attempt_context(workspace, read_attempt(workspace, attempt_id))["exercise"]
    solution = exercise.get("solution")
    if not solution and "answer" in exercise["evaluation"]:
        solution = str(exercise["evaluation"]["answer"])
    if not solution:
        raise ValueError("A worked answer has not been added to this exercise yet.")
    with course_workspace._workspace_lock(workspace):
        record = _read_record(target)
        if not record.get("solution_revealed_at"):
            record["solution_revealed_at"] = utc_now()
            _write_replace(target, record)
    return {"exercise_id": exercise_id, "attempt_id": attempt_id, "solution": solution,
            "revealed_at": record["solution_revealed_at"]}


def _validate_attempt_reference(workspace: Path, exercise_id: str, attempt_id: str | None):
    if attempt_id is None:
        return
    attempt = read_attempt(workspace, attempt_id)
    if attempt.get("exercise_id") != exercise_id:
        raise ValueError("attempt_id does not belong to exercise_id")


def request_hint(workspace: Path, exercise_id: str, attempt_id: str | None = None) -> dict:
    workspace = _workspace(workspace)
    with course_workspace._workspace_lock(workspace):
        exercise = _find_exercise(workspace, exercise_id)["exercise"]
        _validate_attempt_reference(workspace, exercise_id, attempt_id)
        hint_id = new_slugged_id("hint")
        record = dict(id=hint_id, exercise_id=exercise_id, attempt_id=attempt_id,
            requested_at=utc_now(), exercise_fingerprint=exercise_fingerprint(exercise),
            task_fingerprint=task_fingerprint(exercise), status='requested')
        _safe_directory(workspace / 'exercises')
        _safe_directory(workspace / 'exercises' / exercise_id)
        hint_dir = _safe_directory(workspace / "exercises" / exercise_id / "hints")
        _write_new(hint_dir / f"{hint_id}.json", record)
    result = deepcopy(record)
    result["hint_id"] = hint_id
    return result


def _ready_lesson_context(found: dict, context: dict):
    plan = found["plan"]
    chapter = next((item for item in plan["chapters"] if item["id"] == context.get("chapter_id")), None)
    if chapter is None:
        raise ValueError("context.chapter_id is not in the selected course")
    topic = next((item for item in chapter["topics"] if item["id"] == context.get("topic_id")), None)
    if topic is None:
        raise ValueError("context.topic_id is not in context.chapter_id")
    if context.get("lesson_id") is not None:
        if context["lesson_id"] != found["lesson"]["id"]:
            raise ValueError("context.lesson_id is not the selected ready lesson")
    return chapter, topic


def _normalize_question_input(question: dict) -> tuple[str, dict]:
    if not isinstance(question, dict):
        raise ValueError("question must be an object")
    text = question.get("text")
    _nonempty_text(text, "question.text")
    unknown = set(question) - {"text", "context", "question_id", "id", *_CONTEXT_IDS}
    if unknown:
        raise ValueError(f"question contains unsupported fields: {sorted(unknown)!r}")
    context = {}
    nested = question.get("context", {})
    if not isinstance(nested, dict):
        raise ValueError("question.context must be an object")
    for key, value in nested.items():
        if key not in _CONTEXT_IDS:
            raise ValueError(f"question.context contains unsupported field: {key}")
        context[key] = value
    for key in _CONTEXT_IDS:
        if key in question:
            if key in context and context[key] != question[key]:
                raise ValueError(f"question context disagrees on {key}")
            context[key] = question[key]
    for key, value in list(context.items()):
        if value is None:
            context.pop(key)
            continue
        if not isinstance(value, str) or not _ID_RE.fullmatch(value):
            raise ValueError(f"question.context.{key} must be a lowercase ID")
    return text, context


def _validate_question_context(workspace: Path, text: str, context: dict) -> dict:
    course_id = context.get("course_id")
    if course_id is None:
        raise ValueError("question context requires course_id")
    plan = read_plan(workspace)
    if course_id != plan["id"]:
        raise ValueError("question context.course_id does not match workspace")
    if context.get('attempt_id') and not {'block_id', 'artifact_id'} & set(context):
        # Saved work has its own authentic context, even while its lesson is repaired.
        attempt = read_attempt(workspace, context['attempt_id'])
        original = attempt_context(workspace, attempt)
        for key in ('course_id', 'chapter_id', 'topic_id', 'lesson_id'):
            if context.get(key) is not None and context[key] != original[key]:
                raise ValueError(f'question context.{key} does not match the saved attempt')
            context[key] = original[key]
        if context.get('exercise_id') is not None and context['exercise_id'] != attempt['exercise_id']:
            raise ValueError('question context.attempt_id must belong to context.exercise_id')
        context['exercise_id'] = attempt['exercise_id']
        return {key: context[key] for key in _CONTEXT_IDS if key in context}
    chapters = {item["id"]: item for item in plan["chapters"]}
    chapter = chapters.get(context.get("chapter_id")) if context.get("chapter_id") else None
    if context.get("chapter_id") and chapter is None:
        raise ValueError("question context.chapter_id is not in the course")
    if context.get("topic_id") and chapter is None:
        matches = [item for item in plan["chapters"] if any(topic["id"] == context["topic_id"] for topic in item["topics"])]
        if len(matches) != 1:
            raise ValueError("question context.topic_id is not in the course")
        chapter = matches[0]
        context["chapter_id"] = chapter["id"]
    topics = {item["id"]: item for item in chapter["topics"]} if chapter else {}
    if context.get("topic_id") and context["topic_id"] not in topics:
        raise ValueError("question context.topic_id is not in context.chapter_id")
    topic = topics.get(context.get("topic_id")) if context.get("topic_id") else None
    found = None
    if "lesson_id" in context:
        for candidate in _lesson_candidates(workspace, plan):
            if candidate[2]["id"] == context.get("lesson_id"):
                found = {"plan": plan, "chapter": candidate[0], "topic": candidate[1], "lesson": candidate[2]}
                break
        if found is None:
            raise ValueError("question context.lesson_id must name a ready lesson")
        if context.get("chapter_id") and found["chapter"]["id"] != context["chapter_id"]:
            raise ValueError("question context lesson is outside the selected chapter/topic")
        if context.get("topic_id") and found["topic"]["id"] != context["topic_id"]:
            raise ValueError("question context lesson is outside the selected chapter/topic")
        context.setdefault("chapter_id", found["chapter"]["id"])
        context.setdefault("topic_id", found["topic"]["id"])
        chapter, topic = found["chapter"], found["topic"]
    if "exercise_id" in context and found is None:
        exercise_found = _find_exercise(workspace, context["exercise_id"])
        found = {"plan": plan, "chapter": exercise_found["chapter"], "topic": exercise_found["topic"], "lesson": exercise_found["lesson"]}
        if context.get("chapter_id") and found["chapter"]["id"] != context["chapter_id"]:
            raise ValueError("question context exercise is outside the selected chapter")
        if context.get("topic_id") and found["topic"]["id"] != context["topic_id"]:
            raise ValueError("question context exercise is outside the selected topic")
        context.setdefault("chapter_id", found["chapter"]["id"])
        context.setdefault("topic_id", found["topic"]["id"])
        context.setdefault("lesson_id", found["lesson"]["id"])
        chapter, topic = found["chapter"], found["topic"]
    if "block_id" in context and found is None:
        raise ValueError("question context.block_id requires lesson_id")
    if "exercise_id" in context:
        exercise = next((item for item in found["lesson"]["exercises"] if item["id"] == context["exercise_id"]), None)
        if exercise is None or (topic is not None and context["exercise_id"] not in topic.get("exercise_ids", [])):
            raise ValueError("question context.exercise_id is outside the selected lesson")
    if "block_id" in context:
        if not any(item["id"] == context["block_id"] for item in found["lesson"]["blocks"]):
            raise ValueError("question context.block_id is outside the selected lesson")
    if "artifact_id" in context:
        artifacts = {item["id"]: item for item in ready_artifacts(read_manifest(workspace))}
        artifact = artifacts.get(context["artifact_id"])
        if artifact is None:
            raise ValueError("question context.artifact_id must name a ready artifact")
        if context.get("chapter_id") and artifact["chapter_id"] != context["chapter_id"]:
            raise ValueError("question context artifact is outside the selected topic")
        if context.get("topic_id") and artifact["topic_id"] != context["topic_id"]:
            raise ValueError("question context artifact is outside the selected topic")
        context.setdefault("chapter_id", artifact["chapter_id"])
        context.setdefault("topic_id", artifact["topic_id"])
    if "attempt_id" in context:
        attempt = read_attempt(workspace, context["attempt_id"])
        if "exercise_id" in context and attempt.get("exercise_id") != context["exercise_id"]:
            raise ValueError("question context.attempt_id must belong to context.exercise_id")
        if "exercise_id" not in context:
            context["exercise_id"] = attempt["exercise_id"]
            exercise_found = _find_exercise(workspace, attempt["exercise_id"])
            context.setdefault("lesson_id", exercise_found["lesson"]["id"])
            context.setdefault("chapter_id", exercise_found["chapter"]["id"])
            context.setdefault("topic_id", exercise_found["topic"]["id"])
    return {key: context[key] for key in _CONTEXT_IDS if key in context}


def create_question(workspace: Path, question: dict, question_id: str | None = None) -> dict:
    workspace = _workspace(workspace)
    text, context = _normalize_question_input(question)
    question_id = question_id or question.get("question_id") or question.get("id") or new_slugged_id("question")
    if not isinstance(question_id, str) or not _ID_RE.fullmatch(question_id):
        raise ValueError("question_id must be a lowercase slug")
    target = workspace / "questions" / f"{question_id}.json"
    with course_workspace._workspace_lock(workspace):
        checked_context = _validate_question_context(workspace, text, context)
        record = dict(id=question_id, text=text, context=checked_context, created_at=utc_now(), status='pending')
        if target.exists() or target.is_symlink():
            existing = _read_record(target)
            if (existing.get("text") == record["text"] and
                    _json_equal(existing.get("context"), record["context"])):
                result = deepcopy(existing)
                result["question_id"] = question_id
                return result
            raise ValueError("Question ID is already used for different content")
        _safe_directory(target.parent)
        _write_new(target, record)
    result = deepcopy(record)
    result["question_id"] = question_id
    return result


def _question_path(workspace: Path, question_id: str) -> Path:
    if not isinstance(question_id, str) or not _ID_RE.fullmatch(question_id):
        raise ValueError("question_id must be a lowercase slug")
    return workspace / "questions" / f"{question_id}.json"


def answer_question(workspace: Path, question_id: str, answer: str | dict) -> dict:
    workspace = _workspace(workspace)
    text = answer.get("text") if isinstance(answer, dict) else answer
    if isinstance(answer, dict) and set(answer) != {"text"}:
        raise ValueError("answer must contain only explicit text")
    _nonempty_text(text, "answer")
    target = _question_path(workspace, question_id)
    if not target.is_file() or target.is_symlink():
        raise ValueError(f"Unknown question ID: {question_id}")
    with course_workspace._workspace_lock(workspace):
        record = _read_record(target)
        if record.get("status") == "answered":
            if record.get("answer") == text:
                result = deepcopy(record)
                result["question_id"] = question_id
                return result
            raise ValueError("Question already has a different answer")
        if record.get("status") != "pending":
            raise ValueError("Question is not pending")
        record["answer"] = text
        record["answered_at"] = utc_now()
        record["status"] = "answered"
        _write_replace(target, record)
    result = deepcopy(record)
    result["question_id"] = question_id
    return result


def _validate_review(review: dict) -> dict:
    if (not isinstance(review, dict) or not set(_REVIEW_FIELDS).issubset(review)
            or set(review) - {*_REVIEW_FIELDS, "concept_results"}):
        raise ValueError(f"review requires: {', '.join(_REVIEW_FIELDS)}; optional concept_results")
    checked = {}
    for field in _REVIEW_FIELDS:
        value = _nonempty_text(review[field], f"review.{field}", limit=20_000)
        if field in _REVIEW_ENUMS and value not in _REVIEW_ENUMS[field]:
            raise ValueError(f"review.{field} is not a supported evidence value")
        checked[field] = value
    if "concept_results" in review:
        results = review["concept_results"]
        if (not isinstance(results, dict) or not results or
                any(not isinstance(k, str) or not isinstance(v, str) or v not in _REVIEW_ENUMS["result"] for k, v in results.items())):
            raise ValueError("concept_results must map concepts to correct, partial, or incorrect")
        checked["concept_results"] = deepcopy(results)
    return checked


def review_attempt(workspace: Path, attempt_id: str, review: dict) -> dict:
    workspace = _workspace(workspace)
    checked_review = _validate_review(review)
    original = read_attempt(workspace, attempt_id)
    target = _attempt_path(workspace, original["exercise_id"], attempt_id)
    with course_workspace._workspace_lock(workspace):
        record = _read_record(target)
        checked_review = validate_attempt_review(workspace, record, checked_review)
        if record.get("review") is not None:
            if _json_equal(record["review"], checked_review):
                return _with_attempt_alias(record)
            raise ValueError("Attempt already has a different review")
        record["review"] = checked_review
        record["reviewed_at"] = utc_now()
        record["status"] = "reviewed"
        # Task 4 owns the learner-state evidence bridge; keep this explicitly empty.
        record["evidence_event_id"] = None
        _write_replace(target, record)
    return _with_attempt_alias(record)


def _question_files(workspace: Path):
    root = workspace / "questions"
    if root.is_symlink() or not root.is_dir():
        return
    for path in sorted(root.glob("*.json")):
        if not path.is_symlink() and path.is_file():
            yield path


def _read_questions(workspace: Path) -> list[dict]:
    records = []
    for path in _question_files(workspace) or ():
        try:
            records.append(_read_record(path))
        except (OSError, ValueError, json.JSONDecodeError):
            continue
    return sorted(records, key=lambda item: (item.get("created_at", ""), item.get("id", "")))


def list_pending(workspace: Path) -> dict:
    """Return queued questions and attempts awaiting explicit GNOS review."""
    workspace = _workspace(workspace)
    questions = [item for item in _read_questions(workspace) if item.get("status") == "pending"]
    attempts = [item for item in read_attempts(workspace)
                if item.get("status") != "reviewed" or not item.get("evidence_event_id")]
    return {"questions": deepcopy(questions), "attempts": deepcopy(attempts)}
