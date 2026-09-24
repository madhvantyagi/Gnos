# Representation choices for lesson design

Read this while designing the lesson, after the selected subject guide. The
subject guide says what learners need to inspect and check in that field. Use
this reference to choose forms that help explain those ideas.

## Give each form a job

A ready lesson uses at least two distinct teaching forms. Exercises and
feedback do not count toward the two. There is no maximum. Start with the
lesson's question and reasoning, then ask what the learner needs to read,
inspect, hear, change, or work out at each step. Pick a form for that job.
The two-form rule is a minimum, not the lesson plan. A bare equation or a
source link may pass a structural count while adding little understanding.
Work through the equation; use the source as evidence to inspect. Add a third
or fourth form when a remaining difficulty calls for it, such as a diagram
for structure and a trace for order within the same explanation.

| Learner action | Representation |
| --- | --- |
| Follow a claim, definition, derivation, list, or worked step | Text, equations, bullets, or code |
| Compare parts, boundaries, labels, or spatial relations | Still image or diagram |
| Follow a state, quantity, or object changing over time | Animation |
| Change an input and inspect the result | Simulation or interactive graph |
| Listen because a recording is evidence, or narration must track motion | Source block for the recording; Manim voice animation for authored motion |
| Review a stable packet away from the course page | PDF |
| Demonstrate understanding under a changed condition | Exercise |

Do not choose a medium from the subject name alone. In the selected subfield,
identify the fixed structure, changing state, exact quantity, and learner
choice. Use only the views needed to answer the lesson question. A physics
lesson may combine a verbal prediction, a free-body diagram, and motion.
Each should answer a different question about the same system. A history
lesson may combine a dated account, two documents, and a map when time,
evidence, and place all matter. The subject guide decides which details
must stay consistent across those forms.

## Know the available workflows

| Workflow | Use it for | Do not use it for |
| --- | --- | --- |
| Subject teacher | Explanations, derivations, examples, code, and exercises | A file that another media skill must produce |
| Image generation | A still illustration, labeled scene, anatomy, apparatus, or visual analogy | Exact diagrams whose relations must be editable or verifiable |
| [Excalidraw MCP](../../excalidraw/SKILL.md) | A quick inspectable relationship, process, boundary, or sequence sketch | Polished animation or dense paragraphs inside boxes |
| [Pinepaper MCP](../../pinepaper/SKILL.md) | Linked diagrams, charts, motion, or learner-controlled visual states | A simple sketch, an unverified scientific plot, or narrated video lesson |
| Manim voice animation | A narrated rendered sequence where motion carries the explanation | Definitions appearing on screen or decorative camera movement |
| Self-contained HTML | A simulation or interactive graph controlled by the learner | A fixed diagram with no useful control |
| PDF skill | A checked handout, source packet, derivation sheet, or review guide | The primary interactive lesson |

Lesson design chooses between ImageGen, [Excalidraw](../../excalidraw/SKILL.md),
[Pinepaper](../../pinepaper/SKILL.md), Manim, and a simulation using the selected subject
guide. The links load operating instructions; they do not run either MCP server.
When a block selects Excalidraw or Pinepaper, its worker reads that guide and
calls the corresponding `excalidraw` or `pinepaper` MCP tools to build and
inspect the scene. Before assigning a media block, check that the producer
is available and can return a file the viewer supports. A server named in
`.mcp.json` is configured, but its tools may not be connected in this host.
Discover the needed tool, read its workflow, and put the tool and required
output in the brief. A declaration in `skill_routes` does not run the producer.
If a tool is unavailable, revise the block and brief to preserve the teaching
job with an available producer. Report the limitation without describing an
unmade artifact as finished. Follow the artifact manifest for file formats and
registration; a tool preview or editable scene alone is not a published lesson asset.

For ImageGen, follow the subject skill's instruction to invoke the host's
existing image-generation capability. Use `skills/subject/SKILL.md` as the
lesson production route; do not add a local image-generation skill.

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

Use [Excalidraw](../../excalidraw/SKILL.md) for a quick relationship sketch.
Use [Pinepaper](../../pinepaper/SKILL.md) when attached relations, a chart
linked to the scene, motion, or interaction matters. For exact data or
uncertainty that Pinepaper's chart cannot show faithfully, use a plotting
library. Give two views of one idea the same objects, units, and state, then
ask the learner to translate between them.

## Choose a simulation when the learner controls the test

Use a simulation when trying a choice helps explain the model. The learner
may change a parameter, step through events, select an action, or repeat a
random trial. Useful controls include step size, initial condition,
probability, threshold, policy rule, force, and sample size.
Show the model, units, assumptions, and reset state. Ask for a prediction before
the learner moves the control.
Pinepaper can produce a self-contained interactive widget when its export
preserves the controls. Register that HTML as a simulation only after it works
inside the course viewer's restricted iframe. Use the self-contained HTML
route when the widget cannot express the needed model or controls.
Plan the visible space before building it. Use the 1280 by 800 simulation
canvas and responsive rules in [worker-brief.md](worker-brief.md). Put the
question, control, graph, and result where the learner can see their relation
without hunting through an oversized page. Follow the interaction with a
plain explanation of the result in the lesson.

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

## Use depth and time well

Every ready lesson still needs two distinct teaching forms. Use depth and
duration to decide how far to develop each form:

- For a survey or short course, choose only the media needed to explain the
  central ideas. A concise course can still need a diagram or demonstration.
- For a working course, use representations that help the learner apply the
  ideas under changed conditions.
- For a mastery course, support deeper examination of assumptions and limits.
  A longer duration does not by itself justify more media.

Cut any form that repeats the same explanation without giving the learner a
new way to inspect or use the idea. Keep text that introduces or interprets a visual; those
parts develop one explanation together. Include time to inspect and use the
media when estimating lesson duration.

## Choose while designing the lesson

Develop the reasoning and its views together. Use a diagram, animation,
simulation, or source where it makes a difficult step easier to follow or
reveals a relation worth examining. Prose being able to describe the same
idea is not a reason to omit a helpful visual.
Several forms can work together on one idea. A diagram can show the setup, an
animation can show what changes, and a simulation can let the learner test a
new input. Keep the example, labels, units, and terms consistent across them.

Record each choice as a block in `lesson.json`, with its own purpose. New
lessons do not need a course `representations` list or `representation_id`.
If a medium is not helping, revise the lesson block. Return to course design
only if the topic needs another concept, source, or place in the sequence.

## Prepare delegated blocks

Assign every lesson block to its own sub-agent when multi-agent execution is
available, including prose, notation, transitions, and exercises. Keep the
lesson coordinator responsible for the skeleton, dependency scheduling,
acceptance review, assembly, artifact registration, readiness validation, and
publication. If the learner explicitly authorizes solo work, preserve the
same briefs and dependency order. If sub-agents are unavailable and solo work
was not authorized, stop at the validated draft and report the limitation;
do not publish the lesson as ready.

The coordinator writes the ordered lesson skeleton first. Every block gets
one `production` brief with its selected skill route, exact content,
continuity rules, an explicit `depends_on_block_ids` list (empty when there
are no dependencies), and acceptance checks. Each worker implements that
block only, writes to a unique output path, and does not edit `course.json`,
`lesson.json`, or `manifest.json`. Run blocks with no unmet dependencies in
parallel; a dependent block starts after each named predecessor has passed
review.

Read [lesson-contract.md](lesson-contract.md) for how to brief each worker and merge
the results. Read [artifact-manifest.md](../../course-design/references/artifact-manifest.md)
before publishing a file.

## Final checks

- Does the lesson use at least two distinct teaching forms?
- Does each form expose something the learner must inspect, compare, or change?
- Can the learner identify the same state, quantity, and example across forms?
- Does it follow the selected subject guide?
- Does every block have a clear purpose in the lesson?
- Are symbols, colors, direction, units, names, and dates consistent?
- Does each artifact have one owner and one output path?
- Did the coordinator inspect the result before registering it?

If any answer is no, revise the lesson before producing more media.
