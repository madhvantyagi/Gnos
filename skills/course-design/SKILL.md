---
name: course-design
description: Design or revise a GNOS lesson path or sustained course from the learner's goal, starting evidence, and available time.
---

# Course design

Design backward from something the learner wants to be able to do. “Understand
physics” needs a destination; “explain why a satellite keeps falling” already
has one. Use the subject skill to locate prerequisites and choose teachers.

## Ask only what changes the plan

Reuse information already given. For a broad request, ask up to three short
questions: the desired capability, something they can already do or have tried,
and the available time or deadline. Offer concrete destinations if they cannot
name one. Do not require a test, biography, or preferred “learning style.”

A tiny doubt needs only: target → missing connection → example → optional
check. Keep this plan in the turn; a course file is unnecessary unless requested.
For sustained study, read [references/course-contract.md](references/course-contract.md)
and create `courses/<slug>/course.json` plus a readable `COURSE.md` if useful.

## Build a teachable path

1. Phrase outcomes as observable actions: derive, predict, implement, distinguish,
   argue from evidence. Name the conditions under which the action counts.
2. Identify prerequisites. Separate confirmed knowledge from assumptions. Place
   a short diagnostic or bridge where an uncertain prerequisite first matters.
3. Order modules by dependency. Assign one lead teacher per module; add a
   supporting teacher only for a named conceptual bridge.
4. Pair each outcome with an assessment that can reveal misunderstanding.
   Put answer criteria in the plan, but withhold them during an assessment until
   the learner tries or asks for the solution.
5. Pick one main resource per module and optional alternatives for real gaps.
   Record the exact chapter/page once inspected. A book's existence does not
   mean its entire sequence fits this learner.
6. Reserve room for retrieval, repair, and application. Time estimates are
   negotiable; do not equate hours scheduled with mastery.

Present the destination, route, first lesson, and largest assumption in plain
language. If the request already supplies enough detail, begin teaching after
the brief plan. Ask for a choice only when competing destinations would produce
materially different courses.

## Revise rather than accumulate

On new evidence, repair a prerequisite, replace an example, or shorten a module.
Preserve stable concept IDs and completed evidence. Increment the course revision
and note the reason. A new goal can retire modules; mark them out of scope rather
than completed. Never silently rewrite history to make progress look linear.

Validate: `python3 skills/course-design/scripts/validate_course.py <course.json>`.
See `examples/courses/` for a tiny path and a multi-subject course.
