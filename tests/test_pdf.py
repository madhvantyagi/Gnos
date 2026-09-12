"""PDF output must retain text, support images, and reject unsupported blocks."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / 'skills/pdf/scripts/build_pdf.py'


@unittest.skipUnless(importlib.util.find_spec('reportlab') and importlib.util.find_spec('pypdf'),
                     'Optional PDF tests require reportlab and pypdf')
class PDFTests(unittest.TestCase):
    def test_text_and_local_image_survive_export(self):
        from PIL import Image
        from pypdf import PdfReader
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            Image.new('RGB', (200, 100), 'white').save(folder/'figure.png')
            data = dict(title='Rates & change', sections=[dict(heading='Observe', blocks=[
                dict(type='paragraph', text='Compare x < 2 with x > 2.'),
                dict(type='image', path='figure.png', caption='Figure 1. Test diagram.'),
                dict(type='table', headers=['Before','After'], rows=[['1','2']])])])
            source = folder/'lesson.json'; source.write_text(json.dumps(data))
            result = subprocess.run([sys.executable,str(PDF),str(source),'-o',str(folder/'out.pdf')],
                                    capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            reader = PdfReader(folder/'out.pdf')
            text = '\n'.join(p.extract_text() for p in reader.pages)
            self.assertIn('Compare x < 2 with x > 2.',text)
            self.assertIn('Figure 1. Test diagram.',text)
            self.assertTrue(any(len(p.images) for p in reader.pages))

    def test_unknown_block_does_not_produce_a_partial_pdf(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'bad.json'
            source.write_text(json.dumps(dict(title='Bad',sections=[dict(heading='Test',blocks=[
                dict(type='unsupported',text='Do not drop this silently')])])) )
            output=Path(tmp)/'out.pdf'
            result=subprocess.run([sys.executable,str(PDF),str(source),'-o',str(output)],capture_output=True)
            self.assertNotEqual(result.returncode,0)
            self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
