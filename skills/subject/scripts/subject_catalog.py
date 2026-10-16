#!/usr/bin/env python3
"""Discover subject/subfield candidates; the teacher selects the field of judgment."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "skills/subject/references/subject-map.json"


def load_catalog():
    data = json.loads(CATALOG.read_text())
    if data.get("schema_version") != 1 or not isinstance(data.get("subjects"), dict):
        raise ValueError("Subject map requires schema_version 1 and a subjects object")
    return data["subjects"]


def validate_catalog(data=None):
    """Keep the discovery index aligned with its authoritative guide sections."""
    data = load_catalog() if data is None else data
    guides = {path.stem: path for path in (ROOT / "skills/subject/subjects").glob("*.md")}
    if set(data) != set(guides):
        raise ValueError("Subject map and available guides differ")
    ids = set()
    for subject, record in data.items():
        if record.get("guide") != str(guides[subject].relative_to(ROOT)):
            raise ValueError(f"{subject}: guide must name the subject's canonical file")
        sections = [line[4:] for line in guides[subject].read_text().splitlines() if line.startswith("### ")]
        if [row.get("section") for row in record["subfields"]] != sections:
            raise ValueError(f"{subject}: subfields must match guide sections in order")
        for row in record["subfields"]:
            identifier = row.get("id", "")
            if not re.fullmatch(re.escape(subject) + r"\.[a-z0-9]+(?:-[a-z0-9]+)*", identifier) or identifier in ids:
                raise ValueError(f"Invalid or duplicate subfield ID: {identifier!r}")
            ids.add(identifier)
            if not isinstance(row.get("capability"), str) or not row["capability"].strip():
                raise ValueError(f"{identifier}: capability must be nonempty text")
            aliases = row.get("aliases")
            if not isinstance(aliases, list) or any(not isinstance(alias, str) or not alias.strip() for alias in aliases):
                raise ValueError(f"{identifier}: aliases must be a list of nonempty text")
            for bridge in row.get("bridges", []):
                if bridge.get("subject") not in data or bridge["subject"] == subject:
                    raise ValueError(f"{identifier}: bridge must name another available subject")
                if not isinstance(bridge.get("when"), str) or not bridge["when"].strip():
                    raise ValueError(f"{identifier}: bridge must state its bounded contribution")
    return data


def resolve_subfield(identifier, subject=None):
    for owner, record in load_catalog().items():
        for row in record["subfields"]:
            if row["id"] == identifier:
                if subject is not None and subject != owner:
                    raise ValueError(f"Subfield {identifier!r} belongs to {owner}, not {subject}")
                return dict(row, subject=owner, guide=record["guide"])
    raise ValueError(f"Unknown subfield: {identifier!r}; inspect a source for an unlisted specialty")


def search(query="", subject=None):
    data = load_catalog()
    if subject is not None and subject not in data:
        raise ValueError(f"Unknown subject: {subject!r}")
    needle = " ".join(query.casefold().split())
    rows = []
    for owner, record in data.items():
        if subject is not None and subject != owner:
            continue
        for row in record["subfields"]:
            # Deliberately literal discovery: aliases can overlap and a match is
            # a candidate, never evidence that this subject owns the request.
            haystack = " ".join([owner, record["title"], row["id"], row["section"],
                                 row["capability"], *row["aliases"]]).casefold()
            if needle in haystack:
                rows.append(dict(row, subject=owner, guide=record["guide"]))
    return {"candidates": rows, "selected_subject": None,
            "needs_source_inspection": not bool(rows)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subject")
    parser.add_argument("--query", default="")
    parser.add_argument("--subfield", help="Resolve a canonical stable ID; aliases are discovery only")
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    try:
        if args.validate:
            data = validate_catalog()
            result = {"subjects": len(data), "subfields": sum(len(row["subfields"]) for row in data.values())}
        elif args.subfield:
            result = resolve_subfield(args.subfield, args.subject)
        else:
            result = search(args.query, args.subject)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"Subject discovery failed: {exc}\n")


if __name__ == "__main__":
    main()
