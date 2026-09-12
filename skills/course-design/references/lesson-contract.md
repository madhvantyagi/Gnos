# Composed lesson contract

A lesson is one coherent teaching encounter inside a course topic. It is not the
topic itself, and it is not a folder of loosely related files. A topic can gain
several lessons as the learner practices, asks a new question, or repairs a gap.

Read this reference when authoring, revising, validating, or publishing a lesson.
Use the course contract first to resolve the chapter, topic, concepts, teacher,
and current frontier.

## Lesson fields

A lesson file uses `schema_version: 1` and contains:

- `id`, `course_id`, `chapter_id`, and `topic_id`;
- a readable `title` and observable `purpose`;
- `concepts` drawn from that topic;
- the assigned `teacher` or `null`, and repository-relative `skill_routes`;
- `assumptions`, each supported by learner evidence or marked unverified;
- ordered `blocks`;
- detailed `exercises`;
- `publication`: `draft`, `ready`, or `archived`;
- `created_at` and `updated_at` timestamps.

Timestamps are real ISO-8601 UTC instants ending in `Z`; `updated_at` cannot
precede `created_at`. Lesson skill routes must be unique and selected from the
owning topic's declared routes. A lesson can use fewer routes than its topic,
but it cannot silently introduce an unrelated skill.

Stable identifiers preserve links from attempts, artifacts, and questions.
Changing the title or explanation does not justify changing the lesson ID.
The lesson inherits the topic's teacher value. A teacher-neutral topic remains
teacher-neutral; authoring a lesson is not permission to invent a persona.

Only `ready` lessons belong in the ordinary portal sequence. A draft can be
saved while teaching develops; it must not appear as finished learner material.

## Blocks

Every block has a stable `id`, `type`, relevant `concepts`, and a short
`purpose` stating what the representation should reveal. Type-specific fields
contain the text or reference it needs.

Supported types are:

- `explanation`, `bullets`, `equation`, and `code`;
- `voice-animation`, `animation`, `diagram`, `interactive-graph`, and
  `simulation`;
- `source`, `exercise`, `feedback`, and generic `artifact`.

Media blocks refer to registered artifact IDs. Exercise blocks refer to an
exercise defined by the same lesson. References must resolve; a plausible
filename is not an artifact.

Order blocks by reasoning, not by file type. A useful sequence may introduce a
claim, let the learner inspect its changing parts, and then ask for a prediction.
Do not require every lesson to contain every block type.

## One sequence across representations

This example uses prose, media, interaction, and an exercise for one concept:

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
    "skills/manim-voice-animation-skill/SKILL.md"
  ],
  "assumptions": [
    "The learner has computed a two-variable gradient; direction choice remains unverified."
  ],
  "blocks": [
    {
      "id": "local-prediction",
      "type": "explanation",
      "concepts": ["math.directional-derivative"],
      "purpose": "Name the prediction the animation will make visible.",
      "text": "For a small step d, the dot product between the gradient and d predicts the first-order change."
    },
    {
      "id": "direction-video",
      "type": "voice-animation",
      "concepts": ["math.gradient", "math.directional-derivative"],
      "purpose": "Keep the gradient fixed while comparing two step directions.",
      "artifact_id": "gradient-direction-video"
    },
    {
      "id": "connect-sign",
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
      "type": "interactive-graph",
      "concepts": ["math.gradient", "math.directional-derivative"],
      "purpose": "Let the learner rotate the step and inspect the predicted sign.",
      "artifact_id": "direction-simulator"
    },
    {
      "id": "predict-new-direction",
      "type": "exercise",
      "concepts": ["math.directional-derivative"],
      "purpose": "Test whether the learner can predict before moving the simulator.",
      "exercise_id": "predict-direction-sign"
    }
  ],
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
  "publication": "ready",
  "created_at": "2026-09-12T16:00:00Z",
  "updated_at": "2026-09-12T16:00:00Z"
}
```

The same term, symbol, direction, and color meaning should survive across the
explanation, narration, graph, and exercise. Add a short transition when the
reason for changing representation would otherwise be unclear. Do not use
generic connective language to disguise unrelated artifacts.

## Exercises and evaluation

An exercise contains `id`, `concepts`, `prompt`, `response_type`, `evaluation`,
private `success_criteria`, and optional `reference_block_ids`.

Supported response types are `multiple-choice`, `short-text`, `long-text`,
`numeric`, and `code-text`. Supported evaluation modes are:

- `manual` for explanations, proofs, arguments, and code review;
- `choice` for a nonempty unique `options` list and a private `answer` equal to
  one of those options;
- `numeric` for a numeric private `answer` and nonnegative numeric `tolerance`.

The first portal version stores code as text; it never executes submitted code.
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
unique IDs, block types, exercise references, response and evaluation modes,
timestamps, and publication state. It cannot establish that the chosen sequence
actually helps this learner; revise from their response rather than treating a
valid JSON file as evidence of teaching quality.
