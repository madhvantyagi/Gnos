# Charts and quantities

Start from the numbers or equation, not a desired curve shape. Record whether
each value is observed, sourced, calculated, or simulated. Keep the data and
its calculation available in the lesson or a reproducible source. Pinepaper
draws the view; it does not establish the values' truth.

Use `pinepaper_create_chart` for bar, line, scatter, or area charts. Choose
bars for category comparisons, a line for ordered change, scatter for paired
observations, and area when accumulated magnitude matters. Name both axes,
units, population or system, time interval, and any normalization. Use the
tool's `xField` and `yField` mapping for the actual data keys. Show uncertainty
or missing observations when the claim depends on them. If the built-in chart
cannot express a needed interval, distribution, or exact scale, make the
scientific plot with a plotting library and verify it there.

Use `pinepaper_equation_path` for a function or parametric path when the
expression itself defines the curve. Confirm the domain, origin, axis
direction, sample range, and clipping. A smooth sampled path does not prove a
limit, solution, or fit. Compare a point on the path with a hand calculation.

For linked views, identify the same state in the object, graph, and number.
For example, a moving mass and its position-time trace must share one clock.
If a parameter changes, update the path, annotation, and displayed value from
that same parameter. Keep the former path visible when the comparison needs
it. Ask the learner to predict the direction of change before showing it.

Pinepaper's [export matrix](https://pinepaper.studio/api/EXPORT_SUPPORT)
says charts do not survive animated SVG export. Use a checked widget, video,
or still PNG for charts. Do not register an SVG merely because it opens if the
chart is missing. The [chart API](https://pinepaper.studio/api/dataviz/charts)
documents the current chart types and options; check the MCP schema before
using an option.
