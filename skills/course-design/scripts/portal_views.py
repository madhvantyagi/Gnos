"""Safe read models for the local course portal.

This module deliberately builds new objects from allowlisted fields.  Portal
data is a public projection of private course files; it is not a filtered copy
of those files.
"""

from copy import deepcopy
from pathlib import Path
import re
from urllib.parse import urlparse

from artifact_manifest import read_manifest, ready_artifacts
from course_workspace import _read_json, read_plan
from lesson_contract import public_lesson, validate_lesson


_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

_PUBLIC_COURSE_FIELDS = ("schema_version", "id", "title", "goal", "revision")
_PUBLIC_SOURCE_FIELDS = ("title", "url", "local_path", "type", "checked_on", "sections")
_PUBLIC_PROGRESS_FIELDS = ("planning_state", "evidence", "display_status", "concept_ids", "attempt_count")
_PUBLIC_METADATA_FIELDS = (
    "duration_seconds", "pages", "page_count", "width", "height", "dimensions",
    "captions", "transcript", "thumbnail", "filename", "size_bytes",
)
_WATCH_TYPES = {"audio", "animation", "video", "voice-animation"}
_GENERATED_TYPES = {"code", "diagram", "generated", "interactive-graph", "notebook", "simulation"}
_ARTIFACT_GROUPS = ("watch", "generated", "resources")
_PUBLIC_ATTEMPT_FIELDS = ("id", "exercise_id", "submitted_at", "response", "status", "feedback", "review")
_PUBLIC_QUESTION_FIELDS = (
    "id", "course_id", "chapter_id", "topic_id", "lesson_id", "block_id",
    "artifact_id", "exercise_id", "attempt_id", "text", "created_at", "status",
    "answer", "answered_at",
)


def _require_slug(value, label):
    if not isinstance(value, str) or not _SLUG_RE.fullmatch(value):
        raise ValueError(f"{label} must be a lowercase slug")
    return value


def _copy_if_present(source, fields):
    return {field: deepcopy(source[field]) for field in fields if field in source}


def _public_location(location):
    if not isinstance(location, dict):
        raise ValueError("artifact location must be an object")
    keys = [key for key in ("path", "url") if key in location]
    if len(keys) != 1 or len(location) != 1:
        raise ValueError("artifact location must contain exactly one public target")
    key = keys[0]
    value = location[key]
    if not isinstance(value, str) or not value:
        raise ValueError("artifact location target must be nonempty text")
    if key == "path":
        path = Path(value)
        if path.is_absolute() or ".." in path.parts or "." in path.parts or "\\" in value:
            raise ValueError("artifact location path is unsafe")
    elif urlparse(value).scheme != "https" or not urlparse(value).netloc:
        raise ValueError("artifact location URL must use HTTPS")
    return {key: value}


def _public_metadata(metadata):
    result = {}
    for field in _PUBLIC_METADATA_FIELDS:
        if field not in metadata:
            continue
        value = metadata[field]
        if field == "dimensions":
            if isinstance(value, dict):
                dimensions = {}
                for dimension in ("width", "height"):
                    if isinstance(value.get(dimension), (int, float)) and not isinstance(value.get(dimension), bool):
                        dimensions[dimension] = value[dimension]
                if dimensions:
                    result[field] = dimensions
            continue
        if field in {"thumbnail", "captions", "transcript"}:
            if isinstance(value, bool):
                result[field] = value
            elif isinstance(value, str) and _SLUG_RE.fullmatch(value):
                # A string is an artifact ID, never a path or URL.
                result[field] = value
            continue
        if field == "filename":
            if (isinstance(value, str) and value not in {".", ".."} and
                    "\x00" not in value and "/" not in value and "\\" not in value and
                    not urlparse(value).scheme):
                result[field] = value
            continue
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            result[field] = value
    return result


def public_artifact(artifact: dict) -> dict:
    """Return the explicitly public fields of one registered artifact."""
    if not isinstance(artifact, dict):
        raise ValueError("artifact must be an object")
    result = _copy_if_present(
        artifact,
        ("id", "type", "title", "purpose", "concepts", "chapter_id", "topic_id",
         "lesson_id", "exercise_id", "mime_type", "status", "created_at", "updated_at"),
    )
    for field in ("id", "type", "title", "purpose", "chapter_id", "topic_id", "lesson_id"):
        if field not in result:
            raise ValueError(f"artifact requires public field {field}")
    if "location" not in artifact:
        raise ValueError("artifact requires location")
    result["location"] = _public_location(artifact["location"])
    metadata = artifact.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("artifact metadata must be an object")
    result["metadata"] = _public_metadata(metadata)
    return result


def recent_and_older(items: list[dict], current_topic_id: str, limit: int = 6) -> dict:
    """Put current-topic items first, then retain all remaining items as earlier."""
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        raise ValueError("items must be a list of objects")
    _require_slug(current_topic_id, "current_topic_id")
    if type(limit) is not int or limit < 0:
        raise ValueError("limit must be a nonnegative integer")
    prioritized = [item for item in items if item.get("topic_id") == current_topic_id]
    prioritized.extend(item for item in items if item.get("topic_id") != current_topic_id)
    copied = [deepcopy(item) for item in prioritized]
    return {"recent": copied[:limit], "earlier": copied[limit:]}


def _public_progress(progress, fallback_state):
    if not isinstance(progress, dict):
        progress = {}
    result = _copy_if_present(progress, _PUBLIC_PROGRESS_FIELDS)
    result.setdefault("planning_state", fallback_state)
    result.setdefault("evidence", "not-started")
    result.setdefault("concept_ids", [])
    result.setdefault("attempt_count", 0)
    if "display_status" in result and result["display_status"] == result["evidence"]:
        result.pop("display_status")
    return result


def _public_assessment(assessment):
    if not isinstance(assessment, dict):
        return None
    result = {}
    if isinstance(assessment.get("prompt"), str):
        result["prompt"] = assessment["prompt"]
    return result or None


def public_course(plan: dict) -> dict:
    """Project course identity/frontier and inspected sources without assessments."""
    result = _copy_if_present(plan, _PUBLIC_COURSE_FIELDS)
    current = plan.get("current")
    if not isinstance(current, dict):
        raise ValueError("course current frontier must be an object")
    result["current"] = _copy_if_present(current, ("chapter_id", "topic_id", "next_step"))
    result["assumptions"] = list(plan.get("assumptions", []))
    sources = {}
    for source_id, source in plan.get("sources", {}).items():
        if not isinstance(source_id, str) or not isinstance(source, dict):
            continue
        sources[source_id] = _copy_if_present(source, _PUBLIC_SOURCE_FIELDS)
    result["sources"] = sources
    return result


def build_contents(plan: dict, course_progress: dict) -> list[dict]:
    """Build the chapter/topic hierarchy while preserving plan order."""
    if not isinstance(course_progress, dict):
        course_progress = {}
    topic_progress = course_progress.get("topics", {})
    chapter_progress = course_progress.get("chapters", {})
    if not isinstance(topic_progress, dict):
        topic_progress = {}
    if not isinstance(chapter_progress, dict):
        chapter_progress = {}
    contents = []
    for chapter in plan.get("chapters", []):
        chapter_view = _copy_if_present(chapter, ("id", "title", "state"))
        chapter_view["progress"] = _public_progress(
            chapter_progress.get(chapter.get("id")), chapter.get("state", "planned")
        )
        chapter_view["topics"] = []
        for topic in chapter.get("topics", []):
            topic_view = _copy_if_present(
                topic,
                ("id", "title", "subtopics", "state", "subject", "teacher",
                 "supporting_subjects", "supporting_teachers", "concepts", "prerequisites",
                 "minutes", "resource_ids", "exercise_ids", "lesson_ids"),
            )
            topic_view["progress"] = _public_progress(
                topic_progress.get(topic.get("id")), topic.get("state", "planned")
            )
            assessment = _public_assessment(topic.get("assessment"))
            if assessment is not None:
                topic_view["assessment"] = assessment
            chapter_view["topics"].append(topic_view)
        contents.append(chapter_view)
    return contents


def _lesson_paths(workspace: Path, plan: dict):
    """Resolve only lesson IDs declared by the validated plan; never scan lessons."""
    seen = set()
    lessons_root = workspace / "lessons"
    if lessons_root.is_symlink() or not lessons_root.is_dir():
        return
    for chapter in plan.get("chapters", []):
        for topic in chapter.get("topics", []):
            for lesson_id in topic.get("lesson_ids", []):
                if lesson_id in seen:
                    continue
                seen.add(lesson_id)
                _require_slug(lesson_id, "lesson_id")
                lesson_dir = lessons_root / lesson_id
                lesson_path = lesson_dir / "lesson.json"
                if (lesson_dir.is_symlink() or lesson_path.is_symlink() or
                        not lesson_path.is_file()):
                    continue
                yield lesson_path


def ready_lessons(workspace: Path, plan: dict) -> list[dict]:
    lessons = []
    for path in _lesson_paths(workspace, plan):
        data = _read_json(path)
        validate_lesson(data, plan)
        if data.get("publication") != "ready":
            continue
        lesson = public_lesson(data)
        lessons.append(lesson)
    return sorted(lessons, key=lambda item: (item.get("updated_at", ""), item["id"]), reverse=True)


def _public_response(response):
    if isinstance(response, dict):
        result = {}
        if isinstance(response.get("text"), str):
            result["text"] = response["text"]
        value = response.get("value")
        if isinstance(value, (str, int, float, bool)) or value is None:
            result["value"] = deepcopy(value)
        return result
    if isinstance(response, (str, int, float, bool)) or response is None:
        return deepcopy(response)
    return None


def _public_attempt(attempt: dict) -> dict:
    result = _copy_if_present(attempt, _PUBLIC_ATTEMPT_FIELDS)
    if "response" in result:
        result["response"] = _public_response(result["response"])
    if "feedback" in result and not isinstance(result["feedback"], str):
        result.pop("feedback")
    if isinstance(result.get("review"), dict):
        review = _copy_if_present(
            result["review"], ("result", "help", "kind", "interpretation", "next_step", "reviewed_at")
        )
        result["review"] = {key: value for key, value in review.items() if isinstance(value, str)}
    return result


def _public_question(question: dict) -> dict:
    result = _copy_if_present(question, _PUBLIC_QUESTION_FIELDS)
    for field in ("text", "answer"):
        if isinstance(result.get(field), dict):
            text = result[field].get("text")
            result[field] = text if isinstance(text, str) else None
        elif field in result and not isinstance(result[field], str):
            result.pop(field)
    if "context" in question:
        # Context IDs are copied one by one; arbitrary context payloads are not.
        context = question["context"]
        if isinstance(context, dict):
            context_view = _copy_if_present(
                context, ("course_id", "chapter_id", "topic_id", "lesson_id", "block_id",
                          "artifact_id", "exercise_id", "attempt_id")
            )
            result["context"] = {
                key: value for key, value in context_view.items() if isinstance(value, str)
            }
    return result


def _json_files(directory: Path):
    if directory.is_symlink() or not directory.is_dir():
        return []
    paths = []
    for path in directory.iterdir():
        if path.is_symlink() or not path.is_file() or path.suffix != ".json":
            continue
        paths.append(path)
    return sorted(paths, key=lambda path: path.name)


def read_submissions(workspace: Path) -> list[dict]:
    """Read known interaction snapshots without requiring Task 3 to exist."""
    root = workspace / "submissions"
    if root.is_symlink() or not root.is_dir():
        return []
    paths = list(_json_files(root))
    for exercise_dir in sorted(root.iterdir(), key=lambda path: path.name):
        if exercise_dir.is_symlink() or not exercise_dir.is_dir():
            continue
        if not _SLUG_RE.fullmatch(exercise_dir.name):
            continue
        paths.extend(_json_files(exercise_dir))
    records = []
    for path in paths:
        try:
            record = _read_json(path)
        except (OSError, ValueError):
            continue
        if isinstance(record, dict) and "exercise_id" in record:
            records.append(_public_attempt(record))
    return records


def read_questions(workspace: Path) -> list[dict]:
    root = workspace / "questions"
    records = []
    for path in _json_files(root):
        try:
            record = _read_json(path)
        except (OSError, ValueError):
            continue
        if isinstance(record, dict) and "id" in record:
            records.append(_public_question(record))
    return records


def public_exercises(lessons: list[dict], submissions: list[dict]) -> list[dict]:
    by_exercise = {}
    for submission in submissions:
        exercise_id = submission.get("exercise_id")
        if isinstance(exercise_id, str):
            by_exercise.setdefault(exercise_id, []).append(submission)
    exercises = []
    for lesson in lessons:
        for exercise in lesson.get("exercises", []):
            item = _copy_if_present(
                exercise, ("id", "concepts", "prompt", "response_type", "evaluation", "reference_block_ids")
            )
            item["lesson_id"] = lesson["id"]
            item["chapter_id"] = lesson["chapter_id"]
            item["topic_id"] = lesson["topic_id"]
            item["attempts"] = [_public_attempt(attempt) for attempt in by_exercise.get(exercise["id"], [])]
            exercises.append(item)
    return exercises


def public_questions(questions: list[dict], current_topic_id: str) -> dict:
    return recent_and_older(questions, current_topic_id)


def _artifact_group(artifact_type):
    if artifact_type in _WATCH_TYPES:
        return "watch"
    if artifact_type in _GENERATED_TYPES:
        return "generated"
    return "resources"


def group_artifacts(artifacts: list[dict], current_topic_id: str) -> dict:
    grouped = {group: [] for group in _ARTIFACT_GROUPS}
    for artifact in artifacts:
        grouped[_artifact_group(artifact.get("type"))].append(artifact)
    return {
        group: recent_and_older(grouped[group], current_topic_id)
        for group in _ARTIFACT_GROUPS
    }


def build_portal_view(workspace: Path, learner_summary: dict) -> dict:
    """Build a complete redacted portal snapshot from committed workspace files."""
    workspace = Path(workspace)
    if not isinstance(learner_summary, dict):
        raise ValueError("learner_summary must be an object")
    plan = read_plan(workspace)
    course_progress = learner_summary.get("course_progress", {})
    if not isinstance(course_progress, dict):
        course_progress = {}
    current = plan["current"]["topic_id"]
    lessons = ready_lessons(workspace, plan)
    artifacts = [public_artifact(artifact) for artifact in ready_artifacts(read_manifest(workspace))]
    submissions = read_submissions(workspace)
    questions = read_questions(workspace)
    return {
        "course": public_course(plan),
        "contents": build_contents(plan, course_progress),
        "lessons": recent_and_older(lessons, current),
        "artifacts": group_artifacts(artifacts, current),
        "exercises": public_exercises(lessons, submissions),
        "questions": public_questions(questions, current),
    }
