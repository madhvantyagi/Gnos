<p align="center">
  <img src="assets/hero.png" alt="GNOS" width="100%" />
</p>

<h1 align="center">GNOS</h1>

<p align="center">
  <strong>A learning harness that designs your course, teaches in real time, and adapts as you learn.</strong><br>
  <sub>File-based · Markdown governs · Python handles records and media · no model server</sub>
</p>

## What is it

GNOS is a **Codex plugin**: a bundle of skills that teach, plus MCP servers
that produce the visuals. It also runs standalone — drop the repo into any
LLM workspace that can read files. There is no background tutor, model API,
or automatic assessment service behind these files.

## How it works

1. The **orchestrator** reads the request and decides: answer, lesson, or course.
2. The **course skill** researches real sources and writes the route.
3. The **subject skill** picks the teacher persona; teaching happens in chat.
4. The **learner skill** tracks attempts and adapts the route in real time.
5. The **media skills** produce visuals through MCP servers; the viewer
   renders them on one static course page.

## The pillars

People don't learn from playlists. They learn when someone finds the exact
point where reasoning stopped, teaches in a voice that fits, tracks real
attempts, and adapts the moment it hurts. Each pillar is its own skill:

| Pillar | Skill | Solves |
| --- | --- | --- |
| **Start** | [learning-orchestrator](skills/learning-orchestrator/SKILL.md) | Reads the request, routes it, teaches from the actual break in reasoning. |
| **Build** | [course-design](skills/course-design/SKILL.md) | Researches sources, writes the plan, records every route change. |
| **Track & adapt** | [learner-tracking](skills/learner-tracking/SKILL.md) | Records attempts and stuck points; the course changes in real time. |
| **Choose** | [subject](skills/subject/SKILL.md) | Picks the subject and the teacher persona that fits the problem. |
| **Show** | [manim-voice-animation](skills/manim-voice-animation/SKILL.md) · [image-gen](skills/image-gen/SKILL.md) · [pdf](skills/pdf/SKILL.md) | Turns words into narrated animations, images, diagrams, handouts. |
| **View** | [course-viewer](skills/course-viewer/SKILL.md) | Renders the course into one static page: videos, images, simulations, exercises. |

## Teachers with souls

Every teacher is a persona with a `SOUL.md` — identity, voice, and judgment
under pressure. A math topic gets the math soul; a history doubt never hears
an invented panel. The right teacher is assigned per topic, in real time.

## Media comes from MCP servers

Visuals are not decoration. Narrated animations, architecture diagrams, and
images from image models are produced by connected MCP servers, then
registered into the lesson that needs them.

## Use it

Start at the orchestrator, then validate everything:

```bash
python3 skills/learning-orchestrator/scripts/validate_harness.py
python3 -m unittest discover -s tests
```

Design and check a course, then render the learner's page:

```bash
python3 skills/course-design/scripts/validate_course.py course.json
python3 skills/course-viewer/scripts/render_viewer.py learners/<id>/courses/<course-id>
```

A learner's course lives at `learners/<learner-id>/courses/<course-id>/` —
`course.json` is the living route, `lessons/` grows one at a time,
`artifacts/` holds the finished media. Learner evidence stays separate in
`state.json`; progress is derived from independent success, never exposure.

## Subjects

Math · Physics · History · Biology · Economics · Computer Science ·
Accounting · Artificial Intelligence · Business · Psychology ·
Chemical Engineering · Political Science

<p align="center">
  <sub>Start at <a href="skills/learning-orchestrator/SKILL.md">the orchestrator</a> · <a href="docs/flow.html">how it flows</a> · design in <a href="docs/design.md">docs/design.md</a></sub>
</p>
