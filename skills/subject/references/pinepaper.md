# Pinepaper diagrams and animation

Use the bundled `pinepaper` MCP server when motion, interaction, polished vector
graphics, or a relation-rich diagram reveals something that text or a simple
still cannot. Read the selected subject reference after this file for domain
conventions and examples.

## Choose it deliberately

Pinepaper is a strong fit when the learner must inspect:

- a state or quantity changing through several stages;
- a transformation, orbit, propagation, feedback loop, or moving frontier;
- several linked objects whose behavior should stay synchronized;
- a reusable animated SVG or interactive visual.

Prefer a table for exact values, runnable code for program behavior, Excalidraw
for a quick static CS sketch, and Manim for a narrated rendered lesson. A
diagram should answer one named question rather than summarize an entire topic.

## Efficient tool sequence

Pinepaper exposes a large tool surface. Do not explore it tool by tool.

1. State the visual claim, learner level, final medium, and one transfer
   question before calling tools.
2. Call `pinepaper_tool_guide` for the relevant task only when the needed tool
   family is unclear. Use `pinepaper_query_capabilities` for a specific
   capability search instead of reading the full catalog.
3. Keep the default `agent` toolkit. Switch with `pinepaper_set_toolkit` only
   when a narrower `diagram` surface or a capability outside `agent` is needed.
   Return to the smaller surface after the specialized work.
4. Plan the canvas, objects, relationships, timeline, labels, and export. Then
   call `pinepaper_agent_start_job` with the canvas preset that matches the
   requested result.
5. Put the scene's creates, animations, and effects into one
   `pinepaper_agent_batch_execute` call. Use its local item references rather
   than spending calls fetching IDs. Make a later call only for a correction
   that depends on inspection.
6. Encode behavior as relations when the motion expresses the concept. Use
   named stages or events when the explanation depends on order.
7. Run `pinepaper_validate_scene`. If visual inspection is still needed before
   closing the job, request one `pinepaper_browser_screenshot`. Check labels,
   direction, scale, occlusion, initial and final state, and whether motion
   matches the governing rule.
8. Make only material corrections, then call `pinepaper_agent_end_job` and
   inspect its final screenshot and analysis.
9. Export with `pinepaper_agent_export`, or the specialized export tool whose
   current schema matches the requested deliverable. Prefer animated SVG for a
   portable vector result when its supported features preserve the lesson.

Never guess a tool's arguments. Use the schema exposed by the MCP server and
its guide. If a call reports unwired relations or failed operations, repair
those before export; a scene can render while its intended behavior is inert.

## Design rules for teaching

- Keep a stable visual grammar. Give position, arrows, color, line style, and
  motion one meaning each.
- Put the invariant or governing equation beside the changing object. The
  animation should make the rule inspectable rather than merely move shapes.
- Preserve a visible reference state when comparison matters. Ghost the old
  curve, retain the previous frontier, or show initial and final quantities.
- Use short labels. Put full reasoning in the lesson and connect each equation
  term or claim to its visual object.
- Use color as reinforcement, never the sole distinction. Add labels, shapes,
  patterns, or line styles.
- Keep timing slow enough to predict the next state. Pause at causal or logical
  transitions; decorative looping should not compete with the lesson.
- Mark assumed, simulated, observed, and sourced quantities differently. A
  generated visual is an explanation, not empirical evidence.

## Subject handoff

Read only the reference for the active subject:

- [Computer science](computer-science.md): state, memory, algorithms, networks,
  and systems.
- [Mathematics](math.md): transformations, functions, geometry, optimization,
  and proof-supporting pictures.
- [Physics](physics.md): systems, vectors, fields, waves, and model-bound motion.
- [Economics](economics.md): curves, stocks and flows, games, causal structure,
  and policy dynamics.
- [Political science](political-science.md): institutions, processes, coalitions,
  elections, and implementation chains.

## Failure and fallback

The bundled server starts through `npx` and uses a local headless browser. The
first run can take longer while its pinned packages and browser are fetched.
If the server fails, inspect `pinepaper_diagnostic_report` when available and
make one correction based on the returned error. If it remains unavailable,
continue with the smallest faithful static representation. Never claim an
artifact was created or animated unless the tool returned and the result was
inspected.

Pinepaper generates JavaScript for its browser canvas. Use the named tools for
normal work; reserve `pinepaper_execute_custom_code` for a capability that the
tool surface cannot express, and keep that code limited to the current scene.
