"""Content review stays bound to the exact authored lesson, separate from snapshots."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/course-design/scripts'))
from course_contract import validate_course
from course_workspace import create_workspace, publish_lesson, read_plan
import lesson_contract
from tests.test_course_workspace import valid_lesson, valid_v2_course


def reviewed(lesson):
    lesson['design_receipt'].update(
        schema_version=2,
        lesson_content_fingerprint=lesson_contract.lesson_design_fingerprint(lesson))
    return lesson


class DesignBindingTests(unittest.TestCase):
    def test_authored_changes_stale_review_but_bookkeeping_does_not(self):
        course = validate_course(valid_v2_course())
        lesson = reviewed(valid_lesson('ready', course))
        original = lesson_contract.lesson_design_fingerprint(lesson)
        for change in ('explanation', 'answer', 'brief'):
            with self.subTest(change=change):
                changed = copy.deepcopy(lesson)
                if change == 'explanation':
                    changed['blocks'][0]['text'] = 'A different explanation.'
                elif change == 'answer':
                    changed['exercises'][0]['evaluation']['answer'] = -1
                else:
                    changed['blocks'][0]['production']['brief'] = 'A different teaching job.'
                self.assertNotEqual(lesson_contract.lesson_design_fingerprint(changed), original)
                with self.assertRaisesRegex(ValueError, 'lesson_content_fingerprint'):
                    lesson_contract.validate_lesson(changed, course)
        bookkeeping = copy.deepcopy(lesson)
        bookkeeping['publication'] = 'draft'
        bookkeeping['updated_at'] = '2026-09-12T16:01:00Z'
        bookkeeping['design_receipt']['private_notes'] = 'Private reviewer observation.'
        self.assertEqual(lesson_contract.lesson_design_fingerprint(bookkeeping), original)
        lesson_contract.validate_lesson(bookkeeping, course)
        self.assertNotEqual(lesson_contract.lesson_fingerprint(bookkeeping),
                            lesson_contract.lesson_fingerprint(lesson))

    def test_private_receipt_fields_are_never_public(self):
        lesson = valid_lesson('ready')
        lesson['design_receipt']['private_notes'] = 'The answer is 31415.'
        self.assertNotIn('private_notes', lesson_contract.public_lesson(lesson)['design_receipt'])

    def test_legacy_read_allowed_but_new_ready_publication_needs_binding(self):
        course = validate_course(valid_v2_course())
        lesson = valid_lesson('ready', course)
        lesson['design_receipt'].pop('schema_version', None)
        lesson['design_receipt'].pop('lesson_content_fingerprint', None)
        self.assertEqual(lesson_contract.validate_lesson(lesson, course), lesson)
        with tempfile.TemporaryDirectory() as temp:
            workspace = create_workspace(Path(temp), 'fixture', course)
            before = (workspace / 'course.json').read_bytes()
            with self.assertRaisesRegex(ValueError, 'content-bound'):
                publish_lesson(workspace, lesson)
            self.assertEqual((workspace / 'course.json').read_bytes(), before)
            self.assertFalse((workspace / 'lessons' / lesson['id'] / 'lesson.json').exists())
            publish_lesson(workspace, reviewed(lesson))
            self.assertEqual(read_plan(workspace)['chapters'][0]['topics'][0]['lesson_ids'], [lesson['id']])

    def test_stale_review_cannot_replace_existing_published_bytes(self):
        course = validate_course(valid_v2_course())
        lesson = reviewed(valid_lesson('ready', course))
        with tempfile.TemporaryDirectory() as temp:
            workspace = create_workspace(Path(temp), 'fixture', course)
            publish_lesson(workspace, lesson)
            file = workspace / 'lessons' / lesson['id'] / 'lesson.json'
            before = file.read_bytes()
            lesson['blocks'][0]['text'] = 'Changed after review.'
            with self.assertRaisesRegex(ValueError, 'lesson_content_fingerprint'):
                publish_lesson(workspace, lesson)
            self.assertEqual(file.read_bytes(), before)
