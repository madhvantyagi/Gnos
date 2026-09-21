# Course contract — design a course that builds

`course.json` is the map. It says where the learner goes, in what order,
from which source, and where they stand right now. Past topics sit before
`current`, the `current` topic is now, and later topics may stay
`provisional` until evidence firms them up.

It never holds lesson text or scores. Lesson text lives in the lesson
files, and scores live in chat and `learners/<id>/state.json`.

New plans use `schema_version: 2`. Do not write new version-1 plans.

## Build the course in order

This is the most important rule. Design the route so each topic needs
only what earlier topics already taught.

Order every chapter and topic so a later step never introduces what an
earlier step assumes. List only earlier topic IDs in `prerequisites`.
If step 3 needs step 5, reorder the course instead of reaching forward.

Start from the learner, not from the textbook. Record what they already
showed in `starting_evidence`, and write what you have not checked yet in
`assumptions` in plain words. An empty `starting_evidence` means unknown,
never beginner.

Give every topic an `outcome` that starts with a verb, such as predict,
derive, implement, or explain. The outcomes should read as a staircase
toward the course `goal`. Group them into chapters only where the group
marks a real stage in that staircase, so the portal table of contents
still finds its home.

Explain the whole idea in simple language before you formalize it. Each
lesson must leave the learner able to say what the topic is about as a
whole, not just repeat one formula. Build from the familiar case to the
general case, and return to the whole before you close.

Plan every topic to sustain at least four lesson sections that develop
the idea, and it can be more, for example naming the claim, working it through, varying or testing it, and practicing it. Never approve a topic that is only one
definition plus a quiz. Depth sets how far each section goes: a `survey`
still finishes the idea, `working` adds the diagrams, controls, and
motion needed for transfer, and `mastery` defends, derives, and teaches
it back. Thin skim is never acceptable at any depth.

## Keep one teacher per topic

Assign one lead `subject` and its matching `teacher` to every topic, and
read `teachers/<subject>/SOUL.md` with
`skills/subject/subjects/<subject>.md` before you plan that topic. Write
in that teacher's voice all the way through. Do not invent a teacher.
Set `teacher` to `null` when the subject has none. Add a supporting
subject only for a named bottleneck, give it one bounded bridge through
`supporting_subjects` and `supporting_teachers`, then return the lesson
to the lead teacher.

## Write `course.json` without the noise

Keep these fields short and exact:

- `id`, `title` (1-3 words), `goal` (starts with a verb, for example
  "Explain, implement, and diagnose gradient descent"), optional one-line
  `vision` (what done looks like), `depth` (`survey`, `working`, or
  `mastery`, agreed with the learner), `length` (their words, such as
  "six weeks"), `assumptions`, `starting_evidence`, ordered `chapters`
  with ordered `topics`, one `current` (`chapter_id`, `topic_id`,
  `next_step`), `revision` and `revision_notes`, and `sources`.
- Each topic carries `title`, `outcome`, `subject`, `teacher`,
  `supporting_subjects`, `supporting_teachers`, `concepts` (unique IDs
  like `math.derivative`), `prerequisites` (earlier topics only),
  `minutes` (positive integer), `resource_ids` (every ID must exist in
  top-level `sources`), `skill_routes` (nonempty, beneath `skills/`),
  `exercise_ids`, `lesson_ids`, `state`, and optional `feedback` and
  `representations`.
- Each source carries `title`, exactly one of HTTPS `url` or safe
  repository-relative `local_path`, `type`, `checked_on`, `sections`,
  and `verification_notes`.
- `state` is one of `current`, `planned`, `provisional`, `retired`, or
  `out-of-scope`. Keep exactly one `current` chapter and one `current`
  topic, and keep them pointing at each other. Retired history stays for
  the record and is never taught.

## Split each topic into representations

Give each topic its `representations` list, where each entry is a
different part of the topic with its own `id`, `kind` (`text`, `manim`,
`image`, `simulation`, `diagram`, `pdf`, `exercise`), one-line
`purpose`, and optional `concept` and `skill_route`. Do not teach the
same idea twice in two tools.

```json
"representations": [
  {"id": "secant-motion", "kind": "manim",
   "purpose": "Animate secant lines converging to the tangent."},
  {"id": "slope-lab", "kind": "simulation",
   "purpose": "Drag x and watch the predicted sign change."}
]
```

 Read
[representation-choices.md](representation-choices.md) for which medium
each part earns and how it dispatches to its skill and lesson block.
Treat the representation as authorization: the lesson binds each block
through `representation_id` and may add concrete text, timing, controls,
labels, and checks, but it may not change the concept, purpose, kind, or
skill route. If the lesson exposes a bad choice, revise this plan first
and validate before rebuilding the lesson.

## Revise from what the learner actually did

Keep `feedback` on taught steps short: `source_results` (`worked`,
`did-not-work`, `too-hard`, `no-access`), `direction` (`keep`, `swap`,
or `split`), one plain `note`, and a `repeats` count. Full attempts stay
in the learner record.

```json
{"revision": 3, "date": "2026-09-16",
 "reason": "Swapped openstax-3.5 for MIT 18.02 sec 2 on chain-rule after 2 repeats; terms did not match."}
```

Keep IDs stable, add 1 to `revision`, and write what changed and what the
learner struggled with. Never write "Updated plan." Writing `feedback`
alone needs no new revision. Changing sources, order, or scope does, and
then you validate again.

## Check

```bash
python3 skills/course-design/scripts/validate_course.py <course.json>
```

The script checks shape only: names, links, order, sources, one current
step. Whether the course builds well is your judgment, from the research
notes and what the learner actually did.
