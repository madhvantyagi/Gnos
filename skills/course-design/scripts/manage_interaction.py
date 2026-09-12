"""CLI for the active GNOS task to inspect and update portal interactions."""

import argparse
import json
from pathlib import Path
import sys

from course_workspace import workspace_path
from portal_interactions import answer_question, list_pending, review_attempt


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

    review = commands.add_parser("review-attempt", help="store an explicit review without learner evidence")
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
        result = review_attempt(workspace, args.attempt_id, _load_object(args.file))
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
