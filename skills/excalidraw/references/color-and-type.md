# Color and type

Start from the lesson's existing symbols and color meanings. This palette is
the default for a **new** diagram, not permission to recolor a continuing
example. Assign colors to roles in the brief and carry the mapping through
every state and caption.

| Role | Fill | Stroke | Meaning |
| --- | --- | --- | --- |
| Input or source | `#a5d8ff` | `#4a9eed` | A value entering the relation |
| Process | `#d0bfff` | `#8b5cf6` | An operation, not its result |
| Stored state | `#c3fae8` | `#087f66` | The same object across states |
| Result | `#b2f2bb` | `#16803c` | A confirmed output |
| Warning or pending | `#ffd8a8` | `#9a5a00` | A condition to inspect |
| Error or rejected path | `#ffc9c9` | `#b42323` | An invalid state or failed path |

For a dark scene, keep the same roles and meanings with these fills, light
strokes, and white labels. The preview in the brief's image shows each pairing.

| Role | Fill | Stroke |
| --- | --- | --- |
| Input or source, slate sapphire | `#263A53` | `#6F92B8` |
| Process, royal plum | `#493456` | `#A47BB5` |
| Stored state, petrol teal | `#164B4A` | `#54A8A3` |
| Result, heritage green | `#31543B` | `#78A97F` |
| Warning or pending, antique bronze | `#65451F` | `#C89248` |
| Error or rejected path, burgundy wine | `#612F3B` | `#C86B78` |

Use dark neutral strokes for ordinary relationships. Reserve color for a
distinction that matters to the claim; two or three roles usually suffice.
Light fills carry category on light scenes and dark fills on dark ones; strokes and labels carry meaning either way. Color is
never the sole signal: add a label, arrow direction, state number, line style,
or shape distinction. Check the view in grayscale. A mapping that disappears
in grayscale needs another cue.

For a boundary, use a pale zone at low opacity behind its members, with a
clear label and outline. Keep unchanged objects the same color across states;
highlight only the changing relation. Do not color an entire canvas or give
one role different colors merely for decoration.

## Type, size, and camera

`read_me` currently documents `fontSize` and labels; it does not promise a
font-family field. Do not invent one. Use the tool's default face throughout.
Put text in a shape's `label` when possible so it stays centered as the shape
resizes. Standalone text is for titles, annotations, and boundary names. Its
`x` is the **left edge**; estimate width before placement. Do not rely on
`textAlign` or `width` to center a single line.

- Title: at least 20 px; one short line naming the relation.
- Object and arrow labels: at least 16 px at the chosen camera.
- Secondary annotation: 14 px only when readable at inline size. Never smaller.
- Use short nouns for objects and verbs or quantities for arrows. Explain the
  reasoning in lesson prose rather than shrinking paragraphs into boxes.
- Give a labeled shape at least 120 × 60 scene units, with 20–30 units between
  adjacent objects and more space around arrow labels.

The server displays views inline at about 700 px wide. Start with a 4:3
`cameraUpdate` before drawn elements: 800 × 600 for an ordinary scene, 600 ×
450 for a compact group, or 400 × 300 for detail. Use 1200 × 900 only if its
labels remain readable. Leave padding inside the camera and finish with a
complete overview. Recheck after render; coordinates cannot prove legibility.
