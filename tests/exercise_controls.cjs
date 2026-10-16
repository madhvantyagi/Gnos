// Execute the real browser controller against a small DOM/API boundary.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(process.argv[2], 'utf8');

async function check(attempt, expected, checkFocus = false) {
  let onInput;
  let onFocus;
  const field = {value: '', disabled: false};
  const status = {textContent: ''};
  const reveal = {disabled: true};
  const solution = {hidden: true};
  const historyBody = {replaceChildren() {}, appendChild() {}};
  const history = {hidden: true, querySelector() {return historyBody;}};
  const card = {
    dataset: {courseId: 'course', exerciseId: 'sign', responseType: 'numeric'},
    querySelector(selector) {
      if (selector === '.exercise-status') return status;
      if (selector === '.reveal-answer') return reveal;
      if (selector === '.exercise-solution') return solution;
      if (selector === '.exercise-history') return history;
      if (selector === '.exercise-form') return {addEventListener(event, handler) {onInput = handler;}};
      if (selector.startsWith('textarea[name="answer"]')) return field;
      return null;
    },
    querySelectorAll() {return [field];}
  };
  const document = {
    readyState: 'complete', addEventListener() {},
    querySelector(selector) {
      if (selector === 'meta[name="gnos-session"]') return {content: 'test'};
      return null;
    },
    querySelectorAll() {return [card];},
    createElement() {return {textContent: '', appendChild() {}};}
  };
  const context = {document, window: {addEventListener(event, handler) {onFocus = handler;}}, console, setTimeout, clearTimeout,
    localStorage: {getItem() {return checkFocus ? JSON.stringify({answer: 'Old browser draft'}) : null;}},
    fetch: async () => ({ok: true, json: async () => ({attempt, history: [], solution_available: true})})};
  vm.runInNewContext(source, context);
  await new Promise(resolve => setImmediate(resolve));
  assert.match(status.textContent, expected);
  assert.equal(field.value, attempt.response.value);
  assert.equal(reveal.disabled, false);
  if (checkFocus) {
    field.value = 'Unsaved new reasoning';
    onInput();
    onFocus();
    await new Promise(resolve => setImmediate(resolve));
    assert.equal(field.value, 'Unsaved new reasoning');
    assert.equal(status.textContent, 'Unsaved changes.');
    assert.equal(reveal.disabled, true);
  }
}

(async () => {
  const base = {id: 'attempt-one', response: {value: 1}};
  await check({...base, status: 'checked', feedback: 'Correct.'}, /Saved.*Correct/);
  await check({...base, status: 'checked', feedback: 'Not yet; try again.'}, /Not yet/);
  await check({...base, status: 'awaiting-review'}, /Awaiting GNOS review/);
  await check({...base, status: 'awaiting-review'}, /Awaiting GNOS review/, true);
  await check({...base, status: 'reviewed', evidence_recorded: true,
    review: {result: 'partial', help: 'none', interpretation: 'Missing the inner rate.', next_step: 'Compare two rates.'}},
    /Reviewed.*partial.*Missing the inner rate.*Compare two rates/);
  console.log('Exercise save, check, and review feedback passed.');
})().catch(error => {console.error(error); process.exitCode = 1;});
