# Course plan

`course.json` is the map. It says where we go, in what order,
from which source, and where we are now.

Read it like this: past steps are the topics before `current`,
now is the one `current` topic, future steps are the topics after it.
Later work can stay marked `provisional`, which means it may change.

It does not hold lesson text or scores. Those live in chat and
in `learners/<id>/state.json`.

New plans use `schema_version: 2`. Do not write new version-1 plans.

## What to write

- `id`, `title`: short name and readable name.
- `goal`: what the learner will be able to do. Start with a verb:
  predict, derive, implement, explain.
- `depth`: `survey`, `working`, or `mastery` — how deep each topic
  goes, agreed with the learner before designing.
- `length`: the agreed duration in the learner's words, for example
  "one session", "six weeks", "a term". It sets the size of the
  route, the research, and the media budget.
- `vision` (optional, one line): what done looks like,
  for example "Fit a small model and explain each step."
- `assumptions`: what you did not check yet, in plain words.
- `starting_evidence`: what the learner already showed. Empty means
  unknown, not beginner.
- `chapters`: ordered list. Each chapter holds ordered `topics`.
  We keep chapters so old lessons and the portal table of contents
  still find their home.
- `current`: `{chapter_id, topic_id, next_step}`. Only one current
  topic at a time.
- `sources`: starts empty. Search fills it. Each entry has `title`,
  HTTPS `url` or safe local path, `type`, `checked_on`, `sections`,
  `verification_notes`. Any subject is allowed.

## Each topic

Each topic has `id`, `title`, `outcome`, `subject`, `teacher`,
`supporting_subjects`, `supporting_teachers`, `concepts`,
`prerequisites`, `minutes`, `resource_ids`, `exercise_ids`,
`lesson_ids`, `skill_routes`, `state`, and optional `feedback` and
`representations`.

- `outcome`: what the learner can do after it,
  for example "Predict the sign of a small change."
- `prerequisites`: earlier topic IDs only. Step 3 can use step 1,
  never the other way round.
- `resource_ids`: which sources this step uses. Every ID here must
  exist in top-level `sources`. When a source fails, add the new one
  to `sources`, point the topic at it, and remove the old ID when
  no topic uses it.
- `feedback` (optional, only on taught steps): how this step went.
  ```json
  "feedback": {
    "source_results": {"mit-1802-sec2": "too-hard"},
    "direction": "swap",
    "note": "asked twice, terms did not match",
    "repeats": 2
  }
  ```
  `source_results` is `worked`, `did-not-work`, `too-hard`, or
  `no-access`. `direction` is `keep`, `swap`, or `split`.
  `note` is one plain line. `repeats` counts asked-again on this step.
  Full tries stay in the learner record. This is only the short summary.
- `subject` is one main subject. `teacher` is the same name, or `null`
  when there is no persona. Do not invent a teacher.
- `state` tells where the step sits in the route:
  `current` is now, `planned` is next, `provisional` is later and may
  change, `retired` and `out-of-scope` stay as history and are not taught.

## Split each topic by representation

When you design a topic, decide which part of it needs which skill.
Write that into `representations` on the topic:

```json
"representations": [
  {"id": "secant-motion", "kind": "manim", "concept": "math.derivative",
   "purpose": "Animate secant lines converging to the tangent."},
  {"id": "slope-structure", "kind": "image",
   "purpose": "Label the rise-over-run structure of a slope."},
  {"id": "slope-lab", "kind": "simulation",
   "purpose": "Drag x and watch the predicted sign change."},
  {"id": "definition", "kind": "text",
   "purpose": "State the derivative as a local limit."}
]
```

Each representation is a different part of the topic. Do not show the
same idea twice in two tools; different parts of one concept may each
earn one representation.

- `kind` is one of `text`, `manim`, `image`, `simulation`, `diagram`,
  `pdf`, `exercise`.
- `id` is unique inside the topic. `purpose` is one line.
- `concept` is optional; when present it must be one of the topic's
  `concepts`.
- Decide which part needs motion, which needs a still image, and which
  stays text. Read
  [representation-choices.md](representation-choices.md) for the rules
  that stop Manim from being ordered for everything.
- Dispatch each part to its skill, then to its lesson block:

| kind | skill | lesson block type |
| --- | --- | --- |
| `manim` | manim-voice-animation | `voice-animation` or `animation` |
| `image` | image-gen | `diagram` or `artifact` |
| `diagram` | image-gen, or pinepaper / excalidraw per the subject skill | `diagram` or `artifact` |
| `simulation` | a small self-contained HTML file, registered with manage_artifact | `interactive-graph` or `simulation` |
| `pdf` | pdf | `artifact` |
| `text` | the subject teacher | `explanation`, `bullets`, `equation`, `code` |
| `exercise` | the subject teacher | `exercise` |

A `diagram` kind uses image-gen for a still picture, pinepaper for a
polished vector or interactive diagram, or excalidraw for a quick
inspectable sketch — use one tool per idea. An interactive or animated
pinepaper result registers like any other artifact so its chip flips.

- The viewer page shows one chip per representation. A chip flips from
  planned to ready when its artifact is registered. Every skill that
  produces a file must register it in the artifact manifest, or its
  chip never flips.

## Revision notes tell what changed and why

Keep `revision` and `revision_notes`. Each time the route changes,
keep the same IDs, add 1 to `revision`, and add one note with
the date, what changed, and what problem the learner had.

Good:
```json
{"revision": 3, "date": "2026-09-16",
 "reason": "Swapped openstax-3.5 for MIT 18.02 sec 2 on chain-rule after 2 repeats; terms did not match."}
```

Bad: "Updated plan." Say what moved and what was hard.

Writing `feedback` alone does not need a new revision. Changing
sources, order, or scope does. Then run `validate_course.py` again.

## Check

```bash
python3 skills/course-design/scripts/validate_course.py <course.json>
```

The script checks shape: names, links to sources and skill files,
order, HTTPS sources, one current step. It cannot tell if the plan
is well taught. You decide that from the research notes and
what the learner actually did.
