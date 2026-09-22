# Portal interaction boundary

The portal stores work for the active GNOS conversation; it is not a background
tutor. Browser actions may preserve a draft, submit an attempt, request a hint,
or queue a course-scoped question. They do not directly mark a concept learned,
rewrite the course, invoke Codex, or execute submitted code.

## Exercises

Resolve every exercise ID from a validated ready lesson. Render and accept only
the response shape declared by that exercise. Keep private success criteria and
deterministic answers on the server side.

Use `skills/course-viewer/scripts/serve_course.py` to serve the interactive
page. Save answer calls the existing submission store and writes the response
to `submissions/<exercise-id>/<attempt-id>.json`. Show a saved state only after
that write succeeds. A browser draft alone is not a persisted course attempt.

After saving, offer Show answer. Verify that the attempt belongs to this
exercise, return only its authored `solution` (or the deterministic answer for
older numeric/choice exercises), and record `solution_revealed_at` on the
attempt. Preserve the original response. Later attempts record
`solution_seen_before_submission` so review can account for that assistance.
Never send success criteria, tolerances, or private review notes with a solution.

Drafts are replaceable working state. Submitted attempts are append-only. A
retry receives a new attempt ID and never erases the earlier response. Reusing
an attempt ID with an identical payload is idempotent; reusing it with different
content is an error.

The server may check multiple-choice and numeric responses deterministically.
Short text, long text, and code text remain `awaiting-review` until GNOS reviews
the actual response in an active chat. Code is stored as text and is never run.
Requesting a hint is recorded separately so later review can distinguish
independent work from assisted work. Showing a solution cannot establish
independent success.

An attempt becomes learner evidence only through the explicit reviewed-attempt
bridge. The review must state result, help level, attempt kind, interpretation,
and the concrete next step. Until then, portal status describes the submission
workflow—not learner understanding.

## Ask Codex

A portal question stores the learner's text plus validated course, chapter,
topic, lesson, block, artifact, exercise, and attempt IDs that are actually in
scope. It never accepts arbitrary filesystem paths or copies private evaluation
criteria into question context.

Creating the record sets its status to `pending`; it does not call a model and
must not fabricate an answer or typing state. During an active Codex task, GNOS
can list pending items, reason with the chat and course context, and explicitly
write an answer. The portal then displays the stored answer as `answered`.

Inspect pending work:

```bash
python3 skills/course-design/scripts/manage_interaction.py pending \
  <learner-id> <course-id>
```

Answer one queued question:

```bash
python3 skills/course-design/scripts/manage_interaction.py answer-question \
  <learner-id> <course-id> --question-id <question-id> --file answer.json
```

Review one open-ended attempt:

```bash
python3 skills/course-design/scripts/manage_interaction.py review-attempt \
  <learner-id> <course-id> --attempt-id <attempt-id> --file review.json
```

Use the CLI's configured learner root when it is outside the default local
`learners/` directory. A successful write returns stored IDs and status; an
error must never be presented as a saved, checked, answered, or reviewed action.
