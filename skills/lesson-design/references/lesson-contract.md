# Composed lesson contract — the taught topic's default record

Author one formal lesson per taught topic. The course sets its scope and
sequence; the lesson develops the examples, reasoning, practice, and media.
Validate it, then publish it into the enrolled workspace:

```bash
python3 skills/course-design/scripts/validate_lesson.py lesson.json \
  --course learners/<learner>/courses/<course-id>/course.json
python3 skills/course-design/scripts/course_workspace.py publish \
  learners/<learner>/courses/<course-id> --lesson lesson.json
```

Answer questions and clarify misunderstandings during live teaching. Keep the
lesson file current for the portal and the next turn. Publish `draft` while
developing and `ready` after reviewing the assembled lesson and its artifacts.

## Lesson fields

New lessons use `schema_version: 2`; existing version 1 records remain readable.
A lesson contains:

- `id`, `course_id`, `chapter_id`, and `topic_id`,
- a readable `title` and observable `purpose`,
- `concepts` drawn from that topic,
- the assigned `teacher` or `null`, and repository-relative `skill_routes`,
- `assumptions`, each supported by learner evidence or marked unverified,
- ordered `blocks` using the supported types below, with a representation binding
  when the topic has a plan,
- `exercises` with prompts, response types, and private evaluation criteria,
- `publication`: `draft`, `ready`, or `archived`,
- `created_at` and `updated_at` timestamps,
- `design_receipt` after review, required before publication as `ready`.

Timestamps are real ISO-8601 UTC instants ending in `Z`; `updated_at` cannot
precede `created_at`. Lesson skill routes must be unique and resolve to existing skill or subject
guidance files. Include the topic guidance and any media producers selected
during lesson design. A binding representation still fixes its producer route.

Stable identifiers preserve links from attempts, artifacts, and questions.
Changing the title or explanation does not justify changing the lesson ID.
The lesson inherits the topic's teacher value. A teacher-neutral topic remains
teacher-neutral, authoring a lesson is not permission to invent a persona.

Only `ready` lessons belong in the ordinary portal sequence. A draft can be
saved while teaching develops; it must not appear as finished learner material.

A new ready publication records `design_receipt` with `schema_version: 2`,
`designed_at` (between creation and update timestamps), `course_fingerprint`
(the current course content SHA-256), `lesson_content_fingerprint`,
`skill_route: "skills/lesson-design/SKILL.md"`, and `review: "pass"`.
Compute the course hash with `course_contract.course_content_fingerprint`.
After reviewing and repairing the lesson, remove its old receipt, leave it as
`draft`, and calculate the content hash:

```bash
python3 skills/course-design/scripts/validate_lesson.py lesson.json \
  --course learners/<learner>/courses/<course-id>/course.json --design-fingerprint
```

This prints `lesson_contract.lesson_design_fingerprint(lesson)`: a versioned
hash of authored content, including private briefs, exercises, criteria, and
solutions. It excludes the receipt, publication state, and top-level creation
and update timestamps. The existing `lesson_fingerprint` remains the whole-file
snapshot used by saved attempts; do not substitute it for the content hash.
Changing teaching content requires a fresh review and hash. Remove the receipt
when returning an edited lesson to draft.

Legacy unbound receipts remain readable. New ready publication requires a
bound receipt; no script invents a review or upgrades legacy records on read.
The public projection includes only declared receipt fields, never arbitrary
private reviewer notes. The hash identifies reviewed content; it cannot prove
teaching quality or bind mutable external artifact bytes.

## Blocks

Every block has a stable `id`, `type`, relevant `concepts`, and a short
`purpose` stating what the representation should reveal. For a topic with a
representation plan, every block also has `representation_id`. It must name one
of that topic's entries in `course.json`. Type-specific fields contain the text
or reference the block needs.

Supported types are:

- `explanation`, `bullets`, `equation`, and `code`;
- `voice-animation`, `animation`, `diagram`, `interactive-graph`, and
  `simulation`;
- `source`, `khan-video`, `exercise`, `feedback`, and generic `artifact`.

For a topic with a representation plan, each block uses its planned kind:

| representation kind | block type |
| --- | --- |
| `manim` | `voice-animation` or `animation` |
| `image` | `diagram` or `artifact` |
| `diagram` | `diagram` or `artifact` |
| `simulation` | `interactive-graph` or `simulation` |
| `pdf` | `artifact` |
| `text` | `explanation`, `bullets`, `equation`, `code`, `source` |
| `exercise` | `exercise` |
| `khan` | `khan-video` |

For a topic with a representation plan, the validator checks the representation
ID, concept, purpose, and kind-to-block mapping. Revise and validate a binding plan
if its medium or purpose changes. A topic without a representation plan lets
lesson design choose the medium; its blocks still use the topic's concepts.

Media blocks refer to artifact IDs declared by the lesson. After a worker
produces and checks the file, the coordinator registers that ID in the artifact
manifest. Exercise blocks refer to an exercise defined by the same lesson.
References must resolve; a plausible filename is not an artifact.

For a verified Khan Academy video, use a `khan-video` block referencing a course
source with `type: "khan-video"`, the exact Khan Academy video URL, and the
verified 11-character `youtube_id`. Its `source_id` must be in the current
topic's `resource_ids`. Give the block a concrete `text` viewing prompt and
use `skills/khan-academy/SKILL.md` as its production route. If only part of the video is relevant,
set integer `clip_start_seconds` and `clip_end_seconds` on the block. These
are absolute seconds from the beginning of the video, with end greater than
start. The portal embeds that interval in a responsive 16:9 player and links the original Khan page.
Khan articles and exercises use ordinary source links. See
[Khan Academy](../../khan-academy/SKILL.md) for selection and placement.

## Math notation

The course page renders mathematics with KaTeX. Write every formula as
LaTeX, never as bare ASCII:

- inline math in `text`, `items`, and exercise `prompt` fields goes in
  `$...$` (or `\(...\)`): `For $A \in \mathbb{R}^{m \times n}$,
  $T(x) = Ax$ is a linear map from $\mathbb{R}^n$ to $\mathbb{R}^m$`.
- display math goes in `$$...$$` (or `\[...\]`), and `equation` blocks
  hold one LaTeX expression, e.g. `[v]_{new} = P^{-1}[v]_{old}`.
- never write `R^(m x n)`, `[v]_B`, `P^(-1)`, `xW_Q`, or `1/2` as plain
  text and expect them to look right. The viewer translates common ASCII
  idioms as a safety net, but the safety net is lossy: delimit your math.

Order blocks by reasoning, not by file type. A useful sequence may introduce a
claim, let the learner inspect its changing parts, and then ask for a prediction.
Do not require every lesson to contain every block type.

## Production briefs

Version 2 requires `production` on every block, including those written by the
coordinator. It records the teaching job and is removed from the public
projection. Version 1 permits blocks without it.

```json
"production": {
  "skill_route": "skills/manim-voice-animation/SKILL.md",
  "brief": "Keep the gradient fixed while two step directions move from the same point.",
  "must_include": [
    "The gradient vector",
    "One positive and one negative dot product",
    "The local-prediction warning"
  ],
  "continuity": [
    "Use the lesson's gradient symbol and direction colors.",
    "Keep the graph axes fixed across both comparisons."
  ],
  "acceptance_checks": [
    "Each moving step matches the displayed dot-product sign.",
    "The final frame remains readable without narration."
  ],
  "depends_on_block_ids": ["local-prediction"]
}
```

`skill_route` must be declared by the lesson; a binding course representation
also fixes its route. `brief`
states one bounded job. `must_include`, `continuity`, and `acceptance_checks`
are nonempty. Version 2 requires `depends_on_block_ids`; use `[]` when
there are no dependencies. It may name only earlier blocks. Do not write “make it clear,” “make it engaging,” or “add context.” Name
the object, relation, label, control, or check the worker must produce.

## Lesson production

The coordinator owns `course.json`, `lesson.json`, and `manifest.json`. Workers
write only their assigned outputs. Follow [lesson design](../SKILL.md) and
[worker briefs](worker-brief.md) for dispatch and review:

1. Draft blocks in reasoning order, with a shared case, notation, and sources.
   Honor any binding course representation plan.
2. Add production briefs, validate, and publish as `draft` before registering
   artifacts against the lesson ID.
3. Give each worker its block and required earlier context. Supply inspected
   exports for media dependencies; start dependent work after that review.
4. Review returned files and fragments against the brief. Check the complete
   explanation, transitions, and learner interaction after assembly.
5. Register checked artifacts one at a time, validate the assembled lesson,
   publish it as `ready`, and render the course page.

Revise a medium or block purpose in lesson design. Return to course design
for a new concept, source, topic boundary, or changed binding representation.
Workers propose these changes; they do not silently substitute an artifact.

## One sequence across representations

This legacy version 1 example shows prose, media, interaction, and practice
for one concept. New version 2 lessons also brief every block:

```json
{
  "schema_version": 1,
  "id": "gradient-direction-1",
  "course_id": "gradient-descent",
  "chapter_id": "local-change",
  "topic_id": "gradient-direction",
  "title": "What the gradient predicts",
  "purpose": "Predict which small step decreases a local linear approximation.",
  "concepts": ["math.gradient", "math.directional-derivative"],
  "teacher": "math",
  "skill_routes": [
    "skills/subject/SKILL.md",
    "skills/subject/subjects/math.md",
    "skills/manim-voice-animation/SKILL.md"
  ],
  "assumptions": [
    "The learner has computed a two-variable gradient; direction choice remains unverified."
  ],
  "blocks": [
    {
      "id": "local-prediction",
      "representation_id": "local-prediction-text",
      "type": "explanation",
      "concepts": ["math.directional-derivative"],
      "purpose": "Name the prediction the animation will make visible.",
      "text": "For a small step d, the dot product between the gradient and d predicts the first-order change."
    },
    {
      "id": "direction-video",
      "representation_id": "direction-motion",
      "type": "voice-animation",
      "concepts": ["math.gradient", "math.directional-derivative"],
      "purpose": "Keep the gradient fixed while comparing two step directions.",
      "artifact_id": "gradient-direction-video",
      "production": {
        "skill_route": "skills/manim-voice-animation/SKILL.md",
        "brief": "Animate two step directions from one point while the gradient stays fixed.",
        "must_include": ["The gradient", "Two step vectors", "Both dot-product signs"],
        "continuity": ["Reuse the notation and colors from local-prediction."],
        "acceptance_checks": ["Each direction matches its displayed sign."],
        "depends_on_block_ids": ["local-prediction"]
      }
    },
    {
      "id": "connect-sign",
      "representation_id": "connect-sign-text",
      "type": "bullets",
      "concepts": ["math.directional-derivative"],
      "purpose": "Connect the moving arrow to the sign of the dot product.",
      "items": [
        "A positive dot product predicts an increase.",
        "A negative dot product predicts a decrease.",
        "The prediction is local; a large step can leave the region where it is accurate."
      ]
    },
    {
      "id": "direction-lab",
      "representation_id": "direction-control",
      "type": "interactive-graph",
      "concepts": ["math.gradient", "math.directional-derivative"],
      "purpose": "Let the learner rotate the step and inspect the predicted sign.",
      "artifact_id": "direction-simulator"
    },
    {
      "id": "predict-new-direction",
      "representation_id": "direction-check",
      "type": "exercise",
      "concepts": ["math.directional-derivative"],
      "purpose": "Test whether the learner can predict before moving the simulator.",
      "exercise_id": "predict-direction-sign"
    }
  ],
  "artifacts": [{"id": "gradient-direction-video"}, {"id": "direction-simulator"}],
  "exercises": [
    {
      "id": "predict-direction-sign",
      "concepts": ["math.directional-derivative"],
      "prompt": "The gradient is (2, 4) and the step is (1, -1). Predict the sign of the local change and justify it.",
      "response_type": "long-text",
      "reference_block_ids": ["direction-video", "connect-sign", "direction-lab"],
      "evaluation": {"mode": "manual"},
      "success_criteria": [
        "Computes or reasons from a negative dot product.",
        "Describes a local prediction rather than a guaranteed global change."
      ]
    }
  ],
  "publication": "draft",
  "created_at": "2026-09-12T16:00:00Z",
  "updated_at": "2026-09-12T16:00:00Z"
}
```

The example assumes the selected course topic declares the five named
representations and all listed skill routes. The same term, symbol, direction,
and color meaning must survive across the explanation, narration, graph, and
exercise. Add a short transition when the reason for changing representation
would otherwise be unclear. Do not use generic connective language to disguise
unrelated artifacts.

## Exercises and evaluation

An exercise contains `id`, `concepts`, `prompt`, `response_type`, `evaluation`,
private `success_criteria`, and optional `reference_block_ids`. Every lesson
exercise id must be listed in its topic's `exercise_ids`; the portal resolves
saves through that list and validation rejects an unlisted exercise.

Supported response types are `multiple-choice`, `short-text`, `long-text`,
`numeric`, and `code-text`. Supported evaluation modes are:

- `manual` for explanations, proofs, arguments, and code review;
- `choice` for a nonempty unique `options` list and a private `answer` equal to
  one of those options;
- `numeric` for a numeric private `answer` and nonnegative numeric `tolerance`.

The first portal version stores code as text, it never executes submitted code.
An `execute` field is invalid in every evaluation mode. Manual evaluation does
not contain an answer, accepted values, tolerance, or solution.
Manual responses remain awaiting review until an active teacher evaluates the
actual attempt. Revealing a solution is not independent success.

Success criteria belong in the private lesson file so the teacher can review
consistently. A public lesson projection is an explicit allowlist. It includes
the identity, placement, purpose, visible blocks, prompt, response shape, and
publication metadata, but never success criteria, accepted answers, tolerances,
solutions, or other private evaluation fields. Choice options remain public
because the learner needs them to answer; the accepted choice does not.

## Validation

Run:

```bash
python3 skills/course-design/scripts/validate_lesson.py \
  <lesson.json> --course <course.json>
```

Validation checks course placement, teacher and skill routes, concept ownership,
representation bindings, production briefs and dependencies, unique IDs, block
types, exercise references, response and evaluation modes, timestamps, and
publication state. It cannot establish that the chosen sequence helps this
learner; revise from their response rather than treating valid JSON as evidence
of learning.
