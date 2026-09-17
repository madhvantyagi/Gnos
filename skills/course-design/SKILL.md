---
name: course-design
description: Make and update the course plan: ask depth and length, search sources, write course.json, publish formal lessons, and record what changed in the route.
---

# Course design

Make a course only when the goal needs it. Most questions do not.

Answer in chat when the learner has one small target,
for example "why can we divide by x here?". Make a course when
the goal takes several sessions or needs steps in order,
for example "learn mechanics over six weeks".

## How it works

0. **Ask depth and length before designing.** When a course is
   justified, ask the learner how deep and how long they want to go:

   - `depth`: `survey` (see the landscape, connect the ideas),
     `working` (be able to use the ideas on real problems), or
     `mastery` (defend, derive, and teach the ideas back).
   - `length`: one session, a few weeks, a term, or longer.

   The answers decide the size of the route: how many topics, how
   much research, how fine to cut each lesson, and how much media
   is earned. Record both in `course.json` and follow them during
   research — a survey does not need two contrasting textbooks, and
   a term-long mastery route should not be compressed into five chat
   turns.

1. **Search.** Read [course-research.md](references/course-research.md).
   Look in books, course sites, and docs. Take definitions,
   step order, and exercise ideas. Write down what you opened.
   Scale the search to the agreed depth and length.

2. **Write the plan.** Read [course-contract.md](references/course-contract.md).
   Write `course.json` with title, goal, `depth`, `length`, steps,
   sources, and one current step. Say which source each step uses.
   Split each topic into its representations: which part needs manim
   motion, which needs a still image or vector diagram, which needs a
   simulation, which stays text. Read
   [representation-choices.md](references/representation-choices.md)
   for the rules. Check the plan with:

   ```bash
   python3 skills/course-design/scripts/validate_course.py <course.json>
   ```

3. **Teach with a formal lesson, then let the learner skill adapt.**
   A taught topic's default record is its formal lesson file. Author
   `lesson.json` for the current step — read
   [lesson-contract.md](references/lesson-contract.md) — validate it,
   and publish it into the enrolled workspace:

   ```bash
   python3 skills/course-design/scripts/validate_lesson.py lesson.json \
     --course learners/<learner>/courses/<course-id>/course.json
   python3 skills/course-design/scripts/course_workspace.py publish \
     learners/<learner>/courses/<course-id> --lesson lesson.json
   ```

   Publish `draft` while the lesson is developing, `ready` when the
   learner should see it. Teach directly in chat while the learner is
   actively interacting (a live question, a small doubt, a quick fix);
   the chat back-and-forth stays in the learner record, and the formal
   file still captures the topic for the portal. The learner skill
   watches what happens and records it. When it tells you the learner is stuck
   or a source failed, update `course.json`: add the new source, insert
   a missing step, split, or move `current` forward. Write each change
   in `revision_notes` with the date, what changed, and what problem
   the learner had. See `skills/learner-tracking/SKILL.md` for the
   learner record and its adaptive step.

4. **Make each representation, then show the course.** Dispatch each
   topic representation to its skill: `manim` -> manim-voice-animation,
   `image` -> image-gen, `diagram` -> image-gen or pinepaper/excalidraw
   per the subject skill, `simulation` -> a small self-contained HTML
   file registered with `manage_artifact.py`, `pdf` -> pdf,
   `text`/`exercise` -> the subject teacher. Every skill that produces a
   file registers it in the artifact manifest. Do not stop at
   `outputs/course.json`: enroll the plan that same turn. Use the
   learner's name, or the default `learner` when no name was given —
   `init` and `enroll` both default to it:

   ```bash
   python3 skills/learner-tracking/scripts/learner_state.py init <learner>
   python3 skills/learner-tracking/scripts/learner_state.py enroll <learner> --course <course.json>
   ```

   Then ask this exact question and wait for the answer:
   "want to see the course now?" On yes, render the page and reply with
   the `portal/` link and what to click:

   ```bash
   python3 skills/course-viewer/scripts/render_viewer.py learners/<learner>/courses/<course-id>
   ```

   Re-render after every new lesson, video, image, or simulation — even
   when the course has zero lessons, the contents page still renders.

You only need `validate_course.py`, `validate_lesson.py`, and
`course_workspace.py publish` for normal work. Other files in
`scripts/` are for the portal and old plans.
