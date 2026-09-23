"""Math rendering tests: KaTeX delimiters preserved server-side, rendered client-side."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/course-viewer/scripts"))
sys.path.insert(0, str(ROOT / "skills/course-design/scripts"))

import render_viewer as viewer
from course_workspace import create_workspace, publish_lesson
from tests.test_course_contract_v2 import valid_v2_course
from tests.test_lesson_contract import valid_lesson

RENDER = ROOT / "skills/course-viewer/scripts/render_viewer.py"


def equation_block(equation):
    return {"id": "eq1", "type": "equation", "concepts": ["math.derivative"],
            "purpose": "Show math.", "equation": equation}


class MathBlockTests(unittest.TestCase):
    def test_lesson_paragraphs_remain_separate_around_math(self):
        rendered = viewer.render_block({
            'id': 'intro', 'type': 'explanation', 'concepts': ['math.derivative'],
            'purpose': 'Explain the notation.',
            'text': 'First define the quantity $x$.\n\nThen explain its role.'}, {}, {})
        self.assertIn('</p><p>Then explain its role.</p>', rendered)

    def test_authored_tex_is_preserved_across_every_delimiter(self):
        import html
        expressions = [
            r'\min_x f(x)\quad\text{s.t.}\quad x\in\mathcal{X},\quad x^*\in\arg\min_x f(x)',
            r'\mathbf{F}=m\mathbf{a},\quad g=9.81\,\mathrm{m\,s^{-2}}',
            r'\psi^*\psi,\quad A^\dagger,\quad \vec{E}\cdot\vec{B}',
            r'\begin{aligned}x&=1\\y&=2\end{aligned}',
            r'x^*',
        ]
        for tex in expressions:
            with self.subTest(tex=tex):
                for start, end in [('$', '$'), ('$$', '$$'), (r'\(', r'\)'), (r'\[', r'\]')]:
                    rendered = html.unescape(viewer.render_rich_text(start + tex + end))
                    self.assertIn(start + tex + end, rendered)
                self.assertIn('$$' + tex + '$$', html.unescape(viewer.math_display_html(tex)))

    def test_equation_block_does_not_render_as_pre(self):
        html = viewer.render_block(
            equation_block(r"\frac{a}{b} + \sqrt{x}"), {}, {})
        self.assertNotIn("<pre>", html)
        self.assertIn('class="math math-display"', html)
        self.assertIn("$$", html)
        # TeX source is preserved (escaped) for KaTeX auto-render.
        self.assertIn(r"\frac", html)
        self.assertIn(r"\sqrt", html)
        # Hand-rolled span renderer is gone.
        self.assertNotIn("math-frac", html)
        self.assertNotIn("math-sqrt", html)
        self.assertIn('role="math"', html)

    def test_inline_and_display_dollars_in_text_render_as_math(self):
        block = {"id": "t1", "type": "explanation",
                 "concepts": ["math.derivative"], "purpose": "Show math.",
                 "text": r"Euler says $e^{i\pi} + 1 = 0$ and $$\frac{1}{2}$$ done."}
        html = viewer.render_block(block, {}, {})
        self.assertIn('class="math math-inline"', html)
        self.assertIn('class="math math-display"', html)
        self.assertIn("$$", html)
        self.assertIn(r"\frac", html)
        self.assertNotIn("<pre>", html)
        self.assertNotIn("math-frac", html)
        # Exercise prompts support inline math too.
        exercise = {"id": "ex1", "concepts": ["math.derivative"],
                    "prompt": r"Compute $\sum_{i=1}^{n} i$ please.",
                    "response_type": "short-text",
                    "evaluation": {"mode": "manual"}}
        card = viewer.render_exercise_card(exercise, "c1", "exercise · ex1")
        self.assertIn('class="math math-inline"', card)
        self.assertIn(r"\sum", card)
        # \(...\) and \[...\] delimiters are preserved for KaTeX too.
        paren = viewer.render_rich_text(r"Hi \(x^2\) and \[y^2\] end.")
        self.assertIn(r"\(", paren)
        self.assertIn(r"\)", paren)
        self.assertIn(r"\[", paren)
        self.assertIn(r"\]", paren)
        self.assertIn('math-inline', paren)
        self.assertIn('math-display', paren)

    def test_escaping_and_edge_cases(self):
        # <, >, & must be escaped and never break layout.
        html = viewer.render_block(
            equation_block("x < y & y > z"), {}, {})
        self.assertIn("&lt;", html)
        self.assertIn("&amp;", html)
        self.assertNotIn("<script>", html)
        text_html = viewer.render_rich_text("x < y and $a < b$ ok")
        # Comparisons become single KaTeX spans; the relation stays escaped.
        self.assertIn("\\(x &lt; y\\)", text_html)
        self.assertIn("&lt;", text_html)
        # Script injection is neutralised.
        evil = viewer.render_block(
            equation_block("<script>alert(1)</script>"), {}, {})
        self.assertNotIn("<script>alert", evil)
        self.assertIn("&lt;script&gt;", evil)
        # tex_to_html is an escape-only passthrough for KaTeX (backslashes kept).
        stray = viewer.tex_to_html("затравочные \\foo \\")
        self.assertIn("\\foo", stray)
        self.assertIn("затравочные", stray)
        self.assertNotIn("<", stray.replace("&lt;", ""))
        escaped = viewer.tex_to_html("<b>&\"</b>")
        self.assertIn("&lt;b&gt;", escaped)
        self.assertIn("&amp;", escaped)
        self.assertNotIn("<b>", escaped)
        # Empty equation does not crash and renders an empty math slot.
        empty = viewer.render_block(equation_block(""), {}, {})
        self.assertIn("math", empty)
        self.assertIn("math-empty", empty)
        self.assertNotIn("<pre>", empty)
        ws = viewer.render_block(equation_block("   "), {}, {})
        self.assertIn("math", ws)
        self.assertIn("math-empty", ws)
        # Escaped dollars stay literal, unclosed stay literal text, no crash.
        literal = viewer.render_rich_text("unclosed $x + 1 here")
        self.assertIn("$", literal)
        self.assertNotIn("math-inline", literal)
        escaped_dollar = viewer.render_rich_text(r"cost \$5 and $a$ ok")
        self.assertIn("$5", escaped_dollar)
        self.assertIn('math-inline', escaped_dollar)
        # Code blocks keep <pre> and never gain math classes.
        code = viewer.render_block(
            {"id": "c1", "type": "code", "concepts": ["math.derivative"],
             "purpose": "Show code.", "code": "x < y"}, {}, {})
        self.assertIn("<pre>", code)
        self.assertNotIn("math-inline", code)
        self.assertNotIn("math-display", code)

    def test_katex_cdn_in_rendered_portal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = create_workspace(root, "alex", valid_v2_course())
            result = subprocess.run(
                [sys.executable, str(RENDER), str(workspace), "--outline-only"],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            text = (workspace / "portal" / "index.html").read_text()
            # KaTeX 0.16.x ships via jsDelivr CDN.
            self.assertIn("katex.min.css", text)
            self.assertIn("katex.min.js", text)
            self.assertIn("auto-render.min.js", text)
            self.assertIn("cdn.jsdelivr.net/npm/katex@0.16", text)
            self.assertIn("renderMathInElement", text)
            self.assertIn("throwOnError", text)
            # Fallback math styling still ships inline for CDN-blocked reads.
            self.assertIn(".math-display", text)
            # Hand-rolled span CSS is gone.
            self.assertNotIn("math-frac", text)

    def test_plain_ascii_exercise_sentence_renders_math(self):
        sentence = ("A neuron is y-hat=sigmoid(z) with z=w.x+b. "
                    "With squared loss L=1/2(y-hat-t)^2, "
                    "dL/dw=(y-hat-t)sigmoid-prime(z)x. "
                    "The update w:=w-eta dL/dw moves against error times input times saturation.")
        exercise = {"id": "ex1", "concepts": ["math.derivative"],
                    "prompt": sentence,
                    "response_type": "short-text",
                    "evaluation": {"mode": "manual"}}
        card = viewer.render_exercise_card(exercise, "c1", "exercise · ex1")
        # ASCII idioms are normalised to LaTeX for KaTeX, not passed through raw.
        self.assertGreaterEqual(card.count("math-inline"), 4)
        self.assertIn("\\hat{y}", card)
        self.assertIn("w \\cdot x", card)
        self.assertIn("\\frac{1}{2}", card)
        self.assertIn("dL/dw", card)
        self.assertIn("w:=w-eta", card)
        self.assertIn("\\(\\hat{y}=sigmoid(z)\\)", card)
        self.assertIn("moves against error times input times saturation", card)
        self.assertNotIn("<pre>", card)

    def test_plain_prose_without_math_stays_text(self):
        html = viewer.render_rich_text("The cat sat on the mat. Well-known facts here!")
        self.assertNotIn("math-inline", html)
        self.assertNotIn("math-display", html)

    def test_realistic_lesson_with_fraction_sqrt_sum(self):
        lesson = valid_lesson()
        lesson["blocks"] = [
            {"id": "eq-frac", "type": "equation",
             "concepts": ["math.derivative"], "purpose": "Show slope.",
             "equation": r"\frac{d}{dx} x^2 = 2x"},
            {"id": "eq-sqrt", "type": "equation",
             "concepts": ["math.derivative"], "purpose": "Show slope.",
             "equation": r"\sqrt{x^2 + 1} + \sum_{i=1}^{n} i = \int_0^1 x dx"},
            {"id": "intro", "type": "explanation",
             "concepts": ["math.derivative"], "purpose": "Show slope.",
             "text": r"Recall $\alpha \to \beta$ and $$\sqrt{2} \approx 1.4$$ end."},
        ]
        lesson["exercises"] = []
        bodies = [viewer.render_block(b, {}, {}) for b in lesson["blocks"]]
        joined = "".join(bodies)
        self.assertIn('math-display', joined)
        self.assertIn('math-inline', joined)
        self.assertIn("$$", joined)
        self.assertIn(r"\frac", joined)
        self.assertIn(r"\sqrt", joined)
        self.assertIn(r"\sum", joined)
        self.assertIn(r"\int", joined)
        self.assertIn(r"\alpha", joined)
        self.assertIn(r"\to", joined)
        self.assertIn(r"\approx", joined)
        self.assertNotIn("math-frac", joined)
        self.assertNotIn("math-sqrt", joined)
        self.assertNotIn("<pre>", joined)

    def test_linear_maps_paragraph_renders_proper_latex(self):
        # Regression for the reported course page: bare ASCII such as
        # R^(m x n), [v]_B, and P^(-1) rendered as monospace soup.
        text = ("For A in R^(m x n), T(x) = Ax is a linear map from R^n to R^m. "
                "Rank is rank(A) = dim of the column space. "
                "A vector v exists independently of any basis; [v]_B is only its tuple. "
                "Change of basis: [v]_new = P^(-1)[v]_old. "
                "Concrete case: A = diag(2, 0.5) squashes by 1/2. "
                "Every projection (xW_Q, xW_K, xW_V) is exactly this.")
        html = viewer.render_rich_text(text)
        self.assertIn("\\mathbb{R}^{m \\times n}", html)
        self.assertIn("\\mathbb{R}^{n}", html)
        self.assertIn("\\mathbb{R}^{m}", html)
        self.assertIn("\\operatorname{rank}(A)", html)
        self.assertIn("\\operatorname{dim}", html)
        self.assertIn("[v]_B", html)
        self.assertIn("[v]_{new} = P^{-1}[v]_{old}", html)
        self.assertIn("\\operatorname{diag}(2, 0.5)", html)
        self.assertIn("\\frac{1}{2}", html)
        self.assertIn("(xW_Q, xW_K, xW_V)", html)
        # Prose stays prose; leading "A" is the English article here.
        self.assertIn("is a linear map from", html)
        self.assertIn("of the column space", html)
        self.assertNotIn("<pre>", html)
        self.assertGreaterEqual(html.count("math-inline"), 8)

    def test_equation_block_does_not_guess_the_authors_notation(self):
        html = viewer.render_block(equation_block("R^(m x n)"), {}, {})
        self.assertIn('class="math math-display"', html)
        self.assertIn("$$R^(m x n)$$", html)

    def test_sentence_boundary_splits_equations(self):
        html = viewer.render_rich_text("W_Q = [[1,1],[0,1]] and x = [1, 2].")
        self.assertEqual(html.count("math-inline"), 2)
        self.assertIn("\\begin{bmatrix}1 &amp; 1 \\\\ 0 &amp; 1\\end{bmatrix}", html)
        self.assertIn("x = [1, 2]", html)

    def test_lone_letters_wrap_but_articles_do_not(self):
        html = viewer.render_rich_text("A vector v exists independently.")
        self.assertTrue(html.startswith("A vector "))
        self.assertIn("\\(v\\)", html)
        html2 = viewer.render_rich_text("means apply A first, then B.")
        self.assertIn("\\(A\\)", html2)
        self.assertIn("\\(B\\)", html2)

    def test_normaliser_covers_common_idioms(self):
        cases = {
            "R^(m x n)": "\\mathbb{R}^{m \\times n}",
            "R^n": "\\mathbb{R}^{n}",
            "P^(-1)": "P^{-1}",
            "[v]_new": "[v]_{new}",
            "xW_Q": "xW_Q",
            "rank(A)": "\\operatorname{rank}(A)",
            "dim": "\\operatorname{dim}",
            "diag(2, 0.5)": "\\operatorname{diag}(2, 0.5)",
            "sqrt(2)": "\\sqrt{2}",
            "1/2": "\\frac{1}{2}",
            "10/sqrt(2)": "\\frac{10}{\\sqrt{2}}",
            "(q . k)/sqrt(2)": "\\frac{(q \\cdot k)}{\\sqrt{2}}",
            "y-hat": "\\hat{y}",
            "w.x": "w \\cdot x",
            "5*sqrt(2)": "5 \\cdot \\sqrt{2}",
            "[[1,1],[0,1]]": "\\begin{bmatrix}1 & 1 \\\\ 0 & 1\\end{bmatrix}",
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                # normalize_ascii_math returns raw LaTeX (escaping happens later).
                self.assertIn(expected, viewer.normalize_ascii_math(source))

    def test_normaliser_leaves_clean_latex_untouched(self):
        for tex in (r"\frac{a}{b} + \sqrt{x}",
                    r"\mathbb{R}^{n}",
                    r"\operatorname{diag}(2, 0.5)",
                    r"W_Q = \begin{bmatrix}1 & 1 \\ 0 & 1\end{bmatrix}",
                    r"e^{i\pi} + 1 = 0"):
            with self.subTest(tex=tex):
                once = viewer.normalize_ascii_math(tex)
                self.assertEqual(viewer.normalize_ascii_math(once), once)


if __name__ == "__main__":
    unittest.main()
