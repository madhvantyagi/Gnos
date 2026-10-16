"""Check instruction selection with temporary learners and canonical course fixtures."""
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

from tests.test_course_contract_v2 import valid_v2_course

ROOT = Path(__file__).resolve().parents[1]
LOADER = ROOT / "skills/learning-orchestrator/scripts/assemble_context.py"
STATE = ROOT / "skills/learner-tracking/scripts/learner_state.py"


class ContextSelectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_loader(self, *args):
        return subprocess.run([sys.executable, str(LOADER), "--learners-root", str(self.root), *args],
                              capture_output=True, text=True)

    def enroll(self):
        path = self.root / "course.json"
        path.write_text(json.dumps(valid_v2_course()))
        for args in (("init", "isolated"), ("enroll", "isolated", "--course", str(path))):
            result = subprocess.run([sys.executable, str(STATE), "--root", str(self.root), *args],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def instruction_paths(self, text):
        return re.findall(r"^--- INSTRUCTIONS: (.+) ---$", text, re.MULTILINE)

    def test_local_question_ignores_unrelated_active_course_and_private_data(self):
        self.enroll()
        result = self.run_loader("--subject", "history", "--learner", "isolated", "--mode", "local")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("skills/subject/subjects/history.md", self.instruction_paths(result.stdout))
        self.assertNotIn("--- COURSE DATA:", result.stdout)
        self.assertNotIn("--- LEARNER DATA:", result.stdout)
        self.assertNotIn("--- LESSON REVIEW DATA:", result.stdout)
        self.assertNotIn("skills/learner-tracking/SKILL.md", self.instruction_paths(result.stdout))

    def test_manifest_matches_emitted_instructions_with_and_without_enrolled_course(self):
        for enrolled in (False, True):
            with self.subTest(enrolled=enrolled):
                if enrolled:
                    self.enroll()
                args = ("--subject", "math", "--learner", "isolated", "--mode", "lesson")
                actual = self.run_loader(*args)
                manifest = self.run_loader(*args, "--manifest")
                self.assertEqual(actual.returncode, 0, actual.stderr)
                self.assertEqual(manifest.returncode, 0, manifest.stderr)
                self.assertEqual(manifest.stdout.splitlines(), self.instruction_paths(actual.stdout))

    def test_explicit_subfield_and_bridge_load_exact_guides_without_extra_persona(self):
        args = ("--subject", "artificial-intelligence", "--subfield",
                "artificial-intelligence.machine-learning", "--bridge", "math", "--mode", "local")
        result = self.run_loader(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        paths = self.instruction_paths(result.stdout)
        self.assertIn("skills/subject/subjects/artificial-intelligence.md", paths)
        self.assertIn("skills/subject/subjects/math.md", paths)
        self.assertNotIn("teachers/math/SOUL.md", paths)
        self.assertIn("--- SUBJECT ROUTE DATA:", result.stdout)
        self.assertIn('"section": "Machine learning"', result.stdout)

    def test_subfield_cannot_silently_change_lead_subject(self):
        result = self.run_loader("--subject", "physics", "--subfield", "math.statistics-inference", "--mode", "local")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("belongs to math", result.stderr)

    def test_declared_supporting_subject_loads_its_guide_only(self):
        plan = valid_v2_course()
        plan["chapters"][0]["topics"][0]["supporting_subjects"] = ["physics"]
        path = self.root / "bridge.json"
        path.write_text(json.dumps(plan))
        result = self.run_loader("--subject", "math", "--course", str(path))
        self.assertEqual(result.returncode, 0, result.stderr)
        paths = self.instruction_paths(result.stdout)
        self.assertIn("skills/subject/subjects/physics.md", paths)
        self.assertNotIn("teachers/physics/SOUL.md", paths)

    def test_course_and_viewer_omit_private_review_but_lesson_continuation_keeps_it(self):
        self.enroll()
        for mode in ("course", "viewer", "lesson"):
            with self.subTest(mode=mode):
                result = self.run_loader("--subject", "math", "--learner", "isolated", "--mode", mode)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual("--- LESSON REVIEW DATA:" in result.stdout, mode == "lesson")


if __name__ == "__main__":
    unittest.main()
