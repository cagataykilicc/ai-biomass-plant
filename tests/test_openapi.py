"""Automated unit and integration tests for OpenAPI 3.0.3 generator, Swagger UI, and ReDoc routes."""

import json
import os
import time
import urllib.request
import urllib.error
import pytest

from src.api.openapi import get_openapi_spec, get_swagger_ui_html, get_redoc_html
from src.api.server import DigitalTwinServer


def test_openapi_spec_structure() -> None:
    """Verify OpenAPI 3.0.3 specification structure, components, and endpoints."""
    spec = get_openapi_spec()
    assert spec["openapi"] == "3.0.3"
    assert "info" in spec
    assert spec["info"]["version"] == "2.5.0"
    assert "paths" in spec

    # Verify all 20 primary, IoT, and fleet endpoints are documented
    expected_paths = [
        "/api/status",
        "/api/feedstocks",
        "/api/simulate",
        "/api/soft-sensors",
        "/api/optimize",
        "/api/diagnostics",
        "/api/maintenance",
        "/api/control",
        "/api/economics",
        "/api/autopilot/step",
        "/api/autopilot/mission",
        "/api/iot/status",
        "/api/iot/modbus/read",
        "/api/iot/modbus/write",
        "/api/iot/mqtt/publish",
        "/api/iot/hil/step",
        "/api/fleet/status",
        "/api/fleet/dispatch",
        "/api/fleet/corc-arbitrage",
        "/api/fleet/renewable-dispatch",
    ]
    for p in expected_paths:
        assert p in spec["paths"], f"Expected endpoint '{p}' missing from OpenAPI spec"

    # Verify components and security schemes
    assert "components" in spec
    assert "securitySchemes" in spec["components"]
    assert "ApiKeyAuth" in spec["components"]["securitySchemes"]
    assert spec["components"]["securitySchemes"]["ApiKeyAuth"]["name"] == "X-API-Key"


def test_swagger_and_redoc_html_renderers() -> None:
    """Verify Swagger UI and ReDoc HTML template generators."""
    swagger_html = get_swagger_ui_html()
    assert "<!DOCTYPE html>" in swagger_html
    assert "swagger-ui" in swagger_html
    assert "/openapi.json" in swagger_html

    redoc_html = get_redoc_html()
    assert "<!DOCTYPE html>" in redoc_html
    assert "<redoc" in redoc_html
    assert "/openapi.json" in redoc_html


def test_live_openapi_and_docs_endpoints() -> None:
    """Verify live HTTP server serves /openapi.json, /docs, and /redoc."""
    os.environ["BIOPLANT_API_KEY"] = "test-openapi-key"
    server = DigitalTwinServer(host="127.0.0.1", port=8129)
    server.start(blocking=False)
    time.sleep(0.5)

    try:
        # 1. Test GET /openapi.json
        with urllib.request.urlopen("http://127.0.0.1:8129/openapi.json") as res:
            assert res.status == 200
            assert "application/json" in res.headers.get("Content-Type", "")
            data = json.loads(res.read().decode())
            assert data["openapi"] == "3.0.3"
            assert data["info"]["version"] == "2.5.0"

        # 2. Test GET /docs (Swagger UI)
        with urllib.request.urlopen("http://127.0.0.1:8129/docs") as res:
            assert res.status == 200
            assert "text/html" in res.headers.get("Content-Type", "")
            body = res.read().decode()
            assert "swagger-ui" in body

        # 3. Test GET /redoc (ReDoc)
        with urllib.request.urlopen("http://127.0.0.1:8129/redoc") as res:
            assert res.status == 200
            assert "text/html" in res.headers.get("Content-Type", "")
            body = res.read().decode()
            assert "<redoc" in body

    finally:
        if "BIOPLANT_API_KEY" in os.environ:
            del os.environ["BIOPLANT_API_KEY"]
        server.stop()
