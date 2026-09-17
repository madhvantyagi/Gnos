# Search before you promise a course

Search first. Do not copy the first syllabus you see.
Use books, course sites, and docs you can open.

## Scale to the agreed depth and length

The `depth` and `length` recorded in `course.json` decide how much to
search and what to take:

| depth | research effort |
| --- | --- |
| `survey` | One main source for the route is enough; take definitions and the step order. |
| `working` | Main source plus one contrast source that changes or checks a step; take exercise ideas from both. |
| `mastery` | Two or more sources, including a primary or academic one; take the derivation path, counterexamples, and harder exercises. |

A short length means fewer topics per source and lighter media; a term
means enough material to fill it honestly. Do not inflate a survey into
a mastery bibliography, and do not promise a term on one skimmed page.

## Where to look

- **Books:** open textbook contents, for example `site:openstax.org <topic> contents`.
- **Course sites:** syllabus and prerequisites, for example `site:ocw.mit.edu <topic> syllabus`.
- **Docs and papers:** for software read the installed version.
  For disputed topics read the paper itself, not a summary.
- The starter list `skills/subject/references/resources.json`
  is ideas only. Every course starts empty. Search fills it.

One main source for order plus one second source to test it is enough.
The second source counts when it changes a step, not when it repeats it.

## What to take

- the definition in the author's words, plus page or section
- what must come before this step
- one exercise idea that shows a wrong idea fast
- who it is written for, and could you open it

A search snippet is a lead, not proof. If you did not open it,
say so.

## What to save

Keep short notes beside `course.json`. Only sources you will use
move into `course.json/sources`.

1. `RESEARCH.md` — small table: step, source and section,
   what you checked, what is still open, what you chose.
2. `course-research.json` — same facts, short form:

```json
{
  "goal": "predict small changes with derivatives",
  "sources": [
    {
      "id": "mit-1802-sec2",
      "title": "MIT 18.02 notes",
      "url": "https://ocw.mit.edu/example/18-02-notes",
      "opened_sections": ["Chain rule examples"],
      "gives": ["plain definition", "step order", "sign exercise"],
      "trust": "opened",
      "used_in": ["chain-rule"]
    }
  ],
  "open_questions": ["fluency unverified"]
}
```

Rules:

- `id` must match the key you use in `course.json/sources`.
- `trust` is `opened` only when you read it. Else use `snippet`
  and do not call it checked.
- `used_in` lists step IDs it supports. Empty means you skipped it.
- `queries` are optional. For a small course, skip them.
  Keep only what you use. Ten searched links do not belong here,
  only the two or three you teach from.
