"""Worker context follows declared teaching dependencies without rewriting lessons."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tests.test_lesson_contract import valid_lesson, valid_v2_course

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/lesson-design/scripts/build_block_context.py"


class BlockContextTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCRIPT.exists(), "The worker-context compiler is not implemented")
        spec = importlib.util.spec_from_file_location("block_context", SCRIPT)
        self.compiler = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.compiler)
        self.course = valid_v2_course()
        self.lesson = valid_lesson()

    def test_context_contains_transitive_dependencies_in_reading_order(self):
        self.lesson["blocks"][0]["text"] = "At x=2, use the same starting point in every view."
        unrelated = copy.deepcopy(self.lesson["blocks"][0])
        unrelated.update(id="unrelated", text="A separate example not used here.")
        self.lesson["blocks"].insert(2, unrelated)
        packet = self.compiler.build_context(self.lesson, self.course, "exercise-block")
        self.assertEqual([b["id"] for b in packet["dependencies"]], ["intro", "video", "graph"])
        self.assertIn("x=2", packet["dependencies"][0]["text"])
        self.assertNotIn("unrelated", json.dumps(packet))

    def test_exercise_worker_receives_its_contract_but_not_other_answers(self):
        extra = copy.deepcopy(self.lesson["exercises"][0])
        extra.update(id="other-question", prompt="UNRELATED PRIVATE ANSWER")
        self.lesson["exercises"].append(extra)
        self.course["chapters"][0]["topics"][0]["exercise_ids"].append("other-question")
        import sys
        sys.path.insert(0, str(ROOT / "skills/course-design/scripts"))
        from course_contract import course_content_fingerprint, validate_course
        validated = validate_course(self.course)
        self.lesson["design_receipt"]["course_fingerprint"] = course_content_fingerprint(validated)
        packet = self.compiler.build_context(self.lesson, self.course, "exercise-block")
        self.assertEqual(packet["exercise"]["id"], "predict-change")
        self.assertIn("success_criteria", packet["exercise"])
        self.assertNotIn("UNRELATED PRIVATE ANSWER", json.dumps(packet))
        self.assertNotIn("exercise", self.compiler.build_context(self.lesson, self.course, "intro"))

    def test_dependent_explanation_receives_public_exercise_without_answer(self):
        continuation = copy.deepcopy(self.lesson["blocks"][0])
        continuation.update(id="interpret-check", text="Explain the check's reasoning.")
        continuation["production"]["depends_on_block_ids"] = ["exercise-block"]
        self.lesson["blocks"].append(continuation)
        self.lesson["exercises"][0]["solution"] = "PRIVATE SOLUTION"
        packet = self.compiler.build_context(self.lesson, self.course, "interpret-check")
        exercise = packet["dependency_exercises"][0]
        self.assertEqual(exercise["id"], "predict-change")
        self.assertEqual(exercise["prompt"], self.lesson["exercises"][0]["prompt"])
        self.assertNotIn("success_criteria", exercise)
        self.assertNotIn("PRIVATE SOLUTION", json.dumps(packet))

    def test_unknown_target_and_forward_dependency_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown block"):
            self.compiler.build_context(self.lesson, self.course, "missing")
        self.lesson["blocks"][0]["production"]["depends_on_block_ids"] = ["graph"]
        with self.assertRaisesRegex(ValueError, "earlier lesson blocks"):
            self.compiler.build_context(self.lesson, self.course, "intro")

    def test_cli_keeps_source_files_unchanged_and_marks_output_private(self):
        with tempfile.TemporaryDirectory() as directory:
            lesson = Path(directory) / "lesson.json"
            course = Path(directory) / "course.json"
            lesson.write_text(json.dumps(self.lesson))
            course.write_text(json.dumps(self.course))
            before = (lesson.read_bytes(), course.read_bytes())
            result = subprocess.run([sys.executable, str(SCRIPT), str(lesson),
                                     "--course", str(course), "--block", "graph"],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            packet = json.loads(result.stdout)
            self.assertEqual(packet["audience"], "private-production")
            self.assertEqual((lesson.read_bytes(), course.read_bytes()), before)
            self.assertEqual(len(list(Path(directory).iterdir())), 2)


if __name__ == "__main__":
    unittest.main()
