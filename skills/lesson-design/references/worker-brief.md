# How each block worker works

A lesson is built by one coordinator and several workers. The coordinator
owns the full lesson and writes its skeleton in reasoning order. Each
worker builds exactly one block and returns it. A worker never edits
`course.json`, `lesson.json`, or `manifest.json`, and a worker never
changes the concept, the purpose, or the assigned skill route. If the
assigned medium cannot teach the purpose, the worker stops and the
coordinator fixes the plan in `course.json` first.

When you brief a worker, give the worker everything it needs in plain
language: which block it is building, what the block has to teach, which
subject guide and teacher voice to follow, which earlier blocks it has to
stay consistent with, which sources it may use, where to write its output
file, and how you will check its work. The brief for a delegated block is
stored in the block's `production` field, and it always has the same six
parts: the `skill_route` that was already approved for this block, a
`brief` that describes the one job in plain verbs, a `must_include` list
of every object, label, control, or relation that has to appear, a
`continuity` list of the terms and conventions it has to keep, an
`acceptance_checks` list that says what you will look at before you
accept it, and an optional `depends_on_block_ids` list that names earlier
blocks that have to be finished first.

## The text and exercise worker

This worker writes as the teacher who was assigned to the topic. Before
it writes anything, it reads the assigned teacher file in `teachers/`,
such as `teachers/physics/SOUL.md`, and the selected subject guide in
`skills/subject/subjects/`, such as `skills/subject/subjects/physics.md`,
after routing through `skills/subject/SKILL.md`. It writes in that
teacher's voice for the whole block. It follows the output text rules in
`skills/lesson-design/references/lesson-contract.md`, and it selects and
uses sources the way `skills/subject/references/source-use.md` describes.

The text has to explain the idea completely. It does not list short
definitions and move on. It states the exact claim, definition, date,
step, or code contract, then it explains what that statement means, why
it is true or why it matters, and how the learner can see it working in
a concrete example. A learner who reads the finished lesson from top to
bottom should understand the idea, not just recognize its name.

The worker returns the finished block with the same `id`,
`representation_id`, `type`, `concepts`, and `purpose` it was given. It
keeps one idea in each sentence. It uses bullets only when the items are
genuinely parallel, and it puts notation the learner has to inspect into
an equation block written as LaTeX for KaTeX. It never adds a video, an
image, or a simulation on its own, and it never invents a new teacher.
The lesson inherits the topic teacher.

An exercise asks the learner to use the same idea in a new situation.
The worker names the new numbers or the new case explicitly, for example
a different starting value, a different shape, or a different source to
compare. The exercise keeps its success criteria and answers private.
They never appear in the block text the learner sees. Choice options stay
public because the learner needs them to answer. Every lesson ends with
at least one such small exercise, written as homework the learner can do
after reading, so the lesson closes with practice rather than stopping
after the last explanation.

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

Every video teaches its block in depth and runs for at least one minute.
A ten-second clip that flashes a definition is not acceptable. The worker
starts from a short storyboard that says what the learner has to see
changing, writes the exact narration for each cue, builds the scenes so
each spoken term points at the object on screen, and renders and watches
the result before returning it. The finished video has a working
voiceover that matches the motion, subtitles exported from the same cue
timings, labels that stay in frame and stay readable with the sound off,
and a clean first frame, clean transitions, and a clean ending.

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

- Image generation, described in `skills/image-gen/SKILL.md`, makes a
  labeled scene or a visual analogy, such as an apparatus, an anatomy
  view, or a landscape that carries the idea.
- Pinepaper, which runs through the `pinepaper` MCP server defined in
  `.mcp.json` and follows the workflow in
  `skills/subject/references/pinepaper.md`, draws exact relations that
  have to be checked, such as a circuit, a field map, a ray diagram, or
  a polished vector figure with synchronized states. The worker also
  reads the active subject reference that the pinepaper guide points to,
  such as the physics, math, economics, or computer-science reference.
- Excalidraw, which runs through the `excalidraw` MCP server defined in
  `.mcp.json` and follows the workflow in
  `skills/subject/references/excalidraw.md`, makes a quick inspectable
  sketch, such as a pointer diagram, a graph layout, or a trust
  boundary. The worker calls `read_me` before its first `create_view`
  call and builds only what that guide allows.

Never ask an image model to produce exact data, small readable source
text, or a relation that has to match code. That work belongs in
pinepaper or excalidraw, where the relations stay editable and can be
checked.

A good brief says what to draw and how it connects to the text, for
example: "Draw the slope triangle for the worked example in the previous
block, with rise and run labeled using the same axis names and symbols.
Place it above that example and caption which side the learner should
compare with the equation."

## The simulation worker

This worker builds one self-contained interactive simulation in HTML that
the learner can run on the lesson page. Before it builds anything, it
reads the selected subject guide in `skills/subject/subjects/` for what
the learner should vary in this field, and the simulation rules in
`skills/course-design/references/representation-choices.md`. There is no
separate simulation skill file, so the subject guide and the brief are
its specification. The page runs the file in a restricted sandbox with
no network, so the simulation cannot fetch anything. The worker returns
the checked file and its registration details, and the coordinator
registers it with
`python3 skills/course-design/scripts/manage_artifact.py --learners-root learners register`.

Use a simulation whenever letting the learner try something gives a
better understanding of the topic, and let the subject decide what trying
means. In physics that can mean varying a force, a starting position, or
a frequency and watching the motion change. In mathematics it can mean
moving a step vector, changing a step size, or changing a sample size and
watching the prediction change. In economics it can mean moving a
threshold or a policy rule and watching the outcome change. The old test
of "use it only when the learner changes an input" is too narrow on its
own. The real test is whether experimenting with the model helps this
particular topic make sense.

Every simulation shows the model it implements, the units on every
control and axis, the assumptions it makes, and a reset button that
returns it to its starting state. The surrounding text asks the learner
to predict what will happen before they move a control, so they compare
their expectation with the result instead of dragging sliders at random.

A good brief names the controls and what the learner should discover, for
example: "Let the learner rotate the step vector around the fixed
gradient and watch the predicted sign change. Show units on both axes,
include a reset button, and ask for a prediction before they rotate."

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
might not see, the coordinator adds one short sentence that gives the
reason, for example that the video shows the motion the text just
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
assigned. If the medium cannot teach the purpose, stop that block and fix
`course.json` first. Never accept a quiet substitution where the worker
returns a different artifact instead. Once a result passes, merge its
fragment into the lesson, register its artifact if it produced a file
with `manage_artifact.py` following
`skills/course-design/references/artifact-manifest.md`, validate the
assembled lesson with `validate_lesson.py`, publish it with
`course_workspace.py publish`, and re-render the page with
`skills/course-viewer/scripts/render_viewer.py` before telling the
learner the page is updated.
