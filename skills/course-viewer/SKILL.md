---
name: course-viewer
description: Render a learner's course into one static web page that shows lessons, videos, images, simulations, sources, exercises, and resources.
---

# Course viewer

Turn a course workspace into one static page the learner reads.
No app, no build step, no external libraries. One self-contained
HTML file with monospace type on a dark ink page.

Use this skill after a course exists and lessons or artifacts were
added. Re-render after every new lesson, video, image, or simulation.

## Render

```bash
python3 skills/course-viewer/scripts/render_viewer.py learners/alex/courses/motion
```

Or pass the course folder directly. Add `--summary <file>` to show
learner progress beside the topics. The script reads `course.json`,
published lessons, and the artifact manifest, then writes
`portal/index.html` inside the course folder.

Open it locally:

```bash
cd learners/alex/courses/motion
python3 -m http.server 8080
# visit http://localhost:8080/portal/
```

## The look

The design lives in [references/example.html](references/example.html).
Copy that look exactly: centered column, monospace font, old ink style,
ruled tables, small-caps headers. Colors always mean the same thing:

- gold = watch (videos, animations, audio)
- green = generated (diagrams, images, simulations)
- rust = resources (PDFs, documents, files)
- mauve = exercises and questions
- red = the current topic row
- blue = planned, grey = provisional, dimmed = retired or out-of-scope

Lessons appear in plan order. A lesson shows its explanation, bullets,
equations, code, videos, images, sandboxed simulations, source cards,
and exercise prompts. Arrow keys step between lessons; the page also
has prev/next links.

## Compatibility with other skills

The viewer does not know about any single skill. It renders whatever
is registered in the course artifact manifest, whatever made it:

- Manim videos and narrated animations -> `watch` section, inline `<video>`
- images made by image models -> `generated` section, inline `<img>`
- interactive simulations (HTML) -> sandboxed `<iframe>`
- PDFs and documents -> `resources` section, open links
- MCP server data lands here the same way: publish the artifact through
  the manifest first, then re-render

Register every artifact with the course-design skill
(`manage_artifact.py`) before rendering. Only `ready` artifacts appear.

## Rules

- Render only public fields. Never print success criteria, answers,
  tolerances, solutions, or private review notes.
- The page references media files in the workspace; it never copies
  or downloads them. Missing files get a visible note, never a crash.
- Re-render whenever the plan, a lesson, or the manifest changes.
- The page is for local viewing. Host it only for the enrolled learner.
