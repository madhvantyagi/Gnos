# Adapt to the learner in real time

Watch what the learner does and change course the moment something
goes wrong. This is the learner's side. The course map lives
elsewhere, in `course.json`; you write the learner record here and
tell the course skill what to change.

The learner record is `learners/<id>/state.json`. Read and write it
with the script in this skill. The course plan is
`learners/<id>/courses/<course-id>/course.json`, owned by the course
skill.

For exercise-driven resumption, use [exercise-review.md](exercise-review.md)
first. Saving an answer does not automatically assess learning or improve a
lesson. Review the actual work, diagnose the gap, repair teaching when needed,
verify with a changed case, and record the continuation decision.

## The basic loop

The learner studies from whatever source the course suggested.
Something happens:

- it works — keep going
- the learner does not like the source, finds it too hard, or the
  words do not match — get a new source
- the learner is stuck on one idea — add a missing step or split it

You record what happened here, then the course skill updates the
contract with the new source or the new step. The two always move
together.

## What to write in the learner record

- what was tried, in one line
- how many times the learner asked again
- which source helped, which one failed and why
- one line on what the learner said they want or do not want

Store these as evidence, not as guesses. A repeat is a fact.
"Does not like this book" is a fact. "Probably a visual thinker"
is a guess — do not write that.

## What to send to the course skill

When a source fails or the learner is stuck, tell the course skill
to update `course.json`:

1. **New source.** The learner does not like or cannot use the
   suggested source. The course skill adds a new one, points the
   step at it, and removes the old ID when nothing uses it.
2. **Missing step.** The learner is stuck on something that should
   have come first. The course skill adds one small step before now.
3. **Split or cut.** After two or three tries it is still stuck.
   The course skill splits the step or marks extra work out of scope.
4. **Keep going.** It works. The course skill moves `current` to the
   next step.

Every such change goes into `revision_notes` on the plan with the
date, what changed, and what problem the learner had. That keeps
the contract honest about why the route moved.

## Send small fixes to the right skill

Not every fix needs a new plan version.

- The fix stays inside one block: the words are wrong, a label is
  wrong, or the same picture needs a second try. Tell the lesson
  skill to fix the block. No new `revision` is needed.
- The fix changes the plan: a new concept, prerequisite, topic boundary,
  order, source, or less scope. A medium or skill-route change also needs a
  plan revision when it changes a binding representation plan. Tell the
  course skill to update `course.json` with `revision` + 1 and a
  `revision_notes` reason. The lesson skill then rebuilds the blocks
  that changed. A lesson worker never changes `course.json` on its
  own.

## Simple rules

- Diagnose the first error; repair a missing teaching step as soon as it is evident.
- Repeated confusion: change the explanation, example, or representation and check the result.
- A persistent prerequisite gap: split or reorder the route through course-design.

Repeat counts describe observations, not mandatory thresholds for helping.
“Keep going” means recorded evidence supports the next action; a save or a
learner saying they finished reading is insufficient. An explicit skip preserves
the learner's pace and records the unresolved gap.

Never invent a response to fill the record. Steps not taught stay
marked so.

## How to find what is already known

Before teaching, read the learner record to see what they already
learned and what was hard. Do not re-teach from the start because
time passed. Start from the last hard point and the last note.
