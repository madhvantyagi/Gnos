# GNOS design

GNOS is a portable context library operated by a file-capable LLM. Markdown
governs teaching; Python handles records, validation, and media. The host LLM
reads files and calls scripts. There is no background tutor, model API, or
automatic assessment service hidden behind these files.

## Context boundaries

| Layer | Owns | Does not own |
| --- | --- | --- |
| Learning | Turn routing, teaching loop, load order | Teacher biographies |
| Teacher SOUL | Identity, voice, judgment under pressure | Course state |
| Subject | Subfields, prerequisites, representations, sources | General tutor rules |
| Course design | Outcomes, sequence, teacher assignments, assessments | Evidence of progress |
| Learner model | Dated observations, attempts, preferences, next step | Fixed labels of ability |
| PDF / Manim | Artifact construction and verification | Whether the learner understood |

One teacher leads a turn. A supporting subject contributes only the needed
idea; it does not trigger an invented panel discussion. Mathematics is shared
across subjects by concept ID, so vectors are not re-taught under every label.

## Turn flow

1. Read learning. Classify a direct doubt, lesson, course request, or resumption.
2. Load the relevant learner snapshot if an identity is established. Read only
   the active course and recent evidence for the concept at hand.
3. Select subject and teacher. Use course design only when a plan is needed.
4. Teach the missing connection. Choose text, a diagram, an exercise, or motion
   for what it reveals; a media deliverable is not a prerequisite to answering.
5. Record observed evidence and a concrete next step. Persist only when a
   learner identity is established and local tracking is wanted.

`scripts/assemble_context.py` prints this selected context or its file manifest.
It is an explicit loader for hosts without native skill discovery. It does not
classify arbitrary prose or call a model. `AGENTS.md` is the in-repository entry.

## Records and artifacts

`learners/<id>/state.json` contains the profile and ordered session events.
It is private local data, ignored by Git. Updates take a lock and atomically
replace the file. An event ID makes retries idempotent; conflicting reuse is an
error. Each event separates coverage, attempts, interpretation, and next step.
A summary is derived from evidence, never from lesson counts alone.

`courses/<id>/course.json` describes a course; `COURSE.md` can supply narrative
detail. Examples live under `examples/` and are explicitly fictional.
Outputs live under `output/`. Media sources remain editable.

## Media choices

PDF: structured lesson JSON to ReportLab, with embedded fonts, image captions,
equation images, page numbering, and source links. Inspect rendered pages.
Manim: storyboard to narration clips to scenes. Place each clip at the scene's
actual cue start; extra pauses then cannot shift later narration. Export
subtitles from the same cue timings. Keep silent rendering usable offline.

## Scope decisions

Initial subjects: mathematics, physics, history, biology, economics, computer
science. AI routes through computer science with mathematics support. The wider
subject list in the sketches is an expansion path, not a claim of supplied
specialists. Teachers are fictional; Ben Waston adapts the existing user-owned
persona. No real person's identity or affiliation is implied.

Skills stay in the existing `skills/` directory. Every skill has references only
where they change decisions, and scripts only where deterministic work helps.
No empty folders or placeholder curricula. No global skill installation is
needed to use the explicit loader.
