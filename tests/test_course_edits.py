"""Tests for safe, evidence-aware living-course revisions."""

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/course-design/scripts"))
sys.path.insert(0, str(ROOT / "skills/learner-tracking/scripts"))

import course_edits  # noqa: E402
from course_contract import course_fingerprint  # noqa: E402
from course_workspace import create_workspace, read_plan  # noqa: E402
import learner_state  # noqa: E402


def living_course():
    """Return a small valid v2 route with a current and two future topics."""
    return {
        "schema_version": 2,
        "id": "gradient-descent",
        "title": "From slope to a working optimizer",
        "goal": "Explain, implement, and diagnose gradient descent.",
        "revision": 1,
        "revision_notes": [{
            "revision": 1,
            "date": "2026-09-12",
            "reason": "Initial researched route.",
        }],
        "starting_evidence": [],
        "assumptions": ["Single-variable derivative knowledge is unverified."],
        "sources": {
            "openstax-calculus-1": {
                "title": "Calculus Volume 1",
                "url": "https://openstax.org/details/books/calculus-volume-1",
                "type": "textbook",
                "checked_on": "2026-09-12",
                "sections": ["3.5 The Chain Rule"],
                "verification_notes": "Section heading and access checked.",
            }
        },
        "current": {
            "chapter_id": "change",
            "topic_id": "local-change",
            "next_step": "Check slope as local change.",
        },
        "chapters": [{
            "id": "change",
            "title": "Local change",
            "state": "current",
            "topics": [{
                "id": "local-change",
                "title": "Slope as local change",
                "state": "current",
                "outcome": "Predict the sign of a small function change.",
                "subject": "math",
                "teacher": "math",
                "supporting_subjects": [],
                "supporting_teachers": [],
                "skill_routes": [
                    "skills/subject/SKILL.md",
                    "skills/subject/subjects/math.md",
                ],
                "concepts": ["math.derivative"],
                "prerequisites": [],
                "minutes": 25,
                "resource_ids": ["openstax-calculus-1"],
                "exercise_ids": ["predict-change"],
                "lesson_ids": [],
            }, {
                "id": "step-size",
                "title": "Choosing a step",
                "state": "planned",
                "outcome": "Choose a stable step size.",
                "subject": "math",
                "teacher": "math",
                "supporting_subjects": [],
                "supporting_teachers": [],
                "skill_routes": [
                    "skills/subject/SKILL.md",
                    "skills/subject/subjects/math.md",
                ],
                "concepts": ["math.step-size"],
                "prerequisites": ["local-change"],
                "minutes": 25,
                "resource_ids": ["openstax-calculus-1"],
                "exercise_ids": ["choose-step"],
                "lesson_ids": [],
            }, {
                "id": "gradient",
                "title": "Following the gradient",
                "state": "provisional",
                "outcome": "Explain why the gradient changes the parameters.",
                "subject": "math",
                "teacher": "math",
                "supporting_subjects": [],
                "supporting_teachers": [],
                "skill_routes": [
                    "skills/subject/SKILL.md",
                    "skills/subject/subjects/math.md",
                ],
                "concepts": ["math.gradient"],
                "prerequisites": ["step-size"],
                "minutes": 30,
                "resource_ids": ["openstax-calculus-1"],
                "exercise_ids": ["follow-gradient"],
                "lesson_ids": [],
            }],
        }],
    }


def evidence_for(*, completed=False, concept="math.gradient"):
    return {
        "topics": {"gradient": {"concepts": [concept], "completed": completed}},
        "events": [{"id": "portal-old-event", "topic_id": "gradient", "concept": concept}],
    }


class CourseEditTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.plan = living_course()
        self.workspace = create_workspace(self.root, "alex", self.plan)
        learner_state.mutate(self.root, "alex", "enroll", self.plan)

    def tearDown(self):
        self.tempdir.cleanup()

    def fingerprint(self):
        return course_fingerprint(read_plan(self.workspace))

    def enrollment(self):
        return learner_state.read_state(self.root, "alex")["courses"]["gradient-descent"]

    def topic(self, topic_id):
        return next(
            topic for chapter in read_plan(self.workspace)["chapters"]
            for topic in chapter["topics"] if topic["id"] == topic_id
        )

    def test_rename_future_topic_increments_revision_and_records_reason(self):
        old_fingerprint = self.fingerprint()
        new_fingerprint = course_edits.apply_course_edit(
            self.workspace,
            {
                "type": "rename-topic",
                "topic_id": "step-size",
                "title": "Choosing a stable step",
                "reason": "Learner requested clearer wording",
            },
            evidence={},
            expected_fingerprint=old_fingerprint,
        )

        revised = read_plan(self.workspace)
        self.assertEqual(new_fingerprint, course_fingerprint(revised))
        self.assertEqual(revised["revision"], 2)
        self.assertEqual(self.topic("step-size")["title"], "Choosing a stable step")
        self.assertEqual(len(revised["revision_notes"]), 2)
        self.assertEqual(revised["revision_notes"][-1]["revision"], 2)
        self.assertEqual(revised["revision_notes"][-1]["reason"],
                         "Learner requested clearer wording")
        enrolled = self.enrollment()
        self.assertEqual(enrolled["plan_revision"], 2)
        self.assertEqual(enrolled["plan_fingerprint"], new_fingerprint)

    def test_retire_topic_with_evidence_keeps_id_and_events(self):
        before = json.loads((self.root / "alex" / "state.json").read_text())
        old_fingerprint = self.fingerprint()
        new_fingerprint = course_edits.apply_course_edit(
            self.workspace,
            {"type": "retire-topic", "topic_id": "gradient",
             "reason": "The learner chose a different optimization route."},
            evidence=evidence_for(),
            expected_fingerprint=old_fingerprint,
        )

        self.assertEqual(self.topic("gradient")["state"], "retired")
        self.assertEqual(self.topic("gradient")["id"], "gradient")
        after = json.loads((self.root / "alex" / "state.json").read_text())
        self.assertEqual(after["events"], before["events"])
        expected_enrollment = dict(before["courses"]["gradient-descent"])
        expected_enrollment["plan_revision"] = 2
        expected_enrollment["plan_fingerprint"] = new_fingerprint
        self.assertEqual(after["courses"]["gradient-descent"], expected_enrollment)
        self.assertEqual(learner_state.read_state(self.root, "alex")["events"], [])
        self.assertEqual(self.enrollment()["plan_fingerprint"], new_fingerprint)

    def test_add_and_reorder_future_topics_preserve_current_identity(self):
        added = copy.deepcopy(self.plan["chapters"][0]["topics"][1])
        added.update({
            "id": "momentum",
            "title": "Momentum in updates",
            "outcome": "Explain how momentum changes an update.",
            "concepts": ["math.momentum"],
            "prerequisites": ["local-change"],
            "exercise_ids": ["explain-momentum"],
            "state": "planned",
        })
        fingerprint = course_edits.apply_course_edit(
            self.workspace,
            {"type": "add-topic", "chapter_id": "change", "topic": added,
             "reason": "A missing bridge was identified from the latest attempt."},
            evidence={}, expected_fingerprint=self.fingerprint(),
        )
        fingerprint = course_edits.apply_course_edit(
            self.workspace,
            {"type": "reorder-future-topics", "chapter_id": "change",
             "topic_ids": ["momentum", "step-size", "gradient"],
             "reason": "Teach the visual intuition before the step-size details."},
            evidence={}, expected_fingerprint=fingerprint,
        )

        plan = read_plan(self.workspace)
        self.assertEqual(plan["current"]["topic_id"], "local-change")
        self.assertEqual([topic["id"] for topic in plan["chapters"][0]["topics"]],
                         ["local-change", "momentum", "step-size", "gradient"])
        self.assertEqual(plan["revision"], 3)
        self.assertEqual(self.enrollment()["plan_fingerprint"], fingerprint)

    def test_rejects_current_identity_id_and_concept_mutations(self):
        for action in (
            {"type": "rename-topic", "topic_id": "local-change", "title": "New",
             "reason": "No"},
            {"type": "rename-topic", "topic_id": "step-size", "id": "renamed",
             "title": "New", "reason": "No"},
            {"type": "rename-topic", "topic_id": "step-size", "title": "New",
             "concepts": ["math.other"], "reason": "No"},
        ):
            before_plan = (self.workspace / "course.json").read_bytes()
            before_state = (self.root / "alex" / "state.json").read_bytes()
            with self.assertRaises(ValueError):
                course_edits.apply_course_edit(
                    self.workspace, action, evidence={},
                    expected_fingerprint=self.fingerprint(),
                )
            self.assertEqual((self.workspace / "course.json").read_bytes(), before_plan)
            self.assertEqual((self.root / "alex" / "state.json").read_bytes(), before_state)

    def test_rejects_retiring_topic_with_completed_evidence(self):
        with self.assertRaises(ValueError):
            course_edits.apply_course_edit(
                self.workspace,
                {"type": "retire-topic", "topic_id": "gradient",
                 "reason": "Remove it."},
                evidence=evidence_for(completed=True),
                expected_fingerprint=self.fingerprint(),
            )
        self.assertEqual(self.topic("gradient")["state"], "provisional")
        self.assertEqual(read_plan(self.workspace)["revision"], 1)

    def test_stale_fingerprint_rejects_without_changing_plan_or_enrollment(self):
        before_plan = (self.workspace / "course.json").read_bytes()
        before_state = (self.root / "alex" / "state.json").read_bytes()
        with self.assertRaises(ValueError):
            course_edits.apply_course_edit(
                self.workspace,
                {"type": "rename-topic", "topic_id": "step-size",
                 "title": "New", "reason": "Clarify."},
                evidence={}, expected_fingerprint="0" * 64,
            )
        self.assertEqual((self.workspace / "course.json").read_bytes(), before_plan)
        self.assertEqual((self.root / "alex" / "state.json").read_bytes(), before_state)

    def test_write_failure_rolls_back_both_plan_and_enrollment(self):
        before_plan = (self.workspace / "course.json").read_bytes()
        before_state = (self.root / "alex" / "state.json").read_bytes()
        with mock.patch.object(
            course_edits.course_workspace, "_write_plan_unlocked",
            side_effect=OSError("injected write failure"),
        ):
            with self.assertRaises(OSError):
                course_edits.apply_course_edit(
                    self.workspace,
                    {"type": "rename-topic", "topic_id": "step-size",
                     "title": "New", "reason": "Clarify."},
                    evidence={}, expected_fingerprint=self.fingerprint(),
                )
        self.assertEqual((self.workspace / "course.json").read_bytes(), before_plan)
        self.assertEqual((self.root / "alex" / "state.json").read_bytes(), before_state)
        self.assertFalse((self.workspace / ".course.lock").exists())
        self.assertFalse((self.root / "alex" / ".lock").exists())


if __name__ == "__main__":
    unittest.main()
