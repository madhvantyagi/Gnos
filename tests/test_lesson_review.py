"""Review, repair, and continuation over real temporary learner workspaces."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

from tests import test_portal_interactions as interactions
from course_workspace import publish_lesson, read_plan
from portal_interactions import read_attempt, review_attempt, submit_attempt
from manage_interaction import record_reviewed_attempt


class LessonReviewTests(unittest.TestCase):
    def test_reverse_review_order_preserves_submission_chronology_and_source(self):
        from lesson_review import build_review_context
        from learner_state import read_state, summarize
        older = submit_attempt(self.workspace, 'predict-change', {'value': 1})
        newer = submit_attempt(self.workspace, 'predict-change', {'value': 0})
        self.review(newer, 'incorrect')
        self.review(older)
        state = read_state(self.fixture.root, 'alex')
        self.assertEqual(state['events'][0]['occurred_at'], newer['submitted_at'])
        self.assertEqual(state['events'][0]['source']['attempt_id'], newer['id'])
        context = build_review_context(self.workspace)
        self.assertEqual(context['concept_evidence']['math.derivative']['status'], 'practicing')
        summary = summarize(state, 'gradient-descent', self.fixture.root, 'alex')
        self.assertEqual(summary['concepts']['math.derivative']['status'], 'practicing')
        self.assertEqual(summary['course_progress']['concepts']['math.derivative']['status'], 'practicing')

    def test_legacy_portal_order_is_recovered_only_from_matching_saved_work(self):
        from lesson_review import build_review_context
        from learner_state import read_state, save_state, state_path
        older = submit_attempt(self.workspace, 'predict-change', {'value': 1})
        newer = submit_attempt(self.workspace, 'predict-change', {'value': 0})
        self.review(newer, 'incorrect')
        self.review(older)
        state = read_state(self.fixture.root, 'alex')
        for event in state['events']:
            event.pop('occurred_at', None)
            event.pop('source', None)
        save_state(state_path(self.fixture.root, 'alex'), state)
        context = build_review_context(self.workspace)
        self.assertEqual(context['concept_evidence']['math.derivative']['status'], 'practicing')
        self.assertFalse(any(a['needs_review'] for a in context['attempts']))
        self.assertNotIn('occurred_at', read_state(self.fixture.root, 'alex')['events'][0])
        record_reviewed_attempt(self.fixture.root, 'alex', 'gradient-descent', older['id'],
                                read_attempt(self.workspace, older['id'])['review'])
        self.assertNotIn('occurred_at', read_state(self.fixture.root, 'alex')['events'][0])

    def test_interrupted_legacy_link_retry_refreshes_memory_after_recovering_chronology(self):
        from learner_state import read_state, save_state, state_path, summarize
        older = submit_attempt(self.workspace, 'predict-change', {'value': 0})
        newer = submit_attempt(self.workspace, 'predict-change', {'value': 1})
        self.review(newer)
        self.review(older, 'incorrect')
        state = read_state(self.fixture.root, 'alex')
        for event in state['events']:
            event.pop('occurred_at', None)
            event.pop('source', None)
        save_state(state_path(self.fixture.root, 'alex'), state)
        old_path = self.workspace / 'submissions/predict-change' / (older['id'] + '.json')
        unlinked = read_attempt(self.workspace, older['id'])
        unlinked['evidence_event_id'] = None
        old_path.write_text(json.dumps(unlinked))

        record_reviewed_attempt(self.fixture.root, 'alex', 'gradient-descent', older['id'], unlinked['review'])

        self.assertEqual(read_attempt(self.workspace, older['id'])['evidence_event_id'], 'portal-' + older['id'])
        summary = summarize(read_state(self.fixture.root, 'alex'), 'gradient-descent', self.fixture.root, 'alex')
        self.assertEqual(summary['concepts']['math.derivative']['status'], 'demonstrated')
        topic_memory = (self.fixture.root / 'alex/memory/03-topics.md').read_text()
        self.assertIn('`math.derivative`: demonstrated;', topic_memory)
        curriculum = (self.fixture.root / 'alex/memory/courses/gradient-descent/CURRICULUM.md').read_text()
        self.assertIn('latest attempt', curriculum)
        self.assertIn('correct, help=none', curriculum)

    def test_reused_event_id_with_conflicting_content_requires_review(self):
        from lesson_review import build_review_context, record_lesson_review
        from learner_state import read_state, mutate
        attempt = submit_attempt(self.workspace, 'predict-change', {'value': 1})
        self.review(attempt)
        original = copy.deepcopy(read_state(self.fixture.root, 'alex')['events'][0])
        for field, value in [('response', 'Different work.'), ('result', 'partial'),
                             ('help', 'hint'), ('task', 'A different question.'),
                             ('interpretation', 'A different interpretation.'),
                             ('source_hash', '0' * 64)]:
            with self.subTest(field=field):
                mutate(self.fixture.root, 'alex', 'retract', original['id'])
                event = copy.deepcopy(original)
                if field == 'source_hash':
                    event['source']['exercise_fingerprint'] = value
                elif field == 'interpretation':
                    event[field] = value
                else:
                    event['attempts'][0][field] = value
                mutate(self.fixture.root, 'alex', 'record', event)
                context = build_review_context(self.workspace)
                self.assertTrue(context['attempts'][0]['needs_review'])
                with self.assertRaises(ValueError):
                    record_lesson_review(self.workspace, self.decision(context))

    def test_declared_criterion_needs_explicit_evidence_and_allows_real_chat_work(self):
        from lesson_review import build_review_context, record_lesson_review
        from learner_state import mutate
        plan = read_plan(self.workspace)
        plan['revision'] += 1
        plan['revision_notes'].append(dict(revision=plan['revision'], date='2026-09-13', reason='Declare reasoning evidence.'))
        plan['chapters'][0]['topics'][0]['assessment'] = dict(prompt='Explain slope.', success_criteria=['Explain the relationship.'],
            criteria=[dict(id='justify-change', description='Justify why the sign predicts the change.', concepts=['math.derivative'])])
        mutate(self.fixture.root, 'alex', 'enroll', plan)
        lesson = interactions.open_lesson(plan)
        publish_lesson(self.workspace, lesson)
        attempt = submit_attempt(self.workspace, 'predict-change', {'value': 1})
        self.review(attempt)
        context = build_review_context(self.workspace)
        with self.assertRaisesRegex(ValueError, 'criterion'):
            record_lesson_review(self.workspace, self.decision(context))
        event = dict(id='chat-reasoning', date='2026-09-13', course_id='gradient-descent', covered=['math.derivative'],
            attempts=[dict(concept='math.derivative', task='Explain why a positive slope predicts an increase.', response='For positive small dx, dy is approximately slope times dx, hence positive.', result='correct', help='none', kind='transfer')],
            interpretation='Reasoning connects the factors and their signs.', next_step='Try a negative slope.')
        mutate(self.fixture.root, 'alex', 'record', event)
        context = build_review_context(self.workspace)
        payload = self.decision(context)
        payload['criterion_reviews'] = [dict(criterion_id='justify-change', attempt_ids=[], event_ids=['chat-reasoning'], explanation='The response uses the local-change approximation and justifies its sign.')]
        receipt = record_lesson_review(self.workspace, payload)
        self.assertEqual(receipt['decision'], 'advance')
        self.assertEqual(build_review_context(self.workspace)['assessment_review']['unsupported_criterion_ids'], [])

    def setUp(self):
        self.fixture = interactions.PortalInteractionTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)
        self.workspace = self.fixture.workspace

    def review(self, attempt, result='correct', help_='none'):
        review = dict(result=result, help=help_, kind='application',
                      interpretation='Sign follows slope.', next_step='Try changed conditions.')
        review_attempt(self.workspace, attempt['id'], review)
        record_reviewed_attempt(self.fixture.root, 'alex', 'gradient-descent', attempt['id'], review)

    def decision(self, context, decision='advance', repairs=None):
        return dict(lesson_id='slope-introduction', context_fingerprint=context['context_fingerprint'],
                    decision=decision, reason='Reviewed the reasoning and teaching.',
                    next_step='Move to the changed case.',
                    reviewed_attempt_ids=[a['id'] for a in context['attempts'] if not a['needs_review']],
                    repairs=repairs or [])

    def test_resume_packet_includes_current_lesson_original_rubric_and_pending_work(self):
        from lesson_review import build_review_context
        attempt = submit_attempt(self.workspace, 'predict-change', {'value': 0})
        context = build_review_context(self.workspace)
        self.assertEqual(context['lessons'][0]['id'], 'slope-introduction')
        self.assertEqual(context['attempts'][0]['assessment_context']['exercise']['evaluation']['answer'], 1)
        self.assertTrue(context['attempts'][0]['needs_review'])
        loader = Path(__file__).resolve().parents[1] / 'skills/learning-orchestrator/scripts/assemble_context.py'
        result = subprocess.run([sys.executable, str(loader), '--subject', 'math', '--learner', 'alex',
            '--learners-root', str(self.fixture.root), '--course-id', 'gradient-descent'],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('LESSON REVIEW DATA', result.stdout)
        self.assertIn(attempt['id'], result.stdout)
        self.assertIn('success_criteria', result.stdout)

    def test_advance_requires_reviewed_work_and_independent_evidence(self):
        from lesson_review import build_review_context, record_lesson_review
        attempt = submit_attempt(self.workspace, 'predict-change', {'value': 0})
        context = build_review_context(self.workspace)
        with self.assertRaisesRegex(ValueError, '[Rr]eview'):
            record_lesson_review(self.workspace, self.decision(context))
        self.review(attempt, 'incorrect')
        context = build_review_context(self.workspace)
        with self.assertRaisesRegex(ValueError, 'independent'):
            record_lesson_review(self.workspace, self.decision(context))
        receipt = record_lesson_review(self.workspace, self.decision(context, 'practice'))
        self.assertEqual(receipt['decision'], 'practice')
        self.assertEqual(build_review_context(self.workspace)['continuation']['decision'], 'practice')

    def test_new_answer_and_lesson_edit_invalidate_previous_continuation(self):
        from lesson_review import build_review_context, record_lesson_review
        attempt = submit_attempt(self.workspace, 'predict-change', {'value': 1})
        self.review(attempt)
        context = build_review_context(self.workspace)
        record_lesson_review(self.workspace, self.decision(context))
        self.assertEqual(build_review_context(self.workspace)['continuation']['decision'], 'advance')
        lesson = interactions.open_lesson(read_plan(self.workspace))
        lesson['blocks'][0]['text'] += ' Compare equal heights with different slopes.'
        publish_lesson(self.workspace, interactions.reviewed_lesson(lesson))
        self.assertEqual(build_review_context(self.workspace)['continuation']['decision'], 'review-required')
        with self.assertRaisesRegex(ValueError, 'changed'):
            record_lesson_review(self.workspace, self.decision(context))
        context = build_review_context(self.workspace)
        with self.assertRaisesRegex(ValueError, 'independent'):
            record_lesson_review(self.workspace, self.decision(context))
        fresh = submit_attempt(self.workspace, 'predict-change', {'value': 1})
        self.review(fresh)
        context = build_review_context(self.workspace)
        record_lesson_review(self.workspace, self.decision(context))
        submit_attempt(self.workspace, 'explain-gradient', {'text': 'New uncertainty.'})
        self.assertEqual(build_review_context(self.workspace)['continuation']['decision'], 'review-required')

    def test_skip_preserves_unreviewed_work_and_requires_explicit_learner_request(self):
        from lesson_review import build_review_context, record_lesson_review
        submit_attempt(self.workspace, 'predict-change', {'value': 0})
        context = build_review_context(self.workspace)
        payload = self.decision(context, 'skip')
        with self.assertRaisesRegex(ValueError, 'learner_override'):
            record_lesson_review(self.workspace, payload)
        payload['learner_override'] = 'The learner explicitly asked to skip this check.'
        record_lesson_review(self.workspace, payload)
        self.assertTrue(build_review_context(self.workspace)['attempts'][0]['needs_review'])

    def test_malformed_saved_skip_receipt_is_not_a_continuation_authorization(self):
        from lesson_review import build_review_context, require_continuation
        context = build_review_context(self.workspace)
        root = self.workspace / 'lesson-reviews'
        root.mkdir()
        (root / 'bad-receipt.json').write_text(json.dumps(dict(
            id='fake', context_fingerprint=context['context_fingerprint'],
            decision='skip', reason='Skip.', next_step='Continue.')))
        self.assertEqual(build_review_context(self.workspace)['continuation']['decision'], 'review-required')
        with self.assertRaisesRegex(ValueError, 'continuation'):
            require_continuation(self.workspace)

    def test_invalid_receipt_metadata_can_be_recovered_by_retry(self):
        from lesson_review import build_review_context, record_lesson_review
        attempt = submit_attempt(self.workspace, 'predict-change', {'value': 1})
        self.review(attempt)
        payload = self.decision(build_review_context(self.workspace))
        saved = record_lesson_review(self.workspace, payload)
        path = self.workspace / 'lesson-reviews' / (saved['id'] + '.json')
        for bad in ('invalid', 0):
            with self.subTest(timestamp=bad):
                path.write_text(json.dumps(dict(saved, created_at=bad)))
                # Remove the recovery receipt between cases to test the bad record alone.
                for other in path.parent.glob('*.json'):
                    if other != path:
                        other.unlink()
                self.assertEqual(build_review_context(self.workspace)['continuation']['decision'], 'review-required')
                recovered = record_lesson_review(self.workspace, payload)
                self.assertNotEqual(saved['id'], recovered['id'])
                self.assertEqual(build_review_context(self.workspace)['continuation']['decision'], 'advance')

    def test_corrupt_receipt_can_be_recovered_without_authorizing_continuation(self):
        from lesson_review import build_review_context, record_lesson_review
        attempt = submit_attempt(self.workspace, 'predict-change', {'value': 1})
        self.review(attempt)
        payload = self.decision(build_review_context(self.workspace))
        root = self.workspace / 'lesson-reviews'
        root.mkdir()
        (root / 'corrupt.json').write_text('{unfinished')
        self.assertEqual(build_review_context(self.workspace)['continuation']['decision'], 'review-required')
        record_lesson_review(self.workspace, payload)
        self.assertEqual(build_review_context(self.workspace)['continuation']['decision'], 'advance')

    def test_explicit_skip_without_an_authored_lesson_is_topic_scoped(self):
        from lesson_review import build_review_context, record_lesson_review
        (self.workspace / 'lessons/slope-introduction/lesson.json').unlink()
        payload = self.decision(build_review_context(self.workspace), 'skip')
        payload['lesson_id'] = None
        payload['learner_override'] = 'The learner asked to skip this unfinished topic.'
        saved = record_lesson_review(self.workspace, payload)
        self.assertIsNone(saved['lesson_fingerprint'])
        self.assertEqual(build_review_context(self.workspace)['continuation']['decision'], 'skip')

    def test_repair_requires_changed_teaching_and_fresh_independent_verification(self):
        from lesson_review import build_review_context, record_lesson_review
        wrong = submit_attempt(self.workspace, 'predict-change', {'value': 0})
        self.review(wrong, 'incorrect')
        repair = dict(attempt_ids=[wrong['id']], block_ids=['intro'],
                      diagnosis='Confuses height with slope.', change='Added a two-curve contrast.',
                      verification_attempt_ids=[])
        with self.assertRaisesRegex(ValueError, 'changed'):
            record_lesson_review(self.workspace, self.decision(build_review_context(self.workspace), 'practice', [repair]))
        lesson = interactions.open_lesson(read_plan(self.workspace))
        lesson['blocks'][0]['text'] += ' Compare height with the local rate of change.'
        lesson['exercises'][0]['prompt'] = 'Predict the sign at a different point.'
        publish_lesson(self.workspace, interactions.reviewed_lesson(lesson))
        correct = submit_attempt(self.workspace, 'predict-change', {'value': 1})
        self.review(correct)
        with self.assertRaisesRegex(ValueError, 'verification'):
            record_lesson_review(self.workspace, self.decision(build_review_context(self.workspace), repairs=[repair]))
        repair['verification_attempt_ids'] = [correct['id']]
        receipt = record_lesson_review(self.workspace, self.decision(build_review_context(self.workspace), repairs=[repair]))
        self.assertEqual(receipt['repairs'][0]['attempt_ids'], [wrong['id']])
        self.assertEqual(build_review_context(self.workspace)['continuation']['decision'], 'advance')

    def test_legacy_attempts_are_labeled_and_private_snapshot_is_not_public(self):
        from lesson_review import build_review_context
        from portal_views import build_portal_view
        attempt = submit_attempt(self.workspace, 'predict-change', {'value': 0})
        path = self.workspace / 'submissions/predict-change' / (attempt['id'] + '.json')
        record = read_attempt(self.workspace, attempt['id'])
        del record['exercise_snapshot']
        path.write_text(json.dumps(record))
        context = build_review_context(self.workspace)
        self.assertEqual(context['attempts'][0]['assessment_context']['snapshot_source'], 'legacy-current-exercise')
        public = json.dumps(build_portal_view(self.workspace, {}))
        self.assertNotIn('success_criteria', public)
        self.assertNotIn('exercise_snapshot', public)

    def test_enrolled_topic_transition_requires_a_current_continuation_receipt(self):
        from lesson_review import build_review_context, record_lesson_review
        from learner_state import mutate
        plan = read_plan(self.workspace)
        next_topic = copy.deepcopy(plan['chapters'][0]['topics'][0])
        next_topic.update(id='transfer', title='Changed cases', state='planned',
                          concepts=['math.transfer'], exercise_ids=[], lesson_ids=[], prerequisites=['local-change'])
        plan['chapters'][0]['topics'].append(next_topic)
        plan['revision'] += 1
        plan['revision_notes'].append(dict(revision=plan['revision'], date='2026-09-12', reason='Add transfer.'))
        mutate(self.fixture.root, 'alex', 'enroll', plan)
        publish_lesson(self.workspace, interactions.open_lesson(plan))
        moved = copy.deepcopy(read_plan(self.workspace))
        moved['current']['topic_id'] = 'transfer'
        moved['chapters'][0]['topics'][0]['state'] = 'planned'
        moved['chapters'][0]['topics'][1]['state'] = 'current'
        moved['revision'] += 1
        moved['revision_notes'].append(dict(revision=moved['revision'], date='2026-09-12', reason='Continue.'))
        with self.assertRaisesRegex(ValueError, 'continuation'):
            mutate(self.fixture.root, 'alex', 'enroll', moved)
        attempt = submit_attempt(self.workspace, 'predict-change', {'value': 1})
        self.review(attempt)
        record_lesson_review(self.workspace, self.decision(build_review_context(self.workspace)))
        mutate(self.fixture.root, 'alex', 'enroll', moved)
        self.assertEqual(read_plan(self.workspace)['current']['topic_id'], 'transfer')


if __name__ == '__main__':
    unittest.main()
