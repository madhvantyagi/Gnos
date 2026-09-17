---
name: course-design
description: "Make and update the course plan: ask depth and length, search sources, write course.json, publish formal lessons, and record what changed in the route."
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
   Read the selected subject file through `skills/subject/SKILL.md` before
   choosing media. Its representation profile states what learners in that
   field need to inspect.
   Split each topic into its representations: which part needs manim
   motion, which needs a still image or vector diagram, which needs a
   simulation, which stays text. Read
   [representation-choices.md](references/representation-choices.md)
   for the rules. Check the plan with:

   ```bash
   python3 skills/course-design/scripts/validate_course.py <course.json>
   python3 skills/learner-tracking/scripts/learner_state.py init <learner>
   python3 skills/learner-tracking/scripts/learner_state.py enroll <learner> --course <course.json>
   ```

   Enroll the validated plan in the same turn. Use the learner's name, or the
   default `learner` when no name was given. Do not stop at
   `outputs/course.json`; the canonical course workspace must exist before the
   lesson skeleton is published.

3. **Build the lesson from the course plan.** A taught topic's default
   record is its formal lesson file. Read
   [lesson-contract.md](references/lesson-contract.md). Author an ordered
   `lesson.json` skeleton for the current topic. Every block must point to one
   of that topic's approved representations through `representation_id`.
   Do not introduce a new concept, medium, or skill route in the lesson.

   Validate and publish the skeleton as `draft` before producing files. This
   gives every artifact a real lesson ID:

   ```bash
   python3 skills/course-design/scripts/validate_lesson.py lesson.json \
     --course learners/<learner>/courses/<course-id>/course.json
   python3 skills/course-design/scripts/course_workspace.py publish \
     learners/<learner>/courses/<course-id> --lesson lesson.json
   ```

   Add a complete `production` brief to every block that will be delegated.
   When multi-agent execution is available, assign each file-producing block
   to one worker. Also delegate a text or code block when it needs separate
   research or a long worked construction. Keep short explanations,
   transitions, and notation with the coordinator.

   Give each worker only its block, its course representation, the selected
   subject guidance, shared continuity rules, and required source material.
   Workers write to separate output paths. They return a completed block
   fragment or artifact plus its registration payload. They never edit
   `course.json`, `lesson.json`, or `manifest.json`.

   Run blocks with no dependencies in parallel. A block listed in
   `depends_on_block_ids` starts only after those earlier blocks return. The
   coordinator checks every result, merges block fragments, registers artifacts
   one at a time, validates the completed lesson, and publishes it as `ready`.
   If a worker needs a different concept, medium, or purpose, stop that block
   and revise `course.json` first.

   Teach directly in chat while the learner is actively interacting. The
   formal lesson still captures the topic for the portal. The learner skill
   records the exchange. When evidence changes the route, revise `course.json`
   and state the change and reason in `revision_notes`. See
   `skills/learner-tracking/SKILL.md` for the adaptive step.

4. **Route each representation, then show the course.** Dispatch each topic
   representation to its skill: `manim` -> manim-voice-animation,
   `image` -> image-gen, `diagram` -> image-gen or pinepaper/excalidraw
   per the subject skill, `simulation` -> a small self-contained HTML
   file the coordinator registers with `manage_artifact.py`, `pdf` -> pdf,
   `text`/`exercise` -> the subject teacher. Every skill that produces a
   file returns a registration payload to the coordinator. Only the
   coordinator updates the artifact manifest. Then ask this exact question and
   wait for the answer:
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
