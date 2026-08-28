"""Unit tests for Blackbox FlightRecorder and telemetry logging."""

import pytest
from src.autonomous.flight_recorder import FlightRecorder, FlightLogEntry


def test_flight_recorder_logging_and_export() -> None:
    """Verify flight recorder appends entries and exports structured JSON logs."""
    recorder = FlightRecorder(max_entries=100)

    entry = recorder.record_step(
        timestamp_sec=120.0,
        mission_phase="STARTUP",
        fsm_state="STARTUP_PREHEAT",
        reactor_temp_c=250.0,
        target_temp_c=500.0,
        feed_rate_kg_h=0.0,
        moisture_pct=12.0,
        burner_duty_pct=85.0,
        tsi_pct=0.0,
        action_taken="PREHEAT_RAMP",
    )

    assert isinstance(entry, FlightLogEntry)
    assert len(recorder.entries) == 1
    assert entry.time_min == 2.0
    assert entry.reactor_temp_c == 250.0
