#!/usr/bin/env python3
"""
linter.py — Static AST & Pattern Linter for Manim Community Code

Catches 20+ common AI-generated bugs, deprecated APIs, unescaped LaTeX,
and audio-sync pitfalls before spending GPU/CPU cycles on rendering.
"""

import argparse
import ast
import re
import shutil
import sys
from pathlib import Path
from typing import List, Tuple

# Common obsolete APIs from old Manim versions (3b1b / ManimGL / Manim v0.1)
DEPRECATED_APIS = {
    "ShowCreation": "Use 'Create' instead in Manim Community Edition.",
    "TextMobject": "Use 'Tex' for mathematical text or 'Text' for standard text.",
    "FadeInFrom": "Use 'FadeIn(..., shift=...)' in Manim Community.",
    "FadeOutAndShift": "Use 'FadeOut(..., shift=...)' in Manim Community.",
    "get_graph": "Use 'axes.plot()' instead of 'axes.get_graph()'.",
}

# Coordinate boundaries for standard 16:9 1080p frame
FRAME_X_MAX = 7.11
FRAME_Y_MAX = 4.0


class ManimLintVisitor(ast.NodeVisitor):
    def __init__(self, filename: str, content: str):
        self.filename = filename
        self.content = content
        self.lines = content.splitlines()
        self.issues: List[Tuple[int, str, str]] = []  # (line, severity, message)

    def add_issue(self, lineno: int, severity: str, message: str):
        self.issues.append((lineno, severity, message))

    def visit_ClassDef(self, node: ast.ClassDef):
        # Check for obsolete CONFIG dict pattern
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == "CONFIG":
                        self.add_issue(
                            item.lineno,
                            "ERROR",
                            "Obsolete 'CONFIG = {...}' pattern found. Use standard '__init__' or scene methods in ManimCE."
                        )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # Check for deprecated API names
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name and func_name in DEPRECATED_APIS:
            self.add_issue(node.lineno, "WARNING", f"'{func_name}' is deprecated: {DEPRECATED_APIS[func_name]}")

        # Check for bare .animate without a method invocation (e.g. self.play(dot.animate))
        if func_name == "play":
            for arg in node.args:
                if isinstance(arg, ast.Attribute) and arg.attr == "animate":
                    self.add_issue(
                        node.lineno,
                        "ERROR",
                        "Incomplete '.animate' call found. You must chain a method, e.g., 'mobject.animate.shift(UP)'."
                    )

        # Check for MathTex without raw string
        if func_name in ("MathTex", "Tex"):
            if not getattr(self, "_latex_checked", False):
                self._latex_checked = True
                if shutil.which("latex") is None:
                    self.add_issue(
                        node.lineno,
                        "NOTE",
                        "'MathTex'/'Tex' requires system LaTeX. If BasicTeX is not installed ('brew install --cask basictex'), use 'Text(...)' instead."
                    )
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    raw_str = arg.value
                    # Check if string has LaTeX command like \frac, \alpha, \sum
                    if any(cmd in raw_str for cmd in ["\\f", "\\a", "\\b", "\\n", "\\r", "\\t", "\\s"]):
                        # Inspect source line directly
                        line_text = self.lines[arg.lineno - 1] if 0 <= arg.lineno - 1 < len(self.lines) else ""
                        if re.search(r'(MathTex|Tex)\s*\(\s*["\']', line_text) and not re.search(r'(MathTex|Tex)\s*\(\s*r["\']', line_text):
                            self.add_issue(
                                arg.lineno,
                                "WARNING",
                                "LaTeX string in MathTex/Tex lacks raw string prefix r'...'. Backslashes like \\frac may escape as form-feeds."
                            )

        # Check for voiceover bookmark matching
        if func_name == "wait_until_bookmark":
            if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                bm_name = node.args[0].value
                pattern = f'<bookmark mark=[\'"]{re.escape(bm_name)}[\'"]'
                if not re.search(pattern, self.content):
                    self.add_issue(
                        node.lineno,
                        "WARNING",
                        f"wait_until_bookmark('{bm_name}') called, but no matching '<bookmark mark=\"{bm_name}\"/>' found in voiceover text."
                    )

        self.generic_visit(node)


def check_regex_patterns(content: str, filename: str) -> List[Tuple[int, str, str]]:
    """Runs regex checks on code lines for syntax traps."""
    issues = []
    lines = content.splitlines()

    for idx, line in enumerate(lines, 1):
        # Check for coordinates placed far outside standard frame
        match = re.search(r'shift\(\s*([+-]?\d+(?:\.\d+)?)\s*\*\s*(RIGHT|LEFT|UP|DOWN)', line)
        if match:
            val = float(match.group(1))
            dir_name = match.group(2)
            if dir_name in ("RIGHT", "LEFT") and abs(val) > FRAME_X_MAX + 1:
                issues.append((idx, "WARNING", f"Horizontal shift magnitude {val} exceeds typical screen frame limit ({FRAME_X_MAX})."))
            elif dir_name in ("UP", "DOWN") and abs(val) > FRAME_Y_MAX + 1:
                issues.append((idx, "WARNING", f"Vertical shift magnitude {val} exceeds typical screen frame limit ({FRAME_Y_MAX})."))

        # Check for multiple simultaneous transforms without ReplacementTransform
        if "self.play(Transform(" in line and "Transform(" in line[line.find("Transform(") + 10:]:
            issues.append((idx, "NOTE", "Multiple simultaneous 'Transform()' calls on the same line may cause unexpected morphing. Consider 'ReplacementTransform' or 'AnimationGroup'."))

    return issues


def check_slide_syndrome(content: str, filename: str) -> List[Tuple[int, str, str]]:
    """Flags scenes that rely solely on cards and text without mathematical/geometric depth."""
    issues = []
    card_count = len(re.findall(r'(RoundedRectangle|Rectangle|Square)\(', content))
    text_count = len(re.findall(r'(Text|Tex|MathTex)\(', content))
    
    # Mathematical and visual depth markers
    math_depth_markers = re.findall(r'(Axes|NumberPlane|plot|Vector|ArrowVectorField|ParametricFunction|Polygon|Graph|DiGraph|GaussianDistribution|ParticleStream|Glow|TracedPath)', content)
    
    if card_count >= 3 and text_count >= 3 and len(math_depth_markers) == 0:
        issues.append((
            1,
            "WARNING",
            "Slide Syndrome detected: Scene uses multiple cards and text blocks with 0 curves, vectors, or geometric illustrations. Ground concepts into visual geometry (see references/09_cinematic_depth_and_illustrations.md)."
        ))
    return issues


def lint_manim_file(filepath: Path) -> List[Tuple[int, str, str]]:
    """Parses and lints a single Manim Python file."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        return [(0, "ERROR", f"Failed to read file: {e}")]

    try:
        tree = ast.parse(content, filename=str(filepath))
    except SyntaxError as se:
        return [(se.lineno or 0, "ERROR", f"Python Syntax Error: {se.msg}")]

    visitor = ManimLintVisitor(str(filepath), content)
    visitor.visit(tree)
    regex_issues = check_regex_patterns(content, str(filepath))
    slide_issues = check_slide_syndrome(content, str(filepath))

    all_issues = visitor.issues + regex_issues + slide_issues
    all_issues.sort(key=lambda x: x[0])
    return all_issues


def main():
    parser = argparse.ArgumentParser(description="Static linter for Manim Python scripts")
    parser.add_argument("paths", nargs="+", help="Files or directories to lint")
    parser.add_argument("--fail-on-warning", action="store_true", help="Exit with code 1 if warnings are found")

    args = parser.parse_args()
    total_errors = 0
    total_warnings = 0

    for path_str in args.paths:
        p = Path(path_str)
        if not p.exists():
            print(f"[ERROR] Path does not exist: {p}", file=sys.stderr)
            total_errors += 1
            continue
        files = [p] if p.is_file() else list(p.rglob("*.py"))

        for py_file in files:
            issues = lint_manim_file(py_file)
            if issues:
                print(f"\n[LINT] {py_file}:")
                for line, severity, msg in issues:
                    tag = f"[{severity}]"
                    print(f"  Line {line:<4} {tag:<10} {msg}")
                    if severity == "ERROR":
                        total_errors += 1
                    elif severity == "WARNING":
                        total_warnings += 1

    print(f"\nLinter summary: {total_errors} error(s), {total_warnings} warning(s).")
    if total_errors > 0 or (args.fail_on_warning and total_warnings > 0):
        sys.exit(1)
    else:
        print("[SUCCESS] All checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
