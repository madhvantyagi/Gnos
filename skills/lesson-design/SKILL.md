---
name: lesson-design
description: "Develop the current course topic into an in-depth lesson using the assigned teacher, subject guidance, and learner evidence. Choose examples, practice, and useful media; review and publish the finished lesson."
---

# Lesson design

Develop the current topic into a complete lesson. Course design establishes
the progression and scope; this skill develops the reasoning, examples,
practice, and media that make the topic understandable.

Start after course design has enrolled the plan. If there is no enrolled
`learners/<learner>/courses/<course-id>/course.json`, stop and return
to course design. A new topic concept or changed topic scope needs a course
revision first. Choose and revise media within lesson design.

## 0. Read the current topic

Read these before writing anything:

1. The enrolled `course.json`: `depth`, `length`,
   `current.{chapter_id, topic_id}`, and that topic's `concepts`,
   `subtopics`, `prerequisites`, `resource_ids`, `subject`, and `teacher`.
2. The subject guide through `skills/subject/SKILL.md`. It says what
   learners in this field must inspect.
3. The assigned teacher's `SOUL.md`, when one exists, and the relevant
   learner evidence supplied by the orchestrator.
4. [Lesson design](references/lesson-design.md), before drafting the
   explanation. Use it to develop the reasoning, language, examples, and flow.
5. [The lesson contract](references/lesson-contract.md), for the structure
   and constraints of `lesson.json`.
6. [Representation choices](references/representation-choices.md),
   for the purpose and cost of each medium.
7. [The artifact manifest](../course-design/references/artifact-manifest.md).
   Only the coordinator writes it.

For mathematics in any subject, follow the notation and rendered checks in
[the lesson contract](references/lesson-contract.md) before drafting equations,
prompts, or worked answers.

Use the agreed `depth` and `length` to pace the explanation and practice.
Develop the reasoning fully within that scope. A short lesson may need a
careful visual explanation; a long one may rely on text. Choose the forms that
help this lesson. Several forms can explain one idea when each adds a useful step.

## Develop the explanation and choose blocks

Use the lesson design reference to work out the reasoning before producing
files. The coordinator plans the reasoning in notes and briefs; workers write
the finished lesson blocks. Start with a question or example the learner can understand. Build the
idea from there, including steps that textbooks often leave implicit. Decide
which parts need prose, an equation, a diagram, motion, a simulation, or
practice. A lesson may use several of these together. Give each block a clear
purpose and keep the same terms, symbols, and example across them.
Plan the lesson as one answer to that opening question. For each block, say
what the learner already knows, what this block adds, and why the next block
is needed. Do not use a formal definition, theorem, or equation before the
learner has seen the objects it describes. If the current topic itself spans
too many new ideas for a connected lesson, return to course design to split it.
Use the subject's area guidance to identify the difficult transition and
choose views that help explain it. Plan the introduction, observation, and
interpretation of each visual together with the prose. Do not finish a text
lesson and then attach media to satisfy the two-form requirement.

| Need | Lesson block type |
| --- | --- |
| Explain or work through a step | `explanation`, `bullets`, `equation`, or `code` |
| Show a changing process | `voice-animation` or `animation` |
| Let the learner inspect a fixed relation | `diagram` or `artifact` |
| Let the learner change an input | `interactive-graph` or `simulation` |
| Let the learner use the idea | `exercise` |

Choose the block type while drafting the lesson. New blocks do not need a
`representation_id`. Older lessons may keep one when they follow an existing
course representation plan.

A ready lesson needs at least two distinct teaching forms. Prose and a worked
equation, a diagram, a code trace, a source, motion, or a simulation can form
a useful pair when each shows something the other cannot. Two prose blocks
are still one form. Exercises and feedback check learning; they do not count
toward the two. There is no maximum. Add further forms when they deepen the
same explanation, not to fill a quota.

## 1. Write the skeleton in reasoning order

A newly authored `lesson.json` uses `schema_version: 2` and holds `id`,
`course_id`, `chapter_id`, `topic_id`,
readable `title`, observable `purpose`, `concepts` from the topic, the
topic's `teacher` (or `null`), `skill_routes` chosen for the lesson,
`assumptions`, ordered `blocks`, detailed `exercises`, `publication`
(`draft`, `ready`, or `archived`), and real UTC timestamps.

Order blocks so each explanation or activity prepares the learner for what
follows. Develop the topic fully within its concepts and sources. Add media
only where it helps the learner see, change, or practice something specific.
An explanation block may contain several paragraphs. Add as many blocks as
the reasoning needs; there is no target block count. Do not shorten the
teaching to keep JSON small. Use `text` with paragraph breaks for connected
prose; the viewer renders those paragraphs in order.
Existing version-1 lessons remain readable under their original contract.
Before dispatch, the coordinator writes each exercise's structured contract
in `exercises`: stable `id`, concepts, learner prompt, response type,
evaluation mode, success criteria, and any private worked solution. This is
validated lesson data, not a lesson block. It gives the exercise-block worker
a fixed target to build around.

Validate the complete skeleton, including exercise contracts, and publish it
as `draft` before dispatching block workers or producing files. The draft gives
every artifact a real lesson ID:

```bash
python3 skills/course-design/scripts/validate_lesson.py lesson.json \
  --course learners/<learner>/courses/<course-id>/course.json
python3 skills/course-design/scripts/course_workspace.py publish \
  learners/<learner>/courses/<course-id> --lesson lesson.json
```

## 2. Brief each delegated block

Every lesson block is produced by its own sub-agent. Add a complete
`production` brief to every version-2 block, including short explanations, transitions,
notation, and exercises. A worker may return a text fragment without a file;
it still owns exactly one block. The coordinator does not write lesson blocks.
Read [how each block worker works](references/worker-brief.md) for what
each worker has to do and how to brief it. Each brief names:

- `skill_route`: declared in the lesson for this block.
- `brief`: one bounded job. Name the object, relation, label,
  control, or check the worker must produce.
- `must_include`: every item the worker must show.
- `continuity`: terms, symbols, colors, direction, units, names, and
  dates the worker must keep from earlier blocks.
- `acceptance_checks`: how you will check the result.
- `depends_on_block_ids`: an explicit list of earlier block IDs that this
  worker needs to read or build on. Use `[]` when the block has no such
  dependency. Dependencies must point backward in lesson order.

If a block continues the running explanation, make it depend on the earlier
block whose result it uses. Include the preceding block when the transition
would otherwise be lost. Ask each worker to begin from the open question left
by that dependency and end with the question its result raises. Parallel
workers can build separate views of the same established idea; the
coordinator must still join their results into a readable order.

Do not write "make it clear", "make it engaging", or "add context".
Those words test nothing.

## 3. Produce the blocks and assemble the lesson

Assign each block to one sub-agent, with one unique output path per worker.
Give the worker only its block, its purpose, selected subject guidance,
shared continuity rules, required source material, and the outputs of the
blocks named in its dependencies. Do not send the full lesson or unrelated
blocks. Also give every worker the assigned teacher path or `null`, the
relevant teacher guidance, the learner's starting knowledge, the opening
question, and where this block must leave the explanation. Media workers need
this context for captions, narration, and controls too. Workers return a completed block fragment or artifact plus its
registration payload. They never edit `course.json`, `lesson.json`, or
`manifest.json`.

Dispatch all blocks with no unmet dependencies in parallel. Dispatch a
dependent block only after every named block has returned and passed its
checks. Keep the dependency graph acyclic and consistent with lesson order.
If multi-agent execution is unavailable, stop after publishing the validated
draft and report that block delegation could not run. Do not complete or
publish a `ready` lesson as though workers had produced it. Continue solo only
if the learner explicitly changes the request to authorize that workflow.

Check every result against its acceptance checks. Reject a result
that breaks continuity or changes the assigned block. If a worker finds that
the chosen medium cannot teach the idea, revise that lesson block and its
brief. Return to course design only when the topic needs a new concept, source,
or place in the sequence.

After every worker returns, assemble the lesson in the skeleton's original
block order. The coordinator alone merges fragments and updates `lesson.json`.
Copy checked media files to their assigned course-workspace paths. Review the
assembled lesson using
[lesson-design.md](references/lesson-design.md).
Read it start to end and fix unstated definitions, missing steps, and transitions.
Reject a block that only names a concept or drops an equation into the page.
Check that the first block starts from a familiar situation, each later block
uses what came before, every simulation result is interpreted, and the last
teaching block answers the opening question and prepares the next topic.
Check that at least two distinct teaching forms develop the idea and that
each block does what its own purpose says,
check math uses `$...$` and `$$...$$` delimiters in prose,
and check the prose follows the assigned teacher SOUL.md. Then write the design
receipt into `lesson.json`, set `publication` to `ready`, and validate again:

```bash
python3 skills/course-design/scripts/validate_lesson.py lesson.json \
  --course learners/<learner>/courses/<course-id>/course.json
```

The receipt has four fields: `designed_at` (UTC timestamp between `created_at`
and `updated_at`), `course_fingerprint` (output of `course_content_fingerprint()`
for the enrolled `course.json`, which excludes `lesson_ids` so registering the
lesson does not invalidate its own receipt), `skill_route` (`skills/lesson-design/SKILL.md`),
and `review` (`pass`). A `ready` lesson without this receipt fails validation.
A `draft` lesson does not need it. Publish the validated `ready` lesson with
`course_workspace.py publish`. The artifact registry requires that lesson ID
to be published before it accepts a ready artifact. Only then does the
coordinator register each checked artifact and refresh the manifest
fingerprint between writes:

```bash
python3 skills/course-design/scripts/manage_artifact.py --learners-root learners \
  register <learner-id> <course-id> --file artifact.json
```

If a required artifact cannot be registered, return the lesson to `draft`
and repair the file or record. Do not show a page with missing lesson media.
After every artifact is registered, hand control back to the orchestrator. It asks
“Do you want to see the course now?” after this lesson is finished. If the learner
already asked to see it, the orchestrator can use course-viewer immediately.
Do not render or link the page before that request or answer.

Teach directly in chat while the learner is actively interacting. The formal
lesson still captures the topic for the portal. When evidence changes the
route itself, send the change to
course-design with the reason so it lands in `revision_notes`. See
`skills/learner-tracking/SKILL.md` for the adaptive step.

You only need `validate_lesson.py`, `course_workspace.py publish`,
and `manage_artifact.py register` for normal work. The workspace,
the plan validator, and the manifest live in `skills/course-design/scripts/`;
call them by those paths.
