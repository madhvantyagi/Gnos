"""Tests for isolated learner course workspaces."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/course-design/scripts"))
sys.path.insert(0, str(ROOT / "skills/learner-tracking/scripts"))

from course_contract import course_content_fingerprint, course_fingerprint, validate_course
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
import course_workspace as workspace  # noqa: E402
import learner_state  # noqa: E402


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


def valid_lesson(publication="draft", course=None):
    lesson = {
        "schema_version": 2,
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
            "production": {
                "skill_route": "skills/subject/SKILL.md",
                "brief": "Explain what slope predicts.",
                "must_include": ["Local change"],
                "continuity": ["Use the lesson's stated concept."],
                "acceptance_checks": ["The explanation states what slope predicts."],
                "depends_on_block_ids": [],
            },
        }, {
            "id": "slope-equation",
            "type": "equation",
            "concepts": ["math.derivative"],
            "purpose": "Write the local rate as a ratio.",
            "equation": "\\frac{\\Delta y}{\\Delta x}",
            "production": {
                "skill_route": "skills/subject/SKILL.md",
                "brief": "Write the local rate as a ratio.",
                "must_include": ["Change in y", "Change in x"],
                "continuity": ["Reuse the slope explanation's notation."],
                "acceptance_checks": ["The equation shows change in y over change in x."],
                "depends_on_block_ids": ["intro"],
            },
        }, {
            "id": "exercise-block",
            "type": "exercise",
            "concepts": ["math.derivative"],
            "purpose": "Check prediction.",
            "exercise_id": "predict-change",
            "production": {
                "skill_route": "skills/subject/SKILL.md",
                "brief": "Ask the learner to predict the sign of the local change.",
                "must_include": ["A prediction using the slope sign"],
                "continuity": ["Use the ratio introduced in the prior block."],
                "acceptance_checks": ["The exercise checks the stated course concept."],
                "depends_on_block_ids": ["slope-equation"],
            },
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
    if publication == "ready":
        target = validate_course(course if course is not None else valid_v2_course())
        lesson["design_receipt"] = {
            "designed_at": "2026-09-12T16:00:00Z",
            "course_fingerprint": course_content_fingerprint(target),
            "skill_route": "skills/lesson-design/SKILL.md",
            "review": "pass",
        }
    return lesson


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

        for unsafe in (self.root / "other" / "course", self.root / "alex" / "courses" / "../escape"):
            with self.assertRaises(ValueError):
                read_plan(unsafe)

        (self.root / "alex").mkdir()
        (self.root / "alex" / "courses-target").mkdir()
        (self.root / "alex" / "courses").symlink_to(self.root / "alex" / "courses-target", target_is_directory=True)
        with self.assertRaises(ValueError):
            workspace_path(self.root, "alex", "course")

        workspace_target = self.root / "workspace-target"
        workspace_target.mkdir()
        symlink_workspace = self.root / "symlink-user" / "courses"
        symlink_workspace.mkdir(parents=True)
        (symlink_workspace / "gradient-descent").symlink_to(workspace_target, target_is_directory=True)
        with self.assertRaises(ValueError):
            workspace_path(self.root, "symlink-user", "gradient-descent")

        learner_link = self.root / "linked-learner"
        learner_link.symlink_to(self.root / "alex", target_is_directory=True)
        with self.assertRaises(ValueError):
            read_plan(learner_link / "courses" / "gradient-descent")

        # A managed ancestor and a targeted lesson directory are both unsafe.
        safe_root = self.root / "safe"
        safe_root.mkdir()
        path = create_workspace(safe_root, "alex", valid_v2_course())
        (path / "lessons").rename(path / "lessons-real")
        (path / "lessons").symlink_to(path / "lessons-real", target_is_directory=True)
        with self.assertRaises(ValueError):
            publish_lesson(path, valid_lesson())

        (path / "lessons").unlink()
        (path / "lessons-real").rename(path / "lessons")
        target = path / "lesson-target"
        target.mkdir()
        (path / "lessons" / "slope-introduction").symlink_to(target, target_is_directory=True)
        with self.assertRaises(ValueError):
            publish_lesson(path, valid_lesson())

        (path / "lessons" / "slope-introduction").unlink()
        (path / "lessons" / "slope-introduction").mkdir()
        (path / "lessons" / "slope-introduction" / "lesson-target.json").write_text("{}")
        (path / "lessons" / "slope-introduction" / "lesson.json").symlink_to(
            path / "lessons" / "slope-introduction" / "lesson-target.json"
        )
        with self.assertRaises(ValueError):
            publish_lesson(path, valid_lesson())

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

    def test_ready_and_archived_publication_do_not_stale_course_enrollment(self):
        plan = valid_v2_course()
        learner_state.mutate(self.root, "alex", "enroll", plan)
        path = workspace_path(self.root, "alex", plan["id"])

        ready = valid_lesson("ready", plan)
        publish_lesson(path, ready)
        state = learner_state.read_state(self.root, "alex")
        resolved = learner_state.resolve_all_enrolled_plans(self.root, "alex", state)
        self.assertEqual(resolved[plan["id"]]["chapters"][0]["topics"][0]["lesson_ids"],
                         [ready["id"]])

        archived = valid_lesson("archived", plan)
        archived["updated_at"] = "2026-09-12T16:02:00Z"
        publish_lesson(path, archived)
        state = learner_state.read_state(self.root, "alex")
        resolved = learner_state.resolve_all_enrolled_plans(self.root, "alex", state)
        self.assertEqual(resolved[plan["id"]]["chapters"][0]["topics"][0]["lesson_ids"], [])

    def test_published_lesson_does_not_mask_a_meaningful_plan_change(self):
        plan = valid_v2_course()
        learner_state.mutate(self.root, "alex", "enroll", plan)
        path = workspace_path(self.root, "alex", plan["id"])
        publish_lesson(path, valid_lesson("ready", plan))

        changed = read_plan(path)
        changed["title"] = "A meaningfully changed course"
        write_plan(path, changed, expected_fingerprint=course_fingerprint(read_plan(path)))
        state = learner_state.read_state(self.root, "alex")
        with self.assertRaisesRegex(ValueError, "Stale course plan reference"):
            learner_state.resolve_all_enrolled_plans(self.root, "alex", state)

    def test_stale_publication_does_not_leave_an_orphan_lesson(self):
        path = create_workspace(self.root, "alex", valid_v2_course())
        lesson = valid_lesson("ready")
        with mock.patch.object(workspace, "_write_plan_unlocked", side_effect=ConflictError("stale")):
            with self.assertRaises(ConflictError):
                publish_lesson(path, lesson)
        self.assertFalse((path / "lessons" / lesson["id"] / "lesson.json").exists())
        self.assertEqual(read_plan(path)["chapters"][0]["topics"][0]["lesson_ids"], [])
        self.assertFalse((path / ".course.lock").exists())

    def test_plan_write_failure_restores_existing_lesson_atomically(self):
        path = create_workspace(self.root, "alex", valid_v2_course())
        original = valid_lesson("draft")
        publish_lesson(path, original)
        lesson_path = path / "lessons" / original["id"] / "lesson.json"
        original_bytes = lesson_path.read_bytes()

        replacement = valid_lesson("ready")
        replacement["title"] = "Replacement"
        with mock.patch.object(workspace, "_write_plan_unlocked", side_effect=ConflictError("injected")):
            with self.assertRaises(ConflictError):
                publish_lesson(path, replacement)
        self.assertEqual(lesson_path.read_bytes(), original_bytes)
        self.assertEqual(read_plan(path)["chapters"][0]["topics"][0]["lesson_ids"], [])
        self.assertFalse((path / ".course.lock").exists())

    def test_public_plan_writer_is_not_used_inside_publication_lock(self):
        path = create_workspace(self.root, "alex", valid_v2_course())
        lesson = valid_lesson("ready")
        with mock.patch.object(workspace, "write_plan", side_effect=AssertionError("public writer called")):
            publish_lesson(path, lesson)
        self.assertTrue((path / "lessons" / lesson["id"] / "lesson.json").is_file())
        self.assertEqual(read_plan(path)["chapters"][0]["topics"][0]["lesson_ids"], [lesson["id"]])

    def test_lesson_fingerprint_failure_precedes_lesson_and_plan_writes(self):
        path = create_workspace(self.root, "alex", valid_v2_course())
        before_plan = (path / "course.json").read_bytes()
        lesson = valid_lesson("ready")
        with mock.patch.object(workspace, "lesson_fingerprint", side_effect=RuntimeError("hash failed")):
            with self.assertRaises(RuntimeError):
                publish_lesson(path, lesson)
        self.assertEqual((path / "course.json").read_bytes(), before_plan)
        self.assertFalse((path / "lessons" / lesson["id"] / "lesson.json").exists())
        self.assertFalse((path / ".course.lock").exists())

    def test_plan_mutation_lock_is_cleaned_after_success_and_failure(self):
        path = create_workspace(self.root, "alex", valid_v2_course())
        self.assertFalse((path / ".course.lock").exists())
        revised = copy.deepcopy(valid_v2_course())
        revised["revision"] = 2
        write_plan(path, revised, expected_fingerprint=course_fingerprint(valid_v2_course()))
        self.assertFalse((path / ".course.lock").exists())
        with self.assertRaises(ConflictError):
            write_plan(path, valid_v2_course(), expected_fingerprint="stale")
        self.assertFalse((path / ".course.lock").exists())


if __name__ == "__main__":
    unittest.main()
