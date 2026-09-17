"""Course contracts and source catalog lookup; no third-party dependencies."""

import copy
from datetime import date
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[3]
COURSE_SCHEMA_VERSION = 2
PLANNING_STATES = ("current", "planned", "provisional", "retired", "out-of-scope")
REPRESENTATION_KINDS = ("text", "manim", "image", "simulation", "diagram", "pdf", "exercise")


def _available_subjects():
    subject_dir = ROOT / "skills/subject/subjects"
    return tuple(sorted(path.stem for path in subject_dir.glob("*.md")))


def _available_teachers():
    teacher_dir = ROOT / "teachers"
    return tuple(sorted(path.name for path in teacher_dir.iterdir()
                        if (path / "SOUL.md").is_file()))


# Existing callers use this as the CLI's choices list. Its value is derived
# from the repository at import time, rather than being an authority baked
# into the contract.
SUBJECTS = _available_subjects()
TEACHERS = _available_teachers()


def slug(value):
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value) or len(value) > 80:
        raise ValueError(f"Expected a lowercase slug of at most 80 characters: {value!r}")
    return value


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be nonempty text")
    return value


def strings(value, label, required=False):
    if not isinstance(value, list) or (required and not value):
        raise ValueError(f"{label} must be a {'nonempty ' if required else ''}list")
    for item in value:
        nonempty(item, label)
    return value


def resources():
    return json.loads((ROOT / "skills/subject/references/resources.json").read_text())


def course_fingerprint(data):
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def course_topics(data):
    return [topic for chapter in data["chapters"] for topic in chapter["topics"]]


def _known_teachers():
    return set(TEACHERS)


def _known_subjects():
    return set(SUBJECTS)


def _validate_skill_route(route):
    nonempty(route, "skill route")
    path = Path(route)
    if path.is_absolute() or ".." in path.parts or "\\" in route:
        raise ValueError(f"Invalid skill route: {route!r}")
    if not path.parts or path.parts[0] != "skills":
        raise ValueError(f"Skill route must be beneath skills/: {route!r}")
    resolved = ROOT / path
    if not resolved.is_file():
        raise ValueError(f"Unknown skill route: {route!r}")
    approved = path.name == "SKILL.md" or (
        len(path.parts) == 4
        and path.parts[:3] == ("skills", "subject", "subjects")
        and path.suffix == ".md"
    )
    if not approved:
        raise ValueError(f"Skill route is not an approved entry point: {route!r}")


def _validate_source_registry(source_data):
    """Check per-course sources. Any slug is allowed; the course search fills this."""
    if not isinstance(source_data, dict):
        raise ValueError("sources must be an object")
    for source_id, source in source_data.items():
        slug(source_id)
        if not isinstance(source, dict):
            raise ValueError(f"{source_id}: source must be an object")
        nonempty(source.get("title"), f"{source_id}.title")
        location_fields = [field for field in ("url", "local_path") if source.get(field)]
        if len(location_fields) != 1:
            raise ValueError(f"{source_id}: source requires exactly one nonempty url or local_path")
        if source.get("url"):
            parsed = urlparse(source["url"])
            if parsed.scheme != "https" or not parsed.netloc:
                raise ValueError(f"{source_id}: source URL must use HTTPS")
        if source.get("local_path"):
            local_path = Path(source["local_path"])
            if local_path.is_absolute() or ".." in local_path.parts or "\\" in source["local_path"]:
                raise ValueError(f"{source_id}: local_path must be repository-relative and safe")
            resolved = (ROOT / local_path).resolve()
            root = ROOT.resolve()
            if not resolved.is_file() or root not in resolved.parents:
                raise ValueError(f"{source_id}: local_path must name a repository file")
        nonempty(source.get("type"), f"{source_id}.type")
        nonempty(source.get("checked_on"), f"{source_id}.checked_on")
        strings(source.get("sections"), f"{source_id}.sections")
        nonempty(source.get("verification_notes"), f"{source_id}.verification_notes")


def _validate_revision_notes(notes):
    if not isinstance(notes, list) or not notes:
        raise ValueError("revision_notes must be a nonempty list")
    previous = 0
    for note in notes:
        if not isinstance(note, dict):
            raise ValueError("Each revision note must be an object")
        revision = note.get("revision")
        if type(revision) is not int or revision < 1:
            raise ValueError("revision_notes.revision must be a positive integer")
        if revision <= previous:
            raise ValueError("revision_notes.revision must increase with each note")
        previous = revision
        revision_date = note.get("date")
        nonempty(revision_date, "revision_notes.date")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", revision_date):
            raise ValueError("revision_notes.date must be an ISO YYYY-MM-DD date")
        try:
            date.fromisoformat(revision_date)
        except ValueError as exc:
            raise ValueError("revision_notes.date must be a real ISO YYYY-MM-DD date") from exc
        nonempty(note.get("reason"), "revision_notes.reason")


def _validate_v2(data):
    if not isinstance(data, dict) or data.get("schema_version") != COURSE_SCHEMA_VERSION:
        raise ValueError("Course requires schema_version 1 or 2")
    slug(data.get("id"))
    for key in ("title", "goal"):
        nonempty(data.get(key), key)
    if "vision" in data and data["vision"] is not None:
        nonempty(data.get("vision"), "vision")
    depth = data.get("depth")
    if depth is not None:
        if depth not in ("survey", "working", "mastery"):
            raise ValueError("depth must be survey, working, or mastery")
    if "length" in data and data["length"] is not None:
        nonempty(data.get("length"), "length")
    revision = data.get("revision")
    if type(revision) is not int or revision < 1:
        raise ValueError("revision must be a positive integer")
    _validate_revision_notes(data.get("revision_notes"))
    if not isinstance(data.get("starting_evidence"), list):
        raise ValueError("starting_evidence must be a list")
    strings(data.get("assumptions"), "assumptions")

    _validate_source_registry(data.get("sources"))

    chapters = data.get("chapters")
    if not isinstance(chapters, list) or not chapters:
        raise ValueError("chapters must be a nonempty list")
    known_teachers = _known_teachers()
    known_subjects = _known_subjects()
    chapter_ids = set()
    topic_ids = set()
    concept_ids = set()
    exercise_ids = set()
    lesson_ids = set()
    seen_topics = set()

    for chapter in chapters:
        if not isinstance(chapter, dict):
            raise ValueError("Each chapter must be an object")
        chapter_id = slug(chapter.get("id"))
        if chapter_id in chapter_ids:
            raise ValueError(f"Duplicate chapter ID: {chapter_id}")
        chapter_ids.add(chapter_id)
        nonempty(chapter.get("title"), f"{chapter_id}.title")
        if chapter.get("state") not in PLANNING_STATES:
            raise ValueError(f"{chapter_id}: invalid planning state")
        topics = chapter.get("topics")
        if not isinstance(topics, list) or not topics:
            raise ValueError(f"{chapter_id}.topics must be a nonempty list")
        for topic in topics:
            if not isinstance(topic, dict):
                raise ValueError(f"{chapter_id}: each topic must be an object")
            topic_id = slug(topic.get("id"))
            if topic_id in topic_ids:
                raise ValueError(f"Duplicate topic ID: {topic_id}")
            topic_ids.add(topic_id)
            for key in ("title", "outcome"):
                nonempty(topic.get(key), f"{topic_id}.{key}")
            if topic.get("state") not in PLANNING_STATES:
                raise ValueError(f"{topic_id}: invalid planning state")
            if "teacher" not in topic:
                raise ValueError(f"{topic_id}: teacher must be present")
            subject = topic.get("subject")
            teacher = topic.get("teacher")
            if subject not in known_subjects:
                raise ValueError(f"{topic_id}: unknown subject")
            if (teacher is not None and
                    (not isinstance(teacher, str) or teacher not in known_teachers or teacher != subject)):
                raise ValueError(f"{topic_id}: unknown or mismatched lead teacher")

            supporting_subjects = strings(topic.get("supporting_subjects"), "supporting_subjects")
            if len(supporting_subjects) != len(set(supporting_subjects)):
                raise ValueError(f"{topic_id}: duplicate supporting subject")
            if any(support_subject not in known_subjects or support_subject == subject
                   for support_subject in supporting_subjects):
                raise ValueError(f"{topic_id}: invalid supporting subject")
            supporting_teachers = strings(topic.get("supporting_teachers", []), "supporting_teachers")
            if len(supporting_teachers) != len(set(supporting_teachers)):
                raise ValueError(f"{topic_id}: duplicate supporting teacher")
            for support_teacher in supporting_teachers:
                if (support_teacher not in known_teachers or support_teacher == subject or
                        support_teacher not in supporting_subjects):
                    raise ValueError(f"{topic_id}: invalid supporting teacher")

            routes = topic.get("skill_routes")
            if not isinstance(routes, list) or not routes:
                raise ValueError(f"{topic_id}.skill_routes must be a nonempty list")
            for route in routes:
                _validate_skill_route(route)
            concepts = strings(topic.get("concepts"), "concepts", required=True)
            for concept in concepts:
                if not re.fullmatch(r"[a-z][a-z0-9-]*\.[a-z0-9]+(?:[.-][a-z0-9]+)*", concept):
                    raise ValueError(f"Invalid concept ID: {concept}")
                if concept in concept_ids:
                    raise ValueError(f"Duplicate concept ID: {concept}")
                concept_ids.add(concept)

            prerequisites = strings(topic.get("prerequisites"), "prerequisites")
            if any(prerequisite not in seen_topics for prerequisite in prerequisites):
                raise ValueError(f"{topic_id}: prerequisites must refer to earlier topics")
            representations = topic.get("representations")
            if representations is not None:
                if not isinstance(representations, list) or not representations:
                    raise ValueError(f"{topic_id}: representations must be a nonempty list")
                representation_ids = set()
                for representation in representations:
                    if not isinstance(representation, dict):
                        raise ValueError(f"{topic_id}: each representation must be an object")
                    if representation.get("id") is None:
                        raise ValueError(f"{topic_id}: representation requires an id")
                    representation_id = slug(representation.get("id"))
                    if representation_id in representation_ids:
                        raise ValueError(f"{topic_id}: duplicate representation id")
                    representation_ids.add(representation_id)
                    kind = representation.get("kind")
                    if kind not in REPRESENTATION_KINDS:
                        raise ValueError(f"{topic_id}: unknown representation kind {kind!r}")
                    if not representation.get("purpose"):
                        raise ValueError(f"{topic_id}: representation purpose must be nonempty text")
                    concept = representation.get("concept")
                    if concept is not None:
                        if not isinstance(concept, str) or not concept.strip():
                            raise ValueError(f"{topic_id}: representation concept must be nonempty text")
                        if concept not in concepts:
                            raise ValueError(f"{topic_id}: representation concept is not in topic concepts")
            minutes = topic.get("minutes")
            if type(minutes) is not int or minutes <= 0:
                raise ValueError(f"{topic_id}: minutes must be a positive integer")

            selected = strings(topic.get("resource_ids"), "resource_ids")
            if any(resource_id not in data["sources"] for resource_id in selected):
                raise ValueError(f"{topic_id}: resource ID has no source record")
            if "feedback" in topic and topic["feedback"] is not None:
                feedback = topic["feedback"]
                if not isinstance(feedback, dict):
                    raise ValueError(f"{topic_id}: feedback must be an object")
                results = feedback.get("source_results", {})
                if not isinstance(results, dict):
                    raise ValueError(f"{topic_id}: feedback.source_results must be an object")
                for key, value in results.items():
                    slug(key)
                    if key not in selected:
                        raise ValueError(f"{topic_id}: feedback source must be in resource_ids")
                    if value not in ("worked", "did-not-work", "too-hard", "no-access"):
                        raise ValueError(f"{topic_id}: unknown source result")
                if "direction" in feedback and feedback["direction"] not in ("keep", "swap", "split"):
                    raise ValueError(f"{topic_id}: unknown direction")
                if "note" in feedback and feedback["note"] is not None:
                    nonempty(feedback["note"], f"{topic_id}.feedback.note")
                if "repeats" in feedback:
                    repeats = feedback["repeats"]
                    if type(repeats) is not int or repeats < 0:
                        raise ValueError(f"{topic_id}: feedback.repeats must be zero or more")
            for key, label, seen in (
                ("exercise_ids", "exercise_ids", exercise_ids),
                ("lesson_ids", "lesson_ids", lesson_ids),
            ):
                values = strings(topic.get(key), label)
                for value in values:
                    slug(value)
                    if value in seen:
                        raise ValueError(f"Duplicate {label[:-4]} ID: {value}")
                    seen.add(value)
            seen_topics.add(topic_id)

    current = data.get("current")
    if not isinstance(current, dict):
        raise ValueError("current must be an object")
    current_chapter = current.get("chapter_id")
    current_topic = current.get("topic_id")
    nonempty(current_chapter, "current.chapter_id")
    nonempty(current_topic, "current.topic_id")
    nonempty(current.get("next_step"), "current.next_step")
    current_topics = [topic for topic in course_topics(data) if topic["state"] == "current"]
    if len(current_topics) != 1:
        raise ValueError("Course must have exactly one current topic")
    chapter_by_id = {chapter["id"]: chapter for chapter in chapters}
    topic_by_id = {topic["id"]: topic for topic in course_topics(data)}
    if current_chapter not in chapter_by_id:
        raise ValueError("current.chapter_id must refer to a chapter")
    if chapter_by_id[current_chapter]["state"] != "current":
        raise ValueError("current.chapter_id must identify a current chapter")
    if current_topic not in topic_by_id:
        raise ValueError("current.topic_id must refer to a topic")
    if current_topic not in {topic["id"] for topic in chapter_by_id[current_chapter]["topics"]}:
        raise ValueError("current chapter and topic do not match")
    if topic_by_id[current_topic]["state"] != "current":
        raise ValueError("current.topic_id must identify a current topic")
    return data


def _validate_v1(data):
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("Course requires schema_version 1 or 2")
    slug(data.get("id"))
    for key in ("title", "goal"):
        nonempty(data.get(key), key)
    revision = data.get("revision")
    if type(revision) is not int or revision < 1:
        raise ValueError("revision must be a positive integer")
    strings(data.get("assumptions"), "assumptions")
    modules = data.get("modules")
    if not isinstance(modules, list) or not modules:
        raise ValueError("modules must be a nonempty list")
    seen = set()
    known_resources = {resource["id"] for resource in resources()}
    known_teachers = _known_teachers()
    known_subjects = _known_subjects()
    for module in modules:
        if not isinstance(module, dict):
            raise ValueError("Each module must be an object")
        id_ = slug(module.get("id"))
        if id_ in seen:
            raise ValueError(f"Duplicate module: {id_}")
        for key in ("title", "outcome"):
            nonempty(module.get(key), f"{id_}.{key}")
        subject = module.get("subject")
        if subject not in known_subjects or module.get("teacher") not in known_teachers or module.get("teacher") != subject:
            raise ValueError(f"{id_}: lead teacher must match a supplied subject")
        support = strings(module.get("supporting_teachers"), "supporting_teachers")
        if any(t not in known_teachers or t == subject for t in support) or len(support) != len(set(support)):
            raise ValueError(f"{id_}: invalid or duplicate supporting teacher")
        strings(module.get("concepts"), "concepts", required=True)
        for concept in module["concepts"]:
            if not re.fullmatch(r"[a-z][a-z0-9-]*\.[a-z0-9]+(?:[.-][a-z0-9]+)*", concept):
                raise ValueError(f"Invalid concept ID: {concept}")
        topic_titles = module.get("topic_titles", {})
        if not isinstance(topic_titles, dict) or any(k not in module["concepts"] for k in topic_titles):
            raise ValueError(f"{id_}: topic_titles must map module concept IDs to text")
        for value in topic_titles.values():
            nonempty(value, "topic_titles value")
        prerequisites = strings(module.get("prerequisites"), "prerequisites")
        if any(prerequisite not in seen for prerequisite in prerequisites):
            raise ValueError(f"{id_}: prerequisites must refer to earlier modules; found missing, cyclic, or unordered dependency")
        minutes = module.get("minutes")
        if type(minutes) is not int or minutes <= 0:
            raise ValueError(f"{id_}: minutes must be a positive integer")
        assessment = module.get("assessment")
        if not isinstance(assessment, dict):
            raise ValueError(f"{id_}: assessment must be an object")
        nonempty(assessment.get("prompt"), "assessment.prompt")
        strings(assessment.get("success_criteria"), "success_criteria", required=True)
        selected = strings(module.get("resources"), "resources")
        if any(resource_id not in known_resources for resource_id in selected):
            raise ValueError(f"{id_}: unknown resource ID")
        sections = module.get("source_sections", {})
        if not isinstance(sections, dict) or any(key not in selected for key in sections):
            raise ValueError(f"{id_}: source_sections must map selected resource IDs to text")
        for value in sections.values():
            nonempty(value, "source_sections value")
        seen.add(id_)
    return data


def upgrade_v1_course(data):
    """Return a deterministic version-two representation of a version-one plan."""
    _validate_v1(data)
    catalog = {resource["id"]: resource for resource in resources()}
    source_sections = {}
    selected_resources = []
    chapters = []
    modules = copy.deepcopy(data["modules"])
    for index, module in enumerate(modules):
        for resource_id in module["resources"]:
            if resource_id not in selected_resources:
                selected_resources.append(resource_id)
            section = module.get("source_sections", {}).get(resource_id)
            if section and section not in source_sections.setdefault(resource_id, []):
                source_sections[resource_id].append(section)
        chapters.append({
            "id": module["id"],
            "title": module["title"],
            "state": "current" if index == 0 else "planned",
            "topics": [{
                "id": module["id"],
                "title": module["title"],
                "state": "current" if index == 0 else "planned",
                "outcome": module["outcome"],
                "subject": module["subject"],
                "teacher": module["teacher"],
                "supporting_subjects": list(module["supporting_teachers"]),
                "supporting_teachers": list(module["supporting_teachers"]),
                "skill_routes": [
                    "skills/subject/SKILL.md",
                    f"skills/subject/subjects/{module['subject']}.md",
                ],
                "concepts": list(module["concepts"]),
                "prerequisites": list(module["prerequisites"]),
                "minutes": module["minutes"],
                "resource_ids": list(module["resources"]),
                "exercise_ids": [],
                "lesson_ids": [],
                "assessment": copy.deepcopy(module["assessment"]),
            }],
        })

    sources = {}
    for resource_id in selected_resources:
        item = catalog[resource_id]
        sources[resource_id] = {
            "title": item["title"],
            "url": item["url"],
            "type": item.get("format", "reference"),
            "checked_on": item.get("checked", "unknown"),
            "sections": source_sections.get(resource_id, []),
            "verification_notes": item.get("verification", "Catalog entry checked."),
        }
    first = chapters[0]["topics"][0]
    upgraded = copy.deepcopy(data)
    upgraded.update({
        "schema_version": COURSE_SCHEMA_VERSION,
        "revision_notes": [{
            "revision": data["revision"],
            "date": "1970-01-01",
            "reason": "Original revision date unavailable; deterministically upgraded from schema version 1.",
        }],
        "starting_evidence": [],
        "sources": sources,
        "current": {
            "chapter_id": chapters[0]["id"],
            "topic_id": first["id"],
            "next_step": first["outcome"],
        },
        "chapters": chapters,
    })
    return _validate_v2(upgraded)


def validate_course(data):
    if isinstance(data, dict) and data.get("schema_version") == 1:
        return upgrade_v1_course(data)
    return _validate_v2(data)
