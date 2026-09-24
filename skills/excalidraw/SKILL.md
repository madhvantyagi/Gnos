---
name: excalidraw
description: Create inspectable teaching diagrams with the Excalidraw MCP server when a lesson needs a clear relationship, process, state, or boundary sketch.
---

# Excalidraw diagrams

Use Excalidraw when the learner needs to inspect a spatial relationship: what
connects, contains, changes state, or crosses a boundary. The selected subject
guide decides **what must be true** in the picture. This guide decides **how to
draw and check it**. A diagram should answer one question, not decorate a lesson.

## Load only the instructions you need

1. Read this page before using the `excalidraw` MCP server.
2. Read [color and type](references/color-and-type.md) for every diagram. Set
   the meaning of each color and the label hierarchy before drawing.
3. Read the relevant pattern in [diagram types](references/diagram-types.md)
   for the relation in the lesson brief. Combine patterns only when the claim
   requires it.
4. Read [review and handoff](references/review-and-handoff.md) before sending
   the result to the lesson coordinator.

The link to this page loads guidance only. A selected Excalidraw block is
produced by calling the `excalidraw` MCP server's `read_me` and `create_view`
tools, then inspecting the returned scene.

Keep the diagram's terms, symbols, units, arrow direction, and color meanings
identical to the surrounding explanation and exercises. If the brief does not
specify these, establish them from the active lesson.

## Build the scene

1. Write the claim in one sentence: “A learner can see that …”. List the
   objects and the relation needed to support that claim.
2. Call `read_me` before the first `create_view` in a task, unless its current
   element format is already in context. Its schema is authoritative; do not
   guess field names, fonts, export commands, or link format.
3. Sketch the reading order and choose a camera that makes labels readable at
   the inline viewport. Place boundaries behind the objects they contain.
4. Call `create_view` with the schema returned by `read_me`. Draw in the order
   the learner should encounter the idea. Keep a final overview in frame.
5. Open the rendered view and perform the checks in
   [review and handoff](references/review-and-handoff.md). Revise a specific
   defect; stop when the relation is accurate and legible.

If the server fails, make one correction based on its error. If it remains
unavailable, use prose, a table, Mermaid, or a runnable trace and tell the
coordinator what was substituted. Do not claim an Excalidraw view or ready
artifact without an inspected result.
