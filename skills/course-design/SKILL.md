---
name: course-design
description: "Design and revise a course's progression, outcomes, sources, and representations. Record depth and duration, validate and enroll course.json, then hand the current topic to lesson-design. Does not author lessons."
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

Read [course-contract.md](references/course-contract.md) and write
`course.json`. Organize chapters and topics so their outcomes build toward the
course goal. Identify the current topic and leave uncertain later topics
provisional.

Read the selected subject guide through `skills/subject/SKILL.md` and its
assigned teacher's `SOUL.md` when one exists. Use the subject's representation
profile with [representation-choices.md](references/representation-choices.md)
to choose the topic's representations. Give each a specific teaching purpose,
including the text and exercises needed to connect media into a lesson.
Leave the detailed explanations, examples, and block order to lesson design.

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
Describe what the selected representations will help the learner understand.
Use enough detail to make the plan understandable without reciting its fields.

## Show the course and hand off the lesson

Follow the orchestrator's course-viewer step: ask “want to see the course now?”
unless the learner has already requested or approved it. On yes, render the
page and return its `portal/` link with what to open:

```bash
python3 skills/course-viewer/scripts/render_viewer.py learners/<learner>/courses/<course-id>
```

The contents page can render before any lessons exist. Use
[lesson-design](../lesson-design/SKILL.md) to develop the enrolled current
topic. That skill writes the lesson, coordinates production, registers checked
artifacts, and publishes the finished lesson. Re-render the page after a new
lesson or artifact is published. Course design does not write `lesson.json`,
production briefs, or block content.

If lesson design discovers a missing concept or an unsuitable representation,
revise that part of the course first. Record the reason in `revision_notes`,
validate and enroll the revised plan, then return to lesson design. More
explanation within an existing representation does not require a course change.

Use learner evidence to revise future topics as the course progresses. Preserve
stable IDs and record why the sequence, sources, or scope changed, following
[course-contract.md](references/course-contract.md).
