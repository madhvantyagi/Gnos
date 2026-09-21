# Lesson contract — design the topic in depth

Build one in-depth lesson for the current topic. Go deeper than the
`course.json` skeleton. Decide where to elaborate, where to let the
learner inspect, where to let them change inputs, and where to ask
for practice. This file is the rulebook for that lesson.

## Lesson shape

Write one lesson file per topic. It holds:

- `id`, `course_id`, `chapter_id`, `topic_id`, readable `title`, observable `purpose`
- `concepts` from the topic, assigned `teacher` or `null`, repository-relative `skill_routes`
- `assumptions` supported by evidence or marked unverified
- ordered `blocks`, detailed `exercises`
- `publication`: `draft` while building, `ready` when the learner sees it
- real UTC timestamps: `created_at`, `updated_at` ending in `Z`

Keep ids stable. You may change the title. Never change the id to
fix wording. Inherit the topic teacher. Never invent a persona.
Keep `skill_routes` unique and inside the topic routes.

## Blocks and the course plan

Every block carries `id`, `type`, `concepts`, short `purpose`, and
`representation_id`. The `purpose` matches the course representation
purpose word for word. The production `skill_route` matches the
representation skill route.

Use the mapping in `skills/lesson-design/SKILL.md`. If the plan is
wrong, revise and validate `course.json` first. Never add an
unapproved medium to fix a weak block. You may use fewer blocks than
the plan lists.

Choose each block by what the learner must do:

- To state a claim, definition, or step, use text. Say the exact point.
- To show change over time, use motion. Keep one thing fixed while one thing moves.
- To let comparison take time, use a still. Label the relation to inspect.
- To let the learner change an input and see the result, use simulation. Show controls, units, and reset.
- To test transfer, use an exercise. Ask for the same idea under new numbers.

One idea earns one primary medium. Never show the same idea twice in
two tools. Order blocks by reasoning: name the claim, make its
changing parts visible, then ask for a prediction.

## Teamwork and briefs

The coordinator owns the lesson. Each worker owns one block output
and nothing else. Read [how each block worker works](worker-brief.md)
before you brief a worker, and follow the instructions it gives for that
type of block. Do not reinvent the worker instructions.

1. Read the topic, its representations, and the subject guidance.
2. Write the full skeleton in reasoning order.
3. Add a production brief to every delegated block. Validate and publish as `draft`.
4. Send blocks with no unmet dependencies in parallel. Give each worker one block, its representation, subject excerpt, continuity rules, sources, and a separate output path.
5. Check each result against its acceptance checks. Reject shifts in terms, symbols, colors, units, names, or dates.
6. Merge fragments. Register artifacts one at a time. Validate, set to `ready`, publish, and render.

A worker never edits the course, lesson, or manifest. A worker never
changes concept, purpose, type, or route. If the medium cannot teach
the purpose, stop that block. The coordinator fixes `course.json`
and rebuilds. Never substitute silently.

Each brief names:

- `skill_route`: already declared by lesson and topic
- `brief`: one bounded job in plain verbs
- `must_include`: every object, label, control, or relation to show
- `continuity`: symbols, colors, units, and names to keep
- `acceptance_checks`: what you will look at to accept
- `depends_on_block_ids`: earlier blocks only, when needed

Never write make it clear, make it engaging, or add context. Name the
object and the check.

## Output text rules for every block

These rules apply to text, narration, labels, prompts, and controls.
They keep every representation consistent.

- State the exact claim, number, date, or code contract. Keep one idea per sentence.
- Use bullets only for parallel items. Use an equation block when the learner must inspect notation.
- Write math as LaTeX for KaTeX: inline `$...$`, display `$$...$$`. Never leave bare ASCII like `R^(m x n)` or `1/2`.
- Keep terms, symbols, colors, direction, units, names, and dates identical across explanation, motion, graph, and exercise.
- Ask exercises under a changed condition with new numbers. Keep success criteria and answers private. Choice options stay public because the learner needs them. Everything else private stays out of the public projection.
- Add a short transition only when the reason to change medium is unclear. Never hide unrelated artifacts behind generic connectors.

## Validation

Run `python3 skills/course-design/scripts/validate_lesson.py <lesson.json> --course <course.json>` before every publish. Valid JSON is not proof of learning. Revise from learner response.
