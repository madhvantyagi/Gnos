# Excalidraw diagrams for computer science

Use the bundled `excalidraw` MCP server when a spatial representation makes a
computer-science relationship easier to inspect than prose or code alone. The
server is a teaching instrument, not a decoration requirement.

## Tool order

The server exposes `read_me` and `create_view`.

1. Call `read_me` before the first `create_view` call in a task unless its
   current format instructions are already present.
2. Decide the claim the diagram must make before constructing elements.
3. Call `create_view` using the element format returned by `read_me`; do not
   invent parameters from memory.
4. Inspect the rendered result for overlaps, clipped labels, incorrect arrow
   directions, and relationships that contradict the explanation.
5. Revise only when the diagram is materially unclear or incorrect. Do not add
   detail merely to make the canvas busier.

If either tool fails, use the returned error to make one bounded correction.
If the server remains unavailable, continue with text, a Markdown table,
Mermaid, or a runnable trace. Never claim that an Excalidraw diagram was
created when the tool did not return one.

## When a diagram earns its place

Use Excalidraw for relationships whose meaning depends on position, connection,
direction, containment, ownership, or change across time:

| Topic | Diagram should expose |
| --- | --- |
| Data structures | Node identity, references, ownership, and mutation |
| Algorithms | Current state, invariant, frontier, and next transition |
| System architecture | Components, interfaces, data direction, and failure boundaries |
| Operating systems | Process or thread ownership, scheduling, memory, and shared resources |
| Networks | Hosts, protocol layers, request direction, delay, loss, and retry paths |
| Distributed systems | Per-participant timelines, messages, clocks, failures, and recovery |
| Databases | Entities, keys, relationships, transaction boundaries, and replication |
| Security | Trust boundaries, untrusted sources, validation points, and sensitive sinks |
| AI systems | Data, training, inference, retrieval, evaluation, and feedback boundaries |

Prefer runnable code with a trace for ordinary debugging, a table for compact
comparisons, and prose for one local distinction. A diagram is usually wasteful
for a syntax error, a single algebraic step, or a concept the learner already
understands from the execution trace.

## Diagram construction rules

- Begin with the learner's question as the diagram's purpose. Do not attempt to
  draw an entire field when one relationship is confusing.
- Use a stable reading direction. Left-to-right is the default for data flow;
  top-to-bottom is often clearer for layers or call stacks.
- Give every arrow a meaning. Direction can represent control, data, reference,
  dependency, message, or time, but do not mix meanings without labels.
- Show identity separately from value when aliasing, pointers, mutation, or
  shared state matters.
- Put trust, process, transaction, address-space, or service boundaries around
  the objects they contain. A label beside unrelated boxes is not a boundary.
- Use two or more numbered states when order matters. Do not encode an entire
  algorithmic transition in a single crowded picture.
- Keep labels short enough to read at the initial viewport. Put supporting
  explanation in the lesson rather than shrinking paragraphs into boxes.
- Use color consistently and never as the only carrier of meaning. Preserve
  labels, shapes, or line styles for learners who cannot distinguish the colors.
- Distinguish a conceptual model from observed runtime behavior. A diagram of
  an intended architecture does not prove that the implementation follows it.

## Teaching patterns

**Aliasing.** Draw variable names separately from heap objects. Let two names
point to one list, mutate through one name, and keep the object identity fixed.
For a shallow copy, create a second outer object while retaining shared arrows
to nested objects.

**Graph traversal.** Show the graph, visited set, and queue or stack as separate
regions. Update them together for each numbered state so the learner can relate
the abstract frontier to the actual data structure.

**Distributed timeout.** Give the client and server separate vertical lanes.
Place request, server work, response, timeout, and retry on a time axis. Include
the case where work completes but the response is lost; this is the case that
makes idempotency necessary.

**Database isolation.** Give each transaction its own lane and place reads,
writes, locks, and commit points in order. The learner should be able to point
to the interleaving that creates the anomaly.

**Security boundary.** Trace one untrusted value from its source to its sink.
Mark the exact validation, encoding, parameterization, or authorization check.
Changing the sink should make it possible to ask whether the same defense still
applies.

## Pair the visual with reasoning

Introduce the diagram with the question it answers. After rendering, explain
the smallest path through it and ask for a prediction under one changed input,
failure, or boundary condition. The diagram supports the explanation; it does
not replace the learner's reasoning or serve as evidence that they understood.
