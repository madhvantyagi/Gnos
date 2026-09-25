"""Render GNOS's daily GitHub star history as a README-friendly SVG."""

import json
import math
import os
import re
from datetime import date, datetime, timedelta, timezone
from html import escape
from pathlib import Path
from urllib.request import Request, urlopen


API_VERSION = "2026-03-10"
REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "madhvantyagi/Gnos")
SVG_NS = "http://www.w3.org/2000/svg"
WIDTH, HEIGHT = 960, 390
LEFT, RIGHT, TOP, BOTTOM = 70, 42, 96, 66

THEMES = {
    "light": {"text": "#24292f", "muted": "#57606a", "grid": "#d8dee4",
              "line": "#1a7f37", "area": "#2da44e"},
}


def fetch_history(repository=REPOSITORY, token=None):
    """Read every week; GitHub returns newest weeks first, 30 per page."""
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("repository must be owner/name")

    headers = {"Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": API_VERSION,
               "User-Agent": "gnos-star-history-chart"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    weeks = []
    for page in range(1, 101):
        url = (f"https://api.github.com/repos/{repository}/stargazers/history"
               f"?per_page=30&page={page}")
        with urlopen(Request(url, headers=headers), timeout=30) as response:
            batch = json.load(response)
        if not isinstance(batch, list):
            raise ValueError("GitHub returned an unexpected star-history response")
        weeks.extend(batch)
        if len(batch) < 30:
            return weeks
    raise ValueError("GitHub star history exceeded the API's 100-page limit")


def daily_series(history, as_of):
    """Cumulative recorded stars, starting one day before the first star."""
    additions = {}
    for week in history:
        days = week["days"]
        if len(days) != 7 or any(not isinstance(n, int) or n < 0 for n in days):
            raise ValueError("GitHub returned invalid daily star counts")
        if sum(days) != week["total"]:
            raise ValueError("GitHub's daily counts do not match the weekly total")
        first_day = datetime.fromtimestamp(week["week"], timezone.utc).date()
        for offset, count in enumerate(days):
            day = first_day + timedelta(days=offset)
            if day in additions:
                raise ValueError("GitHub returned overlapping star-history weeks")
            if day <= as_of:
                additions[day] = count

    active_days = [day for day, count in additions.items() if count > 0]
    if not active_days:
        return [(as_of, 0)]

    start = min(active_days) - timedelta(days=1)
    total = 0
    series = [(start, 0)]
    day = start + timedelta(days=1)
    while day <= as_of:
        total += additions.get(day, 0)
        series.append((day, total))
        day += timedelta(days=1)
    return series


def nice_step(maximum):
    if maximum <= 0:
        return 1
    rough = maximum / 4
    scale = 10 ** math.floor(math.log10(rough))
    return next((unit * scale for unit in (1, 2, 5, 10)
                 if unit * scale >= rough), 10 * scale)


def label(day):
    return f"{day.strftime('%b')} {day.day}"


def render_svg(series, theme):
    if theme not in THEMES or not series:
        raise ValueError("valid theme and a nonempty series are required")

    colors = THEMES[theme]
    maximum = max(total for _, total in series)
    step = nice_step(maximum)
    ceiling = max(step, math.ceil(maximum / step) * step)
    plot_right = WIDTH - RIGHT
    plot_bottom = HEIGHT - BOTTOM
    plot_height = plot_bottom - TOP

    points = []
    for index, (_, total) in enumerate(series):
        x = LEFT + ((plot_right - LEFT) * index / max(1, len(series) - 1))
        y = plot_bottom - (plot_height * total / ceiling)
        points.append((x, y))

    path = " ".join(f"{'M' if index == 0 else 'L'}{x:.1f},{y:.1f}"
                    for index, (x, y) in enumerate(points))
    area = (f"{path} L{points[-1][0]:.1f},{plot_bottom} "
            f"L{points[0][0]:.1f},{plot_bottom} Z")
    first_star = series[1][0] if len(series) > 1 else None
    subtitle = (f"Daily recorded stars · since {label(first_star)}, {first_star.year}"
                if first_star else "No recorded stars yet")
    desc = (f"Daily recorded stars for {REPOSITORY} from {series[0][0]} "
            f"to {series[-1][0]}. Starts just before the first recorded star. "
            f"Latest recorded total: {series[-1][1]}.")

    parts = [
        f'<svg xmlns="{SVG_NS}" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc" '
        'font-family="Arial, Helvetica, sans-serif">',
        f'<title id="title">Star history for {escape(REPOSITORY)}</title>',
        f'<desc id="desc">{escape(desc)}</desc>',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#ffffff"/>',
        f'<text x="{LEFT}" y="38" fill="{colors["text"]}" '
        f'font-size="20" font-weight="700">{escape(REPOSITORY)}</text>',
        f'<text x="{LEFT}" y="62" fill="{colors["muted"]}" '
        f'font-size="13">{escape(subtitle)}</text>',
        f'<text x="{plot_right}" y="38" text-anchor="end" '
        f'fill="{colors["text"]}" font-size="19" font-weight="700">'
        f'★ {series[-1][1]} recorded stars</text>',
    ]

    tick = 0
    while tick <= ceiling:
        y = plot_bottom - plot_height * tick / ceiling
        parts.append(f'<line x1="{LEFT}" y1="{y:.1f}" x2="{plot_right}" '
                     f'y2="{y:.1f}" stroke="{colors["grid"]}" stroke-width="1"/>')
        parts.append(f'<text x="{LEFT - 12}" y="{y + 4:.1f}" text-anchor="end" '
                     f'fill="{colors["muted"]}" font-size="12">{tick:g}</text>')
        tick += step

    parts.append(f'<path d="{area}" fill="{colors["area"]}" fill-opacity="0.13"/>')
    parts.append(f'<path d="{path}" fill="none" stroke="{colors["line"]}" '
                 'stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')

    indices = (range(len(series)) if len(series) <= 5 else
               sorted({round(index * (len(series) - 1) / 4) for index in range(5)}))
    for index in indices:
        x = points[index][0]
        day = series[index][0]
        parts.append(f'<text x="{x:.1f}" y="{plot_bottom + 25}" '
                     f'text-anchor="{("start" if index == 0 else "end" if index == len(series) - 1 else "middle")}" '
                     f'fill="{colors["muted"]}" font-size="12">{escape(label(day))}</text>')

    marker_indices = range(len(series)) if len(series) <= 14 else [len(series) - 1]
    for index in marker_indices:
        x, y = points[index]
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" '
                     f'fill="{colors["line"]}"><title>'
                     f'{escape(label(series[index][0]))}: {series[index][1]} stars'
                     '</title></circle>')

    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def main():
    history = fetch_history(token=os.environ.get("GITHUB_TOKEN"))
    series = daily_series(history, datetime.now(timezone.utc).date())
    assets = Path(__file__).resolve().parents[2] / "assets"
    for theme in THEMES:
        (assets / f"star-history-{theme}.svg").write_text(
            render_svg(series, theme), encoding="utf-8")
    print(f"Rendered {len(series)} daily points ending at {series[-1][1]} recorded stars")


if __name__ == "__main__":
    main()
