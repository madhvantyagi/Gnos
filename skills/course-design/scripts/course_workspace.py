"""Safe, atomic storage for learner-specific course plans and lessons."""

import copy
import json
import os
from pathlib import Path
import re
import tempfile

from course_contract import course_fingerprint, course_topics, slug, validate_course
from lesson_contract import lesson_fingerprint, validate_lesson


MANIFEST_SCHEMA_VERSION = 1
_WORKSPACE_DIRECTORIES = (
    "lessons",
    "exercises",
    "submissions",
    "questions",
    "artifacts",
    "artifacts/videos",
    "artifacts/animations",
    "artifacts/diagrams",
    "artifacts/simulations",
    "artifacts/documents",
    "artifacts/generated",
    "archive",
    "site",
)


class ConflictError(ValueError):
    """Raised when a caller tries to overwrite a changed course snapshot."""


def _reject_symlink(path):
    if path.is_symlink():
        raise ValueError("Course workspaces cannot use symbolic links")


def _reject_existing_symlinks(path, relative_paths=()):
    """Reject symlinks in a workspace path and its managed child directories."""
    _reject_symlink(path)
    for relative in relative_paths:
        _reject_symlink(path / relative)


def workspace_path(learners_root: Path, learner_id: str, course_id: str) -> Path:
    """Return a safe learner/course workspace path without creating it."""
    learner_id = slug(learner_id)
    course_id = slug(course_id)
    root_input = Path(learners_root)
    _reject_symlink(root_input)
    # Keep the caller's absolute spelling stable (notably on macOS, where
    # temporary directories often live below a symlinked /var/folders path).
    # Existing learner/course components are checked below before use.
    root = root_input.absolute()
    learner = root / learner_id
    courses = learner / "courses"
    path = courses / course_id
    _reject_existing_symlinks(path, (learner, courses))
    return path


def _workspace_path_for_operation(path: Path) -> Path:
    """Validate a workspace path supplied by a caller before touching files."""
    path = Path(path)
    _reject_symlink(path)
    if not path.name:
        raise ValueError("Workspace path must name a course")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", path.name) or len(path.name) > 80:
        raise ValueError("Workspace path must end in a lowercase course slug")
    _reject_existing_symlinks(path, _WORKSPACE_DIRECTORIES)
    _reject_symlink(path / "course.json")
    _reject_symlink(path / "manifest.json")
    return path


def atomic_json(path: Path, data: dict) -> None:
    """Replace a JSON file in one rename, never exposing a partial snapshot."""
    path = Path(path)
    if not isinstance(data, dict):
        raise ValueError("JSON snapshot must be an object")
    if not path.parent.is_dir():
        raise FileNotFoundError(path.parent)
    _reject_symlink(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as handle:
            temporary = Path(handle.name)
            json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
        try:
            directory_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        except OSError:
            # Directory fsync is not available on every supported filesystem;
            # the atomic rename above still provides the snapshot guarantee.
            pass
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


def _read_json(path: Path) -> dict:
    _reject_symlink(path)
    try:
        with path.open(encoding="utf-8") as handle:
            value = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON snapshot: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON snapshot must be an object: {path}")
    return value


def read_plan(path: Path) -> dict:
    """Read and validate the canonical course plan in a workspace."""
    path = _workspace_path_for_operation(Path(path))
    return validate_course(_read_json(path / "course.json"))


def _make_workspace_directories(path: Path) -> None:
    for relative in _WORKSPACE_DIRECTORIES:
        directory = path / relative
        _reject_symlink(directory)
        directory.mkdir(parents=True, exist_ok=True)


def create_workspace(learners_root: Path, learner_id: str, plan: dict) -> Path:
    """Create or reopen a learner course workspace for a validated plan."""
    checked = validate_course(plan)
    path = workspace_path(learners_root, learner_id, checked["id"])
    path.mkdir(parents=True, exist_ok=True)
    _workspace_path_for_operation(path)
    _make_workspace_directories(path)

    course_file = path / "course.json"
    if course_file.exists():
        current = read_plan(path)
        if course_fingerprint(current) != course_fingerprint(checked):
            raise ConflictError("Course workspace already contains a different plan")
    else:
        atomic_json(course_file, checked)

    manifest_file = path / "manifest.json"
    if not manifest_file.exists():
        atomic_json(manifest_file, {
            "schema_version": MANIFEST_SCHEMA_VERSION,
            "course_id": checked["id"],
            "artifacts": [],
        })
    return path


def write_plan(path: Path, plan: dict, expected_fingerprint: str | None = None) -> str:
    """Validate and atomically write a course plan with optimistic concurrency."""
    checked = validate_course(plan)
    path = _workspace_path_for_operation(Path(path))
    course_file = path / "course.json"
    current = read_plan(path) if course_file.exists() else None
    if expected_fingerprint is not None:
        if current is None or course_fingerprint(current) != expected_fingerprint:
            raise ConflictError("Course changed; refresh before writing")
    if current is not None and current["id"] != checked["id"]:
        raise ValueError("Course ID cannot change within a workspace")
    atomic_json(course_file, checked)
    return course_fingerprint(checked)


def publish_lesson(path: Path, lesson: dict) -> str:
    """Validate and atomically save a lesson, exposing only ready lessons."""
    path = _workspace_path_for_operation(Path(path))
    plan = read_plan(path)
    plan_fingerprint = course_fingerprint(plan)
    original_plan = copy.deepcopy(plan)
    checked = validate_lesson(lesson, plan)
    lesson_dir = path / "lessons" / checked["id"]
    _reject_symlink(path / "lessons")
    _reject_symlink(lesson_dir)
    lesson_dir.mkdir(parents=False, exist_ok=True)
    atomic_json(lesson_dir / "lesson.json", checked)

    # Confirm the plan did not change while the lesson snapshot was written.
    if course_fingerprint(read_plan(path)) != plan_fingerprint:
        raise ConflictError("Course changed; refresh before publishing lesson")

    topics = course_topics(plan)
    for topic in topics:
        topic["lesson_ids"] = [
            lesson_id for lesson_id in topic["lesson_ids"]
            if lesson_id != checked["id"]
        ]
    if checked["publication"] == "ready":
        selected = next(topic for topic in topics if topic["id"] == checked["topic_id"])
        selected["lesson_ids"].append(checked["id"])
    if plan != original_plan:
        write_plan(path, plan, expected_fingerprint=plan_fingerprint)
    return lesson_fingerprint(checked)
