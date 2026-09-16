---
name: course-design
description: Make and update the course plan: search sources, write course.json, and record what changed in the route.
---

# Course design

Make a course only when the goal needs it. Most questions do not.

Answer in chat when the learner has one small target,
for example "why can we divide by x here?". Make a course when
the goal takes several sessions or needs steps in order,
for example "learn mechanics over six weeks".

## How it works

1. **Search.** Read [course-research.md](references/course-research.md).
   Look in books, course sites, and docs. Take definitions,
   step order, and exercise ideas. Write down what you opened.

2. **Write the plan.** Read [course-contract.md](references/course-contract.md).
   Write `course.json` with title, goal, steps, sources, and one
   current step. Say which source each step uses. Split each topic
   into its representations: which part needs manim motion, which needs
   a still image, which needs a simulation, which stays text. Read
   [representation-choices.md](references/representation-choices.md)
   for the rules. Check the plan with:

   ```bash
   python3 skills/course-design/scripts/validate_course.py <course.json>
   ```

3. **Teach, then let the learner skill adapt.** Teach the current
   step in chat. The learner skill watches what happens and records
   it. When it tells you the learner is stuck or a source failed,
   update `course.json`: add the new source, insert a missing step,
   split, or move `current` forward. Write each change in
   `revision_notes` with the date, what changed, and what problem
   the learner had. See `skills/learner-tracking/SKILL.md`
   for the learner record and its adaptive step.

4. **Make each representation, then show the course.** Dispatch each
   topic representation to its skill: `manim` -> manim-voice-animation,
   `image`/`diagram` -> image-gen, `simulation` -> a small self-contained
   HTML file registered with `manage_artifact.py`, `pdf` -> pdf,
   `text`/`exercise` -> the subject teacher. Every skill that produces a
   file registers it in the artifact manifest. After lessons or
   artifacts exist, render the learner's page:

   ```bash
   python3 skills/course-viewer/scripts/render_viewer.py learners/<learner>/courses/<course-id>
   ```

   Re-render after every new lesson, video, image, or simulation.

[lesson-contract.md](references/lesson-contract.md) is old and optional.
Teach in chat. Use a formal lesson file only when the portal asks for it.

You only need `validate_course.py` for normal work. Other files in
`scripts/` are for the portal and old plans.
