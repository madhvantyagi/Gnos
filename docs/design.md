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
| Course design | Outcomes, sequence, teacher assignments, assessments | Lesson blocks and files |
| Lesson design | One lesson's blocks, briefs, workers, and finished files | Route order and sources |
| Learner model | Dated observations, attempts, preferences, next step | Fixed labels of ability |
| PDF / Manim / Image | Artifact construction and verification | Whether the learner understood |

One teacher leads a turn. A supporting subject contributes only the needed
idea; it does not trigger an invented panel discussion. Mathematics is shared
across subjects by concept ID, so vectors are not re-taught under every label.

## Turn flow

1. Read learning. Classify a direct doubt, lesson, course request, or resumption.
2. Load the relevant learner snapshot if a record exists. When no identity is
   established, proceed automatically under the default `learner` folder and say
   one plain line; an ID is never required to start. Read only the active course
   and recent evidence for the concept at hand.
3. Select subject and teacher. Use course design only when a persistent route is
   justified; a local doubt keeps its small plan in the turn. Before designing a
   course, ask how deep and how long the learner wants to go, and record both in
   the plan.
4. For a course, resolve the current chapter/topic and author only the next useful
   lesson. The taught topic's default record is its formal lesson file; chat
   carries the live exchange. Teach the missing connection. Choose text, a
   diagram, an exercise, or motion for what it reveals; a media deliverable is
   not a prerequisite to answering.
5. Enroll the plan under the learner's folder the same turn it is written, then
   offer the portal page. Record observed evidence and a concrete next step,
   then revise provisional future topics only when that evidence changes the
   route. Persist under the learner's folder, defaulting to `learner` when no
   name was given.

`skills/learning-orchestrator/scripts/assemble_context.py` prints this selected context or its file manifest.
It is an explicit loader for hosts without native skill discovery. It does not
classify arbitrary prose or call a model. `AGENTS.md` is the in-repository entry.

## Records and artifacts

`learners/<id>/state.json` contains the profile, enrollment references, and
ordered session events. It is private local data, ignored by Git. Updates take a
lock and atomically replace the file. An event ID makes retries idempotent;
conflicting reuse is an error. Each event separates coverage, attempts,
interpretation, and next step. A summary is derived from evidence, never from
lesson counts alone.

The canonical living plan is
`learners/<id>/courses/<course-id>/course.json`. State records its relative
reference, revision, and fingerprint so a stale or missing plan fails before a
learner mutation. Chapters contain topics; topics gain detailed lesson files
gradually. Examples under `examples/` are explicitly fictional. Outputs live
under the learner course workspace or `output/`; media sources remain editable.

## Media choices

A topic declares its representations in `course.json` so each part is
dispatched to the right skill: manim for motion, the host's image generation for still
images, pdf for handouts, simulation for interactive parts, text for the
rest. The plan's agreed `depth` and `length` set the media budget;
`representation-choices.md` holds the rules that stop Manim from
being ordered for everything.

The selected subject guide supplies the domain-specific representation
profile. Each lesson block names one approved course representation through
`representation_id`; the lesson cannot silently introduce a new concept,
medium, or skill route. A delegated block carries a private production brief.
Block workers write separate outputs and return block fragments or artifact
records. The lesson coordinator alone registers checked artifacts one by one,
and publishes the assembled lesson. It never edits the route to fix a bad
block; it sends the fix back to course design.

PDF: structured lesson JSON to ReportLab, with embedded fonts, image captions,
equation images, page numbering, and source links. Inspect rendered pages.
Manim: storyboard to narration clips to scenes. Place each clip at the scene's
actual cue start; extra pauses then cannot shift later narration. Export
subtitles from the same cue timings. Keep silent rendering usable offline.
The course viewer renders registered artifacts on one static page.

## Scope decisions

Supplied subjects: mathematics, physics, history, biology, economics, computer
science, accounting, artificial intelligence, business, psychology, chemical
engineering, and political science. AI has its own subject route with computer
science and mathematics support. Subject guides define scope; curated resources
may require expansion and verification before sustained courses.
Teachers are fictional; Ben Waston adapts the existing user-owned
persona. No real person's identity or affiliation is implied.

Skills stay in the existing `skills/` directory. Every skill has references only
where they change decisions, and scripts only where deterministic work helps.
No empty folders or placeholder curricula. No global skill installation is
needed to use the explicit loader.
