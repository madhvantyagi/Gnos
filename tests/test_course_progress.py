"""Evidence-derived hierarchical course progress."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "skills/understanding-user-learning/scripts/learner_state.py"
sys.path.insert(0, str(ROOT / "skills/course-design/scripts"))
from course_progress import derive_course_progress  # noqa: E402
from tests.test_course_workspace import valid_v2_course  # noqa: E402


class CourseProgressTests(unittest.TestCase):
    def setUp(self):
        self.plan = copy.deepcopy(valid_v2_course())
        self.plan["chapters"][0]["topics"][0]["concepts"] = ["math.slope"]
        self.plan["chapters"][0]["topics"].append({
            "id": "gradient",
            "title": "Gradient as a direction",
            "state": "planned",
            "outcome": "Explain how gradient components identify a direction.",
            "subject": "math",
            "teacher": "math",
            "supporting_subjects": [],
            "supporting_teachers": [],
            "skill_routes": [
                "skills/subject/SKILL.md",
                "skills/subject/subjects/math.md",
            ],
            "concepts": ["math.derivative", "math.gradient"],
            "prerequisites": ["local-change"],
            "minutes": 25,
            "resource_ids": ["openstax-calculus-1"],
            "exercise_ids": ["gradient-direction"],
            "lesson_ids": [],
        })

    @staticmethod
    def attempt(concept, result="correct", help_="none", kind="application"):
        return {
            "concept": concept,
            "task": f"Try {concept}.",
            "response": f"Response for {concept}.",
            "result": result,
            "help": help_,
            "kind": kind,
        }

    @classmethod
    def event(cls, id_, date, attempts, covered=None):
        return {
            "id": id_,
            "date": date,
            "course_id": "gradient-descent",
            "covered": covered or [attempt["concept"] for attempt in attempts],
            "attempts": attempts,
            "interpretation": "",
            "next_step": "Try another task.",
        }

    def test_media_and_time_do_not_advance_progress(self):
        view = derive_course_progress(self.plan, [])

        self.assertEqual(view["topics"]["local-change"]["evidence"], "not-started")
        self.assertEqual(view["topics"]["local-change"]["attempt_count"], 0)

    def test_topic_progress_uses_weakest_relevant_concept_without_erasing_detail(self):
        events = [
            self.event("derivative", "2026-01-01", [self.attempt("math.derivative")]),
            self.event("gradient", "2026-01-02", [
                self.attempt("math.gradient", result="partial"),
            ]),
        ]

        view = derive_course_progress(self.plan, events)

        self.assertEqual(view["topics"]["gradient"]["evidence"], "practicing")
        self.assertEqual(view["concepts"]["math.derivative"]["status"], "demonstrated")
        self.assertEqual(view["concepts"]["math.gradient"]["status"], "practicing")
        self.assertEqual(view["topics"]["gradient"]["attempt_count"], 2)

    def test_later_failure_surfaces_needs_repair_and_preserves_attempts(self):
        events = [
            self.event("success", "2026-01-01", [self.attempt("math.gradient")]),
            self.event("failure", "2026-01-02", [
                self.attempt("math.gradient", result="incorrect"),
            ]),
        ]
        before = copy.deepcopy(events)

        view = derive_course_progress(self.plan, events)

        concept = view["concepts"]["math.gradient"]
        self.assertEqual(concept["status"], "practicing")
        self.assertEqual(concept["display_status"], "needs-repair")
        self.assertEqual(concept["attempts"], 2)
        self.assertEqual(concept["latest"]["result"], "incorrect")
        self.assertEqual(events, before)

    def test_summary_exposes_course_progress_only_for_selected_course(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            course_path = root / "course.json"
            event_path = root / "event.json"
            course_path.write_text(json.dumps(self.plan))
            event_path.write_text(json.dumps(self.event(
                "derivative", "2026-01-01", [self.attempt("math.slope")]
            )))

            def call(*args):
                return subprocess.run(
                    [sys.executable, str(STATE), "--root", str(root), *args],
                    capture_output=True, text=True,
                )

            self.assertEqual(call("enroll", "alex", "--course", str(course_path)).returncode, 0)
            self.assertEqual(call("record", "alex", "--event", str(event_path)).returncode, 0)
            all_courses = json.loads(call("summary", "alex").stdout)
            selected = json.loads(call("summary", "alex", "--course-id", "gradient-descent").stdout)

            self.assertNotIn("course_progress", all_courses)
            self.assertEqual(selected["course_progress"]["course_id"], "gradient-descent")
            self.assertEqual(
                selected["course_progress"]["topics"]["local-change"]["evidence"],
                "demonstrated",
            )

    def test_curriculum_renders_planning_and_evidence_states(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            course_path = root / "course.json"
            course_path.write_text(json.dumps(self.plan))
            result = subprocess.run(
                [sys.executable, str(STATE), "--root", str(root), "enroll", "alex",
                 "--course", str(course_path)], capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            curriculum = root / "alex/memory/courses/gradient-descent/CURRICULUM.md"
            rendered = curriculum.read_text()

            self.assertIn("Chapter 1: Local change (current)", rendered)
            self.assertIn("Topic 2: Gradient as a direction (planned)", rendered)
            self.assertIn("Evidence: not-started", rendered)
            self.assertNotIn("mastery", rendered.lower())


if __name__ == "__main__":
    unittest.main()
