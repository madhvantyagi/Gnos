---
name: course-design
description: Decide whether a GNOS learning goal needs a focused lesson or a persistent course, then research and revise a learner-specific chapter and topic route over time.
---

# Course design

Begin with what the learner wants to be able to do and the evidence already
available. Do not turn a subject name into a generic syllabus before
understanding the destination, current reasoning, depth, and constraints.

## Choose the scale

Use a small in-turn plan for one local target with only a few direct
dependencies. The working sequence is target, missing connection, explanation,
example, and an optional revealing check. Dividing an answer into headings does
not make it a course.

Use a persistent course when the learner requests sustained study or the
destination spans multiple competency branches, prerequisite chains, subjects,
artifacts, assessments, or sessions. A single named topic may still need a
course when learning it well requires that breadth.

Reuse what the learner has already said or demonstrated. If the boundary remains
uncertain, ask only what changes the route: the desired capability, relevant
work they can already do, and available time or depth. Do not require a test,
biography, or preferred learning style. Unknown evidence means unknown, not
beginner.

For a persistent course, read
[the living course contract](references/course-contract.md), then
[research the route](references/course-research.md). Create a defensible
chapter-level table of contents, not every future lesson. Read
[the adaptive lifecycle](references/adaptive-lifecycle.md) before enrollment or
revision. Read [the lesson contract](references/lesson-contract.md) only when
authoring a detailed lesson.

## Design the route

1. Phrase the destination and topic outcomes as observable actions under named
   conditions: derive, predict, implement, distinguish, or argue from evidence.
2. Separate confirmed starting evidence from assumptions. Place a short
   diagnostic or bridge where an uncertain prerequisite first matters.
3. Order chapters and topics by dependency. Mark distant material provisional
   when learner evidence may change it.
4. Assign one lead subject per topic and its matching teacher when an available
   persona helps. Use `null` for teacher-neutral subjects rather than inventing
   one. Add supporting subjects, teachers, or skills only for a named bridge or
   representation.
5. Map each outcome to an exercise that can expose misunderstanding. Keep private
   criteria out of the learner's view until an attempt or explicit solution
   request.
6. Record inspected sources and exact sections. A familiar title or search
   result does not verify a route.
7. Set one current topic and precise next step. Fully author only the next useful
   lesson.

Present the destination, chapter route, current topic, and largest unresolved
assumption in plain language. If competing destinations would produce different
courses, ask for the choice. Otherwise begin teaching rather than making the
learner approve routine internal structure.

## Compose, teach, and revise

A lesson can combine explanation, bullets, equations, voice animation, diagrams,
interactive graphs, simulations, and exercises. Each representation must serve
the same concept and preserve terminology, symbols, and visual meanings. Do not
assemble an artifact gallery and call it a lesson.

Teaching happens primarily in chat. After meaningful learner evidence, keep,
repair, reorder, expand, or retire future topics. Preserve stable identifiers and
earlier attempts. Increment the course revision and state the reason. Material
can be marked out of scope; it cannot be relabeled completed to make progress
look smooth.

Course design owns the route. The learner skill owns attempts and evidence-based
progress. Scheduled minutes, opened files, watched videos, and completed
explanations do not prove understanding.

Validate a plan with:

```bash
python3 skills/course-design/scripts/validate_course.py <course.json>
```
