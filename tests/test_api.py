"""Integration and automated unit tests for Digital Twin REST API and HTTP server."""

import json
import os
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
    assert status["version"] == "2.1.0"
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


def test_api_autopilot() -> None:
    """Verify autonomous autopilot step and mission REST API."""
    step_payload = {"moisture": 12.0, "fault": "none", "setpoint": 500.0}
    res_step = APIRequestHandler.handle_autopilot_step(step_payload)
    assert "plant_state" in res_step
    assert "command" in res_step

    mission_payload = {"dt": 10.0}
    res_mission = APIRequestHandler.handle_autopilot_mission(mission_payload)
    assert res_mission["overall_status"] == "MISSION_SUCCESS"
    assert res_mission["phases_executed_count"] == 6


def test_server_refuses_to_start_without_api_key() -> None:
    """Verify that DigitalTwinServer refuses to start if no API key is configured."""
    old_key = os.environ.pop("BIOPLANT_API_KEY", None)
    old_api_key = os.environ.pop("API_KEY", None)

    try:
        server = DigitalTwinServer(host="127.0.0.1", port=8122)
        with pytest.raises(RuntimeError, match="BIOPLANT_API_KEY"):
            server.start(blocking=False)
    finally:
        if old_key:
            os.environ["BIOPLANT_API_KEY"] = old_key
        if old_api_key:
            os.environ["API_KEY"] = old_api_key


def test_live_http_server_endpoints() -> None:
    """Spin up live ThreadingHTTPServer and execute end-to-end HTTP requests."""
    os.environ["BIOPLANT_API_KEY"] = "test-live-key"
    server = DigitalTwinServer(host="127.0.0.1", port=8123)
    server.start(blocking=False)
    time.sleep(0.5)

    headers = {"X-API-Key": "test-live-key"}

    try:
        # 1. Test GET /api/status
        req_status = urllib.request.Request("http://127.0.0.1:8123/api/status", headers=headers)
        with urllib.request.urlopen(req_status) as response:
            assert response.status == 200
            data = json.loads(response.read().decode())
            assert data["version"] == "2.1.0"
            assert data["status"] == "ONLINE"

        # 2. Test GET / (HTML frontend static asset)
        with urllib.request.urlopen("http://127.0.0.1:8123/") as response:
            assert response.status == 200
            content = response.read().decode()
            assert "BIOPLANT AI" in content
            assert "html" in content.lower()

        # 3. Test POST /api/simulate
        req = urllib.request.Request(
            "http://127.0.0.1:8123/api/simulate",
            data=json.dumps({"feedstock": "olive_pomace", "reactor_temp_c": 500.0}).encode(),
            headers={"Content-Type": "application/json", "X-API-Key": "test-live-key"},
        )
        with urllib.request.urlopen(req) as response:
            assert response.status == 200
            sim_data = json.loads(response.read().decode())
            assert sim_data["feedstock"] == "Olive Pomace"

        # 4. Test Path Traversal Protection (403 Forbidden)
        try:
            req_traversal = urllib.request.Request("http://127.0.0.1:8123/../../pyproject.toml")
            urllib.request.urlopen(req_traversal)
            assert False, "Expected 403 Forbidden on path traversal attempt"
        except urllib.error.HTTPError as err:
            assert err.code == 403

        # 5. Test Input Bounds Validation (400 Bad Request)
        try:
            req_invalid = urllib.request.Request(
                "http://127.0.0.1:8123/api/simulate",
                data=json.dumps({"feed_rate_kg_h": -50.0}).encode(),
                headers={"Content-Type": "application/json", "X-API-Key": "test-live-key"},
            )
            urllib.request.urlopen(req_invalid)
            assert False, "Expected 400 Bad Request on negative feed rate"
        except urllib.error.HTTPError as err:
            assert err.code == 400
            err_data = json.loads(err.read().decode())
            assert "outside allowed range" in err_data["error"]

    finally:
        if "BIOPLANT_API_KEY" in os.environ:
            del os.environ["BIOPLANT_API_KEY"]
        server.stop()


def test_api_key_authentication() -> None:
    """Verify X-API-Key header authentication when BIOPLANT_API_KEY environment variable is set."""
    os.environ["BIOPLANT_API_KEY"] = "bioplant-secure-token-123"
    server = DigitalTwinServer(host="127.0.0.1", port=8124)
    server.start(blocking=False)
    time.sleep(0.5)

    try:
        # 1. Without header -> 401 Unauthorized
        try:
            urllib.request.urlopen("http://127.0.0.1:8124/api/status")
            assert False, "Expected 401 Unauthorized when API key is required"
        except urllib.error.HTTPError as err:
            assert err.code == 401

        # 2. With invalid header -> 401 Unauthorized
        try:
            req_bad = urllib.request.Request("http://127.0.0.1:8124/api/status", headers={"X-API-Key": "wrong-key"})
            urllib.request.urlopen(req_bad)
            assert False, "Expected 401 Unauthorized with invalid API key"
        except urllib.error.HTTPError as err:
            assert err.code == 401

        # 3. With correct header -> 200 OK
        req_good = urllib.request.Request("http://127.0.0.1:8124/api/status", headers={"X-API-Key": "bioplant-secure-token-123"})
        with urllib.request.urlopen(req_good) as response:
            assert response.status == 200
            data = json.loads(response.read().decode())
            assert data["status"] == "ONLINE"

    finally:
        if "BIOPLANT_API_KEY" in os.environ:
            del os.environ["BIOPLANT_API_KEY"]
        server.stop()
