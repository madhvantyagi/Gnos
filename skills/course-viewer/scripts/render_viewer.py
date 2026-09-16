#!/usr/bin/env python3
"""Render one learner course workspace into a single static viewer page.

Reads the validated course plan, ready lessons, and the artifact manifest,
then writes a self-contained index.html with a left sidebar (tabs and
lesson list) and a scrolling main column: lessons with videos, images,
simulations, exercises, sources, and resources. Only public projection
fields are rendered; private evaluation criteria never appear.
"""
import argparse
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "skills/course-design/scripts"))

from portal_views import build_portal_view  # noqa: E402
from course_workspace import read_plan  # noqa: E402

TEMPLATE = ROOT / "skills/course-viewer/references/example.html"
BODY_START = "<!--VIEWER_BODY_START-->"
BODY_END = "<!--VIEWER_BODY_END-->"


def esc(value):
    return html.escape(str(value), quote=True)


def artifact_src(artifact):
    location = artifact.get("location", {})
    if "path" in location:
        return "../" + location["path"]
    return location.get("url", "")


def artifact_note(artifact, workspace):
    location = artifact.get("location", {})
    if "path" not in location:
        return ""
    return "" if (workspace / Path(location["path"])).is_file() else "missing file"


def badge(state):
    css = state if state in ("current", "planned", "provisional", "retired", "out-of-scope") else "planned"
    return f'<span class="badge {css}">{esc(state)}</span>'


def media_element(artifact, group):
    src = esc(artifact_src(artifact))
    title = esc(artifact.get("title", artifact.get("id", "")))
    mime = artifact.get("mime_type", "")
    if group == "watch":
        if mime.startswith("video/"):
            return f'<video controls preload="metadata" src="{src}"></video>'
        if mime.startswith("audio/"):
            return f'<audio controls preload="metadata" src="{src}"></audio>'
    if group == "generated":
        if mime.startswith("image/"):
            return f'<img src="{src}" alt="{title}" loading="lazy">'
        if mime in ("text/html", "application/xhtml+xml"):
            return f'<iframe sandbox="allow-scripts" src="{src}" title="{title}"></iframe>'
    return None


def render_media(artifact, group, workspace):
    src = esc(artifact_src(artifact))
    title = esc(artifact.get("title", artifact.get("id", "")))
    purpose = esc(artifact.get("purpose", ""))
    mime = artifact.get("mime_type", "")
    metadata = artifact.get("metadata", {})
    bits = []
    if metadata.get("duration_seconds") is not None:
        seconds = int(metadata["duration_seconds"])
        bits.append(f"{seconds // 60}:{seconds % 60:02d}")
    if metadata.get("pages") is not None:
        bits.append(f"{metadata['pages']} pages")
    if metadata.get("captions"):
        bits.append("captions")
    if metadata.get("transcript"):
        bits.append("transcript")
    meta = esc(" · ".join(str(bit) for bit in bits))
    missing = artifact_note(artifact, workspace)

    element = media_element(artifact, group)
    if element is None:
        return (f'<div class="card"><div class="card-title">{esc(group)} · {esc(artifact.get("type", ""))}</div>'
                f'<div class="prompt">{title}</div>'
                f'<div class="meta"><a href="{src}">open</a> · {purpose}</div></div>')

    note = f'<div class="missing">{esc(missing)}</div>' if missing else ""
    meta_line = esc(artifact.get("mime_type", ""))
    if meta:
        meta_line += " · " + meta
    return (f'<div class="media">{element}'
            f'<div class="media-body">'
            f'<div class="media-title">{title} {note}</div>'
            f'<div class="media-purpose">{purpose}</div>'
            f'<div class="media-meta">{meta_line}</div></div></div>')


def render_block(block, lesson_exercises, sources):
    block_type = block.get("type", "")
    concepts = " · ".join(esc(c) for c in block.get("concepts", []))
    label = esc(block_type)
    if concepts:
        label += " · " + concepts
    header = f'<div class="block-label">{label}</div>'
    body = ""
    if block.get("text"):
        body = f"<p>{esc(block['text'])}</p>"
    if isinstance(block.get("items"), list):
        body = "<ul>" + "".join(f"<li>{esc(item)}</li>" for item in block["items"]) + "</ul>"
    if block.get("equation"):
        body = f"<pre>{esc(block['equation'])}</pre>"
    if block.get("code"):
        body = f"<pre>{esc(block['code'])}</pre>"

    if block_type == "source":
        source = sources.get(block.get("source_id", ""), {})
        sections = " · ".join(esc(s) for s in source.get("sections", []))
        link = ""
        if source.get("url"):
            link = f'<div class="meta"><a href="{esc(source["url"])}">open source</a></div>'
        body = (f'<div class="card"><div class="card-title">source · {esc(block.get("source_id", ""))}</div>'
                f'<div class="prompt">{esc(source.get("title", ""))}'
                + (f" — {sections}" if sections else "") + f"</div>{link}"
                f'<div class="meta">{esc(block.get("purpose", ""))}</div></div>')
        return f'<div class="block">{header}{body}</div>'

    if block_type == "exercise":
        exercise = lesson_exercises.get(block.get("exercise_id", ""), {})
        body = (f'<div class="card"><div class="card-title">exercise · {esc(block.get("exercise_id", ""))}</div>'
                f'<div class="prompt">{esc(exercise.get("prompt", ""))}</div>'
                f'<div class="meta">response · {esc(exercise.get("response_type", ""))}</div></div>')
        return f'<div class="block">{header}{body}</div>'

    return f'<div class="block">{header}{body}</div>'


def rep_ready(representation, lesson_id, topic_id, artifacts):
    kind = representation.get("kind")
    if kind in ("text", "exercise"):
        return True
    for artifact in artifacts:
        if artifact.get("lesson_id") != lesson_id:
            continue
        mime = artifact.get("mime_type", "")
        if kind == "manim" and artifact.get("type") in ("voice-animation", "animation", "video", "audio"):
            return True
        if kind in ("image", "diagram") and mime.startswith("image/"):
            return True
        if kind == "simulation" and mime in ("text/html", "application/xhtml+xml"):
            return True
        if kind == "pdf" and mime == "application/pdf":
            return True
    return False


def render_chips(representations, lesson_id, topic_id, artifacts):
    if not representations:
        return ""
    chips = []
    for representation in representations:
        kind = esc(representation.get("kind", ""))
        ready = rep_ready(representation, lesson_id, topic_id, artifacts)
        css = f"chip {kind}"
        if ready:
            css += " ready"
        purpose = esc(representation.get("purpose", ""))
        chips.append(f'<span class="{css}" title="{purpose}"><span class="status"></span>'
                     f'{kind}</span>')
    return '<div class="chips">' + "".join(chips) + "</div>"


def render_lesson(lesson, index, total, previous_id, next_id, artifacts, sources, workspace, topic_reps):
    topic = lesson.get("topic_id", "")
    media_groups = {"voice-animation": "watch", "animation": "watch", "video": "watch",
                    "audio": "watch", "diagram": "generated", "interactive-graph": "generated",
                    "simulation": "generated"}
    lesson_exercises = {ex["id"]: ex for ex in lesson.get("exercises", [])}
    blocks = []
    for block in lesson.get("blocks", []):
        artifact_id = block.get("artifact_id")
        if artifact_id and artifact_id in artifacts:
            group = media_groups.get(block.get("type", ""), "resources")
            blocks.append(render_media(artifacts[artifact_id], group, workspace))
            blocks.append(render_block(block, lesson_exercises, sources))
        else:
            blocks.append(render_block(block, lesson_exercises, sources))
    chips = render_chips(topic_reps.get(topic, []), lesson["id"], topic, list(artifacts.values()))
    teacher = esc(lesson.get("teacher")) if lesson.get("teacher") else "no assigned teacher"
    meta = (f'teacher · {teacher} · updated {esc(lesson.get("updated_at", ""))}'
            f' · concepts · {esc(" · ".join(lesson.get("concepts", [])))}')
    left = (f'<a href="#" class="goto" data-index="{index - 2}">← prev · {esc(previous_id)}</a>'
            if previous_id else "<span></span>")
    right = (f'<a href="#" class="goto" data-index="{index}">next · {esc(next_id)} →</a>'
             if next_id else "<span></span>")
    nav = (f'<div class="lesson-nav">{left}<span>{index:02d} / {total:02d}</span>{right}</div>'
           if previous_id or next_id else "")
    return (f'<section class="lesson" id="lesson-{index - 1}">'
            f'<h3>{esc(lesson.get("title", lesson["id"]))}</h3>'
            f'<div class="purpose">{esc(lesson.get("purpose", ""))}</div>'
            f'<div class="meta">{meta}</div>'
            + chips + "".join(blocks) + nav + "</section>")


def ordered_lessons(view, plan):
    order = {}
    for chapter_index, chapter in enumerate(plan.get("chapters", [])):
        for topic_index, topic in enumerate(chapter.get("topics", [])):
            order[(chapter["id"], topic["id"])] = (chapter_index, topic_index)
    lessons = list(view["lessons"].get("recent", [])) + list(view["lessons"].get("earlier", []))
    return sorted(lessons, key=lambda item: (
        order.get((item.get("chapter_id"), item.get("topic_id")), (10 ** 6, 10 ** 6)),
        item.get("updated_at", ""),
        item.get("id", ""),
    ))


def lesson_status(lesson, plan, current_topic):
    order = []
    for chapter in plan.get("chapters", []):
        for topic in chapter.get("topics", []):
            order.append((topic["id"], topic["state"]))
    seen_current = False
    for topic_id, state in order:
        if topic_id == current_topic:
            seen_current = True
        if topic_id == lesson.get("topic_id"):
            if state not in ("current", "planned", "provisional"):
                return "locked"
            if topic_id == current_topic:
                return "current"
            return "done" if not seen_current else "locked"
    return "locked"


def render_sidebar(plan, lessons, current_topic):
    goal = esc(plan.get("goal", ""))
    lesson_buttons = []
    for index, lesson in enumerate(lessons):
        status = lesson_status(lesson, plan, current_topic)
        num = f"{index + 1:02d}"
        title = esc(lesson.get("title", lesson["id"]))
        extra = ' class="locked"' if status == "locked" else (' class="current"' if status == "current" else "")
        lesson_buttons.append(
            f'<button data-lesson="{index}"{extra}><span class="num">{num}</span>'
            f'<span class="dot {status}"></span>{title}</button>')
    return (
        '<aside class="sidebar">'
        f'<div class="side-head"><div class="course-title">{esc(plan.get("title", plan["id"]))}</div>'
        f'<div class="course-id">course · {esc(plan["id"])} · rev {esc(plan.get("revision", ""))}</div>'
        f'<div class="goal">{goal}</div></div>'
        '<nav class="tabs" id="tabs">'
        '<button data-tab="overview" class="active">Overview</button>'
        '<button data-tab="lessons">Lessons</button>'
        '<button data-tab="exercises">Exercises</button>'
        '<button data-tab="sources">Sources</button>'
        '<button data-tab="artifacts">Artifacts</button>'
        '</nav>'
        '<div class="lesson-list" id="lesson-list"><div class="list-label">lessons</div>'
        + "".join(lesson_buttons) + "</div></aside>")


def render_contents(view, course):
    rows = []
    for chapter in view["contents"]:
        for topic in chapter.get("topics", []):
            current = topic["id"] == course["current"]["topic_id"]
            state = topic.get("state", "planned")
            sources = " · ".join(esc(r) for r in topic.get("resource_ids", []))
            progress = topic.get("progress", {})
            evidence = esc(progress.get("evidence", "not-started"))
            attempts = progress.get("attempt_count", 0)
            evidence_cell = evidence if not attempts else f"{evidence} · {attempts} tries"
            rows.append('<tr class="current-row">' if current else "<tr>")
            rows.append(
                f"<td>{esc(chapter.get('title', ''))}</td>"
                f"<td>{esc(topic.get('title', ''))}</td>"
                f"<td>{esc(topic.get('outcome', ''))}</td>"
                f"<td>{badge(state)}</td>"
                f"<td>{evidence_cell}</td>"
                f"<td>{esc(topic.get('minutes', ''))}</td>"
                f"<td>{sources}</td></tr>")
    return ("<table><tr><th>chapter</th><th>topic</th><th>outcome</th><th>state</th>"
            "<th>evidence</th><th>min</th><th>sources</th></tr>" + "".join(rows) + "</table>")


def render_sources(course):
    rows = []
    for source_id, source in course["sources"].items():
        title = esc(source.get("title", source_id))
        if source.get("url"):
            title = f'<a href="{esc(source["url"])}">{title}</a>'
        rows.append(
            f"<tr><td>{esc(source_id)}</td><td>{title}</td>"
            f"<td>{esc(' · '.join(source.get('sections', [])))}</td>"
            f"<td>{esc(source.get('checked_on', ''))}</td></tr>")
    return ("<table><tr><th>id</th><th>title</th><th>sections</th><th>checked</th></tr>"
            + "".join(rows) + "</table>")


def render_artifacts(view, workspace):
    groups = (("watch", "Watch"), ("generated", "Generated"), ("resources", "Resources"))
    parts = []
    for group, label in groups:
        grouped = view["artifacts"].get(group, {})
        items = list(grouped.get("recent", [])) + list(grouped.get("earlier", []))
        if not items:
            continue
        cards = []
        for artifact in items:
            src = esc(artifact_src(artifact))
            missing = artifact_note(artifact, workspace)
            note = f'<div class="meta">· {esc(missing)}</div>' if missing else ""
            action = "open"
            mime = artifact.get("mime_type", "")
            if group == "watch":
                action = "watch"
            elif mime.startswith("text/html"):
                action = "run"
            cards.append(
                f'<div class="item"><div class="kind">{esc(group)} · {esc(artifact.get("type", ""))}</div>'
                f'<div class="t">{esc(artifact.get("title", ""))}</div>'
                f'<div class="p">{esc(artifact.get("purpose", ""))}</div>'
                f'{note}<a href="{src}">{action}</a></div>')
        parts.append(f'<h2 class="sec">{label}</h2><div class="gallery">' + "".join(cards) + "</div>")
    return "".join(parts) or '<p>No ready artifacts yet.</p>'


def render_exercises(view):
    cards = []
    for exercise in view["exercises"]:
        options = exercise.get("evaluation", {}).get("options")
        options_line = ""
        if isinstance(options, list):
            options_line = "<ul>" + "".join(f"<li>{esc(o)}</li>" for o in options) + "</ul>"
        attempts = exercise.get("attempts", [])
        attempt_line = ""
        if attempts:
            attempt_line = " · ".join(
                f"{esc(a.get('status', ''))} {esc(str(a.get('submitted_at', ''))[:10])}"
                for a in attempts)
        cards.append(
            f'<div class="card"><div class="card-title">{esc(exercise["id"])} · lesson {esc(exercise.get("lesson_id", ""))}</div>'
            f'<div class="prompt">{esc(exercise.get("prompt", ""))}</div>{options_line}'
            f'<div class="meta">{esc(exercise.get("response_type", ""))}'
            + (f" · {len(attempts)} attempt{'s' if len(attempts) != 1 else ''} · {attempt_line}"
               if attempts else "")
            + "</div></div>")
    return "".join(cards)


def render_questions(view):
    questions = list(view["questions"].get("recent", [])) + list(view["questions"].get("earlier", []))
    cards = []
    for question in questions:
        cards.append(
            f'<div class="card"><div class="card-title">question · {esc(question.get("id", ""))}</div>'
            f'<div class="prompt">{esc(question.get("text", ""))}</div>'
            f'<div class="meta">status · {esc(question.get("status", ""))}</div></div>')
    return cards


def render_body(view, plan, workspace):
    course = view["course"]
    current = course["current"]
    topic_reps = {}
    for chapter in plan.get("chapters", []):
        for topic in chapter.get("topics", []):
            topic_reps[topic["id"]] = topic.get("representations", [])

    artifacts = {}
    for group in ("watch", "generated", "resources"):
        for artifact in list(view["artifacts"].get(group, {}).get("recent", [])) + \
                list(view["artifacts"].get(group, {}).get("earlier", [])):
            artifacts[artifact["id"]] = artifact

    lessons = ordered_lessons(view, plan)
    lesson_html = ""
    for index, lesson in enumerate(lessons, start=1):
        previous_id = lessons[index - 2]["id"] if index > 1 else None
        next_id = lessons[index]["id"] if index < len(lessons) else None
        lesson_html += render_lesson(lesson, index, len(lessons), previous_id, next_id,
                                     artifacts, course["sources"], workspace, topic_reps)

    assumptions = plan.get("assumptions", [])
    assumptions_html = ""
    if assumptions:
        assumptions_html = ('<h2 class="sec">Assumptions</h2><div class="card"><div class="prompt">'
                            + "".join(f"· {esc(a)}<br>" for a in assumptions) + "</div></div>")
    vision = plan.get("vision")
    vision_line = f'<p class="page-vision">Vision: {esc(vision)}</p>' if vision else ""

    questions_html = ""
    question_cards = render_questions(view)
    if question_cards:
        questions_html = '<h2 class="sec">Questions</h2>' + "".join(question_cards)

    parts = [
        render_sidebar(plan, lessons, current["topic_id"]),
        '<main class="main">',
        '<header class="main-head"><div class="inner">',
        f'<div class="head-title"><span>course /</span> {esc(plan.get("title", plan["id"]))}</div>',
        '<nav><a href="#" id="prev-link" data-disabled="1">← prev</a>'
        '<a href="#" id="next-link">next →</a></nav>',
        '</div></header>',
        '<div class="content">',
        f'<section class="tab active" id="tab-overview">'
        f'<h1 class="page-title">{esc(plan.get("title", plan["id"]))}</h1>'
        f'<p class="page-goal">Goal: {esc(course.get("goal", ""))}</p>'
        f'{vision_line}'
        f'<div class="page-meta">current · {esc(current.get("chapter_id", ""))} · {esc(current.get("topic_id", ""))}'
        f' · next: {esc(current.get("next_step", ""))}</div>'
        f'<h2 class="sec">Contents</h2>{render_contents(view, course)}'
        f'{assumptions_html}</section>',
        f'<section class="tab" id="tab-lessons">'
        + (lesson_html or "<p>No ready lessons yet. Publish a lesson, then render again.</p>")
        + "</section>",
        f'<section class="tab" id="tab-exercises"><h2 class="sec">Exercises</h2>'
        + (render_exercises(view) or "<p>No exercises yet.</p>") + questions_html + "</section>",
        f'<section class="tab" id="tab-sources"><h2 class="sec">Sources</h2>{render_sources(course)}</section>',
        f'<section class="tab" id="tab-artifacts">{render_artifacts(view, workspace)}</section>',
        '<div class="footer">rendered by course-viewer · private evaluation criteria never appear here</div>',
        '</div></main>',
    ]
    return "\n".join(parts)


def _empty_view(plan):
    from portal_views import build_contents, public_course
    return {
        "course": public_course(plan),
        "contents": build_contents(plan, {}),
        "lessons": {"recent": [], "earlier": []},
        "artifacts": {group: {"recent": [], "earlier": []}
                      for group in ("watch", "generated", "resources")},
        "exercises": [],
        "questions": {"recent": [], "earlier": []},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path,
                        help="learner course folder: <learner>/courses/<course-id>")
    parser.add_argument("--summary", type=Path,
                        help="optional learner summary JSON for progress columns")
    parser.add_argument("--out", type=Path,
                        help="output HTML path (default: <workspace>/portal/index.html)")
    args = parser.parse_args()
    workspace = args.workspace
    try:
        plan = read_plan(workspace)
        summary = {}
        if args.summary:
            summary = json.loads(args.summary.read_text())
        try:
            view = build_portal_view(workspace, summary)
        except FileNotFoundError:
            view = _empty_view(plan)
        body = render_body(view, plan, workspace)
        template = TEMPLATE.read_text()
        if BODY_START not in template or BODY_END not in template:
            parser.exit(1, f"Template {TEMPLATE} is missing its content markers\n")
        head, remainder = template.split(BODY_START, 1)
        _, tail = remainder.split(BODY_END, 1)
        page = head + body + tail
        out = args.out or (workspace / "portal" / "index.html")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Render failed: {exc}\n")
    print(f"Rendered {plan['title']} -> {out}")


if __name__ == "__main__":
    main()
