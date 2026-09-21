# Representation choices

Read the selected subject guide before this file. The subject guide states what
the field needs learners to inspect. This file chooses the smallest medium that
does that job.

## Decide from the learner's action

Write one sentence: “The learner must inspect, change, hear, compare, derive, or
practice ___.” If the sentence does not name an action, the representation has
no clear job.

| Learner action | Representation |
| --- | --- |
| Follow a claim, definition, derivation, list, or worked step | Text, equations, bullets, or code |
| Compare parts, boundaries, labels, or spatial relations | Still image or diagram |
| Follow a state, quantity, or object changing over time | Animation |
| Change an input and inspect the result | Simulation or interactive graph |
| Listen because a recording is evidence, or narration must track motion | Source block for the recording; Manim voice animation for authored motion |
| Review a stable packet away from the course page | PDF |
| Demonstrate understanding under a changed condition | Exercise |

Do not choose a medium from the subject name alone. Physics often earns motion;
some physics lessons still need only a free-body diagram. History often earns a
dated source set; a migration sequence may earn motion. Subject guidance is a
starting point, not a quota.

## Know the available workflows

| Workflow | Use it for | Do not use it for |
| --- | --- | --- |
| Subject teacher | Explanations, derivations, examples, code, and exercises | A file that another media skill must produce |
| Image generation | A still illustration, labeled scene, anatomy, apparatus, or visual analogy | Exact diagrams whose relations must be editable or verifiable |
| Excalidraw MCP | A quick inspectable CS architecture, pointer, graph, database, network, or trust-boundary sketch | Polished animation or dense paragraphs inside boxes |
| Pinepaper MCP | Polished vector diagrams, synchronized changes, interactive relations, and animated SVG | A simple sketch or narrated video lesson |
| Manim voice animation | A narrated rendered sequence where motion carries the explanation | Definitions appearing on screen or decorative camera movement |
| Self-contained HTML | A simulation or interactive graph controlled by the learner | A fixed diagram with no useful control |
| PDF skill | A checked handout, source packet, derivation sheet, or review guide | The primary interactive lesson |

The selected subject guide decides between ImageGen, Excalidraw, Pinepaper,
Manim, and a simulation. Read the linked workflow only after that choice. If an
MCP server is unavailable, use the smallest faithful fallback and report the
missing capability. Never claim that an unrendered artifact exists.

## Choose motion only when change is the idea

Use animation for motion, transformation, propagation, feedback, accumulation,
or ordered state change. Keep the governing rule visible and change one thing
at a time.

Do not animate a definition, list, claim, static architecture, or equation
typing effect. If one still frame carries the full explanation, use the still.

## Choose a still when comparison needs time

Use a still image or diagram for structure: a force balance, anatomy, map,
pipeline, system boundary, graph layout, geometry figure, or evidence matrix.
Label the relation the learner must inspect. Do not ask an image model to
produce exact data, readable source text, or a relation that must be checked
against code.

Use Excalidraw for a fast CS sketch. Use Pinepaper when exact relations,
interaction, synchronized states, or polished vector export matter. Use one
tool per idea.

## Choose a simulation when the learner controls the test

Use a simulation when changing a parameter is part of the reasoning: step size,
initial condition, probability, threshold, policy rule, force, or sample size.
Show the model, units, assumptions, and reset state. Ask for a prediction before
the learner moves the control.

Do not use a simulation to conceal a formula or to imply that one chosen model
is empirical evidence.

## Use narration and source media deliberately

Narration belongs with an animation when spoken timing helps coordinate several
changes. When a recording is evidence, use a source block and preserve its
date, creator, location, and evidentiary limits. Do the same for a video,
interview, speech, experiment recording, or archival clip.

Do not add voice because a visual feels empty. Do not use generated motion as
documentary footage or measured evidence.

## Keep text when text is the clearest tool

Keep definitions, hypotheses, proof steps, code contracts, vocabulary, dates,
and concise comparisons in text. Use bullets only for parallel items. Use a
table when exact values or repeated fields matter. Use an equation block when
the learner must inspect notation or derivation.

Text is not a fallback. It is the correct representation when the reasoning is
linguistic, symbolic, or exact.

## Set the media budget

Depth and length set a ceiling:

- `survey` or one session: mostly text; add one medium where the lesson fails
  without it.
- `working`: add the diagrams, controls, and motion needed for transfer.
- `mastery` or a term: include multiple earned representations across the
  course, not multiple versions of one idea.

Cut any representation that repeats the same explanation without giving the
learner a new action.

## Plan the course representation before the lesson block

Write each approved part in the topic's `representations` list in `course.json`.
Give it a stable ID, kind, concept, and one-sentence purpose. Then bind each
`lesson.json` block to that ID through `representation_id`.

The lesson may make the representation concrete. It may not silently change
the concept, purpose, medium, or skill route. If the plan is wrong, revise
`course.json`, record the reason, validate it, and only then revise the lesson.

## Prepare delegated blocks

Delegate each file-producing block when multi-agent execution is available.
Delegate a text or code block only when it needs separate research or a long
worked construction. Keep short explanations, transitions, and notation with
the lesson coordinator.

The coordinator writes the ordered lesson skeleton first. Each delegated block
gets one `production` brief with its approved skill route, exact content,
continuity rules, dependencies, and acceptance checks. The worker implements
that block only. It does not edit `course.json`, `lesson.json`, or
`manifest.json`.

Read [lesson-contract.md](../../lesson-design/references/lesson-contract.md) for how to brief each worker and merge
the results. Read [artifact-manifest.md](artifact-manifest.md) before publishing a
file.

## Final checks

- Does the medium expose something the learner must inspect or control?
- Does it follow the selected subject guide?
- Does every block point to an approved course representation?
- Are symbols, colors, direction, units, names, and dates consistent?
- Does each artifact have one owner and one output path?
- Did the coordinator inspect the result before registering it?

If any answer is no, fix the plan before producing more media.
