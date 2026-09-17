---
name: learner-tracking
description: Record what the learner does and adapt the course to it in real time.
---

# Understanding the learner

Record what happened precisely enough that another teacher can make the next
decision. “Bad at math” is useless. “Cancelled x across addition, corrected it
after comparing x(x+1) with x²+1” tells the next teacher what to check.

## Read and write

For someone you already know, use the script beside this skill:

```bash
python3 skills/learner-tracking/scripts/learner_state.py init alex
python3 skills/learner-tracking/scripts/learner_state.py summary alex
python3 skills/learner-tracking/scripts/learner_state.py record alex --event session.json
```

`init` creates a blank learner profile (`learners/<name>/state.json`). It
starts completely empty — do not guess or assume the user's name, background,
or skill level. By default, profiles are saved in the repository's ignored
`learners/` directory. Pass `--root <directory>` to use a different folder
(e.g., in automated tests). For the full schema and update rules, see
[references/evidence.md](references/evidence.md).

When enrolling a learner, the validated course plan is copied to
`learners/<id>/courses/<course-id>/course.json`. The learner's `state.json`
only stores a relative path, revision number, and fingerprint (hash) of the
course plan rather than keeping a duplicate copy. If the course plan changes
and its hash no longer matches `state.json`, future updates are blocked until
the plan is reconciled. If you are working with an older record that has an
embedded plan, run `migrate-courses <id>` once to convert it safely.

Never render lessons, viewer pages, or progress directly from a blueprint
`course.json`. Always set up the learner first:
1. **Identify the learner:** If they provide a name, convert it to a lowercase
   folder name (e.g., `alex`). If they don't, proceed automatically as
   `learner` and say: *"I'll save your progress under 'learner' — tell me a
   name anytime to make it yours."* Never ask the user for a "learner ID".
2. **Initialize and enroll:** Run `init` followed by `enroll --course <course.json>`.
   Omitting the name defaults to `learner`.
3. **Verify:** Confirm that `learners/<name>/courses/<course-id>/course.json`
   exists before recording attempts, summarizing progress, or rendering views.

## Course and memory categories

Read [references/memory-categories.md](references/memory-categories.md) when
starting, resuming, enrolling, or finishing a course. Store a validated course
with `enroll <id> --course <course.json>`. Use `complete-course <id> --course-id
<slug>` when the learner finishes; the script produces a chapter-by-chapter
curriculum with topic names, teachers, sources, assessments, and actual evidence.

Read [references/adaptive-lifecycle.md](references/adaptive-lifecycle.md) to
adapt in real time: record what the learner does, then tell the course skill to
update the plan when a source fails or the learner is stuck.

Every recorded attempt or topic transition refreshes profile, course, topic,
teaching-observation, and next-step memories. Update at meaningful evidence
changes during the conversation, not only at the end of a course. On resumption,
use earlier taught topics as explicit bridges into the next topic. Keep one
folder per person; do not assume unrelated chats have shared memory.

Resolve every enrolled plan before changing learner state. If a referenced plan
is missing, stale, or invalid, fail before recording a new attempt or profile
change. Derived Markdown views may be rebuilt from valid state; they never
override it.

## Separate the kinds of knowledge

- **Stated preference:** “Use fewer analogies.” Store the wording and date, 
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
