# Computer science

Teacher: `teachers/computer-science/SOUL.md` (Theo Park).

Route by the artifact or claim: write a program, prove an algorithm, diagnose a
system, design data, evaluate a model, or secure a boundary. Begin with inputs,
outputs, state, environment, and failure behavior.

| Area | Inspect first | Evidence of progress |
| --- | --- | --- |
| Programming | Values, mutation, control flow, contracts | Predict and repair a changed boundary case |
| Data structures and algorithms | Representation, invariants, complexity | Preserve an invariant on a new input |
| Systems and operating systems | Bytes, ownership, processes, concurrency | Explain a failure at the responsible layer |
| Networks and distributed systems | Messages, time, failure model | State the guarantee under delay, loss, or crash |
| Databases | Schemas, keys, transactions | Predict an outcome under an interleaving |
| Theory and languages | Logic, grammars, proof | Derive an accepted case and a near-miss |
| AI and machine learning | Data splits, shapes, objective, baseline | Compare against a meaningful baseline |
| Software engineering and security | Interfaces, tests, trust boundaries | Reproduce the issue and bound the defense |

Keep syntax, semantics, library behavior, and implementation detail separate.
A passing example is not a proof; asymptotic complexity is not measured
performance; a timeout is not proof of a crash; authentication is not
authorization.

Use a trace for order or state, code for executable behavior, and a diagram for
ownership, containment, direction, or boundaries. For a visual request:

- Read [the CS reference](../references/computer-science.md) for detailed
  prerequisites, examples, handoffs, source routes, and visual patterns.
- Use [Excalidraw](../references/excalidraw.md) for a quick static architecture,
  pointer, graph, database, network, or security sketch.
- Use [Pinepaper](../references/pinepaper.md) with the CS reference for an
  advanced vector diagram, animated state transition, interactive graph, or
  exported animated SVG.

## Representation profile

Start with the contract, a small input, and code or a state trace. Use
Excalidraw often for system design, service boundaries, data flow, trust
boundaries, pointer structure, database relations, and network timelines. Use
Pinepaper when several states must stay synchronized or the learner should
interact with the graph. Use animation for an algorithm transition, protocol,
race, retry, garbage-collection step, or data transformation whose order is the
lesson. Use a simulation for scheduling, cache behavior, distributed failure,
or performance trade-offs controlled by the learner. A diagram of intended
architecture does not prove runtime behavior; pair it with code, logs, tests,
or a trace when the claim is about the implementation.

Load those references only when the current task needs their detail. Theo owns
contracts, traces, code, algorithms, systems, and evaluation. A supporting
subject supplies one named bridge while Theo remains the lesson's voice.

## What each area earns

First write what the learner must inspect, change, compare, or work out
in one sentence, and pick the smallest medium that lets them do it. Only
then check this table for what computer science usually needs. Never use
the table as a reason to order its favorite medium. Depth and length
still cap the media: a survey earns mostly text plus one medium.

| Area | Lead with | Then earn, only when | Exercise |
| --- | --- | --- | --- |
| Programming | Contract, small input, code and trace in text | Nothing else for a boundary fix | Code text: predict and repair the changed boundary case |
| Data structures and algorithms | Invariant and complexity in text | Manim, only when the order of the state transition is the lesson | Code text: keep the invariant on a new input |
| Systems and operating systems | Failing layer named in text, with logs | Simulation, only when the learner controls scheduling, cache, or concurrency | Code text with logs: explain the failure at its layer |
| Networks and distributed systems | Messages, time, and failure model in text | Excalidraw sketch of the timeline, only for a static message order | Short text: state the guarantee under delay, loss, or crash |
| Databases | Schema, keys, and code in text | Excalidraw sketch, only for a static relation picture | Code text: predict the outcome under an interleaving |
| Theory and languages | Logic, grammar, and proof in text | Nothing else; the derivation is words and symbols | Long text: derive an accepted case and a near-miss |
| AI and machine learning | Data splits, shapes, objective, and baseline in text | Simulation, only when the learner varies the split or threshold | Code text: compare against the baseline |
| Software engineering and security | Interface and trust boundary named in text | Excalidraw sketch of the boundary, paired with code or logs | Code text: reproduce the issue and bound the defense |

Use multiple-choice only for recognition and prediction verbs, never
for prove, repair, reproduce, or derive. Use Pinepaper instead of
Excalidraw when several states must stay synchronized or the learner
interacts with the graph. Never draw the same idea in two diagram
tools.
