"""Course viewer render tests: a fresh course still shows a page."""
import json
import re
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
sys.path.insert(0, str(ROOT / "skills/course-viewer/scripts"))
import render_viewer  # noqa: E402


def plan_with_reps():
    plan = valid_v2_course()
    plan["chapters"][0]["topics"][0]["subtopics"] = [
        "Slope from nearby points", "Slope at one point"]
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


def lesson_with_reps(plan=None):
    from course_contract import course_content_fingerprint, validate_course
    from tests.test_course_contract_v2 import valid_v2_course as base_plan
    target_plan = plan if plan is not None else plan_with_reps()
    validated = validate_course(target_plan)
    lesson = valid_lesson(validated)
    for block, representation_id in zip(lesson["blocks"], ("t", "m", "s", "e")):
        block["representation_id"] = representation_id
    lesson["design_receipt"] = {
        "designed_at": lesson["updated_at"],
        "course_fingerprint": course_content_fingerprint(validated),
        "skill_route": "skills/lesson-design/SKILL.md",
        "review": "pass",
    }
    return lesson


class ViewerTests(unittest.TestCase):
    def test_simulation_iframe_uses_bounded_metadata_dimensions(self):
        artifact = {
            "id": "sim", "type": "simulation", "title": "Simulation",
            "mime_type": "text/html", "location": {"path": "artifacts/sim.html"},
            "metadata": {"dimensions": {"width": 1440, "height": 900}},
        }

        html = render_viewer.media_element(artifact, "generated")
        self.assertIn('class="simulation-frame"', html)
        self.assertIn('width="1440" height="900"', html)
        self.assertIn("--simulation-max-height:900px", html)
        self.assertIn('class="media simulation-media"', render_viewer.render_media(
            artifact, "generated", Path(".")))

    def test_simulation_dimensions_fall_back_when_out_of_bounds(self):
        artifact = {
            "id": "sim", "type": "simulation", "title": "Simulation",
            "mime_type": "text/html", "location": {"path": "artifacts/sim.html"},
            "metadata": {"dimensions": {"width": 99999, "height": 20}},
        }

        html = render_viewer.media_element(artifact, "generated")
        self.assertIn('width="1280" height="800"', html)
        self.assertIn("--simulation-max-height:800px", html)

    def test_simulation_iframe_uses_portrait_height_on_mobile_and_tablet(self):
        text = self.render("--outline-only")

        self.assertIn(
            ".media iframe.simulation-frame{height:clamp(480px,62.5vw,var(--simulation-max-height,800px));}",
            text,
        )
        mobile_start = text.index("@media (max-width:1100px)")
        mobile_end = text.index("@media (prefers-reduced-motion:reduce)", mobile_start)
        mobile_css = text[mobile_start:mobile_end]
        self.assertIn(".media iframe{height:300px;}", mobile_css)
        self.assertIn(
            ".media iframe.simulation-frame{height:min(var(--simulation-max-height,800px),max(760px,150vw));}",
            mobile_css,
        )

    def test_mixed_lesson_blocks_keep_readable_labels_and_preview_media_order(self):
        concept = "artificial-intelligence.agent-environment"
        lesson = {
            "id": "agent-loop", "course_id": "rl-basics", "topic_id": "agent-loop",
            "title": "The agent loop", "purpose": "Connect a prediction to an action.",
            "teacher": "math", "updated_at": "2026-09-23T12:00:00Z",
            "concepts": [concept], "exercises": [{
                "id": "predict-action", "prompt": "Which action should the agent choose?",
                "response_type": "short-text", "evaluation": {"mode": "manual"},
                "success_criteria": ["Connect the observation to the action."],
            }],
            "blocks": [
                {"id": "intro", "type": "explanation", "label": "Start with the loop",
                 "concepts": [concept], "purpose": "Introduce the sequence.",
                 "text": "The agent observes, chooses, and receives feedback."},
                {"id": "code", "type": "code", "label": "A small example",
                 "concepts": [concept], "purpose": "Make the sequence concrete.",
                 "code": "observation = env.observe()\naction = policy(observation)\n"},
                {"id": "equation", "type": "equation", "label": "The update",
                 "concepts": [concept], "purpose": "Show the return update.",
                 "equation": "G_t = R_{t+1} + \\gamma G_{t+1}"},
                {"id": "source", "type": "source", "label": "Read more",
                 "concepts": [concept], "purpose": "See the formal definition.",
                 "source_id": "rl-text", "text": "Use this chapter to check the formal terms."},
                {"id": "exercise", "type": "exercise", "label": "Try a prediction",
                 "concepts": [concept], "purpose": "Check the learner's model.",
                 "exercise_id": "predict-action", "text": "Now try the loop in a new case."},
                {"id": "simulation", "type": "simulation", "label": "Predict first",
                 "concepts": [concept], "purpose": "Watch the rollout respond.",
                 "artifact_id": "sim-html",
                 "text": "Before moving the slider, predict which action earns more.",
                 "caption": "The vertical marker shows the chosen action."},
                {"id": "interpretation", "type": "explanation", "label": "What changed",
                 "concepts": [concept], "purpose": "Interpret the rollout.",
                 "text": "The higher return came from the action with better feedback."},
                {"id": "diagram", "type": "diagram",
                 "concepts": [concept], "purpose": "Show the data flow.",
                 "artifact_id": "loop-diagram", "text": "Follow each arrow once."},
                {"id": "video", "type": "voice-animation", "label": "Watch it unfold",
                 "concepts": [concept], "purpose": "Animate one decision cycle.",
                 "artifact_id": "loop-video", "text": "Watch where the reward enters."},
                {"id": "handout", "type": "artifact", "label": "Keep the handout",
                 "concepts": [concept], "purpose": "Review the loop later.",
                 "artifact_id": "loop-handout", "text": "The handout puts the three steps on one page."},
            ],
        }
        artifacts = {
            "sim-html": {"id": "sim-html", "type": "simulation", "title": "Rollout simulator",
                         "purpose": "Adjust one choice at a time.", "mime_type": "text/html",
                         "location": {"path": "artifacts/sim.html"}, "metadata": {}},
            "loop-diagram": {"id": "loop-diagram", "type": "diagram", "title": "Agent loop",
                             "purpose": "Observation, action, feedback.", "mime_type": "image/png",
                             "location": {"path": "artifacts/loop.png"}, "metadata": {}},
            "loop-video": {"id": "loop-video", "type": "voice-animation", "title": "One cycle",
                           "purpose": "See one complete turn.", "mime_type": "video/mp4",
                           "location": {"path": "artifacts/loop.mp4"}, "metadata": {}},
            "loop-handout": {"id": "loop-handout", "type": "pdf", "title": "Agent loop handout",
                             "purpose": "Review the sequence.", "mime_type": "application/pdf",
                             "location": {"path": "artifacts/loop.pdf"}, "metadata": {"pages": 1}},
        }
        sources = {"rl-text": {"title": "Reinforcement Learning: An Introduction",
                                "sections": ["Chapter 3"], "url": "https://example.org/rl"}}

        rendered = render_viewer.render_lesson(
            lesson, 1, 1, None, None, artifacts, sources, Path("."), {}, course_id="rl-basics")

        self.assertIn('class="block-label">A small example</div>', rendered)
        self.assertIn('class="block-label">diagram</div>', rendered)
        labels = re.findall(r'<div class="block-label">(.*?)</div>', rendered)
        self.assertTrue(labels)
        self.assertTrue(all(concept not in label for label in labels))
        self.assertIn("observation = env.observe()\naction = policy(observation)\n", rendered)
        template = (ROOT / "skills/course-viewer/references/example.html").read_text()
        self.assertIn("white-space:pre;word-break:normal;overflow-wrap:normal", template)
        self.assertIn("tab-size:2;overflow-x:auto", template)
        self.assertIn(".block p{margin:8px 0;font-size:16px;}", template)
        self.assertNotIn("max-width:72ch", template)
        self.assertIn(".lesson .block .card{box-sizing:border-box;max-width:800px;}", template)
        self.assertIn(".lesson .block .card.exercise{max-width:none;}", template)
        self.assertIn('class="math math-display"', rendered)
        self.assertIn('class="card exercise"', rendered)
        self.assertIn('class="simulation-frame"', rendered)
        self.assertIn("<img", rendered)
        self.assertIn("<video", rendered)
        self.assertIn("open source", rendered)
        self.assertIn('class="card media-resource"', rendered)
        self.assertIn("Agent loop handout", rendered)
        self.assertLess(rendered.index("Use this chapter"), rendered.index("open source"))
        self.assertLess(rendered.index("Now try the loop"), rendered.index('class="card exercise"'))
        preview = rendered.index("Before moving the slider")
        caption = rendered.index("The vertical marker")
        simulator = rendered.index('class="simulation-frame"')
        interpretation = rendered.index("The higher return came")
        self.assertLess(preview, caption)
        self.assertLess(caption, simulator)
        self.assertLess(simulator, interpretation)

    def test_new_course_shows_formats_from_finished_lesson(self):
        plan = valid_v2_course()
        del plan["chapters"][0]["topics"][0]["outcome"]
        workspace = create_workspace(self.root, "sam", plan)
        from course_contract import validate_course
        publish_lesson(workspace, valid_lesson(validate_course(plan)))
        result = subprocess.run([sys.executable, str(RENDER), str(workspace)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        html = (workspace / "portal" / "index.html").read_text()
        self.assertIn('class="chip manim"', html)
        self.assertIn('class="chip simulation"', html)
        self.assertNotIn('data-outcome=', html)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plan = plan_with_reps()
        self.workspace = create_workspace(self.root, "alex", self.plan)

    def render(self, *flags):
        result = subprocess.run(
            [sys.executable, str(RENDER), str(self.workspace), *(flags or ("--outline-only",))],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return (self.workspace / "portal" / "index.html").read_text()

    def test_explicit_outline_renders_without_a_lesson(self):
        text = self.render("--outline-only")
        self.assertIn("Slope as local change", text)
        self.assertIn("Slope from nearby points", text)
        self.assertIn('data-td="subtopics"', text)
        self.assertIn('data-subtopics="Slope from nearby points · Slope at one point"', text)
        self.assertIn("chip manim", text)
        self.assertIn("No ready lessons yet", text)
        self.assertNotIn("success_criteria", text)

    def test_default_render_rejects_course_without_current_lesson(self):
        result = subprocess.run([sys.executable, str(RENDER), str(self.workspace)],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("lesson-design", result.stderr)
        self.assertFalse((self.workspace / "portal" / "index.html").exists())

    def test_default_render_rejects_a_draft_current_lesson(self):
        draft = lesson_with_reps(self.plan)
        draft["publication"] = "draft"
        draft.pop("design_receipt")
        publish_lesson(self.workspace, draft)
        result = subprocess.run([sys.executable, str(RENDER), str(self.workspace)],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no ready lesson", result.stderr)

    def test_lesson_delivery_requires_a_ready_current_lesson(self):
        result = subprocess.run([sys.executable, str(RENDER), str(self.workspace),
                                 '--require-current-lesson'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('lesson-design', result.stderr)
        publish_lesson(self.workspace, lesson_with_reps(self.plan))
        result = subprocess.run([sys.executable, str(RENDER), str(self.workspace),
                                 '--require-current-lesson'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_ready_lesson_flips_chips_and_shows_media(self):
        publish_lesson(self.workspace, lesson_with_reps(self.plan))
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
