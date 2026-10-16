"""Exercise saving and gated answers through the real local HTTP boundary."""
import http.client
import json
import shutil
from pathlib import Path
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/course-viewer/scripts'))
from tests.test_portal_interactions import open_lesson, reviewed_lesson
from course_workspace import create_workspace, publish_lesson
from tests.test_lesson_contract import valid_v2_course
from portal_interactions import read_attempts


class CourseServerReadinessTests(unittest.TestCase):
    def test_server_rejects_an_outline_without_a_ready_current_lesson(self):
        from serve_course import create_server
        with tempfile.TemporaryDirectory() as temporary:
            workspace = create_workspace(Path(temporary), 'alex', valid_v2_course())
            portal = workspace / 'portal'
            portal.mkdir(exist_ok=True)
            (portal / 'index.html').write_text('<html>Old outline</html>')
            with self.assertRaisesRegex(ValueError, 'no ready lesson'):
                create_server(workspace, port=0)


class CourseServerTests(unittest.TestCase):
    def setUp(self):
        from serve_course import create_server
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        plan = valid_v2_course()
        plan['chapters'][0]['topics'][0]['exercise_ids'].append('explain-gradient')
        self.workspace = create_workspace(Path(self.temp.name), 'alex', plan)
        lesson = open_lesson(plan)
        lesson['exercises'][1]['solution'] = r'The sign of $f\prime(x)$ predicts local change.'
        publish_lesson(self.workspace, reviewed_lesson(lesson))
        portal = self.workspace / 'portal'
        portal.mkdir(exist_ok=True)
        (portal / 'index.html').write_text('<html><head></head><body>Lesson</body></html>')
        self.server = create_server(self.workspace, port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.close_server)
        self.origin = f'http://127.0.0.1:{self.server.server_port}'

    def close_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def request(self, path, payload=None, **headers):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port)
        base = {'Origin': self.origin, 'X-GNOS-Session': self.server.session_token,
                'Content-Type': 'application/json'}
        base.update(headers)
        if payload is not None and path.endswith('/attempts') and 'exercise_fingerprint' not in payload:
            from portal_interactions import _find_exercise, exercise_fingerprint
            exercise_id = path.split('/')[3]
            payload = dict(payload, exercise_fingerprint=exercise_fingerprint(
                _find_exercise(self.workspace, exercise_id)['exercise']))
        if payload is not None and path.endswith('/attempts') and 'lesson_fingerprint' not in payload:
            from portal_interactions import _find_exercise
            from lesson_contract import lesson_fingerprint
            payload = dict(payload, lesson_fingerprint=lesson_fingerprint(
                _find_exercise(self.workspace, path.split('/')[3])['lesson']))
        connection.request('POST' if payload is not None else 'GET', path,
                           json.dumps(payload) if payload is not None else None, base)
        response = connection.getresponse()
        status, body = response.status, response.read().decode()
        connection.close()
        return status, body

    def test_save_survives_restart_and_reveal_requires_that_exercise_attempt(self):
        status, _ = self.request('/api/exercises/explain-gradient/reveal', {'attempt_id': 'missing'})
        self.assertEqual(status, 400)
        payload = {'response': {'text': 'Positive means increasing locally.'}, 'attempt_id': 'attempt-one'}
        status, body = self.request('/api/exercises/explain-gradient/attempts', payload)
        self.assertEqual(status, 200, body)
        self.assertNotIn('solution', json.loads(body))
        saved = self.workspace / 'submissions/explain-gradient/attempt-one.json'
        self.assertEqual(json.loads(saved.read_text())['response'], payload['response'])
        # A retry must not create a second attempt.
        self.request('/api/exercises/explain-gradient/attempts', payload)
        self.assertEqual(len(read_attempts(self.workspace)), 1)
        status, _ = self.request('/api/exercises/predict-change/reveal', {'attempt_id': 'attempt-one'})
        self.assertEqual(status, 400)
        status, body = self.request('/api/exercises/explain-gradient/reveal', {'attempt_id': 'attempt-one'})
        self.assertEqual(status, 200, body)
        self.assertIn(r'f\prime(x)', body.replace('\\\\', '\\'))
        self.assertTrue(json.loads(saved.read_text())['solution_revealed_at'])
        self.close_server()
        from serve_course import create_server
        self.server = create_server(self.workspace, port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.origin = f'http://127.0.0.1:{self.server.server_port}'
        status, body = self.request('/api/exercises/explain-gradient')
        self.assertEqual(status, 200, body)
        self.assertEqual(json.loads(body)['attempt']['response'], payload['response'])

    def test_origin_token_and_private_file_boundaries(self):
        payload = {'response': {'value': 1}, 'attempt_id': 'attempt-one'}
        self.assertEqual(self.request('/api/exercises/predict-change/attempts', payload,
                                     Origin='https://example.com')[0], 403)
        self.assertEqual(self.request('/api/exercises/predict-change/attempts', payload,
                                     **{'X-GNOS-Session': 'wrong'})[0], 403)
        self.assertEqual(read_attempts(self.workspace), [])
        for path in ['/course.json', '/lessons/slope-introduction/lesson.json',
                     '/portal/../course.json', '/submissions/attempt-one.json']:
            self.assertEqual(self.request(path)[0], 404, path)
        status, body = self.request('/portal/')
        self.assertEqual(status, 200)
        self.assertIn(self.server.session_token, body)
        self.assertNotIn('predicts local change', body)

    def test_only_bundled_viewer_assets_are_served(self):
        from render_viewer import VENDOR
        assets = self.workspace / 'portal/assets'
        shutil.copytree(VENDOR, assets)
        (assets / 'private.txt').write_text('not a viewer asset')
        for asset in ('katex/katex.min.js', 'katex/auto-render.min.js',
                      'highlight/highlight.min.js'):
            status, body = self.request('/portal/assets/' + asset)
            self.assertEqual(status, 200, asset)
            self.assertTrue(body)
        self.assertEqual(self.request('/portal/assets/private.txt')[0], 404)

    def test_server_stops_serving_an_old_page_when_current_lesson_becomes_draft(self):
        lesson_path = self.workspace / 'lessons/slope-introduction/lesson.json'
        lesson = json.loads(lesson_path.read_text())
        lesson['publication'] = 'draft'
        lesson_path.write_text(json.dumps(lesson))

        status, body = self.request('/portal/')
        self.assertEqual(status, 400)
        self.assertIn('no ready lesson', body)

    def test_invalid_response_is_not_saved(self):
        status, _ = self.request('/api/exercises/predict-change/attempts',
                                 {'response': {'value': 'not a number'}})
        self.assertEqual(status, 400)
        self.assertEqual(read_attempts(self.workspace), [])

    def test_draft_and_question_endpoints_persist_without_creating_evidence(self):
        from portal_interactions import exercise_state, answer_question
        state = exercise_state(self.workspace, 'predict-change')
        draft = {'response': {'value': '-'}, 'revision': 0,
                 'exercise_fingerprint': state['exercise_fingerprint'],
                 'lesson_fingerprint': state['lesson_fingerprint'], 'base_attempt_id': None}
        self.assertEqual(self.request('/api/exercises/predict-change/draft', draft,
                         **{'X-GNOS-Session': 'wrong'})[0], 403)
        status, body = self.request('/api/exercises/predict-change/draft', draft)
        self.assertEqual(status, 200, body)
        self.assertEqual(json.loads(body)['revision'], 1)
        self.assertEqual(self.request('/api/exercises/predict-change/draft', draft)[0], 200)
        self.assertEqual(self.request('/api/exercises/predict-change/draft',
                         dict(draft, response={'value': 'newer text'}))[0], 400)
        self.assertEqual(read_attempts(self.workspace), [])
        self.request('/api/exercises/predict-change/attempts',
                     {'response': {'value': 0}, 'attempt_id': 'question-attempt'})
        question = {'question_id': 'question-one', 'text': 'Where did my comparison go wrong?',
                    'context': {'course_id': 'gradient-descent', 'exercise_id': 'predict-change',
                                'attempt_id': 'question-attempt'}}
        status, body = self.request('/api/questions', question)
        self.assertEqual(status, 200, body)
        self.assertNotIn('exercise_snapshot', body)
        self.assertEqual(self.request('/api/questions', question)[0], 200)
        answer_question(self.workspace, 'question-one', 'Compare the sign with the local change.')
        status, body = self.request('/api/questions')
        self.assertEqual(status, 200, body)
        self.assertEqual(len(json.loads(body)['questions']), 1)
        self.assertIn('Compare the sign', body)
        self.assertNotIn('success_criteria', body)

    def test_stale_displayed_question_is_rejected_without_saving(self):
        from portal_interactions import _find_exercise, exercise_fingerprint
        version = exercise_fingerprint(_find_exercise(self.workspace, 'predict-change')['exercise'])
        lesson = json.loads((self.workspace / 'lessons/slope-introduction/lesson.json').read_text())
        lesson['exercises'][0]['prompt'] = 'A different prediction.'
        publish_lesson(self.workspace, reviewed_lesson(lesson))
        status, body = self.request('/api/exercises/predict-change/attempts',
            {'response': {'value': 1}, 'attempt_id': 'stale-attempt', 'exercise_fingerprint': version})
        self.assertEqual(status, 400)
        self.assertIn('changed', body)
        self.assertEqual(read_attempts(self.workspace), [])

    def test_stale_teaching_is_rejected_even_when_the_question_is_unchanged(self):
        from lesson_contract import lesson_fingerprint
        lesson = json.loads((self.workspace / 'lessons/slope-introduction/lesson.json').read_text())
        old = lesson_fingerprint(lesson)
        lesson['blocks'][0]['text'] += ' A new prerequisite bridge.'
        publish_lesson(self.workspace, reviewed_lesson(lesson))
        status, body = self.request('/api/exercises/predict-change/attempts',
            {'response': {'value': 1}, 'attempt_id': 'stale-teaching', 'lesson_fingerprint': old})
        self.assertEqual(status, 400)
        self.assertIn('changed', body)
        self.assertEqual(read_attempts(self.workspace), [])

    def test_exercise_reload_returns_review_and_original_history_without_private_rubric(self):
        from portal_interactions import review_attempt
        self.request('/api/exercises/predict-change/attempts',
                     {'response': {'value': 0}, 'attempt_id': 'attempt-reviewed'})
        review_attempt(self.workspace, 'attempt-reviewed', dict(result='incorrect', help='none',
            kind='application', interpretation='Confuses sign and height.', next_step='Compare two slopes.'))
        status, body = self.request('/api/exercises/predict-change')
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertEqual(data['attempt']['review']['result'], 'incorrect')
        self.assertEqual(data['history'][0]['prompt'], 'Predict the sign.')
        for field in ('exercise_snapshot', 'teaching_blocks', 'success_criteria', 'tolerance'):
            self.assertNotIn(field, body)
        status, body = self.request('/api/review')
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)['decision'], 'review-required')
