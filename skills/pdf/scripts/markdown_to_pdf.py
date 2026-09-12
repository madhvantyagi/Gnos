#!/usr/bin/env python3
"""Convert Markdown/README lessons and local images to an editable lesson JSON and PDF."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urlparse

from markdown_it import MarkdownIt
from build_pdf import build


class HTMLContent(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img' and attrs.get('src'):
            self.images.append((attrs['src'], attrs.get('alt', 'Figure')))

    def handle_data(self, data):
        if data.strip():
            self.text.append(data)


def convert(source, output, font_dir=None, remote_images='link'):
    source, output = Path(source).resolve(), Path(output).resolve()
    tokens = MarkdownIt('commonmark', {'html': True}).enable('table').parse(source.read_text())
    data = dict(title=source.stem, sections=[], sources=[])
    current = dict(heading='', blocks=[])
    data['sections'].append(current)
    links = set()
    list_depth = 0
    title_seen = False
    assets = output.parent / (output.stem + '-assets')

    def add_link(title, url):
        if urlparse(url).scheme in ('http', 'https') and url not in links:
            links.add(url)
            data['sources'].append(dict(title=title or url, url=url))

    def image(src, caption):
        parsed = urlparse(src)
        if parsed.scheme in ('http', 'https'):
            if remote_images == 'error':
                raise ValueError(f'Remote image needs a local copy: {src}')
            add_link('Remote image: ' + caption, src)
            current['blocks'].append(dict(type='paragraph', text=f'{caption} (remote image; see source link)'))
            return
        if parsed.scheme or parsed.netloc:
            raise ValueError(f'Unsupported image source: {src}')
        path = (source.parent / unquote(parsed.path)).resolve()
        if not path.is_file():
            raise FileNotFoundError(f'Markdown image not found: {path}')
        current['blocks'].append(dict(type='image', path=str(path), caption=caption or path.name))

    def inline(token):
        text = []
        def flush():
            value = ''.join(text).strip()
            if value:
                current['blocks'].append(dict(type='bullets', items=[value]) if list_depth else dict(type='paragraph', text=value))
            text.clear()
        for child in token.children or []:
            if child.type == 'image':
                flush(); image(child.attrGet('src'), child.content)
            elif child.type in ('text', 'code_inline'):
                text.append(child.content)
            elif child.type in ('softbreak', 'hardbreak'):
                text.append('\n')
            elif child.type == 'link_open':
                add_link(child.attrGet('href'), child.attrGet('href'))
            elif child.type == 'html_inline':
                parsed = HTMLContent(); parsed.feed(child.content)
                for src, caption in parsed.images:
                    flush(); image(src, caption)
                text.extend(parsed.text)
        flush()

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.type == 'heading_open':
            title = tokens[i+1].content
            if token.tag == 'h1' and not title_seen:
                data['title'] = title; title_seen = True
            else:
                current = dict(heading=title, blocks=[])
                data['sections'].append(current)
            i += 3; continue
        if token.type in ('bullet_list_open', 'ordered_list_open'):
            list_depth += 1
        elif token.type in ('bullet_list_close', 'ordered_list_close'):
            list_depth -= 1
        elif token.type == 'inline':
            inline(token)
        elif token.type == 'fence':
            if token.info.strip() in ('math', 'latex'):
                from render_equation import render
                assets.mkdir(parents=True, exist_ok=True)
                path = assets / f'equation-{i}.png'
                render(token.content.strip(), path)
                current['blocks'].append(dict(type='equation', path=str(path), caption=''))
            else:
                current['blocks'].append(dict(type='code', text=token.content.rstrip()))
        elif token.type == 'code_block':
            current['blocks'].append(dict(type='code', text=token.content.rstrip()))
        elif token.type == 'table_open':
            rows = []; row = []
            i += 1
            while tokens[i].type != 'table_close':
                if tokens[i].type == 'tr_open':
                    row = []
                elif tokens[i].type == 'inline':
                    row.append(tokens[i].content)
                elif tokens[i].type == 'tr_close':
                    rows.append(row)
                i += 1
            current['blocks'].append(dict(type='table', headers=rows[0], rows=rows[1:]))
        elif token.type == 'html_block':
            parsed = HTMLContent(); parsed.feed(token.content)
            for src, caption in parsed.images:
                image(src, caption)
            if parsed.text:
                current['blocks'].append(dict(type='paragraph', text=' '.join(parsed.text)))
        elif token.type == 'hr':
            current['blocks'].append(dict(type='paragraph', text=' '))
        i += 1
    data['sections'] = [section for section in data['sections'] if section['blocks']]
    if not data['sections']:
        raise ValueError('Markdown contains no supported lesson content')
    output.parent.mkdir(parents=True, exist_ok=True)
    intermediate = output.with_suffix('.lesson.json')
    intermediate.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    build(intermediate, output, font_dir)
    return output, intermediate


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('markdown', type=Path)
    parser.add_argument('-o', '--output', type=Path, required=True)
    parser.add_argument('--font-dir', type=Path)
    parser.add_argument('--remote-images', choices=('link', 'error'), default='link',
                        help='Remote images become labeled source links, or stop conversion; never silently disappear')
    args = parser.parse_args()
    try:
        for path in convert(args.markdown, args.output, args.font_dir, args.remote_images):
            print(path)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f'Markdown conversion failed: {exc}\n')
