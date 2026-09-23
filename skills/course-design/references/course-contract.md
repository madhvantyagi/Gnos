# Course contract

Use this reference to design the progression of a course and record it in
`course.json`. Decide what the learner should understand at each stage, what
that stage depends on, and how it prepares them for the next one. Lesson design
uses those decisions to write the explanations, examples, and activities.

Create new plans with `schema_version: 2`. Keep lesson content in lesson files
and learner attempts in `learners/<id>/state.json`.

## Establish the goal and starting point
Write a course `goal` that describes what the learner wants to learn, what they
want to do with it, and what they will be able to do by the end. Preserve the
learner's intended application when they provide one. “Derive and implement
gradient descent to train a small model” gives the course a clearer destination
than “Learn optimization.” If a broad request could lead to substantially
different courses, ask one concise clarification about the intended result or
application before choosing the route. Use `starting_evidence` for abilities
the learner has demonstrated. Put unverified prerequisites in `assumptions`;
an empty record does not establish that someone is a beginner.

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
Treat an `assumption` as a question to check, not permission to omit a needed
foundation. Even when the learner knows related math, teach the first meaning
of a new subject in ordinary language before using its formal notation.

Name the main ideas in each topic and check how they contribute to the
course goal. Group related topics into a chapter when they develop a larger
idea or capability; name the chapter so that progression is visible in the
contents page. Lesson design decides what the learner will do with those ideas.

Choose cases, methods, and later synthesis topics from the stated goal and
application. Where useful, let the route move from foundations to more than
one relevant case or method, then connect them in a later topic. Do not add
unrelated topics just to create variety; each topic must prepare a capability
named in the goal.

Give each new topic an ordered `subtopics` list of the ideas inside it. Each
entry should say what changes in the learner's understanding, not name a media
file or repeat the topic title. For example, a topic on gradients might move
from “Why one slope is not enough for several inputs” to “What each partial
derivative measures” to “How the gradient combines those rates.” The next
topic can then use the gradient to choose an update. Lesson design may add
small connecting steps without changing this route.

Use subtopics to preserve the path into an idea. “Policy, value, Bellman” lists
terms; “How a rule chooses an action,” “Why a choice matters beyond its first
reward,” and “How a later decision contributes to today's value” name steps
that lesson design can develop. These steps may need separate topics. Check
their prerequisites before grouping them. Keep detailed explanations and
representation choices in the lesson; the JSON should make the course's
reasoning order clear without becoming a script for the teacher.

For each adjacent pair of topics, state the bridge in your planning notes:
what concrete question is left open, and which idea in the next topic answers
it? Put that bridge in the titles or subtopics when the sequence would
otherwise be hard to see. A title such as “Expectation to Bellman” may hide
several lessons: first show an agent making a choice and receiving a reward;
then develop return and expectation; only after states, policies, and value
are understood should the Bellman relation become the topic. The same check
applies in every field. Do not spend the opening lesson on vocabulary that
has no visible job yet.

Choose topic boundaries that support a complete lesson. A topic should give
lesson design room to explain the idea, develop an example, examine what
changes in another case, and provide useful practice. These are reasons to
develop the topic, not mandatory section headings or a section count. Split a
topic when it contains several ideas that need separate development.
Estimate time for that full work. A long `minutes` value does not make a
crowded topic teachable; divide it when one lesson would require several
unintroduced concepts or abrupt jumps in notation.

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

## Leave teaching choices to lesson design

The course names the topic, concepts, prerequisites, subject, teacher, and
sources. Do not prescribe an `outcome` or a `representations` list for a new
topic. Lesson design works out the explanation, examples, exercises, and media
when it authors the lesson. If that work reveals a missing concept or source,
revise the course. A different diagram, animation, or exercise does not change
the course route.

## Record the plan

Keep the fields below concise enough to use during lesson design. Write
decisions in complete sentences where an explanation is needed.

| Part | What to record |
| --- | --- |
| Course identity | A stable `id`, a course `title` that is the hero heading of at most 3 words, the `goal`, and an optional one-line `vision` of the finished capability. Put any longer description in `goal`, `vision`, or `hero_subtitle`, never in `title`. |
| Scope | Agreed `depth` and `length`, supported `starting_evidence`, and unverified `assumptions`. |
| Structure | Ordered `chapters` containing ordered `topics`. Give each chapter and topic a stable ID and a readable title. Give each new topic ordered `subtopics` that show its internal progression. |
| Current position | One `current` object with `chapter_id`, `topic_id`, and a concrete `next_step`. |
| History | `revision` and `revision_notes` explaining changes to the plan. |
| Sources | A `sources` record containing the references the course actually uses. |

Each topic records its `subject` and `teacher`, together with any
`supporting_subjects` and `supporting_teachers`. Use unique concept IDs in
`concepts`, earlier topic IDs in `prerequisites`, ordered `subtopics`, and a positive integer for
`minutes`. Its `resource_ids` must refer to top-level `sources`. Keep
`skill_routes` nonempty and beneath `skills/` for the subject guidance. Include
`exercise_ids`, `lesson_ids`, and `state`; add `feedback` when there is evidence
to record. Lesson design declares any media skill routes in `lesson.json`.

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
scope, or topic concepts change, and add a dated `revision_notes`
entry explaining the decision. For example, say that a topic was split because
the learner could compute a derivative but could not interpret its sign.
“Updated plan” does not explain a decision. Recording feedback alone does not
require a new revision.

Validate after creating or revising the plan:

```bash
python3 skills/course-design/scripts/validate_course.py <course.json>
```

The validator checks structure and references. Review the progression yourself:
can the learner reach each topic using the earlier topics and stated starting
knowledge, within the agreed scope and time?
