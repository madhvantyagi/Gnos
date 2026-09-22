"""CLI for the active GNOS task to inspect and update portal interactions."""

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys

import course_workspace
import portal_interactions
from course_contract import course_fingerprint
from course_workspace import read_plan, workspace_path
from portal_interactions import answer_question, list_pending, read_attempt, review_attempt


ROOT = Path(__file__).resolve().parents[3]


def _workspace_from(args):
    return workspace_path(Path(args.learners_root), args.learner_id, args.course_id)


def _load_object(path: str) -> dict:
    source = Path(path)
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read JSON object from {source}") from exc
    if not isinstance(value, dict):
        raise ValueError("JSON input must be an object")
    return value


def _learner_state():
    scripts = str(ROOT / "skills/learner-tracking/scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import learner_state
    return learner_state


def _response_text(response):
    if not isinstance(response, dict) or len(response) != 1:
        raise ValueError("Stored attempt response is malformed")
    if "text" in response:
        value = response["text"]
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Stored attempt response text is malformed")
        return value
    if "value" in response:
        value = response["value"]
        if isinstance(value, bool) or not isinstance(value, (int, float, str)):
            raise ValueError("Stored attempt response value is malformed")
        return str(value)
    raise ValueError("Stored attempt response is malformed")


def _reviewed_event(workspace, attempt, review, event_id):
    checked_review = portal_interactions._validate_review(review)
    stored_review = attempt.get("review")
    if attempt.get("status") != "reviewed" or not isinstance(stored_review, dict):
        raise ValueError("Attempt requires a stored explicit review before recording evidence")
    if portal_interactions._validate_review(stored_review) != checked_review:
        raise ValueError("Provided review conflicts with the stored attempt review")

    found = portal_interactions._find_exercise(workspace, attempt["exercise_id"])
    submitted_at = attempt.get("submitted_at")
    if not isinstance(submitted_at, str):
        raise ValueError("Attempt submitted_at is malformed")
    try:
        # Learner events use local calendar dates; UTC can already be tomorrow.
        submitted_date = datetime.fromisoformat(submitted_at.replace("Z", "+00:00")).astimezone().date()
    except ValueError as exc:
        raise ValueError("Attempt submitted_at is malformed") from exc
    exercise = found["exercise"]
    concepts = list(exercise.get("concepts", []))
    response = _response_text(attempt.get("response"))
    return {
        "id": event_id,
        "date": submitted_date.isoformat(),
        "course_id": found["plan"]["id"],
        "covered": concepts,
        "attempts": [{
            "concept": concept,
            "task": exercise["prompt"],
            "response": response,
            "result": checked_review["result"],
            "help": checked_review["help"],
            "kind": checked_review["kind"],
        } for concept in concepts],
        "interpretation": checked_review["interpretation"],
        "next_step": checked_review["next_step"],
    }


def _link_evidence_event(workspace, attempt_id, event_id, review):
    original = read_attempt(workspace, attempt_id)
    target = portal_interactions._attempt_path(workspace, original["exercise_id"], attempt_id)
    with course_workspace._workspace_lock(workspace):
        record = portal_interactions._read_record(target)
        if record.get("review") != review:
            raise ValueError("Attempt review changed while recording evidence")
        existing = record.get("evidence_event_id")
        if existing is not None:
            if existing == event_id:
                return
            raise ValueError("Attempt already links a different evidence event")
        record["evidence_event_id"] = event_id
        portal_interactions._write_replace(target, record)


def record_reviewed_attempt(learners_root: Path, learner_id: str, course_id: str,
                            attempt_id: str, review: dict) -> str:
    """Convert one stored explicit portal review into ordinary learner evidence."""
    learner_state = _learner_state()
    workspace = workspace_path(Path(learners_root), learner_id, course_id)
    attempt = read_attempt(workspace, attempt_id)
    if attempt.get("exercise_id") is None:
        raise ValueError("Attempt has no exercise identity")

    state = learner_state.read_state(learners_root, learner_id)
    enrollment = state.get("courses", {}).get(course_id)
    if enrollment is None:
        raise ValueError(f"Learner {learner_id!r} is not enrolled in course {course_id!r}")
    canonical = learner_state.resolve_enrolled_plan(learners_root, learner_id, enrollment)
    workspace_plan = read_plan(workspace)
    if course_fingerprint(canonical) != course_fingerprint(workspace_plan):
        raise ValueError("Portal workspace course does not match the learner's canonical plan")
    if workspace_plan["id"] != course_id:
        raise ValueError("Portal workspace course ID does not match the selected course")

    event_id = f"portal-{attempt_id}"
    event = _reviewed_event(workspace, attempt, review, event_id)
    learner_state.record_event(learners_root, learner_id, event)
    _link_evidence_event(workspace, attempt_id, event_id, review)
    return event_id


def _add_workspace_args(parser):
    parser.add_argument("learner_id")
    parser.add_argument("course_id")
    parser.add_argument("--learners-root", default="learners", type=Path)


def build_parser():
    parser = argparse.ArgumentParser(description="Inspect and update GNOS portal interactions.")
    commands = parser.add_subparsers(dest="command", required=True)

    pending = commands.add_parser("pending", help="list unanswered questions and open-ended reviews")
    _add_workspace_args(pending)

    answer = commands.add_parser("answer-question", help="write an explicit answer to one queued question")
    _add_workspace_args(answer)
    answer.add_argument("--question-id", required=True)
    answer.add_argument("--file", required=True, help="JSON object containing {\"text\": ...}")

    review = commands.add_parser("review-attempt", help="store an explicit review and learner evidence")
    _add_workspace_args(review)
    review.add_argument("--attempt-id", required=True)
    review.add_argument("--file", required=True, help="JSON review object")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    workspace = _workspace_from(args)
    if args.command == "pending":
        result = list_pending(workspace)
    elif args.command == "answer-question":
        result = answer_question(workspace, args.question_id, _load_object(args.file))
    else:
        review = _load_object(args.file)
        review_attempt(workspace, args.attempt_id, review)
        record_reviewed_attempt(args.learners_root, args.learner_id, args.course_id,
                                args.attempt_id, review)
        result = read_attempt(workspace, args.attempt_id)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
