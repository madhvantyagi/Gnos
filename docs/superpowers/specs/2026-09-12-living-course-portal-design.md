# Living Course Design and Portal

Date: 2026-09-12  
Status: proposed for implementation planning

## Purpose

GNOS should design sustained courses only when the learner's goal needs one. A
course is a living table of contents that develops from real learner evidence,
not a complete content dump generated from the first request. Teaching remains
primarily conversational. A persistent local portal gives the learner an
organized visual interface for the current course, exercises, finished media,
references, earlier work, and course-scoped questions.

The system must preserve the existing separation of responsibilities:

- Learning routes each turn and conducts the teaching loop.
- Course design researches and revises the route.
- Subject guides select domain methods, resources, and useful representations.
- Teacher SOUL files govern voice and judgment.
- Learner state records observed attempts and derives progress.
- PDF, Manim, Excalidraw, and Pinepaper produce teaching artifacts.
- The portal displays and accepts course-scoped input; it does not infer mastery
  or run a hidden tutor.

## Course-or-lesson decision

Course design first classifies the requested scale.

Use a focused in-turn lesson plan when the request has one local target, only a
few directly dependent subtopics, and no clear need for multi-session state or a
long-lived collection of materials. The working sequence is target, missing
connection, explanation, example, and an optional revealing check. Do not create
a course directory merely because a topic can be divided into headings.

Use a persistent course when the learner explicitly requests sustained study or
when the destination requires several competency branches, prerequisite chains,
subjects, artifacts, assessments, or sessions. A single named topic can still
justify a course when learning it well requires this breadth.

When the boundary is uncertain, ask only for information that changes the route:
the capability the learner wants, relevant work they can already do, and the
available depth or time. Existing learner evidence replaces repeated intake
questions. Never infer a learner biography, ability level, or preferred learning
style.

## Adaptive design lifecycle

At enrollment, GNOS researches the domain and creates a useful chapter-level
table of contents. It records the destination, initial evidence, unresolved
assumptions, prerequisite dependencies, sources, and a provisional later route.
Only the current topic and its next lesson require detailed material.

Before each subsequent lesson, GNOS reads the selected course, relevant learner
evidence, the last next step, and pending portal questions. It then keeps,
repairs, reorders, expands, or retires future topics. Stable chapter, topic, and
concept identifiers preserve history across revisions.

After a meaningful learner attempt or topic transition, GNOS records evidence,
derives the new progress view, writes a precise next step, and republishes the
portal data. A revision records what changed and why. It never changes earlier
evidence to make the route appear linear.

Later chapters may be marked provisional. The portal must distinguish current
commitments from provisional direction without suggesting that provisional
topics have been taught.

## Content hierarchy

The persistent hierarchy is:

```text
course
  chapter
    topic
      lesson
        ordered blocks
        exercises
        artifacts
```

A course contains many chapters. A chapter contains related topics. A topic may
require multiple lessons as the learner practices or repairs a misconception.
A lesson is one authored teaching encounter or coherent unit; its identifier
does not stand for the whole topic.

Each layer has a stable lowercase slug. Human-readable titles may change without
breaking evidence or artifact links.

## Data ownership and contracts

### Course plan

`learners/<learner-id>/courses/<course-id>/course.json` is the canonical current
curriculum plan for a persistent learner course. A new schema version should
support:

- course identity, title, destination, scope, revision, and revision notes;
- learner starting evidence and explicitly unresolved assumptions;
- ordered chapters and topics with stable identifiers;
- observable outcomes, concept IDs, dependencies, and time estimates;
- `current`, `provisional`, `retired`, and other planning states that do not
  masquerade as learning evidence;
- per-topic lead subject and teacher, optional supporting subjects and teachers,
  and the skill entry points required to teach or create planned media;
- a top-level source registry containing inspected title, URL or local path,
  source type, access/check date, relevant sections, and verification limits;
- assessment intentions and exercise references;
- lesson references as lessons are created;
- the current teaching frontier and the agreed next step.

The course plan does not store editable mastery percentages or raw learner
responses.

### Lesson composition

Detailed lesson content lives outside `course.json` so the table of contents
does not become a monolithic content object. Each lesson has a `lesson.json`
with:

- course, chapter, topic, lesson, and concept identifiers;
- assigned teacher and the relevant skill routes;
- an observable purpose;
- assumptions supported by learner evidence or explicitly marked unknown;
- an ordered list of content blocks;
- exercise and artifact references;
- a publication state and timestamps.

Supported content blocks include prose, bullets, equations, code, voice video,
animation, diagram, interactive graph or simulation, source excerpt or link,
exercise, feedback, and a generic registered artifact. A block includes a stable
ID, concept IDs, teaching purpose, and only the type-specific fields it needs.

Exercises reference the explanation and artifacts they depend on. Feedback can
point to a specific block, diagram element, or media timestamp. This makes a
voice animation, short explanation, interactive graph, bullet summary, and
exercise one teaching sequence instead of unrelated files.

### Learner evidence

`learners/<learner-id>/state.json` remains the source of truth for learner
profiles, enrollment status, observed attempts, interpretation, and the next
step. Enrollment records the selected course ID, current plan revision and
fingerprint, plus immutable completion or migration history; it does not become
a second editable copy of the current curriculum.
Progress is derived from evidence rather than edited from the portal.

Concept-level evidence keeps the conservative distinctions already used by
GNOS: exposed, practicing, demonstrated, and retained. The design may add a
derived `needs-repair` display state when later evidence exposes a gap, but the
underlying attempts remain intact. `not-started`, `provisional`, `retired`, and
`out-of-scope` describe curriculum state rather than understanding.

The portal may report concrete coverage such as topics introduced, exercises
attempted, and independently completed tasks. It must not convert scheduled
minutes, opened files, watched videos, or lesson counts into mastery.

## Learner course workspace

For a known learner and persistent course, create:

```text
learners/<learner-id>/courses/<course-id>/
  course.json
  manifest.json
  lessons/
    <lesson-id>/lesson.json
  exercises/
  submissions/
  questions/
  artifacts/
    videos/
    animations/
    diagrams/
    simulations/
    documents/
    generated/
  archive/
  site/
```

The slugged course ID provides a safe directory name based on what the learner
is studying; the human title remains in course data. The workspace must reject
path traversal and symbolic-link escapes. Learner records and course workspaces
remain private, local, and ignored by Git.

`state.json` remains authoritative for evidence and enrolled course status. The
workspace `course.json` is authoritative for the current plan. A compatibility
migration may read an existing plan embedded in learner state once, validate it,
write it into the course workspace, and replace the editable duplicate with its
course ID, revision, and fingerprint. Updates must be written atomically so stale
references are detectable rather than silently diverging.

## Artifact manifest

`manifest.json` is the only publication registry. Artifact-generation folders
are never exposed by directory scanning.

Each registered artifact records:

- stable ID, type, title, short purpose, and related concepts;
- chapter, topic, lesson, and optional exercise placement;
- local path or external URL;
- MIME type and useful metadata such as duration, pages, dimensions, captions,
  transcript availability, or thumbnail;
- creation and update times;
- publication status: draft, ready, archived, or failed;
- renderer hints that cannot override portal safety rules.

Only `ready` artifacts appear in ordinary course views. Temporary render frames,
logs, tool traces, partial transcripts, MCP calls, and creation progress remain
hidden. A transcript appears only when intentionally registered as a finished
companion artifact.

Known browser-safe media receives a specialized viewer. Unknown types inherit a
generic file presentation with truthful open or download actions. A missing
preview never hides the artifact. PDFs receive a useful preview when available
and an explicit full-document link rather than a cramped forced embed.

Excalidraw is appropriate for quick spatial relationships. Pinepaper is
appropriate for polished vector graphics, interactive graphs, or simulations.
Manim owns voice-synchronized teaching animations where motion reveals change.
The portal does not claim an MCP result was saved or interactive until a usable
output or URL has been registered and verified.

Interactive HTML or JavaScript artifacts run in a sandboxed frame with a
restrictive content-security policy. They cannot read arbitrary learner files or
call portal mutation endpoints without the portal's explicit interface.

## Exercise lifecycle

An exercise has a stable ID, placement, concepts, prompt, response type, optional
input constraints, evaluation mode, and private success criteria. Initial
response types include multiple choice, short text, long text, numeric input,
and code text. Executing arbitrary submitted code is outside the first version.

The public portal payload excludes private success criteria, solutions, and
server-side deterministic answer data until disclosure is permitted.

The learner can save a draft, submit an attempt, request a hint, retry, or ask
Codex about the exercise. The system preserves attempts instead of overwriting
them. Deterministic multiple-choice or numeric exercises may be checked locally
by the server. Open-ended explanations and code remain `awaiting-review` until
an active GNOS interaction evaluates the actual response. The interface must not
pretend such work has been graded.

Review creates or links a learner evidence event through the learner-state
contract. Revealing a solution is recorded separately and cannot establish
independent success.

## Ask Codex boundary

The portal includes an Ask Codex view, but the webpage does not silently invoke
the Codex model or installed plugin. It writes a course-scoped question containing
the selected chapter, topic, lesson block, artifact, exercise attempt, and the
learner's text. GNOS reads pending questions during an active Codex task and can
write a response that the portal then displays.

The interface clearly labels questions as pending until an answer exists. There
is no fake typing state, background tutor, hidden API key, or claim of immediate
model availability.

## Local portal

The recommended implementation is a dependency-light local Python server with a
static HTML, CSS, and JavaScript frontend. It binds to loopback only and serves
one validated learner/course workspace. Its endpoints expose sanitized public
course data, registered ready artifacts, exercise drafts and submissions,
course-scoped questions, safe presentation preferences, and allowed curriculum
edits.

The portal files persist when the server stops. GNOS can start or reopen the
portal when the course is created, resumed after a gap, or receives a useful new
artifact. The learning skill should mention the portal at those moments without
advertising it after every teaching turn.

The page refreshes changed plan, evidence, lesson, and manifest data through a
small polling or event mechanism. It displays only committed atomic snapshots;
an in-progress write must never produce a half-rendered course.

## Navigation and aging

Primary views are:

- Home: current topic, next action, latest lesson, and recent finished artifacts.
- Contents: chapters, topics, dependencies, curriculum state, and evidence-based
  progress.
- Lessons: composed lesson sequences.
- Exercises: current work, feedback, and earlier attempts.
- Watch: voice videos and animations.
- Generated: diagrams, simulations, code, and other registered outputs.
- Resources: inspected sources, PDFs, and external materials.
- Ask Codex: course-scoped questions and saved responses.
- Archive: older, retired, or hidden material.

Home emphasizes the current learning frontier. Older lessons, attempts,
questions, and artifacts remain available through chapter/topic filters,
`Earlier work` disclosures, or Archive. Age never deletes learner evidence.

## Visual language

The portal should feel like a calm editorial study workspace, not an analytics
dashboard. Use a restrained responsive shell: module or chapter navigation,
a readable central column, and optional contextual metadata. On mobile, replace
side rails with a compact tab bar or module sheet and keep a single reading
column.

Recommended typography is Newsreader for major headings, Inter for reading and
controls, and IBM Plex Mono sparingly for code and metadata. Fonts must have
local or system fallbacks so offline use remains readable.

Recommended tokens:

- canvas `#F7F5F0`, surface `#FFFEFA`, muted surface `#EFEEE8`;
- ink `#202426`, muted ink `#697174`, line `#D9D8D0`;
- primary accent `#176B68`, soft accent `#DCEDEA`;
- restrained success `#2D765B`, warning `#946B22`, danger `#A4473D`.

Use whitespace and subtle surface changes before borders. Keep body text at
16–18px with generous line height. Controls have visible focus states and at
least 44px touch targets. Status never depends on color alone. Motion is brief,
purposeful, and disabled under `prefers-reduced-motion`.

Lessons render as a continuous sequence. Do not put every paragraph in a card.
Artifact frames contain a type label, title, teaching purpose, relevant metadata,
and an accurate action such as Read, Play, View, Open, or Download.

## Personalized language

Personalization must be evidence-based and maintain continuity across media.
The teacher may say, “You identified the gradient last time; the unresolved part
was why its negative direction reduces the local approximation,” only when the
saved attempt supports that statement. Unknown history receives neutral wording.

Within a lesson, prose, bullets, narration, diagram labels, simulations, and
exercises use consistent symbols, terms, examples, and color meanings. Short
transitions explain why the next representation is appearing and what the
learner should notice. Avoid generic encouragement, fake familiarity, repeated
AI phrasing, and labels that foreground how content was generated.

## Portal mutations and deletion

The portal may save exercise drafts, submit attempts, create questions, archive
finished artifacts, change display preferences, and propose edits to future
curriculum. It may not directly mark concepts understood or rewrite evidence.

Renaming, reordering, adding, or retiring future topics creates a validated
course revision with a reason. Changing a topic with historical evidence keeps
its stable identifier or explicitly migrates it without deleting events.

Delete is recoverable by default: material moves to the course archive and the
manifest records the change. Permanent artifact removal requires an explicit
confirmed action. Learner-evidence removal uses the existing retraction or
learner-deletion flow and is never bundled into an ordinary portal cleanup.

## Failure behavior

- If a media preview fails, retain its title and metadata and offer a truthful
  retry, open, or download fallback.
- If a write conflicts with a newer plan or state fingerprint, reject it and
  refresh instead of overwriting the newer work.
- If an artifact is missing, show that it is unavailable and preserve the
  manifest error; do not expose neighboring files.
- If the portal server is stopped, course files and evidence remain intact and
  teaching can continue in chat.
- If an MCP or media tool is unavailable, teach with the best available
  representation and record only artifacts that were actually produced.
- If learner identity is not established or local tracking is declined, do not
  create a personal course workspace or inferred record.

## Implementation boundaries

The first implementation should support the living table of contents, gradual
lesson publication, manifest-driven artifacts, direct non-code exercise
submissions, pending Ask Codex questions, evidence-derived progress, recoverable
archive actions, and the local responsive portal.

It should not include public internet deployment, accounts, cloud sync,
background model calls, arbitrary code execution, collaborative editing,
notifications, or a general-purpose content-management system.

## Verification

Implementation verification must include:

- course classification examples for a local doubt, a focused topic, and a
  broad or prerequisite-rich sustained goal;
- course schema validation, stable IDs, ordered dependencies, skill/teacher
  routes, source records, and revision checks;
- atomic workspace writes, stale-fingerprint rejection, traversal and symlink
  rejection, and learner isolation;
- lesson block, artifact manifest, public-data redaction, submission, question,
  archive, and recovery tests;
- confirmation that portal submissions become learner evidence only through an
  explicit valid review path;
- desktop and mobile rendering, keyboard navigation, focus visibility, reduced
  motion, contrast, long titles, empty states, and media failures;
- inline playback for supported finished artifacts and honest link fallbacks for
  unsupported or PDF content;
- existing harness validation and the full unit-test suite.

The implementation must finish by running:

```bash
python3 skills/learning/scripts/validate_harness.py
python3 -m unittest discover -s tests -v
```

Media behavior must also be rendered and visually inspected with available
dependencies. Unavailable external MCP, voice, browser, or media dependencies
must be reported separately from locally verified behavior.
