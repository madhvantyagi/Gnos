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
  <a href=".claude-plugin/plugin.json">Claude Code plugin</a>
  &nbsp;·&nbsp;
  <a href="LICENSE">MIT license</a>
</p>

## What is GNOS?

GNOS is a teaching harness made of skills, scripts, and visual tools. Tell it what you want to learn. For a course, it asks how deep you want to go and how much time you have, uses course materials such as university syllabi, textbooks, and documentation to plan a route, then builds the first lesson. Subagents make its lesson blocks; GNOS reviews and joins them before asking if you want to see the course.

As you work, GNOS records what you tried, where your reasoning broke, and what you could do independently. It uses that evidence to adjust upcoming lessons and exercises. The course grows with you.

## Star history

<p align="center">
  <a href="https://www.star-history.com/?repos=madhvantyagi%2FGnos&amp;type=date">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=madhvantyagi%2FGnos&amp;type=date&amp;theme=dark" />
      <img src="https://api.star-history.com/chart?repos=madhvantyagi%2FGnos&amp;type=date" alt="GNOS GitHub stars over time" width="100%" />
    </picture>
  </a>
</p>

## Study your course in a browser

Just ask GNOS to show your course in the browser. It routes the request to the `course-viewer` skill, which renders the curriculum and current lesson as a study page. Open a topic to read its lesson, work through exercises, and follow its sources and learning materials.

<p align="center">
  <img src="assets/course-viewer-rl-to-grpo.png" alt="GNOS course viewer showing the RL to GRPO curriculum and selected topic details" width="100%" />
</p>

<p align="center"><em>Browse the curriculum and open a topic to study it in the course viewer.</em></p>

A true slideshow can't run inside a README, so here is the closest thing — click each frame to expand it:

<details>
<summary><strong>Frame 1 · Simulation</strong> — run route policies on the building grid</summary>
<br />
<p align="center">
  <img src="assets/lesson-simulation.png" alt="Grid simulation where the learner runs courier route policies" width="680" />
</p>
</details>

<details>
<summary><strong>Frame 2 · Lesson video</strong> — watch a narrated lesson block</summary>
<br />
<p align="center">
  <img src="assets/lesson-video.png" alt="Rendered lesson video on the Bellman equation" width="680" />
</p>
</details>

## Why does learning with AI still feel hard?

Frontier models know a great deal, but a good answer is only one part of teaching. Learning a large subject also takes a coherent route, a diagnosis of mistakes, and a way to make abstract ideas visible. GNOS gives a coding agent that structure.

| The problem | What GNOS does |
| --- | --- |
| **The voice feels generic** | Subject-specific teachers use `SOUL.md` files to guide their explanations and judgment. This builds on my earlier [SOUL.md project](https://github.com/madhvantyagi/SOUL.md). |
| **Lessons lose the thread** | A living course plan and learner records keep topics, prior attempts, and the next step together across sessions. |
| **A correct answer gets mistaken for understanding** | Learner tracking distinguishes seeing an explanation, solving with help, and solving independently; the next exercise responds to the evidence. |
| **Everything becomes text** | GNOS can choose diagrams, images, simulations, narrated animations, or PDF handouts when that format helps explain the idea. Visual tools and media dependencies vary by environment. |

## Get started

### Use GNOS as a plugin

1. **Codex:** Install GNOS from this repository:

   ```sh
   codex plugin marketplace add madhvantyagi/Gnos --ref main
   codex plugin add gnos@gnos
   ```

   Start a new task: “Use the GNOS learning-orchestrator skill to teach me [topic].”

2. **Claude Code:** Clone the repository and load GNOS for the session:

   ```sh
   git clone https://github.com/madhvantyagi/Gnos.git
   cd Gnos
   claude --plugin-dir .
   ```

   Run `/gnos:learning-orchestrator Teach me [topic]` in Claude Code.

### Use GNOS with another agent

1. **Any agent that reads local files:** Clone the repo, open it as your workspace, and send:

   ```
   Read `AGENTS.md`, then `skills/learning-orchestrator/SKILL.md`. Help me learn [topic].
   ```

2. **Shape the course:** For a longer course, also give your goal, starting point, desired depth, and time. For a single question, just ask it.

## Help it grow

GNOS grows through its users. If it helps you learn something hard, [share what worked or broke](https://github.com/madhvantyagi/Gnos/issues) and [star the repo](https://github.com/madhvantyagi/Gnos/stargazers) so others can find it.
