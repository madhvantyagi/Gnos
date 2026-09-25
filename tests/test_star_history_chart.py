"""Keep the README chart tied to GitHub's actual daily star data."""

import importlib.util
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from xml.etree import ElementTree


SCRIPT = Path(__file__).resolve().parents[1] / ".github/scripts/render_star_history.py"
SPEC = importlib.util.spec_from_file_location("render_star_history", SCRIPT)
chart = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(chart)


class StarHistoryChartTests(unittest.TestCase):
    def test_starts_just_before_first_star_and_uses_daily_counts(self):
        history = [
            {"week": int(datetime(2026, 9, 20, tzinfo=timezone.utc).timestamp()),
             "total": 172, "days": [0, 0, 0, 0, 121, 51, 0]},
            {"week": int(datetime(2026, 9, 13, tzinfo=timezone.utc).timestamp()),
             "total": 0, "days": [0] * 7},
        ]

        self.assertEqual(
            chart.daily_series(history, date(2026, 9, 25)),
            [(date(2026, 9, 23), 0),
             (date(2026, 9, 24), 121),
             (date(2026, 9, 25), 172)],
        )

    def test_rendered_chart_is_valid_svg_with_distinct_dates(self):
        series = [(date(2026, 9, 23), 0),
                  (date(2026, 9, 24), 121),
                  (date(2026, 9, 25), 172)]

        svg = chart.render_svg(series, "light")
        root = ElementTree.fromstring(svg)
        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
        background = root.find("{http://www.w3.org/2000/svg}rect")
        self.assertIsNotNone(background)
        self.assertEqual(background.attrib["fill"], "#ffffff")
        self.assertIn("Sep 23", svg)
        self.assertIn("Sep 24", svg)
        self.assertIn("Sep 25", svg)
        self.assertIn("172 recorded stars", svg)
        self.assertNotIn("2026-09-12", svg)
        self.assertNotIn("<script", svg)
        self.assertNotIn("href=", svg)


if __name__ == "__main__":
    unittest.main()
