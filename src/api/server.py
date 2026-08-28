"""High-performance multi-threaded HTTP server hosting the Digital Twin REST API and Static Web GUI."""

from __future__ import annotations

import json
import mimetypes
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs

from src.api.handlers import APIRequestHandler


class DigitalTwinHTTPHandler(BaseHTTPRequestHandler):
    """Handles REST API calls and serves modern static Web GUI assets."""

    server_version = "DigitalTwinHTTP/1.0"

    def _set_cors_headers(self, content_type: str = "application/json") -> None:
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == "/api/status":
            res = APIRequestHandler.handle_status()
            self._send_json(200, res)
            return

        if path == "/api/feedstocks":
            res = APIRequestHandler.handle_feedstocks()
            self._send_json(200, res)
            return

        # Serve static assets
        self._serve_static_file(path)

    def do_POST(self) -> None:
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # Read JSON body
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len) if content_len > 0 else b"{}"

        try:
            data = json.loads(post_body.decode("utf-8")) if post_body else {}
        except Exception:
            data = {}

        try:
            if path == "/api/simulate":
                res = APIRequestHandler.handle_simulate(data)
                self._send_json(200, res)
            elif path == "/api/soft-sensors":
                res = APIRequestHandler.handle_soft_sensors(data)
                self._send_json(200, res)
            elif path == "/api/optimize":
                res = APIRequestHandler.handle_optimize(data)
                self._send_json(200, res)
            elif path == "/api/diagnostics":
                res = APIRequestHandler.handle_diagnostics(data)
                self._send_json(200, res)
            elif path == "/api/maintenance":
                res = APIRequestHandler.handle_maintenance(data)
                self._send_json(200, res)
            else:
                self._send_json(404, {"error": f"Endpoint not found: {path}"})
        except Exception as exc:
            self._send_json(500, {"error": str(exc), "endpoint": path})

    def _send_json(self, status_code: int, payload: Dict[str, Any]) -> None:
        raw_bytes = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status_code)
        self._set_cors_headers("application/json")
        self.send_header("Content-Length", str(len(raw_bytes)))
        self.end_headers()
        self.wfile.write(raw_bytes)

    def _serve_static_file(self, req_path: str) -> None:
        static_dir = Path(__file__).resolve().parent.parent / "web" / "static"
        clean_path = req_path.lstrip("/")
        if not clean_path or clean_path == "":
            target_file = static_dir / "index.html"
        else:
            target_file = static_dir / clean_path

        if not target_file.is_file():
            # Fallback to index.html for SPA routing
            target_file = static_dir / "index.html"

        if not target_file.is_file():
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 - Not Found")
            return

        mime_type, _ = mimetypes.guess_type(str(target_file))
        if mime_type is None:
            mime_type = "application/octet-stream"

        with open(target_file, "rb") as f:
            content = f.read()

        self.send_response(200)
        self._set_cors_headers(mime_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format: str, *args: Any) -> None:
        # Suppress noisy standard HTTP logs during automated tests
        return


class DigitalTwinServer:
    """Manages the lifecycle of the threading HTTP server."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        self.host = host
        self.port = port
        self.server: Optional[ThreadingHTTPServer] = None
        self._thread: Optional[threading.Thread] = None

    def start(self, blocking: bool = False) -> None:
        self.server = ThreadingHTTPServer((self.host, self.port), DigitalTwinHTTPHandler)
        if blocking:
            print(f"[*] Digital Twin Server running at http://{self.host}:{self.port}/")
            self.server.serve_forever()
        else:
            self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        if self.server:
            self.server.shutdown()
            self.server.server_close()


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = DigitalTwinServer(host=host, port=port)
    server.start(blocking=True)
