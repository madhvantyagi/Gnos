---
name: pinepaper
description: Build and check Pinepaper MCP diagrams, charts, motion, and interactive models when a lesson needs linked visual states or a changing quantity.
---

# Pinepaper

Use the `pinepaper` MCP server for a lesson view whose parts must stay linked or
change together. Start with the selected subject guide and the block brief.
Name the question the learner should answer from the scene. Keep the same
objects, symbols, units, and example as the surrounding lesson.

## Choose the visual job

- For a fixed relationship or boundary, read [diagrams](references/diagrams.md).
  Use [Excalidraw](../excalidraw/SKILL.md) when a quick static sketch is enough.
- For a plotted quantity, curve, or linked numerical view, read
  [charts and quantities](references/charts-and-quantities.md). Keep exact values
  in a table or reproducible calculation.
- For ordered states, physical motion, waves, or a model such as heat transfer,
  read [motion and models](references/motion-and-models.md).
- For learner controls or any finished file, read
  [interaction and export](references/interaction-and-export.md). Choose the
  export before building features that the format cannot preserve.

One lesson may combine a diagram, graph, and motion around the same state.
Each view must reveal a different part of the explanation. Do not make the
learner infer which curve, arrow, or moving object corresponds to a number in
the text.

## Build through the MCP server

1. Write a short scene brief: claim, objects, source of quantities, units,
   what changes, and the expected output file. Decide what the learner will
   predict or compare.
2. Read the current tool schema. Use `pinepaper_tool_guide` for a tool family
   or `pinepaper_query_capabilities` for a specific missing capability. The
   server schema wins over examples in these files.
3. Call `pinepaper_agent_start_job` with the canvas preset and a description
   of the teaching claim. Plan positions and labels at the size the learner
   will see in the course viewer.
4. Use one `pinepaper_agent_batch_execute` for the base scene when its
   operations cover the job. Reuse its `$0`, `$1`, and later item references.
   Call a specialized tool, such as `pinepaper_create_chart`,
   `pinepaper_equation_path`, or `pinepaper_physics`, when the scene needs that
   capability. Do not approximate a chart or physical rule with decorative
   movement. Check the returned result of every operation.
5. Run `pinepaper_validate_scene`. Inspect the initial state and a meaningful
   changed state with a screenshot or playback. Check labels, scales, arrow
   meanings, clipping, and whether the graph and motion agree. Repair failed
   operations or unwired relations before finishing.
6. Call `pinepaper_agent_end_job`, inspect its final image, then export through
   `pinepaper_agent_export` or the specialized export tool required by the
   deliverable. Open the exported file. A correct editor scene is not proof
   that its export works.

Use named tools for ordinary production. Use `pinepaper_execute_custom_code`
only for a bounded scene behavior the tool surface cannot express, and check
the generated values against the lesson's model. A visually plausible model
is still a model. Label measured data, sourced data, assumptions, and simulated
outputs distinctly.

## Hand off a checked artifact

Return the file, MIME type, title, purpose, source or model assumptions, and
one learner question to the lesson coordinator. The coordinator alone updates
the lesson and registers the artifact. Check the export in the course viewer
before calling it ready. If the server is unavailable, use its diagnostic
report when available, make one error-based correction, and report the
remaining limitation. Never describe an unmade scene as finished.
