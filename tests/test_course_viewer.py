"""Course viewer render tests: a fresh course still shows a page."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/course-design/scripts"))

from course_workspace import create_workspace, publish_lesson  # noqa: E402
import artifact_manifest  # noqa: E402
from tests.test_course_contract_v2 import valid_v2_course  # noqa: E402
from tests.test_lesson_contract import valid_lesson  # noqa: E402

RENDER = ROOT / "skills/course-viewer/scripts/render_viewer.py"


def plan_with_reps():
    plan = valid_v2_course()
    plan["chapters"][0]["topics"][0]["representations"] = [
        {"id": "m", "kind": "manim", "concept": "math.derivative",
         "purpose": "Show slope."},
        {"id": "m-unbuilt", "kind": "manim", "concept": "math.derivative",
         "purpose": "A second unbuilt motion."},
        {"id": "t", "kind": "text", "concept": "math.derivative",
         "purpose": "Introduce slope."},
        {"id": "t-unbuilt", "kind": "text", "concept": "math.derivative",
         "purpose": "An unbuilt explanation."},
        {"id": "s", "kind": "simulation", "concept": "math.derivative",
         "purpose": "Vary slope."},
        {"id": "e", "kind": "exercise", "concept": "math.derivative",
         "purpose": "Check prediction."},
    ]
    return plan


def lesson_with_reps():
    lesson = valid_lesson()
    for block, representation_id in zip(lesson["blocks"], ("t", "m", "s", "e")):
        block["representation_id"] = representation_id
    return lesson


class ViewerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.workspace = create_workspace(self.root, "alex", plan_with_reps())

    def render(self):
        result = subprocess.run(
            [sys.executable, str(RENDER), str(self.workspace)],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return (self.workspace / "portal" / "index.html").read_text()

    def test_zero_lesson_course_still_renders_contents_and_plan(self):
        text = self.render()
        self.assertIn("Slope as local change", text)
        self.assertIn("chip manim", text)
        self.assertIn("No ready lessons yet", text)
        self.assertNotIn("success_criteria", text)

    def test_ready_lesson_flips_chips_and_shows_media(self):
        publish_lesson(self.workspace, lesson_with_reps())
        video = self.workspace / "artifacts/videos/slope-video.mp4"
        video.parent.mkdir(parents=True, exist_ok=True)
        video.write_bytes(b"fake")
        artifact_manifest.register_artifact(self.workspace, {
            "id": "slope-video", "type": "voice-animation", "title": "Slope video",
            "purpose": "Show slope.", "concepts": ["math.derivative"],
            "chapter_id": "change", "topic_id": "local-change",
            "lesson_id": "slope-introduction",
            "location": {"path": "artifacts/videos/slope-video.mp4"},
            "mime_type": "video/mp4", "metadata": {},
            "status": "ready", "created_at": "2026-09-12T16:00:00Z",
            "updated_at": "2026-09-12T16:00:00Z",
        })
        text = self.render()
        lesson_html = text[text.index('<section class="lesson"'):]
        self.assertIn("<video", text)
        self.assertEqual(lesson_html.count('class="chip manim ready"'), 1)
        self.assertEqual(lesson_html.count('class="chip manim"'), 1)
        self.assertEqual(lesson_html.count('class="chip text ready"'), 1)
        self.assertEqual(lesson_html.count('class="chip text"'), 1)
        self.assertNotIn("success_criteria", text)

    def test_missing_manifest_still_renders(self):
        (self.workspace / "manifest.json").unlink()
        text = self.render()
        self.assertIn("Slope as local change", text)

    def test_course_shell_keeps_compact_logo_and_grainy_selection_surface(self):
        text = self.render()
        logo_start = text.index('<a class="gnos-logo"')
        logo_end = text.index("</a>", logo_start)
        logo = text[logo_start:logo_end]

        self.assertIn('width="320" height="107"', logo)
        self.assertNotIn('style="', logo)
        selected_start = text.index(".curr-row.is-selected{")
        selected_end = text.index("}", selected_start)
        selected_css = text[selected_start:selected_end]
        self.assertIn("background-color:var(--row-selected)", selected_css)
        self.assertIn("background-image:", selected_css)
        self.assertIn("feTurbulence", selected_css)

    def test_course_shell_uses_reference_paper_and_selection_tones(self):
        text = self.render()

        self.assertIn("--paper:#F6F4EE", text)
        self.assertIn("--row-selected:#E0DFDC", text)

    def test_explicit_hero_copy_can_present_a_short_editorial_title(self):
        course_file = self.workspace / "course.json"
        course = json.loads(course_file.read_text())
        course["title"] = "Probability for prediction, algorithms, and quantitative finance"
        course["goal"] = "Build and critique probabilistic systems."
        course["hero_title"] = "Probability"
        course["hero_subtitle"] = "For prediction, algorithms, and quantitative finance."
        course_file.write_text(json.dumps(course))

        text = self.render()

        self.assertIn('class="hero-title hero-title-display">Probability</h1>', text)
        self.assertIn(
            '<p class="hero-subtitle">For prediction, algorithms, and quantitative finance.</p>',
            text,
        )

    def test_editorial_hero_uses_montserrat_at_a_bounded_scale(self):
        course_file = self.workspace / "course.json"
        course = json.loads(course_file.read_text())
        course["hero_title"] = "Probability"
        course_file.write_text(json.dumps(course))

        text = self.render()
        title_start = text.index(".hero-title{")
        title_end = text.index("}", title_start)
        title_css = text[title_start:title_end]
        display_start = text.index(".hero-title-display{")
        display_end = text.index("}", display_start)
        display_css = text[display_start:display_end]
        display_row_start = text.index(".hero-title-row.is-display{")
        display_row_end = text.index("}", display_row_start)
        display_row_css = text[display_row_start:display_row_end]

        self.assertIn('--title-font:"Oxanium","Montserrat",sans-serif', text)
        self.assertIn("font-weight:700", title_css)
        self.assertIn(".hero.hero-display{padding-top:64px", text)
        self.assertIn("height:auto", display_row_css)
        self.assertIn("font-size:clamp(72px,6.25vw,150px)", display_css)
        self.assertNotIn("scaleY", display_css)

    def test_rendered_course_loads_display_and_text_fonts(self):
        text = self.render()

        self.assertIn("https://fonts.googleapis.com/css2?family=Source+Serif+4", text)
        self.assertIn("https://fonts.googleapis.com/css2?family=IBM+Plex+Mono", text)
        self.assertIn("family=Montserrat:ital,wght@0,100..900;1,100..900", text)
        self.assertIn("family=Oxanium:wght@200..800", text)
        self.assertIn('--title-font:"Oxanium","Montserrat",sans-serif', text)
        # Prose is serif; monospace survives only for code and tabs.
        self.assertIn('--body-font:"Source Serif 4"', text)
        self.assertIn('--mono-font:"IBM Plex Mono",ui-monospace', text)
        self.assertIn("pre,code{font-family:var(--mono-font);}", text)

    def test_mobile_editorial_title_remains_bounded(self):
        text = self.render()

        self.assertIn("font-size:clamp(48px,6.5vw,86px)", text)

    def test_for_phrase_stays_in_unconfigured_course_title(self):
        course_file = self.workspace / "course.json"
        course = json.loads(course_file.read_text())
        course["title"] = "Algorithms for Decision Making"
        course["goal"] = "Build reliable decision algorithms."
        course_file.write_text(json.dumps(course))

        text = self.render()

        self.assertIn('class="hero-title">Algorithms for Decision Making</h1>', text)
        self.assertIn(
            '<p class="hero-subtitle">Build reliable decision algorithms.</p>', text,
        )

    def test_partial_hero_copy_falls_back_without_dropping_course_content(self):
        course_file = self.workspace / "course.json"
        course = json.loads(course_file.read_text())
        course["hero_title"] = "Short title"
        course["goal"] = "Keep the canonical learning goal visible."
        course_file.write_text(json.dumps(course))

        text = self.render()

        self.assertIn('class="hero-title hero-title-display">Short title</h1>', text)
        self.assertIn(
            '<p class="hero-subtitle">Keep the canonical learning goal visible.</p>',
            text,
        )


if __name__ == "__main__":
    unittest.main()
