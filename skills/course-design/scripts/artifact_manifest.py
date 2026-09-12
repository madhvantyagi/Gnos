"""Validated, manifest-driven publication of learner course artifacts."""

import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlparse

import course_workspace
from course_contract import slug


MANIFEST_SCHEMA_VERSION = 1
ARTIFACT_STATUSES = {"draft", "ready", "archived", "failed"}
INLINE_MIME_PREFIXES = ("image/", "video/", "audio/")
_TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_MIME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.+-]*/[A-Za-z0-9][A-Za-z0-9.+-]*$")
_REQUIRED_FIELDS = (
    "id", "type", "title", "purpose", "concepts", "chapter_id", "topic_id",
    "lesson_id", "location", "mime_type", "metadata", "status", "created_at",
    "updated_at",
)

# The workspace module owns the conflict type used by all course mutations. It
# is re-exported here so callers do not need to know which storage layer raises
# optimistic-concurrency failures.
ConflictError = course_workspace.ConflictError


def _nonempty_text(value, label, maximum=4000):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(f"{label} must be nonempty text")
    if any(ord(character) < 32 and character not in "\t\n" for character in value):
        raise ValueError(f"{label} contains a control character")
    return value


def _timestamp(value, label):
    if not isinstance(value, str) or not _TIMESTAMP_RE.fullmatch(value):
        raise ValueError(f"{label} must be an ISO UTC timestamp")
    try:
        return datetime.fromisoformat(value[:-1]).replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise ValueError(f"{label} must be a real ISO UTC timestamp") from exc


def _validate_location_shape(location):
    if not isinstance(location, dict):
        raise ValueError("location must contain exactly one path or url")
    keys = [key for key in ("path", "url") if key in location]
    if len(keys) != 1 or len(location) != 1:
        raise ValueError("location must contain exactly one path or url")
    key = keys[0]
    value = location[key]
    if not isinstance(value, str) or not value:
        raise ValueError(f"location.{key} must be nonempty text")
    if "\x00" in value:
        raise ValueError("location cannot contain NUL bytes")
    if key == "url":
        parsed = urlparse(value)
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
            raise ValueError("location.url must be an HTTPS URL")
    return key, value


def _validate_artifact_shape(artifact):
    if not isinstance(artifact, dict):
        raise ValueError("Each artifact must be an object")
    for field in _REQUIRED_FIELDS:
        if field not in artifact:
            raise ValueError(f"Artifact requires {field}")
    artifact_id = slug(artifact.get("id"))
    _nonempty_text(artifact.get("type"), f"{artifact_id}.type", maximum=120)
    _nonempty_text(artifact.get("title"), f"{artifact_id}.title")
    _nonempty_text(artifact.get("purpose"), f"{artifact_id}.purpose")
    concepts = artifact.get("concepts")
    if not isinstance(concepts, list) or not concepts:
        raise ValueError(f"{artifact_id}.concepts must be a nonempty list")
    for concept in concepts:
        _nonempty_text(concept, f"{artifact_id}.concepts", maximum=240)
    if len(concepts) != len(set(concepts)):
        raise ValueError(f"{artifact_id}.concepts must be unique")
    for field in ("chapter_id", "topic_id", "lesson_id"):
        slug(artifact.get(field))
    if "exercise_id" in artifact and artifact["exercise_id"] is not None:
        slug(artifact["exercise_id"])
    location_key, _ = _validate_location_shape(artifact.get("location"))
    mime_type = artifact.get("mime_type")
    if not isinstance(mime_type, str) or not _MIME_RE.fullmatch(mime_type):
        raise ValueError(f"{artifact_id}.mime_type must be a valid MIME type")
    if not isinstance(artifact.get("metadata"), dict):
        raise ValueError(f"{artifact_id}.metadata must be an object")
    try:
        json.dumps(artifact["metadata"], ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{artifact_id}.metadata must be JSON data") from exc
    if artifact.get("status") not in ARTIFACT_STATUSES:
        raise ValueError(f"{artifact_id}.status must be draft, ready, archived, or failed")
    created = _timestamp(artifact.get("created_at"), f"{artifact_id}.created_at")
    updated = _timestamp(artifact.get("updated_at"), f"{artifact_id}.updated_at")
    if updated < created:
        raise ValueError(f"{artifact_id}.updated_at must be greater than or equal to created_at")
    return artifact_id, location_key


def validate_manifest(data: dict, course_id: str) -> dict:
    """Validate a manifest snapshot without mutating it."""
    if not isinstance(data, dict) or data.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise ValueError("Manifest requires schema_version 1")
    expected_course_id = slug(course_id)
    if data.get("course_id") != expected_course_id:
        raise ValueError("manifest.course_id must refer to the selected course")
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError("manifest.artifacts must be a list")
    history = data.get("history", [])
    if not isinstance(history, list):
        raise ValueError("manifest.history must be a list")
    ids = set()
    for artifact in artifacts:
        artifact_id, _ = _validate_artifact_shape(artifact)
        if artifact_id in ids:
            raise ValueError(f"Duplicate artifact ID: {artifact_id}")
        ids.add(artifact_id)
    for artifact in history:
        _validate_artifact_shape(artifact)
    return data


def manifest_fingerprint(manifest: dict) -> str:
    """Return the stable hash used as the manifest optimistic-concurrency token."""
    payload = json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _checked_workspace(workspace: Path) -> Path:
    return course_workspace._workspace_path_for_operation(Path(workspace))


def _read_manifest_unlocked(workspace: Path) -> dict:
    manifest_path = workspace / "manifest.json"
    current = course_workspace._read_json(manifest_path)
    plan = course_workspace.read_plan(workspace)
    return validate_manifest(current, plan["id"])


def read_manifest(workspace: Path) -> dict:
    """Read and validate the manifest for a validated course workspace."""
    workspace = _checked_workspace(workspace)
    return _read_manifest_unlocked(workspace)


def _validate_local_path(workspace: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute() or ".." in path.parts or "." in path.parts or "\\" in raw_path:
        raise ValueError("Artifact path must be a clean workspace-relative path")
    if not path.parts:
        raise ValueError("Artifact path must not be empty")
    candidate = workspace.joinpath(*path.parts)
    current = workspace
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("Artifact paths cannot use symbolic links")
    root = workspace.resolve()
    try:
        candidate.resolve(strict=False).relative_to(root)
    except ValueError as exc:
        raise ValueError("Artifact path must remain inside the course workspace") from exc
    if candidate.exists() and candidate.is_dir():
        raise ValueError("Artifact path must name a file")
    return candidate


def _validate_artifact_for_workspace(workspace: Path, artifact: dict, plan: dict) -> dict:
    checked = copy.deepcopy(artifact)
    artifact_id, location_key = _validate_artifact_shape(checked)
    chapter_ids = {chapter["id"]: chapter for chapter in plan.get("chapters", [])}
    chapter = chapter_ids.get(checked["chapter_id"])
    if chapter is None:
        raise ValueError(f"{artifact_id}.chapter_id must refer to a course chapter")
    topics = {topic["id"]: topic for topic in chapter.get("topics", [])}
    if checked["topic_id"] not in topics:
        raise ValueError(f"{artifact_id}.topic_id must belong to {checked['chapter_id']}")
    topic = topics[checked["topic_id"]]
    if checked["lesson_id"] not in topic.get("lesson_ids", []):
        raise ValueError(f"{artifact_id}.lesson_id must be a published lesson for {checked['topic_id']}")
    topic_concepts = set(topic.get("concepts", []))
    if any(concept not in topic_concepts for concept in checked["concepts"]):
        raise ValueError(f"{artifact_id}.concepts must belong to {checked['topic_id']}")
    if location_key == "path":
        resolved_path = _validate_local_path(workspace, checked["location"]["path"])
        if checked["status"] == "ready" and not resolved_path.is_file():
            raise ValueError("Ready local artifacts must name an existing regular file")
    return checked


def _manifest_with_defaults(manifest, course_id):
    checked = copy.deepcopy(manifest)
    checked.setdefault("history", [])
    return validate_manifest(checked, course_id)


def _check_expected_fingerprint(manifest, expected_fingerprint):
    current_fingerprint = manifest_fingerprint(manifest)
    if expected_fingerprint is not None and expected_fingerprint != current_fingerprint:
        raise ConflictError("Manifest changed; refresh before writing")
    return current_fingerprint


def register_artifact(workspace: Path, artifact: dict, expected_fingerprint: str | None = None) -> str:
    """Validate and atomically register one artifact in the course manifest."""
    workspace = _checked_workspace(workspace)
    # Validate the candidate before acquiring the mutation lock where possible;
    # the plan is read again under the lock to make the write decision current.
    candidate = copy.deepcopy(artifact)
    with course_workspace._workspace_lock(workspace):
        plan = course_workspace.read_plan(workspace)
        checked = _validate_artifact_for_workspace(workspace, candidate, plan)
        manifest = _manifest_with_defaults(_read_manifest_unlocked(workspace), plan["id"])
        _check_expected_fingerprint(manifest, expected_fingerprint)
        existing_index = next((index for index, item in enumerate(manifest["artifacts"])
                               if item["id"] == checked["id"]), None)
        if existing_index is not None:
            previous = manifest["artifacts"][existing_index]
            if _timestamp(checked["updated_at"], "updated_at") <= _timestamp(previous["updated_at"], "updated_at"):
                raise ValueError("Replacing an artifact requires a newer updated_at timestamp")
            manifest["history"].append(copy.deepcopy(previous))
            manifest["artifacts"][existing_index] = checked
        else:
            manifest["artifacts"].append(checked)
        validate_manifest(manifest, plan["id"])
        course_workspace.atomic_json(workspace / "manifest.json", manifest)
        return manifest_fingerprint(manifest)


def archive_artifact(workspace: Path, artifact_id: str, expected_fingerprint: str) -> str:
    """Archive an artifact without deleting its registered file."""
    workspace = _checked_workspace(workspace)
    artifact_id = slug(artifact_id)
    with course_workspace._workspace_lock(workspace):
        plan = course_workspace.read_plan(workspace)
        manifest = _manifest_with_defaults(_read_manifest_unlocked(workspace), plan["id"])
        _check_expected_fingerprint(manifest, expected_fingerprint)
        index = next((index for index, item in enumerate(manifest["artifacts"])
                      if item["id"] == artifact_id), None)
        if index is None:
            raise ValueError(f"Unknown artifact ID: {artifact_id}")
        current = manifest["artifacts"][index]
        if current["status"] == "archived":
            raise ValueError(f"Artifact is already archived: {artifact_id}")
        manifest["history"].append(copy.deepcopy(current))
        archived = copy.deepcopy(current)
        archived["status"] = "archived"
        now = datetime.now(timezone.utc).replace(microsecond=0)
        previous_updated = _timestamp(archived["updated_at"], "updated_at")
        if now > previous_updated:
            archived["updated_at"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        manifest["artifacts"][index] = archived
        validate_manifest(manifest, plan["id"])
        course_workspace.atomic_json(workspace / "manifest.json", manifest)
        return manifest_fingerprint(manifest)


def ready_artifacts(manifest: dict) -> list[dict]:
    """Return a defensive, newest-first view of explicitly ready artifacts."""
    return sorted(
        (copy.deepcopy(artifact) for artifact in manifest.get("artifacts", [])
         if artifact.get("status") == "ready"),
        key=lambda artifact: (artifact["updated_at"], artifact["id"]), reverse=True,
    )
