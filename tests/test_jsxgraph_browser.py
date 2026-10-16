"""Inspect JSXGraph examples inside the real course viewer with Node Playwright."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/course-design/scripts"))
sys.path.insert(0, str(ROOT / "skills/jsxgraph/scripts"))

from artifact_manifest import register_artifact
from build_graph import build_graph
from course_contract import validate_course
from course_workspace import create_workspace, publish_lesson
from tests.test_lesson_contract import valid_lesson, valid_v2_course
from tests.test_portal_interactions import reviewed_lesson


EXAMPLES = {
    "derivative": ("Slope at a point", "math", "math", "math.derivative", "forest",
                   "y=x^2", "At x = 1, y = 1 and dy/dx = 2. The tangent rises locally.",
                   "At x = -1, explain the sign of a small change in y when x increases."),
    "gradient-descent": ("Step down a loss", "artificial-intelligence", None,
                         "artificial-intelligence.gradient-descent", "luxe",
                         r"L(w)=\frac{1}{2}w^2,\quad w_{t+1}=w_t-\eta w_t",
                         "For this quadratic, the gradient is w. At w = 3 and η = 0.4, the next parameter is 1.8.",
                         "Explain why η = 1.2 crosses zero but still reduces the loss from w = 3."),
    "supply-demand": ("A demand shift", "economics", "economics", "economics.equilibrium", "blue",
                      r"P_d=a-Q,\quad P_s=2+\frac{1}{2}Q",
                      "At a = 8, both curves give P = 4 at Q = 4. Changing a shifts demand while supply stays fixed.",
                      "At a = 11, calculate equilibrium and distinguish a shift from movement along supply."),
}


def make_course(root, example, palette=None):
    title, subject, teacher, concept, default_palette, equation, explanation, task = EXAMPLES[example]
    plan = valid_v2_course()
    plan.update(id=example, title=title, goal=task)
    topic = plan["chapters"][0]["topics"][0]
    topic.update(title=title, subject=subject, teacher=teacher, concepts=[concept], outcome=task)
    topic["skill_routes"] = ["skills/subject/SKILL.md", f"skills/subject/subjects/{subject}.md"]
    plan = validate_course(plan)
    workspace = create_workspace(root, "graph-review", plan)
    lesson = valid_lesson(plan)
    lesson.update(course_id=example, title=title, teacher=teacher, concepts=[concept],
                  skill_routes=["skills/subject/SKILL.md", "skills/jsxgraph/SKILL.md"],
                  assumptions=["This is a synthetic artifact review, not learner evidence."],
                  artifacts=[{"id": "slope-graph"}])
    lesson["blocks"][0]["text"] = explanation
    lesson["blocks"][1] = {
        "id": "model-equation", "type": "equation", "concepts": [concept],
        "purpose": "Connect the worked values to the model.", "equation": equation,
        "production": lesson["blocks"][1]["production"],
    }
    for block in lesson["blocks"]:
        block["concepts"] = [concept]
    graph = lesson["blocks"][2]
    graph["purpose"] = task
    graph["production"]["skill_route"] = "skills/jsxgraph/SKILL.md"
    graph["production"]["depends_on_block_ids"] = ["model-equation"]
    exercise = lesson["exercises"][0]
    exercise.update(concepts=[concept], prompt=task, response_type="long-text",
                    evaluation={"mode": "manual"}, success_criteria=[task],
                    reference_block_ids=["intro", "graph"])
    publish_lesson(workspace, reviewed_lesson(lesson))
    html = workspace / "artifacts/simulations/graph.html"
    html.write_text(build_graph(ROOT / f"skills/jsxgraph/examples/{example}.js", palette or default_palette))
    register_artifact(workspace, {
        "id": "slope-graph", "type": "simulation", "title": title,
        "purpose": task, "concepts": [concept], "chapter_id": "change",
        "topic_id": "local-change", "lesson_id": lesson["id"],
        "location": {"path": "artifacts/simulations/graph.html"},
        "mime_type": "text/html", "metadata": {"dimensions": {"width": 1280, "height": 800}},
        "status": "ready", "created_at": "2026-09-30T16:00:00Z", "updated_at": "2026-09-30T16:00:00Z",
    })
    result = subprocess.run([sys.executable, str(ROOT / "skills/course-viewer/scripts/render_viewer.py"),
                             str(workspace)], capture_output=True, text=True)
    if result.returncode:
        raise AssertionError(result.stderr)
    return workspace / "portal/index.html"


def playwright_available():
    node = shutil.which("node")
    return node and subprocess.run([node, "-e", "require('playwright')"],
                                  capture_output=True).returncode == 0


@unittest.skipUnless(playwright_available(), "Node Playwright is unavailable; supply NODE_PATH when needed")
class JSXGraphBrowserTests(unittest.TestCase):
    def test_graphs_in_course_iframes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pages = {example: str(make_course(root, example)) for example in EXAMPLES}
            # Exercise the fourth shared palette as well.
            wine = root / "wine"
            pages["wine"] = str(make_course(wine, "derivative", "wine"))
            config = root / "review.json"
            config.write_text(json.dumps({"pages": pages, "screenshots": str(root / "screenshots")}))
            result = subprocess.run([shutil.which("node"), str(ROOT / "tests/jsxgraph_browser.cjs"),
                                     str(config)], capture_output=True, text=True, timeout=180)
            review = os.environ.get("GNOS_GRAPH_REVIEW_DIR")
            if review:
                shutil.copytree(root, review, dirs_exist_ok=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
