<p align="center">
  <img src="assets/hero.png" alt="GNOS" width="100%" />
</p>

<div align="center">

**A teaching harness that turns your coding agent into a teacher — it designs the course, teaches the lesson, and adapts to you in real time.**

[![GitHub stars](https://img.shields.io/github/stars/madhvantyagi/Gnos?style=social)](https://github.com/madhvantyagi/Gnos)
[![License: MIT](https://img.shields.io/badge/License-MIT-2F5D50.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.2.0-2F5D50)]()
[![Codex plugin](https://img.shields.io/badge/plugin-Codex-2F5D50)](https://github.com/madhvantyagi/Gnos/tree/codex)

File-based · Markdown governs teaching · Python handles records and media · no model server

</div>

---

## What is GNOS?

GNOS is a **teaching harness**: a bundle of skills, scripts, and MCP servers
that converts a general-purpose coding agent into a personal tutor. It does
not wrap an API around a chatbot. It gives the model structure — a system for
teaching, not just a system prompt.

Give GNOS a goal, and it:

- **designs a course** from real sources — university syllabi, open textbooks,
  documentation, and papers — then sizes the route to how deep and how long
  you want to go
- **teaches one lesson at a time** from the exact point where your reasoning
  breaks, in the voice of a teacher persona matched to the subject
- **tracks and adapts in real time** — every attempt, every stuck point, and
  every misconception is recorded, and the course reshapes itself around them
- **produces real visuals** — narrated animations, images, diagrams, PDFs, and
  simulations — instead of wall-of-text explanations

It runs as a **Codex plugin**, and it also runs standalone: drop the repository
into any LLM workspace that can read files. There is no background tutor, no
model API, and no hidden service. Everything is files on your machine, and
your learner records stay yours.

---

## Why teaching with AI is a hard problem

Frontier models carry immense knowledge in their weights — but they are
designed to *perform actions and accomplish tasks*, not to teach. Teaching
is a different skill: it needs a sequence, a diagnosis of where the learner
actually broke, a voice that fits, and evidence of understanding, not just
exposure. GNOS exists to force that immense knowledge into teachable,
learnable patterns through skills, scripts, and MCP servers.

Four problems make AI a bad teacher out of the box. GNOS attacks each one
directly:

| The problem | How GNOS solves it |
| --- | --- |
| **AI language** — models default to a flat assistant voice, no matter the subject. | Persona instructions can change model output dramatically — [SOUL.md](https://github.com/madhvantyagi/SOUL.md) (my earlier project, ~400 stars) proved that. Every GNOS teacher is a persona with a `SOUL.md`: identity, voice, and judgment under pressure. |
| **Course synchronization** — a course is state: where you are, what comes next, what you already proved. | The harness maintains multiple JSON records — `course.json` for the living syllabus, `state.json` for learner evidence — so progress, topics, and history survive across sessions. |
| **Detecting learning patterns** — "watched the lesson" is not "understood the lesson". | A dedicated learner skill separates exposure from assisted success from independent success, analyzes mistakes, and adjusts exercises and lessons in real time. |
| **Visual representation** — complex ideas die in walls of text. | GNOS can produce narrated Manim animations, generated images, diagrams, PDFs, and simulations — each dispatched to the concept where that medium actually helps. |

---

## How it works

Every turn starts at the **orchestrator** and moves through one small loop:

1. The **orchestrator** reads the request and decides what it needs — a quick
   answer, one lesson, or a full course.
2. The **course skill** researches real sources and writes the route, sized to
   the depth and duration you agreed on.
3. The **subject skill** selects the lead subject and the teacher persona that
   fits the problem.
4. The **lesson skill** builds the current topic block by block; the teaching
   itself happens live in chat.
5. The **learner skill** records attempts and stuck points — and the course
   adapts in real time.
6. The **media skills** produce visuals through MCP servers, and the
   **course viewer** renders everything onto one clean course page.

> Want the full picture? See [how it flows](docs/flow.html) and the
> [design document](docs/design.md).

### The skills

Each pillar of the system is its own skill, loaded only when the turn needs it:

| Pillar | Skill | Solves |
| --- | --- | --- |
| **Start** | [learning-orchestrator](skills/learning-orchestrator/SKILL.md) | Reads the request, routes it, teaches from the actual break in reasoning. |
| **Build** | [course-design](skills/course-design/SKILL.md) | Researches sources, writes the plan, records every route change. |
| **Lesson** | [lesson-design](skills/lesson-design/SKILL.md) | Builds one lesson from the current topic, block by block. |
| **Track & adapt** | [learner-tracking](skills/learner-tracking/SKILL.md) | Records attempts and stuck points; the course changes in real time. |
| **Choose** | [subject](skills/subject/SKILL.md) | Picks the subject and the teacher persona that fits the problem. |
| **Show** | [manim-voice-animation](skills/manim-voice-animation/SKILL.md) · host image generation · [pdf](skills/pdf/SKILL.md) | Turns words into narrated animations, images, diagrams, and handouts. |
| **View** | [course-viewer](skills/course-viewer/SKILL.md) | Renders the course into one static page: videos, images, simulations, exercises. |

---

## Teachers with souls

Every teacher in GNOS is a persona with a `SOUL.md` — identity, voice, and
judgment under pressure. A math topic gets the math soul. A history doubt
never hears an invented panel of experts: **one teacher leads the turn**, and
a supporting subject contributes only the bridge it can actually verify.

Supplied teachers: **mathematics, physics, computer science, biology,
economics, history** — assigned per topic, in real time.

---

## Use it

**[Install the Codex plugin](https://github.com/madhvantyagi/Gnos/tree/codex) · or [clone and start at the orchestrator](skills/learning-orchestrator/SKILL.md) — no sign-up, no ID required. Just ask: *"Teach me recursion"*.**

---

## Where this is going

GNOS today is a foundation — and the ceiling is much higher. It can improve
by a large factor in almost every direction:

- **Voice and transcription** — spoken lessons, and listening back to what you
  actually said
- **Richer visuals** — interactive 3D, a stronger simulation framework, tighter
  manim-to-narration pipelines
- **More subjects and teachers** — each new `SOUL.md` and subject guide widens
  coverage
- **Stronger learning models** — spaced repetition and longer-horizon memory
  across courses
- **Open evaluation** — measuring real learning outcomes, not engagement

If one of these excites you, jump in — the system is deliberately modular, and
each direction is a contained skill.

---

## Contributing

This harness is organized so a contribution stays small: skills own their
decisions, teachers own their voice, and subjects own their scope. Start at
[`AGENTS.md`](AGENTS.md) for the operating rules and
[`docs/design.md`](docs/design.md) for the architecture.

Validate your changes before opening a PR:

```bash
python3 skills/learning-orchestrator/scripts/validate_harness.py
python3 -m unittest discover -s tests -v
```

PRs, issues, new teacher souls, and new subject guides are all welcome.

Built for self-learners, by a self-learner — cheers to everyone who learns on
their own and leans on AI to chase the hard topics anyway.

---

## License

[MIT](LICENSE) © 2026 [Madhvan Tyagi](https://github.com/madhvantyagi)

<p align="center">
  <sub>If GNOS helps you learn something hard, star the repo —
  <a href="https://github.com/madhvantyagi/Gnos">⭐ it helps more people find it</a></sub>
</p>
