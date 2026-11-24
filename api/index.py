"""Lightweight, authenticated upstream proxy; no ML imports."""
import json
import os
import re
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlsplit, parse_qs
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

class handler(BaseHTTPRequestHandler):
    def respond(self, status, payload):
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self.proxy("GET")

    def do_POST(self):
        self.proxy("POST")

    def proxy(self, method):
        path = parse_qs(urlsplit(self.path).query).get("path", [""])[0]
        if not path and method == "GET":
            return self.respond(200, {"status":"ok","worker_configured":bool(os.getenv("WORKER_URL") and os.getenv("WORKER_TOKEN"))})
        allowed = (method == "POST" and path == "/jobs") or (method == "GET" and re.fullmatch(r"/jobs/[a-f0-9]{32}(?:/scene\.(?:ply|splat))?", path))
        if not allowed:
            return self.respond(404, {"message":"Unknown endpoint"})
        base, token = os.getenv("WORKER_URL"), os.getenv("WORKER_TOKEN")
        if not base or not token:
            return self.respond(503, {"message":"Reconstruction worker is not configured"})
        data = None
        if method == "POST":
            # Optional deployment-wide gate. Public deployments require additional abuse protection.
            gate = os.getenv("GENERATION_KEY")
            if not gate or self.headers.get("X-Generation-Key") != gate:
                return self.respond(403, {"message":"Generation requires a valid access key"})
            try:
                n = int(self.headers.get("Content-Length", "0"))
                if not 0 < n <= 4096: raise ValueError()
                data = self.rfile.read(n)
            except ValueError:
                return self.respond(400, {"message":"Invalid request size"})
        req = Request(base.rstrip("/") + path, data=data, method=method, headers={"X-Worker-Token":token,"Content-Type":"application/json"})
        try:
            upstream = urlopen(req, timeout=25)
        except HTTPError as exc:
            upstream = exc
        except (URLError, TimeoutError):
            return self.respond(502, {"message":"Worker unavailable"})
        with upstream:
            self.send_response(upstream.status)
            for key in ("Content-Type", "Content-Disposition", "Content-Length"):
                if upstream.headers.get(key): self.send_header(key, upstream.headers[key])
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            while True:
                chunk = upstream.read(65536)
                if not chunk: break
                self.wfile.write(chunk)
