"""Tests for private persistence behind the course portal interactions."""

import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/course-design/scripts"))
sys.path.insert(0, str(ROOT / "skills/learner-tracking/scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from course_workspace import create_workspace, publish_lesson  # noqa: E402
from portal_interactions import (  # noqa: E402
    answer_question,
    create_question,
    list_pending,
    read_attempt,
    read_attempts,
    exercise_state,
    reveal_solution,
    request_hint,
    review_attempt,
    save_draft,
    submit_attempt,
)
from manage_interaction import _reviewed_event, record_reviewed_attempt  # noqa: E402
from learner_state import mutate as mutate_learner_state, read_state  # noqa: E402
from test_course_workspace import valid_lesson, valid_v2_course  # noqa: E402


def open_lesson(course=None):
    from course_contract import course_content_fingerprint, validate_course
    from test_course_workspace import valid_v2_course as base_plan
    lesson = valid_lesson("ready")
    lesson["exercises"] = [
        lesson["exercises"][0],
        {
            "id": "explain-gradient",
            "concepts": ["math.derivative"],
            "prompt": "Explain why the sign predicts the change.",
            "response_type": "long-text",
            "evaluation": {"mode": "manual"},
            "success_criteria": ["Connects sign and local change."],
        },
    ]
    lesson["blocks"].append({
        "id": "explain-block",
        "type": "exercise",
        "concepts": ["math.derivative"],
        "purpose": "Check explanation.",
        "exercise_id": "explain-gradient",
        "production": {
            "skill_route": "skills/subject/SKILL.md",
            "brief": "Ask the learner to explain how slope sign predicts local change.",
            "must_include": ["A connection between sign and change"],
            "continuity": ["Build on the slope and ratio blocks."],
            "acceptance_checks": ["The prompt requires an explanation of the relationship."],
            "depends_on_block_ids": ["slope-equation"],
        },
    })
    target = validate_course(course if course is not None else base_plan())
    lesson["design_receipt"] = {
        "designed_at": lesson["updated_at"],
        "course_fingerprint": course_content_fingerprint(target),
        "skill_route": "skills/lesson-design/SKILL.md",
        "review": "pass",
    }
    return lesson


class PortalInteractionTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        plan = valid_v2_course()
        plan["chapters"][0]["topics"][0]["lesson_ids"] = ["slope-introduction"]
        plan["chapters"][0]["topics"][0]["exercise_ids"] = [
            "predict-change", "explain-gradient",
        ]
        self.workspace = create_workspace(self.root, "alex", plan)
        publish_lesson(self.workspace, open_lesson(plan))
        mutate_learner_state(self.root, "alex", "enroll", plan)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_submitting_twice_preserves_both_attempts(self):
        first = submit_attempt(self.workspace, "predict-change", {"value": 1})
        second = submit_attempt(self.workspace, "predict-change", {"value": 0})

        self.assertNotEqual(first["attempt_id"], second["attempt_id"])
        self.assertEqual(len(read_attempts(self.workspace, "predict-change")), 2)

    def test_reveal_preserves_response_and_marks_subsequent_attempt_as_assisted(self):
        first = submit_attempt(self.workspace, 'predict-change', {'value': 0})
        reveal_solution(self.workspace, 'predict-change', first['id'])
        self.assertEqual(read_attempt(self.workspace, first['id'])['response'], {'value': 0})
        second = submit_attempt(self.workspace, 'predict-change', {'value': 1})
        self.assertTrue(second['solution_seen_before_submission'])
        self.assertEqual(exercise_state(self.workspace, 'predict-change')['attempt']['id'], second['id'])

    @unittest.skipUnless(hasattr(time, 'tzset'), 'Requires a process-local timezone setting')
    def test_review_uses_local_submission_date_across_utc_midnight(self):
        with mock.patch('portal_interactions.utc_now', return_value='2026-09-13T01:00:00Z'):
            attempt = submit_attempt(self.workspace, 'predict-change', {'value': 1})
        review = {'result': 'correct', 'help': 'none', 'kind': 'retrieval',
                  'interpretation': 'Correct sign.', 'next_step': 'Try another example.'}
        reviewed = review_attempt(self.workspace, attempt['id'], review)
        try:
            with mock.patch.dict(os.environ, {'TZ': 'America/New_York'}):
                time.tzset()
                event = _reviewed_event(self.workspace, reviewed, review, 'test-event')
                self.assertEqual(event['date'], '2026-09-12')
        finally:
            time.tzset()

    def test_open_ended_attempt_waits_for_review(self):
        result = submit_attempt(self.workspace, "explain-gradient", {"text": "My reasoning"})

        self.assertEqual(result["status"], "awaiting-review")
        self.assertNotIn("success_criteria", result)

    def test_deterministic_feedback_does_not_disclose_private_answer(self):
        result = submit_attempt(self.workspace, "predict-change", {"value": 0})

        self.assertEqual(result["status"], "checked")
        self.assertNotIn("answer", result)
        self.assertNotIn("1", result["feedback"])

    def test_duplicate_attempt_id_is_idempotent_but_conflicts_fail(self):
        first = submit_attempt(self.workspace, "predict-change", {"value": 1}, attempt_id="attempt-fixed")
        same = submit_attempt(self.workspace, "predict-change", {"value": 1}, attempt_id="attempt-fixed")

        self.assertEqual(first, same)
        with self.assertRaises(ValueError):
            submit_attempt(self.workspace, "predict-change", {"value": 0}, attempt_id="attempt-fixed")
        self.assertEqual(len(read_attempts(self.workspace, "predict-change")), 1)

    def test_draft_is_replaceable_and_hint_is_recorded_separately(self):
        draft = save_draft(self.workspace, "explain-gradient", {"text": "first"})
        replacement = save_draft(self.workspace, "explain-gradient", {"text": "revised"})
        hint = request_hint(self.workspace, "explain-gradient")

        self.assertEqual(draft["exercise_id"], replacement["exercise_id"])
        self.assertEqual(replacement["response"], {"text": "revised"})
        self.assertEqual(hint["status"], "requested")
        self.assertEqual(len(read_attempts(self.workspace, "explain-gradient")), 0)

    def test_question_is_saved_without_invoking_a_model(self):
        result = create_question(self.workspace, {
            "text": "Why does the sign matter?",
            "context": {
                "course_id": "gradient-descent",
                "chapter_id": "change",
                "topic_id": "local-change",
                "lesson_id": "slope-introduction",
                "block_id": "intro",
                "exercise_id": "explain-gradient",
            },
        })

        self.assertEqual(result["status"], "pending")
        self.assertNotIn("answer", result)
        self.assertEqual(list_pending(self.workspace)["questions"][0]["id"], result["id"])

    def test_question_rejects_unscoped_paths_and_ids(self):
        with self.assertRaises(ValueError):
            create_question(self.workspace, {
                "text": "No path injection",
                "path": "../../secret",
                "context": {"course_id": "gradient-descent"},
            })
        with self.assertRaises(ValueError):
            create_question(self.workspace, {
                "text": "Wrong block",
                "context": {
                    "course_id": "gradient-descent",
                    "lesson_id": "slope-introduction",
                    "block_id": "missing-block",
                },
            })

    def test_answer_question_requires_explicit_text_and_is_idempotent(self):
        question = create_question(self.workspace, {
            "text": "Why does the sign matter?",
            "context": {"course_id": "gradient-descent", "lesson_id": "slope-introduction"},
        })
        answered = answer_question(self.workspace, question["id"], "Because slope predicts local change.")
        repeated = answer_question(self.workspace, question["id"], "Because slope predicts local change.")

        self.assertEqual(answered, repeated)
        self.assertEqual(answered["status"], "answered")
        self.assertEqual(answered["answer"], "Because slope predicts local change.")
        with self.assertRaises(ValueError):
            answer_question(self.workspace, question["id"], "A different answer")

    def test_explicit_question_retry_is_idempotent_across_new_timestamps(self):
        request = {
            "text": "Why does the sign matter?",
            "context": {"course_id": "gradient-descent", "lesson_id": "slope-introduction"},
        }
        with mock.patch("portal_interactions.utc_now", side_effect=[
            "2026-09-12T16:00:00Z", "2026-09-12T16:01:00Z",
        ]):
            first = create_question(self.workspace, request, question_id="question-fixed")
            second = create_question(self.workspace, request, question_id="question-fixed")

        self.assertEqual(second, first)
        self.assertEqual(second["created_at"], first["created_at"])
        with self.assertRaises(ValueError):
            create_question(self.workspace, {
                "text": "A different question",
                "context": request["context"],
            }, question_id="question-fixed")

    def test_review_stores_review_without_linking_learner_evidence(self):
        attempt = submit_attempt(self.workspace, "explain-gradient", {"text": "My reasoning"})
        reviewed = review_attempt(self.workspace, attempt["attempt_id"], {
            "result": "incorrect",
            "help": "none",
            "kind": "application",
            "interpretation": "The sign rule is not yet connected to change.",
            "next_step": "Revisit the local-change example.",
        })

        self.assertEqual(reviewed["status"], "reviewed")
        self.assertEqual(reviewed["review"]["result"], "incorrect")
        self.assertIsNone(reviewed["evidence_event_id"])
        self.assertIsNone(read_attempt(self.workspace, attempt["attempt_id"])["evidence_event_id"])

    def test_review_rejects_values_outside_existing_evidence_enums(self):
        attempt = submit_attempt(self.workspace, "explain-gradient", {"text": "My reasoning"})
        valid = {
            "result": "correct",
            "help": "none",
            "kind": "retrieval",
            "interpretation": "The learner recalled the sign rule.",
            "next_step": "Apply it to a new example.",
        }
        for field, invalid in {
            "result": "needs-repair",
            "help": "independent",
            "kind": "transfer-without-evidence",
        }.items():
            candidate = dict(valid)
            candidate[field] = invalid
            with self.assertRaises(ValueError):
                review_attempt(self.workspace, attempt["attempt_id"], candidate)

    def test_unreviewed_attempt_cannot_become_evidence(self):
        attempt = submit_attempt(self.workspace, "explain-gradient", {"text": "My reasoning"},
                                 attempt_id="attempt-unreviewed")

        with self.assertRaises(ValueError):
            record_reviewed_attempt(self.root, "alex", "gradient-descent",
                                    attempt["attempt_id"], {})
        self.assertEqual(read_state(self.root, "alex")["events"], [])

    def test_review_creates_one_linked_evidence_event_from_stored_work(self):
        attempt = submit_attempt(self.workspace, "explain-gradient", {"text": "My reasoning"},
                                 attempt_id="attempt-reviewed")
        review = {
            "result": "correct",
            "help": "none",
            "kind": "application",
            "interpretation": "The learner connected sign and local change.",
            "next_step": "Apply the sign rule to a new example.",
        }
        review_attempt(self.workspace, attempt["attempt_id"], review)

        event_id = record_reviewed_attempt(
            self.root, "alex", "gradient-descent", attempt["attempt_id"], review
        )
        linked = read_attempt(self.workspace, attempt["attempt_id"])
        state = read_state(self.root, "alex")

        self.assertEqual(event_id, "portal-attempt-reviewed")
        self.assertEqual(linked["evidence_event_id"], event_id)
        self.assertEqual(len(state["events"]), 1)
        event = state["events"][0]
        self.assertEqual(event["id"], event_id)
        self.assertEqual(event["course_id"], "gradient-descent")
        self.assertEqual(event["covered"], ["math.derivative"])
        self.assertEqual(event["attempts"][0]["task"],
                         "Explain why the sign predicts the change.")
        self.assertEqual(event["attempts"][0]["response"], "My reasoning")
        self.assertEqual(event["attempts"][0]["result"], "correct")

    def test_link_failure_leaves_event_for_retry_without_duplicate(self):
        attempt = submit_attempt(self.workspace, "explain-gradient", {"text": "My reasoning"},
                                 attempt_id="attempt-retry")
        review = {
            "result": "correct",
            "help": "none",
            "kind": "application",
            "interpretation": "The response is sound.",
            "next_step": "Transfer the idea to a new slope.",
        }
        review_attempt(self.workspace, attempt["attempt_id"], review)

        with mock.patch("portal_interactions._write_replace", side_effect=OSError("link failed")):
            with self.assertRaises(OSError):
                record_reviewed_attempt(self.root, "alex", "gradient-descent",
                                        attempt["attempt_id"], review)
        self.assertEqual(len(read_state(self.root, "alex")["events"]), 1)
        self.assertIsNone(read_attempt(self.workspace, attempt["attempt_id"])["evidence_event_id"])

        repeated = record_reviewed_attempt(
            self.root, "alex", "gradient-descent", attempt["attempt_id"], review
        )
        self.assertEqual(repeated, "portal-attempt-retry")
        self.assertEqual(len(read_state(self.root, "alex")["events"]), 1)
        self.assertEqual(read_attempt(self.workspace, attempt["attempt_id"])["evidence_event_id"], repeated)


if __name__ == "__main__":
    unittest.main()
