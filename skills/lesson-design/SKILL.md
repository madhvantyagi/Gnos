---
name: lesson-design
description: "Develop the current topic into a connected lesson. Choose complementary representations, review each block, register its artifacts, and publish lesson.json."
---

# Lesson design

Build only the lesson for the current topic. The course is already
enrolled and designed by course-design. Do not rebuild the course here.

Start here after course-design has enrolled the course. If there is no enrolled
`learners/<learner>/courses/<course-id>/course.json`, stop and return
to course-design. Return there for a new concept, source, or topic boundary.
Choose media and develop explanations here; those choices alone do not require
a course revision unless the topic has a binding representation plan.

## Repair from reviewed exercises

Before authoring a follow-up lesson for “finished” or “next”, follow
[exercise review](../learner-tracking/references/exercise-review.md). Read the
current lesson, original prompts and criteria, actual attempts, and assistance;
do not rely only on a progress label. Inspect whether the explanation prepared
the exercise. Deepen or replace the block where reasoning breaks, add a distinct
worked contrast when useful, and keep the lesson's terms and flow connected.
Publish a revised draft through the normal review/ready workflow. Record source
attempts, changed blocks, diagnosis, and a fresh verification task in the lesson
review receipt. A correct retry of a disclosed answer does not verify the repair.
Return to course-design for a new prerequisite, concept, source, or topic boundary.

## 0. Read the current topic

Read these before writing anything:

1. The enrolled `course.json`: `depth`, `length`,
   `current.{chapter_id, topic_id}`, and that topic's optional `representations[]`,
   `skill_routes`, `concepts`,
   and `teacher`.
2. The subject guide through `skills/subject/SKILL.md`. It says what
   learners in this field must inspect.
3. [Developing the explanation](references/lesson-design.md).
   Read it before drafting and again when reviewing the assembled lesson.
4. [The lesson contract](references/lesson-contract.md).
   It defines `lesson.json`.
5. [Representation choices](references/representation-choices.md).
   Use it to choose a medium for each teaching job.
6. [The artifact manifest](../course-design/references/artifact-manifest.md).
   Only the coordinator writes it.

For a core concept or an unverified prerequisite that Khan Academy can explain
at the needed level, use [the Khan Academy skill](../khan-academy/SKILL.md)
to inspect an exact item before choosing it. A prerequisite clip should repair
one gap and lead straight back to this topic. A main-topic clip should sit
between a specific prediction and GNOS's own explanation or changed example.
Use Khan for an important section when it fits, and reuse it only when
a later section needs that exact content. Read its [selection reference](../khan-academy/references/selection.md) to distinguish
target-topic coverage from prerequisite-only coverage. Keep diagrams, code,
derivations, simulations, and other forms where they serve the remaining
reasoning. Do not add a generic resource list or assume watching proves understanding.

`depth` and `length` were agreed during course design. Use them to decide how
far to develop the reasoning and each representation. A survey needs a
carefully chosen central case; working depth needs application under changed
conditions; mastery needs closer examination of assumptions and limits.
Choose complementary forms for those jobs, including within one concept.
Duration alone neither requires more media nor limits a useful combination.

## Decide each representation

Choose the block type while drafting the reasoning. Write one sentence per
block before you build it:

"The learner must inspect, change, hear, compare, derive, or
practice ___."


Give each representation a distinct teaching job. Several forms can develop
one concept: a video can demonstrate a relation, a diagram can keep its parts
inspectable, and a simulation can test a changed input. Remove repetition
that adds no new explanation, observation, or practice.

| Representation kind | Lesson block type |
| --- | --- |
| `manim` | `voice-animation` |
| `image` | `diagram` or `artifact` |
| `diagram` | `diagram` or `artifact` |
| `simulation` | `interactive-graph` or `simulation` |
| `pdf` | `artifact` |
| `text` | `explanation`, `bullets`, `equation`, `code`, `source` |
| `exercise` | `exercise` |
| `khan` | `khan-video` |
| Khan Academy article or exercise | `source` |

For a mathematical graph, follow the selection rules in representation choices
and use [JSXGraph](../jsxgraph/SKILL.md) when they fit. Declare its production
route in the lesson as with the other media skills. It uses the existing
`interactive-graph` or `simulation` blocks; the graph library does not add a
new representation kind.

When the topic has a representation plan, bind a block to the matching
entry with `representation_id` and keep its concept, purpose, kind, and
skill route. For a topic without that plan, choose the medium during lesson
design. In either case, put a Khan video in its own `khan-video` block with
a prompt tied to this lesson's concept and the next learner action. Check the
actual segment before publishing and follow it with GNOS's own example or
exercise. If a planned representation is wrong, revise and validate
`course.json` before changing the lesson.

## 1. Write the skeleton in reasoning order

A `lesson.json` holds `id`, `course_id`, `chapter_id`, `topic_id`,
readable `title`, observable `purpose`, `concepts` from the topic, the
topic's `teacher` (or `null`), `skill_routes` carrying the topic guidance and chosen media producers,
`assumptions`, ordered `blocks`, detailed `exercises`, `publication`
(`draft`, `ready`, or `archived`), and real UTC timestamps.

Order blocks by reasoning, not by file type. A good order names the
claim, lets the learner inspect its changing parts, then asks for a
prediction. When a topic has a representation plan, use its approved
media or revise that plan. Without a plan, choose the media that teach
the current concept.

Validate the skeleton and publish it as `draft` before producing
files. The draft gives every artifact a real lesson ID:

```bash
python3 skills/course-design/scripts/validate_lesson.py lesson.json \
  --course learners/<learner>/courses/<course-id>/course.json
python3 skills/course-design/scripts/course_workspace.py publish \
  learners/<learner>/courses/<course-id> --lesson lesson.json
```

## 2. Brief each delegated block

For schema version 2, give every block a complete `production` brief, including
blocks the coordinator writes. The brief preserves the teaching decision.
Read [the worker packets](references/worker-brief.md) for per-kind
wording. Each brief names:

- `skill_route`: declared by the lesson. Honor the topic route when a
  binding representation specifies it.
- `brief`: one bounded job. Name the object, relation, label,
  control, or check the worker must produce.
- `must_include`: every item the worker must show.
- `continuity`: terms, symbols, colors, direction, units, names, and
  dates the worker must keep from earlier blocks.
- `acceptance_checks`: how you will check the result.
- `depends_on_block_ids`: earlier blocks needed for this block; use `[]` when none.

Carry one concrete case through related blocks. Put its exact values, source
passages, assumptions, notation, and visual meaning in `continuity`. State what
the next view adds: a diagram exposes a relation, a trace explains its order,
or a control tests a changed condition. Do not make workers invent a fresh
example to fill missing context.

Use [build_block_context.py](scripts/build_block_context.py) to compile the
assigned block and its earlier dependencies without rewriting the lesson:

```bash
python3 skills/lesson-design/scripts/build_block_context.py lesson.json \
  --course learners/<learner>/courses/<course-id>/course.json --block <block-id>
```

The packet is private production context. Attach accepted media exports when
a dependency uses them; the script cannot establish that a file was inspected.

Do not write "make it clear", "make it engaging", or "add context".
Those words test nothing.

## 3. **Run workers, then merge**

Run multi-agent execution for each file-producing block.

Delegate long explanations or worked code when they benefit from focused
production. Keep short explanations, transitions, and notation yourself.

Give each worker only its block, its course representation, the
selected subject guidance, shared continuity rules, and required
source material. Workers write to separate output paths. They return
a completed block fragment or artifact plus its registration payload.
They never edit `course.json`, `lesson.json`, or `manifest.json`.


Check every result against its acceptance checks. Reject a result
that breaks the brief or continuity. Revise a medium or block purpose here;
return to course design for a new concept, source, or binding representation.
A worker proposes a change instead of silently returning a different artifact.

Only the coordinator updates the artifact manifest. Register finished
artifacts one at a time and refresh the fingerprint between writes:

```bash
python3 skills/course-design/scripts/manage_artifact.py --learners-root learners \
  register <learner-id> <course-id> --file artifact.json
```

Review the assembled public lesson in reading order and its private exercise
contracts using [the teaching review](references/lesson-design.md#review-depth-and-flow).
For a substantial lesson, delegate an independent review of that assembled
content, then repair its concrete findings while preserving one connected voice.
Block-level acceptance alone does not complete this review.

After repairs, remove any old receipt, keep the lesson as `draft`, and calculate
its authored-content fingerprint with `validate_lesson.py --design-fingerprint`.
Record the schema-2 `design_receipt` specified in the lesson contract, using
that hash and the current course fingerprint. Set the lesson to `ready`,
validate with `validate_lesson.py --for-publication`, publish it with
`course_workspace.py publish`, and re-render the course page:

```bash
python3 skills/course-viewer/scripts/render_viewer.py learners/<learner>/courses/<course-id>
```

If the learner has requested or approved viewing, give the fresh `portal/`
link with what to inspect. Otherwise return to the orchestrator's show question.
Teach directly in chat while the learner is actively
interacting. The formal lesson still captures the topic for the
portal. When evidence changes the route itself, send the change to
course-design with the reason so it lands in `revision_notes`. See
`skills/learner-tracking/SKILL.md` for the adaptive step.

Use `validate_lesson.py`, `course_workspace.py publish`,
and `manage_artifact.py register` for publication. The context compiler is an
authoring aid. The workspace,
the plan validator, and the manifest live in `skills/course-design/scripts/`;
call them by those paths.
