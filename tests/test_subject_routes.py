"""Subject discovery returns inspectable candidates, never a keyword decision."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/subject/scripts/subject_catalog.py"


class SubjectRouteTests(unittest.TestCase):
    def load_catalog(self):
        self.assertTrue(SCRIPT.is_file(), "Subject discovery is not implemented")
        spec = importlib.util.spec_from_file_location("subject_catalog_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_catalog_covers_existing_guides_and_every_subfield_section(self):
        catalog = self.load_catalog()
        data = catalog.load_catalog()
        guides = {path.stem: path for path in (ROOT / "skills/subject/subjects").glob("*.md")}
        self.assertEqual(set(data), set(guides))
        for subject, path in guides.items():
            with self.subTest(subject=subject):
                sections = [line[4:] for line in path.read_text().splitlines()
                            if line.startswith("### ")]
                self.assertEqual([entry["section"] for entry in data[subject]["subfields"]], sections)
                self.assertEqual(data[subject]["guide"], str(path.relative_to(ROOT)))
        catalog.validate_catalog(data)

    def test_ambiguous_names_keep_candidates_from_both_fields(self):
        catalog = self.load_catalog()
        for query, expected in (("thermodynamics", {"physics", "chemical-engineering"}),
                                ("machine learning", {"artificial-intelligence", "computer-science"}),
                                ("research methods", {"psychology", "political-science"})):
            with self.subTest(query=query):
                result = catalog.search(query)
                self.assertTrue(expected.issubset({row["subject"] for row in result["candidates"]}))
                self.assertIsNone(result["selected_subject"])

    def test_subfield_uses_stable_id_and_checks_subject_ownership(self):
        catalog = self.load_catalog()
        result = catalog.resolve_subfield("math.statistics-inference", "math")
        self.assertEqual(result["section"], "Statistics and inference")
        with self.assertRaisesRegex(ValueError, "belongs to math"):
            catalog.resolve_subfield("math.statistics-inference", "biology")
        with self.assertRaisesRegex(ValueError, "Unknown subfield"):
            catalog.resolve_subfield("differential privacy")

    def test_unknown_specialty_does_not_fabricate_coverage(self):
        result = self.load_catalog().search("algebraic quantum field theory")
        self.assertEqual(result["candidates"], [])
        self.assertTrue(result["needs_source_inspection"])
        self.assertIsNone(result["selected_subject"])

    def test_resource_lookup_accepts_every_current_subject_without_inventing_sources(self):
        script = ROOT / "skills/subject/scripts/resources.py"
        for path in (ROOT / "skills/subject/subjects").glob("*.md"):
            with self.subTest(subject=path.stem):
                result = subprocess.run([sys.executable, str(script), "--subject", path.stem],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(all(path.stem in row["subjects"] for row in json.loads(result.stdout)))


if __name__ == "__main__":
    unittest.main()
