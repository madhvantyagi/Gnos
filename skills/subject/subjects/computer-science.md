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
