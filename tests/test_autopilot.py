"""Unit tests for AutonomousSupervisoryAgent and 5-State FSM Controller."""

import pytest
from src.autonomous.autopilot import AutonomousSupervisoryAgent, PlantOperatingState, AutopilotCommand


def test_autopilot_startup_to_cruise_transition() -> None:
    """Verify autopilot ramps temperature from preheat and transitions to cruise mode."""
    agent = AutonomousSupervisoryAgent(dt_sec=2.0)
    agent.reset(initial_temp_c=479.5)  # Near 480C transition threshold

    assert agent.current_state == PlantOperatingState.STARTUP_PREHEAT

    # Step through transition
    for _ in range(15):
        state, cmd = agent.step(mission_phase="QUALIFICATION")

    assert agent.current_state == PlantOperatingState.AUTONOMOUS_CRUISE
    assert cmd.target_feed_rate_kg_h == 100.0
    assert state.reactor_temp_c >= 480.0


def test_autopilot_cyclone_fault_pulse_jet_mitigation() -> None:
    """Verify autonomous fault mitigation executes nitrogen pulse-jet blowback."""
    agent = AutonomousSupervisoryAgent(dt_sec=2.0)
    agent.reset(initial_temp_c=500.0)
    agent.current_state = PlantOperatingState.AUTONOMOUS_CRUISE

    # Inject cyclone blockage
    state, cmd = agent.step(injected_fault="cyclone_blockage")
    assert agent.current_state == PlantOperatingState.FAULT_MITIGATION
    assert cmd.pulse_jet_active is True

    # Advance until cleared (40 seconds / 20 steps)
    for _ in range(25):
        state, cmd = agent.step(injected_fault="none")

    assert agent.current_state == PlantOperatingState.AUTONOMOUS_CRUISE
    assert cmd.pulse_jet_active is False
