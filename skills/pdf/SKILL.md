---
name: pdf
description: Turn lesson content into a PDF handout; render and check it before delivery.
---

# Lesson PDFs

Build a document the learner can return to without the conversation. Keep the
teaching sequence visible: question, explanation, worked example, changed case.
Use headings to mark conceptual changes rather than decorating every paragraph.

Run the commands below with the project's `.venv/bin/python` when that
environment is present. Check that interpreter before treating a missing
package in the system Python as a missing PDF capability. For a fresh
environment, install `skills/pdf/requirements.txt` there.

1. Select the lesson's outcome and audience. Read only the necessary teacher and
   subject context. Do not print internal learner records or hidden assessment
   criteria in a handout unless requested.
2. Write the lesson as Markdown or use an existing README. Place diagrams and
   image-model outputs beside it and reference them with `![caption](image.png)`.
   HTML `<img src="..." alt="...">` works too. Keep captions and source credits.
3. Convert with `python3 skills/pdf/scripts/markdown_to_pdf.py lesson.md -o output/lesson.pdf`.
   This also writes editable lesson JSON. Dependencies: ReportLab, Pillow,
   markdown-it-py; Matplotlib supplies fonts and equation rendering. Fenced
   `math` blocks render as equations. Remote images become explicit source links;
   save a permitted local image first when the figure must appear in the PDF.
   For precise block control, use `build_pdf.py lesson.json -o output/lesson.pdf`;
   see [references/lesson-format.md](references/lesson-format.md).
4. Render pages with `pdftoppm -scale-to 1400 -png output/lesson.pdf output/lesson`.
   Inspect every page. Check equations, captions, page breaks, text size, and
   source links; extraction alone cannot establish visual quality.
5. Extract text with `pdftotext` or `pypdf` and check for omissions or missing
   glyphs. Deliver the PDF with its editable source. State any unverified layout.

## Register the artifact

The viewer page shows the topic's `pdf` chip as ready only after the
PDF is registered. Copy it into the course workspace, then register:

```bash
cp output/lesson.pdf learners/<learner>/courses/<course-id>/artifacts/documents/<slug>.pdf
python3 skills/course-design/scripts/manage_artifact.py --learners-root learners \
  register <learner-id> <course-id> --file artifact.json
```

Use `type: document`, `mime_type: application/pdf`, the topic's
`lesson_id`, and `status: ready`. Then re-render the page:

```bash
python3 skills/course-viewer/scripts/render_viewer.py learners/<learner>/courses/<course-id>
```

## Typography and figures

Use a calm hierarchy: serif body, sans heading, mono code; 11–12 pt body with
comfortable leading and margins. The builder embeds DejaVu fonts when found;
use `--font-dir` for another installation of that family. It fails if the font
set is incomplete rather than silently substituting missing glyphs.

Keep diagrams labeled and interpretable without color alone. Preserve image
aspect ratio; avoid enlarging a tiny raster into a blurry page. Keep the caption
with the figure. Include source/creator and whether a diagram is schematic.
Use actual math rendering for equations; do not send raw LaTeX to paragraph text.

Read [references/visual-review.md](references/visual-review.md) when inspecting.
`examples/lessons/gradient/README.md` exercises the builder with equations,
an image, a comparison table, and a worked example.
