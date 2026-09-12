"""Validation and public projections for composed GNOS lessons."""
import copy
from datetime import datetime
import math
import hashlib
import json
import re

from course_contract import _validate_skill_route, nonempty, slug

LESSON_SCHEMA_VERSION = 1
BLOCK_TYPES = {
    "explanation", "bullets", "equation", "code", "voice-animation", "animation",
    "diagram", "interactive-graph", "simulation", "source", "exercise", "feedback", "artifact",
}
RESPONSE_TYPES = {"multiple-choice", "short-text", "long-text", "numeric", "code-text"}
EVALUATION_MODES = {"manual", "choice", "numeric"}
PUBLIC_BLOCK_FIELDS = {"id", "type", "concepts", "purpose", "text", "items", "equation", "code",
                       "artifact_id", "source_id", "exercise_id", "options", "caption", "label"}


def _strings(value, label, required=False):
    if not isinstance(value, list) or (required and not value):
        raise ValueError(f"{label} must be a {'nonempty ' if required else ''}list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"{label} must contain nonempty text")
    return value


def _timestamp(value, label):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value):
        raise ValueError(f"{label} must be an ISO UTC timestamp")
    try:
        datetime.fromisoformat(value[:-1])
    except ValueError as exc:
        raise ValueError(f"{label} must be a real ISO UTC timestamp") from exc


def _artifact_ids(data):
    artifacts = data.get("artifacts", [])
    if isinstance(artifacts, dict):
        return set(artifacts)
    if isinstance(artifacts, list):
        ids = set()
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                raise ValueError("artifacts must contain objects")
            artifact_id = slug(artifact.get("id"))
            if artifact_id in ids:
                raise ValueError(f"Duplicate artifact ID: {artifact_id}")
            ids.add(artifact_id)
        return ids
    raise ValueError("artifacts must be a list or object")


def _validate_evaluation(evaluation, response_type, label):
    if not isinstance(evaluation, dict) or evaluation.get("mode") not in EVALUATION_MODES:
        raise ValueError(f"{label}.evaluation has an invalid mode")
    if "execute" in evaluation or any(evaluation.get(key) is True for key in ("executable", "code_execution", "run_code")):
        raise ValueError(f"{label}: executable submitted-code evaluation is forbidden")
    mode = evaluation["mode"]
    if response_type == "multiple-choice":
        if mode != "choice":
            raise ValueError(f"{label}: multiple-choice requires choice evaluation")
        options = evaluation.get("options")
        if (not isinstance(options, list) or not options or
                any(not isinstance(option, str) or not option.strip() for option in options) or
                len(options) != len(set(options))):
            raise ValueError(f"{label}: choice evaluation requires unique nonempty options")
        if "answer" not in evaluation or evaluation["answer"] not in options:
            raise ValueError(f"{label}: choice answer must be one of the options")
    elif response_type == "numeric" and mode != "numeric":
        raise ValueError(f"{label}: numeric requires numeric evaluation")
    elif response_type != "multiple-choice" and mode == "choice":
        raise ValueError(f"{label}: choice evaluation requires multiple-choice")
    if mode == "numeric":
        answer = evaluation.get("answer")
        tolerance = evaluation.get("tolerance")
        if (isinstance(answer, bool) or not isinstance(answer, (int, float)) or
                not math.isfinite(float(answer))):
            raise ValueError(f"{label}: numeric answer must be numeric")
        if (isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)) or
                not math.isfinite(float(tolerance)) or tolerance < 0):
            raise ValueError(f"{label}: numeric tolerance must be nonnegative numeric")
    if mode == "manual" and any(key in evaluation for key in ("answer", "accepted", "tolerance", "solution")):
        raise ValueError(f"{label}: manual evaluation cannot include private answer fields")


def validate_lesson(data, course):
    """Validate a lesson against an already validated version-two course."""
    if not isinstance(data, dict) or data.get("schema_version") != LESSON_SCHEMA_VERSION:
        raise ValueError("Lesson requires schema_version 1")
    for key in ("id", "course_id", "chapter_id", "topic_id"):
        slug(data.get(key))
    for key in ("title", "purpose", "teacher"):
        nonempty(data.get(key), key)
    if data["course_id"] != course.get("id"):
        raise ValueError("lesson.course_id must refer to the selected course")
    chapters = {chapter["id"]: chapter for chapter in course.get("chapters", [])}
    chapter = chapters.get(data["chapter_id"])
    if not chapter:
        raise ValueError("lesson.chapter_id must refer to a course chapter")
    topics = {topic["id"]: topic for topic in chapter.get("topics", [])}
    topic = topics.get(data["topic_id"])
    if not topic:
        raise ValueError("lesson.topic_id must belong to lesson.chapter_id")
    if data["teacher"] != topic["teacher"]:
        raise ValueError("lesson.teacher must match the topic teacher")
    lesson_concepts = _strings(data.get("concepts"), "concepts", required=True)
    if any(concept not in topic["concepts"] for concept in lesson_concepts):
        raise ValueError("lesson concepts must belong to the selected topic")
    routes = _strings(data.get("skill_routes"), "skill_routes", required=True)
    if len(routes) != len(set(routes)):
        raise ValueError("skill_routes must be unique")
    topic_routes = set(topic.get("skill_routes", []))
    if any(route not in topic_routes for route in routes):
        raise ValueError("skill_routes must be a subset of the selected topic routes")
    for route in routes:
        _validate_skill_route(route)
    _strings(data.get("assumptions"), "assumptions")
    if data.get("publication") not in {"draft", "ready", "archived"}:
        raise ValueError("publication must be draft, ready, or archived")
    _timestamp(data.get("created_at"), "created_at")
    _timestamp(data.get("updated_at"), "updated_at")
    if datetime.fromisoformat(data["updated_at"][:-1]) < datetime.fromisoformat(data["created_at"][:-1]):
        raise ValueError("updated_at must be greater than or equal to created_at")

    exercises = data.get("exercises")
    if not isinstance(exercises, list):
        raise ValueError("exercises must be a list")
    exercise_ids = set()
    for exercise in exercises:
        if not isinstance(exercise, dict):
            raise ValueError("each exercise must be an object")
        exercise_id = slug(exercise.get("id"))
        if exercise_id in exercise_ids:
            raise ValueError(f"Duplicate exercise ID: {exercise_id}")
        exercise_ids.add(exercise_id)
        concepts = _strings(exercise.get("concepts"), f"{exercise_id}.concepts", required=True)
        if any(c not in lesson_concepts for c in concepts):
            raise ValueError(f"{exercise_id}: concepts must belong to the lesson")
        nonempty(exercise.get("prompt"), f"{exercise_id}.prompt")
        response_type = exercise.get("response_type")
        if response_type not in RESPONSE_TYPES:
            raise ValueError(f"{exercise_id}: invalid response_type")
        _validate_evaluation(exercise.get("evaluation"), response_type, exercise_id)
        _strings(exercise.get("success_criteria"), f"{exercise_id}.success_criteria", required=True)
        refs = exercise.get("reference_block_ids", [])
        _strings(refs, f"{exercise_id}.reference_block_ids")

    blocks = data.get("blocks")
    if not isinstance(blocks, list) or not blocks:
        raise ValueError("blocks must be a nonempty list")
    block_ids = set()
    artifact_ids = _artifact_ids(data)
    source_ids = set(course.get("sources", {}))
    media_types = {"voice-animation", "animation", "diagram", "interactive-graph", "simulation", "artifact"}
    for block in blocks:
        if not isinstance(block, dict):
            raise ValueError("each block must be an object")
        block_id = slug(block.get("id"))
        if block_id in block_ids or block_id in exercise_ids:
            raise ValueError(f"Duplicate lesson ID: {block_id}")
        block_ids.add(block_id)
        block_type = block.get("type")
        if block_type not in BLOCK_TYPES:
            raise ValueError(f"{block_id}: invalid block type")
        concepts = _strings(block.get("concepts"), f"{block_id}.concepts", required=True)
        if any(c not in lesson_concepts for c in concepts):
            raise ValueError(f"{block_id}: concepts must belong to the lesson")
        nonempty(block.get("purpose"), f"{block_id}.purpose")
        if block_type == "exercise":
            if block.get("exercise_id") not in exercise_ids:
                raise ValueError(f"{block_id}: unknown exercise reference")
        if "exercise_id" in block and block["exercise_id"] not in exercise_ids:
            raise ValueError(f"{block_id}: unknown exercise reference")
        if "artifact_id" in block:
            if not isinstance(block["artifact_id"], str) or block["artifact_id"] not in artifact_ids:
                raise ValueError(f"{block_id}: unknown artifact reference")
        if block_type in media_types and block.get("artifact_id") not in artifact_ids:
            raise ValueError(f"{block_id}: media block requires a known artifact reference")
        if block_type == "source":
            if block.get("source_id") not in source_ids:
                raise ValueError(f"{block_id}: unknown source reference")
        elif "source_id" in block and not isinstance(block["source_id"], str):
            raise ValueError(f"{block_id}: source_id must be text")
    for exercise in exercises:
        if any(ref not in block_ids for ref in exercise.get("reference_block_ids", [])):
            raise ValueError(f"{exercise['id']}: unknown reference block")
    return data


def public_block(block):
    return {key: copy.deepcopy(block[key]) for key in PUBLIC_BLOCK_FIELDS if key in block}


def public_exercise(exercise):
    evaluation = {"mode": exercise["evaluation"]["mode"]}
    if evaluation["mode"] == "choice":
        evaluation["options"] = copy.deepcopy(exercise["evaluation"]["options"])
    result = {"id": exercise["id"], "concepts": list(exercise["concepts"]), "prompt": exercise["prompt"],
              "response_type": exercise["response_type"], "evaluation": evaluation}
    if exercise.get("reference_block_ids"):
        result["reference_block_ids"] = list(exercise["reference_block_ids"])
    return result


def public_lesson(data):
    return {"schema_version": data["schema_version"], "id": data["id"], "course_id": data["course_id"],
            "chapter_id": data["chapter_id"], "topic_id": data["topic_id"], "title": data["title"],
            "purpose": data["purpose"], "concepts": list(data["concepts"]), "teacher": data["teacher"],
            "blocks": [public_block(block) for block in data["blocks"]],
            "exercises": [public_exercise(exercise) for exercise in data["exercises"]],
            "publication": data["publication"], "updated_at": data["updated_at"]}


def lesson_fingerprint(data):
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()
