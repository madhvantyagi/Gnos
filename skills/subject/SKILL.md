---
name: subject
description: Select the lead subject, supporting bridges, teacher, sources, and subject-specific representations for a learning goal.
---

# Subject routing

Select the subject from the capability the learner wants to build, not from the
first technical noun in the request. A biological dataset may need a statistics
lesson. A programming example may expose an algebra gap. A historical price
series still needs historical source judgment.

## Route the learning job

1. State the learner's intended action: derive, predict, implement, interpret,
   compare, diagnose, or argue from evidence.
2. Name the field that decides whether that action is correct. That is the lead
   subject.
3. Check the selected guide's prerequisites and distinctions. Add a supporting
   subject only for a named bottleneck.
4. Keep one lead teacher. A supporting teacher supplies one bounded bridge and
   returns the lesson to the lead subject.
5. Read the guide's representation profile before planning course media.
6. Record the selected subject guide and every producing skill in the topic's
   `skill_routes`.

Do not route by vocabulary alone. “Gradient” does not make every optimization
question mathematics; the domain subject owns what the objective and variables
mean. “Code” does not make a biological inference computer science; CS owns the
implementation while biology owns the claim.

## Subjects and teachers

| Subject ID | Guide | Lead teacher |
| --- | --- | --- |
| math | [Mathematics](subjects/math.md) | `teachers/math/SOUL.md` |
| physics | [Physics](subjects/physics.md) | `teachers/physics/SOUL.md` |
| history | [History](subjects/history.md) | `teachers/history/SOUL.md` |
| biology | [Biology](subjects/biology.md) | `teachers/biology/SOUL.md` |
| economics | [Economics](subjects/economics.md) | `teachers/economics/SOUL.md` |
| computer-science | [Computer science](subjects/computer-science.md) | `teachers/computer-science/SOUL.md` |
| accounting | [Accounting](subjects/accounting.md) | Use an existing teacher only for a named bridge |
| artificial-intelligence | [Artificial intelligence](subjects/artificial-intelligence.md) | Use an existing teacher only for a named bridge |
| business | [Business](subjects/business.md) | Use an existing teacher only for a named bridge |
| chemical-engineering | [Chemical engineering](subjects/chemical-engineering.md) | Use an existing teacher only for a named bridge |
| political-science | [Political science](subjects/political-science.md) | Use an existing teacher only for a named bridge |
| psychology | [Psychology](subjects/psychology.md) | Use an existing teacher only for a named bridge |

Do not invent a persona for a subject without a teacher. Set `teacher` to
`null`, or assign an existing teacher only when that teacher owns a real
supporting method. The subject still owns its evidence and interpretation.

## Use the selected guide

Read the selected subject file in full. Its subfield map is a starting
structure, not a complete taxonomy. For an unlisted specialty, inspect a
primary, official, or academic source before designing a sustained course.
Do not imply that an introductory textbook covers every advanced branch.

Read a linked deep reference only when the guide sends you there for detailed
prerequisites, sources, examples, or visual patterns. Do not preload every
subject reference.

Use `python3 skills/subject/scripts/resources.py --subject physics` to list
curated sources. Add `--query vectors` to narrow the list. A catalog entry or
landing page is not proof that the needed section was inspected.

## Bridges

- AI and machine learning: artificial intelligence owns model and evaluation
  claims; CS owns implementation; math owns the needed linear algebra,
  probability, derivatives, or optimization.
- Biophysics: biology owns the mechanism when the question is biological;
  physics owns forces, diffusion, energy, or measurement for the named bridge.
- Economic history: history owns chronology and source context; economics owns
  an explicitly conditional model. Neither substitutes for the other's
  evidence.
- Quantitative biology, psychology, economics, or political science: the domain
  owns the question and interpretation; math owns the statistical tool.
- Chemical engineering: chemical engineering owns the system boundary and
  process assumptions; physics, math, and CS support transport, equations, and
  simulation.
- Business and accounting: business owns the operating decision; accounting
  owns recognition and reconciliation; economics owns the stated market model.

Carry the learner's last sound step, notation, units, and unresolved question
through every bridge. Do not stage a panel discussion.

## Choose subject-specific representations

The subject guide answers “What must be visible in this field?” The course
representation guide answers “Which medium reveals it with the least extra
machinery?” Read both, in that order.

| Workflow | What it produces | Route |
| --- | --- | --- |
| Subject teacher | Explanation, derivation, code, bullets, and exercises | This skill and the selected subject guide |
| Image generation | Still illustration or labeled image | `skills/image-gen/SKILL.md` |
| Manim voice animation | Narrated rendered motion with subtitles | `skills/manim-voice-animation/SKILL.md` |
| PDF | Rendered and inspected handout or source packet | `skills/pdf/SKILL.md` |
| Excalidraw MCP | Quick inspectable CS relationship or boundary diagram | [Excalidraw workflow](references/excalidraw.md) through the CS guide |
| Pinepaper MCP | Polished vector, interactive relation, or animated SVG | [Pinepaper workflow](references/pinepaper.md) and a linked subject reference |
| Simulation | Learner-controlled graph or model | Self-contained HTML registered through `manage_artifact.py` |

The MCP references are workflows under the subject route, not standalone lesson
skills. The topic still declares the subject skill and selected subject guide.
Add a producing `SKILL.md` route when ImageGen, Manim, or PDF will create a
file.

Apply these tests:

- Use text for exact claims, definitions, dates, derivations, code contracts,
  and short comparisons.
- Use a still for structure, spatial relations, labels, boundaries, maps, or
  source comparison.
- Use motion only when time, transformation, propagation, feedback, or ordered
  state change is the object.
- Use a simulation only when the learner should change an input and predict the
  result.
- Use narration when spoken timing coordinates meaningful visual change. Use
  source audio or video only when listening or viewing is part of the evidence.
- Use a PDF for review or a stable source packet, not as a substitute for the
  live lesson.

One idea gets one primary medium. Do not recreate the same diagram in ImageGen,
Excalidraw, Pinepaper, and Manim. Do not add media to meet a quota. Do not omit
an earned graph, map, diagram, or control merely to keep the lesson short.

For a course, write the approved choices into the topic's
`representations` list. Then read
`skills/course-design/references/representation-choices.md`. Each delegated
lesson worker receives the selected subject guide and only the deep workflow
reference its block needs.

## Source discipline

Read [source-use.md](references/source-use.md) for source selection and
downloads. The lead subject decides what counts as evidence. A simulation,
generated image, or explanatory animation is a model unless it directly and
accurately presents a cited source.
