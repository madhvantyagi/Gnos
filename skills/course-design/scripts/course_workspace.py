"""Safe, atomic storage for learner-specific course plans and lessons."""

import copy
from contextlib import contextmanager
import json
import os
from pathlib import Path
import threading
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


_LOCK_STATE = threading.local()


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
    if ".." in path.parts:
        raise ValueError("Workspace path cannot contain traversal components")
    if len(path.parts) < 3 or path.parts[-2] != "courses":
        raise ValueError("Workspace path must end in <learner-id>/courses/<course-id>")
    try:
        slug(path.parts[-3])
        slug(path.parts[-1])
    except ValueError as exc:
        raise ValueError("Workspace path must use lowercase learner and course slugs") from exc
    _reject_symlink(path)
    learner = path.parent.parent
    courses = path.parent
    for candidate in (
        learner,
        courses,
        path,
        path / "course.json",
        path / "manifest.json",
        path / "lessons",
        path / ".course.lock",
    ):
        _reject_symlink(candidate)
    return path


def _held_locks():
    locks = getattr(_LOCK_STATE, "paths", None)
    if locks is None:
        locks = set()
        _LOCK_STATE.paths = locks
    return locks


@contextmanager
def _workspace_lock(path: Path):
    """Hold an exclusive lock for all mutations of one workspace plan."""
    path = Path(path)
    key = str(path.absolute())
    held = _held_locks()
    if key in held:
        yield
        return

    lock_path = path / ".course.lock"
    _reject_symlink(lock_path)
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    fd = None
    try:
        fd = os.open(lock_path, flags | nofollow, 0o600)
    except FileExistsError as exc:
        raise ConflictError("Course workspace is busy; retry after refresh") from exc
    held.add(key)
    try:
        os.write(fd, f"pid={os.getpid()}\n".encode("ascii"))
        os.fsync(fd)
        yield
    finally:
        held.discard(key)
        if fd is not None:
            os.close(fd)
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


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


def _atomic_bytes(path: Path, data: bytes) -> None:
    """Atomically replace a file while preserving its original bytes."""
    path = Path(path)
    if not path.parent.is_dir():
        raise FileNotFoundError(path.parent)
    _reject_symlink(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=path.parent,
                                         prefix=f".{path.name}.", suffix=".tmp",
                                         delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
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
    with _workspace_lock(path):
        _make_workspace_directories(path)

        course_file = path / "course.json"
        if course_file.exists():
            current = read_plan(path)
            if course_fingerprint(current) != course_fingerprint(checked):
                raise ConflictError("Course workspace already contains a different plan")
        else:
            _write_plan_unlocked(path, checked, None)

        manifest_file = path / "manifest.json"
        if not manifest_file.exists():
            atomic_json(manifest_file, {
                "schema_version": MANIFEST_SCHEMA_VERSION,
                "course_id": checked["id"],
                "artifacts": [],
            })
    return path


def _write_plan_unlocked(path: Path, checked: dict, expected_fingerprint: str | None) -> str:
    checked = validate_course(checked)
    course_file = path / "course.json"
    current = read_plan(path) if course_file.exists() else None
    if expected_fingerprint is not None:
        if current is None or course_fingerprint(current) != expected_fingerprint:
            raise ConflictError("Course changed; refresh before writing")
    if current is not None and current["id"] != checked["id"]:
        raise ValueError("Course ID cannot change within a workspace")
    fingerprint = course_fingerprint(checked)
    atomic_json(course_file, checked)
    return fingerprint


def write_plan(path: Path, plan: dict, expected_fingerprint: str | None = None) -> str:
    """Validate and atomically write a course plan with optimistic concurrency."""
    checked = validate_course(plan)
    path = _workspace_path_for_operation(Path(path))
    with _workspace_lock(path):
        return _write_plan_unlocked(path, checked, expected_fingerprint)


def publish_lesson(path: Path, lesson: dict) -> str:
    """Validate and atomically save a lesson, exposing only ready lessons."""
    path = _workspace_path_for_operation(Path(path))
    with _workspace_lock(path):
        plan = read_plan(path)
        plan_fingerprint = course_fingerprint(plan)
        original_plan = copy.deepcopy(plan)
        checked = validate_lesson(lesson, plan)
        lesson_fingerprint_value = lesson_fingerprint(checked)
        lesson_dir = path / "lessons" / checked["id"]
        lesson_file = lesson_dir / "lesson.json"
        _reject_symlink(lesson_dir)
        _reject_symlink(lesson_file)
        had_lesson = lesson_file.exists()
        previous_bytes = lesson_file.read_bytes() if had_lesson else None
        lesson_dir.mkdir(parents=False, exist_ok=True)
        try:
            atomic_json(lesson_file, checked)

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
                _write_plan_unlocked(path, plan, expected_fingerprint=plan_fingerprint)
        except Exception:
            if had_lesson:
                _atomic_bytes(lesson_file, previous_bytes)
            else:
                try:
                    lesson_file.unlink()
                except FileNotFoundError:
                    pass
                try:
                    lesson_dir.rmdir()
                except OSError:
                    pass
            raise
        return lesson_fingerprint_value


def main():
    """CLI for the operations a teacher turn needs: publish a formal lesson."""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    publish = commands.add_parser("publish", help="validate and publish a lesson into a course workspace")
    publish.add_argument("workspace", type=Path,
                         help="course workspace path: learners/<learner>/courses/<course-id>")
    publish.add_argument("--lesson", type=Path, required=True,
                         help="lesson JSON file to validate and publish")
    args = parser.parse_args()
    try:
        if args.command == "publish":
            lesson = json.loads(args.lesson.read_text())
            fingerprint = publish_lesson(args.workspace, lesson)
            print(f"Published {lesson['id']} (fingerprint {fingerprint})")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(1, f"Course workspace error: {exc}\n")


if __name__ == "__main__":
    main()
