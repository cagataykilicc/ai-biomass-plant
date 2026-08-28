"""Unit tests for AutonomousStressTestRunner multi-phase mission execution."""

import pytest
from src.autonomous.stress_test import AutonomousStressTestRunner


def test_autonomous_mission_stress_test() -> None:
    """Verify autonomous stress test executes all 6 phases successfully."""
    # Use dt=10.0s for rapid unit test verification
    runner = AutonomousStressTestRunner(dt_sec=10.0)
    rep = runner.run_4hour_mission()

    assert rep["overall_status"] == "MISSION_SUCCESS"
    assert rep["phases_executed_count"] == 6
    assert len(rep["phases"]) == 6
    assert rep["phases"][0]["status"] == "PASSED"
    assert rep["phases"][-1]["status"] == "PASSED"
