---
name: understanding-user-learning
description: Record and interpret GNOS learner evidence, recurring difficulties, preferences, coverage, and the next teaching step across sessions.
---

# Understanding the learner

Record what happened precisely enough that another teacher can make the next
decision. “Bad at math” is useless. “Cancelled x across addition; corrected it
after comparing x(x+1) with x²+1” tells the next teacher what to check.

## Read and write

For an established learner ID, use the script beside this skill:

```bash
python3 skills/understanding-user-learning/scripts/learner_state.py init alex
python3 skills/understanding-user-learning/scripts/learner_state.py summary alex
python3 skills/understanding-user-learning/scripts/learner_state.py record alex --event session.json
```

`init` creates an empty local record; it does not infer a name or ability.
Use `--root <directory>` before the subcommand for isolated tests or another
storage location. The default is this repository's ignored `learners/`.
For schema and update rules, read [references/evidence.md](references/evidence.md).

Enrollment writes the validated current plan to
`learners/<id>/courses/<course-id>/course.json`. Learner state stores its
relative reference, revision, and fingerprint rather than a second editable
copy. A mismatch blocks ordinary updates; reconcile the plan instead of choosing
one version silently. For an older record containing embedded plans, run
`migrate-courses <id>` once. The migration is idempotent and preserves events
and completion history.

## Course and memory categories

Read [references/memory-categories.md](references/memory-categories.md) when
starting, resuming, enrolling, or finishing a course. Store a validated course
with `enroll <id> --course <course.json>`. Use `complete-course <id> --course-id
<slug>` when the learner finishes; the script produces a chapter-by-chapter
curriculum with topic names, teachers, sources, assessments, and actual evidence.

Every recorded attempt or topic transition refreshes profile, course, topic,
teaching-observation, and next-step memories. Update at meaningful evidence
changes during the conversation, not only at the end of a course. On resumption,
use earlier taught topics as explicit bridges into the next topic. Read the
same learner ID; do not assume unrelated chats have shared memory.

Resolve every enrolled plan before changing learner state. If a referenced plan
is missing, stale, or invalid, fail before recording a new attempt or profile
change. Derived Markdown views may be rebuilt from valid state; they never
override it.

## Separate the kinds of knowledge

- **Stated preference:** “Use fewer analogies.” Store the wording and date;
  a current request overrides it.
- **Observation:** a specific answer, error, hint used, or successful transfer.
- **Interpretation:** a tentative explanation of the observation. Say “possibly
  confuses slope with height,” not “is a visual thinker.”
- **Action:** what the next teacher should try or ask.

Mark taught-but-untested concepts as exposed. Assisted success is practice.
Independent success supports demonstrated understanding of that concept in that
task. A later independent retrieval/transfer supports retention. None is a
permanent trait or a guarantee of general mastery.

## Choose the next move

If a wrong answer could have several causes, use one contrast to distinguish
them before labeling the gap. A new representation counts as helpful only when
subsequent work improves, not because the learner says it looks nice.

Use recent evidence and task difficulty together. After a long gap, check recall
briefly before choosing the pace. If the learner is correct but slow, distinguish
fluency practice from a conceptual repair. Do not prescribe a fixed review
interval as scientifically optimal; agree a date suited to the goal.

## Keep the record small and honest

Save short evidence excerpts, not whole conversations. Do not store unrelated
personal details, secrets, diagnoses, or guesses about intelligence. Keep records
for different learners separate. Never copy example evidence into a real profile.
Only report saved progress after a successful write. If saving fails, preserve
the note in the response and say it was not saved.

Use `profile <id> --file <json>` to replace explicitly provided preferences/goals.
Use `retract <id> --event-id <id>` to remove a mistaken event, then re-record a
correction if needed. Use `delete <id>` only when the learner requests erasure.
