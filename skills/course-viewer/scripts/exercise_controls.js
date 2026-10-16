(function () {
  "use strict";
  // The reference template also supports an older browser-only demo.
  // Claim its ownership hook before that fallback installs another save handler.
  if (document.documentElement) document.documentElement.setAttribute('data-gnos-exercises', '1');
  const groups = new Map();
  function key(card) { return card.dataset.courseId + ':' + card.dataset.exerciseId; }
  function status(group, message) {
    group.cards.forEach(card => {
      const area = card.querySelector('.exercise-status');
      area.textContent = message;
      if (window.gnosRenderMath) window.gnosRenderMath(area);
    });
  }
  function answer(card) {
    const field = card.querySelector('input[type="radio"]:checked') ||
      card.querySelector('textarea[name="answer"], input:not([type="radio"])[name="answer"]');
    return field ? field.value : '';
  }
  function setAnswer(group, value) {
    group.cards.forEach(card => card.querySelectorAll('[name="answer"]').forEach(field => {
      if (field.type === 'radio') field.checked = field.value === String(value);
      else field.value = value;
    }));
  }
  async function request(path, payload) {
    const meta = document.querySelector('meta[name="gnos-session"]');
    if (!meta) throw new Error('Open this course through its local GNOS viewer to save work.');
    const response = await fetch(path, {
      method: payload === undefined ? 'GET' : 'POST',
      headers: {'Content-Type': 'application/json', 'X-GNOS-Session': meta.content},
      body: payload === undefined ? undefined : JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'The request did not complete.');
    return data;
  }
  function api(group, suffix = '', payload) {
    return request('/api/exercises/' + encodeURIComponent(group.cards[0].dataset.exerciseId) + suffix, payload);
  }
  function versions(group) {
    const card = group.cards[0];
    return {exercise_fingerprint: card.dataset.exerciseFingerprint, lesson_fingerprint: card.dataset.lessonFingerprint};
  }
  function controls(group) {
    group.cards.forEach(card => {
      card.querySelector('.reveal-answer').disabled = group.busy || group.editing || !group.attempt || !group.solutionAvailable;
      const feedback = card.querySelector('.request-feedback');
      if (feedback) feedback.disabled = group.busy || !group.attempt;
    });
  }
  function saved(group, attempt) {
    group.attempt = attempt;
    group.baseAttemptId = attempt.id;
    setAnswer(group, attempt.response.text ?? attempt.response.value);
    group.dirty = false;
    group.editing = false;
    group.pendingId = null;
    let message = 'Saved. ';
    if (attempt.status === 'reviewed' && attempt.review) {
      const review = attempt.review;
      message += 'Reviewed: ' + review.result + '. ' + review.interpretation + ' Next: ' + review.next_step;
      if (review.help !== 'none') message += ' This was assisted practice.';
      if (!attempt.evidence_recorded) message += ' Progress recording is pending.';
    } else if (attempt.status === 'checked') {
      message += (attempt.feedback || 'Checked.') + ' GNOS will review this before continuing.';
    } else message += 'Awaiting GNOS review. Ask GNOS to review this lesson when you are ready.';
    status(group, message);
    controls(group);
  }
  function history(group, attempts) {
    group.cards.forEach(card => {
      const area = card.querySelector('.exercise-history');
      if (!area) return;
      const body = area.querySelector('div');
      body.replaceChildren();
      area.hidden = !attempts.length;
      attempts.forEach(attempt => {
        const item = document.createElement('p');
        const response = attempt.response || {}, review = attempt.review || {};
        item.textContent = (attempt.submitted_at || '') + ' · ' + (review.result || attempt.status) +
          '\n' + (attempt.prompt || '') + '\nYour answer: ' + (response.text ?? response.value ?? '') +
          (review.interpretation ? '\n' + review.interpretation + ' Next: ' + review.next_step : '');
        body.appendChild(item);
      });
      if (window.gnosRenderMath) window.gnosRenderMath(body);
    });
  }
  async function restore(group) {
    const generation = group.generation;
    const epoch = group.epoch;
    const refresh = ++group.refresh;
    try {
      const data = await api(group);
      history(group, data.history || []);
      const current = versions(group);
      group.stale = (current.exercise_fingerprint && data.exercise_fingerprint !== current.exercise_fingerprint) ||
        (current.lesson_fingerprint && data.lesson_fingerprint !== current.lesson_fingerprint);
      group.solutionAvailable = data.solution_available === true;
      if (group.stale) {
        status(group, 'This lesson changed. Copy unfinished work, ask GNOS to re-render it, then reload before saving.');
        return;
      }
      // Initial metadata may arrive after typing starts. Adopt its revision,
      // while keeping newer text; a later refresh must never rebase a local edit.
      if (!group.initialized && epoch === group.epoch && refresh === group.refresh && !group.saving) {
        group.revision = data.draft_revision || 0;
        group.attempt = data.attempt || null;
        group.baseAttemptId = data.draft ? data.draft.base_attempt_id : (data.attempt ? data.attempt.id : null);
        group.initialized = true;
      }
      if (generation !== group.generation || epoch !== group.epoch || refresh !== group.refresh || group.dirty || group.saving) return;
      group.revision = data.draft_revision || 0;
      if (data.draft) {
        group.editing = true;
        group.attempt = data.attempt || null;
        group.baseAttemptId = data.draft.base_attempt_id || null;
        setAnswer(group, data.draft.response.text ?? data.draft.response.value);
        status(group, 'Draft saved. Submit your answer when ready.');
      } else if (data.attempt) saved(group, data.attempt);
      else if (data.stale_draft) status(group, 'An older lesson draft is preserved on the server. Ask GNOS to recover it before replacing it.');
      else {
        try {
          const old = JSON.parse(localStorage.getItem('gnos:exercise:' + key(group.cards[0])) || 'null');
          if (old && typeof old.answer === 'string') {
            setAnswer(group, old.answer); group.dirty = true; group.editing = true;
            status(group, 'Restored a browser draft. Edit or save it to preserve it with this course.');
          }
        } catch (_) { /* Legacy import is optional. */ }
      }
    } catch (error) { status(group, 'Could not refresh saved work. ' + error.message); }
    finally { controls(group); }
  }
  function draftResponse(group) {
    const card = group.cards[0], value = answer(card);
    return ['numeric', 'multiple-choice'].includes(card.dataset.responseType) ? {value} : {text: value};
  }
  async function persist(group) {
    if (!group.dirty) return;
    if (group.stale) throw new Error('Reload the changed lesson before saving. Copy your current text first.');
    const generation = group.generation;
    group.epoch += 1;
    group.saving = true;
    try {
      const draft = await api(group, '/draft', {...versions(group), response: draftResponse(group),
        revision: group.revision, base_attempt_id: group.baseAttemptId});
      group.revision = draft.revision;
      if (generation === group.generation) {
        group.dirty = false; status(group, 'Draft saved. Submit your answer when ready.');
      }
    } finally { group.saving = false; }
  }
  function autosave(group) {
    group.tail = group.tail.then(() => group.ready).then(() => persist(group)).catch(error => {
      status(group, 'Draft not saved. Your text remains on this page. ' + error.message);
    });
    return group.tail;
  }
  function edited(group, card) {
    setAnswer(group, answer(card));
    group.generation += 1; group.dirty = true; group.editing = true; group.pendingId = null;
    group.cards.forEach(other => { other.querySelector('.exercise-solution').hidden = true; });
    controls(group); status(group, 'Unsaved changes.');
    clearTimeout(group.timer);
    group.timer = setTimeout(() => autosave(group), 400);
  }
  async function submit(event) {
    const form = event.target.closest('.exercise-form');
    if (!form) return;
    event.preventDefault();
    const group = groups.get(key(form.closest('.card.exercise')));
    if (group.busy) return;
    const value = answer(group.cards[0]), type = group.cards[0].dataset.responseType;
    if (!value.trim()) { status(group, 'Enter or choose an answer before saving.'); return; }
    let response = draftResponse(group);
    if (type === 'numeric') {
      if (!Number.isFinite(Number(value))) { status(group, 'Enter a finite number. Your draft is preserved.'); return; }
      response = {value: Number(value)};
    } else if (type !== 'multiple-choice') response = {text: value.trim()};
    clearTimeout(group.timer); group.busy = true;
    group.cards.forEach(card => card.querySelectorAll('[name="answer"], [type="submit"]').forEach(field => { field.disabled = true; }));
    controls(group);
    try {
      await group.ready; await group.tail; await persist(group);
      group.epoch += 1;
      group.pendingId ||= 'attempt-' + crypto.randomUUID();
      status(group, 'Saving…');
      const attempt = await api(group, '/attempts', {...versions(group), response,
        attempt_id: group.pendingId, draft_revision: group.revision});
      saved(group, attempt);
      try { localStorage.removeItem('gnos:exercise:' + key(group.cards[0])); } catch (_) { /* Legacy cleanup. */ }
      await restore(group); refreshCourseReview();
    } catch (error) { status(group, 'Not saved. Your text remains on this page. ' + error.message); }
    finally {
      group.busy = false;
      group.cards.forEach(card => card.querySelectorAll('[name="answer"], [type="submit"]').forEach(field => { field.disabled = false; }));
      controls(group);
    }
  }
  async function refreshCourseReview() {
    const area = document.querySelector('.course-review-status');
    if (!area || !document.querySelector('meta[name="gnos-session"]')) return;
    try {
      const result = await request('/api/review');
      const labels = {'advance': 'Ready to continue.', 'practice': 'More practice needed.',
        'repair-prerequisite': 'A prerequisite needs attention.', 'skip': 'Continuing by your request.',
        'review-required': 'Lesson review needed.'};
      area.textContent = (labels[result.decision] || 'Lesson review needed.') + ' ' +
        (result.reason ? result.reason + ' ' : '') + result.next_step;
      if (window.gnosRenderMath) window.gnosRenderMath(area);
    } catch (error) { area.textContent = 'Lesson review unavailable. ' + error.message; }
  }
  async function refreshQuestions() {
    const area = document.querySelector('.course-questions');
    if (!area || !document.querySelector('meta[name="gnos-session"]')) return;
    try {
      const data = await request('/api/questions');
      area.replaceChildren();
      const heading = document.createElement('h2');
      heading.textContent = 'Questions'; heading.className = 'sec'; area.appendChild(heading);
      data.questions.forEach(question => {
        const card = document.createElement('div'); card.className = 'card';
        const text = document.createElement('p'); text.textContent = question.text;
        const state = document.createElement('p'); state.textContent = 'Status: ' + question.status;
        card.appendChild(text); card.appendChild(state);
        if (question.answer) { const answer = document.createElement('p'); answer.textContent = question.answer; card.appendChild(answer); }
        area.appendChild(card);
      });
      if (window.gnosRenderMath) window.gnosRenderMath(area);
    } catch (_) { /* Existing rendered questions remain readable after a refresh failure. */ }
  }
  async function click(event) {
    const button = event.target.closest('.reveal-answer, .request-feedback, .send-feedback, .copy-feedback');
    if (!button || button.disabled) return;
    const card = button.closest('.card.exercise'), group = groups.get(key(card));
    if (button.classList.contains('request-feedback')) {
      card.querySelector('.feedback-request').hidden = false;
      card.querySelector('.feedback-status').textContent = 'Saved response (' + group.attempt.id + '): ' +
        (group.attempt.response.text ?? group.attempt.response.value);
      card.querySelector('.feedback-text').focus(); return;
    }
    if (button.classList.contains('reveal-answer')) {
      button.disabled = true;
      try {
        const result = await api(group, '/reveal', {attempt_id: group.attempt.id});
        const area = card.querySelector('.exercise-solution');
        area.innerHTML = '<h4>Worked answer</h4>' + result.html; area.hidden = false;
        if (window.gnosRenderMath) window.gnosRenderMath(area);
        status(group, 'Answer shown. Your saved response is unchanged.');
      } catch (error) { status(group, error.message); }
      finally { controls(group); }
      return;
    }
    const field = card.querySelector('.feedback-text'), area = card.querySelector('.feedback-status');
    const text = field.value.trim();
    if (!group.attempt || !text) { area.textContent = 'Save an answer and enter a question first.'; return; }
    const context = {course_id: card.dataset.courseId, exercise_id: card.dataset.exerciseId, attempt_id: group.attempt.id};
    if (button.classList.contains('copy-feedback')) {
      const message = text + '\nCourse: ' + context.course_id + '\nExercise: ' + context.exercise_id + '\nAttempt: ' + context.attempt_id +
        '\nSaved response: ' + (group.attempt.response.text ?? group.attempt.response.value);
      try { await navigator.clipboard.writeText(message); area.textContent = 'Copied. Paste this request into the teaching chat.'; }
      catch (_) { field.value = message; field.focus(); field.select(); area.textContent = 'Select and copy this request into the teaching chat.'; }
      return;
    }
    const signature = JSON.stringify({text, context});
    if (group.questionSignature !== signature) { group.questionSignature = signature; group.questionId = 'question-' + crypto.randomUUID(); }
    button.disabled = true;
    try {
      await request('/api/questions', {question_id: group.questionId, text, context});
      area.textContent = 'Pending GNOS review. Copy the request into the teaching chat when ready.'; refreshQuestions();
    } catch (error) { area.textContent = 'Request not saved. ' + error.message; }
    finally { button.disabled = false; }
  }
  function init() {
    document.querySelectorAll('.card.exercise').forEach(card => {
      const id = key(card);
      if (!groups.has(id)) groups.set(id, {cards: [], generation: 0, revision: 0, dirty: false, editing: false, epoch: 0, refresh: 0,
        busy: false, saving: false, initialized: false, tail: Promise.resolve(), attempt: null, baseAttemptId: null});
      const group = groups.get(id); group.cards.push(card);
      card.querySelector('.exercise-form').addEventListener('input', () => edited(group, card));
    });
    groups.forEach(group => { group.ready = restore(group); });
    document.addEventListener('submit', submit); document.addEventListener('click', click);
    refreshCourseReview(); refreshQuestions();
    window.addEventListener('focus', () => {
      groups.forEach(group => { if (!group.busy && !group.saving) restore(group); });
      refreshCourseReview(); refreshQuestions();
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
