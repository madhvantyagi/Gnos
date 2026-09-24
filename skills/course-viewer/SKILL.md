---
name: course-viewer
description: "Show an enrolled course and its lessons. Use lesson-design to author or repair the current lesson before delivering teaching; render published content and serve the local page with saved exercises."
---

# Course viewer

Render the enrolled course and its published lessons. The HTML page and its
neighboring `assets/` directory can be read locally; the course server saves exercises to JSON and reveals
answers after submission. Math uses KaTeX. Cream editorial page: top bar with GNOS + tabs, hero
with giant title + field metadata, curriculum list + topic details.

Use this skill when the learner asks to see the course or answers yes after
the current lesson is ready. Re-render after a changed lesson or artifact
before giving a page link. A learner who explicitly asks for only
the outline may see its contents and sources through `--outline-only`.
For an explicit context load at this step, use `assemble_context.py --mode
viewer --subject <subject> --learner <learner> --course-id <course-id>`.
Render only from the
enrolled workspace at `learners/<learner>/courses/<course-id>`,
never from a blueprint `outputs/` file.

## Complete the lesson handoff before showing teaching

Read the current topic and its published lesson. Course design supplies the
outline; [lesson-design](../lesson-design/SKILL.md) supplies the teaching.
If the current topic has no ready lesson, use that skill and its
[lesson design reference](../lesson-design/references/lesson-design.md) to
author it before delivering a lesson page. If the learner reports a shallow
lesson, set its `publication` back to `draft`, use the same reference to
repair its explanation and examples, write a new `design_receipt`, and
re-publish as `ready` — do not edit a `ready` file in place.

Do not write lesson content from `course.json` inside this viewer workflow.
The renderer does not call a model or invoke skills: the host must perform
the handoff, review the lesson, and publish it. A normal render requires a
`ready` lesson for the current
topic whose `design_receipt.course_fingerprint` equals the enrolled
`course.json` fingerprint and whose `design_receipt.review` is `pass`.
It fails otherwise with instructions to run lesson design first. Use
`--outline-only` only for an explicitly requested outline or contents preview.
If rendering fails, do not link an earlier `portal/index.html` or say the
course is ready to view.
The local server also checks the current lesson before starting and whenever
it serves the page, so an old page cannot be used after the course moves on.
The receipt checks a recorded handoff and course match. It cannot prove that
the host read the skill or that the explanation is good; review the lesson.

## Render

```bash
.venv/bin/python skills/course-viewer/scripts/render_viewer.py learners/alex/courses/motion
```
  
The script reads `course.json`, published lessons, and the artifact
manifest, then writes `portal/index.html` and copies the bundled KaTeX,
syntax-highlighting, and math-font assets to `portal/assets/`.

Open it locally:

```bash
.venv/bin/python skills/course-viewer/scripts/serve_course.py learners/alex/courses/motion --port 8080
# visit http://127.0.0.1:8080/portal/
```

Use this server for exercise interaction. A plain file or generic static server
cannot write a learner response to the course workspace. Save answer persists
an attempt under `submissions/<exercise-id>/<attempt-id>.json`; only a
successful save enables Show answer. The solution is fetched on that explicit
request and the reveal is recorded separately from the learner's response.

## The layout

The design lives in [references/example.html](references/example.html).
Copy that look exactly:

- cream paper (#F6F4EE), near-black ink, teal links (#155E63),
  ochre labels (#8A6D3B), plum state/title (#5E2B4D), thin dividers
- topbar: GNOS logo left, tabs center (Overview, Lessons, Exercises,
  Sources, Artifacts with teal underline for active), All courses → right
- hero: giant condensed title + Rev, mono subtitle; right meta block
  with FIELD / LEVEL / RESOURCES behind a vertical divider
- overview is Curriculum (left) + Topic details (right):
  chapters as "Chapter 01 + Title", topics as numbered rows with
  Current (navy) / Planned (plum) + › chevron; selected row has
  textured grey fill; clicking a row updates Topic details
  (eyebrow, plum title, Subtopics / State / Formats / Evidence / Sources)
- lessons show their actual block formats as chips: manim,
  image, simulation, text (kept as `chip manim` hooks, hidden in
  curriculum rows, visible in Lessons). Older course plans still show their
  planned formats. A chip turns ready
  (`chip manim ready`) when its artifact is registered
- videos, images, and sandboxed simulations render full width inside
  rounded frames, captions below, never overlapping
- arrow keys step between lessons; lesson hooks (`#tabs`, `#lesson-list`,
  `.lesson`, `#prev-link` / `#next-link`) stay intact

## Compatibility with other skills

The viewer renders whatever is registered in the course artifact
manifest, whatever made it:

- manim-voice-animation videos -> watch, inline `<video>`
- host-generated images -> generated, inline `<img>`
- interactive simulations (HTML) -> sandboxed `<iframe>`
- pdf handouts and documents -> resources, open links

The lesson blocks show which forms were used. Older courses can still show
their planned formats. The lesson coordinator registers every artifact with
`manage_artifact.py` before rendering; only `ready` artifacts appear.

## Rules

- Render only public fields in the initial page. Keep success criteria,
  tolerances, and private review notes private. The local server may return
  an authored solution only after a saved attempt and explicit Show answer.
- The page references learner media files in the workspace; it never copies
  or downloads them. Missing files get a visible note, never a crash.
- Re-render whenever the plan, a lesson, or the manifest changes.
- Math renders with bundled KaTeX, including local fonts. Lesson text
  must already delimit math as LaTeX (`$...$`, `$$...$$`); the renderer
  preserves delimited LaTeX and equation blocks exactly. Legacy undelimited
  ASCII text has a limited compatibility converter; never rely on it when
  authoring. Follow [the lesson contract](../lesson-design/references/lesson-contract.md).
  Body prose is serif. Code blocks use semantic `<pre><code>` markup and the
  bundled highlighter; the code remains readable when highlighting cannot run.
- When reviewing a changed lesson, inspect rendered math in an explanation,
  an equation block, and an exercise prompt. Switch between Lessons and
  Exercises, then inspect a worked answer after an authorized save and reveal.
  Check the DOM for KaTeX output rather than only checking TeX strings in the
  HTML. A visible math-load warning means the page is not ready to deliver.
- If enroll or render fails, say plainly what failed and fix it that
  turn. Never silently skip the page.
- If the learner did not answer the show question, ask again on the
  next course turn.
- The page is for local viewing. Host it only for the enrolled learner.
