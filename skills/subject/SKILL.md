---
name: subject
description: Select GNOS subjects, prerequisite bridges, teaching representations, resources, and teachers for a learning goal.
---

# Subject routing

Choose the subject from the capability the learner wants. A biological dataset
can require a statistics lesson; a programming example can expose an algebra
gap. Select a lead subject, then add only the bridge that the task requires.

| Subject ID | Reference | Teacher |
| --- | --- | --- |
| math | [Mathematics](subjects/math.md) | `teachers/math/SOUL.md` |
| physics | [Physics](subjects/physics.md) | `teachers/physics/SOUL.md` |
| history | [History](subjects/history.md) | `teachers/history/SOUL.md` |
| biology | [Biology](subjects/biology.md) | `teachers/biology/SOUL.md` |
| economics | [Economics](subjects/economics.md) | `teachers/economics/SOUL.md` |
| computer-science | [Computer science](subjects/computer-science.md) | `teachers/computer-science/SOUL.md` |

The subject-only expansion guides are available for [accounting](subjects/accounting.md),
[artificial intelligence](subjects/artificial-intelligence.md), [business](subjects/business.md),
[psychology](subjects/psychology.md), [chemical engineering](subjects/chemical-engineering.md),
and [political science](subjects/political-science.md). They do not add teacher personas
or course-contract subjects; use an existing teacher when a lesson needs one.

Read the selected subject file. Its subfield map is a starting structure, not a
complete taxonomy. For an unlisted specialty, research a suitable primary or
academic source before designing a deep course. Do not imply that a supplied
introductory textbook covers every advanced branch.

Subject files stay short. Read a linked subject reference only when the current
topic needs its deeper prerequisites, examples, sources, or visual patterns.
Do not preload references for an ordinary explanation.

Use `python3 skills/subject/scripts/resources.py --subject physics` to list
curated sources. `--query vectors` narrows by topic. Entries include verification
status and format notes; a landing page is not a downloaded PDF.

## Bridges

- AI / machine learning: artificial intelligence leads model and evaluation questions;
  computer science supports implementation; math supports linear algebra,
  probability, derivatives, and optimization.
- Biophysics: the learner's question decides the lead; connect mechanisms to
  forces, diffusion, energy, or measurement at the appropriate scale.
- Economic history: history owns source and context claims; economics supplies
  an explicitly conditional model. Neither establishes the other's evidence.
- Quantitative biology or economics: teach the data question first, then the
  statistical tool it needs. Use common `math.*` concept IDs for shared ideas.

One teacher speaks. Supporting teachers contribute a named explanation or
module, not decorative dialogue. Carry notation and the learner's last sound
step across the handoff.

## Choose the representation by the task

A still diagram helps inspect structure; an animation helps inspect change;
runnable code tests behavior; a PDF supports review. No subject requires media
by default.

- For an advanced vector diagram, interactive relation, or animated SVG in
  computer science, mathematics, physics, economics, or political science,
  read [the Pinepaper workflow](references/pinepaper.md) and the selected
  subject's linked reference.
- For a quick inspectable computer-science canvas, read
  [the Excalidraw workflow](references/excalidraw.md).
- For a narrated rendered lesson, use
  `skills/manim-voice-animation-skill/SKILL.md`; for a handout, use
  `skills/pdf/SKILL.md`.

Choose one primary medium. Do not create the same diagram in multiple tools
unless comparison or export requirements justify it.

For source selection and downloads, read
[references/source-use.md](references/source-use.md).
