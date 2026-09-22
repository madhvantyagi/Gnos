---
name: course-viewer
description: "Show an enrolled course and its lessons. Use lesson-design to author or repair the current lesson before delivering teaching; render published content and serve the local page with saved exercises."
---

# Course viewer

Render the enrolled course and its published lessons. The HTML page can be
read on its own; the local course server saves exercises to JSON and reveals
answers after submission. Math uses KaTeX. Cream editorial page: top bar with GNOS + tabs, hero
with giant title + field metadata, curriculum list + topic details.

Use this skill whenever a course plan is created, enrolled, or
changed — even with zero lessons. A fresh course still renders its
contents table, sources, and representation plan. Re-render after
every new lesson, video, image, or simulation. Render only from the
enrolled workspace at `learners/<learner>/courses/<course-id>`,
never from a blueprint `outputs/` file.


## lesson-design should have been used before using this skill

**Make sure that you have used [lesson-design](../lesson-design/SKILL.md) skill to design the lesson for the current in way better manner and then use the course-viewer to view the lesson , after you done using the lesson-design skill. then you can smoothly use course-viewer**




## Complete the lesson handoff before showing teaching

Read the current topic and its published lesson. Course design supplies the
outline; [lesson-design](../lesson-design/SKILL.md) supplies the teaching.
If the current topic has no ready lesson, use that skill and its
[lesson design reference](../lesson-design/references/lesson-design.md) to
author it before delivering a lesson page. If the learner reports a shallow
lesson, use the same reference to repair its explanation and examples even
when its file is already marked `ready`.

Do not write lesson content from `course.json` inside this viewer workflow.
The renderer does not call a model or invoke skills: the host must perform
the handoff, review the lesson, and publish it. Use `--require-current-lesson`
when delivering teaching so a missing lesson cannot silently produce only an
outline. Omit that flag for an explicitly requested outline or contents preview.

## Render

```bash
.venv/bin/python skills/course-viewer/scripts/render_viewer.py learners/alex/courses/motion --require-current-lesson
```
  
The script reads `course.json`, published lessons, and the artifact
manifest, then writes `portal/index.html` inside the course folder.

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

- cream paper (#F6F1E7), near-black ink, teal links (#155E63),
  ochre labels (#8A6D3B), plum state/title (#5E2B4D), thin dividers
- topbar: GNOS logo left, tabs center (Overview, Lessons, Exercises,
  Sources, Artifacts with teal underline for active), All courses → right
- hero: giant condensed title + Rev, mono subtitle; right meta block
  with FIELD / LEVEL / RESOURCES behind a vertical divider
- overview is Curriculum (left) + Topic details (right):
  chapters as "Chapter 01 + Title", topics as numbered rows with
  Current (navy) / Planned (plum) + › chevron; selected row has
  textured grey fill; clicking a row updates Topic details
  (eyebrow, plum title, Outcome / State / Formats / Evidence / Sources)
- lessons show the topic's representation plan as chips: manim,
  image, simulation, text (kept as `chip manim` hooks, hidden in
  curriculum rows, visible in Lessons). A chip turns ready
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

The topic's `representations` in `course.json` say which parts need
which skill. The page shows that plan as chips, so the learner sees
what is coming. The lesson coordinator registers every artifact with
`manage_artifact.py` before rendering; only `ready` artifacts appear.

## Rules

- Render only public fields in the initial page. Keep success criteria,
  tolerances, and private review notes private. The local server may return
  an authored solution only after a saved attempt and explicit Show answer.
- The page references media files in the workspace; it never copies
  or downloads them. Missing files get a visible note, never a crash.
- Re-render whenever the plan, a lesson, or the manifest changes.
- Math renders with KaTeX (CDN, the one network exception). Lesson text
  must already delimit math as LaTeX (`$...$`, `$$...$$`); the renderer
  preserves delimited LaTeX and equation blocks exactly. Legacy undelimited
  ASCII text has a limited compatibility converter; never rely on it when
  authoring. Follow [math notation](../lesson-design/references/math-notation.md).
  Body prose is serif; monospace is only for code.
- If enroll or render fails, say plainly what failed and fix it that
  turn. Never silently skip the page.
- If the learner did not answer the show question, ask again on the
  next course turn.
- The page is for local viewing. Host it only for the enrolled learner.
