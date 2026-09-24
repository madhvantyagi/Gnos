"""Browser checks for the viewer's local math and code assets."""
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/course-viewer/scripts"))
import render_viewer as viewer  # noqa: E402

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


@unittest.skipUnless(sync_playwright, "Playwright is unavailable")
class ViewerBrowserTests(unittest.TestCase):
    def test_math_in_lessons_exercises_and_late_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            portal = Path(tmp)
            shutil.copytree(viewer.VENDOR, portal / "assets")
            lesson = viewer.render_block({
                "id": "intro", "type": "explanation",
                "text": r"For $x=2$, $f(x)=x^2$. Read `p_T_given_S = sens`.",
                "items": [r"Then $f'(x)=2x$."],
                "code": "def square(x):\n    return x * x\n",
            }, {}, {})
            equation = viewer.render_block({
                "id": "eq", "type": "equation", "equation": r"f'(2)=4"
            }, {}, {})
            exercise = viewer.render_exercise_card({
                "id": "ex1", "prompt": r"At $x=3$, what is $f'(x)$?",
                "response_type": "short-text", "evaluation": {"mode": "manual"},
            }, "browser-check", "Exercise")
            body = (
                '<div id="math-render-status" role="alert" hidden>Math could not render.</div>'
                '<div id="tabs"><button data-tab="lessons">Lessons</button>'
                '<button data-tab="exercises">Exercises</button></div>'
                f'<section id="tab-lessons" class="tab active">{lesson}{equation}</section>'
                f'<section id="tab-exercises" class="tab">{exercise}</section>'
                '<div id="late-answer"></div>'
            )
            template = viewer.TEMPLATE.read_text()
            head, rest = template.split(viewer.BODY_START, 1)
            _, tail = rest.split(viewer.BODY_END, 1)
            page_path = portal / "index.html"
            page_path.write_text(head + body + tail)

            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(channel="chrome", headless=True)
                try:
                    page = browser.new_page()
                    page.route("https://**", lambda route: route.abort())
                    page.goto(page_path.as_uri())
                    page.wait_for_selector("#tab-lessons .katex")
                    self.assertGreaterEqual(page.locator("#tab-lessons .katex").count(), 4)
                    self.assertEqual(page.locator("#tab-lessons .katex-display").count(), 1)
                    self.assertEqual(page.locator("#tab-exercises .katex").count(), 2)
                    self.assertEqual(page.locator(".katex-error").count(), 0)
                    self.assertEqual(page.locator(".inline-code").count(), 1)
                    self.assertTrue(page.locator("#math-render-status").is_hidden())

                    page.locator('[data-tab="exercises"]').click()
                    self.assertTrue(page.locator("#tab-exercises .katex").first.is_visible())
                    page.locator('[data-tab="lessons"]').click()
                    self.assertTrue(page.locator("#tab-lessons .katex").first.is_visible())

                    code = page.locator("pre.code-block code")
                    self.assertGreater(code.locator("span[class^='hljs-']").count(), 0)
                    self.assertEqual(code.evaluate("el => getComputedStyle(el.parentElement).borderLeftWidth"), "1px")

                    answer = viewer.render_rich_text(r"The worked answer is $f'(3)=6$.")
                    page.evaluate("html => {const el = document.getElementById('late-answer');"
                                  "el.innerHTML = html; window.gnosRenderMath(el);}", answer)
                    self.assertEqual(page.locator("#late-answer .katex").count(), 1)
                    if os.environ.get("GNOS_VIEWER_SCREENSHOT"):
                        page.screenshot(path=os.environ["GNOS_VIEWER_SCREENSHOT"], full_page=True)
                finally:
                    browser.close()


if __name__ == "__main__":
    unittest.main()
