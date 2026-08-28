"""Unit tests for Model Predictive Controller (MPC)."""

import pytest
from src.control.mpc_controller import ModelPredictiveController, MPCConfig


def test_mpc_trajectory_tracking() -> None:
    """Verify MPC generates smooth control moves towards setpoint."""
    mpc = ModelPredictiveController(MPCConfig(prediction_horizon_Np=10, control_horizon_Nc=4))

    # Test error step
    u_move = mpc.compute(setpoint=520.0, current_pv=500.0)
    assert u_move > 55.0  # Ramps up firing
    assert 0.0 <= u_move <= 100.0

    # Ensure consecutive moves respect slew rate
    u_next = mpc.compute(setpoint=520.0, current_pv=505.0)
    assert abs(u_next - u_move) <= 8.0  # Max slew limit
