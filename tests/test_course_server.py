"""Exercise saving and gated answers through the real local HTTP boundary."""
import http.client
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/course-viewer/scripts'))
from tests.test_portal_interactions import open_lesson
from course_workspace import create_workspace, publish_lesson
from tests.test_lesson_contract import valid_v2_course
from portal_interactions import read_attempts


class CourseServerTests(unittest.TestCase):
    def setUp(self):
        from serve_course import create_server
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        plan = valid_v2_course()
        plan['chapters'][0]['topics'][0]['exercise_ids'].append('explain-gradient')
        self.workspace = create_workspace(Path(self.temp.name), 'alex', plan)
        lesson = open_lesson()
        lesson['exercises'][1]['solution'] = r'The sign of $f\prime(x)$ predicts local change.'
        publish_lesson(self.workspace, lesson)
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

    def test_invalid_response_is_not_saved(self):
        status, _ = self.request('/api/exercises/predict-change/attempts',
                                 {'response': {'value': 'not a number'}})
        self.assertEqual(status, 400)
        self.assertEqual(read_attempts(self.workspace), [])
