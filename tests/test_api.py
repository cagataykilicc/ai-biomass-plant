"""Integration and automated unit tests for Digital Twin REST API and HTTP server."""

import json
import time
import urllib.request
import urllib.error
import pytest

from src.api.handlers import APIRequestHandler
from src.api.server import DigitalTwinServer


def test_api_status_and_feedstocks() -> None:
    """Verify status and feedstock catalog API endpoints."""
    status = APIRequestHandler.handle_status()
    assert status["status"] == "ONLINE"
    assert status["version"] == "1.2.0"
    assert "pine_sawdust" in status["available_feedstocks"]

    feedstocks = APIRequestHandler.handle_feedstocks()
    assert "feedstocks" in feedstocks
    assert "olive_pomace" in feedstocks["feedstocks"]
    assert feedstocks["feedstocks"]["pine_sawdust"]["hhv_dry_mj_kg"] > 15.0


def test_api_simulate() -> None:
    """Verify simulation REST API returns expected flowsheet results."""
    payload = {
        "feedstock": "pine_sawdust",
        "reactor_temp_c": 520.0,
        "feed_rate_kg_h": 120.0,
        "moisture_pct": 10.0,
        "yield_mode": "deterministic",
    }
    res = APIRequestHandler.handle_simulate(payload)
    assert res["feedstock"] == "Pine Sawdust"
    assert res["operating_conditions"]["reactor_temp_c"] == 520.0
    assert res["yields_dry"]["bio_oil_yield_pct"] > 0.0
    assert res["energy_and_heat"]["tsi_pct"] > 0.0


def test_api_soft_sensors() -> None:
    """Verify soft sensors REST API returns predictions and uncertainty intervals."""
    payload = {"feedstock": "olive_pomace", "reactor_temp_c": 500.0, "feed_rate_kg_h": 100.0}
    res = APIRequestHandler.handle_soft_sensors(payload)
    assert "telemetry" in res
    assert "soft_sensors" in res
    assert "SS_101_BIO_OIL_TAN" in res["soft_sensors"]
    assert res["soft_sensors"]["SS_101_BIO_OIL_TAN"]["point_estimate"] > 0.0


def test_api_optimization() -> None:
    """Verify Pareto multiobjective optimization REST API."""
    payload = {"feedstock": "pine_sawdust", "mode": "pareto"}
    res = APIRequestHandler.handle_optimize(payload)
    assert "frontier" in res
    assert res["frontier_size"] > 0
    assert "top_solution" in res


def test_api_diagnostics() -> None:
    """Verify fault simulation and anomaly diagnostics REST API."""
    payload = {"fault_type": "cyclone_blockage", "severity": 0.85}
    res = APIRequestHandler.handle_diagnostics(payload)
    assert res["fault_injected"] == "CYCLONE_DIPLEG_BLOCKAGE"
    assert "anomaly_detection" in res
    assert "alarm" in res
    assert res["anomaly_detection"]["is_anomaly"] is True


def test_api_maintenance() -> None:
    """Verify predictive maintenance and work orders REST API."""
    payload = {"operating_hours": 4500.0}
    res = APIRequestHandler.handle_maintenance(payload)
    assert "fleet_summary" in res
    assert "work_orders" in res
    assert len(res["fleet_summary"]["assets"]) == 4
    assert res["fleet_summary"]["current_operating_hours"] == 4500.0


def test_api_control() -> None:
    """Verify dynamic closed-loop control REST API."""
    payload = {"controller": "mpc", "setpoint": 520.0, "moisture_disturb": 18.0}
    res = APIRequestHandler.handle_control(payload)
    assert res["controller"] == "MPC"
    assert "metrics" in res
    assert "trajectory" in res
    assert len(res["trajectory"]) > 0


def test_api_economics() -> None:
    """Verify TEA and LCA carbon accounting REST API."""
    payload = {"feedstock": "olive_pomace", "reactor_temp_c": 500.0, "feed_rate_kg_h": 100.0}
    res = APIRequestHandler.handle_economics(payload)
    assert "capital_expenditure_capex" in res
    assert "financial_viability_dcf" in res
    assert "life_cycle_assessment_lca" in res
    assert res["financial_viability_dcf"]["net_present_value_usd"] > 0.0


def test_live_http_server_endpoints() -> None:
    """Spin up live ThreadingHTTPServer and execute end-to-end HTTP requests."""
    server = DigitalTwinServer(host="127.0.0.1", port=8123)
    server.start(blocking=False)
    time.sleep(0.5)

    try:
        # 1. Test GET /api/status
        with urllib.request.urlopen("http://127.0.0.1:8123/api/status") as response:
            assert response.status == 200
            data = json.loads(response.read().decode())
            assert data["version"] == "1.2.0"
            assert data["status"] == "ONLINE"

        # 2. Test GET / (HTML frontend)
        with urllib.request.urlopen("http://127.0.0.1:8123/") as response:
            assert response.status == 200
            content = response.read().decode()
            assert "BIOPLANT AI" in content
            assert "html" in content.lower()

        # 3. Test POST /api/simulate
        req = urllib.request.Request(
            "http://127.0.0.1:8123/api/simulate",
            data=json.dumps({"feedstock": "olive_pomace", "reactor_temp_c": 500.0}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as response:
            assert response.status == 200
            sim_data = json.loads(response.read().decode())
            assert sim_data["feedstock"] == "Olive Pomace"

    finally:
        server.stop()
