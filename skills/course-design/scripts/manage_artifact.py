"""CLI for registering, listing, and archiving course artifacts."""

import argparse
import json
from pathlib import Path
import sys

from artifact_manifest import archive_artifact, manifest_fingerprint, read_manifest, ready_artifacts, register_artifact
from course_workspace import workspace_path


def _parser():
    parser = argparse.ArgumentParser(description="Manage explicitly published course artifacts")
    parser.add_argument("--learners-root", type=Path, required=True)
    commands = parser.add_subparsers(dest="command", required=True)

    register = commands.add_parser("register")
    register.add_argument("learner_id")
    register.add_argument("course_id")
    register.add_argument("--file", type=Path, required=True)
    register.add_argument("--fingerprint")

    archive = commands.add_parser("archive")
    archive.add_argument("learner_id")
    archive.add_argument("course_id")
    archive.add_argument("--artifact-id", required=True)
    archive.add_argument("--fingerprint", required=True)

    listing = commands.add_parser("list")
    listing.add_argument("learner_id")
    listing.add_argument("course_id")
    listing.add_argument("--ready", action="store_true")
    return parser


def _load_artifact(path: Path):
    try:
        with path.open(encoding="utf-8") as handle:
            value = json.load(handle)
    except OSError as exc:
        raise ValueError(f"Cannot read artifact file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Artifact file is not valid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError("Artifact file must contain a JSON object")
    return value


def main(argv=None):
    args = _parser().parse_args(argv)
    try:
        workspace = workspace_path(args.learners_root, args.learner_id, args.course_id)
        if args.command == "register":
            artifact = _load_artifact(args.file)
            fingerprint = register_artifact(workspace, artifact, args.fingerprint)
            result = {"course_id": args.course_id, "artifact_id": artifact.get("id"),
                      "fingerprint": fingerprint}
        elif args.command == "archive":
            fingerprint = archive_artifact(workspace, args.artifact_id, args.fingerprint)
            result = {"course_id": args.course_id, "artifact_id": args.artifact_id,
                      "fingerprint": fingerprint}
        else:
            manifest = read_manifest(workspace)
            artifacts = ready_artifacts(manifest) if args.ready else manifest["artifacts"]
            result = {"course_id": args.course_id, "artifacts": artifacts,
                      "fingerprint": manifest_fingerprint(manifest)}
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
