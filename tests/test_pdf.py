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


@unittest.skipUnless(all(importlib.util.find_spec(p) for p in ('reportlab','pypdf','matplotlib','markdown_it')),
                     'Optional PDF tests require the PDF skill dependencies')
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

    def test_markdown_relative_image_and_math_are_rendered(self):
        from PIL import Image
        from pypdf import PdfReader
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            Image.new('RGB',(100,60),'teal').save(folder/'drawing.png')
            source=folder/'README.md'
            source.write_text('# Local lesson\n\n## Compare\n\nA < B.\n\n'
                              '![A local figure](drawing.png)\n\n```math\nf(x)=x^2\n```\n')
            output=folder/'export/lesson.pdf'
            result=subprocess.run([sys.executable,str(ROOT/'skills/pdf/scripts/markdown_to_pdf.py'),
                                   str(source),'-o',str(output)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            reader=PdfReader(output)
            self.assertIn('A local figure',''.join(p.extract_text() for p in reader.pages))
            self.assertGreaterEqual(sum(len(p.images) for p in reader.pages),2)
            intermediate=json.loads(output.with_suffix('.lesson.json').read_text())
            images=[b for s in intermediate['sections'] for b in s['blocks'] if b['type']=='image']
            self.assertFalse(Path(images[0]['path']).is_absolute())


if __name__ == '__main__':
    unittest.main()
