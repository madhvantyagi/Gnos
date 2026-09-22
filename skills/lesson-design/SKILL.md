---
name: lesson-design
description: "Develop the current course topic into an in-depth lesson using the assigned teacher, subject guidance, and approved representations. Write and review the explanation, produce its blocks, and publish the finished lesson."
---

# Lesson design

Develop the current topic into a complete lesson. Course design establishes
the progression and scope; this skill develops the reasoning, examples,
practice, and media that make the topic understandable.

Start after course design has enrolled the plan. If there is no enrolled
`learners/<learner>/courses/<course-id>/course.json`, stop and return
to course design. A new concept, changed topic scope, or different medium or
skill route needs a course revision first. Additional explanation and blocks
within the approved scope do not.

## 0. Read the current topic

Read these before writing anything:

1. The enrolled `course.json`: `depth`, `length`,
   `current.{chapter_id, topic_id}`, and that topic's `representations[]`
   (`id`, `kind`, `concept`, `purpose`), `skill_routes`, `concepts`,
   and `teacher`.
2. The subject guide through `skills/subject/SKILL.md`. It says what
   learners in this field must inspect.
3. The assigned teacher's `SOUL.md`, when one exists, and the relevant
   learner evidence supplied by the orchestrator.
4. [Lesson design](references/lesson-design.md), before drafting the
   explanation. Use it to develop the reasoning, language, examples, and flow.
5. [The lesson contract](references/lesson-contract.md), for the structure
   and constraints of `lesson.json`.
6. [Representation choices](../course-design/references/representation-choices.md),
   for the purpose and cost of each medium.
7. [The artifact manifest](../course-design/references/artifact-manifest.md).
   Only the coordinator writes it.

For mathematics in any subject, read [math notation](references/math-notation.md)
before drafting equations, prompts, or worked answers.

Use the agreed `depth` and `length` to pace the explanation and practice.
Develop the reasoning fully within that scope. A short lesson may need a
careful visual explanation; a long one may rely on text. Follow the approved
representations and return to course design if their selection needs to change.

## Develop the explanation and assign blocks

Use the lesson design reference to draft the reasoning before producing files.
Decide what each block contributes to that explanation and which approved
representation supports it. Text can introduce and interpret an image; remove
duplication when another block adds no explanation, observation, or practice.

| Representation kind | Lesson block type |
| --- | --- |
| `manim` | `voice-animation` or `animation` |
| `image` | `diagram` or `artifact` |
| `diagram` | `diagram` or `artifact` |
| `simulation` | `interactive-graph` or `simulation` |
| `pdf` | `artifact` |
| `text` | `explanation`, `bullets`, `equation`, `code` |
| `exercise` | `exercise` |

Every block carries a `representation_id`. It must name one entry in
the topic's `representations` list. The block purpose must match the
course representation purpose word for word. The lesson may add
concrete text, timing, controls, labels, and checks. It may not change
the concept, purpose, kind, or skill route. If the plan is wrong,
revise and validate `course.json` before changing the lesson.

## 1. Write the skeleton in reasoning order

A `lesson.json` holds `id`, `course_id`, `chapter_id`, `topic_id`,
readable `title`, observable `purpose`, `concepts` from the topic, the
topic's `teacher` (or `null`), `skill_routes` taken from the topic,
`assumptions`, ordered `blocks`, detailed `exercises`, `publication`
(`draft`, `ready`, or `archived`), and real UTC timestamps.

Order blocks so each explanation or activity prepares the learner for what
follows. One representation may support several blocks, and unused
representations need not become blocks. Develop the topic's outcome without
adding a medium the course did not approve.

Validate the skeleton and publish it as `draft` before producing
files. The draft gives every artifact a real lesson ID:

```bash
python3 skills/course-design/scripts/validate_lesson.py lesson.json \
  --course learners/<learner>/courses/<course-id>/course.json
python3 skills/course-design/scripts/course_workspace.py publish \
  learners/<learner>/courses/<course-id> --lesson lesson.json
```

## 2. Brief each delegated block

Add a complete `production` brief to every block a worker will build.
Read [how each block worker works](references/worker-brief.md) for what
each worker has to do and how to brief it. Each brief names:

- `skill_route`: already declared by the lesson and its topic.
- `brief`: one bounded job. Name the object, relation, label,
  control, or check the worker must produce.
- `must_include`: every item the worker must show.
- `continuity`: terms, symbols, colors, direction, units, names, and
  dates the worker must keep from earlier blocks.
- `acceptance_checks`: how you will check the result.
- `depends_on_block_ids` (optional): earlier blocks only.

Do not write "make it clear", "make it engaging", or "add context".
Those words test nothing.

## 3. Produce the blocks and assemble the lesson

When using multi-agent execution, assign each file-producing block to one
worker. Give a text or code block to a worker only when
it needs separate research or a long worked construction. Keep short
explanations, transitions, and notation yourself.

Give each worker only its block, its course representation, the
selected subject guidance, shared continuity rules, and required
source material. Workers write to separate output paths. They return
a completed block fragment or artifact plus its registration payload.
They never edit `course.json`, `lesson.json`, or `manifest.json`.

Run blocks with no unmet dependencies in parallel. A block listed in
`depends_on_block_ids` starts only after those earlier blocks return.
If multi-agent execution is unavailable or the user requests solo work, use
the same briefs and produce the blocks one by one. Apply the same checks.

Check every result against its acceptance checks. Reject a result
that changes the plan or breaks continuity. If a worker needs a
different concept, medium, or purpose, stop that block and revise
`course.json` first. A worker never repairs a course decision by
silently returning a different artifact.

Only the coordinator updates the artifact manifest. Register finished
artifacts one at a time and refresh the fingerprint between writes:

```bash
python3 skills/course-design/scripts/manage_artifact.py --learners-root learners \
  register <learner-id> <course-id> --file artifact.json
```

Review the assembled lesson using [lesson-design.md](references/lesson-design.md).
Check the explanation and transitions across blocks as well as each artifact.
Then validate the assembled lesson, set it to `ready`, publish it
with `course_workspace.py publish`, and re-render the course page:

```bash
python3 skills/course-viewer/scripts/render_viewer.py learners/<learner>/courses/<course-id> --require-current-lesson
```

Tell the learner the page is updated and give the `portal/` link with
what to click. The course-design turn already asked to show the
course, do not ask that question again here, just point at the fresh
page. Teach directly in chat while the learner is actively
interacting. The formal lesson still captures the topic for the
portal. When evidence changes the route itself, send the change to
course-design with the reason so it lands in `revision_notes`. See
`skills/learner-tracking/SKILL.md` for the adaptive step.

You only need `validate_lesson.py`, `course_workspace.py publish`,
and `manage_artifact.py register` for normal work. The workspace,
the plan validator, and the manifest live in `skills/course-design/scripts/`;
call them by those paths.
