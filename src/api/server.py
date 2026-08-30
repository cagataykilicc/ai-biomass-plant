"""High-performance multi-threaded HTTP server hosting the Digital Twin REST API and Static Web GUI."""

from __future__ import annotations

import json
import logging
import mimetypes
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs

from src.api.handlers import APIRequestHandler
from src.api.openapi import get_openapi_spec, get_swagger_ui_html, get_redoc_html


class DigitalTwinHTTPHandler(BaseHTTPRequestHandler):
    """Handles REST API calls and serves modern static Web GUI assets."""

    server_version = "DigitalTwinHTTP/2.2"

    def _set_cors_headers(self, content_type: str = "application/json") -> None:
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-API-Key")

    def _is_authorized(self) -> bool:
        """Validate API key from environment variable, failing closed if unset or invalid."""
        required_key = os.environ.get("BIOPLANT_API_KEY") or os.environ.get("API_KEY")
        if not required_key:
            return False
        provided_key = self.headers.get("X-API-Key")
        return bool(provided_key and provided_key == required_key)

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == "/openapi.json":
            spec = get_openapi_spec()
            self._send_json(200, spec)
            return

        if path in ("/docs", "/docs/"):
            html = get_swagger_ui_html().encode("utf-8")
            self.send_response(200)
            self._set_cors_headers("text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return

        if path in ("/redoc", "/redoc/"):
            html = get_redoc_html().encode("utf-8")
            self.send_response(200)
            self._set_cors_headers("text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return

        if path.startswith("/api/"):
            if not self._is_authorized():
                self._send_json(401, {"error": "Unauthorized: Missing or invalid X-API-Key header.", "endpoint": path})
                return

            try:
                if path == "/api/status":
                    res = APIRequestHandler.handle_status()
                    self._send_json(200, res)
                    return

                if path == "/api/feedstocks":
                    res = APIRequestHandler.handle_feedstocks()
                    self._send_json(200, res)
                    return

                if path == "/api/iot/status":
                    res = APIRequestHandler.handle_iot_status()
                    self._send_json(200, res)
                    return

                if path == "/api/iot/modbus/read":
                    res = APIRequestHandler.handle_modbus_read()
                    self._send_json(200, res)
                    return

                self._send_json(404, {"error": f"Endpoint not found: {path}", "endpoint": path})
                return
            except ValueError as val_err:
                self._send_json(400, {"error": str(val_err), "endpoint": path})
                return
            except Exception as exc:
                logging.exception("Unhandled server exception in GET %s: %s", path, exc)
                self._send_json(500, {"error": "Internal server error occurred while processing request.", "endpoint": path})
                return

        # Serve static assets
        self._serve_static_file(path)

    def do_POST(self) -> None:
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path.startswith("/api/"):
            if not self._is_authorized():
                self._send_json(401, {"error": "Unauthorized: Missing or invalid X-API-Key header.", "endpoint": path})
                return

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
            elif path == "/api/control":
                res = APIRequestHandler.handle_control(data)
                self._send_json(200, res)
            elif path == "/api/economics":
                res = APIRequestHandler.handle_economics(data)
                self._send_json(200, res)
            elif path == "/api/autopilot/step":
                res = APIRequestHandler.handle_autopilot_step(data)
                self._send_json(200, res)
            elif path == "/api/autopilot/mission":
                res = APIRequestHandler.handle_autopilot_mission(data)
                self._send_json(200, res)
            elif path == "/api/iot/status":
                res = APIRequestHandler.handle_iot_status()
                self._send_json(200, res)
            elif path == "/api/iot/modbus/read":
                res = APIRequestHandler.handle_modbus_read(data)
                self._send_json(200, res)
            elif path == "/api/iot/modbus/write":
                res = APIRequestHandler.handle_modbus_write(data)
                self._send_json(200, res)
            elif path == "/api/iot/mqtt/publish":
                res = APIRequestHandler.handle_mqtt_publish(data)
                self._send_json(200, res)
            elif path == "/api/iot/hil/step":
                res = APIRequestHandler.handle_hil_step(data)
                self._send_json(200, res)
            else:
                self._send_json(404, {"error": f"Endpoint not found: {path}", "endpoint": path})
        except ValueError as val_err:
            self._send_json(400, {"error": str(val_err), "endpoint": path})
        except Exception as exc:
            logging.exception("Unhandled server exception in POST %s: %s", path, exc)
            self._send_json(500, {"error": "Internal server error occurred while processing request.", "endpoint": path})

    def _send_json(self, status_code: int, payload: Dict[str, Any]) -> None:
        raw_bytes = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status_code)
        self._set_cors_headers("application/json")
        self.send_header("Content-Length", str(len(raw_bytes)))
        self.end_headers()
        self.wfile.write(raw_bytes)

    def _serve_static_file(self, req_path: str) -> None:
        static_dir = (Path(__file__).resolve().parent.parent / "web" / "static").resolve()
        clean_path = req_path.lstrip("/")
        if not clean_path or clean_path == "":
            target_file = (static_dir / "index.html").resolve()
        else:
            target_file = (static_dir / clean_path).resolve()

        # Path traversal security verification
        try:
            is_inside = target_file.is_relative_to(static_dir)
        except AttributeError:
            is_inside = str(target_file).startswith(str(static_dir))

        if not is_inside:
            self.send_response(403)
            self._set_cors_headers("text/plain")
            self.end_headers()
            self.wfile.write(b"403 - Forbidden")
            return

        if not target_file.is_file():
            # Fallback to index.html for SPA routing
            target_file = (static_dir / "index.html").resolve()

        if not target_file.is_file():
            self.send_response(404)
            self._set_cors_headers("text/plain")
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
        required_key = os.environ.get("BIOPLANT_API_KEY") or os.environ.get("API_KEY")
        if not required_key:
            raise RuntimeError(
                "Failed to start DigitalTwinServer: BIOPLANT_API_KEY (or API_KEY) environment variable "
                "is not set. The server refuses to start in unauthenticated mode."
            )

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
