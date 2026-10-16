"""Browser-controller feedback without requiring a browser installation."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ExerciseControlTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), 'Node.js is unavailable')
    def test_save_and_review_feedback_is_visible(self):
        result = subprocess.run(['node', str(ROOT / 'tests/exercise_controls.cjs'),
            str(ROOT / 'skills/course-viewer/scripts/exercise_controls.js')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
