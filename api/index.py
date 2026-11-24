"""Minimal Vercel serverless entrypoint for the Keras Gaussian Splatting project.

The training pipeline is a CLI/library workload; this function intentionally
provides a lightweight HTTP health endpoint and does not import TensorFlow.
"""

import json
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    """Vercel Python runtime entrypoint."""

    def do_GET(self):
        path = self.path.split("?", 1)[0].rstrip("/") or "/"

        if path not in ("/api", "/api/health"):
            self._json_response(
                404,
                {"status": "not_found", "message": "Try GET /api or GET /api/health."},
            )
            return

        self._json_response(
            200,
            {
                "status": "ok",
                "service": "keras-gaussian-splatting",
                "runtime": "vercel-python",
                "message": (
                    "HTTP entrypoint is running. 3D Gaussian Splatting training "
                    "is currently provided by the local CLI, not this serverless API."
                ),
            },
        )

    def do_POST(self):
        self._json_response(
            501,
            {
                "status": "not_implemented",
                "message": (
                    "Training and rendering endpoints are not implemented in this "
                    "serverless entrypoint."
                ),
            },
        )

    def _json_response(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)
