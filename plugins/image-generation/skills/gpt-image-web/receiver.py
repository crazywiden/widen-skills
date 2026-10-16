"""Save images POSTed from the ChatGPT tab into OUT_DIR.

Usage: python3 -I receiver.py OUT_DIR [PORT]   (PORT defaults to 8765)
"""
import html
import os
import re
import sys
from email.parser import BytesParser
from email.policy import default
from http.server import BaseHTTPRequestHandler, HTTPServer

OUT = os.path.abspath(sys.argv[1])
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8765
NAME = re.compile(r'^[a-z0-9][a-z0-9-]*\.(png|jpg|webp)$')
MAGIC = {'png': b'\x89PNG', 'jpg': b'\xff\xd8\xff', 'webp': b'RIFF'}
MAX_BYTES = 30_000_000


def free_path(fn):
    base, ext = os.path.splitext(fn)
    path = os.path.join(OUT, fn)
    i = 2
    while os.path.exists(path):
        path = os.path.join(OUT, f'{base}-{i}{ext}')
        i += 1
    return path


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get('Content-Length', 0))
        if n > MAX_BYTES:
            return self.reply(413, 'too large')
        body = self.rfile.read(n)
        msg = BytesParser(policy=default).parsebytes(
            b'Content-Type: ' + self.headers['Content-Type'].encode() + b'\r\n\r\n' + body)
        saved = []
        for part in msg.iter_parts():
            fn = os.path.basename(part.get_filename() or '')
            if not fn:
                continue
            m = NAME.match(fn)
            if not m:
                return self.reply(400, f'bad name {fn}')
            data = part.get_payload(decode=True)
            if not data.startswith(MAGIC[m.group(1)]):
                return self.reply(400, f'bytes do not match extension: {fn}')
            path = free_path(fn)
            with open(path, 'wb') as f:
                f.write(data)
            saved.append(f'{os.path.basename(path)} {len(data)}')
            print('saved', path, len(data), flush=True)
        self.reply(200, 'SAVED ' + '; '.join(saved) if saved else 'NOTHING')

    def do_GET(self):
        self.reply(200, 'receiver up')

    def reply(self, code, text):
        b = f'<!doctype html><title>{html.escape(text)}</title><pre id="r">{html.escape(text)}</pre>'.encode()
        self.send_response(code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)


os.makedirs(OUT, exist_ok=True)
print(f'receiver on http://127.0.0.1:{PORT} -> {OUT}', flush=True)
HTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
