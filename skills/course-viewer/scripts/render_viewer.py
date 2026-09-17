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
LOGO_PNG = ROOT / "skills/course-viewer/references/gnos-logo.png"
BODY_START = "<!--VIEWER_BODY_START-->"
BODY_END = "<!--VIEWER_BODY_END-->"

_LOGO_URI = None


def logo_img():
    """Chrome-pixel GNOS wordmark as a data-URI <img>; text fallback."""
    global _LOGO_URI
    if _LOGO_URI is None:
        try:
            import base64
            raw = LOGO_PNG.read_bytes()
            _LOGO_URI = "data:image/png;base64," + base64.b64encode(raw).decode()
        except OSError:
            _LOGO_URI = ""
    if _LOGO_URI:
        return f'<img src="{_LOGO_URI}" alt="GNOS" width="320" height="107">'
    return "GNOS"


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


def rep_ready(representation, lesson, artifacts):
    kind = representation.get("kind")
    blocks = [block for block in lesson.get("blocks", [])
              if block.get("representation_id") == representation.get("id")]
    if not blocks:
        return False
    if kind in ("text", "exercise"):
        return True
    artifact_ids = {block.get("artifact_id") for block in blocks if block.get("artifact_id")}
    for artifact in artifacts:
        if artifact.get("lesson_id") != lesson.get("id") or artifact.get("id") not in artifact_ids:
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


def render_chips(representations, lesson, artifacts):
    if not representations:
        return ""
    chips = []
    for representation in representations:
        kind = esc(representation.get("kind", ""))
        ready = rep_ready(representation, lesson, artifacts)
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
    chips = render_chips(topic_reps.get(topic, []), lesson, list(artifacts.values()))
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


def _pretty_subject(slug):
    mapping = {
        "math": "Mathematics", "mathematics": "Mathematics",
        "statistics": "Statistics", "stat": "Statistics",
        "physics": "Physics", "history": "History",
        "biology": "Biology", "economics": "Economics",
        "computer-science": "Computer Science", "cs": "Computer Science",
        "accounting": "Accounting", "ai": "Artificial Intelligence",
        "artificial-intelligence": "Artificial Intelligence",
        "business": "Business", "psychology": "Psychology",
        "chemical-engineering": "Chemical Engineering",
        "political-science": "Political Science",
    }
    if not slug:
        return ""
    key = str(slug).strip().lower().replace("_", "-")
    if key in mapping:
        return mapping[key]
    return " ".join(w.capitalize() for w in key.split("-"))


def _pretty_evidence(evidence, attempts=0):
    pretty = str(evidence or "not-started").replace("-", " ").replace("_", " ")
    pretty = pretty[:1].upper() + pretty[1:] if pretty else "Not started"
    if attempts:
        return f"{pretty} · {attempts} tries"
    return pretty


def _topic_sources_html(topic, course):
    sources = course.get("sources", {})
    rids = topic.get("resource_ids", [])
    if not rids:
        return ("—", "—")
    bits = []
    for rid in rids:
        src = sources.get(rid, {})
        label = src.get("title") or rid
        if src.get("url"):
            bits.append(f'<a href="{esc(src["url"])}">{esc(label)}</a>')
        else:
            bits.append(esc(label))
    return (" / ".join(bits), " / ".join(rids))


def _hero_field(plan):
    if plan.get("field"):
        return esc(plan["field"])
    subjects = []
    seen = set()
    for chapter in plan.get("chapters", []):
        for topic in chapter.get("topics", []):
            subj = topic.get("subject") or ""
            pretty = _pretty_subject(subj)
            if pretty and pretty not in seen:
                seen.add(pretty)
                subjects.append(pretty)
    if not subjects:
        return "General"
    # Keep it short like "Mathematics / Statistics"
    return esc(" / ".join(subjects[:2]))


def _hero_level(plan):
    if plan.get("level"):
        return esc(plan["level"])
    return "Foundations &#8594; Advanced"


def _hero_resources(course):
    sources = course.get("sources", {})
    if not sources:
        return ""
    items = list(sources.items())[:2]
    links = []
    for sid, src in items:
        title = src.get("title") or sid
        # Shorten common titles: "MIT 18.05 ..." -> keep short id-like label
        short = sid
        # Prefer a compact human label: use title up to first "·" or first 18 chars
        label = title
        if len(label) > 28:
            label = sid
        # Prettify known ids
        pretty_ids = {
            "openstax-calculus-1": "OpenStax Calculus",
        }
        label = pretty_ids.get(sid, label)
        if src.get("url"):
            links.append(f'<a href="{esc(src["url"])}">{esc(label)}</a>')
        else:
            links.append(esc(label))
    return " &middot; ".join(links)


def _display_state(topic_id, raw_state, current_topic_id):
    if topic_id == current_topic_id or raw_state == "current":
        return ("Current", "disp-current")
    return ("Planned", "disp-planned")


def render_sidebar(plan, lessons, current_topic):
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
        '<header class="topbar">'
        '<div class="topbar-inner">'
        f'<a class="gnos-logo" href="#" aria-label="GNOS home">{logo_img()}</a>'
        '<nav class="top-tabs" aria-label="course sections">'
        '<ul id="tabs" role="tablist">'
        '<li><button data-tab="overview" class="active" role="tab" aria-selected="true">Overview</button></li>'
        '<li><button data-tab="lessons" role="tab" aria-selected="false">Lessons</button></li>'
        '<li><button data-tab="exercises" role="tab" aria-selected="false">Exercises</button></li>'
        '<li><button data-tab="sources" role="tab" aria-selected="false">Sources</button></li>'
        '<li><button data-tab="artifacts" role="tab" aria-selected="false">Artifacts</button></li>'
        '</ul></nav>'
        '<a class="all-courses" href="#">All courses &#8594;</a>'
        '</div></header>'
        # Keep lesson hooks for existing JS; hidden visually but functional.
        '<div class="lesson-list" id="lesson-list" aria-label="lessons" style="display:none">'
        + "".join(lesson_buttons) + "</div>")


def render_hero(plan, course):
    display_title = plan.get("hero_title")
    use_display_title = isinstance(display_title, str) and bool(display_title.strip())
    raw_title = display_title if use_display_title else plan.get("title", plan.get("id", "Course"))
    display_subtitle = plan.get("hero_subtitle")
    use_display_subtitle = isinstance(display_subtitle, str) and bool(display_subtitle.strip())
    raw_subtitle = (display_subtitle if use_display_subtitle
                    else course.get("goal", plan.get("goal", "")))
    title = esc(raw_title)
    subtitle = esc(raw_subtitle or "")
    title_class = "hero-title hero-title-display" if use_display_title else "hero-title"
    row_class = "hero-title-row is-display" if use_display_title else "hero-title-row"
    hero_class = "hero hero-display" if use_display_title else "hero"
    rev = esc(plan.get("revision", ""))
    rev_html = f'<span class="hero-rev">Rev. {rev}</span>' if rev != "" else ""
    # Screenshot subtitle has no "Goal:" prefix; keep plain sentence.
    field = _hero_field(plan)
    level = _hero_level(plan)
    resources = _hero_resources(course)
    resources_row = (f'<div class="meta-row"><dt>Resources</dt><dd>{resources}</dd></div>'
                     if resources else "")
    return (
        f'<section class="{hero_class}" aria-labelledby="course-title">'
        '<div class="hero-main">'
        f'<div class="{row_class}"><h1 id="course-title" class="{title_class}">{title}</h1>{rev_html}</div>'
        + (f'<p class="hero-subtitle">{subtitle}</p>' if subtitle else "") +
        '</div>'
        '<dl class="hero-meta">'
        f'<div class="meta-row"><dt>Field</dt><dd>{field}</dd></div>'
        f'<div class="meta-row"><dt>Level</dt><dd>{level}</dd></div>'
        f'{resources_row}'
        '</dl></section>')


def render_topic_details(view, plan, topic_reps):
    course = view["course"]
    current_id = course["current"].get("topic_id", "")
    # Locate current topic + chapter position + global topic number.
    found = None
    num = 0
    for ci, chapter in enumerate(view.get("contents", []), start=1):
        for ti, topic in enumerate(chapter.get("topics", [])):
            num += 1
            if topic.get("id") == current_id:
                found = (chapter, ci, topic, num)
    if found is None:
        # Fallback to first topic so the panel never renders empty.
        for ci, chapter in enumerate(view.get("contents", []), start=1):
            topics = chapter.get("topics", [])
            if topics:
                found = (chapter, ci, topics[0], 1)
                break
    if found is None:
        return ('<aside class="topic-details" id="topic-details" aria-label="Topic details">'
                '<h2 class="td-heading">Topic details</h2>'
                '<p class="td-eyebrow">No topics yet</p></aside>')
    chapter, ci, topic, n = found
    # Topic index within chapter for eyebrow is not tracked; use global number.
    eyebrow = f"Chapter {ci:02d} &middot; Topic {n:02d}"
    title = esc(topic.get("title", topic.get("id", "")))
    outcome = esc(topic.get("outcome", "")) or "—"
    raw_state = topic.get("state", "planned")
    label, _ = _display_state(topic.get("id", ""), raw_state, current_id)
    reps = topic_reps.get(topic.get("id", ""), [])
    if reps:
        formats = " &middot; ".join(esc(str(r.get("kind", "")).capitalize()) for r in reps)
    else:
        formats = "—"
    progress = topic.get("progress", {})
    evidence_text = _pretty_evidence(progress.get("evidence", "not-started"),
                                     progress.get("attempt_count", 0))
    sources_html, _ = _topic_sources_html(topic, course)
    return (
        '<aside class="topic-details" id="topic-details" aria-label="Topic details" aria-live="polite">'
        '<h2 class="td-heading">Topic details</h2>'
        f'<p class="td-eyebrow" data-td="eyebrow">{eyebrow}</p>'
        f'<h3 class="td-title" data-td="title">{title}</h3>'
        '<dl class="td-fields">'
        f'<div class="td-field"><dt class="td-label">Outcome</dt><dd class="td-value" data-td="outcome">{outcome}</dd></div>'
        f'<div class="td-field"><dt class="td-label">State</dt><dd class="td-value td-state" data-td="state">{esc(label)}</dd></div>'
        f'<div class="td-field"><dt class="td-label">Formats</dt><dd class="td-value" data-td="formats">{formats}</dd></div>'
        f'<div class="td-field"><dt class="td-label">Evidence</dt><dd class="td-value" data-td="evidence">{evidence_text}</dd></div>'
        f'<div class="td-field"><dt class="td-label">Sources</dt><dd class="td-value td-sources" data-td="sources">{sources_html}</dd></div>'
        '</dl></aside>')


def render_contents(view, course, topic_reps):
    current_topic = course["current"].get("topic_id", "")
    parts = ['<section class="curriculum" aria-label="Curriculum">',
             '<h2 class="curriculum-title">Curriculum</h2>']
    num = 0
    for ch_index, chapter in enumerate(view.get("contents", []), start=1):
        ch_id = chapter.get("id", "")
        ch_title = chapter.get("title", "")
        parts.append(
            f'<section class="curr-chapter" data-chapter-id="{esc(ch_id)}">'
            f'<h3 class="curr-chapter-head">'
            f'<span class="curr-kicker">Chapter {ch_index:02d}</span> '
            f'<span class="curr-chapter-title">{esc(ch_title)}</span>'
            "</h3>"
            '<div class="curr-topics">'
        )
        for topic in chapter.get("topics", []):
            num += 1
            t_id = topic.get("id", "")
            t_title = topic.get("title", "")
            outcome = topic.get("outcome", "")
            raw = topic.get("state", "planned")
            label, disp = _display_state(t_id, raw, current_topic)
            selected = (t_id == current_topic)
            cls = "curr-row"
            if selected:
                cls += " is-selected"
            if raw in ("retired", "out-of-scope"):
                cls += " is-dimmed"
            aria = ' aria-current="true"' if selected else ""
            progress = topic.get("progress", {})
            evidence_text = _pretty_evidence(progress.get("evidence", "not-started"),
                                             progress.get("attempt_count", 0))
            reps = topic_reps.get(t_id, [])
            formats = " · ".join(str(r.get("kind", "")).capitalize() for r in reps)
            sources_html, _ = _topic_sources_html(topic, course)
            chips_hidden = render_chips(reps, {}, [])
            parts.append(
                f'<button type="button" class="{cls}"'
                f' data-chapter-id="{esc(ch_id)}"'
                f' data-topic-id="{esc(t_id)}"'
                f' data-state="{esc(label)}"'
                f' data-outcome="{esc(outcome)}"'
                f' data-eyebrow="Chapter {ch_index:02d} · Topic {num:02d}"'
                f' data-title="{esc(t_title)}"'
                f' data-formats="{esc(formats)}"'
                f' data-evidence="{esc(evidence_text)}"'
                f' data-sources-html="{esc(sources_html)}"'
                f' aria-label="{num:02d} {esc(t_title)} — {esc(label)}"{aria}>'
                f'<span class="curr-num" aria-hidden="true">{num:02d}</span>'
                f'<span class="curr-name">{esc(t_title)}</span>'
                f'<span class="curr-state {disp}">{esc(label)}</span>'
                f'<span class="curr-chev" aria-hidden="true">&#8250;</span>'
                f'<span class="curr-chips-hidden">{chips_hidden}</span>'
                f'<span class="sr-only">Outcome: {esc(outcome)}</span>'
                "</button>"
            )
        parts.append("</div></section>")
    parts.append("</section>")
    return "".join(parts)


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

    curriculum_html = render_contents(view, course, topic_reps)
    details_html = render_topic_details(view, plan, topic_reps)

    parts = [
        render_sidebar(plan, lessons, current["topic_id"]),
        render_hero(plan, course),
        '<section class="tab active" id="tab-overview">'
        '<div class="overview-layout">'
        f'{curriculum_html}'
        f'{details_html}'
        '</div></section>',
        f'<section class="tab" id="tab-lessons"><h2 class="sec">Lessons</h2>'
        + (lesson_html or "<p>No ready lessons yet. Publish a lesson, then render again.</p>")
        + "</section>",
        f'<section class="tab" id="tab-exercises"><h2 class="sec">Exercises</h2>'
        + (render_exercises(view) or "<p>No exercises yet.</p>") + questions_html + "</section>",
        f'<section class="tab" id="tab-sources"><h2 class="sec">Sources</h2>{render_sources(course)}</section>',
        f'<section class="tab" id="tab-artifacts">{render_artifacts(view, workspace)}</section>',
        '<div class="footer">rendered by course-viewer · private evaluation criteria never appear here</div>',
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
