<p align="center">
  <img src="assets/hero.png" alt="GNOS" width="100%" />
</p>

<h1 align="center">GNOS</h1>

<p align="center">
  <strong>Learning is built in layers. GNOS gives each layer its own skill.</strong><br>
  <sub>File-based · Markdown governs · Python handles records and media · no model server</sub>
</p>

## The pillars

People don't learn from playlists. They learn when someone finds the exact
point where reasoning stopped, teaches in a voice that fits, tracks real
attempts, and adapts the moment it hurts. GNOS turns each of those into a
dedicated skill:

| Pillar | Skill | Solves |
| --- | --- | --- |
| **Start** | [learning-orchestrator](skills/learning-orchestrator/SKILL.md) | Reads the request, routes it, teaches from the actual break in reasoning. |
| **Build** | [course-design](skills/course-design/SKILL.md) | Researches sources, writes the plan, records every route change. |
| **Track & adapt** | [learner-tracking](skills/learner-tracking/SKILL.md) | Records attempts and stuck points; the course changes in real time. |
| **Choose** | [subject](skills/subject/SKILL.md) | Picks the subject and the teacher persona that fits the problem. |
| **Show** | [manim-voice-animation](skills/manim-voice-animation/SKILL.md) · [pdf](skills/pdf/SKILL.md) | Turns words into narrated animations, videos, images, diagrams, handouts. |

## Teachers with souls

Every teacher is a persona with a `SOUL.md` — identity, voice, and judgment
under pressure. A math topic gets the math soul; a history doubt never hears
an invented panel. The right teacher is assigned per topic, in real time.

## Media comes from MCP servers

Visuals are not decoration. Narrated animations, architecture diagrams, and
images from image models are produced by connected MCP servers, then
registered into the lesson that needs them.

## Quick start

```bash
python3 skills/learning-orchestrator/scripts/validate_harness.py
python3 -m unittest discover -s tests
```

<p align="center">
  <sub>Start at <a href="skills/learning-orchestrator/SKILL.md">the orchestrator</a> · design in <a href="docs/design.md">docs/design.md</a></sub>
</p>
