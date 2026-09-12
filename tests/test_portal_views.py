"""Tests for the redacted, read-only course portal view model."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/course-design/scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from artifact_manifest import register_artifact  # noqa: E402
from course_workspace import create_workspace, publish_lesson  # noqa: E402
from portal_views import (  # noqa: E402
    build_portal_view,
    public_artifact,
    recent_and_older,
    ready_lessons,
)
from test_course_workspace import valid_lesson, valid_v2_course  # noqa: E402


def ready_artifact(artifact_id="gradient-video", artifact_type="voice-animation",
                   topic_id="local-change", updated_at="2026-09-12T16:00:00Z"):
    return {
        "id": artifact_id,
        "type": artifact_type,
        "title": f"Artifact {artifact_id}",
        "purpose": "Show the change clearly.",
        "concepts": ["math.derivative"],
        "chapter_id": "change",
        "topic_id": topic_id,
        "lesson_id": "slope-introduction",
        "location": {"path": f"artifacts/generated/{artifact_id}.bin"},
        "mime_type": "application/octet-stream",
        "metadata": {
            "duration_seconds": 42,
            "thumbnail": "thumbnail-artifact",
            "solution": "private metadata must not be public",
            "accepted": ["private answer"],
        },
        "status": "ready",
        "created_at": "2026-09-12T16:00:00Z",
        "updated_at": updated_at,
    }


class PortalViewTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        plan = valid_v2_course()
        plan["chapters"][0]["topics"][0]["lesson_ids"] = ["slope-introduction"]
        self.workspace = create_workspace(self.root, "alex", plan)
        lesson = valid_lesson("ready")
        publish_lesson(self.workspace, lesson)
        artifact_path = self.workspace / "artifacts/generated/gradient-video.bin"
        artifact_path.write_bytes(b"artifact")
        register_artifact(self.workspace, ready_artifact())
        self.learner_summary = {
            "course_progress": {
                "course_id": "gradient-descent",
                "current": {
                    "chapter_id": "change",
                    "topic_id": "local-change",
                    "next_step": "Check slope as local change.",
                },
                "chapters": {
                    "change": {
                        "planning_state": "current",
                        "evidence": "practicing",
                        "topic_ids": ["local-change"],
                        "attempt_count": 1,
                    },
                },
                "topics": {
                    "local-change": {
                        "planning_state": "current",
                        "evidence": "practicing",
                        "concept_ids": ["math.derivative"],
                        "attempt_count": 1,
                    },
                },
            },
        }

    def tearDown(self):
        self.tempdir.cleanup()

    def test_portal_view_contains_current_frontier_and_hierarchical_contents(self):
        view = build_portal_view(self.workspace, self.learner_summary)

        self.assertEqual(view["course"]["current"]["topic_id"], "local-change")
        self.assertEqual(view["contents"][0]["topics"][0]["progress"]["evidence"], "practicing")
        self.assertEqual(view["contents"][0]["topics"][0]["lesson_ids"], ["slope-introduction"])
        self.assertEqual(view["lessons"]["recent"][0]["topic_id"], "local-change")

    def test_portal_payload_never_contains_private_answer_data(self):
        payload = json.dumps(build_portal_view(self.workspace, self.learner_summary))

        for secret in ("success_criteria", "accepted", "tolerance", "solution"):
            self.assertNotIn(f'"{secret}"', payload)

    def test_old_items_move_to_earlier_without_disappearing(self):
        items = [
            {"id": f"artifact-{index}", "topic_id": "gradient"}
            for index in range(8)
        ]

        groups = recent_and_older(items, "gradient", limit=3)

        self.assertEqual(len(groups["recent"]), 3)
        self.assertEqual(len(groups["earlier"]), 5)
        self.assertEqual(
            {item["id"] for item in groups["recent"] + groups["earlier"]},
            {item["id"] for item in items},
        )

    def test_public_artifact_keeps_type_and_only_safe_metadata(self):
        artifact = public_artifact(ready_artifact("diagram-one", "diagram"))

        self.assertEqual(artifact["type"], "diagram")
        self.assertEqual(
            artifact["metadata"],
            {"duration_seconds": 42, "thumbnail": "thumbnail-artifact"},
        )
        self.assertEqual(artifact["location"], {"path": "artifacts/generated/diagram-one.bin"})

    def test_ready_lesson_is_validated_before_public_projection(self):
        lesson_path = self.workspace / "lessons/slope-introduction/lesson.json"
        lesson = json.loads(lesson_path.read_text())
        lesson["topic_id"] = "tampered-topic"
        lesson_path.write_text(json.dumps(lesson))

        with self.assertRaises(ValueError):
            ready_lessons(self.workspace, json.loads((self.workspace / "course.json").read_text()))

    def test_artifact_metadata_never_exposes_arbitrary_paths(self):
        artifact = ready_artifact("unsafe-metadata")
        artifact["metadata"].update({
            "thumbnail": "artifacts/generated/thumb.png",
            "captions": "/private/captions.vtt",
            "transcript": "file:///private/transcript.txt",
            "filename": "../secret.txt",
        })

        public = public_artifact(artifact)

        for field in ("thumbnail", "captions", "transcript", "filename"):
            self.assertNotIn(field, public["metadata"])

    def test_artifact_metadata_accepts_safe_references_and_availability(self):
        artifact = ready_artifact("safe-metadata")
        artifact["metadata"].update({
            "thumbnail": "thumbnail-artifact",
            "captions": True,
            "transcript": "transcript-artifact",
            "filename": "lesson.pdf",
        })

        public = public_artifact(artifact)

        self.assertEqual(public["metadata"]["thumbnail"], "thumbnail-artifact")
        self.assertTrue(public["metadata"]["captions"])
        self.assertEqual(public["metadata"]["transcript"], "transcript-artifact")
        self.assertEqual(public["metadata"]["filename"], "lesson.pdf")

    def test_artifacts_are_grouped_by_presentation_family(self):
        view = build_portal_view(self.workspace, self.learner_summary)

        self.assertEqual(view["artifacts"]["watch"]["recent"][0]["type"], "voice-animation")
        self.assertEqual(view["artifacts"]["generated"]["recent"], [])
        self.assertEqual(view["artifacts"]["resources"]["recent"], [])

    def test_missing_interaction_files_are_safe_empty_views(self):
        view = build_portal_view(self.workspace, self.learner_summary)

        self.assertEqual(len(view["exercises"]), 1)
        self.assertEqual(view["exercises"][0]["attempts"], [])
        self.assertEqual(view["questions"], {"recent": [], "earlier": []})

    def test_nested_private_values_are_not_reintroduced_by_public_keys(self):
        question_dir = self.workspace / "questions"
        question_dir.mkdir(exist_ok=True)
        (question_dir / "question-1.json").write_text(json.dumps({
            "id": "question-1",
            "topic_id": "local-change",
            "text": "Why is this approximate?",
            "status": "answered",
            "answer": {"text": "Because it is first order.", "solution": "private"},
        }))

        payload = json.dumps(build_portal_view(self.workspace, self.learner_summary))

        self.assertNotIn('"solution"', payload)


if __name__ == "__main__":
    unittest.main()
