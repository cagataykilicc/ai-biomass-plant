"""Unit tests for ProcessFaultSimulator and fault injection configurations."""

import pytest
from src.diagnostics.fault_simulator import IndustrialFaultType, FaultInjectionConfig, ProcessFaultSimulator


def test_fault_simulation_all_modes() -> None:
    """Verify fault simulator runs all 5 fault modes and alters telemetry."""
    sim = ProcessFaultSimulator()

    for fm in [
        IndustrialFaultType.NONE,
        IndustrialFaultType.CYCLONE_DIPLEG_BLOCKAGE,
        IndustrialFaultType.CONDENSER_TAR_FOULING,
        IndustrialFaultType.REACTOR_THERMAL_RUNAWAY,
        IndustrialFaultType.THERMOCOUPLE_SENSOR_DRIFT,
        IndustrialFaultType.FEED_AUGER_JAMMING,
    ]:
        cfg = FaultInjectionConfig(fault_type=fm, severity=0.8)
        rep, tel = sim.run_faulted_simulation(cfg, feedstock_name="olive_pomace")
        assert rep is not None
        assert tel is not None
        assert tel.TI_103 > 0.0

        if fm == IndustrialFaultType.CYCLONE_DIPLEG_BLOCKAGE:
            assert tel.PI_101 > 8.0  # Delta P surge
        elif fm == IndustrialFaultType.CONDENSER_TAR_FOULING:
            assert tel.TI_105 > 50.0  # Gas exit temp spike
        elif fm == IndustrialFaultType.REACTOR_THERMAL_RUNAWAY:
            assert tel.TI_103 > 600.0  # Core temp excursion
        elif fm == IndustrialFaultType.FEED_AUGER_JAMMING:
            assert tel.FI_101 < 30.0  # Feed flow loss
