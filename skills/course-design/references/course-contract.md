# Course contract

Use this reference to design the progression of a course and record it in
`course.json`. Decide what the learner should understand at each stage, what
that stage depends on, and how it prepares them for the next one. Lesson design
uses those decisions to write the explanations, examples, and activities.

Create new plans with `schema_version: 2`. Keep lesson content in lesson files
and learner attempts in `learners/<id>/state.json`.

## Establish the goal and starting point

Write a course `goal` that describes what the learner will be able to do.
“Derive and implement gradient descent” gives the course a clearer destination
than “Learn optimization.” Use `starting_evidence` for abilities the learner
has demonstrated. Put unverified prerequisites in `assumptions`; an empty
record does not establish that someone is a beginner.

Use the agreed `depth` to decide how far the course develops its ideas. A
`survey` should explain the central ideas and their connections. A `working`
course should prepare the learner to apply them independently. A `mastery`
course should also develop their ability to justify the methods and examine
their limits. Each depth needs complete explanations within its chosen scope.

Use `length` to set a realistic scope and pace. Estimate topic `minutes` for
explanation, examples, practice, and reflection together. If that work exceeds
the available time, narrow the course or discuss a longer duration. Do not fit
the schedule by removing the reasoning that makes a topic understandable.

## Build the progression

Arrange topics so each one uses knowledge established earlier or explicitly
identified as a starting prerequisite. List only earlier topic IDs in
`prerequisites`. If an early topic depends on a later one, repair the order.

Give each topic an observable `outcome`, such as explaining a distinction,
predicting a result, or implementing a method. Check how those outcomes
contribute to the course goal. Group related topics into a chapter when they
develop a larger idea or capability; name the chapter so that progression is
visible in the contents page.

Choose topic boundaries that support a complete lesson. A topic should give
lesson design room to explain the idea, develop an example, examine what
changes in another case, and provide useful practice. These are reasons to
develop the topic, not mandatory section headings or a section count. Split a
topic when it contains several outcomes that need separate development.

Plan the whole course, but leave uncertain future topics `provisional`. Develop
them further as learner evidence establishes what is needed. The position of
a topic in the plan does not prove that the learner has understood it.

## Assign the subject and teacher

Read the selected subject guide through `skills/subject/SKILL.md` and its
matching `teachers/<subject>/SOUL.md` when one exists. Use the subject guide to
check prerequisites, likely misconceptions, and suitable evidence of learning.
Assign one lead `subject` and its matching `teacher` to each topic. Use `null`
for a subject with no teacher; do not invent a persona.

Add `supporting_subjects` and `supporting_teachers` only when a specific
connection requires them. Identify what the supporting subject contributes
and where its contribution ends. Lesson design keeps the lead teacher's voice
through that explanation.

## Plan what each representation contributes

Read [representation-choices.md](representation-choices.md) alongside the
subject guide. Give each topic a `representations` list that covers the
explanation and practice as well as any useful media. For each entry, record
a stable `id`, a `kind`, and a sentence stating its `purpose`. The supported
kinds are `text`, `manim`, `image`, `simulation`, `diagram`, `pdf`, and `exercise`.
Use `concept` to identify the relevant topic concept and `skill_route` to name
the production skill; include the route for any representation that will have
a production brief.

Choose complementary representations. Text might explain a geometric relation
while a diagram lets the learner inspect it. That pairing serves one
explanation. Two artifacts that repeat the same demonstration without adding
anything useful should be combined or removed.

For example, a topic about local slope might include:

```json
"representations": [
  {"id": "slope-explanation", "kind": "text",
   "purpose": "Explain local slope through a worked example."},
  {"id": "secant-motion", "kind": "manim",
   "purpose": "Show how secant slopes approach a tangent slope."},
  {"id": "slope-practice", "kind": "exercise",
   "purpose": "Predict and justify the slope in a changed example."}
]
```

Lesson design may expand an approved representation into several blocks and
choose the examples, wording, and transitions. Each block refers to its
representation through `representation_id`. A new concept, changed purpose,
different medium, or different skill route requires a course revision first.
Adding detail within the approved scope does not.

## Record the plan

Keep the fields below concise enough to use during lesson design. Write
decisions in complete sentences where an explanation is needed.

| Part | What to record |
| --- | --- |
| Course identity | A stable `id`, a short descriptive `title`, the `goal`, and an optional one-line `vision` of the finished capability. |
| Scope | Agreed `depth` and `length`, supported `starting_evidence`, and unverified `assumptions`. |
| Structure | Ordered `chapters` containing ordered `topics`. Give each chapter and topic a stable ID and a readable title. |
| Current position | One `current` object with `chapter_id`, `topic_id`, and a concrete `next_step`. |
| History | `revision` and `revision_notes` explaining changes to the plan. |
| Sources | A `sources` record containing the references the course actually uses. |

Each topic records its `outcome`, `subject`, and `teacher`, together with any
`supporting_subjects` and `supporting_teachers`. Use unique concept IDs in
`concepts`, earlier topic IDs in `prerequisites`, and a positive integer for
`minutes`. Its `resource_ids` must refer to top-level `sources`. Keep
`skill_routes` nonempty and beneath `skills/`. Include `exercise_ids`,
`lesson_ids`, `state`, and the planned `representations`; add `feedback` when
there is evidence to record.

For each source, provide `title`, `type`, `checked_on`, `sections`, and
`verification_notes`. Supply exactly one location: an HTTPS `url` or a safe
repository-relative `local_path`.

Use the states `current`, `planned`, `provisional`, `retired`, and
`out-of-scope`. Keep exactly one current chapter and one current topic, aligned
with the `current` object. Retain retired topics as history rather than
including them in active teaching.

## Revise from learner evidence

Keep topic `feedback` brief. Record `source_results` as `worked`, `did-not-work`,
`too-hard`, or `no-access`; set `direction` to `keep`, `swap`, or `split`.
Include a plain `note` and a `repeats` count. Full attempts belong in the
learner record.

Preserve IDs when revising. Increase `revision` by one when sources, sequence,
scope, or representation decisions change, and add a dated `revision_notes`
entry explaining the decision. For example, say that a topic was split because
the learner could compute a derivative but could not interpret its sign.
“Updated plan” does not explain a decision. Recording feedback alone does not
require a new revision.

Validate after creating or revising the plan:

```bash
python3 skills/course-design/scripts/validate_course.py <course.json>
```

The validator checks structure and references. Review the progression yourself:
can the learner reach each outcome using the earlier topics and stated starting
knowledge, within the agreed scope and time?
