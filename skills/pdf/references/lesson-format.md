# Lesson source format

The builder accepts JSON with `title`, optional `subtitle`, and a nonempty
`sections` list. Each section has `heading` and `blocks`. Each block has `type`:

| Type | Fields | Use |
| --- | --- | --- |
| paragraph | `text` | Plain text; XML characters are escaped |
| bullets | `items` (strings) | Parallel points |
| equation | `path`, `caption` | Pre-rendered local equation image |
| image | `path`, `caption`, optional `width` (points) | Local PNG/JPEG figure |
| table | `headers`, `rows` | Short comparisons; wraps cell text |
| code | `text` | Short preformatted code; wrap long lines yourself |
| pagebreak | no extra fields | Intentional section or exercise boundary |

Optional `sources` is a list of objects with `title` and an `https://` or
`http://` URL. Source links appear in a final reference section. Image paths
resolve relative to the lesson JSON file, not the working directory. The builder
does not download remote images or execute content in the lesson.

Do not pack a textbook into a table cell. Split large tables by topic. Long
content can flow over pages, but one cell must still fit a page. Equations can
be prepared with:

```bash
python3 skills/pdf/scripts/render_equation.py 'f(x)=x^2' -o output/equation.png
```

The helper uses Matplotlib mathtext (a LaTeX subset), not a full TeX engine.
Unsupported notation fails visibly; use an installed TeX renderer for that case.
Keep equation source with the lesson-generation script.

Fonts: `--font-dir` must contain `DejaVuSerif.ttf`, `DejaVuSans.ttf`,
`DejaVuSans-Bold.ttf`, and `DejaVuSansMono.ttf`. System locations are searched
when omitted. GNOS does not redistribute host font files.
