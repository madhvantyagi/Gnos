# Diagrams with linked parts

Use Pinepaper when a diagram needs precise repeated layout, connectors that
stay attached, or several states that share one visual grammar. For a single
static boundary or relationship, use [Excalidraw](../../excalidraw/SKILL.md).

Name the entities before drawing. Place containment boundaries behind their
members. Label arrows with the thing transferred or the action performed.
Keep direction and arrow meaning fixed. A causal arrow, a physical flow, and
a sequence arrow are different claims; give them different labels or styles.

Use `pinepaper_create_diagram_shape` and connector or relation tools when
ports and attachment matter. Use the agent batch for ordinary shapes and
relations. Confirm from the current tool schema which relation connects each
pair. After creation, inspect the scene graph or item list if a connection
looks detached. A connector drawn near a box is not proof that it follows
the box.

For a before and after view, keep unchanged objects in the same positions.
Change the relevant edge, value, or label. For a process, show one concrete
input passing through named stages, then ask what the next stage receives.
For a comparison, use the same scale and labels on both sides. Preserve a
visible reference state if the learner must compare it with the new state.

For a dated map, use the map tools only with checked geography and source
dates. Mark reconstructed boundaries or routes. Inspect the chosen scale and
region before drawing conclusions from distance or area. Pinepaper's export
matrix shows that maps need a checked still or video file; they do not survive
SVG or widget export.

Check that the labels remain readable in the exported image at the course
viewer's inline size. Keep paragraph-length explanations in the lesson.
