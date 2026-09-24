# Diagram types

Choose the form from the question in the lesson brief. Each form needs a
reading order, few enough objects to inspect, and one prediction the learner
can make after seeing it.

## Relationship or architecture

Use labeled shapes for actors or components and bound arrows for their
relations. Put a verb or payload on each arrow. If arrow kinds differ, label
both. Group services, address spaces, trust zones, or institutions inside
visible boundaries. Ask what changes if one connection is removed.

## Process or data flow

Place inputs on the left, transformations in the middle, and outputs on the
right unless the subject convention requires another direction. Number steps
when chronology matters. Mark each branch condition at its split. Name what
returns on a return arrow. Do not use one arrow for data and another for time
without a key. Ask the learner to trace a concrete input through the path.

## State, memory, or pointer trace

Separate **identity** (object, address, node) from **value** (contents). For
mutation or an algorithm, draw at least two numbered states. Keep unchanged
objects in the same positions and colors; alter only the relevant value, edge,
or status. Label pointers and ownership separately from values. For many
transitions, use a sequence of views or a runnable trace rather than one
crowded canvas. Ask for the next state before revealing it.

## Comparison or causal claim

Use parallel lanes with the same scale, labels, and object positions. Name
the changed input and annotate the different result. Mark observed evidence
separately from an assumed mechanism; a conceptual arrow does not prove the
mechanism occurred. Ask which observation distinguishes the two cases.

## Quantities and geometry

Use Excalidraw for a qualitative spatial relation: which side is rise or run,
what lies inside a region, or which vector points where. Label axes, units,
origin, direction, and quantities named in the lesson. If exact values,
coordinates, curves, or synchronized numeric states matter, use a graph, code
trace, or [Pinepaper](../../pinepaper/SKILL.md) instead of hand-positioning shapes and
implying precision. Ask the learner to verify the picture with the equation
or data beside it.
