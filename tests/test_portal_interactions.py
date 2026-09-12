"""Tests for private persistence behind the course portal interactions."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/course-design/scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from course_workspace import create_workspace, publish_lesson  # noqa: E402
from portal_interactions import (  # noqa: E402
    answer_question,
    create_question,
    list_pending,
    read_attempt,
    read_attempts,
    request_hint,
    review_attempt,
    save_draft,
    submit_attempt,
)
from test_course_workspace import valid_lesson, valid_v2_course  # noqa: E402


def open_lesson():
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
    })
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
        publish_lesson(self.workspace, open_lesson())

    def tearDown(self):
        self.tempdir.cleanup()

    def test_submitting_twice_preserves_both_attempts(self):
        first = submit_attempt(self.workspace, "predict-change", {"value": 1})
        second = submit_attempt(self.workspace, "predict-change", {"value": 0})

        self.assertNotEqual(first["attempt_id"], second["attempt_id"])
        self.assertEqual(len(read_attempts(self.workspace, "predict-change")), 2)

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

    def test_review_stores_review_without_linking_learner_evidence(self):
        attempt = submit_attempt(self.workspace, "explain-gradient", {"text": "My reasoning"})
        reviewed = review_attempt(self.workspace, attempt["attempt_id"], {
            "result": "needs-repair",
            "help": "none",
            "kind": "independent",
            "interpretation": "The sign rule is not yet connected to change.",
            "next_step": "Revisit the local-change example.",
        })

        self.assertEqual(reviewed["status"], "reviewed")
        self.assertEqual(reviewed["review"]["result"], "needs-repair")
        self.assertIsNone(reviewed["evidence_event_id"])
        self.assertIsNone(read_attempt(self.workspace, attempt["attempt_id"])["evidence_event_id"])


if __name__ == "__main__":
    unittest.main()
