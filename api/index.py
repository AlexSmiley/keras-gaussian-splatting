"""Minimal Vercel serverless entrypoint for the Keras Gaussian Splatting project.

The training pipeline is a CLI/library workload; this function intentionally
provides a lightweight HTTP health endpoint and does not import TensorFlow.
"""

import json
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    """Vercel Python runtime entrypoint exposed at GET /api."""

    def do_GET(self):
        body = json.dumps(
            {
                "status": "ok",
                "service": "keras-gaussian-splatting",
                "runtime": "vercel-python",
                "message": (
                    "The HTTP entrypoint is running. 3D Gaussian Splatting training "
                    "is currently provided by the local CLI, not this serverless API."
                ),
            }
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        body = json.dumps(
            {
                "status": "not_implemented",
                "message": (
                    "Training and rendering endpoints are not implemented in this "
                    "serverless entrypoint."
                ),
            }
        ).encode("utf-8")
        self.send_response(501)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
