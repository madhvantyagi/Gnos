"""Contract tests for the explicit course artifact publication registry."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/course-design/scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from artifact_manifest import (  # noqa: E402
    archive_artifact,
    ConflictError,
    manifest_fingerprint,
    read_manifest,
    ready_artifacts,
    register_artifact,
    validate_manifest,
)
from course_workspace import create_workspace  # noqa: E402
from test_course_workspace import valid_v2_course  # noqa: E402


def ready_video():
    return {
        "id": "gradient-video",
        "type": "voice-animation",
        "title": "Why the gradient points uphill",
        "purpose": "Show how the update direction changes.",
        "concepts": ["math.derivative"],
        "chapter_id": "change",
        "topic_id": "local-change",
        "lesson_id": "slope-introduction",
        "location": {"path": "artifacts/videos/gradient.mp4"},
        "mime_type": "video/mp4",
        "metadata": {"duration_seconds": 42},
        "status": "ready",
        "created_at": "2026-09-12T16:00:00Z",
        "updated_at": "2026-09-12T16:00:00Z",
    }


def draft_diagram():
    artifact = copy.deepcopy(ready_video())
    artifact.update({
        "id": "gradient-draft",
        "type": "diagram",
        "title": "Draft update diagram",
        "location": {"path": "artifacts/diagrams/gradient.svg"},
        "mime_type": "image/svg+xml",
        "status": "draft",
        "updated_at": "2026-09-12T16:01:00Z",
    })
    return artifact


class ArtifactManifestTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        plan = valid_v2_course()
        plan["chapters"][0]["topics"][0]["lesson_ids"] = ["slope-introduction"]
        self.workspace = create_workspace(self.root, "alex", plan)
        (self.workspace / "artifacts/videos/gradient.mp4").write_bytes(b"video")
        (self.workspace / "artifacts/diagrams/gradient.svg").write_text("<svg/>")

    def tearDown(self):
        self.tempdir.cleanup()

    def test_only_registered_ready_artifacts_are_public(self):
        register_artifact(self.workspace, ready_video())
        register_artifact(self.workspace, draft_diagram())
        self.assertEqual(
            [a["id"] for a in ready_artifacts(read_manifest(self.workspace))],
            ["gradient-video"],
        )

    def test_simulation_dimensions_are_bounded_when_provided(self):
        artifact = copy.deepcopy(ready_video())
        artifact.update({"id": "route-simulation", "type": "simulation",
                         "mime_type": "text/html",
                         "metadata": {"dimensions": {"width": 1280, "height": 800}}})
        manifest = read_manifest(self.workspace)
        manifest["artifacts"].append(artifact)
        validate_manifest(manifest, manifest["course_id"])
        for dimensions in ({"width": 200, "height": 800},
                           {"width": 1280, "height": 2000},
                           {"width": True, "height": 800},
                           {"width": 1280.5, "height": 800},
                           {"width": 1280}):
            artifact["metadata"]["dimensions"] = dimensions
            with self.subTest(dimensions=dimensions), self.assertRaises(ValueError):
                validate_manifest(manifest, manifest["course_id"])

    def test_unknown_type_is_valid_when_open_action_is_safe(self):
        item = copy.deepcopy(ready_video())
        item.update({
            "id": "generated-notebook",
            "type": "notebook",
            "title": "Generated notebook",
            "location": {"path": "artifacts/generated/demo.ipynb"},
            "mime_type": "application/x-ipynb+json",
        })
        (self.workspace / "artifacts/generated/demo.ipynb").write_text("{}")
        self.assertEqual(
            register_artifact(self.workspace, item),
            manifest_fingerprint(read_manifest(self.workspace)),
        )

    def test_archive_preserves_file_and_manifest_history(self):
        register_artifact(self.workspace, ready_video())
        current = manifest_fingerprint(read_manifest(self.workspace))
        fingerprint = archive_artifact(self.workspace, "gradient-video", current)
        manifest = read_manifest(self.workspace)
        self.assertTrue((self.workspace / "artifacts/videos/gradient.mp4").exists())
        self.assertEqual(manifest["artifacts"][0]["status"], "archived")
        self.assertEqual(manifest["history"][0]["status"], "ready")
        self.assertEqual(fingerprint, manifest_fingerprint(manifest))

    def test_replacing_artifact_requires_newer_timestamp_and_preserves_history(self):
        register_artifact(self.workspace, ready_video())
        replacement = copy.deepcopy(ready_video())
        replacement.update({
            "title": "Updated gradient explanation",
            "updated_at": "2026-09-12T16:02:00Z",
        })
        register_artifact(self.workspace, replacement)
        manifest = read_manifest(self.workspace)
        self.assertEqual(manifest["artifacts"][0]["title"], "Updated gradient explanation")
        self.assertEqual([entry["id"] for entry in manifest["history"]], ["gradient-video"])
        with self.assertRaises(ValueError):
            register_artifact(self.workspace, ready_video())

    def test_stale_fingerprint_rejects_registration_without_mutation(self):
        register_artifact(self.workspace, ready_video())
        before = read_manifest(self.workspace)
        changed = copy.deepcopy(draft_diagram())
        with self.assertRaises(ConflictError):
            register_artifact(self.workspace, changed, expected_fingerprint="stale")
        self.assertEqual(read_manifest(self.workspace), before)

    def test_atomic_manifest_write_failure_leaves_previous_snapshot_intact(self):
        register_artifact(self.workspace, ready_video())
        before_bytes = (self.workspace / "manifest.json").read_bytes()
        replacement = copy.deepcopy(draft_diagram())
        with mock.patch("course_workspace.atomic_json", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                register_artifact(self.workspace, replacement)
        self.assertEqual((self.workspace / "manifest.json").read_bytes(), before_bytes)

    def test_local_locations_reject_traversal_absolute_and_symlink_paths(self):
        for location in (
            {"path": "../outside.mp4"},
            {"path": str(self.workspace / "artifacts/videos/gradient.mp4")},
            {"path": "artifacts/../course.json"},
        ):
            artifact = copy.deepcopy(ready_video())
            artifact["id"] = "unsafe-location"
            artifact["location"] = location
            with self.assertRaises(ValueError):
                register_artifact(self.workspace, artifact)

        target = self.workspace / "artifacts/videos/real.mp4"
        target.write_bytes(b"real")
        link = self.workspace / "artifacts/videos/link.mp4"
        link.symlink_to(target)
        artifact = copy.deepcopy(ready_video())
        artifact["id"] = "symlink-location"
        artifact["location"] = {"path": "artifacts/videos/link.mp4"}
        with self.assertRaises(ValueError):
            register_artifact(self.workspace, artifact)

    def test_urls_must_be_https_and_location_has_exactly_one_target(self):
        for location in (
            {"url": "file:///tmp/secret"},
            {"url": "//example.com/file"},
            {"url": "http://example.com/file"},
            {"path": "artifacts/videos/gradient.mp4", "url": "https://example.com/file"},
        ):
            artifact = copy.deepcopy(ready_video())
            artifact["id"] = "unsafe-url"
            artifact["location"] = location
            with self.assertRaises(ValueError):
                register_artifact(self.workspace, artifact)

    def test_ready_local_artifact_requires_existing_regular_file(self):
        missing = copy.deepcopy(ready_video())
        missing["id"] = "missing-ready"
        missing["location"] = {"path": "artifacts/videos/not-created.mp4"}
        with self.assertRaises(ValueError):
            register_artifact(self.workspace, missing)

        directory = self.workspace / "artifacts/videos/directory.mp4"
        directory.mkdir()
        directory_artifact = copy.deepcopy(ready_video())
        directory_artifact["id"] = "directory-ready"
        directory_artifact["location"] = {"path": "artifacts/videos/directory.mp4"}
        with self.assertRaises(ValueError):
            register_artifact(self.workspace, directory_artifact)

        symlink_target = self.workspace / "artifacts/videos/target.mp4"
        symlink_target.write_bytes(b"target")
        symlink = self.workspace / "artifacts/videos/symlink-ready.mp4"
        symlink.symlink_to(symlink_target)
        symlink_artifact = copy.deepcopy(ready_video())
        symlink_artifact["id"] = "symlink-ready"
        symlink_artifact["location"] = {"path": "artifacts/videos/symlink-ready.mp4"}
        with self.assertRaises(ValueError):
            register_artifact(self.workspace, symlink_artifact)

    def test_draft_local_artifact_can_be_registered_before_output_exists(self):
        draft = copy.deepcopy(draft_diagram())
        draft["location"] = {"path": "artifacts/diagrams/not-created.svg"}
        fingerprint = register_artifact(self.workspace, draft)
        self.assertEqual(fingerprint, manifest_fingerprint(read_manifest(self.workspace)))

    def test_artifact_requires_published_lesson_placement(self):
        artifact = copy.deepcopy(ready_video())
        artifact["lesson_id"] = "different-lesson"
        with self.assertRaises(ValueError):
            register_artifact(self.workspace, artifact)

    def test_artifact_concepts_must_belong_to_selected_topic(self):
        artifact = copy.deepcopy(ready_video())
        artifact["concepts"] = ["math.unrelated"]
        with self.assertRaises(ValueError):
            register_artifact(self.workspace, artifact)

    def test_manifest_validation_rejects_wrong_course_and_duplicate_ids(self):
        manifest = read_manifest(self.workspace)
        with self.assertRaises(ValueError):
            validate_manifest(manifest, "other-course")
        manifest["artifacts"] = [ready_video(), ready_video()]
        with self.assertRaises(ValueError):
            validate_manifest(manifest, "gradient-descent")

    def test_cli_register_archive_and_list_return_json(self):
        artifact_file = self.root / "artifact.json"
        artifact_file.write_text(json.dumps(ready_video()))
        cli = ROOT / "skills/course-design/scripts/manage_artifact.py"
        base = [sys.executable, str(cli), "--learners-root", str(self.root)]
        registered = subprocess.run(
            base + ["register", "alex", "gradient-descent", "--file", str(artifact_file)],
            check=True, capture_output=True, text=True,
        )
        result = json.loads(registered.stdout)
        self.assertEqual(result["artifact_id"], "gradient-video")
        listed = subprocess.run(
            base + ["list", "alex", "gradient-descent", "--ready"],
            check=True, capture_output=True, text=True,
        )
        self.assertEqual([a["id"] for a in json.loads(listed.stdout)["artifacts"]], ["gradient-video"])
        archived = subprocess.run(
            base + ["archive", "alex", "gradient-descent", "--artifact-id", "gradient-video",
                    "--fingerprint", result["fingerprint"]],
            check=True, capture_output=True, text=True,
        )
        self.assertEqual(json.loads(archived.stdout)["artifact_id"], "gradient-video")


if __name__ == "__main__":
    unittest.main()
