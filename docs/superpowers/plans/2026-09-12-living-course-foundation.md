# Living Course Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace one-shot module plans with a researched, hierarchical, gradually authored course whose route and progress remain grounded in learner evidence.

**Architecture:** A version-2 course contract owns chapters, topics, sources, teaching routes, and the current frontier. Versioned lesson files own composed teaching content. Learner state owns enrollment and evidence, while a course workspace owns the canonical current plan and manifests; fingerprints connect them without editable duplication.

**Tech Stack:** Python 3 standard library, JSON, Markdown skill instructions, `unittest`

**Spec:** `docs/superpowers/specs/2026-09-12-living-course-portal-design.md`

## Global Constraints

- Teaching remains primarily conversational; the course is a living table of contents, not a one-shot content dump.
- Create a persistent course only for explicit sustained study or a destination requiring multiple branches, prerequisites, subjects, artifacts, assessments, or sessions.
- Never infer learner biography, ability, preference, or progress.
- `learners/<learner-id>/state.json` is authoritative for enrollment and evidence.
- `learners/<learner-id>/courses/<course-id>/course.json` is authoritative for the current plan.
- Progress is derived from attempts; opened files, watched media, scheduled minutes, and lesson counts do not establish understanding.
- Preserve stable chapter, topic, lesson, and concept IDs across revisions.
- Reject traversal and symbolic-link escapes; write JSON atomically.
- Keep shared routing, course design, teacher voice, subject judgment, learner evidence, and media mechanics in their owning files.
- Core functionality must use only the Python standard library.

---

### Task 1: Define and Validate the Version-2 Course Contract

**Files:**
- Create: `tests/test_course_contract_v2.py`
- Modify: `skills/course-design/scripts/course_contract.py`
- Modify: `skills/course-design/scripts/validate_course.py`
- Modify: `skills/course-design/references/course-contract.md`

**Interfaces:**
- Consumes: `skills/subject/references/resources.json`, `skills/*/SKILL.md`, `teachers/*/SOUL.md`
- Produces: `validate_course(data: dict) -> dict`, `upgrade_v1_course(data: dict) -> dict`, `course_topics(data: dict) -> list[dict]`, `course_fingerprint(data: dict) -> str`

- [ ] **Step 1: Add failing hierarchy, routing, source, dependency, and migration tests**

```python
def test_v2_course_accepts_chapters_topics_routes_and_sources(self):
    plan = valid_v2_course()
    checked = contract.validate_course(plan)
    self.assertEqual(checked["current"]["topic_id"], "local-change")
    self.assertEqual(contract.course_topics(checked)[0]["id"], "local-change")

def test_v2_course_rejects_unknown_teacher_skill_and_forward_dependency(self):
    for mutation in (unknown_teacher, unknown_skill, forward_dependency):
        with self.assertRaises(ValueError):
            contract.validate_course(mutation(valid_v2_course()))

def test_v1_upgrade_is_deterministic_and_preserves_concepts(self):
    first = contract.upgrade_v1_course(valid_v1_course())
    second = contract.upgrade_v1_course(valid_v1_course())
    self.assertEqual(first, second)
    self.assertEqual(first["schema_version"], 2)
    self.assertIn("math.derivative", first["chapters"][0]["topics"][0]["concepts"])
```

- [ ] **Step 2: Run the new contract tests and confirm the missing API failure**

Run: `python3 -m unittest tests.test_course_contract_v2 -v`

Expected: FAIL because `upgrade_v1_course`, `course_topics`, and version-2 validation do not exist.

- [ ] **Step 3: Implement the version-2 validator and deterministic version-1 adapter**

Use these public shapes and constants:

```python
COURSE_SCHEMA_VERSION = 2
PLANNING_STATES = ("current", "planned", "provisional", "retired", "out-of-scope")

def course_fingerprint(data):
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()

def course_topics(data):
    return [topic for chapter in data["chapters"] for topic in chapter["topics"]]

def validate_course(data):
    if data.get("schema_version") == 1:
        data = upgrade_v1_course(data)
    if data.get("schema_version") != COURSE_SCHEMA_VERSION:
        raise ValueError("Course requires schema_version 1 or 2")
    # Validate root identity, goal, revision, current frontier, sources,
    # chapter/topic ordering, globally unique IDs, earlier dependencies,
    # teachers, subjects, skill entrypoints, concepts, exercises, and resources.
    return data
```

The version-2 fixture must use this contract:

```json
{
  "schema_version": 2,
  "id": "gradient-descent",
  "title": "From slope to a working optimizer",
  "goal": "Explain, implement, and diagnose gradient descent.",
  "revision": 1,
  "revision_notes": [{"revision": 1, "date": "2026-09-12", "reason": "Initial researched route."}],
  "starting_evidence": [],
  "assumptions": ["Single-variable derivative knowledge is unverified."],
  "sources": {
    "openstax-calculus-1": {
      "title": "Calculus Volume 1",
      "url": "https://openstax.org/details/books/calculus-volume-1",
      "type": "textbook",
      "checked_on": "2026-09-12",
      "sections": ["3.5 The Chain Rule"],
      "verification_notes": "Section heading and access checked."
    }
  },
  "current": {"chapter_id": "change", "topic_id": "local-change", "next_step": "Check slope as local change."},
  "chapters": [{
    "id": "change",
    "title": "Local change",
    "state": "current",
    "topics": [{
      "id": "local-change",
      "title": "Slope as local change",
      "state": "current",
      "outcome": "Predict the sign of a small function change.",
      "subject": "math",
      "teacher": "math",
      "supporting_subjects": [],
      "supporting_teachers": [],
      "skill_routes": ["skills/subject/SKILL.md", "skills/subject/subjects/math.md"],
      "concepts": ["math.derivative"],
      "prerequisites": [],
      "minutes": 25,
      "resource_ids": ["openstax-calculus-1"],
      "exercise_ids": ["predict-change"],
      "lesson_ids": []
    }]
  }]
}
```

Validate teacher and subject availability from the repository rather than a six-item hard-coded tuple. Restrict `skill_routes` to existing repository-relative Markdown files beneath `skills/` and reject `..`, absolute paths, and non-`SKILL.md`/approved subject-reference destinations.

- [ ] **Step 4: Document planning states, source records, routes, and migration semantics**

Update `course-contract.md` with the exact version-2 fields above. State that `current`, `planned`, `provisional`, `retired`, and `out-of-scope` describe curriculum decisions, not learner understanding. Explain that version-1 plans are accepted only through deterministic upgrade and that newly written plans use version 2.

- [ ] **Step 5: Run the contract and existing core tests**

Run: `python3 -m unittest tests.test_course_contract_v2 tests.test_core -v`

Expected: PASS; existing version-1 fixtures validate through the adapter.

- [ ] **Step 6: Commit the contract slice**

```bash
git add tests/test_course_contract_v2.py skills/course-design/scripts/course_contract.py skills/course-design/scripts/validate_course.py skills/course-design/references/course-contract.md
git commit -m "Add living course contract"
```

### Task 2: Add the Composed Lesson Contract

**Files:**
- Create: `skills/course-design/scripts/lesson_contract.py`
- Create: `skills/course-design/scripts/validate_lesson.py`
- Create: `skills/course-design/references/lesson-contract.md`
- Create: `tests/test_lesson_contract.py`

**Interfaces:**
- Consumes: validated version-2 course dictionaries from `validate_course`
- Produces: `validate_lesson(data: dict, course: dict) -> dict`, `public_lesson(data: dict) -> dict`, `lesson_fingerprint(data: dict) -> str`

- [ ] **Step 1: Write failing tests for lesson placement, block order, exercises, and answer redaction**

```python
def test_lesson_combines_media_explanation_simulation_and_exercise(self):
    lesson = valid_lesson()
    checked = validate_lesson(lesson, valid_v2_course())
    self.assertEqual([b["type"] for b in checked["blocks"]],
                     ["explanation", "voice-animation", "interactive-graph", "exercise"])

def test_public_lesson_removes_private_evaluation_data(self):
    public = public_lesson(valid_lesson())
    exercise = public["exercises"][0]
    self.assertNotIn("success_criteria", exercise)
    self.assertNotIn("answer", exercise["evaluation"])

def test_lesson_rejects_topic_or_artifact_refs_outside_course(self):
    with self.assertRaises(ValueError):
        validate_lesson(lesson_with_unknown_topic(), valid_v2_course())
```

- [ ] **Step 2: Run the lesson tests and verify failure**

Run: `python3 -m unittest tests.test_lesson_contract -v`

Expected: FAIL because `lesson_contract.py` does not exist.

- [ ] **Step 3: Implement the lesson and exercise validators**

Use this stable public structure:

```python
BLOCK_TYPES = {
    "explanation", "bullets", "equation", "code", "voice-animation",
    "animation", "diagram", "interactive-graph", "simulation", "source",
    "exercise", "feedback", "artifact"
}
RESPONSE_TYPES = {"multiple-choice", "short-text", "long-text", "numeric", "code-text"}
EVALUATION_MODES = {"manual", "choice", "numeric"}

def validate_lesson(data, course):
    # Validate identity and course/chapter/topic membership.
    # Require globally unique block and exercise IDs inside the lesson.
    # Require every block's concepts to belong to the selected topic.
    # Require referenced exercise/artifact IDs to exist in the lesson.
    # Reject executable submitted-code evaluation.
    return data

def public_lesson(data):
    return {
        "schema_version": data["schema_version"],
        "id": data["id"],
        "course_id": data["course_id"],
        "chapter_id": data["chapter_id"],
        "topic_id": data["topic_id"],
        "title": data["title"],
        "purpose": data["purpose"],
        "concepts": list(data["concepts"]),
        "teacher": data["teacher"],
        "blocks": [public_block(block) for block in data["blocks"]],
        "exercises": [public_exercise(exercise) for exercise in data["exercises"]],
        "publication": data["publication"],
        "updated_at": data["updated_at"],
    }
```

An exercise records `id`, `concepts`, `prompt`, `response_type`, `evaluation`, `success_criteria`, and optional `reference_block_ids`. Blocks record `id`, `type`, `concepts`, `purpose`, and type-specific content or references. Publication states are `draft`, `ready`, and `archived`.
`public_block` and `public_exercise` likewise construct explicit allowlisted
dictionaries. Public evaluation data contains only the mode and response-shape
metadata needed to render an input; it never contains answers, accepted values,
tolerances, solutions, or success criteria.

- [ ] **Step 4: Document how lesson blocks form one teaching sequence**

In `lesson-contract.md`, include one complete example where an explanation introduces a symbol, a voice animation uses it, an interactive graph lets the learner vary it, and an exercise asks for a prediction. Require consistent terminology and forbid invent disconnected media galleries as lessons.

- [ ] **Step 5: Run focused tests**

Run: `python3 -m unittest tests.test_lesson_contract -v`

Expected: PASS.

- [ ] **Step 6: Commit the lesson contract**

```bash
git add skills/course-design/scripts/lesson_contract.py skills/course-design/scripts/validate_lesson.py skills/course-design/references/lesson-contract.md tests/test_lesson_contract.py
git commit -m "Add composed lesson contract"
```

### Task 3: Create Safe Learner Course Workspaces

**Files:**
- Create: `skills/course-design/scripts/course_workspace.py`
- Create: `tests/test_course_workspace.py`

**Interfaces:**
- Consumes: `validate_course`, `course_fingerprint`, `validate_lesson`, `lesson_fingerprint`
- Produces: `workspace_path(learners_root: Path, learner_id: str, course_id: str) -> Path`, `create_workspace(...) -> dict`, `read_plan(...) -> dict`, `write_plan(..., expected_fingerprint: str | None) -> str`, `publish_lesson(...) -> str`, `atomic_json(path: Path, data: dict) -> None`

- [ ] **Step 1: Write failing isolation, atomicity, and stale-write tests**

```python
def test_workspace_is_inside_learner_and_contains_initial_manifest(self):
    path = create_workspace(root, "alex", valid_v2_course())
    self.assertEqual(path, root / "alex" / "courses" / "gradient-descent")
    self.assertTrue((path / "course.json").is_file())
    self.assertEqual(json.loads((path / "manifest.json").read_text())["artifacts"], [])

def test_workspace_rejects_traversal_symlinks_and_stale_fingerprint(self):
    with self.assertRaises(ValueError):
        workspace_path(root, "../alex", "course")
    # Add a symlinked courses directory and assert rejection.
    with self.assertRaises(ConflictError):
        write_plan(path, revised_plan, expected_fingerprint="stale")
```

- [ ] **Step 2: Run workspace tests and verify failure**

Run: `python3 -m unittest tests.test_course_workspace -v`

Expected: FAIL because the workspace module is missing.

- [ ] **Step 3: Implement validated paths and atomic JSON snapshots**

```python
class ConflictError(ValueError):
    pass

def workspace_path(learners_root, learner_id, course_id):
    learner_id = slug(learner_id)
    course_id = slug(course_id)
    root = Path(learners_root).resolve()
    path = root / learner_id / "courses" / course_id
    for candidate in (root / learner_id, root / learner_id / "courses", path):
        if candidate.is_symlink():
            raise ValueError("Course workspaces cannot use symbolic links")
    return path

def write_plan(path, plan, expected_fingerprint=None):
    checked = validate_course(plan)
    current = read_plan(path) if (path / "course.json").exists() else None
    if expected_fingerprint and course_fingerprint(current) != expected_fingerprint:
        raise ConflictError("Course changed; refresh before writing")
    atomic_json(path / "course.json", checked)
    return course_fingerprint(checked)
```

Create only the directories named in the approved spec. Initialize `manifest.json` with `schema_version`, `course_id`, and empty `artifacts`; do not scan generated directories for publishable files.

- [ ] **Step 4: Implement lesson publication without exposing drafts**

`publish_lesson` validates the lesson against the current plan, writes
`lessons/<lesson-id>/lesson.json` atomically, and updates the topic's `lesson_ids`
only when the lesson publication state is `ready`. A draft may be saved but does
not enter the public lesson list.

- [ ] **Step 5: Run workspace and contract tests**

Run: `python3 -m unittest tests.test_course_workspace tests.test_course_contract_v2 tests.test_lesson_contract -v`

Expected: PASS.

- [ ] **Step 6: Commit the workspace slice**

```bash
git add skills/course-design/scripts/course_workspace.py tests/test_course_workspace.py
git commit -m "Add learner course workspaces"
```

### Task 4: Move Enrollment to Plan References with Compatibility Migration

**Files:**
- Modify: `skills/understanding-user-learning/scripts/learner_state.py`
- Modify: `skills/understanding-user-learning/scripts/memory_views.py`
- Modify: `skills/understanding-user-learning/references/evidence.md`
- Modify: `skills/understanding-user-learning/references/memory-categories.md`
- Modify: `tests/test_core.py`

**Interfaces:**
- Consumes: `create_workspace`, `read_plan`, `course_fingerprint`
- Produces: enrollment entries `{status, plan_ref, plan_revision, plan_fingerprint, completion_history}`, `resolve_enrolled_plan(learners_root: Path, learner_id: str, entry: dict) -> dict`

- [ ] **Step 1: Add failing enrollment-reference and legacy-migration tests**

```python
def test_enroll_stores_reference_not_editable_plan(self):
    self.enroll_v2("alex")
    entry = self.state("alex")["courses"]["gradient-descent"]
    self.assertNotIn("plan", entry)
    self.assertEqual(entry["plan_ref"], "courses/gradient-descent/course.json")
    self.assertEqual(len(entry["plan_fingerprint"]), 64)

def test_legacy_embedded_plan_migrates_once_without_losing_events(self):
    self.write_legacy_state()
    result = self.call("migrate-courses", "alex")
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertEqual(self.state("alex")["events"], self.legacy_events)
    self.assertTrue((self.root / "alex/courses/test-course/course.json").exists())
```

- [ ] **Step 2: Run the focused learner tests and confirm failure**

Run: `python3 -m unittest tests.test_core.LearnerTests -v`

Expected: FAIL because enrollment still embeds the whole plan.

- [ ] **Step 3: Implement referenced enrollment and explicit migration**

Add `migrate-courses` to the CLI. For a legacy entry containing `plan`, validate
and upgrade it, create its workspace, then replace the entry with:

```python
{
    "status": old["status"],
    "plan_ref": f"courses/{plan['id']}/course.json",
    "plan_revision": plan["revision"],
    "plan_fingerprint": course_fingerprint(plan),
    "completion_history": old.get("completion_history", []),
    **({"completed_at": old["completed_at"]} if old.get("completed_at") else {})
}
```

Run migration under the existing learner lock. Write the workspace before the
state reference; an interrupted write may leave an unreferenced valid workspace
but never a state reference to a missing plan. An identical rerun is idempotent.

- [ ] **Step 4: Make summaries and memory views resolve the canonical plan**

Replace `entry['plan']` reads with `resolve_enrolled_plan`. If the file fingerprint
does not match the enrollment reference, return a precise stale-reference error;
do not silently select either copy. Update the curriculum renderer to iterate
chapters and topics rather than version-1 modules.

- [ ] **Step 5: Run learner, workspace, and context-loader regressions**

Run: `python3 -m unittest tests.test_core tests.test_course_workspace -v`

Expected: PASS, including idempotent retry, completion history, and course-scoped resumption.

- [ ] **Step 6: Commit the learner-state migration**

```bash
git add skills/understanding-user-learning/scripts/learner_state.py skills/understanding-user-learning/scripts/memory_views.py skills/understanding-user-learning/references/evidence.md skills/understanding-user-learning/references/memory-categories.md tests/test_core.py
git commit -m "Reference canonical learner course plans"
```

### Task 5: Derive Hierarchical Progress and the Current Teaching Frontier

**Files:**
- Create: `skills/course-design/scripts/course_progress.py`
- Create: `tests/test_course_progress.py`
- Modify: `skills/understanding-user-learning/scripts/learner_state.py`
- Modify: `skills/understanding-user-learning/scripts/memory_views.py`

**Interfaces:**
- Consumes: validated course plan and validated learner events
- Produces: `derive_course_progress(plan: dict, events: list[dict]) -> dict`

- [ ] **Step 1: Write failing evidence-derived progress tests**

```python
def test_media_and_time_do_not_advance_progress(self):
    view = derive_course_progress(plan, [])
    self.assertEqual(view["topics"]["local-change"]["evidence"], "not-started")

def test_topic_progress_uses_weakest_relevant_concept_without_erasing_detail(self):
    view = derive_course_progress(plan, events_with_demonstrated_derivative_and_practicing_gradient())
    self.assertEqual(view["topics"]["gradient"]["evidence"], "practicing")
    self.assertEqual(view["concepts"]["math.derivative"]["status"], "demonstrated")

def test_later_failure_surfaces_needs_repair_and_preserves_attempts(self):
    view = derive_course_progress(plan, events_with_later_failure())
    self.assertEqual(view["concepts"]["math.gradient"]["display_status"], "needs-repair")
```

- [ ] **Step 2: Run progress tests and verify failure**

Run: `python3 -m unittest tests.test_course_progress -v`

Expected: FAIL because `course_progress.py` is missing.

- [ ] **Step 3: Implement course progress as a pure derived view**

```python
def derive_course_progress(plan, events):
    concept_summary = summarize_concepts(events)
    topics = {}
    for topic in course_topics(plan):
        statuses = [concept_summary.get(c, {"status": "not-started"}) for c in topic["concepts"]]
        topics[topic["id"]] = {
            "planning_state": topic["state"],
            "evidence": conservative_topic_status(statuses),
            "concept_ids": list(topic["concepts"]),
            "attempt_count": sum(s.get("attempts", 0) for s in statuses),
        }
    return {"course_id": plan["id"], "topics": topics, "concepts": concept_summary}
```

Keep the full concept evidence in the response. `needs-repair` is a display label
when a concept previously had an unassisted success and its latest relevant
attempt is partial or incorrect; it does not replace the stored result.

- [ ] **Step 4: Add progress to learner summary and hierarchical curriculum views**

Expose the derived course view only when a course is selected. Render chapter and
topic states plus exact evidence wording in `CURRICULUM.md`. Never render a
percentage called mastery.

- [ ] **Step 5: Run progress and learner tests**

Run: `python3 -m unittest tests.test_course_progress tests.test_core -v`

Expected: PASS.

- [ ] **Step 6: Commit progress derivation**

```bash
git add skills/course-design/scripts/course_progress.py tests/test_course_progress.py skills/understanding-user-learning/scripts/learner_state.py skills/understanding-user-learning/scripts/memory_views.py
git commit -m "Derive hierarchical course progress"
```

### Task 6: Teach Course Design to Build and Revise Gradually

**Files:**
- Modify: `skills/course-design/SKILL.md`
- Modify: `skills/course-design/references/course-research.md`
- Create: `skills/course-design/references/adaptive-lifecycle.md`
- Modify: `skills/learning/SKILL.md`
- Modify: `skills/learning/scripts/assemble_context.py`
- Modify: `docs/design.md`
- Modify: `tests/test_core.py`

**Interfaces:**
- Consumes: course v2, learner summary, course progress, lesson contract
- Produces: context assembly containing only the selected course, current topic, relevant evidence, last next step, and applicable skill/teacher routes

- [ ] **Step 1: Add failing context-selection tests**

```python
def test_course_mode_loads_adaptive_guidance_and_current_topic_routes(self):
    result = self.call_loader("--subject", "math", "--mode", "course", "--course", course_path)
    self.assertIn("ADAPTIVE COURSE LIFECYCLE", result.stdout)
    self.assertIn("skills/subject/subjects/math.md", result.stdout)

def test_local_doubt_manifest_does_not_load_course_design(self):
    result = self.call_loader("--subject", "math", "--manifest")
    self.assertNotIn("skills/course-design/SKILL.md", result.stdout)
```

- [ ] **Step 2: Run the context tests and verify failure**

Run: `python3 -m unittest tests.test_core -v`

Expected: FAIL for the new adaptive-guidance assertion.

- [ ] **Step 3: Rewrite course-design routing around the course-or-lesson decision**

The skill entrypoint must state these decisions directly:

```markdown
Use an in-turn lesson plan for one local target with only a few direct
dependencies. Use a persistent course when the learner requests sustained study
or the destination spans multiple competency branches, prerequisite chains,
subjects, artifacts, assessments, or sessions. A named topic may still need a
course when learning it well requires that breadth.
```

Route persistent work to `course-contract.md`, `course-research.md`,
`adaptive-lifecycle.md`, and `lesson-contract.md` only at the stage that needs
them. Require a researched chapter-level route at enrollment but detailed
authoring only for the current lesson.

- [ ] **Step 4: Document the adaptive turn loop and revision rules**

`adaptive-lifecycle.md` must specify: read evidence; locate the reasoning gap;
keep or revise the current frontier; author one coherent lesson; teach in chat;
publish only finished materials; record actual evidence; update the next step;
and revise provisional future topics with a reason. Include the distinction
between curriculum state and learner evidence.

- [ ] **Step 5: Update context assembly to resolve the current course workspace**

Load the canonical plan from the enrollment reference. In course mode, include
adaptive guidance and lesson contract paths. Include only teacher and subject
routes required by the current topic plus the lead teacher selected by the CLI;
reject a mismatch instead of silently combining unrelated routes.

- [ ] **Step 6: Run the harness and core regressions**

Run: `python3 skills/learning/scripts/validate_harness.py`

Expected: `Validated 6 skills, 12 subjects/teachers, links, Python syntax, and example courses.`

Run: `python3 -m unittest tests.test_core tests.test_course_contract_v2 tests.test_lesson_contract tests.test_course_progress -v`

Expected: PASS.

- [ ] **Step 7: Commit adaptive routing**

```bash
git add skills/course-design/SKILL.md skills/course-design/references/course-research.md skills/course-design/references/adaptive-lifecycle.md skills/learning/SKILL.md skills/learning/scripts/assemble_context.py docs/design.md tests/test_core.py
git commit -m "Design courses from learner evidence"
```

### Task 7: Upgrade Examples, Documentation, and Whole-Harness Validation

**Files:**
- Modify: `examples/courses/chain-rule/course.json`
- Modify: `examples/courses/gradient-descent/course.json`
- Create: `examples/courses/gradient-descent/lessons/slope-introduction.json`
- Modify: `examples/courses/gradient-descent/RESEARCH.md`
- Modify: `README.md`
- Modify: `skills/learning/scripts/validate_harness.py`
- Modify: `tests/test_core.py`

**Interfaces:**
- Consumes: all foundation contracts and CLIs
- Produces: validated version-2 focused and broad examples plus end-to-end documentation

- [ ] **Step 1: Add failing harness assertions for version-2 examples and lessons**

```python
for course_path in (ROOT / "examples/courses").glob("*/course.json"):
    plan = validate_course(json.loads(course_path.read_text()))
    if plan["schema_version"] != 2:
        errors.append(f"{course_path.relative_to(ROOT)}: example must use schema version 2")
for lesson_path in (ROOT / "examples/courses").glob("*/lessons/*.json"):
    plan = validate_course(json.loads((lesson_path.parents[1] / "course.json").read_text()))
    validate_lesson(json.loads(lesson_path.read_text()), plan)
```

- [ ] **Step 2: Run validation and verify the version-1 example failure**

Run: `python3 skills/learning/scripts/validate_harness.py`

Expected: FAIL because current examples still declare schema version 1.

- [ ] **Step 3: Convert examples to meaningful chapter/topic hierarchies**

Keep chain rule as a focused one-chapter course demonstrating that a narrow topic
can still become persistent when multi-session use is requested. Convert gradient
descent into multiple chapters with mathematics and computer-science topics,
explicit sources, provisional later chapters, and only its first ready lesson.
Do not pre-generate every lesson.

- [ ] **Step 4: Update README commands and explanations**

Document the workspace path, version-2 table of contents, enrollment migration,
course/lesson distinction, current frontier, and evidence-derived progress. Keep
the portal itself reserved for the second implementation plan.

- [ ] **Step 5: Run all foundation checks**

Run: `python3 skills/learning/scripts/validate_harness.py`

Expected: validation reports six skills, twelve subjects/teachers, valid links,
Python syntax, version-2 courses, and composed lessons.

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests pass; optional dependency tests may skip only with their
existing explicit reason.

Run: `git diff --check`

Expected: no output.

- [ ] **Step 6: Commit the complete foundation documentation**

```bash
git add examples/courses README.md skills/learning/scripts/validate_harness.py tests/test_core.py
git commit -m "Document living GNOS courses"
```
