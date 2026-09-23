#!/usr/bin/env python3
"""
linter.py — Static AST & Pattern Linter for Manim Community Code

Catches 20+ common AI-generated bugs, deprecated APIs, unescaped LaTeX,
and audio-sync pitfalls before spending GPU/CPU cycles on rendering.

Also validates storyboard JSON against the pedagogical contract in
templates/storyboard_schema.json (concept ID, prerequisite, success check,
per-scene concept target, and per-cue narration, visible objects, and change)
and checks CuePlayer timeline usage in scene code.
"""

import argparse
import ast
import json
import math
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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

# Mobject factories that are expensive to rebuild every frame inside an updater.
TEX_FACTORIES = {"MathTex", "Tex", "Text", "DecimalNumber", "Integer"}

SCENE_ID_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]*\Z")
CUE_ID_RE = re.compile(r"[A-Za-z0-9_-]+\Z")


def _func_name(node: ast.Call) -> Optional[str]:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def _contains_tex_factory(node: ast.AST) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Call) and _func_name(child) in TEX_FACTORIES:
            return True
    return False


def _run_time_keyword(node: ast.Call) -> Optional[ast.keyword]:
    for kw in node.keywords:
        if kw.arg == "run_time":
            return kw
    return None


class ManimLintVisitor(ast.NodeVisitor):
    def __init__(self, filename: str, content: str):
        self.filename = filename
        self.content = content
        self.lines = content.splitlines()
        self.issues: List[Tuple[int, str, str]] = []  # (line, severity, message)
        self.cue_player_lineno: Optional[int] = None
        self.cue_plays: Dict[str, int] = {}
        self.finish_lineno: Optional[int] = None
        self.direct_play_linenos: List[int] = []
        self.add_updater_lineno: Optional[int] = None
        self.has_clear_updaters = False
        self._always_redraw_lambda_lines = set()

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

    def visit_Lambda(self, node: ast.Lambda):
        # Rebuilding text/Tex glyphs inside a per-frame callback flickers and is slow.
        # (Lambdas passed to always_redraw are reported at the always_redraw call site.)
        if node.lineno not in self._always_redraw_lambda_lines and _contains_tex_factory(node.body):
            self.add_issue(
                node.lineno,
                "WARNING",
                "MathTex/Tex/Text built inside a lambda runs every frame. Prefer ValueTracker plus DecimalNumber.set_value() (see template_calculus_plot.py)."
            )
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Flag updater-style defs (mob, dt) that rebuild glyphs each tick.
        arg_names = [a.arg for a in node.args.args]
        if len(arg_names) >= 2 and "dt" in arg_names[1:]:
            for child in ast.walk(node):
                if isinstance(child, ast.Call) and _func_name(child) in TEX_FACTORIES:
                    self.add_issue(
                        child.lineno,
                        "WARNING",
                        f"Updater '{node.name}' rebuilds '{_func_name(child)}' every frame. Update values in place instead of reconstructing glyphs."
                    )
                    break
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # Check for deprecated API names
        func_name = _func_name(node)

        if func_name and func_name in DEPRECATED_APIS:
            self.add_issue(node.lineno, "WARNING", f"'{func_name}' is deprecated: {DEPRECATED_APIS[func_name]}")

        # CuePlayer construction: CuePlayer(scene, manifest_path, scene_id).
        if func_name == "CuePlayer":
            if self.cue_player_lineno is None:
                self.cue_player_lineno = node.lineno
            if len(node.args) + len(node.keywords) < 3:
                self.add_issue(
                    node.lineno,
                    "ERROR",
                    "CuePlayer must be constructed with (scene, manifest_path, scene_id), e.g. CuePlayer(self, manifest, 'MyScene')."
                )
            else:
                scene_id_node: Optional[ast.AST] = None
                if len(node.args) >= 3:
                    scene_id_node = node.args[2]
                else:
                    for kw in node.keywords:
                        if kw.arg == "scene_id":
                            scene_id_node = kw.value
                if not (
                    isinstance(scene_id_node, ast.Constant)
                    and isinstance(scene_id_node.value, str)
                    and scene_id_node.value.strip()
                ):
                    self.add_issue(
                        node.lineno,
                        "WARNING",
                        "CuePlayer scene ID should be a string literal matching the Scene class so cue coverage can be checked."
                    )

        # play(): distinguish Scene.play (self.play) from CuePlayer.play (player.play).
        if func_name == "play" and isinstance(node.func, ast.Attribute):
            receiver = node.func.value
            if isinstance(receiver, ast.Name) and receiver.id == "self":
                self.direct_play_linenos.append(node.lineno)
            else:
                cue_node: Optional[ast.AST] = None
                if node.args:
                    cue_node = node.args[0]
                else:
                    for kw in node.keywords:
                        if kw.arg == "cue_id":
                            cue_node = kw.value
                if cue_node is None:
                    self.add_issue(
                        node.lineno,
                        "ERROR",
                        "CuePlayer.play requires a cue_id as its first argument; each cue plays exactly once."
                    )
                elif isinstance(cue_node, ast.Constant) and isinstance(cue_node.value, str) and cue_node.value:
                    cue_id = cue_node.value
                    if cue_id in self.cue_plays:
                        self.add_issue(
                            node.lineno,
                            "ERROR",
                            f"Cue '{cue_id}' is played twice (first at line {self.cue_plays[cue_id]}). CuePlayer rejects cue reuse."
                        )
                    else:
                        self.cue_plays[cue_id] = node.lineno
                else:
                    self.add_issue(
                        node.lineno,
                        "WARNING",
                        "CuePlayer.play cue_id should be a string literal so cue reuse and coverage can be checked statically."
                    )
                run_time_kw = _run_time_keyword(node)
                if run_time_kw is not None:
                    value = run_time_kw.value
                    if isinstance(value, ast.Constant) and type(value.value) in (int, float):
                        if not math.isfinite(value.value) or value.value <= 0:
                            self.add_issue(
                                node.lineno,
                                "ERROR",
                                "CuePlayer.play run_time must be positive and fit inside its narration cue."
                            )
                    elif isinstance(value, ast.UnaryOp) and isinstance(value.op, ast.USub):
                        self.add_issue(
                            node.lineno,
                            "ERROR",
                            "CuePlayer.play run_time must be positive and fit inside its narration cue."
                        )

        # finish(): required after all cues to catch unplayed cues and export subtitles.
        if func_name == "finish" and isinstance(node.func, ast.Attribute):
            if self.finish_lineno is None:
                self.finish_lineno = node.lineno
            if not node.args and not any(kw.arg == "output_prefix" for kw in node.keywords):
                self.add_issue(
                    node.lineno,
                    "ERROR",
                    "CuePlayer.finish requires an output prefix to export timing JSON and SRT subtitles."
                )

        # Updater lifecycle tracking.
        if func_name == "add_updater":
            if self.add_updater_lineno is None:
                self.add_updater_lineno = node.lineno
        if func_name in ("clear_updaters", "clear_all_updaters"):
            self.has_clear_updaters = True

        # always_redraw rebuilding glyphs every frame.
        if func_name == "always_redraw":
            for arg in node.args:
                for child in ast.walk(arg):
                    if isinstance(child, ast.Lambda):
                        self._always_redraw_lambda_lines.add(child.lineno)
                if _contains_tex_factory(arg):
                    self.add_issue(
                        node.lineno,
                        "WARNING",
                        "always_redraw rebuilds MathTex/Tex/Text every frame. Prefer ValueTracker plus DecimalNumber.set_value() and keep the compared quantity visible."
                    )
                    break

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


def check_cue_timeline(visitor: ManimLintVisitor) -> List[Tuple[int, str, str]]:
    """Cross-checks CuePlayer construction, per-cue play, finish, and updater cleanup."""
    issues = []
    if visitor.cue_player_lineno is not None:
        if not visitor.cue_plays:
            issues.append((
                visitor.cue_player_lineno,
                "WARNING",
                "CuePlayer is constructed but play() is never called. Play each narration cue exactly once."
            ))
        if visitor.finish_lineno is None:
            issues.append((
                visitor.cue_player_lineno,
                "ERROR",
                "CuePlayer is constructed but finish() is never called. finish() rejects unplayed cues and exports cue timings to SRT and timing JSON."
            ))
        for lineno in visitor.direct_play_linenos:
            issues.append((
                lineno,
                "WARNING",
                "Direct self.play() bypasses CuePlayer timing and can drift from narration. Route cue choreography through player.play(cue_id, ...) so the animation fits inside its cue."
            ))
    if visitor.add_updater_lineno is not None and not visitor.has_clear_updaters:
        issues.append((
            visitor.add_updater_lineno,
            "WARNING",
            "add_updater() without clear_updaters(): updaters keep firing after the section. Call mobject.clear_updaters() before the next section or when objects leave the scene."
        ))
    return issues


def check_regex_patterns(content: str, filename: str) -> List[Tuple[int, str, str]]:
    """Runs regex checks on code lines for syntax traps."""
    issues = []
    lines = content.splitlines()

    direction_pair = re.compile(
        r"(RIGHT|LEFT|UP|DOWN)\s*\*\s*([+-]?\d+(?:\.\d+)?)"
        r"|([+-]?\d+(?:\.\d+)?)\s*\*\s*(RIGHT|LEFT|UP|DOWN)"
    )
    move_to_literal = re.compile(
        r"\.move_to\(\s*\[?\s*([+-]?\d+(?:\.\d+)?)\s*,\s*([+-]?\d+(?:\.\d+)?)"
    )

    for idx, line in enumerate(lines, 1):
        # Check for coordinates placed far outside the standard 16:9 frame.
        for match in direction_pair.finditer(line):
            if match.group(1):
                dir_name, val = match.group(1), float(match.group(2))
            else:
                val, dir_name = float(match.group(3)), match.group(4)
            if dir_name in ("RIGHT", "LEFT") and abs(val) > FRAME_X_MAX + 1:
                issues.append((idx, "WARNING", f"Horizontal shift magnitude {val} exceeds typical screen frame limit ({FRAME_X_MAX})."))
            elif dir_name in ("UP", "DOWN") and abs(val) > FRAME_Y_MAX + 1:
                issues.append((idx, "WARNING", f"Vertical shift magnitude {val} exceeds typical screen frame limit ({FRAME_Y_MAX})."))

        move_match = move_to_literal.search(line)
        if move_match:
            x_val, y_val = float(move_match.group(1)), float(move_match.group(2))
            if abs(x_val) > FRAME_X_MAX or abs(y_val) > FRAME_Y_MAX:
                issues.append((idx, "WARNING", f"move_to([{x_val}, {y_val}]) places a label outside the 16:9 frame (x in [-{FRAME_X_MAX}, {FRAME_X_MAX}], y in [-{FRAME_Y_MAX}, {FRAME_Y_MAX}]). Keep labels in frame at actual playback size."))

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


def _is_nonempty_str(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def lint_storyboard_file(filepath: Path) -> List[Tuple[int, str, str]]:
    """Validates a storyboard JSON instance against the pedagogical contract.

    Mirrors scripts/voice_synthesizer.py ID, cue, and duration rules and adds
    the schema's teaching fields: concept_id, prerequisite, success check,
    per-scene concept target, and per-cue visible objects plus change.
    """
    try:
        data = json.loads(filepath.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [(exc.lineno or 0, "ERROR", f"Invalid storyboard JSON: {exc.msg}")]
    except Exception as e:
        return [(0, "ERROR", f"Failed to read file: {e}")]

    issues: List[Tuple[int, str, str]] = []
    if not isinstance(data, dict):
        return [(0, "ERROR", "Storyboard must be a JSON object with title, concept_id, prerequisite, success_check, and scenes.")]
    if not _is_nonempty_str(data.get("title")):
        issues.append((0, "ERROR", "Storyboard requires a nonempty title."))
    for field in ("concept_id", "prerequisite", "success_check"):
        if not _is_nonempty_str(data.get(field)):
            issues.append((0, "ERROR", f"Storyboard requires a nonempty '{field}' (see SKILL.md: state the concept ID, prerequisite assumption, and one observable success check)."))
    if data.get("aspect_ratio", "16:9") not in ("16:9", "9:16", "1:1"):
        issues.append((0, "ERROR", "Unsupported aspect ratio; use '16:9', '9:16', or '1:1'."))

    scenes = data.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        issues.append((0, "ERROR", "Storyboard requires a nonempty 'scenes' list."))
        return sorted(issues, key=lambda x: x[0])

    seen_scenes = set()
    for scene in scenes:
        if not isinstance(scene, dict):
            issues.append((0, "ERROR", "Each scene must be an object with id, title, concept_target, and narration_cues."))
            continue
        scene_id = scene.get("id", "")
        if not isinstance(scene_id, str) or not SCENE_ID_RE.match(scene_id):
            issues.append((0, "ERROR", "Scene IDs must be unique, safe Python class names (e.g. 'GradientStep')."))
        elif scene_id in seen_scenes:
            issues.append((0, "ERROR", f"Duplicate scene ID: {scene_id}"))
        else:
            seen_scenes.add(scene_id)
        label = scene_id if isinstance(scene_id, str) and scene_id else "<scene>"
        if not _is_nonempty_str(scene.get("title")):
            issues.append((0, "ERROR", f"{label}: scene title must be nonempty."))
        if not _is_nonempty_str(scene.get("concept_target")):
            issues.append((0, "ERROR", f"{label}: each scene needs one concept target (single core insight)."))
        cues = scene.get("narration_cues")
        if not isinstance(cues, list) or not cues:
            issues.append((0, "ERROR", f"{label}: narration_cues must be a nonempty list with exact narration per cue."))
            continue
        seen_cues = set()
        for cue in cues:
            if not isinstance(cue, dict):
                issues.append((0, "ERROR", f"{label}: each cue must be an object with cue_id, text, visible_objects, and change."))
                continue
            cue_id = cue.get("cue_id", "")
            if not isinstance(cue_id, str) or not CUE_ID_RE.match(cue_id):
                issues.append((0, "ERROR", f"{label}: cue IDs may use letters, digits, underscore, hyphen (got {cue_id!r})."))
                cue_tag = f"{label}/<cue>"
            elif cue_id in seen_cues:
                issues.append((0, "ERROR", f"Duplicate cue ID: {label}/{cue_id}; each cue plays exactly once."))
                cue_tag = f"{label}/{cue_id}"
            else:
                seen_cues.add(cue_id)
                cue_tag = f"{label}/{cue_id}"
            if not _is_nonempty_str(cue.get("text")):
                issues.append((0, "ERROR", f"{cue_tag}: narration text must be nonempty exact words."))
            visible = cue.get("visible_objects")
            if (
                not isinstance(visible, list)
                or not visible
                or not all(_is_nonempty_str(item) for item in visible)
            ):
                issues.append((0, "ERROR", f"{cue_tag}: visible_objects must list at least one Mobject."))
            if not _is_nonempty_str(cue.get("change")):
                issues.append((0, "ERROR", f"{cue_tag}: each cue must name the change it reveals."))
            for key in ("duration", "pause_after"):
                if key in cue:
                    value = cue[key]
                    if (
                        type(value) not in (int, float)
                        or not math.isfinite(value)
                        or value < 0
                        or (key == "duration" and value == 0)
                    ):
                        issues.append((0, "ERROR", f"{cue_tag}: {key} must be finite and {'positive' if key == 'duration' else 'nonnegative'}."))
    issues.sort(key=lambda x: x[0])
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
    cue_issues = check_cue_timeline(visitor)

    all_issues = visitor.issues + regex_issues + slide_issues + cue_issues
    all_issues.sort(key=lambda x: x[0])
    return all_issues


def main():
    parser = argparse.ArgumentParser(description="Static linter for Manim Python scripts and storyboard JSON")
    parser.add_argument("paths", nargs="+", help="Files or directories to lint (.py scenes; .json storyboards when passed as files)")
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
        if p.is_file():
            files = [p]
        else:
            files = list(p.rglob("*.py"))

        for target in files:
            if target.suffix == ".json":
                issues = lint_storyboard_file(target)
            elif target.suffix == ".py":
                issues = lint_manim_file(target)
            else:
                continue
            if issues:
                print(f"\n[LINT] {target}:")
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
