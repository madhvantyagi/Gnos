"""Graph selection, offline export, and existing lesson integration."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/jsxgraph"


class Resources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.external = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("script", "img", "iframe", "link"):
            for key in ("src", "href"):
                if attrs.get(key):
                    self.external.append(attrs[key])


class JSXGraphTests(unittest.TestCase):
    def test_graph_context_selects_graph_skill_without_diagram_servers(self):
        for media in ("graph", "jsxgraph"):
            result = subprocess.run([
                sys.executable, str(ROOT / "skills/learning-orchestrator/scripts/assemble_context.py"),
                "--subject", "math", "--mode", "local", "--media", media, "--manifest",
            ], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            paths = result.stdout.splitlines()
            self.assertIn("skills/jsxgraph/SKILL.md", paths)
            self.assertNotIn("skills/pinepaper/SKILL.md", paths)
            self.assertNotIn("skills/excalidraw/SKILL.md", paths)
            for path in paths:
                self.assertTrue((ROOT / path).is_file(), path)

    def test_examples_build_without_external_resources(self):
        with tempfile.TemporaryDirectory() as temporary:
            for example in ("derivative", "gradient-descent", "supply-demand"):
                output = Path(temporary) / f"{example}.html"
                result = subprocess.run([
                    sys.executable, str(SKILL / "scripts/build_graph.py"),
                    "--example", example, "--palette", "forest", "--output", str(output),
                ], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                content = output.read_text()
                parser = Resources()
                parser.feed(content)
                self.assertEqual(parser.external, [])
                self.assertIn('data-palette="forest"', content)
                self.assertIn("Permission is hereby granted", content)
                self.assertNotIn("{{", content)

    def test_custom_scene_and_invalid_palette(self):
        with tempfile.TemporaryDirectory() as temporary:
            scene = Path(temporary) / "a custom scene.js"
            scene.write_text('document.getElementById("graph-title").textContent = "My graph";')
            command = [sys.executable, str(SKILL / "scripts/build_graph.py"),
                       "--scene", str(scene), "--output", str(Path(temporary) / "graph.html")]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("My graph", (Path(temporary) / "graph.html").read_text())
            invalid = subprocess.run(command + ["--palette", "unknown"], capture_output=True, text=True)
            self.assertNotEqual(invalid.returncode, 0)

    def test_graph_skill_is_valid_in_existing_lesson_contract(self):
        sys.path.insert(0, str(ROOT / "skills/course-design/scripts"))
        from course_contract import validate_course
        from lesson_contract import validate_lesson
        from tests.test_lesson_contract import valid_lesson, valid_v2_course
        plan = validate_course(valid_v2_course())
        lesson = valid_lesson(plan)
        lesson["skill_routes"].append("skills/jsxgraph/SKILL.md")
        lesson["blocks"][2]["production"]["skill_route"] = "skills/jsxgraph/SKILL.md"
        self.assertEqual(validate_lesson(lesson, plan), lesson)


if __name__ == "__main__":
    unittest.main()
