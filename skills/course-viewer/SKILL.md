---
name: course-viewer
description: Render and show the learner's course page. Use when the learner says see, show, or open my course, or after course.json is created, enrolled, or changed; render portal/index.html and return the link.
---

# Course viewer

Turn a course workspace into one static page the learner reads.
No app, no build step, no external libraries. One self-contained
HTML file. White, minimal, full screen: a left sidebar with tabs
and the lesson list, a main column with the lesson content.

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

Add `--summary <file>` to show learner progress beside the topics.
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

- white page, near-black text, one accent color, no gradients
- left sidebar: course title, tabs (Overview, Lessons, Exercises,
  Sources, Artifacts), lesson list with done / current / locked dots
- main column scrolls; sticky header shows the course and prev/next
- lessons show the topic's representation plan as chips: manim,
  image, simulation, text. A chip turns ready when its artifact is
  registered
- videos, images, and sandboxed simulations render full width inside
  rounded frames, captions below, never overlapping
- arrow keys step between lessons

## Compatibility with other skills

The viewer renders whatever is registered in the course artifact
manifest, whatever made it:

- manim-voice-animation videos -> watch, inline `<video>`
- image-gen images -> generated, inline `<img>`
- interactive simulations (HTML) -> sandboxed `<iframe>`
- pdf handouts and documents -> resources, open links

The topic's `representations` in `course.json` say which parts need
which skill. The page shows that plan as chips, so the learner sees
what is coming. Register every artifact with the course-design skill
(`manage_artifact.py`) before rendering; only `ready` artifacts appear.

## Rules

- Render only public fields. Never print success criteria, answers,
  tolerances, solutions, or private review notes.
- The page references media files in the workspace; it never copies
  or downloads them. Missing files get a visible note, never a crash.
- Re-render whenever the plan, a lesson, or the manifest changes.
- If enroll or render fails, say plainly what failed and fix it that
  turn. Never silently skip the page.
- If the learner did not answer the show question, ask again on the
  next course turn.
- The page is for local viewing. Host it only for the enrolled learner.
