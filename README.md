<p align="center">
  <img src="assets/hero.png" alt="GNOS artwork" width="100%" />
</p>

<p align="center">
  <strong>Turn your coding agent into a teacher that builds a course around you.</strong>
</p>

<p align="center">
  <a href="https://github.com/madhvantyagi/Gnos/stargazers"><img src="https://img.shields.io/github/stars/madhvantyagi/Gnos?style=social" alt="Star GNOS on GitHub" /></a>
  &nbsp;·&nbsp;
  <a href=".codex-plugin/plugin.json">Codex plugin</a>
  &nbsp;·&nbsp;
  <a href="#get-started">Claude Code & other agents</a>
  &nbsp;·&nbsp;
  <a href="LICENSE">MIT license</a>
</p>

## What is GNOS?

GNOS is a teaching harness made of skills, scripts, and visual tools. Tell it what you want to learn and how deep you want to go. It uses course materials such as university syllabi, textbooks, and documentation to plan a route, then teaches the next useful lesson.

As you work, GNOS records what you tried, where your reasoning broke, and what you could do independently. It uses that evidence to adjust upcoming lessons and exercises. The course grows with you.

## Why does learning with AI still feel hard?

Frontier models know a great deal, but a good answer is only one part of teaching. Learning a large subject also takes a coherent route, a diagnosis of mistakes, and a way to make abstract ideas visible. GNOS gives a coding agent that structure.

| The problem | What GNOS does |
| --- | --- |
| **The voice feels generic** | Subject-specific teachers use `SOUL.md` files to guide their explanations and judgment. This builds on my earlier [SOUL.md project](https://github.com/madhvantyagi/SOUL.md). |
| **Lessons lose the thread** | A living course plan and learner records keep topics, prior attempts, and the next step together across sessions. |
| **A correct answer gets mistaken for understanding** | Learner tracking distinguishes seeing an explanation, solving with help, and solving independently; the next exercise responds to the evidence. |
| **Everything becomes text** | GNOS can choose diagrams, images, simulations, narrated animations, or PDF handouts when that format helps explain the idea. Visual tools and media dependencies vary by environment. |

## Get started

**Codex:** Use the [Codex plugin](.codex-plugin/plugin.json), then ask it to teach you a topic.

**Claude Code or another agent that can read local files:** Clone the repo, open it as your workspace, and start with:

> Read `AGENTS.md`, then `skills/learning-orchestrator/SKILL.md`. Help me learn [topic].

For a longer course, tell GNOS your goal, starting point, desired depth, and how much time you have. For a single question, just ask it. [See the teaching entry point](skills/learning-orchestrator/SKILL.md).

## Help it grow

There is room for better visuals, transcription and spoken lessons, more subjects, and stronger ways to measure learning. If you use AI to teach yourself difficult things, try GNOS and [share what worked or broke](https://github.com/madhvantyagi/Gnos/issues). Contributions are welcome.

Built by a self-learner, for self-learners. If it helps you learn something hard, [star the repo](https://github.com/madhvantyagi/Gnos/stargazers) so others can find it.
