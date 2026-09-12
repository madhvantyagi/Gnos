# Evidence contract

State has `schema_version: 1`, `learner_id`, `profile`, `courses`, and `events`.
The profile contains only user-provided goals/preferences. Each course entry
records enrollment and points to its canonical living plan:

```json
{
  "status": "active",
  "plan_ref": "courses/calculus-for-motion/course.json",
  "plan_revision": 2,
  "plan_fingerprint": "<sha256 of the validated plan>",
  "completion_history": []
}
```

`plan_ref` is learner-relative and must resolve to
`learners/<learner-id>/courses/<course-id>/course.json`. Revision and fingerprint
must match that file. A mismatch is an error requiring an explicit course update
or recovery; never choose one copy silently. Learner state is authoritative for
enrollment and evidence. The workspace course file is authoritative for the
current curriculum.

Each event has these fields:

```json
{
  "id": "2026-09-12-chain-rule-1",
  "date": "2026-09-12",
  "course_id": "calculus-for-motion",
  "covered": ["math.chain-rule"],
  "attempts": [{
    "concept": "math.chain-rule",
    "task": "Differentiate (3x+1)^2 and explain both factors.",
    "response": "2(3x+1); forgot the inner rate.",
    "result": "incorrect",
    "help": "none",
    "kind": "application"
  }],
  "interpretation": "Can apply the outer rule; inner rate needs a concrete comparison.",
  "next_step": "Compare u=3x+1 and y=u^2 before multiplying the two rates."
}
```

This is fictional example data. `result` is `correct`, `partial`, or `incorrect`;
`help` is `none`, `hint`, or `worked-example`; `kind` is `application`, `retrieval`,
or `transfer`. Empty attempts are valid for an untested lesson. Dates are ISO
dates and may not be in the future. Use unique event IDs; identical retries do
nothing, conflicting retries fail. Events are ordered by date, then insertion.

The deterministic summary uses a conservative rule:

- Covered without attempts: **exposed**.
- Latest attempt is assisted, partial, or incorrect: **practicing**.
- Latest attempt is correct without help: **demonstrated**.
- That latest success is retrieval/transfer on a later date than an earlier
  unassisted success: **retained**.

These are workflow labels, not calibrated scores. The summary retains counts
and the latest task so the teacher can judge scope. It never issues “mastered.”
Latest failure can move a concept back to practicing; earlier evidence remains.
Upcoming reviews are teacher/learner decisions captured in `next_step`.

The learner-state file is the source of truth for observations; summaries are
computed, not independently edited. Atomic replacement avoids partial JSON. A
filesystem lock prevents simultaneous writers. A stale lock after a crash must
be inspected before manual removal; the script fails rather than guessing that
a competing writer is dead.

Older records may contain an embedded `plan`. Migrate them explicitly:

```bash
python3 skills/understanding-user-learning/scripts/learner_state.py \
  migrate-courses <learner-id>
```

Migration validates and upgrades the plan, creates its canonical workspace,
then replaces the duplicate with its reference, revision, and fingerprint. It
preserves events, status, completion metadata, and stable IDs. Identical retries
are safe. Do not remove the embedded plan before the workspace write succeeds.
