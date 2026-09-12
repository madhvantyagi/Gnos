"""Version-two living-course contract tests."""
import copy
import unittest

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/course-design/scripts"))

import course_contract as contract


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


def valid_v1_course():
    return {
        "schema_version": 1,
        "id": "gradient-descent",
        "title": "Gradient descent",
        "goal": "Explain and implement gradient descent.",
        "revision": 1,
        "assumptions": ["Derivatives are unverified."],
        "modules": [{
            "id": "derivatives",
            "title": "Derivatives",
            "outcome": "Compute a local slope.",
            "subject": "math",
            "teacher": "math",
            "supporting_teachers": [],
            "concepts": ["math.derivative"],
            "prerequisites": [],
            "minutes": 20,
            "assessment": {
                "prompt": "Find a slope.",
                "success_criteria": ["Explain the sign."],
            },
            "resources": ["openstax-calculus-1"],
        }],
    }


class CourseContractV2Tests(unittest.TestCase):
    def test_v2_course_accepts_chapters_topics_routes_and_sources(self):
        checked = contract.validate_course(valid_v2_course())
        self.assertEqual(checked["current"]["topic_id"], "local-change")
        self.assertEqual(contract.course_topics(checked)[0]["id"], "local-change")

    def test_v2_course_rejects_unknown_teacher_skill_and_forward_dependency(self):
        mutations = []
        unknown_teacher = valid_v2_course()
        unknown_teacher["chapters"][0]["topics"][0]["teacher"] = "missing"
        mutations.append(unknown_teacher)
        unknown_skill = valid_v2_course()
        unknown_skill["chapters"][0]["topics"][0]["skill_routes"] = [
            "skills/subject/../course-design/SKILL.md"
        ]
        mutations.append(unknown_skill)
        forward_dependency = valid_v2_course()
        forward_dependency["chapters"][0]["topics"][0]["prerequisites"] = [
            "later-topic"
        ]
        mutations.append(forward_dependency)
        for mutation in mutations:
            with self.assertRaises(ValueError):
                contract.validate_course(mutation)

    def test_v1_upgrade_is_deterministic_and_preserves_concepts(self):
        first = contract.upgrade_v1_course(valid_v1_course())
        second = contract.upgrade_v1_course(valid_v1_course())
        self.assertEqual(first, second)
        self.assertEqual(first["schema_version"], 2)
        self.assertIn("math.derivative", first["chapters"][0]["topics"][0]["concepts"])
        self.assertEqual(contract.validate_course(valid_v1_course()), first)

    def test_course_fingerprint_is_stable_and_changes_with_data(self):
        plan = valid_v2_course()
        original = contract.course_fingerprint(plan)
        self.assertEqual(original, contract.course_fingerprint(copy.deepcopy(plan)))
        plan["revision"] = 2
        self.assertNotEqual(original, contract.course_fingerprint(plan))

    def test_v2_rejects_duplicate_ids_and_invalid_skill_route(self):
        duplicate = valid_v2_course()
        duplicate["chapters"].append(copy.deepcopy(duplicate["chapters"][0]))
        with self.assertRaises(ValueError):
            contract.validate_course(duplicate)
        invalid = valid_v2_course()
        invalid["chapters"][0]["topics"][0]["skill_routes"] = [
            "skills/subject/references/resources.json"
        ]
        with self.assertRaises(ValueError):
            contract.validate_course(invalid)

    def test_v2_rejects_multiple_current_topics(self):
        plan = valid_v2_course()
        second_chapter = copy.deepcopy(plan["chapters"][0])
        second_chapter["id"] = "next-change"
        second_chapter["topics"][0]["id"] = "global-change"
        second_chapter["topics"][0]["state"] = "current"
        second_chapter["topics"][0]["concepts"] = ["math.gradient"]
        second_chapter["topics"][0]["exercise_ids"] = ["predict-global-change"]
        second_chapter["topics"][0]["prerequisites"] = ["local-change"]
        plan["chapters"].append(second_chapter)
        with self.assertRaises(ValueError):
            contract.validate_course(plan)

    def test_v2_rejects_current_topic_in_noncurrent_chapter(self):
        plan = valid_v2_course()
        plan["chapters"][0]["state"] = "planned"
        with self.assertRaises(ValueError):
            contract.validate_course(plan)

    def test_v2_requires_https_source_urls(self):
        plan = valid_v2_course()
        plan["sources"]["openstax-calculus-1"]["url"] = (
            "http://openstax.org/details/books/calculus-volume-1"
        )
        with self.assertRaises(ValueError):
            contract.validate_course(plan)

    def test_v2_rejects_absolute_and_traversing_source_paths(self):
        for local_path in ("/etc/passwd", "../skills/subject/references/resources.json"):
            plan = valid_v2_course()
            source = plan["sources"]["openstax-calculus-1"]
            del source["url"]
            source["local_path"] = local_path
            with self.assertRaises(ValueError):
                contract.validate_course(plan)

    def test_v2_accepts_safe_repository_relative_source_path(self):
        plan = valid_v2_course()
        source = plan["sources"]["openstax-calculus-1"]
        del source["url"]
        source["local_path"] = "skills/subject/references/resources.json"
        self.assertEqual(contract.validate_course(plan), plan)

    def test_v1_upgrade_uses_exact_legacy_revision_sentinel(self):
        upgraded = contract.upgrade_v1_course(valid_v1_course())
        self.assertEqual(upgraded["revision_notes"][0]["date"], "1970-01-01")
        self.assertEqual(
            upgraded["revision_notes"][0]["reason"],
            "Original revision date unavailable; deterministically upgraded from schema version 1.",
        )

    def test_v2_rejects_non_iso_revision_note_date(self):
        plan = valid_v2_course()
        plan["revision_notes"][0]["date"] = "2026-02-30"
        with self.assertRaises(ValueError):
            contract.validate_course(plan)


if __name__ == "__main__":
    unittest.main()
