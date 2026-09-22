#!/usr/bin/env python3
"""Serve one local course with persisted exercise attempts and explicit answer reveal."""
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import mimetypes
from pathlib import Path
import re
import secrets
import shutil
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'skills/course-design/scripts'))
from artifact_manifest import read_manifest, ready_artifacts
from course_workspace import read_plan
from portal_interactions import exercise_state, reveal_solution, submit_attempt
from render_viewer import render_rich_text

_API = re.compile(r'/api/exercises/([a-z0-9]+(?:-[a-z0-9]+)*)(?:/(attempts|reveal))?')


class CourseHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send_bytes(self, status, content, mime='application/json; charset=utf-8'):
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, status, data):
        self.send_bytes(status, json.dumps(data, ensure_ascii=False).encode())

    def allowed(self, api=False):
        host = f'127.0.0.1:{self.server.server_port}'
        if self.headers.get('Host') != host:
            self.send_json(403, {'error': 'Open the course through its local viewer URL.'})
            return False
        origin = self.headers.get('Origin')
        if origin is not None and origin != f'http://{host}':
            self.send_json(403, {'error': 'Cross-origin requests are not accepted.'})
            return False
        if api and not secrets.compare_digest(self.headers.get('X-GNOS-Session', ''),
                                               self.server.session_token):
            self.send_json(403, {'error': 'Reload the course page to reconnect.'})
            return False
        return True

    def do_GET(self):
        path = unquote(urlsplit(self.path).path)
        match = _API.fullmatch(path)
        if not self.allowed(api=path.startswith('/api/')):
            return
        try:
            if match and match[2] is None:
                self.send_json(200, exercise_state(self.server.workspace, match[1]))
                return
            if path in ('/', '/portal/', '/portal/index.html'):
                page = (self.server.workspace / 'portal/index.html').read_text()
                meta = f'<meta name="gnos-session" content="{self.server.session_token}">'
                self.send_bytes(200, page.replace('</head>', meta + '</head>', 1).encode(),
                                'text/html; charset=utf-8')
                return
            # Never expose course JSON, lesson answers, submissions, or directory listings.
            manifest = read_manifest(self.server.workspace)
            permitted = {item['location']['path'] for item in ready_artifacts(manifest)
                         if 'path' in item.get('location', {})}
            relative = path.removeprefix('/')
            if relative not in permitted:
                self.send_json(404, {'error': 'Not found.'})
                return
            target = self.server.workspace / relative
            if (not target.is_file() or target.is_symlink()
                    or any(parent.is_symlink() for parent in target.parents)
                    or not target.resolve().is_relative_to(self.server.workspace)):
                self.send_json(404, {'error': 'Not found.'})
                return
            self.send_response(200)
            self.send_header('Content-Type', mimetypes.guess_type(target.name)[0] or 'application/octet-stream')
            self.send_header('Content-Length', str(target.stat().st_size))
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            with target.open('rb') as source:
                shutil.copyfileobj(source, self.wfile)
        except (ValueError, OSError) as exc:
            self.send_json(400, {'error': str(exc)})

    def do_POST(self):
        if not self.allowed(api=True):
            return
        match = _API.fullmatch(urlsplit(self.path).path)
        if not match or match[2] not in ('attempts', 'reveal'):
            self.send_json(404, {'error': 'Not found.'})
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 250_000:
                raise ValueError('Request body is missing or too large.')
            if self.headers.get_content_type() != 'application/json':
                raise ValueError('Expected a JSON request.')
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ValueError('Expected a JSON object.')
            if match[2] == 'attempts':
                result = submit_attempt(self.server.workspace, match[1], payload.get('response'),
                                        payload.get('attempt_id'))
                self.send_json(200, {key: result[key] for key in (
                    'id', 'exercise_id', 'response', 'submitted_at', 'status', 'feedback')})
            else:
                result = reveal_solution(self.server.workspace, match[1], payload.get('attempt_id'))
                result['html'] = render_rich_text(result['solution'])
                self.send_json(200, result)
        except (ValueError, OSError) as exc:
            self.send_json(400, {'error': str(exc)})


def create_server(workspace, port=8080):
    workspace = Path(workspace).resolve()
    read_plan(workspace)
    server = HTTPServer(('127.0.0.1', port), CourseHandler)
    server.workspace = workspace
    server.session_token = secrets.token_urlsafe(32)
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('workspace', type=Path)
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    with create_server(args.workspace, args.port) as server:
        print(f'Course viewer: http://127.0.0.1:{server.server_port}/portal/', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
