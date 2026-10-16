# Course contract

Use this reference to design the progression of a course and record it in
`course.json`. Decide what the learner should understand at each stage, what
that stage depends on, and how it prepares them for the next one. Lesson design
uses those decisions to write the explanations, examples, and activities.

Create new plans with `schema_version: 2`. Keep lesson content in lesson files
and learner attempts in `learners/<id>/state.json`.

## Establish the goal and starting point
Write a course `goal` that describes what the learner will be able to do.
“Derive and implement gradient descent” names a clearer destination than
“Learn optimization.” Use `starting_evidence` for demonstrated abilities and
`assumptions` for unverified prerequisites. An empty record does not establish
that someone is a beginner.

Use the agreed `depth` to guide the course and its lessons. A `survey` explains
the central ideas and their connections. A `working` course prepares the learner
to apply them independently. A `mastery`
course should also develop their ability to justify the methods and examine
their limits. Each depth needs complete explanations within its chosen scope.

Use `length` to set a realistic scope and pace. Estimate topic `minutes` for
explanation, examples, practice, and reflection together. If that work exceeds
the available time, explain the tradeoff and agree a change in time or scope.
Do not fit the schedule by removing necessary reasoning.

## Build the progression
Arrange topics so each one uses knowledge established earlier or explicitly
identified as a starting prerequisite. List only earlier topic IDs in
`prerequisites`. If an early topic depends on a later one, repair the order.

Give each topic an observable `outcome`, such as explaining a distinction,
predicting a result, or implementing a method. Check how those outcomes
contribute to the course goal. Group related topics into a chapter when they
develop a larger idea or capability, name the chapter so that progression is
visible in the contents page.

Choose topic boundaries that support a complete lesson. A topic should give
lesson design room to explain the idea, develop an example, examine what
changes in another case, and provide useful practice. These are reasons to
develop the topic, not mandatory section headings or a section count. Split a
topic when its outcomes need separate development. Lesson design uses this
structure to develop the explanations and activities.

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

## Hand representation choices to lesson design

Course design owns the goal, concepts, prerequisites, and source coverage.
Lesson design chooses forms after developing the current topic's reasoning.
Read [representation choices](../../lesson-design/references/representation-choices.md)
with the subject guide when a source or prerequisite depends on what the
learner must inspect. New topics do not need a `representations` list.

For a topic that already has one, preserve its stable `id`, `kind`, `concept`,
`purpose`, and `skill_route`. Lesson blocks must keep those bindings through
`representation_id`. Revise and validate the plan before changing a binding;
extra explanation within it stays with lesson design. Supported kinds are
`text`, `manim`, `image`, `simulation`, `diagram`, `pdf`, `exercise`, and `khan`.

Do not assign one medium to a subject. A motion diagram, an equation, and a
control can develop different parts of the same mechanics question. The lesson
must explain their relationship and preserve the same system and units.

## Record the plan

Keep the fields below concise enough to use during lesson design. Write
decisions in complete sentences where an explanation is needed.

| Part | What to record |
| --- | --- |
| Course identity | A stable `id`, a course `title` that is the hero heading of at most 3 words, the `goal`, and an optional one-line `vision` of the finished capability. Put any longer description in `goal`, `vision`, or `hero_subtitle`, never in `title`. |
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
`lesson_ids`, and `state`; include `representations` only for a binding plan.
List in `exercise_ids` every exercise the topic's lessons use; the portal
resolves saves through that list, and lesson validation rejects an exercise
missing from it. Add `feedback` when
there is evidence to record.

For each source, provide `title`, `type`, `checked_on`, `sections`, and
`verification_notes`. Supply exactly one location: an HTTPS `url` or a safe
repository-relative `local_path`.

A Khan Academy video source uses `type: "khan-video"`, the exact HTTPS
`khanacademy.org` `/v/` URL, and a verified 11-character `youtube_id` for the
portal player. Put its source ID in the topic's `resource_ids`. The lesson's
`khan-video` block owns any start and end seconds for the selected segment.
Use `kind: "khan"` when this topic already has a representation plan. A new
lesson may choose the video during lesson design without adding that plan.

Use the states `current`, `planned`, `provisional`, `retired`, and
`out-of-scope`. Keep exactly one current chapter and one current topic, aligned
with the `current` object. Retain retired topics as history rather than
including them in active teaching.

## Define the evidence each new topic needs

For a new topic, include an `assessment` object with a nonempty `prompt`,
`success_criteria` containing nonempty readable strings, and `criteria`:

```json
{
  "prompt": "Derive the recurrence and explain why its cases cover every path.",
  "success_criteria": ["Justifies the recurrence from exhaustive, disjoint cases."],
  "criteria": [{
    "id": "derive-recurrence",
    "description": "Justifies the recurrence from exhaustive, disjoint cases.",
    "concepts": ["cs.recurrence"]
  }]
}
```

This is contract example data. Use the topic's actual concept IDs. Criterion
IDs are distinct stable slugs; `description` is required. Optional `concepts`
must be a nonempty unique subset of the topic's concepts; omitting it requires
evidence covering the whole topic. The readable strings and named criteria
describe the same requirements. Design exercises that actually request the
reasoning those requirements evaluate.

On `advance`, the teacher explicitly reviews each named criterion against saved
attempt or real chat evidence and explains what that evidence establishes.
Scripts verify scope, assistance, and current portal versions. They cannot infer
a derivation from a numeric response or judge the explanation themselves.
Older plans with only string criteria remain readable; those requirements are
visible as unmapped and are not silently certified by a concept's status.
Introduce IDs through an intentional plan revision and assess the actual work;
do not rewrite historical evidence to make it appear compliant.

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
