import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/course-design/scripts"))

from course_contract import course_content_fingerprint, validate_course
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


def valid_lesson(course=None):
    lesson = {"schema_version": 2, "id": "slope-introduction", "course_id": "gradient-descent",
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
    target = course if course is not None else validate_course(valid_v2_course())
    for index, block in enumerate(lesson["blocks"]):
        block["production"] = {
            "skill_route": "skills/subject/SKILL.md",
            "brief": f"Produce the {block['id']} lesson block.",
            "must_include": [block["purpose"]],
            "continuity": ["Use the lesson's established concepts and notation."],
            "acceptance_checks": ["The block fulfills its stated purpose."],
            "depends_on_block_ids": [lesson["blocks"][index - 1]["id"]] if index else [],
        }
    lesson["design_receipt"] = {
        "designed_at": "2026-09-12T16:00:00Z",
        "course_fingerprint": course_content_fingerprint(target),
        "skill_route": "skills/lesson-design/SKILL.md",
        "review": "pass",
    }
    return lesson


def attach_receipt(lesson, validated_course):
    lesson["design_receipt"] = {
        "designed_at": lesson["updated_at"],
        "course_fingerprint": course_content_fingerprint(validated_course),
        "skill_route": "skills/lesson-design/SKILL.md",
        "review": "pass",
    }
    return lesson


class LessonContractTests(unittest.TestCase):
    def test_schema_one_lessons_remain_readable_without_production_briefs(self):
        course = validate_course(valid_v2_course())
        lesson = valid_lesson(course)
        lesson["schema_version"] = 1
        lesson["blocks"] = [lesson["blocks"][0], lesson["blocks"][-1]]
        lesson["blocks"][0].pop("production")
        lesson["blocks"][1].pop("production")
        lesson["exercises"][0]["reference_block_ids"] = ["intro"]
        self.assertEqual(validate_lesson(lesson, course), lesson)

    def test_ready_lesson_needs_two_distinct_teaching_forms(self):
        course = validate_course(valid_v2_course())
        lesson = valid_lesson(course)
        lesson["blocks"] = [lesson["blocks"][0], lesson["blocks"][-1]]
        lesson["blocks"][1]["production"]["depends_on_block_ids"] = []
        lesson["exercises"][0]["reference_block_ids"] = ["intro"]
        with self.assertRaisesRegex(ValueError, "two distinct teaching forms"):
            validate_lesson(lesson, course)
        lesson["publication"] = "draft"
        lesson.pop("design_receipt")
        self.assertEqual(validate_lesson(lesson, course), lesson)

    def test_lesson_can_choose_media_route_without_course_media_plan(self):
        course = valid_v2_course()
        del course["chapters"][0]["topics"][0]["outcome"]
        validated = validate_course(course)
        lesson = valid_lesson(validated)
        lesson["skill_routes"].append("skills/manim-voice-animation/SKILL.md")
        lesson["blocks"][1]["production"] = {
            "skill_route": "skills/manim-voice-animation/SKILL.md",
            "brief": "Show a secant moving toward the tangent.",
            "must_include": ["secant", "tangent"],
            "continuity": ["Keep the axes fixed."],
            "acceptance_checks": ["The final line is tangent."],
            "depends_on_block_ids": ["intro"],
        }
        self.assertEqual(validate_lesson(lesson, validated), lesson)

    def test_worked_solution_is_validated_but_excluded_from_public_lesson(self):
        lesson = valid_lesson()
        lesson['exercises'][0]['solution'] = 'A positive slope predicts an increase.'
        checked = validate_lesson(lesson, validate_course(valid_v2_course()))
        self.assertNotIn('solution', public_lesson(checked)['exercises'][0])
        for invalid in ['', '  ', {'answer': 1}]:
            lesson['exercises'][0]['solution'] = invalid
            with self.assertRaises(ValueError):
                validate_lesson(lesson, validate_course(valid_v2_course()))

    def test_teacher_neutral_lesson_matches_null_topic_teacher(self):
        course = valid_v2_course()
        course["chapters"][0]["topics"][0]["teacher"] = None
        validated = validate_course(course)
        lesson = valid_lesson(validated)
        lesson["teacher"] = None
        checked = validate_lesson(lesson, validated)
        self.assertIsNone(checked["teacher"])

    def test_lesson_combines_media_explanation_simulation_and_exercise(self):
        checked = validate_lesson(valid_lesson(), validate_course(valid_v2_course()))
        self.assertEqual([b["type"] for b in checked["blocks"]], ["explanation", "voice-animation", "interactive-graph", "exercise"])

    def test_blocks_follow_the_topic_representation_plan(self):
        course = valid_v2_course()
        topic = course["chapters"][0]["topics"][0]
        topic["representations"] = [
            {"id": "slope-explanation", "kind": "text", "concept": "math.derivative",
             "purpose": "Introduce slope.", "skill_route": "skills/subject/SKILL.md"},
            {"id": "slope-motion", "kind": "manim", "concept": "math.derivative",
             "purpose": "Show slope.", "skill_route": "skills/manim-voice-animation/SKILL.md"},
            {"id": "slope-control", "kind": "simulation", "concept": "math.derivative",
             "purpose": "Vary slope.", "skill_route": "skills/subject/SKILL.md"},
            {"id": "slope-check", "kind": "exercise", "concept": "math.derivative",
             "purpose": "Check prediction.", "skill_route": "skills/subject/SKILL.md"},
        ]
        topic["skill_routes"].append("skills/manim-voice-animation/SKILL.md")
        validated = validate_course(course)
        lesson = valid_lesson(validated)
        lesson["skill_routes"].append("skills/manim-voice-animation/SKILL.md")
        for block, representation_id in zip(
                lesson["blocks"],
                ("slope-explanation", "slope-motion", "slope-control", "slope-check")):
            block["representation_id"] = representation_id
        lesson["blocks"][1]["production"] = {
            "skill_route": "skills/manim-voice-animation/SKILL.md",
            "brief": "Keep the point fixed while the secant approaches the tangent.",
            "must_include": ["The secant", "The limiting tangent"],
            "continuity": ["Use the lesson's x and y labels."],
            "acceptance_checks": ["The final frame matches the stated limit."],
            "depends_on_block_ids": ["intro"],
        }

        checked = validate_lesson(lesson, validated)

        self.assertEqual(checked["blocks"][1]["representation_id"], "slope-motion")
        public_block = public_lesson(lesson)["blocks"][1]
        self.assertNotIn("production", public_block)
        self.assertEqual(public_block["representation_id"], "slope-motion")

    def test_new_blocks_need_no_ids_even_with_an_old_topic_media_plan(self):
        course = valid_v2_course()
        course["chapters"][0]["topics"][0]["representations"] = [
            {"id": "slope-explanation", "kind": "text", "concept": "math.derivative",
             "purpose": "State what slope predicts."}
        ]
        validated = validate_course(course)

        self.assertEqual(validate_lesson(valid_lesson(validated), validated)["blocks"][0]["id"], "intro")

    def test_block_rejects_unknown_or_incompatible_representation(self):
        course = valid_v2_course()
        course["chapters"][0]["topics"][0]["representations"] = [
            {"id": "slope-explanation", "kind": "text", "concept": "math.derivative",
             "purpose": "Introduce slope."}
        ]
        validated = validate_course(course)
        lesson = valid_lesson(validated)
        for block in lesson["blocks"]:
            block["representation_id"] = "slope-explanation"

        unknown = copy.deepcopy(lesson)
        unknown["blocks"][0]["representation_id"] = "missing"
        with self.assertRaisesRegex(ValueError, "unknown representation"):
            validate_lesson(unknown, validated)

        with self.assertRaisesRegex(ValueError, "does not allow block type"):
            validate_lesson(lesson, validated)

    def test_block_rejects_malformed_representation_id_and_purpose_drift(self):
        course = valid_v2_course()
        course["chapters"][0]["topics"][0]["representations"] = [
            {"id": "slope-explanation", "kind": "text", "concept": "math.derivative",
             "purpose": "Introduce slope.", "skill_route": "skills/subject/SKILL.md"}
        ]
        validated = validate_course(course)
        lesson = valid_lesson(validated)
        for block in lesson["blocks"]:
            block["representation_id"] = "slope-explanation"
        lesson["blocks"] = [lesson["blocks"][0]]
        lesson["exercises"] = []

        malformed = copy.deepcopy(lesson)
        malformed["blocks"][0]["representation_id"] = ["slope-explanation"]
        with self.assertRaisesRegex(ValueError, "lowercase slug"):
            validate_lesson(malformed, validated)

        drifted = copy.deepcopy(lesson)
        drifted["blocks"][0]["purpose"] = "Explain something else."
        with self.assertRaisesRegex(ValueError, "purpose must match"):
            validate_lesson(drifted, validated)

    def test_production_route_must_match_its_course_representation(self):
        course = valid_v2_course()
        topic = course["chapters"][0]["topics"][0]
        topic["skill_routes"].append("skills/manim-voice-animation/SKILL.md")
        topic["representations"] = [
            {"id": "slope-motion", "kind": "manim", "concept": "math.derivative",
             "purpose": "Show slope.", "skill_route": "skills/manim-voice-animation/SKILL.md"}
        ]
        validated = validate_course(course)
        lesson = valid_lesson(validated)
        lesson["skill_routes"].append("skills/manim-voice-animation/SKILL.md")
        lesson["blocks"] = [lesson["blocks"][1]]
        lesson["blocks"][0]["production"]["depends_on_block_ids"] = []
        lesson["blocks"][0]["representation_id"] = "slope-motion"
        lesson["blocks"][0]["production"] = {
            "skill_route": "skills/subject/SKILL.md",
            "brief": "Show the secant approaching the tangent.",
            "must_include": ["secant", "tangent"],
            "continuity": ["Keep the axes fixed."],
            "acceptance_checks": ["The final line is tangent."],
            "depends_on_block_ids": [],
        }
        lesson["exercises"] = []

        with self.assertRaisesRegex(ValueError, "must match the course representation"):
            validate_lesson(lesson, validated)

    def test_production_brief_requires_declared_skill_and_complete_checks(self):
        lesson = valid_lesson()
        lesson["blocks"][1]["production"] = {
            "skill_route": "skills/manim-voice-animation/SKILL.md",
            "brief": "Show the secant approaching the tangent.",
            "must_include": ["secant", "tangent"],
            "continuity": ["Keep the axes fixed."],
            "acceptance_checks": ["The final line is tangent."],
            "depends_on_block_ids": ["intro"],
        }
        with self.assertRaisesRegex(ValueError, "skill_route must be declared"):
            validate_lesson(lesson, validate_course(valid_v2_course()))

        lesson["blocks"][1]["production"]["skill_route"] = "skills/subject/SKILL.md"
        lesson["blocks"][1]["production"]["acceptance_checks"] = []
        with self.assertRaisesRegex(ValueError, "acceptance_checks must be a nonempty list"):
            validate_lesson(lesson, validate_course(valid_v2_course()))

    def test_production_dependencies_must_name_earlier_blocks(self):
        lesson = valid_lesson()
        production = {
            "skill_route": "skills/subject/SKILL.md",
            "brief": "Build the block from the lesson's established notation.",
            "must_include": ["The stated concept"],
            "continuity": ["Reuse the lesson notation."],
            "acceptance_checks": ["The block answers its purpose."],
            "depends_on_block_ids": ["intro"],
        }
        lesson["blocks"][1]["production"] = production
        validate_lesson(lesson, validate_course(valid_v2_course()))

        invalid = copy.deepcopy(lesson)
        invalid["blocks"][0]["production"] = copy.deepcopy(production)
        invalid["blocks"][0]["production"]["depends_on_block_ids"] = ["video"]
        with self.assertRaisesRegex(ValueError, "earlier lesson blocks"):
            validate_lesson(invalid, validate_course(valid_v2_course()))

    def test_every_block_requires_a_producer_and_dependency_list(self):
        course = validate_course(valid_v2_course())
        lesson = valid_lesson(course)
        lesson["publication"] = "draft"
        lesson.pop("design_receipt")

        missing_production = copy.deepcopy(lesson)
        missing_production["blocks"][0].pop("production")
        with self.assertRaisesRegex(ValueError, "production is required"):
            validate_lesson(missing_production, course)

        missing_dependencies = copy.deepcopy(lesson)
        missing_dependencies["blocks"][0]["production"].pop("depends_on_block_ids")
        with self.assertRaisesRegex(ValueError, "depends_on_block_ids is required"):
            validate_lesson(missing_dependencies, course)

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

    def test_execute_key_is_rejected_for_any_value(self):
        for value in (True, 1, "yes", False, 0, None):
            lesson = valid_lesson()
            lesson["exercises"][0]["evaluation"]["execute"] = value
            with self.assertRaises(ValueError):
                validate_lesson(lesson, valid_v2_course())

    def test_choice_evaluation_requires_unique_options_and_private_member_answer(self):
        lesson = valid_lesson()
        exercise = lesson["exercises"][0]
        exercise.update({"response_type": "multiple-choice", "evaluation": {
            "mode": "choice", "options": ["increase", "decrease"], "answer": "decrease"}})
        validate_lesson(lesson, validate_course(valid_v2_course()))
        public = public_lesson(lesson)["exercises"][0]["evaluation"]
        self.assertEqual(public, {"mode": "choice", "options": ["increase", "decrease"]})
        for options, answer in (([], "decrease"), (["same", "same"], "same"), (["increase"], "decrease")):
            invalid = copy.deepcopy(lesson)
            invalid["exercises"][0]["evaluation"].update(options=options, answer=answer)
            with self.assertRaises(ValueError):
                validate_lesson(invalid, valid_v2_course())

    def test_numeric_evaluation_rejects_boolean_answer_or_tolerance(self):
        for answer, tolerance in ((True, 0.1), (1, True), (1, -0.1)):
            lesson = valid_lesson()
            lesson["exercises"][0]["evaluation"].update(answer=answer, tolerance=tolerance)
            with self.assertRaises(ValueError):
                validate_lesson(lesson, valid_v2_course())

    def test_manual_evaluation_rejects_private_answer_fields(self):
        lesson = valid_lesson()
        exercise = lesson["exercises"][0]
        exercise["response_type"] = "long-text"
        exercise["evaluation"] = {"mode": "manual", "solution": "hidden"}
        with self.assertRaises(ValueError):
            validate_lesson(lesson, valid_v2_course())

    def test_timestamps_are_real_ordered_utc_times(self):
        for created, updated in (("2026-02-30T16:00:00Z", "2026-09-12T16:00:00Z"),
                                 ("2026-09-12T16:00:01Z", "2026-09-12T16:00:00Z"),
                                 ("2026-09-12T16:00:00+00:00", "2026-09-12T16:00:00Z")):
            lesson = valid_lesson(); lesson["created_at"] = created; lesson["updated_at"] = updated
            with self.assertRaises(ValueError):
                validate_lesson(lesson, valid_v2_course())

    def test_skill_routes_are_unique_and_known(self):
        for routes in (["skills/subject/SKILL.md", "skills/subject/SKILL.md"],
                       ["skills/subject/SKILL.md", "skills/subject/subjects/missing.md"]):
            lesson = valid_lesson(); lesson["skill_routes"] = routes
            with self.assertRaises(ValueError):
                validate_lesson(lesson, valid_v2_course())

    def test_duplicate_artifact_ids_are_rejected(self):
        lesson = valid_lesson()
        lesson["artifacts"].append({"id": "slope-video"})
        with self.assertRaises(ValueError):
            validate_lesson(lesson, valid_v2_course())

    def test_choice_options_must_be_nonempty_unique_strings(self):
        lesson = valid_lesson()
        exercise = lesson["exercises"][0]
        exercise.update({"response_type": "multiple-choice", "evaluation": {
            "mode": "choice", "options": ["yes", "no"], "answer": "yes"}})
        for options in ([[] , "no"], [{"value": "yes"}, "no"], ["", "no"], ["yes", "yes"]):
            invalid = copy.deepcopy(lesson)
            invalid["exercises"][0]["evaluation"]["options"] = options
            with self.assertRaises(ValueError):
                validate_lesson(invalid, valid_v2_course())

    def test_numeric_evaluation_rejects_nonfinite_answer_and_tolerance(self):
        import math
        for field, value in (("answer", math.nan), ("answer", math.inf), ("answer", -math.inf),
                             ("tolerance", math.nan), ("tolerance", math.inf), ("tolerance", -math.inf)):
            lesson = valid_lesson()
            lesson["exercises"][0]["evaluation"][field] = value
            with self.assertRaises(ValueError):
                validate_lesson(lesson, valid_v2_course())

    def test_numeric_evaluation_rejects_huge_integer_answer_and_tolerance(self):
        for field in ("answer", "tolerance"):
            lesson = valid_lesson()
            lesson["exercises"][0]["evaluation"][field] = 10 ** 400
            with self.assertRaises(ValueError):
                validate_lesson(lesson, valid_v2_course())


if __name__ == "__main__": unittest.main()
