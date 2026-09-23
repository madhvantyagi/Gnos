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
| Subject | Subfields, prerequisites, evidence, and visual advice | General tutor rules |
| Course design | Goal, chapter and topic order, subtopics, prerequisites, teachers, and sources | Lesson content and media |
| Lesson design | One lesson's explanation, examples, practice, media, blocks, briefs, and files | Topic order and scope |
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
4. Build chapters, topics, and ordered subtopics. Enroll the plan under the
   learner's folder in the same turn. Then use lesson design to brief one
   subagent for each block, respect block dependencies, assemble and review
   their results, and publish the current lesson with at least two distinct
   teaching forms.
   The formal lesson file holds that teaching; chat carries the live exchange.
5. Once the current lesson is ready, ask whether the learner wants to see the
   course. On yes, render and link the viewer. Record observed evidence and a
   concrete next step, then revise provisional future topics only when that
   evidence changes the route. Persist under the learner's folder, defaulting
   to `learner` when no name was given.

`skills/learning-orchestrator/scripts/assemble_context.py` prints this selected context or its file manifest.
Its `course`, `lesson`, and `viewer` modes load instructions for the current
step. Viewer instructions enter only when the learner asks to see the course
or answers yes.
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
learner mutation. Chapters contain topics with ordered subtopics; topics gain detailed lesson files
gradually. Examples under `examples/` are explicitly fictional. Outputs live
under the learner course workspace or `output/`; media sources remain editable.

## Media choices

Course design records the topic's subtopics, concepts, prerequisites, teacher,
and sources. Lesson design chooses the forms that help explain and test those
concepts. A ready lesson has at least two distinct teaching forms, with no
maximum. Exercises and feedback do not count toward the two. The selected
subject guide says what must be shown or checked in that field;
`skills/lesson-design/references/representation-choices.md` helps the lesson
designer choose each form.

Subject files map the subfields; their deeper references develop difficult
examples, source comparisons, and domain checks. Tool operation belongs in
`skills/lesson-design/references/excalidraw.md` and
`skills/lesson-design/references/pinepaper.md`. These references cover tool
calls, inspection, and export across subjects. The context loader selects them
through `--media excalidraw` or `--media pinepaper`.

Older courses may still have topic `representations` and lesson blocks with
`representation_id`. Those bindings remain valid for existing lessons. New
courses leave both fields out. Lesson design declares any media skill routes
in `lesson.json` and gives every block a brief and a list of earlier blocks
it depends on. Each block has its own subagent, including text and exercise
blocks. Workers write separate outputs and return block fragments or artifact
records. The lesson coordinator checks their work and publishes the assembled
lesson. A change in
media or explanation stays in lesson design; a new topic concept or source
goes back to course design.

PDF: structured lesson JSON to ReportLab, with embedded fonts, image captions,
equation images, page numbering, and source links. Inspect rendered pages.
Manim: storyboard to narration clips to scenes. Place each clip at the scene's
actual cue start; extra pauses then cannot shift later narration. Export
subtitles from the same cue timings. Keep silent rendering usable offline.
The course viewer renders published lessons and registered artifacts on one
page. A normal render and the local server require a ready current lesson;
only an explicit
`--outline-only` preview can render earlier. The host loads lesson design and its teaching reference
before authoring. The renderer itself does not invoke skills or a model.

`skills/course-viewer/scripts/serve_course.py` serves that page on loopback and
connects exercise controls to the existing private submission store. Worked
answers remain outside the initial page and are returned only after a saved
attempt and explicit reveal. The original response and reveal time are stored
separately. A plain static server supports reading, but cannot persist answers.

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
