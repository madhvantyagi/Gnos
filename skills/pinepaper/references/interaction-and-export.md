# Interaction and export

Choose interaction only when the learner has a useful choice to test. Start
with a prediction, the controls needed to test it, immediate feedback, and a
reset state. Show the current parameter value, units, and the result it
changes. Prevent impossible settings or explain why they are allowed in the
model. A play button alone does not make a simulation.

Use the MCP relation and interaction tools for event or pointer behavior.
Check the initial state, a changed input, reset, and repeated use. Test that
the number, graph, and scene all update together. If the widget cannot expose
the needed control clearly, use the lesson's self-contained HTML simulation
route and verify it in the same viewer sandbox.

Choose the exported file by the learner's job:

| Learner needs | Export to test |
| --- | --- |
| Inspect a fixed diagram | PNG or a supported SVG |
| Inspect a single chart or map state | PNG |
| Watch a full scene, including canvas effects or physics | MP4 or WebM |
| Use click, key, drag, or pointer relations | Self-contained HTML widget |
| Inspect supported vector motion without controls | Animated SVG |

The [Pinepaper export matrix](https://pinepaper.studio/api/EXPORT_SUPPORT)
is the feature check. SVG omits charts, maps, and complex or event relations. PNG
holds one frame. Video preserves motion but no learner control. Widgets keep
charts and interactions, but some canvas effects and 3D features do not
survive. Inspect the exported file, not only the editor scene.

GNOS shows image and video files inline. It runs interactive HTML only when
registered as a `simulation` in the course viewer's restricted iframe. For
that route, return a self-contained HTML file with `text/html`, a responsive
layout, and valid `metadata.dimensions`. Open it at wide and narrow widths.
Check that controls work without relying on the Pinepaper editor or an
external session. Follow the [artifact manifest](../../course-design/references/artifact-manifest.md)
for registration. The lesson coordinator owns that registration.
