<p align="center">
  <img src="assets/hero.png" alt="GNOS" width="100%" />
</p>

# GNOS

A file-based teaching harness. A learning skill chooses a teacher, designs the
right-sized course, teaches from the learner's current understanding, and keeps
usable evidence for the next session.

The Markdown files are the operating context for a file-capable LLM. Python
scripts handle records, course checks, PDFs, and animations. GNOS does not run
a model server or listen to conversations in the background.

## Install as a Codex plugin

The `codex` branch packages GNOS as a Codex plugin and bundles Excalidraw and
Pinepaper MCP servers. Add the GitHub marketplace and install GNOS:

```bash
codex plugin marketplace add madhvantyagi/Gnos --ref codex
codex plugin add gnos@gnos
```

Start a new Codex task after installation so the GNOS skills and bundled MCP
tools enter the new task's tool inventory. Users do not configure either MCP
separately. Excalidraw uses its hosted endpoint. Pinepaper is fetched by `npx`
on first use with its browser runtime and then runs locally in headless mode.
GNOS loads its detailed visual references only when the lesson needs a diagram
or animation.

## Start learning

Open this repository in your LLM workspace and ask:

> Use GNOS to teach me why gradient descent subtracts the gradient. Begin with
> my current question; build a course only if we need one.

The repository's `AGENTS.md` points to [the learning skill](skills/learning/SKILL.md).
For a host that needs explicitly supplied context:

```bash
python3 skills/learning/scripts/assemble_context.py --subject math
```

Give that output to the host along with your question. The host needs file-read
and script-execution tools to persist learning or produce artifacts.

## Teachers and subjects

| Subject | Teacher | Teaching emphasis |
| --- | --- | --- |
| [Mathematics](skills/subject/subjects/math.md) | [Ben Waston](teachers/math/SOUL.md) | Find the last defensible step; test conditions |
| [Physics](skills/subject/subjects/physics.md) | [Mira Sen](teachers/physics/SOUL.md) | Predict, model, measure; check units and limits |
| [History](skills/subject/subjects/history.md) | [Elias Ward](teachers/history/SOUL.md) | Provenance, evidence, chronology, interpretation |
| [Biology](skills/subject/subjects/biology.md) | [Leena Rao](teachers/biology/SOUL.md) | Mechanisms across levels; predict perturbations |
| [Economics](skills/subject/subjects/economics.md) | [Nadia Vale](teachers/economics/SOUL.md) | Choices, assumptions, comparisons, empirical claims |
| [Computer science](skills/subject/subjects/computer-science.md) | [Theo Park](teachers/computer-science/SOUL.md) | Trace state; explain contracts, invariants, failures |

Teacher SOUL files contain identity, judgment, tone, good and bad examples, and
drift checks. Subject files contain subfields, prerequisites, resources, and
connections to the other skills.

## Skill library

| Skill | Responsibility |
| --- | --- |
| [Learning](skills/learning/SKILL.md) | Entry point, pacing, context selection, teaching loop |
| [Subject](skills/subject/SKILL.md) | Subject routes, bridges, teacher and resource selection |
| [Course design](skills/course-design/SKILL.md) | Research, prerequisite order, chapters, outcomes, assessments |
| [Understanding user learning](skills/understanding-user-learning/SKILL.md) | Separate memory categories, observed evidence, resumption, final curriculum |
| [PDF](skills/pdf/SKILL.md) | Markdown/README to PDF, local images, math, typography, visual review |
| [Manim](skills/manim-voice-animation-skill/SKILL.md) | Storyboards, narration cues, animations, subtitles, render checks |

Every script lives in its owning skill. References are loaded when needed;
the whole library does not need to enter every lesson's context.

## Learning that carries into the next chat

Pick a stable learner ID when you want local tracking. These commands illustrate
using `alex`; they do not imply an existing learner profile:

```bash
python3 skills/understanding-user-learning/scripts/learner_state.py init alex
python3 skills/understanding-user-learning/scripts/learner_state.py enroll alex \
  --course examples/courses/gradient-descent/course.json
python3 skills/understanding-user-learning/scripts/learner_state.py record alex \
  --event output/session.json
python3 skills/learning/scripts/assemble_context.py --subject math \
  --learner alex --course-id gradient-descent
```

The host writes `session.json` from actual learner work using the
[evidence contract](skills/understanding-user-learning/references/evidence.md).
An explanation by the teacher is exposure; it is not evidence that the learner
can solve a new problem. Independent success and later recall are distinguished.

Each update refreshes separate memories for profile, courses, taught topics,
teaching observations, and next steps. The enrolled plan becomes a chapter
curriculum under `learners/alex/memory/courses/gradient-descent/CURRICULUM.md`.
Complete the course when the learner chooses to finish:

```bash
python3 skills/understanding-user-learning/scripts/learner_state.py \
  complete-course alex --course-id gradient-descent
```

The final curriculum includes topic names, teachers, assessments, sources, and
actual coverage. Untaught or untested material remains marked. Files under
`learners/`, personal `courses/`, and `output/` are ignored by Git. Same learner
ID and filesystem are required for resumption; unrelated chats are not imported.

## PDFs and animations

Core teaching and memory scripts use standard-library Python. Optional media
setup stays inside a project environment:

```bash
uv venv .venv --python 3.11
uv pip install --python .venv/bin/python -r skills/pdf/requirements.txt
uv pip install --python .venv/bin/python \
  -r skills/manim-voice-animation-skill/requirements.txt
```

Manim may also require platform Cairo/Pango dependencies. LaTeX is needed for
`MathTex` templates; the supplied gradient animation uses text and needs no TeX.

Convert a Markdown lesson, including its local image-model outputs:

```bash
.venv/bin/python skills/pdf/scripts/markdown_to_pdf.py \
  examples/lessons/gradient/README.md -o output/pdf/gradient-lesson.pdf
```

Generate an offline animation preview:

```bash
.venv/bin/python skills/manim-voice-animation-skill/scripts/voice_synthesizer.py \
  --storyboard examples/animations/gradient/storyboard.json \
  --out output/gradient/silent --silent
GNOS_MANIFEST=output/gradient/silent/timing_manifest.json \
  .venv/bin/python skills/manim-voice-animation-skill/scripts/render_pipeline.py \
  render examples/animations/gradient/scene.py GradientStep \
  -q l -o output/gradient/preview.mp4
```

Omit `--silent` and write to `output/gradient/audio` to synthesize narration
through Edge TTS, then render using that manifest. Local MP3 recordings are also
supported. Provider availability is external to GNOS. Cue playback attaches
speech to the actual scene timeline and writes subtitles; a silent preview is
always labeled as such.

## Examples and checks

- [Tiny chain-rule plan](examples/courses/chain-rule/course.json)
- [Multi-subject gradient-descent course](examples/courses/gradient-descent/course.json)
- [Course research ledger](examples/courses/gradient-descent/RESEARCH.md)
- [Illustrated Markdown lesson](examples/lessons/gradient/README.md)
- [Animation storyboard](examples/animations/gradient/storyboard.json)
- [Architecture](docs/design.md)

```bash
python3 skills/learning/scripts/validate_harness.py
python3 -m unittest discover -s tests -p test_core.py -v
.venv/bin/python -m unittest discover -s tests -v
```

The tests cover persistence, course revisions, scoped resumption, PDF content,
and media operations. They do not certify teaching effectiveness. Teacher quality
should be evaluated against real learner responses and revised from evidence.
