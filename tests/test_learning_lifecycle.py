"""Temporary learners exercise the actual draft, question, and viewer boundaries."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
import threading
import subprocess
import os

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/course-design/scripts'))
sys.path.insert(0, str(ROOT / 'skills/course-viewer/scripts'))
from tests.test_portal_interactions import open_lesson
from tests.test_lesson_contract import valid_v2_course
from course_workspace import create_workspace, publish_lesson, ConflictError
from lesson_contract import exercise_fingerprint, lesson_fingerprint
from portal_interactions import (save_draft, exercise_state, submit_attempt, read_attempts,
    create_question, answer_question, request_hint, review_attempt)
from portal_views import build_portal_view
import render_viewer as viewer
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


class LearningLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.plan = valid_v2_course()
        self.plan['chapters'][0]['topics'][0]['exercise_ids'].append('explain-gradient')
        self.workspace = create_workspace(Path(self.temp.name), 'alex', self.plan)
        self.lesson = open_lesson(self.plan)
        self.publish()

    def publish(self):
        from course_contract import course_content_fingerprint
        from lesson_contract import lesson_design_fingerprint
        self.lesson['design_receipt']['course_fingerprint'] = course_content_fingerprint(self.plan)
        self.lesson['design_receipt'].update(schema_version=2,
            lesson_content_fingerprint=lesson_design_fingerprint(self.lesson))
        publish_lesson(self.workspace, self.lesson)

    def versions(self, index=0):
        return dict(expected_exercise_fingerprint=exercise_fingerprint(self.lesson['exercises'][index]),
                    expected_lesson_fingerprint=lesson_fingerprint(self.lesson))

    def test_unfinished_draft_is_versioned_and_does_not_submit(self):
        first = save_draft(self.workspace, 'predict-change', {'value': '-'},
                           expected_revision=0, **self.versions())
        self.assertEqual(first['revision'], 1)
        retry = save_draft(self.workspace, 'predict-change', {'value': '-'},
                           expected_revision=0, **self.versions())
        self.assertEqual(retry['revision'], first['revision'])
        self.assertEqual(exercise_state(self.workspace, 'predict-change')['draft']['response'], {'value': '-'})
        self.assertEqual(read_attempts(self.workspace), [])
        with self.assertRaises(ValueError):
            submit_attempt(self.workspace, 'predict-change', {'value': '-'})
        with self.assertRaises(ConflictError):
            save_draft(self.workspace, 'predict-change', {'value': '2'}, expected_revision=0, **self.versions())
        self.assertEqual(exercise_state(self.workspace, 'predict-change')['draft']['response'], {'value': '-'})

    def test_submit_clears_only_matching_revision_and_retains_monotonic_revision(self):
        first = save_draft(self.workspace, 'predict-change', {'value': '1'}, expected_revision=0, **self.versions())
        second = save_draft(self.workspace, 'predict-change', {'value': '2'}, expected_revision=1, **self.versions())
        submit_attempt(self.workspace, 'predict-change', {'value': 1}, attempt_id='older-save',
                       draft_revision=first['revision'], **self.versions())
        state = exercise_state(self.workspace, 'predict-change')
        self.assertEqual(state['draft']['revision'], second['revision'])
        submit_attempt(self.workspace, 'predict-change', {'value': 2}, attempt_id='current-save',
                       draft_revision=second['revision'], **self.versions())
        state = exercise_state(self.workspace, 'predict-change')
        self.assertIsNone(state['draft'])
        self.assertGreater(state['draft_revision'], second['revision'])
        with self.assertRaises(ConflictError):
            save_draft(self.workspace, 'predict-change', {'value': '3'}, expected_revision=2, **self.versions())

    def test_stale_draft_is_preserved_but_not_restored_over_new_lesson(self):
        save_draft(self.workspace, 'predict-change', {'value': '-'}, expected_revision=0, **self.versions())
        old = self.versions()
        self.lesson['blocks'][0]['text'] += ' A clarified explanation.'
        self.publish()
        state = exercise_state(self.workspace, 'predict-change')
        self.assertIsNone(state['draft'])
        self.assertTrue(state['stale_draft'])
        with self.assertRaises(ConflictError):
            save_draft(self.workspace, 'predict-change', {'value': '2'}, expected_revision=1, **old)

    def test_question_answer_renders_and_attempt_context_survives_draft_lesson(self):
        attempt = submit_attempt(self.workspace, 'predict-change', {'value': 0}, attempt_id='original-answer')
        self.lesson['publication'] = 'draft'
        self.publish()
        question = {'text': 'Why did my sign comparison fail?', 'context': {
            'course_id': self.plan['id'], 'exercise_id': 'predict-change', 'attempt_id': attempt['id']}}
        first = create_question(self.workspace, question, 'question-one')
        self.assertEqual(create_question(self.workspace, question, 'question-one')['id'], first['id'])
        answer_question(self.workspace, first['id'], 'Compare the change with the slope.')
        html = ''.join(viewer.render_questions(build_portal_view(self.workspace, {})))
        self.assertIn('Compare the change with the slope.', html)
        self.assertEqual(len(read_attempts(self.workspace)), 1)

    def test_hint_follows_same_task_renamed_but_later_hint_is_not_retroactive(self):
        request_hint(self.workspace, 'predict-change')
        self.plan['chapters'][0]['topics'][0]['exercise_ids'][0] = 'renamed-prediction'
        from course_workspace import atomic_json
        atomic_json(self.workspace / 'course.json', self.plan)
        self.lesson['exercises'][0]['id'] = 'renamed-prediction'
        for block in self.lesson['blocks']:
            if block.get('exercise_id') == 'predict-change': block['exercise_id'] = 'renamed-prediction'
        self.publish()
        attempt = submit_attempt(self.workspace, 'renamed-prediction', {'value': 1})
        self.assertTrue(attempt['hint_requested_before_submission'])
        with self.assertRaisesRegex(ValueError, 'hint assistance'):
            review_attempt(self.workspace, attempt['id'], dict(result='correct', help='none', kind='application',
                interpretation='Correct sign.', next_step='Transfer.'))

    def test_hint_requested_after_submission_does_not_change_that_attempt(self):
        attempt = submit_attempt(self.workspace, 'predict-change', {'value': 1})
        request_hint(self.workspace, 'predict-change', attempt['id'])
        reviewed = review_attempt(self.workspace, attempt['id'], dict(result='correct', help='none',
            kind='application', interpretation='Predicted before requesting help.', next_step='Transfer.'))
        self.assertEqual(reviewed['review']['help'], 'none')

    def test_registered_companions_have_usable_controls_and_unknown_ids_do_not(self):
        video = dict(id='video', title='Video', mime_type='video/mp4', type='video',
                     location={'path': 'artifacts/video.mp4'}, metadata={'captions': 'captions', 'transcript': 'transcript'})
        companions = {'captions': dict(id='captions', status='ready', mime_type='text/vtt', location={'path': 'artifacts/captions.vtt'}),
                      'transcript': dict(id='transcript', status='ready', mime_type='text/plain', location={'path': 'artifacts/transcript.txt'})}
        (self.workspace / 'artifacts/captions.vtt').write_text('WEBVTT\n\n00:00.000 --> 00:01.000\nHello\n')
        (self.workspace / 'artifacts/transcript.txt').write_text('Hello')
        html = viewer.render_media(video, 'watch', self.workspace, companions)
        self.assertIn('<track ', html)
        self.assertIn('../artifacts/captions.vtt', html)
        self.assertIn('href="../artifacts/transcript.txt"', html)
        self.assertNotIn('<track ', viewer.render_media(video, 'watch', self.workspace, {}))
        for changes in ({'status': 'draft'}, {'location': {'url': 'https://example.com/captions.vtt'}},
                        {'mime_type': 'application/x-subrip'}):
            altered = copy.deepcopy(companions)
            altered['captions'].update(changes)
            self.assertNotIn('<track ', viewer.render_media(video, 'watch', self.workspace, altered))
        altered = copy.deepcopy(companions)
        altered['transcript']['mime_type'] = 'video/mp4'
        self.assertNotIn('Open transcript', viewer.render_media(video, 'watch', self.workspace, altered))

    @unittest.skipUnless(sync_playwright, 'Playwright is unavailable')
    def test_browser_draft_submit_question_review_and_scoped_tabs(self):
        from serve_course import create_server
        from portal_interactions import review_attempt
        subprocess.run([sys.executable, str(ROOT / 'skills/course-viewer/scripts/render_viewer.py'),
                        str(self.workspace)], check=True, capture_output=True, text=True)
        server = create_server(self.workspace, port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(channel='chrome', headless=True)
                try:
                    page = browser.new_page()
                    page.goto(f'http://127.0.0.1:{server.server_port}/portal/')
                    page.locator('#tabs [data-tab="exercises"]').click()
                    card = page.locator('#tab-exercises [data-exercise-id="predict-change"]')
                    field = card.locator('[name="answer"]')
                    field.fill('-')
                    page.wait_for_function("document.querySelector('#tab-exercises [data-exercise-id=\"predict-change\"] .exercise-status').textContent.includes('Draft saved')")
                    page.reload()
                    page.locator('#tabs [data-tab="exercises"]').click()
                    field = card.locator('[name="answer"]')
                    self.assertEqual(field.input_value(), '-')
                    field.fill('1')
                    page.route('**/api/exercises/predict-change/attempts', lambda route: route.abort())
                    card.locator('[type="submit"]').click()
                    page.wait_for_function("document.querySelector('#tab-exercises [data-exercise-id=\"predict-change\"] .exercise-status').textContent.startsWith('Not saved.')")
                    self.assertEqual(field.input_value(), '1')
                    self.assertIsNone(page.evaluate("localStorage.getItem('gnos:exercise:gradient-descent:predict-change')"),
                                      'The legacy browser-only save handler must not run alongside server persistence')
                    page.unroute('**/api/exercises/predict-change/attempts')
                    card.locator('[type="submit"]').click()
                    page.wait_for_function("document.querySelector('#tab-exercises [data-exercise-id=\"predict-change\"] .exercise-status').textContent.startsWith('Saved.')")
                    self.assertEqual(len(read_attempts(self.workspace)), 1)
                    self.assertIsNone(exercise_state(self.workspace, 'predict-change')['draft'])
                    card.locator('.request-feedback').click()
                    card.locator('.feedback-text').fill('Why is the sign positive?')
                    with page.expect_response(lambda response: response.url.endswith('/api/questions') and response.request.method == 'POST'):
                        card.locator('.send-feedback').click()
                    page.wait_for_function("document.querySelector('#tab-exercises .feedback-status').textContent.includes('Pending')")
                    with page.expect_response(lambda response: response.url.endswith('/api/questions') and response.request.method == 'POST'):
                        card.locator('.send-feedback').click()
                    from portal_interactions import list_pending
                    pending = list_pending(self.workspace)['questions']
                    self.assertEqual(len(pending), 1)
                    answer_question(self.workspace, pending[0]['id'], 'The height increases when x increases.')
                    review_attempt(self.workspace, read_attempts(self.workspace)[0]['id'], dict(result='correct',
                        help='none', kind='application', interpretation='Correct prediction.', next_step='Explain the reason.'))
                    field.fill('Unfinished newer work')
                    page.evaluate('window.dispatchEvent(new Event("focus"))')
                    page.wait_for_function("document.querySelector('.course-questions').textContent.includes('The height increases')")
                    self.assertEqual(field.input_value(), 'Unfinished newer work')
                    sources = page.locator('#tabs [data-tab="sources"]')
                    sources.focus()
                    sources.press('ArrowRight')
                    self.assertEqual(page.locator('#tabs [aria-selected="true"]').get_attribute('data-tab'), 'artifacts')
                    self.assertEqual(page.locator('#tabs button[tabindex="0"]').count(), 1)
                    page.locator('#tabs [data-tab="exercises"]').click()
                    field.focus()
                    field.press('ArrowLeft')
                    self.assertEqual(page.locator('#tabs [aria-selected="true"]').get_attribute('data-tab'), 'exercises')
                    if os.environ.get('GNOS_LIFECYCLE_SCREENSHOT'):
                        page.screenshot(path=os.environ['GNOS_LIFECYCLE_SCREENSHOT'], full_page=True)
                finally:
                    browser.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    @unittest.skipUnless(sync_playwright, 'Playwright is unavailable')
    def test_browser_serializes_late_drafts_across_duplicate_cards_and_restart(self):
        from serve_course import create_server
        save_draft(self.workspace, 'explain-gradient', {'text': 'An older acknowledged draft'},
                   expected_revision=0, **self.versions(1))
        subprocess.run([sys.executable, str(ROOT / 'skills/course-viewer/scripts/render_viewer.py'),
                        str(self.workspace)], check=True, capture_output=True, text=True)
        server = create_server(self.workspace, port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(channel='chrome', headless=True)
                try:
                    page = browser.new_page()
                    page.set_default_timeout(7000)
                    held, initial, draft_requests = [], [], []
                    def delay_initial_state(route):
                        response = route.fetch()
                        initial.append((route, response))
                        page.evaluate('window.initialStateHeld = true')
                    page.route('**/api/exercises/explain-gradient', delay_initial_state)
                    def delay_first_draft(route):
                        draft_requests.append(route.request.post_data_json)
                        if len(draft_requests) == 1:
                            response = route.fetch()
                            held.append((route, response))
                            page.evaluate('window.firstDraftHeld = true')
                        else:
                            route.continue_()
                    page.route('**/api/exercises/explain-gradient/draft', delay_first_draft)
                    page.goto(f'http://127.0.0.1:{server.server_port}/portal/')
                    page.locator('#tabs [data-tab="exercises"]').click()
                    card = page.locator('#tab-exercises [data-exercise-id="explain-gradient"]')
                    field = card.locator('[name="answer"]')
                    page.wait_for_function('window.initialStateHeld === true')
                    field.fill('First unfinished reasoning')
                    initial[0][0].fulfill(response=initial[0][1])
                    page.unroute('**/api/exercises/explain-gradient', delay_initial_state)
                    page.wait_for_function('window.firstDraftHeld === true')
                    self.assertEqual(draft_requests[0]['revision'], 1)
                    field.fill('Newer reasoning while the first save is delayed')
                    page.wait_for_timeout(500)
                    self.assertEqual(len(draft_requests), 1, 'Autosaves must remain serialized')
                    held[0][0].fulfill(response=held[0][1])
                    page.wait_for_function("document.querySelector('#tab-exercises [data-exercise-id=\"explain-gradient\"] .exercise-status').textContent.includes('Draft saved')")
                    self.assertEqual(field.input_value(), 'Newer reasoning while the first save is delayed')
                    fields = page.locator('[data-exercise-id="explain-gradient"] [name="answer"]')
                    self.assertEqual(fields.count(), 2)
                    self.assertEqual(fields.nth(0).input_value(), fields.nth(1).input_value())
                    self.assertEqual(exercise_state(self.workspace, 'explain-gradient')['draft']['response']['text'], field.input_value())
                    server.shutdown(); server.server_close(); thread.join()
                    server = create_server(self.workspace, port=0)
                    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
                    page.goto(f'http://127.0.0.1:{server.server_port}/portal/')
                    page.locator('#tabs [data-tab="exercises"]').click()
                    page.wait_for_function("document.querySelector('#tab-exercises [data-exercise-id=\"explain-gradient\"] textarea[name=answer]').value.startsWith('Newer reasoning')")
                    card.locator('[type="submit"]').click()
                    page.wait_for_function("document.querySelector('#tab-exercises [data-exercise-id=\"explain-gradient\"] .exercise-status').textContent.startsWith('Saved.')")
                    self.assertTrue(card.locator('.reveal-answer').is_disabled(), 'No solution is authored for this exercise')
                    self.assertEqual(len(read_attempts(self.workspace)), 1)
                finally:
                    browser.close()
        finally:
            server.shutdown(); server.server_close(); thread.join()


if __name__ == '__main__': unittest.main()
