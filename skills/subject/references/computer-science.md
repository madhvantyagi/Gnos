# Computer-science depth and visual patterns

Read this reference when a CS lesson needs prerequisite diagnosis, a sustained
example, source selection, or a substantial diagram or animation. The concise
route remains in [the subject guide](../subjects/computer-science.md).

Use the guide's 'Ways to show the idea' section first, then apply
`skills/lesson-design/references/representation-choices.md`. This reference
defines CS content and visual grammar; it does not order media by itself.

## Prerequisite checks

- Programming: values versus names, mutation, control flow, and input
  contracts. Try empty, singleton, duplicate, and malformed inputs.
- Algorithms: functions, induction, sets, and asymptotic notation. Ask what
  remains true after one iteration or recursive call.
- Systems: binary representation, memory ownership, process versus thread, and
  blocking versus nonblocking behavior. A language runtime detail is not a
  universal machine rule.
- Networks: message timeline and failure model. A timeout means a response was
  not observed.
- Databases: keys, joins, constraints, and transaction boundaries. Returned
  rows do not establish durability or isolation.
- AI: vector shapes, probability, derivatives, leakage, and evaluation split.
  A plausible output is not a reliability measurement.
- Security: asset, boundary, attacker capability, source, sink, and validation.
  Require an actual path before calling a bad input exploitable.

## Teaching patterns

**Recursion.** For factorial on nonnegative integers, name base case `n=0` and
progress `n-1`. Extend the input contract to negative values; require a policy
or an explanation that the original function is partial.

**Binary search.** Fix whether the right endpoint is included. Trace a target,
an absent value, and a one-element list while preserving the interval
invariant. Connect `O(log n)` to the shrinking interval.

**Aliasing.** Let two names reference one list and mutate through one name.
Contrast that with a shallow copy of a nested list so object identity stays
visible at each layer.

**Concurrency.** Show two read-modify-write interleavings on one counter. Locate
the lost update, then add synchronization or change ownership. One successful
run does not establish the absence of a race.

**Distributed timeout.** Put request, work, response, timeout, and retry on
client/server lanes. Include a completed operation whose response is lost; this
is the case that makes idempotency or request identity necessary.

**Database isolation.** Put two transactions in separate lanes with reads,
writes, locks, and commits. Change the interleaving and ask which isolation
guarantee prevents the anomaly.

**Gradient descent.** Keep loss, parameter update, shapes, baseline, and data
split separate. Vary step size and stopping rule; lower training loss alone does
not establish generalization.

**Security boundary.** Trace one untrusted value to SQL, shell, HTML, or file
sink. Mark the exact validation, encoding, parameterization, or authorization
step. Change the sink and retest whether the defense still applies.

## Visual patterns

Use these patterns with the producer selected by lesson design. A static
diagram, narrated sequence, or interactive trace can develop the same CS
relation in different ways. Read the producer's workflow before using it.

### Algorithm state

For BFS, Dijkstra, dynamic programming, or partitioning, keep the structure,
frontier, visited or finalized state, and current invariant in distinct regions.
Animate one transition at a time. Retain the previous state faintly and pause
before the next choice so the learner can predict it. Drive labels from the
actual state values rather than decorative narration.

### Memory and ownership

Draw names, objects, addresses or identities, and ownership boundaries as
different visual types. Animate reference changes without moving the underlying
object unless the object itself changes. For shallow copy, duplicate only the
outer object and preserve shared nested references.

### Protocols and concurrency

Use vertical participant lanes and a shared time direction. Messages, local
work, locks, timeouts, retries, and crashes need distinct marks. Keep the
failure model on screen. For a race, animate two valid local steps whose global
interleaving violates the invariant.

### Architecture and data flow

Give arrows one meaning: call, data, event, dependency, or trust transition.
Put process, service, address-space, transaction, and trust boundaries around
their contents. Animate a single request or record through the system, including
the failure path being discussed.

### Interactive checks

When interaction improves learning, let the learner step forward, reset, or
choose the next transition. The same scene state should drive visuals and
labels. Validate that every declared relation is wired before export.

## Tool and medium decision

- Use code plus a trace for ordinary debugging.
- Use [Excalidraw](../../excalidraw/SKILL.md) for a quick static relationship or boundary.
- Use [Pinepaper](../../pinepaper/SKILL.md) when a code step must update
  pointers, graph state, or a visible trace together. Check its export format
  before choosing a chart or learner control.
- Use Manim when narration and a rendered lesson timeline are the deliverable.

Do not duplicate the same scene across media unless the outputs serve different
learning or distribution needs.

## Handoffs and sources

Theo leads implementation and system behavior. Ben supports vectors,
probability, derivatives, optimization, and asymptotic proof. Mira defines
physical quantities in simulations; a domain teacher defines what data means.
Carry the last sound claim, notation, and unresolved invariant through the
handoff.

Catalog starting points are `cs50`, `python-tutorial`, `mit-algorithms`,
`mit-gradient-descent`, and `mit-linear-algebra`. Inspect the relevant section
before assigning it. For operating systems, networks, databases, languages,
security, software engineering, or advanced ML, use an official specification,
university course, standards document, or primary paper and verify its version.
