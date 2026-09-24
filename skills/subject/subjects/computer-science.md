# Computer science

Teacher: `teachers/computer-science/SOUL.md` (Theo Park).

Choose the branch by the behavior the learner wants to explain or build.
Name inputs, outputs, state, and failure assumptions. Develop a small working
case before adding an abstraction. A passing run is evidence about that run;
use an invariant or argument for a claim over all inputs.

## Ways to show the idea

Use [Excalidraw](../../excalidraw/SKILL.md) for structure and boundaries,
[Manim](../../manim-voice-animation/SKILL.md) for narrated state changes, and
[Pinepaper](../../pinepaper/SKILL.md) for linked or interactive diagrams.
Code and traces connect those pictures to executable behavior. Use a graph
for measured cost or scaling; do not infer complexity from a timing curve.
Read [the CS reference](../references/computer-science.md) when the lesson
needs a detailed trace, invariant, or visual construction pattern.

Theo leads the explanation. Math supports a specific proof or quantitative
step; the application subject owns the meaning of data and success.

## Teaching each area

Choose the matching section. Its order suggests how to build the topic; it is
not a complete syllabus. Course design uses the starting point and source
checks. Lesson design chooses the views that explain the difficult steps.
Treat the named confusion as a possibility, not a diagnosis of this learner.

### Programming

- **Build:** Start with a small input and what each executed line changes. Assignment
  can share an object. A function call needs a return path and state.
- **Research:** Inspect the language reference and a small runnable example for the
  actual version. Separate language guarantees from library behavior.
- **Show and check:** Runnable code anchors behavior. A trace table records values. A
  memory or call-stack diagram explains identity and lifetime. Change a boundary input.

### Data structures

- **Build:** Start with a collection and the operations it must support. A logical
  sequence and its memory representation are different.
- **Research:** Use a data-structures chapter and the chosen runtime documentation.
  Check ownership, operation costs, and iterator or mutation guarantees.
- **Show and check:** Use [Excalidraw](../../excalidraw/SKILL.md) for a fixed
  array, node, reference, or ownership relation. Use Pinepaper when insertion,
  deletion, or rebalance must update links and the code trace together. Check
  the invariant at every shown state.

### Algorithms

- **Build:** Start with a small problem and a simple solution, then the repeated work an
  improved method avoids. Following an animation does not explain correctness or
  complexity.
- **Research:** Inspect a university algorithms chapter with pseudocode and proof. Check
  the input domain, invariant, termination argument, and cost model.
- **Show and check:** Trace one input in a table first. Use Pinepaper when the
  learner needs to step through a graph and see the frontier, current node,
  and code state together. Use Manim for a narrated search or sort. Derive
  cost from the trace and test a changed input.

### Systems and operating systems

- **Build:** Start with one program operation crossing a named system boundary. A
  language value, virtual address, and physical location are different accounts.
- **Research:** Use an operating-systems chapter for the mechanism and platform
  documentation for actual behavior. Check the memory model or system-call contract.
- **Show and check:** A layered diagram locates responsibility. Logs or a memory trace
  show events. A scheduling simulation tests interleavings or resource limits.

### Networks and distributed systems

- **Build:** Start with one message exchange and what each participant knows. A timeout
  cannot distinguish a failed server from a lost response.
- **Research:** Inspect the protocol specification for messages and guarantees. Use a
  distributed-systems chapter or original paper for failure assumptions.
- **Show and check:** An Excalidraw sequence diagram compares success and
  delayed response. Use Pinepaper if changing delay, loss, or retry must
  update message lanes and visible state together. Logs check the order and
  the claimed guarantee.

### Relational data and queries

- **Build:** Start with a small dataset, a question, and the rows needed to answer it. A
  join can duplicate rows. A diagram alone does not explain query results.
- **Research:** Use a relational-database chapter for keys and query meaning. Check
  official engine documentation for NULL, ordering, constraints, and query plans.
- **Show and check:** Use tables for exact rows and [Excalidraw](../../excalidraw/SKILL.md) for keys and relations.
  Walk through a join beside SQL. Compare a missing or duplicate key. Use a plan tree
  when explaining execution cost.

### Transactions and storage

- **Build:** Start with two operations sharing data, then the failure or interleaving
  the database must handle. Isolation, atomicity, and durability describe different
  guarantees.
- **Research:** Inspect the engine documentation for the chosen isolation level and
  recovery behavior. Use a database-systems chapter for locking, logging, indexes, or
  storage.
- **Show and check:** Use [Excalidraw](../../excalidraw/SKILL.md) transaction lanes or index pages. Use Manim when
  lock order, a page split, or recovery sequence needs narration. Run or label the event
  trace and check the state after an interruption.

### Theory and languages

- **Build:** Start with a tiny language or machine and an accepted string. One accepted
  example does not establish the language. Syntax differs from meaning.
- **Research:** Use a theory or language-semantics text with explicit definitions and
  proofs. Verify the accepted language and the domain of each claim.
- **Show and check:** A parse tree exposes grouping. A transition table traces
  acceptance. A near-miss tests the rule. A proof connects the cases to a general claim.

### AI and machine learning

- **Build:** Start with a prediction task, baseline, and held-out case. A working
  implementation does not establish generalization.
- **Research:** Inspect official implementation documentation and a reproducible
  evaluation. Use the AI guide for model assumptions and evidence.
- **Show and check:** Code traces one prediction. A shape diagram tracks data. An error
  table compares the baseline. Use the AI guide for model and evaluation claims.

### APIs and software design

- **Build:** Start with one caller request, the promised response, and what can fail. A
  successful response does not define retry safety, compatibility, or every failure
  case.
- **Research:** Inspect the API specification, provider documentation, and relevant
  protocol standard for the actual version. Check authentication, errors, pagination,
  timeouts, and retries as needed.
- **Show and check:** Use [Excalidraw](../../excalidraw/SKILL.md) for services,
  interfaces, and a fixed request path. Pair it with concrete requests and
  responses. Use Pinepaper only when timing, a retry, or a timeout changes the
  visible state. Trace an invalid input without inventing service behavior.

### Security

- **Build:** Start with an asset, an untrusted input, and the boundary it crosses. A
  defense depends on the exact operation and attacker capability.
- **Research:** Inspect the relevant security or interface specification and a minimal
  reproducer. Verify the source-to-sink path and the guarantee of the defense.
- **Show and check:** Use [Excalidraw](../../excalidraw/SKILL.md) for trust boundaries and data flow. Pair it with
  the vulnerable and corrected operation. Test a changed input or sink. Label examples
  separately from evidence about a deployed system.

## Source use

Use [the source-use guide](../references/source-use.md). Catalog entries are
leads; inspect the relevant section before using it. Match the source to the
subfield and question. Start with an accessible explanation, then inspect the
technical argument or evidence needed for the agreed depth. Record the section,
its job, and any access limit in the course research notes.
