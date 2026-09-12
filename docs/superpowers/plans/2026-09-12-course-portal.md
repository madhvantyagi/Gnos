# Interactive Course Portal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a private local visual interface that presents living courses, accepts exercises and questions, and organizes finished teaching artifacts without replacing chat as the primary teaching environment.

**Architecture:** A loopback-only Python server reads validated course workspaces and exposes redacted JSON endpoints. Static HTML, CSS, and JavaScript render a responsive editorial interface. All mutations pass through atomic workspace APIs; learner evidence changes only through explicit review in the existing learner-state workflow.

**Tech Stack:** Python 3 standard library `http.server`, JSON, HTML5, CSS, browser JavaScript, `unittest`

**Spec:** `docs/superpowers/specs/2026-09-12-living-course-portal-design.md`

## Global Constraints

- Complete `docs/superpowers/plans/2026-09-12-living-course-foundation.md` first.
- Bind the portal to `127.0.0.1` only; do not add internet deployment or cloud sync.
- The webpage is a visual companion; teaching and adaptive judgment remain in chat.
- Never invoke Codex, an MCP server, or another model silently from the webpage.
- Publish only artifacts explicitly registered as `ready`; never scan render directories.
- Redact success criteria, solutions, and deterministic answer data from public payloads.
- Preserve all attempts; open-ended work remains `awaiting-review` until explicit GNOS review.
- Archive is the default removal behavior; permanent deletion and evidence retraction remain separate explicit actions.
- Reject traversal, symbolic-link escapes, stale fingerprints, oversized JSON bodies, and unknown mutation actions.
- Interactive artifacts run in sandboxed frames and cannot read arbitrary learner files.
- Use Newsreader for display text, Inter for UI/body, and IBM Plex Mono sparingly, with offline-safe fallbacks.
- Use the approved warm neutral and deep teal tokens; meet WCAG AA and respect `prefers-reduced-motion`.
- Do not add a frontend framework, database, arbitrary submitted-code execution, or background service.

---

### Task 1: Register and Archive Finished Artifacts

**Files:**
- Create: `skills/course-design/scripts/artifact_manifest.py`
- Create: `skills/course-design/scripts/manage_artifact.py`
- Create: `skills/course-design/references/artifact-manifest.md`
- Create: `tests/test_artifact_manifest.py`

**Interfaces:**
- Consumes: a validated learner course workspace from `course_workspace.workspace_path`
- Produces: `validate_manifest(data: dict, course_id: str) -> dict`, `register_artifact(workspace: Path, artifact: dict, expected_fingerprint: str | None) -> str`, `archive_artifact(workspace: Path, artifact_id: str, expected_fingerprint: str) -> str`, `ready_artifacts(manifest: dict) -> list[dict]`

- [ ] **Step 1: Write failing registration, readiness, fallback, and archive tests**

```python
def test_only_registered_ready_artifacts_are_public(self):
    register_artifact(workspace, ready_video())
    register_artifact(workspace, draft_diagram())
    self.assertEqual([a["id"] for a in ready_artifacts(read_manifest(workspace))], ["gradient-video"])

def test_unknown_type_is_valid_when_open_action_is_safe(self):
    item = unknown_local_artifact(type="notebook", path="artifacts/generated/demo.ipynb")
    self.assertEqual(register_artifact(workspace, item), manifest_fingerprint(workspace))

def test_archive_preserves_file_and_manifest_history(self):
    archive_artifact(workspace, "gradient-video", current_fingerprint())
    self.assertTrue((workspace / "artifacts/videos/gradient.mp4").exists())
    self.assertEqual(find_artifact("gradient-video")["status"], "archived")
```

- [ ] **Step 2: Run tests and confirm the missing-module failure**

Run: `python3 -m unittest tests.test_artifact_manifest -v`

Expected: FAIL because the manifest module is absent.

- [ ] **Step 3: Implement the manifest contract and atomic mutations**

```python
ARTIFACT_STATUSES = {"draft", "ready", "archived", "failed"}
INLINE_MIME_PREFIXES = ("image/", "video/", "audio/")

def ready_artifacts(manifest):
    return sorted(
        (copy.deepcopy(a) for a in manifest["artifacts"] if a["status"] == "ready"),
        key=lambda a: (a["updated_at"], a["id"]), reverse=True)

def register_artifact(workspace, artifact, expected_fingerprint=None):
    # Validate stable IDs, placement, concepts, path/URL, MIME, timestamps,
    # publication state, and path containment. Replace the same artifact ID only
    # with a newer updated_at value; preserve its history entry.
    # Compare the manifest fingerprint before atomic replacement.
    return new_fingerprint
```

An artifact contains `id`, `type`, `title`, `purpose`, `concepts`, `chapter_id`,
`topic_id`, `lesson_id`, `location`, `mime_type`, `metadata`, `status`,
`created_at`, and `updated_at`. `location` is exactly one of a contained relative
`path` or an `https` URL. Reject `file:` URLs, protocol-relative URLs, path
traversal, absolute paths, and symbolic links.

- [ ] **Step 4: Implement the artifact CLI**

Support exact commands:

```bash
python3 skills/course-design/scripts/manage_artifact.py --learners-root learners \
  register alex gradient-descent --file artifact.json
python3 skills/course-design/scripts/manage_artifact.py --learners-root learners \
  archive alex gradient-descent --artifact-id gradient-video --fingerprint <sha256>
python3 skills/course-design/scripts/manage_artifact.py --learners-root learners \
  list alex gradient-descent --ready
```

Print a JSON result containing the course ID, artifact ID where applicable, and
new manifest fingerprint. Do not claim registration after a failed write.

- [ ] **Step 5: Run manifest tests**

Run: `python3 -m unittest tests.test_artifact_manifest -v`

Expected: PASS.

- [ ] **Step 6: Commit artifact publication**

```bash
git add skills/course-design/scripts/artifact_manifest.py skills/course-design/scripts/manage_artifact.py skills/course-design/references/artifact-manifest.md tests/test_artifact_manifest.py
git commit -m "Register finished course artifacts"
```

### Task 2: Build Redacted Portal Views

**Files:**
- Create: `skills/course-design/scripts/portal_views.py`
- Create: `tests/test_portal_views.py`

**Interfaces:**
- Consumes: canonical course plan, ready lessons, ready artifacts, learner summary, submissions, questions
- Produces: `build_portal_view(workspace: Path, learner_summary: dict) -> dict`, `public_artifact(artifact: dict) -> dict`, `recent_and_older(items: list[dict], current_topic_id: str, limit: int = 6) -> dict`

- [ ] **Step 1: Write failing redaction, hierarchy, and aging tests**

```python
def test_portal_view_contains_current_frontier_and_hierarchical_contents(self):
    view = build_portal_view(workspace, learner_summary)
    self.assertEqual(view["course"]["current"]["topic_id"], "local-change")
    self.assertEqual(view["contents"][0]["topics"][0]["progress"]["evidence"], "practicing")

def test_portal_payload_never_contains_private_answer_data(self):
    payload = json.dumps(build_portal_view(workspace, learner_summary))
    for secret in ("success_criteria", "accepted", "tolerance", "solution"):
        self.assertNotIn(f'"{secret}"', payload)

def test_old_items_move_to_earlier_without_disappearing(self):
    groups = recent_and_older(eight_artifacts(), "gradient", limit=3)
    self.assertEqual(len(groups["recent"]), 3)
    self.assertEqual(len(groups["earlier"]), 5)
```

- [ ] **Step 2: Run view tests and verify failure**

Run: `python3 -m unittest tests.test_portal_views -v`

Expected: FAIL because the view builder is missing.

- [ ] **Step 3: Implement one sanitized portal read model**

```python
def build_portal_view(workspace, learner_summary):
    plan = read_plan(workspace)
    lessons = [public_lesson(read_json(p)) for p in ready_lesson_paths(workspace, plan)]
    artifacts = [public_artifact(a) for a in ready_artifacts(read_manifest(workspace))]
    return {
        "course": public_course(plan),
        "contents": build_contents(plan, learner_summary.get("course_progress", {})),
        "lessons": recent_and_older(lessons, plan["current"]["topic_id"]),
        "artifacts": group_artifacts(artifacts, plan["current"]["topic_id"]),
        "exercises": public_exercises(lessons, read_submissions(workspace)),
        "questions": public_questions(workspace),
    }
```

Copy only explicit public fields. Do not rely on deleting a few known secret keys
from arbitrary input. Group artifact types into `watch`, `generated`, and
`resources`, while retaining the original type for generic presentation.

- [ ] **Step 4: Run portal view tests**

Run: `python3 -m unittest tests.test_portal_views -v`

Expected: PASS.

- [ ] **Step 5: Commit redacted views**

```bash
git add skills/course-design/scripts/portal_views.py tests/test_portal_views.py
git commit -m "Build safe course portal views"
```

### Task 3: Persist Exercise Drafts, Attempts, and Course Questions

**Files:**
- Create: `skills/course-design/scripts/portal_interactions.py`
- Create: `skills/course-design/scripts/manage_interaction.py`
- Create: `skills/course-design/references/portal-interactions.md`
- Create: `tests/test_portal_interactions.py`

**Interfaces:**
- Consumes: validated public exercise IDs and workspace paths
- Produces: `save_draft(...) -> dict`, `submit_attempt(...) -> dict`, `request_hint(...) -> dict`, `create_question(...) -> dict`, `answer_question(...) -> dict`, `list_pending(workspace: Path) -> dict`

- [ ] **Step 1: Write failing attempt-preservation and question-boundary tests**

```python
def test_submitting_twice_preserves_both_attempts(self):
    first = submit_attempt(workspace, "predict-change", {"text": "It increases"})
    second = submit_attempt(workspace, "predict-change", {"text": "It increases by about 4h"})
    self.assertNotEqual(first["attempt_id"], second["attempt_id"])
    self.assertEqual(len(read_attempts(workspace, "predict-change")), 2)

def test_open_ended_attempt_waits_for_review(self):
    result = submit_attempt(workspace, "explain-gradient", {"text": "My reasoning"})
    self.assertEqual(result["status"], "awaiting-review")

def test_question_is_saved_without_invoking_a_model(self):
    result = create_question(workspace, valid_question_context())
    self.assertEqual(result["status"], "pending")
    self.assertNotIn("answer", result)
```

- [ ] **Step 2: Run interaction tests and verify failure**

Run: `python3 -m unittest tests.test_portal_interactions -v`

Expected: FAIL because persistence APIs do not exist.

- [ ] **Step 3: Implement append-only attempts and deterministic checks**

```python
def submit_attempt(workspace, exercise_id, response, attempt_id=None):
    exercise = find_exercise(workspace, exercise_id)
    attempt_id = attempt_id or new_slugged_id("attempt")
    status, feedback = evaluate_if_deterministic(exercise, response)
    record = {
        "id": attempt_id,
        "exercise_id": exercise_id,
        "submitted_at": utc_now(),
        "response": validate_response(exercise, response),
        "status": status,
        "feedback": feedback,
        "evidence_event_id": None,
    }
    atomic_create_json(attempt_path(workspace, exercise_id, attempt_id), record)
    return record
```

Return `checked` only for server-side choice or numeric evaluation. Return
`awaiting-review` for text and code text. The browser never receives the private
answer data used by deterministic evaluation. Duplicate attempt IDs with
identical payloads are idempotent; conflicting reuse fails.

- [ ] **Step 4: Implement the Ask Codex queue and explicit answer writer**

A question records stable ID, learner text, created time, status, and validated
context IDs for course, chapter, topic, lesson, block, artifact, exercise, and
attempt. It contains no arbitrary file paths or copied private criteria.
`answer_question` requires explicit answer text and changes `pending` to
`answered`; it never calls a model.

Expose CLI commands `pending`, `answer-question`, and `review-attempt` so an
active GNOS task can inspect and update interactions. `review-attempt` stores a
review object but does not yet write learner evidence; Task 4 owns that bridge.

- [ ] **Step 5: Run interaction tests**

Run: `python3 -m unittest tests.test_portal_interactions -v`

Expected: PASS.

- [ ] **Step 6: Commit interactions**

```bash
git add skills/course-design/scripts/portal_interactions.py skills/course-design/scripts/manage_interaction.py skills/course-design/references/portal-interactions.md tests/test_portal_interactions.py
git commit -m "Persist course exercises and questions"
```

### Task 4: Convert Explicit Reviews into Learner Evidence

**Files:**
- Modify: `skills/course-design/scripts/manage_interaction.py`
- Modify: `skills/understanding-user-learning/scripts/learner_state.py`
- Modify: `skills/understanding-user-learning/references/evidence.md`
- Modify: `tests/test_portal_interactions.py`
- Modify: `tests/test_core.py`

**Interfaces:**
- Consumes: a reviewed attempt with result, help, kind, interpretation, and next step
- Produces: `record_reviewed_attempt(learners_root: Path, learner_id: str, course_id: str, attempt_id: str, review: dict) -> str`

- [ ] **Step 1: Write failing explicit-review and no-fabrication tests**

```python
def test_unreviewed_attempt_cannot_become_evidence(self):
    with self.assertRaises(ValueError):
        record_reviewed_attempt(root, "alex", "gradient-descent", attempt_id, {})

def test_review_creates_one_linked_evidence_event(self):
    event_id = record_reviewed_attempt(root, "alex", "gradient-descent", attempt_id, valid_review())
    attempt = read_attempt(workspace, attempt_id)
    self.assertEqual(attempt["evidence_event_id"], event_id)
    self.assertEqual(summary("alex")["concepts"]["math.derivative"]["status"], "demonstrated")
```

- [ ] **Step 2: Run the focused tests and verify failure**

Run: `python3 -m unittest tests.test_portal_interactions tests.test_core -v`

Expected: FAIL because reviewed attempts are not connected to learner state.

- [ ] **Step 3: Implement the explicit evidence bridge**

Require review fields `result`, `help`, `kind`, `interpretation`, and `next_step`.
Construct the existing event format from the actual exercise prompt and stored
learner response. Use deterministic event ID `portal-<attempt-id>` so retry is
idempotent. Write learner state first, then atomically link its event ID into the
attempt. If the link write fails, a retry recognizes the existing identical
event and repairs the link without duplicating evidence.

- [ ] **Step 4: Run interaction and learner-state tests**

Run: `python3 -m unittest tests.test_portal_interactions tests.test_core tests.test_course_progress -v`

Expected: PASS.

- [ ] **Step 5: Commit the review bridge**

```bash
git add skills/course-design/scripts/manage_interaction.py skills/understanding-user-learning/scripts/learner_state.py skills/understanding-user-learning/references/evidence.md tests/test_portal_interactions.py tests/test_core.py
git commit -m "Record reviewed portal attempts"
```

### Task 5: Add Validated Future-Curriculum Edits

**Files:**
- Create: `skills/course-design/scripts/course_edits.py`
- Create: `tests/test_course_edits.py`

**Interfaces:**
- Consumes: current plan, expected plan fingerprint, existing learner evidence
- Produces: `apply_course_edit(workspace: Path, action: dict, evidence: dict, expected_fingerprint: str) -> str`

- [ ] **Step 1: Write failing revision and historical-ID protection tests**

```python
def test_rename_future_topic_increments_revision_and_records_reason(self):
    fingerprint = apply_course_edit(workspace, {
        "type": "rename-topic", "topic_id": "step-size",
        "title": "Choosing a stable step", "reason": "Learner requested clearer wording"
    }, evidence={}, expected_fingerprint=current_fingerprint())
    self.assertEqual(read_plan(workspace)["revision"], 2)

def test_retire_topic_with_evidence_keeps_id_and_events(self):
    apply_course_edit(workspace, retire("gradient"), evidence=gradient_evidence,
                      expected_fingerprint=current_fingerprint())
    self.assertEqual(find_topic("gradient")["state"], "retired")
    self.assertEqual(gradient_evidence, original_evidence)
```

- [ ] **Step 2: Run edit tests and verify failure**

Run: `python3 -m unittest tests.test_course_edits -v`

Expected: FAIL because the edit module is missing.

- [ ] **Step 3: Implement a closed edit vocabulary**

Support only `rename-topic`, `add-topic`, `reorder-future-topics`, and
`retire-topic`. Reject edits to IDs, concepts with evidence, the current topic's
identity, and completed evidence. Every successful edit validates the full plan,
increments revision exactly once, appends a dated reason, updates enrollment
revision/fingerprint under the learner lock, and returns the new fingerprint.

- [ ] **Step 4: Run course edit, workspace, and learner tests**

Run: `python3 -m unittest tests.test_course_edits tests.test_course_workspace tests.test_core -v`

Expected: PASS.

- [ ] **Step 5: Commit safe curriculum edits**

```bash
git add skills/course-design/scripts/course_edits.py tests/test_course_edits.py
git commit -m "Add safe living course revisions"
```

### Task 6: Serve One Course Safely on Loopback

**Files:**
- Create: `skills/course-design/scripts/portal_server.py`
- Create: `tests/test_portal_server.py`

**Interfaces:**
- Consumes: portal views, interaction APIs, artifact archive, course edit API, portal static assets
- Produces: `create_server(config: PortalConfig) -> ThreadingHTTPServer`, CLI `portal_server.py <learner> <course-id>`

- [ ] **Step 1: Write failing endpoint, traversal, origin, and payload-limit tests**

```python
def test_server_binds_loopback_and_returns_redacted_course(self):
    with running_server() as url:
        self.assertTrue(url.startswith("http://127.0.0.1:"))
        payload = get_json(url + "/api/course")
        self.assertNotIn("success_criteria", json.dumps(payload))

def test_post_rejects_wrong_origin_and_large_body(self):
    self.assertEqual(post("/api/attempts", origin="https://evil.example").status, 403)
    self.assertEqual(post("/api/attempts", body=b"x" * 1_048_577).status, 413)

def test_static_route_rejects_traversal_and_unregistered_files(self):
    self.assertIn(get("/files/../../state.json").status, (400, 404))
    self.assertEqual(get("/files/artifacts/videos/unregistered.mp4").status, 404)
```

- [ ] **Step 2: Run server tests and verify failure**

Run: `python3 -m unittest tests.test_portal_server -v`

Expected: FAIL because the server does not exist.

- [ ] **Step 3: Implement the loopback server and explicit routes**

```python
@dataclass(frozen=True)
class PortalConfig:
    learners_root: Path
    learner_id: str
    course_id: str
    host: str = "127.0.0.1"
    port: int = 0
    max_body_bytes: int = 1_048_576

READ_ROUTES = {"/api/course", "/api/pending", "/api/health"}
WRITE_ROUTES = {"/api/drafts", "/api/attempts", "/api/questions", "/api/archive", "/api/course-edits"}
```

Reject any configured host other than `127.0.0.1`. Issue a random session token
at startup, set it in a `SameSite=Strict` cookie, and require both the token and
same loopback Origin on writes. Add `Cache-Control: no-store` to JSON and private
files. Add `X-Content-Type-Options: nosniff`, a restrictive content-security
policy, and `frame-ancestors 'self'`.

Serve files only by registered artifact ID through `/files/<artifact-id>` after
resolving the current ready manifest entry. Never map request paths directly to
the filesystem.

- [ ] **Step 4: Implement atomic snapshot refresh**

`GET /api/course` rebuilds from committed JSON snapshots and returns an ETag made
from plan, manifest, learner-state, submission, and question fingerprints. Honor
`If-None-Match` with `304`. This gives the frontend efficient polling without a
background watcher or partially read files.

- [ ] **Step 5: Run portal server tests**

Run: `python3 -m unittest tests.test_portal_server -v`

Expected: PASS.

- [ ] **Step 6: Commit the local server**

```bash
git add skills/course-design/scripts/portal_server.py tests/test_portal_server.py
git commit -m "Serve private course portal"
```

### Task 7: Build the Responsive Editorial Portal Shell

**Files:**
- Create: `skills/course-design/assets/portal/index.html`
- Create: `skills/course-design/assets/portal/styles.css`
- Create: `skills/course-design/assets/portal/app.js`
- Create: `tests/test_portal_assets.py`

**Interfaces:**
- Consumes: `GET /api/course` and write endpoints from Task 6
- Produces: accessible views `home`, `contents`, `lessons`, `exercises`, `watch`, `generated`, `resources`, `ask`, and `archive`

- [ ] **Step 1: Write failing structural asset tests**

```python
def test_portal_has_one_main_landmark_and_named_navigation(self):
    parser = PortalHTMLParser(INDEX.read_text())
    self.assertEqual(parser.main_count, 1)
    self.assertEqual(parser.nav_label, "Course sections")
    self.assertEqual(parser.live_region_count, 1)

def test_css_contains_focus_reduced_motion_and_approved_tokens(self):
    css = STYLES.read_text()
    self.assertIn(":focus-visible", css)
    self.assertIn("prefers-reduced-motion", css)
    self.assertIn("--color-canvas: #F7F5F0", css)
    self.assertIn("--color-accent: #176B68", css)
```

- [ ] **Step 2: Run asset tests and verify failure**

Run: `python3 -m unittest tests.test_portal_assets -v`

Expected: FAIL because portal assets do not exist.

- [ ] **Step 3: Implement semantic shell and tabs**

`index.html` contains a skip link, compact course header, labeled primary nav,
single `<main id="course-view" tabindex="-1">`, and polite status region. Tabs
are ordinary links or buttons with `aria-current`; JavaScript supports browser
history and restores per-topic scroll positions.

Desktop uses a 248px contents rail and a central reading column capped at 760px,
with media allowed to expand to 1080px. Mobile below 760px uses a sticky compact
header and horizontally scrollable section navigation, never horizontal body
scrolling. Touch targets are at least 44px.

- [ ] **Step 4: Implement the approved visual tokens and typography**

```css
:root {
  --color-canvas: #F7F5F0;
  --color-surface: #FFFEFA;
  --color-surface-muted: #EFEEE8;
  --color-ink: #202426;
  --color-ink-muted: #697174;
  --color-line: #D9D8D0;
  --color-accent: #176B68;
  --color-accent-soft: #DCEDEA;
  --color-success: #2D765B;
  --color-warning: #946B22;
  --color-danger: #A4473D;
  --font-display: "Newsreader", Georgia, serif;
  --font-body: Inter, ui-sans-serif, system-ui, sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, monospace;
}
```

Use local/system fallbacks when web fonts are unavailable. Use continuous
editorial sections, not a border around every paragraph. Keep transitions
between 150ms and 220ms and remove them under reduced motion.

- [ ] **Step 5: Implement refresh, empty, and error states**

Poll `/api/course` with the last ETag every five seconds while the page is
visible, pause when hidden, and rerender only after a changed response. Preserve
the current tab and scroll. Show truthful inline errors with Retry; never replace
the entire course with an error screen. Use the exact empty-state meanings from
the specification without claiming content is still generating.

- [ ] **Step 6: Run asset and server tests**

Run: `python3 -m unittest tests.test_portal_assets tests.test_portal_server -v`

Expected: PASS.

- [ ] **Step 7: Commit the portal shell**

```bash
git add skills/course-design/assets/portal tests/test_portal_assets.py
git commit -m "Build responsive course portal shell"
```

### Task 8: Render Composed Lessons, Media, Exercises, and Earlier Work

**Files:**
- Modify: `skills/course-design/assets/portal/app.js`
- Modify: `skills/course-design/assets/portal/styles.css`
- Modify: `tests/test_portal_assets.py`
- Modify: `tests/test_portal_server.py`

**Interfaces:**
- Consumes: redacted lesson blocks, ready artifacts, exercise states, questions, recent/earlier groups
- Produces: safe type-specific renderers and direct interaction forms

- [ ] **Step 1: Add failing browser-contract tests for renderers and forms**

```python
def test_renderer_registry_has_specialized_and_generic_fallbacks(self):
    js = APP.read_text()
    for renderer in ("renderVideo", "renderDiagram", "renderSimulation", "renderPdf", "renderGenericArtifact"):
        self.assertIn(renderer, js)

def test_interactive_iframe_is_sandboxed_without_same_origin(self):
    html = render_fixture("interactive-graph")
    frame = first_iframe(html)
    self.assertIn("allow-scripts", frame["sandbox"])
    self.assertNotIn("allow-same-origin", frame["sandbox"])
```

- [ ] **Step 2: Run portal asset tests and verify failure**

Run: `python3 -m unittest tests.test_portal_assets -v`

Expected: FAIL because type-specific lesson rendering is absent.

- [ ] **Step 3: Implement continuous lesson block rendering**

Render explanation, bullets, equations, code, media, simulations, sources,
exercises, and feedback in declared order. Each transition uses the stored
teaching purpose and consistent concept vocabulary; it must not invent generic
connector language. Treat text lessons as reading content rather than file cards.

- [ ] **Step 4: Implement honest artifact viewers**

- Images and diagrams: contained preview, descriptive alt text, keyboard-openable
  full view, and close button with focus restoration.
- Videos and animations: native controls, poster when registered, duration, and
  captions/transcript actions only when those files are registered.
- Interactive graphs and simulations: sandboxed iframe with title and explicit
  open-full action.
- PDFs: registered first-page thumbnail and page count when available, plus
  `Open full document`; never force a tiny reader.
- Unknown types: type, filename/title, size when known, purpose, and safe Open or
  Download action. Never hide them for lacking a specialized viewer.

- [ ] **Step 5: Implement exercise and Ask Codex forms**

Render response controls from the declared response type. Save drafts on an
explicit action or a debounced change with visible saved state. Submit with a
new idempotency ID, retain the response, and render `checked` or
`awaiting-review` accurately. A retry creates a new attempt without erasing the
old one. Ask Codex submits selected context and displays `pending` until an
answer exists; do not show fake typing.

- [ ] **Step 6: Implement recent and archive disclosure**

Home shows the current topic, next learner action, latest lesson, and at most six
recent ready artifacts. Lessons and exercises show current-topic items first.
Place older entries inside a keyboard-accessible native `<details>` disclosure
labeled `Earlier work`; Archive exposes the complete retained collection.

- [ ] **Step 7: Run portal tests**

Run: `python3 -m unittest tests.test_portal_assets tests.test_portal_server tests.test_portal_views tests.test_portal_interactions -v`

Expected: PASS.

- [ ] **Step 8: Commit full portal rendering**

```bash
git add skills/course-design/assets/portal/app.js skills/course-design/assets/portal/styles.css tests/test_portal_assets.py tests/test_portal_server.py
git commit -m "Render composed course materials"
```

### Task 9: Integrate Portal Use into GNOS and Verify the Whole Experience

**Files:**
- Modify: `skills/course-design/SKILL.md`
- Create: `skills/course-design/references/course-portal.md`
- Modify: `skills/learning/SKILL.md`
- Modify: `skills/learning/scripts/validate_harness.py`
- Modify: `README.md`
- Create: `examples/courses/gradient-descent/artifacts/gradient-video.json`
- Create: `tests/test_portal_end_to_end.py`

**Interfaces:**
- Consumes: all portal and foundation commands
- Produces: documented create, serve, publish, submit, inspect, answer, review, archive, and resume workflow

- [ ] **Step 1: Add a failing end-to-end local workflow test**

```python
def test_course_portal_round_trip(self):
    enroll("alex", course_path)
    publish_lesson("alex", "gradient-descent", lesson_path)
    register("alex", "gradient-descent", artifact_path)
    with running_portal("alex", "gradient-descent") as client:
        client.submit("predict-change", {"text": "about 4h"})
        question_id = client.ask({"text": "Why is this only approximate?", "lesson_id": "slope-introduction"})
    self.assertIn(question_id, pending_questions("alex", "gradient-descent"))
    review_latest_attempt("alex", result="correct", help="none", kind="application")
    self.assertEqual(summary("alex")["concepts"]["math.derivative"]["status"], "demonstrated")
```

- [ ] **Step 2: Run the end-to-end test and verify failure**

Run: `python3 -m unittest tests.test_portal_end_to_end -v`

Expected: FAIL until skill routing, example registration, and command integration are complete.

- [ ] **Step 3: Teach GNOS when to create, mention, and reopen the portal**

Course design creates the workspace only after the learner is known, tracking is
wanted, and a persistent course is justified. Learning mentions the portal when
it is created, when resuming after a gap, or when a useful artifact is published.
It does not advertise it after every turn. Chat remains the primary teaching
surface.

Document these exact commands:

```bash
python3 skills/course-design/scripts/portal_server.py alex gradient-descent
python3 skills/course-design/scripts/manage_artifact.py register alex gradient-descent --file artifact.json
python3 skills/course-design/scripts/manage_interaction.py pending alex gradient-descent
python3 skills/course-design/scripts/manage_interaction.py answer-question alex gradient-descent --question-id <id> --file answer.json
python3 skills/course-design/scripts/manage_interaction.py review-attempt alex gradient-descent --attempt-id <id> --file review.json
```

- [ ] **Step 4: Validate documentation links, assets, and schemas**

Extend `validate_harness.py` to require the portal assets, parse every example
course/lesson/artifact, and confirm each referenced local artifact exists. Keep
network MCP and font availability outside this deterministic validation.

- [ ] **Step 5: Run automated verification**

Run: `python3 skills/learning/scripts/validate_harness.py`

Expected: PASS with six skills, twelve subjects/teachers, links, Python syntax,
courses, lessons, artifacts, and portal assets validated.

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests pass; dependency-gated media tests skip only with their
explicit existing reason.

Run: `git diff --check`

Expected: no output.

- [ ] **Step 6: Render and inspect the portal**

Start the example portal on an ephemeral loopback port. Inspect desktop widths
1440px and 1024px and mobile widths 390px and 320px. Verify keyboard-only tabs,
focus visibility, native media controls, long titles, empty states, earlier-work
disclosure, pending review, pending Ask Codex, media failures, unknown artifact
fallback, and reduced motion. Save screenshots beneath `output/qa/course-portal/`;
do not commit them.

- [ ] **Step 7: Correct visual or interaction defects and rerun affected checks**

For every observed defect, add or tighten the smallest meaningful regression
test, make the focused correction, rerun that test, then rerun the full harness.
Do not weaken the visual system into generic cards to make one fixture fit.

- [ ] **Step 8: Commit integration and documentation**

```bash
git add skills/course-design/SKILL.md skills/course-design/references/course-portal.md skills/learning/SKILL.md skills/learning/scripts/validate_harness.py README.md examples/courses/gradient-descent/artifacts/gradient-video.json tests/test_portal_end_to_end.py
git commit -m "Integrate the GNOS course portal"
```
