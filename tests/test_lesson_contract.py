import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/course-design/scripts"))

from course_contract import validate_course
from lesson_contract import public_lesson, validate_lesson


def valid_v2_course():
    return {
        "schema_version": 2, "id": "gradient-descent", "title": "Gradient descent",
        "goal": "Predict updates.", "revision": 1,
        "revision_notes": [{"revision": 1, "date": "2026-09-12", "reason": "Initial."}],
        "starting_evidence": [], "assumptions": ["Derivatives unverified."],
        "sources": {"openstax-calculus-1": {"title": "Calculus", "url": "https://openstax.org/calculus",
            "type": "textbook", "checked_on": "2026-09-12", "sections": [], "verification_notes": "Checked."}},
        "current": {"chapter_id": "change", "topic_id": "local-change", "next_step": "Predict."},
        "chapters": [{"id": "change", "title": "Change", "state": "current", "topics": [{
            "id": "local-change", "title": "Local change", "state": "current", "outcome": "Predict change.",
            "subject": "math", "teacher": "math", "supporting_subjects": [], "supporting_teachers": [],
            "skill_routes": ["skills/subject/SKILL.md", "skills/subject/subjects/math.md"],
            "concepts": ["math.derivative"], "prerequisites": [], "minutes": 20,
            "resource_ids": ["openstax-calculus-1"], "exercise_ids": ["predict-change"], "lesson_ids": []
        }]}]
    }


def valid_lesson():
    return {"schema_version": 1, "id": "slope-introduction", "course_id": "gradient-descent",
        "chapter_id": "change", "topic_id": "local-change", "title": "Slope", "purpose": "Predict change.",
        "concepts": ["math.derivative"], "teacher": "math", "skill_routes": ["skills/subject/SKILL.md"],
        "assumptions": ["The learner can read a graph."], "artifacts": [{"id": "slope-video"}, {"id": "slope-graph"}],
        "blocks": [{"id": "intro", "type": "explanation", "concepts": ["math.derivative"], "purpose": "Introduce slope.", "text": "Slope predicts local change."},
            {"id": "video", "type": "voice-animation", "concepts": ["math.derivative"], "purpose": "Show slope.", "artifact_id": "slope-video"},
            {"id": "graph", "type": "interactive-graph", "concepts": ["math.derivative"], "purpose": "Vary slope.", "artifact_id": "slope-graph"},
            {"id": "exercise-block", "type": "exercise", "concepts": ["math.derivative"], "purpose": "Check prediction.", "exercise_id": "predict-change"}],
        "exercises": [{"id": "predict-change", "concepts": ["math.derivative"], "prompt": "Predict the sign.",
            "response_type": "numeric", "evaluation": {"mode": "numeric", "answer": 1, "tolerance": 0.1},
            "success_criteria": ["Uses the sign of slope."], "reference_block_ids": ["intro", "graph"]}],
        "publication": "ready", "created_at": "2026-09-12T16:00:00Z", "updated_at": "2026-09-12T16:00:00Z"}


class LessonContractTests(unittest.TestCase):
    def test_lesson_combines_media_explanation_simulation_and_exercise(self):
        checked = validate_lesson(valid_lesson(), validate_course(valid_v2_course()))
        self.assertEqual([b["type"] for b in checked["blocks"]], ["explanation", "voice-animation", "interactive-graph", "exercise"])

    def test_public_lesson_removes_private_evaluation_data(self):
        exercise = public_lesson(valid_lesson())["exercises"][0]
        self.assertNotIn("success_criteria", exercise)
        self.assertNotIn("answer", exercise["evaluation"])
        self.assertNotIn("tolerance", exercise["evaluation"])

    def test_lesson_rejects_topic_or_artifact_refs_outside_course(self):
        lesson = valid_lesson(); lesson["topic_id"] = "missing"
        with self.assertRaises(ValueError): validate_lesson(lesson, valid_v2_course())
        lesson = valid_lesson(); lesson["blocks"][1]["artifact_id"] = "missing"
        with self.assertRaises(ValueError): validate_lesson(lesson, valid_v2_course())

    def test_lesson_rejects_duplicate_ids_and_unknown_exercise_reference(self):
        lesson = valid_lesson(); lesson["blocks"][1]["id"] = "intro"
        with self.assertRaises(ValueError): validate_lesson(lesson, valid_v2_course())
        lesson = valid_lesson(); lesson["blocks"][-1]["exercise_id"] = "missing"
        with self.assertRaises(ValueError): validate_lesson(lesson, valid_v2_course())

    def test_lesson_fingerprint_is_stable(self):
        from lesson_contract import lesson_fingerprint
        self.assertEqual(lesson_fingerprint(valid_lesson()), lesson_fingerprint(copy.deepcopy(valid_lesson())))


if __name__ == "__main__": unittest.main()
