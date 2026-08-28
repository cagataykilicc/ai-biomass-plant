"""Unit tests for DynamicBiomassReactor transient simulation model."""

import pytest
from src.control.dynamic_model import DynamicBiomassReactor, PlantDynamicState


def test_dynamic_reactor_step_and_thermal_response() -> None:
    """Verify reactor temperature rises when high burner heat is applied."""
    plant = DynamicBiomassReactor(initial_temp_c=500.0, initial_feed_rate_kg_h=100.0)

    # Step with 90% firing duty
    state = None
    for _ in range(30):
        state = plant.step(control_input_pct=90.0, dt_sec=2.0)

    assert isinstance(state, PlantDynamicState)
    assert state.reactor_temp_c > 500.0  # Temperature increased under heavy heating
    assert state.burner_heat_kw > 45.0
    assert state.time_sec == 60.0


def test_moisture_disturbance_cooling_effect() -> None:
    """Verify sudden moisture increase causes transient thermal drop."""
    plant = DynamicBiomassReactor(initial_temp_c=500.0, initial_moisture_pct=10.0)

    # Step with constant 55% firing duty and higher moisture (25%)
    for _ in range(20):
        state = plant.step(control_input_pct=55.0, moisture_override=25.0, dt_sec=2.0)

    assert state.reactor_temp_c < 500.0  # Evaporation cools the bed
    assert state.moisture_pct == 25.0
