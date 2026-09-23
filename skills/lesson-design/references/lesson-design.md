# Design a lesson that develops understanding

Read this before writing the lesson skeleton and again when reviewing the
assembled lesson. It explains how to develop the teaching. Use
[lesson-contract.md](lesson-contract.md) for the file structure and
[worker-brief.md](worker-brief.md) for production instructions.

## Begin with the idea

The course gives you a topic, its place in the sequence, and the concepts it
covers. It does not give you a finished explanation. Start by asking what the
idea is, why someone would use it, and what a simple case makes visible.
Explain that case before giving a compact definition. Fill in the steps and
assumptions that a textbook might leave for the reader to infer. Use plain,
natural language, as if you were helping a friend understand a hard idea.
Do not open with a definition or equation whose objects have not appeared in
the lesson. On a first lesson, show the simplest meaningful situation in the
field and name its parts before explaining the math that describes it.

## Understand the teaching assignment

Read the topic's concepts, ordered subtopics, prerequisites, and sources. Look at the preceding
topic to see what this lesson builds on and the following topic to understand
what it prepares. Use learner evidence to see what has been demonstrated.
Do not treat missing evidence as proof that the learner knows nothing, or use
an assumed prerequisite to skip the first explanation of a new idea.
Write down the last question the previous lesson answered and the question it
left open. Begin this lesson from that gap. If this is the first lesson, begin
from the learner's goal and a small case they can follow without new notation.
End by saying what this lesson now makes possible in the next one.

Plan the reasoning needed to understand the topic. Decide what the learner
should be able to explain or do by the end, then choose examples and practice
that let you see it. The course sets the topic boundary and the order of its
main ideas; the lesson develops
the definitions, intermediate steps, examples, and connections within it.
Return to course design when the lesson needs a new topic concept or source.

## Use the teacher and subject guidance

Read the assigned teacher's `SOUL.md` before drafting. Apply its examples and
judgment: how the teacher introduces abstraction, responds to confusion,
chooses examples, and decides when to move faster. Let those decisions shape
the prose. Repeating a name, biography, or favorite phrase does not establish
the teacher's voice. For a topic without a teacher, write directly without
inventing one.
Carry the teacher's decisions into each worker brief: how to introduce this
abstraction, which example to stay with, and which confusing step needs more
time. A concise teacher can still explain a hard step at length. Keep the
teacher's manner while giving the learner every step needed to follow it.

Use the selected subject guide and its relevant references to determine what
the explanation must establish. A mathematical picture needs stated
conditions; a historical claim needs evidence and context. Address likely
misconceptions where they affect the reasoning. Check definitions and claims
against the course's source sections. Keep the lead teacher's voice when
introducing an idea from a supporting subject.

## Develop the explanation before producing media

Plan the reasoning and representations together before producing files. The
coordinator writes teaching notes for the briefs, not finished lesson prose.
Start with a concrete question, problem, or situation that
gives the topic a purpose. Explain what the learner is trying to account for,
then introduce the terms needed to account for it.

Work through an example and explain why each important step follows. Include
the intermediate operation or assumption that would otherwise force the
learner to guess. Connect the example to the general rule and examine where
that rule applies. Return to the opening problem so the learner can see what
the new idea explains.

Make the difficult transition the center of the lesson. Show what a reasonable
first answer misses, then work through the missing step slowly. For expected
return, for example, first distinguish one trip's reward from what happens
across many trips. Count outcomes in a small table before introducing weights
and their sum. Merely defining expectation and showing its equation leaves
the connection unexplained. Use the selected subject's confusion guidance to
find the equivalent transition for this topic.

Keep one running case through the main explanation. Before each new block,
identify what the learner has just established and what question remains.
After a diagram, equation, code trace, or simulation, explain what the learner
saw and how it changes the original answer. A simulation needs more than a
prediction prompt: interpret one result, explain why it happened, and connect
it to the next step. Do not leave an artifact between unrelated paragraphs.

Choose sections that develop this reasoning; do not impose the same headings
on every lesson. The finished lesson may open with a diagram or question if
that makes the problem easier to grasp. Keep related blocks together so the
reader can follow one explanation across text and media.

## Start from usable knowledge and write precisely

Begin at the knowledge the learner can reasonably use. Define unfamiliar words
when they first matter. Explain new notation before asking the learner to
reason with it, and translate between ordinary language and the formal
statement. Review earlier material only as far as this explanation needs it.

Choose words that state the relationship. “The output changes” leaves the
work to the learner. “Doubling this input doubles its contribution to the
weighted sum, because its weight stays fixed” identifies the change and its
cause. Replace “apply the formula” with the substitution and the reason it
fits this case.

Write connected paragraphs in the teacher's natural cadence. Give a difficult
step several paragraphs when it needs them: set up the case, reason through
it, interpret the result, and only then state the compact rule. A block can
hold several paragraphs. Split a block when its teaching job changes, not
because a paragraph looks long in JSON. Explain why the next step is needed
instead of announcing “now let's explore” another topic.
Use lists for parallel choices or actual steps, not as a substitute for
explaining relationships. When using an analogy, state where it stops matching
the subject before drawing a conclusion it cannot support.

## Make examples lead to independent use

Choose an example with enough detail to work through. Keep it across the
explanation and visual blocks when continuity helps. Explain the decision at
each important step, rather than showing only the conditions and the answer.
Distinguish what this example demonstrates from what still needs a general
argument or further evidence.

Then change something that tests the central idea: an input, assumption,
source, or constraint. Show which part of the reasoning survives and which
part must change. Use a counterexample when it reveals a limit more directly
than another successful case.

End the formal lesson with a manageable opportunity to use the idea
independently. Match the exercise to the lesson, whether it requires a
prediction, derivation, explanation, implementation, or evidence comparison.
Keep answers and assessment criteria in the private exercise fields. During
live teaching, follow the orchestrator's guidance on responding to the learner;
a written exercise is not a reason to withhold an explanation.

## Place media where the explanation needs it

Use at least two distinct teaching forms in the finished lesson. Let one
establish the idea and another make a relationship inspectable or testable.
For example, explain a rate in prose, show it on a graph, and let the learner
change the input if that reveals a further point. In history, pair an account
of a decision with a dated source and ask what that source can establish.
More forms are welcome when each adds a useful step. A second paragraph or
another version of the same picture is not a second form.

Introduce the object or question before the learner inspects it. Place an image
beside the passage it supports, use the same example and labels, and write a
caption that points to the relationship worth noticing. Use that observation
in the next step of the explanation.

For motion, establish what changes and what stays fixed. For a simulation,
explain the model and ask for a prediction before inviting the learner to
change a control. Connect the result to the lesson's question. If narration
is part of an artifact, write it in the teacher's voice and align
it with what is visible. A PDF should preserve a useful reading or practice
sequence for later use.

Text and an image can explain one concept together. Remove repetition when it
adds no explanation, observation, or practice. Follow
[representation-choices.md](representation-choices.md)
for medium selection and the owning media skill for construction and checks.

Translate between forms instead of assuming the learner sees the connection.
Point from one example value to its table row, from that row to its plotted
point, or from an equation term to the code that computes it. Then explain
what the new view makes easier to notice. A caption that only names the topic
does not perform this work.

## Review depth and flow

Give difficult transitions enough space to be understood. A survey can develop
one central example carefully while leaving specialist cases for later. A
working lesson needs enough explanation and practice for independent use. A
mastery lesson should examine justification, assumptions, and limits as the
topic requires.

Use the planned duration to pace explanation, media, and practice together.
Do not pad to a word count or compress reasoning into fragments to meet a
section limit. If the topic cannot be developed in the available time,
return to course design to adjust the topic boundary or duration.
For a full lesson, several short blocks with one definition apiece are not
enough. Develop the central example over connected paragraphs, explain the
hard transition, and work through a changed case before independent practice.
Spend more space on why the result follows than on announcing terms. Estimate
time for following the reasoning and using the media, not just reading the
headings. A longer lesson should answer more of the learner's likely questions
about the same idea before adding another idea.

Read the assembled lesson from beginning to end as the learner would. At each
block boundary, ask: what question makes this block necessary, and does the
opening sentence answer that question? Mark every first use of a term or
symbol; explain it before the learner must use it. Repair jumps in the worked
example, interpret every visual, and ensure the final practice follows from
what was taught. Reject a sequence of short definitions even if it contains
two media types and passes the file validator. A complete explanation gives
the learner an opportunity to understand; their subsequent work provides
evidence that they did.
