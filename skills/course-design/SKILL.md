---
name: course-design
description: "Design and revise a course's goal, progression, prerequisites, and sources. Record depth and duration, validate and enroll course.json, then hand the current topic to lesson-design."
---

# Course design

Use this skill when a learning goal needs several sessions or a sequence of
prerequisites. Answer a small local question directly in chat. For a course,
design the progression from the learner's starting point to the agreed goal.
Lesson design develops each topic into a complete lesson.

## Establish depth and duration

Before designing, establish how deeply the learner wants to study and how
much time they have. Ask for whichever information they have not already
provided. Record both in `course.json`:

- `depth`: `survey` for understanding the central ideas and connections,
  `working` for applying them independently, or `mastery` for justifying
  methods and examining their limits.
- `length`: the learner's intended duration, such as one session, six weeks,
  or a term.

Use these answers to choose the scope, pace, research, and useful media.
A shorter course should cover fewer ideas well rather than abbreviating every
explanation.

## Research and plan the course

Read [course-research.md](references/course-research.md). Consult accessible
books, course materials, or documentation to check prerequisites, definitions,
and suitable exercises. Record what you actually opened and which sections
the course will use.

When a current topic or its blocking prerequisite might have a Khan Academy
resource, send lesson design to check [the Khan Academy skill](../khan-academy/SKILL.md).
Record the verified item as a course source, add its ID to that topic's
`resource_ids`, add the Khan skill route to the topic's `skill_routes`, and use
representation kind `khan` when the plan names one; leave clip selection and
placement to lesson design. Do not expand the course around a broad Khan match
when the learner needs one bridge.

Read [course-contract.md](references/course-contract.md) and write
`course.json`. Organize chapters and topics so their outcomes build toward the
course goal. Identify the current topic and leave uncertain later topics
provisional.

For every new topic, declare its assessment prompt, readable `success_criteria`,
and stable `assessment.criteria` IDs as specified in the course contract.
Name observable capabilities such as deriving a recurrence or justifying a
method; a depth label or correct number cannot stand in for that work. Preserve
legacy assessments when resuming. Adopt criterion IDs through an explicit
reviewed plan revision; never convert old concept labels into claimed passes.

Read the selected subject guide through `skills/subject/SKILL.md` and its
assigned teacher's `SOUL.md` when one exists. Use its matching subfield to
check the starting case, difficult distinction, and evidence the topic needs.
Leave media, worked examples, and block order to lesson design using
[representation choices](../lesson-design/references/representation-choices.md).
Keep existing representation plans binding until explicitly revised; new plans
need not prescribe media before the lesson's reasoning is developed.

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

Briefly explain the course goal, agreed depth and duration, and current topic.
Describe what the current topic will help the learner understand.
Use enough detail to make the plan understandable without reciting its fields.

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
ready lesson. Do not turn topic outcomes or representation purposes into short
paragraphs and call that the lesson. Its finished content belongs in
`lessons/<lesson-id>/lesson.json`. Course design stops authoring at the plan;
the same host continues the work under lesson design's instructions.


## Show the finished lesson

**Ask "Do you want to see the course now?" unless the learner already requested or
approved it. This question controls opening the page, not whether lesson
design runs. On yes, use [course-viewer](../course-viewer/SKILL.md) and render**

```bash
python3 skills/course-viewer/scripts/render_viewer.py learners/<learner>/courses/<course-id> --require-current-lesson
```

Return the `portal/` link with the current lesson to open. An explicit request
for only an outline may render before a lesson exists; identify that result
as the course outline. For teaching, complete the lesson handoff before
delivering the page. Re-render after changes to the lesson or its artifacts.

If lesson design discovers a missing concept, source, or topic boundary,
revise that part of the course. Record the reason in `revision_notes`, validate
and enroll the revised plan, then return to lesson design. A media change stays
with lesson design unless it changes a binding representation plan.

Use learner evidence to revise future topics as the course progresses. Preserve
stable IDs and record why the sequence, sources, or scope changed, following
[course-contract.md](references/course-contract.md).

## Advance from reviewed evidence

Before changing an enrolled course's current topic, follow
[exercise review](../learner-tracking/references/exercise-review.md). Review
saved work and the current lesson, let lesson-design repair explanation gaps,
and record a current `advance` or explicit learner `skip` receipt through
`manage_interaction.py review-lesson`. Plan writing and enrollment reject an
unreviewed topic transition. A `practice` or `repair-prerequisite` decision
keeps the frontier in place while you develop the required work. Then revise
and enroll the plan and hand the selected topic to lesson-design.
