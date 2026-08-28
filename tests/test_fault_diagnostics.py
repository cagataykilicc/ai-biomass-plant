"""Unit tests for FaultDiagnosticEngine and root cause attribution."""

import pytest
from src.diagnostics.fault_simulator import IndustrialFaultType, FaultInjectionConfig, ProcessFaultSimulator
from src.diagnostics.fault_diagnostics import FaultDiagnosticEngine, DiagnosticClassificationResult


def test_fault_classifier_training_and_diagnosis() -> None:
    """Verify supervised fault classifier trains and identifies injected faults."""
    engine = FaultDiagnosticEngine()
    engine.train_on_synthetic_faults(samples_per_fault=15)
    assert engine.is_fitted is True

    sim = ProcessFaultSimulator()

    # Simulate Cyclone Blockage and diagnose
    cfg = FaultInjectionConfig(IndustrialFaultType.CYCLONE_DIPLEG_BLOCKAGE, severity=0.9)
    rep, tel = sim.run_faulted_simulation(cfg)

    res = engine.diagnose(tel)
    assert isinstance(res, DiagnosticClassificationResult)
    assert res.predicted_fault == IndustrialFaultType.CYCLONE_DIPLEG_BLOCKAGE
    assert res.affected_equipment_tag == "CYCLONE_C101"
    assert res.confidence_probability > 0.50
