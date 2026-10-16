# How each block worker works

A lesson has one coordinator, who writes the skeleton in reasoning order and
owns assembly. Each delegated worker builds one assigned block and returns it.
Follow [lesson design](../SKILL.md) for when to delegate. A worker never edits
`course.json`, `lesson.json`, or `manifest.json`, and a worker never
changes the concept, the purpose, or the assigned skill route. If the
assigned medium cannot teach the purpose, the worker stops and the
coordinator revises the lesson block and brief first. A new topic concept or source goes back to course design.

Before dispatching, the coordinator writes a short account of the lesson's
running example and how each block advances it. Put the part relevant to a
worker in its brief. Give a dependent worker the accepted output of each
named earlier block, not just its title. A worker that needs the previous
block to make its opening sentence connect must list that block as a
dependency. The coordinator reviews the complete reading order after
assembly and sends disconnected blocks back for revision.
Put the block's question and starting knowledge in `brief`, its worked step
and likely confusion in `must_include`, and the exact values, assumptions,
notation, and visual meanings in `continuity`. Acceptance checks must test the
reasoning and interaction, not merely headings or file presence.

Use the private packet from
[build_block_context.py](../scripts/build_block_context.py) for the target and
its declared earlier dependencies. Add the selected subject guidance, teacher
instructions, inspected media exports, and a separate output path. The packet
contains authored records; it does not certify completed media. Dispatch
independent blocks together and dependent blocks after review.

For diagrams, charts, animation, and simulation UI, use one approved palette
from [simulation presentation](simulation-design.md). Put that preset and each
color's meaning in the shared brief. Keep related visuals consistent; do not
mix presets or add gradients.

## The text and exercise worker

This worker writes as the teacher who was assigned to the topic. Before
it writes anything, it reads the assigned teacher file in `teachers/` when one exists,
such as `teachers/physics/SOUL.md`, and the selected subject guide in
`skills/subject/subjects/`, such as `skills/subject/subjects/physics.md`,
after routing through `skills/subject/SKILL.md`. It writes in that
teacher's voice for the whole block. It follows the output text rules in
`skills/lesson-design/references/lesson-contract.md`, and it selects and
uses sources the way `skills/subject/references/source-use.md` describes.

The text has to explain the idea completely. It does not list short
definitions and move on. It begins from the question left by the block it
depends on, states the exact claim or step, and explains what it means and
why it follows. Work through the shared example before giving a compact
rule. If several paragraphs are needed, put them in the block's `text` with
blank lines between them. Do not stop after a definition and one sentence.
When a transition is needed, connect this result to the next unresolved
question. Let the coordinator join neighboring blocks without a forced
conclusion after each one.
Give the confusing step room: show the intermediate calculation, causal link,
or source inference and explain why a tempting alternative fails. Do not
restart the whole lesson in each block. A small transition block can be short;
a block responsible for developing a new idea needs the full explanation.

The worker returns the finished block with the same `id`,
`type`, `concepts`, and `purpose` it was given. If an older block has a
`representation_id`, keep it. It
keeps one idea in each sentence. It uses bullets only when the items are
genuinely parallel, and it puts notation the learner has to inspect into
an equation block written as LaTeX for KaTeX. It never adds a video, an
image, or a simulation on its own, and it never invents a new teacher.
The lesson inherits the topic teacher.

The coordinator writes a complete provisional exercise contract in
`exercises` before publishing the draft. It includes a prompt, response type,
evaluation, success criteria, so the draft passes validation. Store its worked solution in the exercise
`solution` field, outside `evaluation`; this keeps manual evaluation valid. The exercise-block worker receives that contract, checks that it
asks for transfer to a changed case, and authors the final learner-facing
prompt and worked solution. It returns the block with the same `exercise_id`
and the completed exercise data. The coordinator merges both into
`lesson.json` and checks that the final prompt still fits the assigned
response type, evaluation, and success criteria. Success criteria and answers
stay private; choice options stay public because the learner needs them to
answer. If the contract needs revision, return a proposal; the coordinator
updates the contract and revalidates the draft before accepting the result.
Every lesson ends with at least one manageable opportunity to use the idea
independently.

A weak brief says "make the explanation clear and engaging" because there
is nothing to check in that sentence. A good brief says what to state and
in which voice, for example: "Explain the local prediction for a small
step as a dot product, in Mira Sen's voice. Name the physical system
first, then state the equation, then work through one numerical example
with units, then point out what changes sign and why."

## The video worker

This worker builds a narrated video with the manim-voice-animation skill.
Before it writes any scene code, it reads
`skills/manim-voice-animation/SKILL.md` and the storyboard guide in
`skills/manim-voice-animation/references/01_pedagogical_storyboard.md`,
then only the one visual reference its scene needs, such as the proofs,
linear-algebra, mechanics, algorithms, or 3D-camera guide. It times its
narration the way
`skills/manim-voice-animation/references/02_voiceover_synchronization.md`
describes, using `scripts/cue_player.py` and the storyboard schema in
`templates/storyboard_schema.json`. It reads only that skill and the
subject excerpt you pasted into the brief, and it writes its video to
its own output path. It checks its environment with
`scripts/setup_env.py`, checks its scene with `scripts/linter.py`, and
renders through `scripts/render_pipeline.py` before returning anything.

Give the learner enough time to follow the assigned change and inspect its
result. Duration follows the reasoning, narration, and readable holds.
A ten-second clip that flashes a definition is not acceptable. The worker
starts from a short storyboard that says what the learner has to see
changing, writes the exact narration for each cue, builds the scenes so
each spoken term points at the object on screen, and renders and watches
the result before returning it. The finished video has a working
voiceover that matches the motion, subtitles exported from the same cue
timings, labels that stay in frame and stay readable with the sound off,
and a clean first frame, clean transitions, and a clean ending.
Use the teacher guidance supplied in the brief for narration. Keep its pace
at the difficult change; a media worker must not replace the teacher with a
generic documentary voice.

A good brief names the one change the learner has to watch and the
objects that have to move, for example: "Show the gradient vector held
fixed while two step directions move from the same point, one with a
positive dot product and one with a negative dot product. Narrate why the
sign flips, keep the gradient symbol and the direction colors from the
earlier text block, and hold the final frame long enough to read without
sound."

## The image worker

This worker draws one still image or diagram that belongs with a specific
text block. The image sits next to that text or directly above it on the
page, it illustrates the same example with the same labels and symbols,
and its caption tells the learner what relation to inspect. Text and
image explain each other: the text names the objects, the image shows how
they fit together, and neither one introduces different names for the
same thing.

The coordinator picks one drawing tool for each image, and the brief
names that tool. Each tool has its own instructions the worker reads
before drawing:

- Use the host's existing image-generation skill or tool to make a labeled
  scene or visual analogy, such as an apparatus or anatomy view. Follow the
  image-generation instructions in `skills/subject/SKILL.md`, then read the
  host skill if it provides one. Do not create or look for a separate GNOS
  image-generation skill.
- [Pinepaper](../../pinepaper/SKILL.md), which runs through the `pinepaper` MCP server
  defined in `.mcp.json`, builds diagrams, charts, motion, or controls when
  their states must stay linked. The worker reads only the skill's reference
  for the selected visual job. The brief names the model or data source and
  the required export so the worker can check both the scene and its file.
- [Excalidraw](../../excalidraw/SKILL.md), which runs through the `excalidraw` MCP server
  defined in `.mcp.json`, makes a quick inspectable
  sketch, such as a pointer diagram, a graph layout, or a trust
  boundary. The worker calls `read_me` before its first `create_view`
  call and builds only what that guide allows.

These links select instructions for the chosen server. The worker must invoke
the server's tools, inspect the returned scene, and hand back an export or
working view. Merely linking the guide or naming the server in `skill_route`
does not produce a diagram.
Use `skills/pinepaper/SKILL.md` or `skills/excalidraw/SKILL.md` as the block's
`skill_route`, and declare that same route in the lesson.

Never ask an image model to produce exact data, small readable source
text, or a relation that has to match code. Keep exact data in a table,
code trace, or verified plot. Use Pinepaper or
[Excalidraw](../../excalidraw/SKILL.md) for a diagram whose relations must
be inspected. When the tool is Excalidraw, paste the exact text-element schema
from `read_me` into the brief — field names and sizing rules, not a pointer
to it. Make one acceptance check per label: each string must appear verbatim
in the returned scene data.

A good brief says what to draw and how it connects to the text, for
example: "Draw the slope triangle for the worked example in the previous
block, with rise and run labeled using the same axis names and symbols.
Place it above that example and caption which side the learner should
compare with the equation."

## The simulation worker

For a mathematical graph, read [JSXGraph](../../jsxgraph/SKILL.md) and use its
export helper and starter closest to the assigned action. Set the block's
`production.skill_route` to `skills/jsxgraph/SKILL.md`. The same route belongs
in the lesson's declared skills. This worker still returns the artifact to the
coordinator and follows the shared presentation rules below.

Build one self-contained HTML experiment for the question in the brief. Read
the selected subfield guidance and
[simulation presentation](simulation-design.md). Start from the
[reusable shell](../templates/simulation.html) when it fits the interaction.
Use one approved palette, keep all active content inside the frame without
scrolling, and preserve state between Controls, Result, and Model views.

Show the model, assumptions, units, current values, and reset state. Motion
needs pause or step controls and must honor reduced-motion preferences. The
surrounding lesson asks for a prediction and interprets a result afterward.
Compute related views from one state; do not add controls without a teaching job.

Inline all required CSS and script. Test the delivered file inside the viewer's
`sandbox="allow-scripts"` at desktop, tablet, and phone widths. Check inputs,
reset, view switches, and the longest feedback state. The sandbox does not
itself prevent network access; a self-contained artifact must make no external
requests. Return the inspected file and registration payload, including its
actual `metadata.dimensions` (normally 1280 × 800). The coordinator registers it.

A useful brief says: "Rotate the step around the fixed gradient. Use the same
vectors as the worked example, show the dot-product sign in both views, and
check a right-angle step before resetting."

## The PDF handout worker

This worker builds a stable handout the learner can keep and review away
from the lesson page, such as a derivation sheet, a set of sources, or a
review guide with the worked example and the closing homework. Before it
builds anything, it reads `skills/pdf/SKILL.md`, layouts its pages the
way `skills/pdf/references/lesson-format.md` describes, and reviews them
the way `skills/pdf/references/visual-review.md` describes. It converts
with `python3 skills/pdf/scripts/markdown_to_pdf.py` or, when precise
block control is needed, with `build_pdf.py`, then it renders each page
with `pdftoppm` and checks the extracted text for missing glyphs. The PDF is
always a companion to the finished lesson at the end. It is never the
primary way the lesson is taught, and it never replaces the text, video,
image, or simulation on the page. The worker renders the PDF, inspects
every page for equations, captions, page breaks, text size, and source
links, and returns the checked file. The coordinator registers it with
`manage_artifact.py` like any other artifact, following
`skills/course-design/references/artifact-manifest.md`.

## Keeping the whole lesson consistent

The finished lesson has to read as one complete explanation from top to
bottom, with text, video, images, and simulation supporting each other.
The coordinator makes that happen by telling every worker which
conventions to keep, and every worker keeps them exactly.

Terms, symbols, colors, direction of arrows, units, names, and dates stay
the same in the explanation, the narration, the labels, the graph, and
the exercise. When an earlier block fixed a symbol for the gradient, the
video uses that same symbol. When the text introduced axis names and
units, the image and the simulation use those same names and units. When
a color meant a positive direction, it keeps meaning a positive
direction.

When the lesson moves from one medium to another for a reason the learner
might not see, the coordinator asks the responsible worker for a sentence
that explains the reason, for example that the video shows the motion the text just
described, or that the image below compares the two cases side by side.
These sentences explain the move. They do not paper over unrelated
artifacts with generic phrases.

## Checking a worker's result

Check every returned block against the acceptance checks you wrote in its
brief. Read the text for completeness, watch the full video with sound on
and once with sound off, open the image at the size the learner will see
it, and run the simulation through its controls and its reset state.
Reject any result that changes the terms, symbols, colors, units, names,
or dates, or that teaches a different concept or purpose than the one you
assigned. If the medium cannot teach the purpose, stop that block and revise
the lesson block and brief. Return to course design only if the topic needs a
new concept, source, or place in the sequence. Never accept a quiet
substitution where the worker returns a different artifact instead. Follow
every view link yourself; a view that opens empty fails. After
all workers pass review, merge their fragments in lesson order. Follow the
publication sequence in [lesson design](../SKILL.md): keep the published
lesson in draft while registering checked artifacts, then validate and publish
the reviewed lesson as ready. Repair failed registration before offering the page.
Hand control back to the orchestrator; it asks whether the learner
wants to see the course. Render the reviewed course page with `skills/course-viewer/scripts/render_viewer.py`;
show its link after the learner requests or approves viewing.
