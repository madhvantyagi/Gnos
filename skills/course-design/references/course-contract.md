# Living course contract

New persistent courses use `schema_version: 2`. The course file is a living
table of contents: it records the destination, dependency route, teaching
assignments, inspected sources, and current frontier. Detailed lessons and
learner attempts belong elsewhere.

Version 1 remains readable through a deterministic adapter so an enrolled course
does not break during migration. Do not author new version-1 plans.

## Course fields

Required root fields are:

- `id`, `title`, `goal`: stable slug and readable destination.
- `revision`: positive integer.
- `revision_notes`: ordered objects with that revision, an ISO date, and the
  concrete reason the route changed.
- `starting_evidence`: observations already established before enrollment. An
  empty list means unknown, not beginner.
- `assumptions`: unverified prerequisites or constraints stated as text.
- `sources`: source ID to inspected-source record.
- `current`: `chapter_id`, `topic_id`, and a precise `next_step`.
- `chapters`: a nonempty ordered list.

The source registry makes the plan portable. Each source contains `title`, an
HTTPS `url` or safe local path, `type`, `checked_on`, relevant `sections`, and
`verification_notes`. A search result or plausible title is not an inspected
source. If access or scope remains uncertain, say so in the notes.

## Chapters and topics

Each chapter has a stable `id`, readable `title`, planning `state`, and nonempty
ordered `topics`. A topic has:

- stable `id`, `title`, and planning `state`;
- an observable `outcome`;
- one lead `subject` and an optional `teacher`;
- `supporting_subjects` and `supporting_teachers` only for named bridges;
- repository-relative `skill_routes` needed to teach the topic;
- stable `concepts`;
- `prerequisites` referring only to earlier topic IDs;
- a positive `minutes` estimate;
- `resource_ids`, `exercise_ids`, and `lesson_ids`.

Use the matching teacher when that subject has an available SOUL and the persona
helps the course. Otherwise store `teacher: null`; never invent a persona or
exclude a supported subject because it has no teacher file. Supporting subjects
may likewise appear without supporting teachers. Every named supporting teacher
must exist and correspond to one of the named supporting subjects. Teachers do
not create a panel discussion: one assigned teacher leads, and another appears
only for a specific conceptual bridge.

Skill routes must resolve inside this repository's `skills/` tree. Use the
general subject entrypoint and the selected subject file when needed. Add PDF,
Manim, or another production skill only when the planned representation calls
for it. A directory name alone does not load or invoke a skill.

## Planning state is not progress

Chapter and topic `state` is one of:

- `current`: the active teaching frontier;
- `planned`: committed near-term route;
- `provisional`: likely later route that evidence may change;
- `retired`: preserved history no longer on the active route;
- `out-of-scope`: deliberately omitted from this course goal.

These values describe curriculum decisions. They never mean that the learner
understands a concept. Exposure, practice, independent success, and later
retention are derived from learner attempts.

Keep exactly one current topic. `current.chapter_id` and `current.topic_id` must
resolve to it. If evidence changes the route, preserve stable identifiers,
increment the revision, append the reason, and update the frontier. Do not edit
old attempts or rename retired material as completed.

## Initial depth

Research enough at enrollment to produce a defensible chapter-level route and
identify major prerequisites. Later chapters may remain provisional. Fully
author only the current topic and its next useful lesson. A complete table of
contents is not permission to generate every explanation, exercise, and media
artifact before the learner responds.

`lesson_ids` grows as validated lessons are published. `exercise_ids` expresses
the topic's assessment intent; the detailed prompts, response formats, private
criteria, and lesson placement live in lesson files.

## Compatibility

The version-1 adapter preserves the old plan's goal, assumptions, concepts,
teachers, sources, assessments, order, and dependencies while placing its
modules into a valid chapter/topic hierarchy. Its output must be deterministic.
Migration changes storage shape, not evidence. Validate the resulting version-2
plan before saving it.

## Validation

Run:

```bash
python3 skills/course-design/scripts/validate_course.py <course.json>
```

The validator checks structure, slugs, repository routes, source records,
optional teacher and subject availability, unique IDs, ordered dependencies, the current
frontier, and reference integrity. Validation cannot establish that a course is
well researched or suitable for a particular learner; the course-design skill
must make those judgments from the current request and evidence.
