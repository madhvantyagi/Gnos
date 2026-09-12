"""Pure, conservative progress views for validated course plans and events."""

import copy

from course_contract import course_topics


_STATUS_ORDER = {
    "not-started": 0,
    "exposed": 1,
    "practicing": 2,
    "demonstrated": 3,
    "retained": 4,
}


def summarize_concepts(events):
    """Summarize observed concept evidence without mutating any event."""
    concepts = {}
    successful_dates = {}

    for event in sorted(events, key=lambda item: item["date"]):
        for concept in event["covered"]:
            concepts.setdefault(concept, {"status": "exposed", "attempts": 0})
        for attempt in event["attempts"]:
            concept = attempt["concept"]
            entry = concepts.setdefault(concept, {"status": "exposed", "attempts": 0})
            entry["attempts"] += 1
            independent_success = (
                attempt["result"] == "correct" and attempt["help"] == "none"
            )
            had_earlier_success = bool(successful_dates.get(concept))
            status = "practicing"
            if independent_success:
                status = (
                    "retained"
                    if had_earlier_success and attempt["kind"] in ("retrieval", "transfer")
                    else "demonstrated"
                )
                successful_dates.setdefault(concept, []).append(event["date"])
            entry.update(
                status=status,
                last_date=event["date"],
                latest=copy.deepcopy(attempt),
            )
            if independent_success:
                entry["_has_independent_success"] = True
            elif attempt["result"] in ("partial", "incorrect"):
                entry["_latest_failure"] = True

    for entry in concepts.values():
        needs_repair = (
            entry.get("_has_independent_success", False)
            and entry.get("_latest_failure", False)
            and entry.get("latest", {}).get("result") in ("partial", "incorrect")
        )
        entry["display_status"] = "needs-repair" if needs_repair else entry["status"]
        entry.pop("_has_independent_success", None)
        entry.pop("_latest_failure", None)
    return concepts


def conservative_topic_status(statuses):
    """Return the weakest evidence status among a topic's relevant concepts."""
    if not statuses:
        return "not-started"
    return min(
        (status.get("status", "not-started") for status in statuses),
        key=lambda status: _STATUS_ORDER.get(status, 0),
    )


def derive_course_progress(plan, events):
    """Build a read-only hierarchical progress view for one validated course."""
    relevant_events = [event for event in events if event.get("course_id") == plan["id"]]
    concept_summary = summarize_concepts(relevant_events)
    topics = {}
    for topic in course_topics(plan):
        statuses = [
            concept_summary.get(concept, {"status": "not-started", "attempts": 0})
            for concept in topic["concepts"]
        ]
        topics[topic["id"]] = {
            "planning_state": topic["state"],
            "evidence": conservative_topic_status(statuses),
            "concept_ids": list(topic["concepts"]),
            "attempt_count": sum(status.get("attempts", 0) for status in statuses),
        }

    chapters = {}
    for chapter in plan["chapters"]:
        chapter_topics = [topics[topic["id"]] for topic in chapter["topics"]]
        chapters[chapter["id"]] = {
            "planning_state": chapter["state"],
            "evidence": conservative_topic_status(chapter_topics),
            "topic_ids": [topic["id"] for topic in chapter["topics"]],
            "attempt_count": sum(topic["attempt_count"] for topic in chapter_topics),
        }

    return {
        "course_id": plan["id"],
        "current": copy.deepcopy(plan.get("current")),
        "chapters": chapters,
        "topics": topics,
        "concepts": concept_summary,
    }
