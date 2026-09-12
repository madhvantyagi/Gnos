# Course contract

`course.json` uses `schema_version: 1`. The validator checks shape and
dependencies; the teacher must still judge the content and assessment quality.

Required course fields: `id`, `title`, `goal`, `revision` (positive integer),
`assumptions` (strings), `modules` (nonempty ordered list).

Each module has:

- `id`: stable lowercase slug, unique in the course.
- `title`, `outcome`: plain text; outcome describes a performance.
- `subject`: `math`, `physics`, `history`, `biology`, `economics`, or `computer-science`.
- `teacher`: the same subject ID, resolving to `teachers/<id>/SOUL.md`.
- `supporting_teachers`: other supplied subject IDs, possibly empty.
- `concepts`: stable IDs such as `math.derivative` or `physics.net-force`.
- `prerequisites`: module IDs earlier in this course. Outside prerequisites
  belong in assumptions and the first diagnostic, not as dangling module IDs.
- `minutes`: positive estimate, not an achievement counter.
- `assessment`: `prompt` plus `success_criteria` (nonempty strings).
- `resources`: IDs from `skills/subject/references/resources.json`.

Optional fields include scope notes, selected chapters, artifacts, and revision
notes. The validator tolerates extensions. Preserve their meaning when editing.

## Assessment design

“Do you understand?” is not evidence. Match the performance to the outcome:

| Outcome | Revealing task | What would not establish it |
| --- | --- | --- |
| Explain gradient direction | Predict loss change along a new direction and justify the sign | Repeat the update equation |
| Read historical evidence | Compare two accounts' provenance and limits | Recall two dates |
| Debug a loop | Trace a failing input, repair the invariant, test another boundary | Copy a fixed implementation |
| Explain natural selection | Separate pre-existing variation from differential reproduction in a new case | Say “survival of the fittest” |

For tiny lessons, these fields can stay implicit in a three-line working plan.
JSON is for a persistent, machine-checkable route, not mandatory ceremony.
