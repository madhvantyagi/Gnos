(function () {
  "use strict";
  function cardsFor(card) {
    return Array.from(document.querySelectorAll('.card.exercise')).filter(other =>
      other.dataset.courseId === card.dataset.courseId && other.dataset.exerciseId === card.dataset.exerciseId);
  }
  function status(card, message) {
    card.querySelector('.exercise-status').textContent = message;
  }
  function getAnswer(card) {
    const checked = card.querySelector('input[type="radio"]:checked');
    const field = checked || card.querySelector('textarea[name="answer"], input:not([type="radio"])[name="answer"]');
    return field ? field.value : '';
  }
  function setAnswer(card, value) {
    card.querySelectorAll('[name="answer"]').forEach(field => {
      if (field.type === 'radio') field.checked = field.value === String(value);
      else field.value = value;
    });
  }
  function key(card) {
    return 'gnos:exercise:' + card.dataset.courseId + ':' + card.dataset.exerciseId;
  }
  async function api(card, suffix = '', payload) {
    const meta = document.querySelector('meta[name="gnos-session"]');
    if (!meta) throw new Error('Open this course through its local GNOS viewer to save answers.');
    const response = await fetch('/api/exercises/' + encodeURIComponent(card.dataset.exerciseId) + suffix, {
      method: payload === undefined ? 'GET' : 'POST',
      headers: {'Content-Type': 'application/json', 'X-GNOS-Session': meta.content},
      body: payload === undefined ? undefined : JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'The request did not complete.');
    return data;
  }
  function saved(card, attempt, restoring = false) {
    cardsFor(card).forEach(other => {
      if (restoring && other.dataset.edited) return;
      setAnswer(other, attempt.response.text ?? attempt.response.value);
      other.dataset.attemptId = attempt.id;
      delete other.dataset.pendingId;
      delete other.dataset.edited;
      other.querySelector('.exercise-solution').hidden = true;
      other.querySelector('.reveal-answer').disabled = false;
      status(other, 'Saved. Your response is stored with this course.');
    });
  }
  async function restore(card) {
    // Preserve answers from the earlier browser-only viewer as unsaved drafts.
    try {
      const old = JSON.parse(localStorage.getItem(key(card)) || 'null');
      if (old && typeof old.answer === 'string') {
        setAnswer(card, old.answer);
        status(card, 'Restored a browser draft. Save it to record it with this course.');
      }
    } catch (_) { /* A browser draft is optional; server persistence is authoritative. */ }
    try {
      const data = await api(card);
      if (data.attempt) saved(card, data.attempt, true);
    } catch (error) {
      status(card, error.message);
    }
  }
  function edited(card) {
    card.dataset.edited = '1';
    delete card.dataset.attemptId;
    delete card.dataset.pendingId;
    card.querySelector('.reveal-answer').disabled = true;
    card.querySelector('.exercise-solution').hidden = true;
    status(card, 'Unsaved changes.');
  }
  async function submit(event) {
    const form = event.target.closest('.exercise-form');
    if (!form) return;
    event.preventDefault();
    const card = form.closest('.card.exercise');
    const answer = getAnswer(card);
    const type = card.dataset.responseType;
    if (!answer.trim()) { status(card, 'Enter or choose an answer before saving.'); return; }
    let response;
    if (type === 'numeric') {
      const value = Number(answer);
      if (!Number.isFinite(value)) { status(card, 'Enter a finite number.'); return; }
      response = {value};
    } else if (type === 'multiple-choice') response = {value: answer};
    else response = {text: answer.trim()};
    const button = form.querySelector('[type="submit"]');
    const fields = form.querySelectorAll('[name="answer"]');
    button.disabled = true;
    fields.forEach(field => { field.disabled = true; });
    card.querySelector('.reveal-answer').disabled = true;
    card.querySelector('.exercise-solution').hidden = true;
    status(card, 'Saving…');
    // Reuse this ID after a lost response; editing starts a new attempt.
    card.dataset.pendingId ||= 'attempt-' + crypto.randomUUID();
    try {
      const attempt = await api(card, '/attempts', {response, attempt_id: card.dataset.pendingId});
      saved(card, attempt);
      try { localStorage.removeItem(key(card)); } catch (_) { /* Optional draft cleanup. */ }
    } catch (error) {
      status(card, 'Not saved. ' + error.message);
    } finally {
      button.disabled = false;
      fields.forEach(field => { field.disabled = false; });
    }
  }
  async function reveal(event) {
    const button = event.target.closest('.reveal-answer');
    if (!button || button.disabled) return;
    const card = button.closest('.card.exercise');
    button.disabled = true;
    try {
      const result = await api(card, '/reveal', {attempt_id: card.dataset.attemptId});
      const area = card.querySelector('.exercise-solution');
      // The server returns escaped lesson prose with only renderer-owned math markup.
      area.innerHTML = '<h4>Worked answer</h4>' + result.html;
      area.hidden = false;
      if (window.renderMathInElement) window.renderMathInElement(area, {
        delimiters: [{left:'$$',right:'$$',display:true},{left:'\\[',right:'\\]',display:true},
                     {left:'\\(',right:'\\)',display:false},{left:'$',right:'$',display:false}],
        throwOnError: false
      });
      status(card, 'Answer shown. Your saved response is unchanged.');
    } catch (error) { status(card, error.message); }
    finally { button.disabled = false; }
  }
  function init() {
    const cards = document.querySelectorAll('.card.exercise');
    cards.forEach(card => {
      restore(card);
      card.querySelector('.exercise-form').addEventListener('input', () => edited(card));
    });
    document.addEventListener('submit', submit);
    document.addEventListener('click', reveal);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
