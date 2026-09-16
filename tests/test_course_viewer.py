"""Course viewer render tests: a fresh course still shows a page."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/course-design/scripts"))

from course_workspace import create_workspace, publish_lesson  # noqa: E402
import artifact_manifest  # noqa: E402
from tests.test_course_contract_v2 import valid_v2_course  # noqa: E402
from tests.test_lesson_contract import valid_lesson  # noqa: E402

RENDER = ROOT / "skills/course-viewer/scripts/render_viewer.py"


def plan_with_reps():
    plan = valid_v2_course()
    plan["chapters"][0]["topics"][0]["representations"] = [
        {"id": "m", "kind": "manim", "concept": "math.derivative",
         "purpose": "Secant motion."},
        {"id": "t", "kind": "text", "concept": "math.derivative",
         "purpose": "Definition."},
    ]
    return plan


class ViewerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.workspace = create_workspace(self.root, "alex", plan_with_reps())

    def render(self):
        result = subprocess.run(
            [sys.executable, str(RENDER), str(self.workspace)],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return (self.workspace / "portal" / "index.html").read_text()

    def test_zero_lesson_course_still_renders_contents_and_plan(self):
        text = self.render()
        self.assertIn("Slope as local change", text)
        self.assertIn("chip manim", text)
        self.assertIn("No ready lessons yet", text)
        self.assertNotIn("success_criteria", text)

    def test_ready_lesson_flips_chips_and_shows_media(self):
        publish_lesson(self.workspace, valid_lesson())
        video = self.workspace / "artifacts/videos/slope-video.mp4"
        video.parent.mkdir(parents=True, exist_ok=True)
        video.write_bytes(b"fake")
        artifact_manifest.register_artifact(self.workspace, {
            "id": "slope-video", "type": "voice-animation", "title": "Slope video",
            "purpose": "Show slope.", "concepts": ["math.derivative"],
            "chapter_id": "change", "topic_id": "local-change",
            "lesson_id": "slope-introduction",
            "location": {"path": "artifacts/videos/slope-video.mp4"},
            "mime_type": "video/mp4", "metadata": {},
            "status": "ready", "created_at": "2026-09-12T16:00:00Z",
            "updated_at": "2026-09-12T16:00:00Z",
        })
        text = self.render()
        self.assertIn("<video", text)
        self.assertIn("chip manim ready", text)
        self.assertNotIn("success_criteria", text)

    def test_missing_manifest_still_renders(self):
        (self.workspace / "manifest.json").unlink()
        text = self.render()
        self.assertIn("Slope as local change", text)


if __name__ == "__main__":
    unittest.main()
