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

Use the [subject map](references/subject-map.json) to discover the supplied
subfields without opening every guide:

```bash
python3 skills/subject/scripts/subject_catalog.py --query "machine learning"
python3 skills/subject/scripts/subject_catalog.py --subject biology
```

Each entry points to an existing guide section with a stable ID, aliases, a
capability, and any named bridge candidates. Search returns candidates and
never selects a lead subject. Shared terms such as attention, thermodynamics,
or research methods can belong to several fields. Read the learner's intended
action and the evidence that would establish it before choosing. Ask one
focused question when that distinction changes the explanation and cannot be
resolved from the request. A catalog capability is a routing hint, not evidence
of the learner's prerequisites or a promise of complete specialty coverage.

After choosing, use a canonical ID to make the route inspectable:

```bash
python3 skills/learning-orchestrator/scripts/assemble_context.py \
  --subject artificial-intelligence --subfield artificial-intelligence.machine-learning \
  --bridge math --mode local
```

`--subfield` checks the chosen guide's ownership; it does not replace the guide
with an excerpt. `--bridge` loads an explicitly selected supporting guide and
keeps the lead teacher. Catalog bridge candidates are never loaded
automatically. For an enrolled course, the loader also reads its declared
`supporting_subjects` and only explicitly assigned `supporting_teachers`.
`--mode local` loads no learner, active course, or private assessment packet.
Use lesson mode for course continuation and its actual saved attempts.

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

Do not invent a persona for a subject without a teacher. Set its lead
`teacher` to `null`. An existing teacher can appear in `supporting_teachers`
only for a named bridge it actually owns. The lead subject still owns its
evidence and interpretation.

## Use the selected guide

Read the selected subject file in full. Its subfield map is a starting
structure, not a complete taxonomy. For an unlisted specialty, inspect a
primary, official, or academic source before designing a sustained course.
Do not imply that an introductory textbook covers every advanced branch.
Name an unlisted niche as such. Use a supplied subject only when it actually
owns the intended action; otherwise explain the missing guide before proposing
an addition. Chemistry, for example, is not interchangeable with chemical
engineering. A biological explanation can consult a chemistry source for a
bounded missing step without pretending that GNOS supplies a chemistry guide.
Keep prerequisites specific to the learner's next action; an index edge or
course prerequisite is not proof of an observed learner gap.

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
For a visual block, specify the relation to reveal and the values or sources
it must preserve. Select graphs and maps through
[representation choices](../lesson-design/references/representation-choices.md).
Use [JSXGraph](../jsxgraph/SKILL.md) for mathematical coordinates and linked
quantities, [Excalidraw](../excalidraw/SKILL.md) for a fixed structural sketch,
and [Pinepaper](../pinepaper/SKILL.md) for a composed scene. The media skill explains
construction and export; the subject guide keeps the science or evidence
correct.

| Workflow | What it produces | Route |
| --- | --- | --- |
| Subject teacher | Explanation, derivation, code, bullets, and exercises | This skill and the selected subject guide |
| Image generation | Still illustration or labeled image | The host's existing image-generation skill or tool, following the instructions below |
| Manim voice animation | Narrated rendered motion with subtitles | `skills/manim-voice-animation/SKILL.md` |
| PDF | Rendered and inspected handout or source packet | `skills/pdf/SKILL.md` |
| Excalidraw MCP | Quick inspectable relationship, process, or boundary diagram | [Excalidraw workflow](../excalidraw/SKILL.md) and the selected subject guide |
| JSXGraph | Mathematical graph or coordinate construction | [JSXGraph workflow](../jsxgraph/SKILL.md) and the selected subfield guidance |
| Pinepaper MCP | Composed diagram or changing scene | [Pinepaper workflow](../pinepaper/SKILL.md) and the selected subfield guidance |
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

Keep one case across forms. Identify which object, equation term, code step,
or source passage corresponds to each visible part, then state what the new
view adds. Change a meaningful condition for practice and ask which part of
the reasoning survives. Avoid rebuilding the same visual in several tools.

During lesson design, read
`skills/lesson-design/references/representation-choices.md` for the medium
choices. Each delegated lesson worker receives the selected subject guide and
only the deep workflow reference its block needs.

## Source discipline

Read [source-use.md](references/source-use.md) for source selection and
downloads. The lead subject decides what counts as evidence. A simulation,
generated image, or explanatory animation is a model unless it directly and
accurately presents a cited source.
