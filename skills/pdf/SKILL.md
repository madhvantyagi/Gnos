---
name: pdf
description: Create GNOS lesson handouts and course PDFs with embedded fonts, equations, images, exercises, and source credits; render and inspect before delivery.
---

# Lesson PDFs

Build a document the learner can return to without the conversation. Keep the
teaching sequence visible: question, explanation, worked example, changed case.
Use headings to mark conceptual changes rather than decorating every paragraph.

1. Select the lesson's outcome and audience. Read only the necessary teacher and
   subject context. Do not print internal learner records or hidden assessment
   criteria in a handout unless requested.
2. Read [references/lesson-format.md](references/lesson-format.md). Author a
   structured lesson JSON next to its local images; keep this editable source.
3. Generate with `python3 skills/pdf/scripts/build_pdf.py lesson.json -o output/lesson.pdf`.
   Dependencies: ReportLab and Pillow. The optional equation helper uses Matplotlib.
4. Render pages with `pdftoppm -scale-to 1400 -png output/lesson.pdf output/lesson`.
   Inspect every page. Check equations, captions, page breaks, text size, and
   source links; extraction alone cannot establish visual quality.
5. Extract text with `pdftotext` or `pypdf` and check for omissions or missing
   glyphs. Deliver the PDF with its editable source. State any unverified layout.

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
`examples/lessons/gradient/lesson.json` exercises the builder with equations,
an image, a comparison table, and a worked example.
