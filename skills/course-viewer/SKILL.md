---
name: course-viewer
description: Render and show the learner's course page. Use when the learner says see, show, or open my course, or after course.json is created, enrolled, or changed; render portal/index.html and return the link.
---

# Course viewer

Turn a course workspace into one static page the learner reads.
No app, no build step. One self-contained page + one CDN exception for math (KaTeX). Cream editorial page: top bar with GNOS + tabs, hero
with giant title + field metadata, curriculum list + topic details.

Use this skill whenever a course plan is created, enrolled, or
changed — even with zero lessons. A fresh course still renders its
contents table, sources, and representation plan. Re-render after
every new lesson, video, image, or simulation. Render only from the
enrolled workspace at `learners/<learner>/courses/<course-id>`,
never from a blueprint `outputs/` file.

## Render

```bash
python3 skills/course-viewer/scripts/render_viewer.py learners/alex/courses/motion
```
  
The script reads `course.json`, published lessons, and the artifact
manifest, then writes `portal/index.html` inside the course folder.

Open it locally:

```bash
cd learners/alex/courses/motion
python3 -m http.server 8080
# visit http://localhost:8080/portal/
```

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

- Render only public fields. Never print success criteria, answers,
  tolerances, solutions, or private review notes.
- The page references media files in the workspace; it never copies
  or downloads them. Missing files get a visible note, never a crash.
- Re-render whenever the plan, a lesson, or the manifest changes.
- Math renders with KaTeX (CDN, the one network exception). Lesson text
  must already delimit math as LaTeX (`$...$`, `$$...$$`); the renderer
  additionally normalises bare ASCII idioms (`R^(m x n)` →
  `\mathbb{R}^{m \times n}`, `P^(-1)` → `P^{-1}`) as a safety net, never
  as the authorised notation. Body prose is serif; monospace is only
  for code.
- If enroll or render fails, say plainly what failed and fix it that
  turn. Never silently skip the page.
- If the learner did not answer the show question, ask again on the
  next course turn.
- The page is for local viewing. Host it only for the enrolled learner.
