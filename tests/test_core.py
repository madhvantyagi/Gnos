"""Exercise persisted evidence and course contracts through their public CLIs."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'skills/understanding-user-learning/scripts/learner_state.py'
COURSE = ROOT / 'skills/course-design/scripts/validate_course.py'


class LearnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def call(self, *args):
        return subprocess.run([sys.executable, str(STATE), '--root', str(self.root), *args],
                              text=True, capture_output=True)

    def event(self, **overrides):
        data = dict(id='first', date='2026-01-01', course_id='motion',
                    covered=['math.derivative'], attempts=[], interpretation='',
                    next_step='Try a new slope problem.')
        data.update(overrides)
        path = self.root / 'event.json'
        path.write_text(json.dumps(data))
        return str(path)

    def summary(self, learner='alex'):
        result = self.call('summary', learner)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_exposure_is_not_demonstrated_and_retry_does_not_duplicate(self):
        event = self.event()
        for _ in range(2):
            result = self.call('record', 'alex', '--event', event)
            self.assertEqual(result.returncode, 0, result.stderr)
        summary = self.summary()
        self.assertEqual(summary['session_count'], 1)
        self.assertEqual(summary['concepts']['math.derivative']['status'], 'exposed')

    def test_hint_delayed_transfer_and_later_error_change_evidence(self):
        attempt = dict(concept='math.derivative', task='Slope at a new point',
                       response='Correct slope with reason', result='correct',
                       help='hint', kind='application')
        for id_, date, help_, kind, result_, want in [
            ('one', '2026-01-01', 'hint', 'application', 'correct', 'practicing'),
            ('two', '2026-01-02', 'none', 'application', 'correct', 'demonstrated'),
            ('three', '2026-01-04', 'none', 'transfer', 'correct', 'retained'),
            ('four', '2026-01-05', 'none', 'application', 'incorrect', 'practicing')]:
            attempt.update(help=help_, kind=kind, result=result_)
            result = self.call('record','alex','--event',self.event(id=id_,date=date,attempts=[attempt]))
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(self.summary()['concepts']['math.derivative']['status'],want)

    def test_conflicting_retry_and_invalid_evidence_preserve_state(self):
        self.assertEqual(self.call('record','alex','--event',self.event()).returncode,0)
        before = (self.root/'alex/state.json').read_bytes()
        result = self.call('record','alex','--event',self.event(next_step='Conflicting retry'))
        self.assertNotEqual(result.returncode,0)
        result = self.call('record','alex','--event',self.event(id='bad',date='2099-01-01'))
        self.assertNotEqual(result.returncode,0)
        self.assertEqual((self.root/'alex/state.json').read_bytes(),before)

    def test_isolation_path_validation_and_retraction(self):
        self.assertEqual(self.call('record','alex','--event',self.event()).returncode,0)
        self.assertEqual(self.call('init','bea').returncode,0)
        self.assertEqual(self.summary('bea')['session_count'],0)
        self.assertNotEqual(self.call('init','../outside').returncode,0)
        self.assertEqual(self.call('retract','alex','--event-id','first').returncode,0)
        self.assertEqual(self.summary()['concepts'],{})

    def test_active_lock_prevents_update(self):
        self.assertEqual(self.call('init','alex').returncode,0)
        (self.root/'.alex.lock').write_text('busy')
        result=self.call('record','alex','--event',self.event())
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(self.summary()['session_count'],0)

    def test_course_views_completion_retry_and_revision(self):
        plan=CourseTests().course()
        path=self.root/'course.json'; path.write_text(json.dumps(plan))
        self.assertEqual(self.call('enroll','alex','--course',str(path)).returncode,0)
        self.assertEqual(self.call('complete-course','alex','--course-id','test-course').returncode,0)
        before=json.loads((self.root/'alex/state.json').read_text())['courses']['test-course']
        self.assertEqual(self.call('enroll','alex','--course',str(path)).returncode,0)
        after=json.loads((self.root/'alex/state.json').read_text())['courses']['test-course']
        self.assertEqual(after,before)
        curriculum=self.root/'alex/memory/courses/test-course/CURRICULUM.md'
        self.assertIn('Chapter 1: Rates',curriculum.read_text())
        self.assertIn('not recorded as taught',curriculum.read_text())
        plan['revision']=2;plan['modules'][0]['concepts'].append('math.vector')
        path.write_text(json.dumps(plan))
        self.assertEqual(self.call('enroll','alex','--course',str(path)).returncode,0)
        self.assertEqual(self.summary()['courses']['test-course']['status'],'active')

    def test_invalid_topic_titles_cannot_poison_record(self):
        self.assertEqual(self.call('init','alex').returncode,0)
        before=(self.root/'alex/state.json').read_bytes()
        plan=CourseTests().course();plan['modules'][0]['topic_titles']=None
        path=self.root/'course.json';path.write_text(json.dumps(plan))
        self.assertNotEqual(self.call('enroll','alex','--course',str(path)).returncode,0)
        self.assertEqual((self.root/'alex/state.json').read_bytes(),before)

    def test_selected_course_resumes_its_own_event_and_enrolled_plan(self):
        plan=CourseTests().course();path=self.root/'course.json';path.write_text(json.dumps(plan))
        self.assertEqual(self.call('enroll','alex','--course',str(path)).returncode,0)
        self.call('record','alex','--event',self.event(course_id='test-course',next_step='Resume slope here'))
        self.call('record','alex','--event',self.event(id='other',date='2026-01-02',course_id='history',next_step='Read a diary'))
        loader=ROOT/'skills/learning/scripts/assemble_context.py'
        result=subprocess.run([sys.executable,str(loader),'--subject','math','--learner','alex',
                               '--learners-root',str(self.root),'--course-id','test-course'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('Resume slope here',result.stdout)
        self.assertIn('Predict motion',result.stdout)
        self.assertNotIn('Read a diary',result.stdout)


class CourseTests(unittest.TestCase):
    def check_course(self, data):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'course.json'; path.write_text(json.dumps(data))
            return subprocess.run([sys.executable,str(COURSE),str(path)],capture_output=True,text=True)

    def course(self):
        return dict(schema_version=1,id='test-course',title='Motion',goal='Predict motion',
                    revision=1,assumptions=['Can read a graph'],modules=[dict(
                        id='rates',title='Rates',outcome='Compute slope',subject='math',teacher='math',
                        supporting_teachers=[],concepts=['math.derivative'],prerequisites=[],minutes=20,
                        resources=['openstax-calculus-1'],assessment=dict(prompt='Find slope',
                        success_criteria=['Explain units']))])

    def test_valid_course_and_reject_unknown_teacher_resource_and_cycle(self):
        good=self.course()
        self.assertEqual(self.check_course(good).returncode,0)
        for field,value in [('teacher','missing'),('resources',['missing']),('prerequisites',['rates'])]:
            bad=copy.deepcopy(good); bad['modules'][0][field]=value
            self.assertNotEqual(self.check_course(bad).returncode,0,field)

    def test_reject_empty_assessment_and_nonpositive_duration(self):
        for field,value in [('assessment',{'prompt':'Guess','success_criteria':[]}),('minutes',0)]:
            bad=self.course(); bad['modules'][0][field]=value
            self.assertNotEqual(self.check_course(bad).returncode,0,field)


if __name__ == '__main__':
    unittest.main()
