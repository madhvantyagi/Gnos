"""Tests for isolated learner course workspaces."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/course-design/scripts"))

from course_contract import course_fingerprint
from course_workspace import (  # noqa: E402
    ConflictError,
    atomic_json,
    create_workspace,
    publish_lesson,
    read_plan,
    write_plan,
    workspace_path,
)
from lesson_contract import lesson_fingerprint  # noqa: E402


def valid_v2_course():
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
            }],
        }],
    }


def valid_lesson(publication="draft"):
    return {
        "schema_version": 1,
        "id": "slope-introduction",
        "course_id": "gradient-descent",
        "chapter_id": "change",
        "topic_id": "local-change",
        "title": "Slope",
        "purpose": "Predict change.",
        "concepts": ["math.derivative"],
        "teacher": "math",
        "skill_routes": ["skills/subject/SKILL.md"],
        "assumptions": ["The learner can read a graph."],
        "blocks": [{
            "id": "intro",
            "type": "explanation",
            "concepts": ["math.derivative"],
            "purpose": "Introduce slope.",
            "text": "Slope predicts local change.",
        }, {
            "id": "exercise-block",
            "type": "exercise",
            "concepts": ["math.derivative"],
            "purpose": "Check prediction.",
            "exercise_id": "predict-change",
        }],
        "exercises": [{
            "id": "predict-change",
            "concepts": ["math.derivative"],
            "prompt": "Predict the sign.",
            "response_type": "numeric",
            "evaluation": {"mode": "numeric", "answer": 1, "tolerance": 0.1},
            "success_criteria": ["Uses the sign of slope."],
        }],
        "publication": publication,
        "created_at": "2026-09-12T16:00:00Z",
        "updated_at": "2026-09-12T16:00:00Z",
    }


class CourseWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_workspace_is_inside_learner_and_contains_initial_manifest(self):
        path = create_workspace(self.root, "alex", valid_v2_course())
        self.assertEqual(path, self.root / "alex" / "courses" / "gradient-descent")
        self.assertTrue((path / "course.json").is_file())
        self.assertEqual(json.loads((path / "manifest.json").read_text())["artifacts"], [])
        for relative in (
            "lessons", "exercises", "submissions", "questions", "artifacts",
            "artifacts/videos", "artifacts/animations", "artifacts/diagrams",
            "artifacts/simulations", "artifacts/documents", "artifacts/generated",
            "archive", "site",
        ):
            self.assertTrue((path / relative).is_dir(), relative)

    def test_workspace_rejects_traversal_and_symlinked_course_directories(self):
        with self.assertRaises(ValueError):
            workspace_path(self.root, "../alex", "course")

        (self.root / "alex").mkdir()
        (self.root / "alex" / "courses-target").mkdir()
        (self.root / "alex" / "courses").symlink_to(self.root / "alex" / "courses-target", target_is_directory=True)
        with self.assertRaises(ValueError):
            workspace_path(self.root, "alex", "course")

    def test_plan_writes_are_atomic_and_reject_stale_fingerprints(self):
        plan = valid_v2_course()
        path = create_workspace(self.root, "alex", plan)
        revised = copy.deepcopy(plan)
        revised["revision"] = 2
        with self.assertRaises(ConflictError):
            write_plan(path, revised, expected_fingerprint="stale")
        self.assertEqual(read_plan(path), plan)

        fingerprint = write_plan(path, revised, expected_fingerprint=course_fingerprint(plan))
        self.assertEqual(fingerprint, course_fingerprint(revised))
        self.assertEqual(read_plan(path), revised)

    def test_atomic_json_replaces_complete_snapshot(self):
        target = self.root / "snapshot.json"
        atomic_json(target, {"new": [1, 2, 3]})
        self.assertEqual(json.loads(target.read_text()), {"new": [1, 2, 3]})
        self.assertEqual(list(self.root.glob(".snapshot.json.*.tmp")), [])

    def test_draft_lesson_is_saved_but_ready_lesson_is_listed(self):
        path = create_workspace(self.root, "alex", valid_v2_course())
        draft = valid_lesson("draft")
        self.assertEqual(publish_lesson(path, draft), lesson_fingerprint(draft))
        lesson_path = path / "lessons" / draft["id"] / "lesson.json"
        self.assertTrue(lesson_path.is_file())
        self.assertEqual(read_plan(path)["chapters"][0]["topics"][0]["lesson_ids"], [])

        ready = valid_lesson("ready")
        ready["updated_at"] = "2026-09-12T16:01:00Z"
        self.assertEqual(publish_lesson(path, ready), lesson_fingerprint(ready))
        self.assertEqual(read_plan(path)["chapters"][0]["topics"][0]["lesson_ids"], [ready["id"]])

        archived = valid_lesson("archived")
        archived["updated_at"] = "2026-09-12T16:02:00Z"
        publish_lesson(path, archived)
        self.assertEqual(read_plan(path)["chapters"][0]["topics"][0]["lesson_ids"], [])


if __name__ == "__main__":
    unittest.main()
