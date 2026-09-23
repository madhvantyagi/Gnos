---
name: subject
description: Select the lead subject, supporting bridges, teacher, sources, and field-specific teaching guidance for a learning goal.
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
5. Read the guide's matching subfield section when planning the course and lesson.
   Course design uses its starting point and likely confusions to order ideas.
   Lesson design uses its suggested views to explain those ideas.
6. Record the selected subject guide in the topic's `skill_routes`. Lesson
   design records media skill routes in `lesson.json`.

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

## Use subject guidance in the lesson

The subject guide says what the learner must notice, work out, or check in
this field. Lesson design uses that advice to choose explanations, examples,
practice, and media. Read the guide before choosing blocks. A lesson may use
several forms when each helps with a different step of the same idea.
Every ready lesson needs at least two distinct teaching forms. The subject
guide helps choose a useful pair; it does not assign a fixed pair to every
topic. Exercise and feedback blocks are practice, not one of the two forms.
There is no upper limit when more forms deepen the explanation.
For the current topic, carry three decisions into lesson design: the concrete
starting case, the distinction most likely to need explanation, and what the
learner could inspect or change to understand it. Use the matching subfield
section for its research checks and representation choices. Adapt them to the
learner's question. Read deeper references when that section leaves a
prerequisite, mechanism, or evidence question unresolved.

| Workflow | What it produces | Route |
| --- | --- | --- |
| Subject teacher | Explanation, derivation, code, bullets, and exercises | This skill and the selected subject guide |
| Image generation | Still illustration or labeled image | The host's existing image-generation skill or tool, following the instructions below |
| Manim voice animation | Narrated rendered motion with subtitles | `skills/manim-voice-animation/SKILL.md` |
| PDF | Rendered and inspected handout or source packet | `skills/pdf/SKILL.md` |
| Excalidraw MCP | Quick inspectable relationship, process, or boundary diagram | [Excalidraw workflow](../lesson-design/references/excalidraw.md) and the selected subject guide |
| Pinepaper MCP | Polished vector, interactive relation, or animated SVG | [Pinepaper workflow](../lesson-design/references/pinepaper.md) and a linked subject reference |
| Simulation | Learner-controlled graph or model | Self-contained HTML registered through `manage_artifact.py` |

For generated images, invoke the host's existing image-generation skill
(such as Codex's `imagegen`) and follow its instructions. Give it the lesson's
visual brief and keep the returned image with the course artifacts. Inspect
the result before the lesson coordinator registers it. GNOS does not need a
separate image-generation skill. If the host has no image-generation capability,
report that and revise the representation rather than claiming an image exists.

Image generation and the MCP references use the subject route. Declare
`skills/subject/SKILL.md` and the selected subject guide in the course topic.
Declare any media producer in the lesson's `skill_routes`; use
`skills/subject/SKILL.md` for a generated image block. The host skill is
invoked from these instructions, so its installation path does not belong in
`course.json`.

Several forms may explain one idea: text states the claim, a diagram shows
its parts, motion shows a change, and practice checks whether the learner can
use it. Give each form a distinct job. Do not recreate the same diagram in
several tools or add media to meet a quota. Do not omit a useful graph, map,
diagram, or control just to keep the lesson short.

For a physics lesson on a pendulum, name the system and make a prediction,
draw the forces at one position, show how position and velocity change over
time, then let the learner vary the starting angle. Keep the same pendulum,
units, and labels throughout. For a history lesson on a policy decision, give
the dated choices in prose, show the relevant documents side by side, then ask
the learner to explain what each source can and cannot establish. These are
examples of different jobs for different forms, not templates for every lesson.

During lesson design, read
`skills/lesson-design/references/representation-choices.md` for the medium
choices. Each delegated lesson worker receives the selected subject guide and
only the deep workflow reference its block needs.

## Source discipline

Read [source-use.md](references/source-use.md) for source selection and
downloads. The lead subject decides what counts as evidence. A simulation,
generated image, or explanatory animation is a model unless it directly and
accurately presents a cited source.
