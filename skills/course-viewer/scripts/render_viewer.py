#!/usr/bin/env python3
"""Render one learner course workspace into a single static viewer page.

Reads the validated course plan, ready lessons, and the artifact manifest,
then writes a self-contained index.html that shows videos, images,
simulations, sources, exercises, and resources. Only public projection
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
    target = workspace / Path(location["path"])
    if not target.is_file():
        return "missing file"
    return ""


def badge(state):
    label = esc(state)
    css = state if state in ("current", "planned", "provisional", "retired", "out-of-scope") else "planned"
    return f'<span class="badge {css}">{label}</span>'


def render_media(artifact, group, workspace):
    src = esc(artifact_src(artifact))
    title = esc(artifact.get("title", artifact.get("id", "")))
    purpose = esc(artifact.get("purpose", ""))
    mime = artifact.get("mime_type", "")
    metadata = artifact.get("metadata", {})
    meta_bits = []
    if metadata.get("duration_seconds") is not None:
        seconds = int(metadata["duration_seconds"])
        meta_bits.append(f"{seconds // 60}:{seconds % 60:02d}")
    for key, label in (("pages", "pages"), ("width", "w"), ("height", "h")):
        if metadata.get(key) is not None:
            meta_bits.append(f"{label} {metadata[key]}")
    if metadata.get("captions"):
        meta_bits.append("captions")
    if metadata.get("transcript"):
        meta_bits.append("transcript")
    meta = esc(" · ".join(str(bit) for bit in meta_bits))

    missing = artifact_note(artifact, workspace)
    element = None
    if group == "watch":
        if mime.startswith("video/"):
            element = f'<video controls preload="metadata" src="{src}"></video>'
        elif mime.startswith("audio/"):
            element = f'<audio controls preload="metadata" src="{src}"></audio>'
    elif group == "generated":
        if mime.startswith("image/"):
            element = f'<img src="{src}" alt="{title}" loading="lazy">'
        elif mime in ("text/html", "application/xhtml+xml"):
            element = f'<iframe sandbox="allow-scripts allow-same-origin" src="{src}" title="{title}"></iframe>'

    if element is None:
        return (f'<div class="card"><div class="card-title">{group} · {esc(artifact.get("type", ""))}</div>'
                f'<div class="prompt">{title}</div>'
                f'<div class="meta"><a href="{src}">open</a> · {purpose}</div></div>')

    note = f'<div class="missing">{esc(missing)}</div>' if missing else ""
    return (f'<div class="media">{element}'
            f'<div class="media-title">{title} {note}</div>'
            f'<div class="media-purpose">{purpose}</div>'
            f'<div class="media-meta">{esc(artifact.get("mime_type", ""))}'
            + (f" · {meta}" if meta else "") + "</div></div>")


def render_block(block, exercises, sources):
    block_type = block.get("type", "")
    concepts = " · ".join(esc(c) for c in block.get("concepts", []))
    header = f'<div class="block-purpose">{esc(block_type)}'
    if concepts:
        header += f" · {concepts}"
    header += "</div>"
    body = ""
    text = block.get("text")
    if text:
        body = f"<p>{esc(text)}</p>"
    items = block.get("items")
    if isinstance(items, list):
        body = "<ul>" + "".join(f"<li>{esc(item)}</li>" for item in items) + "</ul>"
    equation = block.get("equation")
    if equation:
        body = f"<pre>{esc(equation)}</pre>"
    code = block.get("code")
    if code:
        body = f"<pre>{esc(code)}</pre>"
    caption = block.get("caption")
    if caption:
        body += f'<div class="caption">{esc(caption)}</div>'

    if block_type == "source":
        source = sources.get(block.get("source_id", ""), {})
        sections = " · ".join(esc(s) for s in source.get("sections", []))
        link = ""
        if source.get("url"):
            link = f'<div class="meta"><a href="{esc(source["url"])}">open source</a></div>'
        body = (f'<div class="card src"><div class="card-title">source · {esc(block.get("source_id", ""))}</div>'
                f'<div class="prompt">{esc(source.get("title", ""))}'
                + (f" — {sections}" if sections else "") + "</div>"
                f'{link}<div class="meta">{esc(block.get("purpose", ""))}</div></div>')
        return f'<div class="block">{header}{body}</div>'

    if block_type == "exercise":
        exercise = exercises.get(block.get("exercise_id", ""), {})
        return (f'<div class="block">{header}'
                f'<div class="card ex"><div class="card-title">exercise · {esc(block.get("exercise_id", ""))}</div>'
                f'<div class="prompt">{esc(exercise.get("prompt", ""))}</div>'
                f'<div class="meta">response · {esc(exercise.get("response_type", ""))}</div></div></div>')

    return f'<div class="block">{header}{body}</div>'


def render_lesson(lesson, index, total, previous_id, next_id, artifacts, sources, exercises, workspace):
    media_groups = {"voice-animation": "watch", "animation": "watch", "video": "watch",
                    "audio": "watch", "diagram": "generated", "interactive-graph": "generated",
                    "simulation": "generated"}
    blocks = []
    for block in lesson.get("blocks", []):
        artifact_id = block.get("artifact_id")
        if artifact_id and artifact_id in artifacts:
            group = media_groups.get(block.get("type", ""), "resources")
            kind = "watch" if group == "watch" else "generated" if group == "generated" else "resources"
            blocks.append(render_media(artifacts[artifact_id], kind, workspace))
            blocks.append(render_block(block, exercises, sources))
        else:
            blocks.append(render_block(block, exercises, sources))
    nav = ""
    if previous_id or next_id:
        left = f'<a href="#lesson-{esc(previous_id)}">← prev</a>' if previous_id else "<span></span>"
        right = f'<a href="#lesson-{esc(next_id)}">next →</a>' if next_id else "<span></span>"
        nav = f'<div class="lesson-nav">{left}<span>{index} / {total}</span>{right}</div>'
    concepts = " · ".join(esc(c) for c in lesson.get("concepts", []))
    teacher = lesson.get("teacher")
    teacher_line = esc(teacher) if teacher else "no assigned teacher"
    return (f'<section class="lesson" id="lesson-{esc(lesson["id"])}">'
            f'<span class="lesson-no">LESSON {index:02d}</span>'
            f'<h3>{esc(lesson.get("title", lesson["id"]))}</h3>'
            f'<div class="purpose">{esc(lesson.get("purpose", ""))}</div>'
            f'<div class="concepts">concepts · {concepts}</div>'
            f'<div class="teacher">teacher · {teacher_line} · updated {esc(lesson.get("updated_at", ""))}</div>'
            + "".join(blocks) + nav + "</section>")


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


def render_contents(view, course):
    rows = []
    for chapter in view["contents"]:
        for topic in chapter.get("topics", []):
            current = topic["id"] == course["current"]["topic_id"]
            sources = " · ".join(esc(r) for r in topic.get("resource_ids", []))
            rows.append(
                f'<tr class="current-row">' if current else "<tr>")
            rows.append(
                f"<td>{esc(chapter.get('title', ''))}</td>"
                f"<td>{esc(topic.get('title', ''))}</td>"
                f"<td>{esc(topic.get('outcome', ''))}</td>"
                f"<td>{badge(topic.get('state', 'planned'))}</td>"
                f"<td>{esc(topic.get('minutes', ''))}</td>"
                f"<td>{sources}</td></tr>")
    return ("<table><tr><th>chapter</th><th>topic</th><th>outcome</th><th>state</th>"
            "<th>min</th><th>sources</th></tr>" + "".join(rows) + "</table>")


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
    groups = (("watch", "watch · video / animation / audio"),
              ("generated", "generated · diagram / image / simulation"),
              ("resources", "resources · pdf / document / file"))
    cards = []
    for group, _label in groups:
        grouped = view["artifacts"].get(group, {})
        for artifact in list(grouped.get("recent", [])) + list(grouped.get("earlier", [])):
            src = esc(artifact_src(artifact))
            kind = "watch" if group == "watch" else "gen" if group == "generated" else "res"
            missing = artifact_note(artifact, workspace)
            note = f'<div class="meta">· {esc(missing)}</div>' if missing else ""
            action = "open" if group == "resources" else (
                "run" if artifact.get("mime_type", "").startswith("text/html") else
                "watch" if group == "watch" else "open")
            cards.append(
                f'<div class="item"><div class="kind {kind}">{esc(group)} · {esc(artifact.get("type", ""))}</div>'
                f'<div class="t">{esc(artifact.get("title", ""))}</div>'
                f'<div class="p">{esc(artifact.get("purpose", ""))}</div>'
                f'{note}<a class="open" href="{src}">{action}</a></div>')
    return '<div class="gallery">' + "".join(cards) + "</div>"


def render_exercises(view):
    cards = []
    for exercise in view["exercises"]:
        evaluation = exercise.get("evaluation", {})
        options = evaluation.get("options")
        options_line = ""
        if isinstance(options, list):
            options_line = "<ul>" + "".join(f"<li>{esc(o)}</li>" for o in options) + "</ul>"
        attempts = exercise.get("attempts", [])
        attempt_lines = ""
        if attempts:
            attempt_lines = '<div class="meta">'
            attempt_lines += " · ".join(
                f"{esc(a.get('status', ''))} {esc(a.get('submitted_at', '')[:10])}"
                for a in attempts)
            attempt_lines += "</div>"
        cards.append(
            f'<div class="card ex"><div class="card-title">{esc(exercise["id"])} · lesson {esc(exercise.get("lesson_id", ""))}</div>'
            f'<div class="prompt">{esc(exercise.get("prompt", ""))}</div>{options_line}'
            f'<div class="meta">{esc(exercise.get("response_type", ""))}'
            + (f" · {len(attempts)} attempt{'s' if len(attempts) != 1 else ''}" if attempts else "")
            + f"</div>{attempt_lines}</div>")
    return "".join(cards)


def render_body(view, plan, workspace):
    course = view["course"]
    current = course["current"]
    assumptions = plan.get("assumptions", [])
    assumptions_line = ""
    if assumptions:
        assumptions_line = ('<div class="card src"><div class="card-title">assumptions</div>'
                            + "".join(f"<div class=\"prompt\">· {esc(a)}</div>" for a in assumptions)
                            + "</div>")
    vision = plan.get("vision")
    vision_line = f'<p class="vision">Vision: {esc(vision)}</p>' if vision else ""

    sources = course["sources"]
    lessons = ordered_lessons(view, plan)
    artifacts = {}
    for group in ("watch", "generated", "resources"):
        for artifact in list(view["artifacts"].get(group, {}).get("recent", [])) + \
                list(view["artifacts"].get(group, {}).get("earlier", [])):
            artifacts[artifact["id"]] = artifact
    exercises = {ex["id"]: ex for ex in view["exercises"]}

    lesson_html = ""
    for index, lesson in enumerate(lessons, start=1):
        previous_id = lessons[index - 2]["id"] if index > 1 else None
        next_id = lessons[index]["id"] if index < len(lessons) else None
        lesson_exercises = {ex["id"]: ex for ex in lesson.get("exercises", [])}
        lesson_html += render_lesson(lesson, index, len(lessons), previous_id, next_id,
                                     artifacts, sources, lesson_exercises, workspace)

    questions = list(view["questions"].get("recent", [])) + list(view["questions"].get("earlier", []))
    questions_html = ""
    if questions:
        cards = []
        for question in questions:
            status = esc(question.get("status", ""))
            cards.append(
                f'<div class="card ex"><div class="card-title">question · {esc(question.get("id", ""))}</div>'
                f'<div class="prompt">{esc(question.get("text", ""))}</div>'
                f'<div class="meta">status · {status}</div></div>')
        questions_html = '<h2 class="section"><span class="no">06</span> Questions</h2>' + "".join(cards)

    parts = [
        '<header class="masthead">',
        f'<div class="course-id">course · {esc(course["id"])} · revision {esc(course.get("revision", ""))}</div>',
        f'<h1>{esc(course.get("title", course["id"]))}</h1>',
        f'<p class="goal">Goal: {esc(course.get("goal", ""))}</p>',
        vision_line,
        f'<div class="meta">current · {esc(current.get("chapter_id", ""))} · {esc(current.get("topic_id", ""))}'
        f' · next: {esc(current.get("next_step", ""))}</div>',
        '<div class="rule"></div></header>',
        '<div class="legend">',
        '<span class="watch"><span class="dot"></span>watch · video / animation / audio</span>',
        '<span class="gen"><span class="dot"></span>generated · diagram / image / simulation</span>',
        '<span class="res"><span class="dot"></span>resources · pdf / document / file</span>',
        '<span class="ex"><span class="dot"></span>exercises</span>',
        '<span class="now"><span class="dot"></span>current topic</span>',
        '</div>',
        '<h2 class="section"><span class="no">01</span> Contents</h2>',
        render_contents(view, course),
        assumptions_line,
        '<h2 class="section"><span class="no">02</span> Sources</h2>',
        render_sources(course),
        '<h2 class="section"><span class="no">03</span> Lessons</h2>',
        lesson_html or '<p>No ready lessons yet. Publish a lesson, then render again.</p>',
        '<h2 class="section"><span class="no">04</span> Artifacts</h2>',
        render_artifacts(view, workspace) or '<p>No ready artifacts yet.</p>',
        '<h2 class="section"><span class="no">05</span> Exercises</h2>',
        render_exercises(view) or '<p>No exercises yet.</p>',
        questions_html,
        '<div class="footer">rendered by course-viewer · data read from course.json, lessons, '
        'and the artifact manifest · private evaluation criteria never appear here</div>',
    ]
    return "\n".join(parts)


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
        view = build_portal_view(workspace, summary)
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
