# Lesson contract

Use this reference for the structure and publication requirements of
`lesson.json`. Read [lesson-design.md](lesson-design.md) for how to develop
the explanation, examples, and teaching sequence within that structure.

## Lesson shape

Write one lesson file per topic. It holds:

- `schema_version: 2` for newly authored lessons; existing version-1 lessons
  remain readable and are not retroactively required to have worker briefs.
- `id`, `course_id`, `chapter_id`, `topic_id`, readable `title`, teaching `purpose`
- `concepts` from the topic, assigned `teacher` or `null`, repository-relative `skill_routes`
- `assumptions` supported by evidence or marked unverified
- ordered `blocks`, detailed `exercises`
- `publication`: `draft` while building, `ready` when the learner sees it
- real UTC timestamps: `created_at`, `updated_at` ending in `Z`

Keep ids stable. You may change the title. Never change the id to
fix wording. Inherit the topic teacher. Never invent a persona.
Keep `skill_routes` unique and beneath `skills/`. Include each skill that
will produce a lesson block or file.

Before validating and publishing the draft, the coordinator writes each
exercise's structured contract in `exercises`: stable `id`, concepts, a
provisional learner prompt, response type, evaluation mode, success criteria,
and any worked solution. This contract is data used by the exercise block and
viewer; it is not itself a lesson block. The worker assigned the corresponding
`exercise` block receives the contract and authors the final learner-facing
prompt and worked solution against it. It returns the block reference plus
the completed exercise data. The coordinator merges both into `lesson.json`,
checks that response type, evaluation, and success criteria still match the
contract, then revalidates and republishes the draft before accepting the
result. If those contract fields need a change, the worker returns a proposal;
the coordinator decides, updates the data, and revalidates.

Write a worked answer in the exercise's top-level `solution` string. Explain
the reasoning as well as the result, using the same notation as the lesson.
This is separate from `evaluation`: manual evaluation still means a teacher
must review the learner's response. The solution stays out of the initial
HTML and public lesson JSON. The local server returns it only after a saved
attempt and an explicit Show answer request. Older exercises without a
solution remain readable; add one when revising them.

## Blocks and the course plan

Every block carries `id`, `type`, `concepts`, and a short `purpose`. Its
concepts must belong to the topic. Choose its type and purpose while designing
the lesson; the course does not prescribe a media list. A new block needs no
`representation_id`. Older lessons may keep that field when their course has
a representation plan. In those lessons, keep the old ID, kind, purpose, and
production route consistent with the plan.

Before setting `publication` to `ready`, include at least two distinct
teaching forms. Explanation and bullets are both prose. An equation, code,
source, still visual, animation, interactive model, or artifact may add a
second form. Exercise and feedback blocks do not count. Give every form a
different job in the reasoning. The validator checks the form count; the
lesson review checks whether the forms actually help.

Choose each block by what the learner must do:

- To state a claim, definition, or step, use text. Say the exact point.
- To show change over time, use motion. Keep one thing fixed while one thing moves.
- To let comparison take time, use a still. Label the relation to inspect.
- To let the learner change an input and see the result, use simulation. Show controls, units, and reset.
- To test transfer, use an exercise that applies the idea to a changed case or condition.

Order blocks so the learner can follow the reasoning across them. Text and
media may explain one idea together. Remove repetition that contributes no
new explanation, observation, or practice.

## Teamwork and briefs

For a new version-2 lesson, every block has a complete `production` brief,
even in a `draft`. Existing version-1 lessons keep their earlier optional
production-field semantics.

The coordinator owns assembly. One sub-agent owns each block output
and nothing else, including prose, notation, transitions, and exercises.
Read [how each block worker works](worker-brief.md)
before you brief a worker, and follow the instructions it gives for that
type of block. Do not reinvent the worker instructions.

1. Read the topic and subject guidance, then decide what the lesson must explain.
2. Write the full skeleton in reasoning order, including complete exercise
   contracts in `exercises`.
3. Add a production brief to every block, then validate and publish as `draft`.
4. Dispatch blocks with no unmet dependencies in parallel. Give each worker its block, purpose, subject excerpt, assigned teacher guidance, learner starting point, opening question, continuity rules, sources, dependency outputs, and a separate output path. State what the next block needs from this one. Dispatch dependent blocks only after their dependencies pass review.
5. Check each result against its acceptance checks. Reject shifts in terms, symbols, colors, units, names, or dates.
6. After all workers return, merge fragments in skeleton order and inspect the files. Review and validate the lesson, set it to `ready`, and publish it. Then register its checked artifacts one at a time; the manifest requires a published lesson ID. If registration fails, return the lesson to `draft` and repair the artifact. Hand back to the orchestrator only when the lesson and its artifacts are ready; render after the learner says yes.

If sub-agents are unavailable, stop after publishing the validated draft and
report that delegation could not run. Do not publish the lesson as `ready`
unless sub-agents produced and passed review for every block. Continue solo
only if the learner explicitly changes the request to authorize it.

A worker never edits the course, lesson, or manifest. A worker never
changes concept, purpose, type, or route. If the medium cannot teach
the purpose, stop that block. The coordinator revises the lesson brief and
checks the result again. Revise `course.json` only for a change in topic scope.

Each brief names:

- `skill_route`: declared by the lesson
- `brief`: one bounded job in plain verbs
- `must_include`: every object, label, control, or relation to show
- `continuity`: symbols, colors, units, and names to keep
- `acceptance_checks`: what you will look at to accept
- `depends_on_block_ids`: an explicit list of earlier blocks this worker needs; use `[]` if there are none

Never write make it clear, make it engaging, or add context. Name the
object and the check.

## Output text rules for every block

These rules apply to text, narration, labels, prompts, and controls.
They keep every representation consistent.

- State claims precisely and explain how they follow. Keep sentences readable without breaking connected reasoning into fragments.
- Use bullets only for parallel items. Use an equation block when the learner must inspect notation.
- Write mathematics as LaTeX. Use `$...$` in prose and `$$...$$` for a displayed expression; an `equation` block holds the expression without those delimiters. Escape backslashes in JSON strings, then inspect the rendered page for correct symbols, units, and layout.
- Keep terms, symbols, colors, direction, units, names, and dates identical across explanation, motion, graph, and exercise.
- Ask exercises under a changed condition, such as new inputs or evidence. Keep success criteria and answers private. Choice options stay public because the learner needs them. Everything else private stays out of the public projection.
- Add a short transition only when the reason to change medium is unclear. Never hide unrelated artifacts behind generic connectors.

## Validation

Run `python3 skills/course-design/scripts/validate_lesson.py <lesson.json> --course <course.json>` before every publish. Valid JSON is not proof of learning. Revise from learner response.
