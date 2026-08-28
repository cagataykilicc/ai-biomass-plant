"""Unit tests for AlarmManager and safety action mitigation triage."""

import pytest
from src.diagnostics.fault_simulator import IndustrialFaultType
from src.diagnostics.anomaly_detector import AnomalyDetectionResult
from src.diagnostics.fault_diagnostics import DiagnosticClassificationResult
from src.diagnostics.alarm_manager import AlarmManager, AlarmPriority, SafetyActionProtocol


def test_alarm_evaluation_and_priority_triage() -> None:
    """Verify emergency actions and priorities are dispatched correctly."""
    # Test Thermal Runaway -> CRITICAL_EMERGENCY
    anom_crit = AnomalyDetectionResult(
        is_anomaly=True,
        overall_anomaly_score=0.92,
        isolation_forest_anomaly=True,
        isolation_forest_score=0.88,
        pca_q_statistic=15.0,
        pca_q_limit_99=3.5,
        pca_q_exceeded=True,
        pca_t2_statistic=25.0,
        pca_t2_limit_99=5.0,
        pca_t2_exceeded=True,
        physical_residual_violation=False,
        top_contributing_sensors=[],
    )
    diag_crit = DiagnosticClassificationResult(
        predicted_fault=IndustrialFaultType.REACTOR_THERMAL_RUNAWAY,
        confidence_probability=0.95,
        fault_probabilities={},
        affected_equipment_tag="REACTOR_R101",
        root_cause_explanation="Thermal excursion",
    )

    alarm = AlarmManager.evaluate_alarm(anom_crit, diag_crit)
    assert isinstance(alarm, SafetyActionProtocol)
    assert alarm.priority == AlarmPriority.CRITICAL_EMERGENCY
    assert "nitrogen" in alarm.automated_interlock_action.lower() or "trip" in alarm.automated_interlock_action.lower()
    assert "R101" in alarm.affected_equipment
