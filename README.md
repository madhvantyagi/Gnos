<p align="center">
  <img src="assets/hero.png" alt="GNOS" width="100%" />
</p>

<h1 align="center">GNOS</h1>

<p align="center">
  <strong>A learning harness that designs your course, teaches in real time, and adapts as you learn.</strong>
</p>

<p align="center">
  <a href="#what-it-is">What it is</a> &nbsp;·&nbsp;
  <a href="#what-you-can-do">What you can do</a> &nbsp;·&nbsp;
  <a href="#subjects">Subjects</a> &nbsp;·&nbsp;
  <a href="#how-it-works">How it works</a>
</p>

## What it is

GNOS is a file-based teaching harness operated by a capable LLM. A learning skill picks the right teacher, designs a course sized to your question, and teaches from where you actually are — then keeps usable evidence for next time.

No model server. No background listener. Markdown governs teaching, Python handles records and media.

## What you can do

**Answer a focused doubt** — split a small topic into the few useful ideas and
teach it without manufacturing a permanent syllabus.

**Design a living course** — when the goal genuinely spans many topics or the
learner wants sustained study, build a researched table of contents and author
only the current lesson in detail.

**Learn adaptively** — GNOS follows your understanding in real time and adjusts pace, depth, and style.

**Route the right expertise** — topics name their subject, teaching skills, and
an optional teacher persona. Cross-subject courses can use a supporting subject
without turning the lesson into a panel discussion.

**Fetch what matters** — the harness pulls only the content you need for this step.

**Track evidence, not attendance** — attempts, independent success, retrieval,
and next steps stay separate from the curriculum's planning state.

**Practice properly** — exercises tuned to your level, scored on independent success not exposure.

**See it, not just read it** — diagrams, simulations, video, and images when they reveal more than text.

## Subjects

<a href="skills/subject/subjects/math.md">Mathematics</a> · <a href="skills/subject/subjects/physics.md">Physics</a> · <a href="skills/subject/subjects/history.md">History</a> · <a href="skills/subject/subjects/biology.md">Biology</a> · <a href="skills/subject/subjects/economics.md">Economics</a> · <a href="skills/subject/subjects/computer-science.md">Computer Science</a> · <a href="skills/subject/subjects/accounting.md">Accounting</a> · <a href="skills/subject/subjects/artificial-intelligence.md">Artificial Intelligence</a> · <a href="skills/subject/subjects/business.md">Business</a> · <a href="skills/subject/subjects/psychology.md">Psychology</a> · <a href="skills/subject/subjects/chemical-engineering.md">Chemical Engineering</a> · <a href="skills/subject/subjects/political-science.md">Political Science</a>

Teachers live in <a href="teachers/">teachers/</a> · subject guides in <a href="skills/subject/subjects/">skills/subject/subjects/</a> · design notes in <a href="docs/design.md">docs/design.md</a>

## How it works

1. **Understand** — establish the learner's goal, prior evidence, constraints,
   and whether the request needs one focused explanation or a persistent course.
2. **Map** — for a course, inspect suitable sources and create a version-2 table
   of contents: chapters, topics, dependencies, teaching routes, exercises, and
   one current frontier. Later chapters can remain provisional.
3. **Teach in chat** — compose the next lesson from explanations, examples,
   exercises, diagrams, simulations, animation, or video. Chat remains the main
   relationship; generated material supports the lesson instead of fragmenting it.
4. **Observe and adapt** — record what the learner actually attempted, derive
   progress from that evidence, and revise future topics only when the evidence
   or goal changes.

## Course files

A tracked learner's course lives at:

```text
learners/<learner-id>/courses/<course-id>/
├── course.json        # living table of contents and current frontier
├── lessons/           # validated lesson compositions, created gradually
├── artifacts/         # final diagrams, videos, PDFs, simulations, and files
├── exercises/         # learner-facing exercise state and submissions
└── portal/             # generated visual companion when enabled
```

`course.json` is not a transcript and its `current`, `planned`, and
`provisional` values are curriculum states—not claims of mastery. Learner events
remain in `learners/<learner-id>/state.json`; the enrollment stores the course
path, revision, and fingerprint so stale state cannot be updated silently.

Examples under `examples/courses/` are fictional and safe to inspect. Validate a
course or lesson directly with:

```bash
python3 skills/course-design/scripts/validate_course.py path/to/course.json
python3 skills/course-design/scripts/validate_lesson.py path/to/lesson.json \
  --course path/to/course.json
```

Existing version-1 plans remain readable, but new courses use schema version 2.
Use the learner-state migration command explicitly when adopting an old plan;
validation happens before any learner record is changed:

```bash
python3 skills/understanding-user-learning/scripts/learner_state.py \
  --root learners migrate-courses <learner-id>
```

<p align="center">
  <sub>Start in any LLM workspace that can read files. See <a href="skills/learning/SKILL.md">skills/learning/SKILL.md</a> for the entry point.</sub>
</p>
