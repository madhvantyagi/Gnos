#!/usr/bin/env python3
"""Render a structured GNOS lesson with embedded fonts and local figures."""
import argparse
from importlib.util import find_spec
import json
import os
from pathlib import Path
import tempfile
from urllib.parse import urlparse
from xml.sax.saxutils import escape

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                               KeepTogether, PageBreak, Preformatted, Table, TableStyle)

FONT_FILES = {'Body': 'DejaVuSerif.ttf', 'Heading': 'DejaVuSans-Bold.ttf',
              'Sans': 'DejaVuSans.ttf', 'Mono': 'DejaVuSansMono.ttf'}
INK = colors.HexColor('#172c35')
ACCENT = colors.HexColor('#156d70')
WIDTH = A4[0] - 108


def register_fonts(directory=None):
    candidates = [Path(directory)] if directory else []
    if not directory:
        candidates += [Path('/usr/share/fonts/truetype/dejavu'), Path('/Library/Fonts')]
        spec = find_spec('matplotlib')
        if spec and spec.origin:
            candidates.append(Path(spec.origin).parent / 'mpl-data/fonts/ttf')
    folder = next((p for p in candidates if all((p / f).exists() for f in FONT_FILES.values())), None)
    if folder is None:
        raise ValueError('DejaVu font family not found. Supply --font-dir or install matplotlib for its bundled fonts.')
    for name, filename in FONT_FILES.items():
        pdfmetrics.registerFont(TTFont(name, str(folder / filename)))


def checked_text(value, font='Body'):
    if not isinstance(value, str):
        raise ValueError('Text fields must be strings')
    supported = pdfmetrics.getFont(font).face.charToGlyph
    missing = sorted({c for c in value if not c.isspace() and ord(c) not in supported})
    if missing:
        raise ValueError(f'Unsupported glyphs in {font}: {missing}; render complex equations as images')
    return escape(value).replace('\n', '<br/>')


def styles():
    return {
        'title': ParagraphStyle('Title', fontName='Heading', fontSize=26, leading=32,
                                textColor=INK, spaceAfter=12),
        'subtitle': ParagraphStyle('Subtitle', fontName='Sans', fontSize=11, leading=17,
                                   textColor=ACCENT, spaceAfter=24),
        'heading': ParagraphStyle('Heading', fontName='Heading', fontSize=14, leading=19,
                                  textColor=ACCENT, spaceBefore=17, spaceAfter=9, keepWithNext=True),
        'body': ParagraphStyle('Body', fontName='Body', fontSize=11, leading=17,
                               textColor=INK, spaceAfter=10),
        'caption': ParagraphStyle('Caption', fontName='Sans', fontSize=9, leading=13,
                                  textColor=INK, spaceBefore=6, spaceAfter=13),
        'cell': ParagraphStyle('Cell', fontName='Sans', fontSize=9, leading=13, textColor=INK),
        'code': ParagraphStyle('Code', fontName='Mono', fontSize=9, leading=13,
                               textColor=INK, spaceAfter=12),
    }


def build(source, output, font_dir=None):
    source, output = Path(source), Path(output)
    data = json.loads(source.read_text())
    if not isinstance(data, dict) or not isinstance(data.get('title'), str) or not data['title'].strip():
        raise ValueError('Lesson requires a title')
    if not isinstance(data.get('sections'), list) or not data['sections']:
        raise ValueError('Lesson requires sections')
    register_fonts(font_dir)
    s = styles()
    story = [Paragraph(checked_text(data['title'], 'Heading'), s['title'])]
    if data.get('subtitle'):
        story.append(Paragraph(checked_text(data['subtitle'], 'Sans'), s['subtitle']))
    for section in data['sections']:
        if not isinstance(section, dict) or not isinstance(section.get('blocks'), list) or not section['blocks']:
            raise ValueError('Each section requires nonempty blocks')
        if section.get('heading'):
            story.append(Paragraph(checked_text(section['heading'], 'Heading'), s['heading']))
        for block in section['blocks']:
            kind = block.get('type')
            if kind == 'paragraph':
                story.append(Paragraph(checked_text(block['text']), s['body']))
            elif kind == 'bullets':
                for item in block['items']:
                    story.append(Paragraph('• ' + checked_text(item), s['body']))
            elif kind in ('image', 'equation'):
                path = (source.parent / block['path']).resolve()
                with PILImage.open(path) as image:
                    w, h = image.size
                max_width = min(float(block.get('width', WIDTH)), WIDTH)
                if max_width <= 0:
                    raise ValueError('Image width must be positive')
                scale = min(max_width / w, 360 / h)
                if kind == 'equation':
                    scale = min(scale, 72 / 220)  # Equation helper exports at 220 DPI.
                picture = Image(str(path), width=w * scale, height=h * scale)
                picture.hAlign = 'LEFT'
                caption = Paragraph(checked_text(block['caption'], 'Sans'), s['caption'])
                story.append(KeepTogether([picture, caption]))
            elif kind == 'table':
                headers, rows = block['headers'], block['rows']
                if not headers or any(len(row) != len(headers) for row in rows):
                    raise ValueError('Table rows must match nonempty headers')
                cells = [[Paragraph(checked_text(str(cell), 'Sans'), s['cell']) for cell in row]
                         for row in [headers] + rows]
                table = Table(cells, colWidths=[WIDTH / len(headers)] * len(headers), repeatRows=1,
                              hAlign='LEFT')
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eaf3f1')),
                    ('LINEBELOW', (0, 0), (-1, 0), 0.7, ACCENT),
                    ('LINEBELOW', (0, 1), (-1, -1), 0.3, colors.HexColor('#d8e2e2')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 9),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 9),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                story += [KeepTogether([table]) if len(rows) <= 8 else table, Spacer(1, 12)]
            elif kind == 'code':
                text = block['text']
                checked_text(text, 'Mono')
                if any(pdfmetrics.stringWidth(line, 'Mono', 9) > WIDTH for line in text.splitlines()):
                    raise ValueError('Code line exceeds page width; wrap it in the lesson source')
                story.append(Preformatted(text, s['code']))
            elif kind == 'pagebreak':
                story.append(PageBreak())
            else:
                raise ValueError(f'Unknown lesson block: {kind!r}')
    if data.get('sources'):
        story.append(Paragraph('Sources and further reading', s['heading']))
        for item in data['sources']:
            url = item['url']
            if urlparse(url).scheme not in ('http', 'https') or not urlparse(url).netloc:
                raise ValueError('Source links must be HTTP(S) URLs')
            label = checked_text(item['title'], 'Sans')
            safe_url = escape(url, {'"': '&quot;'})
            story.append(Paragraph(f'<link href="{safe_url}" color="#156d70">{label}</link>', s['caption']))

    def furniture(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor('#d8e2e2'))
        canvas.line(54, 44, A4[0]-54, 44)
        canvas.setFont('Sans', 8)
        canvas.setFillColor(INK)
        canvas.drawString(54, 30, 'GNOS  /  ' + data['title'][:60])
        canvas.drawRightString(A4[0]-54, 30, str(doc.page))
        canvas.restoreState()

    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(suffix='.pdf', dir=output.parent)
    os.close(fd)
    try:
        doc = SimpleDocTemplate(temporary, pagesize=A4, rightMargin=54, leftMargin=54,
                                topMargin=48, bottomMargin=62, title=data['title'], author='GNOS')
        doc.build(story, onFirstPage=furniture, onLaterPages=furniture)
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lesson', type=Path)
    parser.add_argument('-o', '--output', type=Path, required=True)
    parser.add_argument('--font-dir', type=Path)
    args = parser.parse_args()
    try:
        print(build(args.lesson, args.output, args.font_dir))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f'PDF build failed: {exc}\n')


if __name__ == '__main__':
    main()
