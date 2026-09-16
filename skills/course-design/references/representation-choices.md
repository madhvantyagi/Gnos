# Representation choices

Pick the smallest representation that reveals the idea. Bigger is not
better. Read this when a topic needs a visual, then pick one and stick
with it.

## Choose by what the learner must inspect

| What the topic-part does | Use this |
| --- | --- |
| Something changes over time, or one thing becomes another. | Manim animation |
| The learner must compare parts of a structure. | Static image |
| The learner changes a value and watches the result. | Simulation |
| A claim, definition, list, or worked step. | Text |
| Material to keep or print for later study. | PDF handout |
| A check of understanding after the teaching. | Exercise |

## Motion is earned, not default

Order Manim only when one change shows what text and a still frame
cannot. Earned examples: a vector rotates, a limit shrinks, a wave
moves, a secant approaches a tangent, a basis transforms a space, a
force changes motion, an algorithm changes state, a distribution builds
up from repeated samples.

Not earned: a definition appears, a list appears, an equation types
itself, labels fade in around a still diagram, decorative camera moves.

## Trigger words

If the beat uses one of these, motion may be right. If it uses none,
do not order Manim: changes over time, moves, rotates, shrinks, grows,
approaches, follows a path. Check "builds up" and "transforms into"
against the still test first.

## Use a static image instead

Structure does not move. Use an image for: an architecture diagram, a
labeled anatomy, a pipeline overview, a network or graph layout, a
geometry figure with givens marked. The learner needs time to compare
parts; a still image gives that time.

## Use a simulation instead

Use a simulation when the learner changes a parameter and predicts the
result: step size in gradient descent, the direction of a step, a
probability or sample size, a filter or threshold. If the learner is
the one changing the value, hand over the control instead.

## Keep it text

No image and no motion for: definitions, lists of rules, worked algebra
or a proof step, a claim and its hypotheses, vocabulary.

## Hard rules

1. Never animate a definition, a list, or a claim. If nothing changes,
   it is not animation.
2. One animation per concept, and one change per animation. Split the
   concept before adding a second scene.
3. Motion must reveal something a still image cannot. If a still frame
   says it, remove the motion.

## Before ordering Manim

Write the storyboard beat first: the concept target, the exact
narration, the visible objects, the one change each cue reveals, the
success check. Then ask: does the beat use a trigger word? Does the
change pass the still-frame test? Only then open the scene code.

## After choosing

Use one representation per idea. Do not make the same diagram in two
tools. Keep the same symbol, color, and direction across every block
in the lesson.

The kind-to-skill dispatch lives in
[course-contract.md](course-contract.md): manim -> manim-voice-animation,
image/diagram -> image-gen, simulation -> a self-contained HTML file,
pdf -> pdf, text/exercise -> the subject teacher. Every file-producing
skill registers its artifact, or the viewer chip stays planned.
