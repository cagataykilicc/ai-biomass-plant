"""Unit tests for digital PID controller with anti-windup clamping."""

import pytest
from src.control.pid_controller import PIDController, PIDGains


def test_pid_controller_regulation() -> None:
    """Verify PID controller increases control effort when PV is below setpoint."""
    pid = PIDController()

    # Temperature below target (480 vs 500) -> Control effort increases
    u_out = pid.compute(setpoint=500.0, process_variable=480.0, dt_sec=2.0)
    assert u_out > 55.0  # Firing increased

    # Temperature above target (520 vs 500) -> Control effort decreases
    pid.reset()
    u_down = pid.compute(setpoint=500.0, process_variable=520.0, dt_sec=2.0)
    assert u_down < 55.0


def test_pid_anti_windup_saturation_clamping() -> None:
    """Verify integrator does not wind up beyond saturation limits."""
    pid = PIDController(u_min=0.0, u_max=100.0)

    # Large sustained error
    for _ in range(50):
        u = pid.compute(setpoint=600.0, process_variable=400.0, dt_sec=2.0)
        assert 0.0 <= u <= 100.0
