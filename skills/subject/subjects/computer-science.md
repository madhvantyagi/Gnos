# Computer science

Teacher: `teachers/computer-science/SOUL.md` (Theo Park).

Route computer science by the artifact or claim the learner wants to make:
write a program, prove an algorithm, diagnose a system, design a data model,
evaluate a model, or secure a boundary. Start with inputs, outputs, state,
failure behavior, and environment. A working example is evidence for one case;
it is not automatically a correctness proof or production design.

## Route by computational work

| Area | Inspect first | Teaching decision | Evidence of progress |
| --- | --- | --- | --- |
| Programming | Expressions, state, control flow | Trace a small input before adding abstraction | Predict output and repair a boundary case |
| Data structures | References, invariants, complexity | Show representation and operation costs together | Choose a structure for a stated workload |
| Algorithms | Discrete math, recursion, invariants | Separate correctness argument from runtime analysis | Preserve a loop invariant and handle absent input |
| Systems and architecture | Memory, representation, processes | Follow bytes or state across a concrete boundary | Explain a failure at the layer where it occurs |
| Operating systems | Processes, memory, files, concurrency | Make ownership, scheduling, and races explicit | Reproduce a race or resource failure and bound it |
| Networks and distributed systems | Messages, delay, failure models | Use a timeline; distinguish delay, loss, and crash | State what the protocol guarantees under failure |
| Databases | Sets, schemas, transactions | Connect query result to data state and isolation | Predict a transaction outcome under an interleaving |
| Theory and languages | Logic, grammars, proofs | Put formal rule beside accepted and rejected strings | Derive a parse, invariant, or undecidability boundary |
| AI and machine learning | Linear algebra, probability, calculus | Track data split, shapes, objective, baseline, metric | Compare a model with a meaningful baseline |
| Software engineering | Contracts, testing, versioning | Make interfaces and failure behavior reviewable | Reproduce a bug and verify a bounded change |
| Security | Trust boundaries, auth, input handling | Trace source to sink and state attacker capability | Explain exploitability and a defense's scope |

## Prerequisite checks

- For programming, check values versus names, mutation, control flow, and input
  contracts. Run an empty, singleton, duplicate, and malformed case early.
- For algorithms, check functions, induction, sets, and asymptotic notation.
  Ask what remains true after one loop iteration or recursive call.
- For systems, check binary representation, memory ownership, process versus
  thread, and blocking versus nonblocking behavior. Do not teach one language's
  runtime accident as a universal machine rule.
- For networks, check the message timeline and failure model. A timeout is
  evidence that a response was not observed, not proof that the server crashed.
- For databases, check keys, joins, constraints, and transaction boundaries.
  A query returning rows does not establish that writes are durable or isolated.
- For AI, check vector shapes, probability, derivatives, data leakage, and the
  evaluation split. A plausible output is not a reliability measurement.
- For security, check asset, boundary, attacker capability, source, sink, and
  validation. Do not label a theoretical bad input exploitable without a path.

## High-value teaching decisions

Use a trace when order or state is the obstacle; use a diagram when ownership,
data flow, or a boundary is the obstacle; use code when the learner needs to run
a changed case. For an algorithm, write the contract, invariant, termination
measure, and cost model separately. For a system, name the layer and observable
before proposing a fix. For an ML lesson, keep data, objective, parameters, and
evaluation as separate objects.

## Excalidraw MCP diagrams

GNOS bundles the `excalidraw` MCP server for computer-science diagrams. Use it
when position, connection, direction, containment, ownership, or change over
time is central to the learner's confusion. Strong uses include architecture,
pointers and aliasing, graph traversal, process and thread relationships,
network flows, distributed timelines, database relationships, AI pipelines,
and security boundaries.

Before the first diagram in a task, read
[the Excalidraw reference](../references/excalidraw.md). It defines the required
tool order, construction rules, verification pass, teaching patterns, and
fallback behavior. Do not call Excalidraw merely because the subject is computer
science; a local syntax error or small execution trace rarely needs a canvas.

Keep these distinctions explicit:

- syntax, language semantics, library behavior, and implementation detail;
- a program that passes examples versus a procedure correct over its domain;
- correctness, asymptotic complexity, and measured performance;
- process, thread, coroutine, and distributed service;
- delay, loss, crash, and a timeout observation;
- database consistency, durability, isolation, and application-level validity;
- training, validation, test, and deployment distributions;
- authentication, authorization, confidentiality, integrity, and availability.

## Mini lesson patterns
**Recursion.** For factorial on nonnegative integers, identify base case `n=0`
and progress `n−1`. Change the input contract to include negative values; the
learner must add a policy or explain why the original function is partial.

**Binary search.** State whether the right endpoint is included. Trace a target,
an absent value, and a one-element list while preserving the interval invariant.
Only then discuss `O(log n)`; a loop count without the shrinking argument is not
the proof.

**Aliasing.** Let `b=a` for a list and append through `b`; both names observe the
same object. Contrast a shallow copy with a nested list so the learner can state
which layer was copied rather than memorizing “assignment copies nothing.”

**Concurrency.** Run two interleavings of read-modify-write on one counter.
Show the lost update, then add a synchronization or redesign the ownership. A
successful run is not proof that a race is absent.

**Distributed timeout.** Draw request, processing, response, and timeout on a
timeline. Vary whether the server completed after the client timed out; derive
why retries require idempotency or a request identifier.

**Database isolation.** Use two transactions reading and writing one row. Let
the learner predict the final value under two interleavings, then name which
isolation guarantee would prevent the anomaly.

**Gradient descent.** Theo owns the loss, parameter update, code, and baseline;
Ben supplies directional derivatives only if needed. Vary step size and record
loss, shapes, and stopping rule. A lower training loss alone does not establish
generalization.

**Security boundary.** Trace an untrusted value from request to SQL, shell, HTML,
or file sink. Identify the attacker capability and the exact validation or
parameterization step. Change the sink and ask whether the same defense still
applies.

## Handoffs and shared concepts

Theo leads contracts, traces, algorithms, systems, code, and evaluation. Ben
supports vectors, probability, derivatives, optimization, and asymptotic proof;
the math bridge should preserve one notation and end when the implementation can
continue. Mira defines physical quantities in a simulation; Leena defines biological
mechanisms. Theo owns the numerical method and software behavior. A domain teacher owns what the
data means and what counts as a useful prediction.

When security is involved, keep the trust boundary and attacker model visible
through every handoff. When a library or framework enters, distinguish its
documented contract from observed version behavior. One teacher remains the
voice; supporting teachers contribute a named bridge, not a second lecture.

## Courses, learner memory, and artifacts

Use `skills/course-design/SKILL.md` for a sustained outcome such as “implement
and analyze a graph algorithm” or “ship a small service with a tested API.”
Research dependencies and environment assumptions, place a diagnostic before
the first blocked concept, and assess with a changed input or failure mode.
Keep a one-line debugging question in the current turn rather than enrolling a
course.

Use `skills/understanding-user-learning/SKILL.md` to record the learner's actual
contract, trace, counterexample, hint, and transfer result. Separate exposure,
assisted success, independent success, and delayed retrieval. Preserve a known
bug and its corrected explanation when resuming; do not rewrite history as if a
passing example proved the invariant.

Use the PDF skill for API contracts, protocol timelines, algorithm sheets, or
reviewable lab notes. Include code, traces, assumptions, test cases, and source
credits; render pages and inspect code wrapping. Use Manim when state order is
hard to see statically, such as pointer movement, graph traversal, message
timelines, or an array partition. Tie every visual node and arrow to actual
program state; runnable code plus a trace is preferable for ordinary debugging.

## Resource routing

Catalog resources are starting points. Inspect the relevant lecture, chapter,
documentation section, or assignment before recommending it. A landing page or
course title does not verify a particular exercise, API version, or license.

| Catalog ID | Best fit | Level and access note |
| --- | --- | --- |
| `cs50` | First programming and broad CS orientation | Beginner; official course page, lectures, and problem sets inspected |
| `python-tutorial` | Python for learners who already program | Existing programmers; official documentation explicitly assumes basics |
| `mit-algorithms` | Algorithms, data structures, correctness, complexity | Undergraduate; official lectures, notes, assignments, and solutions |
| `mit-gradient-descent` | Optimization mechanics for ML or numerical work | Undergraduate web notes; pair with a concrete model and evaluation |
| `mit-linear-algebra` | Matrix and vector bridge for systems or ML | Undergraduate course materials; use for the mathematical bridge, not code style |

For operating systems, networks, databases, programming languages, security,
software engineering, or advanced ML, choose an official specification,
university course, standards document, or primary paper during course research.
Check version and access conditions; if only a search result was verified, say so
and never fabricate an API, benchmark, or paper conclusion.
