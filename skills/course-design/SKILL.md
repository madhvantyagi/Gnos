---
name: course-design
description: "Design and revise a course's goal, topic sequence, prerequisites, and sources. Record depth and duration, validate and enroll course.json, then hand the current topic to lesson-design."
---

# Course design

Use this skill when a learning goal needs several sessions or a sequence of
prerequisites. Answer a small local question directly in chat. For a course,
design the progression from the learner's starting point to the agreed goal.
Lesson design develops each topic into a complete lesson.

## Establish depth and duration

Before designing, establish what the learner wants to learn and be able to do,
how deeply they want to study it, and how much time they have. Ask only for
missing information. When the goal is broad or could mean several things,
also ask what they want to use it for and what they already know. Bundle the
unanswered points into one concise question instead of starting a generic
intake. Preserve the learner's wording for their goal and intended use in
`course.json`; record demonstrated knowledge separately from assumptions.

Record the agreed depth and duration in `course.json`:

- `depth`: `survey` for understanding the central ideas and connections,
  `working` for applying them independently, or `mastery` for justifying
  methods and examining their limits.
- `length`: the learner's intended duration, such as one session, six weeks,
  or a term.

Use these answers and the learner's intended use to choose the scope, pace,
research, and a course route that fits their goal.
A shorter course should cover fewer ideas well rather than abbreviating every
explanation.

## Research and plan the course

Read [course-research.md](references/course-research.md). Consult accessible
books, course materials, or documentation to check prerequisites, definitions,
and suitable exercises. Record what you actually opened and which sections
the course will use.

Read [course-contract.md](references/course-contract.md) and write
`course.json`. Work backward from the course goal and intended use to identify
the ideas it depends on, then order those ideas from the learner's starting
point forward.
Read the selected subject's subfield guidance before fixing that order. Use
its common confusions to find steps the route must develop, not just terms it
must mention. For each major method, identify the problem that makes it useful,
the simpler approach it builds on, and the limit that calls for the next idea.
Give each chapter a clear part of that route. Within each topic, list the
subtopics in the order the learner needs them. Make the current topic specific
enough to teach; leave uncertain later topics provisional.

Start the route with a situation the learner can picture in the subject they
asked to study. Identify the first unfamiliar idea needed to explain that
situation, then build the language and math for it. If the learner asks to
rebuild foundations, give those foundations their own topics. Do not put the
first example, its probability rules, its formal model, and its advanced
equation into one opening lesson. Ask what each topic lets the learner answer
that the previous topic could not, and name that step in its subtopics.

Make the route varied when the goal calls for it: include the needed
foundations, different relevant cases or methods, and opportunities to connect
ideas in later topics. Choose that variety from the learner's intended use and
the subject's evidence; do not add unrelated topics to make the course look
varied.

Check the route in both directions: can each topic use what came before, and
does it prepare the next topic? Read just the titles and subtopics in order.
If they sound like a list of terms instead of a developing explanation,
rewrite them. Split a topic when it asks the learner to learn several new
ideas before they can use any one of them. The subtopic list names ideas to
cover; it does not choose the lesson's examples, blocks, or media.
Explain the route aloud in ordinary language: “We can now explain this, but
we still cannot explain that; the next topic gives us the missing idea.”
If that connection needs an untaught concept, add it before the dependent
topic. A learner's familiarity with adjacent subjects does not establish
familiarity with this subject's basic objects or questions.

Read the selected subject guide through `skills/subject/SKILL.md` and its
assigned teacher's `SOUL.md` when one exists. Use them to check the topic
boundaries, prerequisites, and sources. Leave the explanation, examples,
practice, and media choices to lesson design.

## Validate and enroll

Validate the plan and enroll it in the same turn:

```bash
python3 skills/course-design/scripts/validate_course.py <course.json>
python3 skills/learner-tracking/scripts/learner_state.py init <learner>
python3 skills/learner-tracking/scripts/learner_state.py enroll <learner> --course <course.json>
```

Use the learner's name, or `learner` when no name was given. Confirm that the
canonical workspace at `learners/<learner>/courses/<course-id>/course.json`
exists before handing the topic to lesson design. Do not stop at saving a plan
under `outputs/`; enroll it so lesson design can use the canonical course.
Enrollment finishes the plan, not the current lesson. Continue to lesson
design in this turn; do not describe the course as ready to view yet.

Briefly explain the course goal, agreed depth and duration, and current topic.
Explain how the current topic fits the course goal. Use enough detail to make
the plan understandable without reciting its fields.

## Hand the current topic to lesson design

After enrollment, continue with [lesson-design](../lesson-design/SKILL.md).
Read its [teaching reference](../lesson-design/references/lesson-design.md) and
load the current topic, teacher, subject guidance, and learner evidence. When
using the context loader, switch to lesson authoring explicitly:

```bash
python3 skills/learning-orchestrator/scripts/assemble_context.py --subject <subject> \
  --learner <learner> --course-id <course-id> --mode lesson
```

Lesson design must develop and review the explanation before publishing a
ready lesson. Do not turn a topic title or concept list into short paragraphs
and call that the lesson. Its finished content belongs in
`lessons/<lesson-id>/lesson.json`. Course design stops authoring at the plan;
the same host continues the work under lesson design's instructions. Enrollment
alone does not permit a teaching render: `render_viewer.py` rejects a current
lesson whose `design_receipt`
is missing or whose `course_fingerprint` differs from the enrolled `course.json`.

## Show the finished lesson

After the current lesson is published as `ready`, ask “Do you want to see the course now?”
unless the learner already requested or approved it. On yes, use
[course-viewer](../course-viewer/SKILL.md) and render:

```bash
python3 skills/course-viewer/scripts/render_viewer.py learners/<learner>/courses/<course-id>
```

Return the `portal/` link with the current lesson to open. An explicit request
for only an outline may render with `--outline-only` before a lesson exists;
identify that result as the course outline, not a ready lesson. For teaching, complete the
lesson-design draft, review checklist, receipt, and `ready` publish before
delivering the page. Re-render after changes to the lesson or its artifacts.
Revising a taught lesson means setting it back to `draft`, editing blocks,
writing a new `designed_at` and `course_fingerprint`, and re-publishing as `ready`.

If lesson design discovers that the topic needs another concept, source, or
different place in the sequence, revise that part of the course first. Record
the reason in `revision_notes`, validate and enroll the revised plan, then
return to lesson design. Changing a lesson's explanation or media does not
require a course revision.

Use learner evidence to revise future topics as the course progresses. Preserve
stable IDs and record why the sequence, sources, or scope changed, following
[course-contract.md](references/course-contract.md).
