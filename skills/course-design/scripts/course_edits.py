"""Safe, evidence-aware edits to a learner's living course plan.

The course workspace owns the plan and the learner state owns the enrollment
reference.  A successful edit changes both snapshots while holding the
learner lock and the workspace lock; no edit is allowed to create a second
editable copy of the plan or to rewrite learner evidence.
"""

from copy import deepcopy
from datetime import date
import json
from pathlib import Path
import re

import course_workspace
from course_contract import course_fingerprint, course_topics, slug, validate_course
import learner_state


_ACTIONS = {"rename-topic", "add-topic", "reorder-future-topics", "retire-topic"}
_FUTURE_STATES = {"planned", "provisional"}
_COMPLETED_STATES = {"completed"}
_HEX_FINGERPRINT = re.compile(r"^[0-9a-f]{64}$")


def _nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be nonempty text")
    return value


def _action_type(action):
    if not isinstance(action, dict):
        raise ValueError("Course edit must be an object")
    action_type = action.get("type")
    if action_type not in _ACTIONS:
        raise ValueError(f"Unsupported course edit action: {action_type!r}")
    _nonempty(action.get("reason"), "reason")
    return action_type


def _only_fields(action, allowed):
    unexpected = set(action) - set(allowed)
    if unexpected:
        raise ValueError(f"Course edit contains unsupported fields: {sorted(unexpected)!r}")


def _topic_index(plan, topic_id):
    for chapter_index, chapter in enumerate(plan["chapters"]):
        for topic_index, topic in enumerate(chapter["topics"]):
            if topic["id"] == topic_id:
                return chapter_index, topic_index, chapter, topic
    raise ValueError(f"Unknown topic ID: {topic_id!r}")


def _current(plan):
    current_id = plan["current"]["topic_id"]
    return _topic_index(plan, current_id)


def _require_future_topic(plan, topic_id):
    if not isinstance(topic_id, str):
        raise ValueError("topic_id must be a slug")
    slug(topic_id)
    chapter_index, topic_index, chapter, topic = _topic_index(plan, topic_id)
    if topic_id == plan["current"]["topic_id"] or topic["state"] == "current":
        raise ValueError("The current topic identity cannot be edited")
    if topic["state"] not in _FUTURE_STATES:
        raise ValueError(f"Topic {topic_id!r} is not a future topic")
    return chapter_index, topic_index, chapter, topic


def _iter_values(value):
    """Yield scalar values from evidence-shaped nested data without trusting it."""
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _iter_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_values(item)
    elif isinstance(value, str):
        yield value


def _evidence_for_topic(evidence, topic_id):
    """Find explicit topic/concept references without inferring learner facts."""
    if not isinstance(evidence, dict):
        raise ValueError("evidence must be an object")
    topics = evidence.get("topics")
    if isinstance(topics, dict) and topic_id in topics:
        return True
    if isinstance(evidence.get("topic_ids"), list) and topic_id in evidence["topic_ids"]:
        return True
    if isinstance(evidence.get("completed_topics"), list) and topic_id in evidence["completed_topics"]:
        return True
    events = evidence.get("events")
    if isinstance(events, list):
        for event in events:
            if isinstance(event, dict) and event.get("topic_id") == topic_id:
                return True
    return False


def _evidence_concepts(evidence):
    concepts = set()
    if not isinstance(evidence, dict):
        raise ValueError("evidence must be an object")
    direct = evidence.get("concepts")
    if isinstance(direct, dict):
        concepts.update(key for key in direct if isinstance(key, str))
    elif isinstance(direct, list):
        concepts.update(item for item in direct if isinstance(item, str))
    for event in evidence.get("events", []):
        if not isinstance(event, dict):
            continue
        for key in ("covered", "concepts"):
            values = event.get(key)
            if isinstance(values, list):
                concepts.update(item for item in values if isinstance(item, str))
        for attempt in event.get("attempts", []):
            if isinstance(attempt, dict) and isinstance(attempt.get("concept"), str):
                concepts.add(attempt["concept"])
    return concepts


def _topic_has_completed_evidence(evidence, topic_id):
    if not isinstance(evidence, dict):
        raise ValueError("evidence must be an object")
    completed_topics = evidence.get("completed_topics")
    if isinstance(completed_topics, list) and topic_id in completed_topics:
        return True
    topics = evidence.get("topics")
    if isinstance(topics, dict):
        entry = topics.get(topic_id)
        if isinstance(entry, dict):
            if entry.get("completed") is True:
                return True
            if entry.get("status") in _COMPLETED_STATES:
                return True
    return False


def _check_topic_evidence_policy(plan, topic_id, evidence, *, allow_historical):
    """Protect explicit completion while allowing stable-ID historical edits."""
    _require_future_topic(plan, topic_id)
    if _topic_has_completed_evidence(evidence, topic_id):
        raise ValueError(f"Topic {topic_id!r} has completed evidence")
    # Historical evidence is deliberately not rewritten.  The flag documents
    # which operations are allowed to act on a topic referenced by old events.
    if not allow_historical and _evidence_for_topic(evidence, topic_id):
        raise ValueError(f"Topic {topic_id!r} has historical evidence")


def _apply_rename(plan, action, evidence):
    _only_fields(action, {"type", "topic_id", "title", "reason"})
    topic_id = action.get("topic_id")
    _check_topic_evidence_policy(plan, topic_id, evidence, allow_historical=True)
    title = _nonempty(action.get("title"), "title")
    _, _, _, topic = _topic_index(plan, topic_id)
    if topic["title"] == title:
        raise ValueError("Topic title is already unchanged")
    topic["title"] = title


def _apply_add(plan, action, evidence):
    _only_fields(action, {"type", "chapter_id", "topic", "reason", "index", "position"})
    if evidence:
        # Adding a new topic cannot have historical evidence.  Rejecting a
        # nonempty evidence object here prevents callers from smuggling an
        # inferred learner record into the revision operation.
        topic = action.get("topic")
        if isinstance(topic, dict) and _evidence_for_topic(evidence, topic.get("id")):
            raise ValueError("A new topic cannot already have learner evidence")
    chapter_id = action.get("chapter_id")
    if not isinstance(chapter_id, str):
        raise ValueError("chapter_id must be a slug")
    slug(chapter_id)
    chapter = next((item for item in plan["chapters"] if item["id"] == chapter_id), None)
    if chapter is None:
        raise ValueError(f"Unknown chapter ID: {chapter_id!r}")
    topic = action.get("topic")
    if not isinstance(topic, dict):
        raise ValueError("topic must be an object")
    topic = deepcopy(topic)
    topic_id = topic.get("id")
    slug(topic_id)
    if any(existing["id"] == topic_id for existing in course_topics(plan)):
        raise ValueError(f"Topic ID already exists: {topic_id!r}")
    if topic.get("state") not in _FUTURE_STATES:
        raise ValueError("New topics must be planned or provisional")
    if topic_id == plan["current"]["topic_id"]:
        raise ValueError("The current topic identity cannot be replaced")
    if "index" in action and "position" in action:
        raise ValueError("Use only one of index or position")
    raw_index = action.get("index", action.get("position"))
    if raw_index is None:
        index = len(chapter["topics"])
    elif type(raw_index) is int:
        index = raw_index
    else:
        raise ValueError("index must be an integer")
    if index < 0 or index > len(chapter["topics"]):
        raise ValueError("index is outside the chapter")
    current_chapter_index, current_topic_index, _, _ = _current(plan)
    chapter_index = plan["chapters"].index(chapter)
    if chapter_index == current_chapter_index and index <= current_topic_index:
        raise ValueError("A future topic cannot be inserted before the current topic")
    chapter["topics"].insert(index, topic)


def _order_ids(action):
    values = [key for key in ("topic_ids", "ordered_topic_ids", "order") if key in action]
    if len(values) != 1:
        raise ValueError("reorder-future-topics requires exactly one topic ID list")
    ids = action[values[0]]
    if not isinstance(ids, list) or not ids or any(not isinstance(item, str) for item in ids):
        raise ValueError("topic_ids must be a nonempty list of slugs")
    for item in ids:
        slug(item)
    if len(ids) != len(set(ids)):
        raise ValueError("topic_ids cannot contain duplicates")
    return ids


def _apply_reorder(plan, action, evidence):
    _only_fields(action, {
        "type", "chapter_id", "topic_ids", "ordered_topic_ids", "order", "reason",
    })
    ids = _order_ids(action)
    chapter_id = action.get("chapter_id")
    if chapter_id is None:
        locations = [_topic_index(plan, item) for item in ids]
        chapter_ids = {chapter["id"] for _, _, chapter, _ in locations}
        if len(chapter_ids) != 1:
            raise ValueError("Future topics must be reordered within one chapter")
        chapter = locations[0][2]
    else:
        slug(chapter_id)
        chapter = next((item for item in plan["chapters"] if item["id"] == chapter_id), None)
        if chapter is None:
            raise ValueError(f"Unknown chapter ID: {chapter_id!r}")
    current_chapter_index, current_topic_index, current_chapter, _ = _current(plan)
    if chapter is current_chapter:
        eligible = [
            topic for topic in chapter["topics"][current_topic_index + 1:]
            if topic["state"] in _FUTURE_STATES
        ]
    else:
        eligible = [topic for topic in chapter["topics"] if topic["state"] in _FUTURE_STATES]
    eligible_ids = [topic["id"] for topic in eligible]
    if set(ids) != set(eligible_ids) or len(ids) != len(eligible_ids):
        raise ValueError("Reorder must name every active future topic in the chapter exactly once")
    for topic_id in ids:
        _check_topic_evidence_policy(plan, topic_id, evidence, allow_historical=True)
    replacement = {topic["id"]: topic for topic in eligible}
    ordered = [replacement[item] for item in ids]
    positions = [index for index, topic in enumerate(chapter["topics"])
                 if topic["id"] in replacement]
    for index, topic in zip(positions, ordered):
        chapter["topics"][index] = topic


def _apply_retire(plan, action, evidence):
    _only_fields(action, {"type", "topic_id", "reason"})
    topic_id = action.get("topic_id")
    _check_topic_evidence_policy(plan, topic_id, evidence, allow_historical=True)
    _, _, _, topic = _topic_index(plan, topic_id)
    topic["state"] = "retired"


def _edit_plan(plan, action, evidence):
    action_type = _action_type(action)
    revised = deepcopy(plan)
    if action_type == "rename-topic":
        _apply_rename(revised, action, evidence)
    elif action_type == "add-topic":
        _apply_add(revised, action, evidence)
    elif action_type == "reorder-future-topics":
        _apply_reorder(revised, action, evidence)
    else:
        _apply_retire(revised, action, evidence)

    revised["revision"] = plan["revision"] + 1
    revised["revision_notes"] = list(plan["revision_notes"]) + [{
        "revision": revised["revision"],
        "date": date.today().isoformat(),
        "reason": action["reason"],
    }]
    return validate_course(revised)


def _canonical_identity(workspace):
    path = course_workspace._workspace_path_for_operation(Path(workspace)).absolute()
    learner_id = path.parts[-3]
    course_id = path.parts[-1]
    learners_root = path.parent.parent.parent
    canonical = course_workspace.workspace_path(learners_root, learner_id, course_id)
    if canonical.absolute() != path:
        raise ValueError("Workspace path is not the canonical learner course path")
    return path, learners_root, learner_id, course_id


def _restore(path, data):
    """Restore a byte snapshot without routing through a possibly failing writer."""
    course_workspace._atomic_bytes(path, data)


def _update_enrollment(data, course_id, plan):
    courses = data.get("courses")
    if not isinstance(courses, dict) or course_id not in courses:
        raise ValueError(f"Learner is not enrolled in course {course_id!r}")
    entry = courses[course_id]
    expected_ref = f"courses/{course_id}/course.json"
    if not isinstance(entry, dict) or entry.get("plan_ref") != expected_ref or "plan" in entry:
        raise ValueError("Enrollment must reference the canonical course plan")
    entry["plan_revision"] = plan["revision"]
    entry["plan_fingerprint"] = course_fingerprint(plan)


def apply_course_edit(workspace: Path, action: dict, evidence: dict,
                      expected_fingerprint: str) -> str:
    """Apply one validated future-curriculum edit and return its new fingerprint.

    The caller supplies the fingerprint it displayed.  A stale caller is
    rejected.  Both the canonical plan and its enrollment reference are
    snapshotted before writing so an exception, including ``KeyboardInterrupt``,
    restores the previous pair.
    """
    if not isinstance(expected_fingerprint, str) or not _HEX_FINGERPRINT.fullmatch(expected_fingerprint):
        raise ValueError("expected_fingerprint must be a SHA-256 hex digest")
    if not isinstance(evidence, dict):
        raise ValueError("evidence must be an object")
    path, learners_root, learner_id, course_id = _canonical_identity(workspace)
    state_path = learner_state.state_path(learners_root, learner_id)

    # Existing learner mutations take the learner lock before entering a
    # workspace lock.  Keeping that order avoids deadlock with enrollment and
    # still rechecks the plan after the workspace lock is acquired.
    with learner_state.locked(learners_root, learner_id):
        state = learner_state.read_state(learners_root, learner_id)
        with course_workspace._workspace_lock(path):
            plan = course_workspace.read_plan(path)
            if plan["id"] != course_id:
                raise ValueError("Workspace course ID does not match its path")
            actual_fingerprint = course_fingerprint(plan)
            if actual_fingerprint != expected_fingerprint:
                raise course_workspace.ConflictError("Course changed; refresh before writing")
            enrollment = state.get("courses", {}).get(course_id)
            if not isinstance(enrollment, dict):
                raise ValueError(f"Learner is not enrolled in course {course_id!r}")
            if (enrollment.get("plan_revision") != plan["revision"] or
                    enrollment.get("plan_fingerprint") != actual_fingerprint):
                raise course_workspace.ConflictError(
                    "Enrollment reference is stale; refresh before editing"
                )

            revised = _edit_plan(plan, action, evidence)
            new_fingerprint = course_fingerprint(revised)
            original_plan_bytes = (path / "course.json").read_bytes()
            original_state_bytes = state_path.read_bytes()
            next_state = deepcopy(state)
            _update_enrollment(next_state, course_id, revised)
            try:
                course_workspace._write_plan_unlocked(
                    path, revised, expected_fingerprint=actual_fingerprint
                )
                learner_state.save_state(state_path, next_state)
            except BaseException:
                # Roll back both sides even for an interrupt between writes.
                # Preserve the original exception unless rollback itself fails.
                try:
                    _restore(path / "course.json", original_plan_bytes)
                    _restore(state_path, original_state_bytes)
                except BaseException:
                    pass
                raise
            return new_fingerprint
