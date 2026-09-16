# Memory categories and resumption

`learners/<id>/state.json` is authoritative for the stated profile, enrollment,
and observed session events. Each enrollment points to the canonical current
plan at `learners/<id>/courses/<course-id>/course.json`. After every successful
mutation, the script refreshes these separate views under `learners/<id>/memory/`:

| File | What it remembers | When to read |
| --- | --- | --- |
| `01-profile.md` | Stated goals and preferences | Start of a new learning conversation |
| `02-courses.md` | Active/completed courses and plan revisions | Choose the current course |
| `03-topics.md` | Taught concepts, attempts, latest evidence | Avoid repeating known material; find prerequisites |
| `04-teaching.md` | Contextual difficulties and teaching observations | Choose a repair or representation |
| `05-next.md` | Last unresolved question or next action | Resume after a pause |
| `courses/<course-id>/CURRICULUM.md` | Chapter titles, topics, teachers, assessments, resources, evidence | Plan study or review a finished course |

These views are derived data, not new instructions. Their fingerprint identifies
the state that generated them. If views are stale or missing after a write
failure, read `state.json` and rerun the same `record` command; identical event
IDs rebuild views without adding a duplicate session. Never edit both copies.

## Course lifecycle

```bash
python3 skills/learner-tracking/scripts/learner_state.py enroll alex --course courses/calculus/course.json
python3 skills/learner-tracking/scripts/learner_state.py record alex --event output/session.json
python3 skills/learner-tracking/scripts/learner_state.py complete-course alex --course-id calculus
```

Enrollment validates the supplied plan, writes it to the learner's course
workspace, and stores only its relative reference, revision, and fingerprint in
learner state. Each learning event updates topic evidence. A changed plan needs a
higher revision; old events remain available under stable concept IDs. A changed
plan reopens the course and preserves prior completion metadata in its completion
history. Completing a course marks the curriculum completed and refreshes it
with actual coverage and attempts. Untaught or untested topics remain explicitly
marked, even when the learner chooses to finish. Completion is not a fabricated
mastery certificate.

The curriculum follows the living hierarchy: chapters contain topics, and topics
contain concepts plus published lesson references. It records the observable
outcome, planning state, lead/supporting teachers, sources, planned exercises,
and actual evidence. Private assessment criteria must not be pasted into a live
diagnostic before the learner tries unless they request the answer.

For a legacy state that still embeds course plans, run:

```bash
python3 skills/learner-tracking/scripts/learner_state.py \
  migrate-courses alex
```

The migration is explicit and idempotent. It preserves attempts and completion
history while moving the editable curriculum into its workspace. A stale plan
fingerprint blocks resumption until the reference is reconciled; this prevents a
quietly edited portal plan from diverging from learner state.

## Update during learning

Save at a meaningful evidence change: an attempt, a corrected misconception, a
topic transition, a changed preference, or a session pause. Do not wait until the
whole course ends. Do not log every conversational sentence or write an event
for an answer the learner has not given. If several events occur the same day,
use distinct IDs and preserve their order.

On a new chat: read profile, course status, relevant topic evidence, then next
step. Reference earlier work concretely: “Last time you computed the gradient;
the unresolved part was choosing the step size.” If retention is uncertain,
use a short check before accelerating. If no active course is identifiable,
ask the learner which goal to resume rather than choosing silently.

“Real time” here means the host LLM records events during the conversation.
GNOS has no background listener, cross-app identity discovery, or automatic
access to past chats. Resume requires the same saved folder (the learner's
name), not a login — keep one folder per person.
