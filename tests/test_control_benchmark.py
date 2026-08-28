"""Unit tests for ControlBenchmarkSuite and comparative evaluations."""

import pytest
from src.control.benchmark_control import ControlBenchmarkSuite, ControlBenchmarkMetrics


def test_control_benchmark_execution() -> None:
    """Verify benchmark runs Open-Loop, PID, and MPC and calculates IAE."""
    suite = ControlBenchmarkSuite(simulation_duration_sec=600.0, dt_sec=4.0)
    rep = suite.run_all_benchmarks()

    assert "controllers" in rep
    assert "OPEN_LOOP" in rep["controllers"]
    assert "PID" in rep["controllers"]
    assert "MPC" in rep["controllers"]
    assert rep["champion_controller"] == "MPC"
    assert rep["controllers"]["MPC"]["iae"] > 0.0
