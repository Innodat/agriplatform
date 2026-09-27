"""Serve only assembled artifacts, applying the generated Netlify SPA rules."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]/'public-release'
if not (ROOT/'index.html').is_file() or not (ROOT/'_redirects').is_file():raise SystemExit('Build public-release before the artifact browser test')
RULES=[line.split() for line in (ROOT/'_redirects').read_text().splitlines()]
class Handler(SimpleHTTPRequestHandler):
 def send_head(self):
  requested=urlsplit(self.path).path;file=ROOT/requested.lstrip('/')
  if not file.is_file():
   for pattern,target,status in RULES:
    if requested==pattern or pattern.endswith('*') and requested.startswith(pattern[:-1]):
     if status=='301':self.send_response(301);self.send_header('Location',target);self.end_headers();return None
     self.path=target;break
  return super().send_head()
 def log_message(self,*args):pass
ThreadingHTTPServer(('127.0.0.1',5183),partial(Handler,directory=str(ROOT))).serve_forever()
