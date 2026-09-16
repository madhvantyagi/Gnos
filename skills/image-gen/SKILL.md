---
name: image-gen
description: Make still lesson images with an image-model MCP server when the topic plan asks for one.
---

# Generated lesson images

Make an image only when the topic's representation plan asks for one
(`kind: image`). Most ideas are better as text, a small table, or
runnable code. Use this skill when one picture can carry what the
lesson needs.

## What makes a good teaching image

- One idea per image. Split a two-part concept into two images.
- Label every axis, object, and step. A label is part of the image,
  not the caption.
- No clutter. Remove decoration and detail that do not carry the idea.
- Readable at half width. The viewer shows images inside a column;
  check text and thin lines at half the exported size.
- Color reinforces meaning; never rely on color alone. Keep one
  meaning per color and line style across the lesson.

## Generate

Call the image-model MCP server with a precise prompt. Name the
subject, the single idea, what must be labeled, what must be absent,
and the viewing size. Read the schema the server exposes; never guess
its arguments. If the server fails, report it and continue with the
smallest faithful static representation. Regenerate when the result is
wrong, not because it looks plain. Inspect before saving: labels
spelled right, nothing cut off, one idea visible at half width.

## Save and register

1. Save the file inside the course workspace:
   `artifacts/generated/` for image-model output, `artifacts/diagrams/`
   for a diagram made another way. Use a short name that says what the
   image shows.
2. Write an artifact file:

```json
{
  "id": "slope-annotated-diagram",
  "type": "image",
  "title": "Secant narrowing to the tangent",
  "purpose": "Show the secant slope approaching the tangent slope.",
  "concepts": ["math.derivative"],
  "chapter_id": "local-change",
  "topic_id": "gradient-direction",
  "lesson_id": "gradient-direction-1",
  "location": {"path": "artifacts/generated/slope-annotated.png"},
  "mime_type": "image/png",
  "metadata": {"width": 1200, "height": 900},
  "status": "ready",
  "created_at": "2026-09-16T10:00:00Z",
  "updated_at": "2026-09-16T10:00:00Z"
}
```

Paths are relative to the course workspace. `chapter_id`, `topic_id`,
and `lesson_id` must exist in `course.json`; `concepts` must belong to
that topic; `lesson_id` must be a published lesson. Use real ISO UTC
timestamps. Register it:

```bash
python3 skills/course-design/scripts/manage_artifact.py --learners-root learners \
  register <learner-id> <course-id> --file path/to/artifact.json
```

Register only the finished image with `status: ready`. Keep a wrong or
unchecked output as `draft`, or `failed` with an honest note.

3. Re-render the learner's page:

```bash
python3 skills/course-viewer/scripts/render_viewer.py learners/<learner>/courses/<course-id>
```

The image appears in the generated section of the page. Re-render after
every new or replaced image.
