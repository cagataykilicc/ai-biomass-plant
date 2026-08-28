"""Industrial fault simulation and equipment degradation injection framework.

Simulates 5 critical industrial failure modes:
1. CYCLONE_DIPLEG_BLOCKAGE: Solids accumulation, high delta-P, char carryover into condenser.
2. CONDENSER_TAR_FOULING: Heavy tar/wax coating, degraded heat transfer, gas exit temp spike.
3. REACTOR_THERMAL_RUNAWAY: Exothermic secondary reaction runaway or air leak (temp spike).
4. THERMOCOUPLE_SENSOR_DRIFT: Subtle instrument measurement bias.
5. FEED_AUGER_JAMMING: Mechanical auger stall, loss of biomass feed flow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, Tuple
import numpy as np

from src.simulation.plant_simulator import BiomassPlantSimulator, SimulationReport
from src.sensors.telemetry import TelemetryExtractor, HardwareTelemetryPacket
from src.utils.config import PlantScenarioConfig


class IndustrialFaultType(str, Enum):
    """Enumeration of simulated industrial plant fault modes."""
    NONE = "NONE"
    CYCLONE_DIPLEG_BLOCKAGE = "CYCLONE_DIPLEG_BLOCKAGE"
    CONDENSER_TAR_FOULING = "CONDENSER_TAR_FOULING"
    REACTOR_THERMAL_RUNAWAY = "REACTOR_THERMAL_RUNAWAY"
    THERMOCOUPLE_SENSOR_DRIFT = "THERMOCOUPLE_SENSOR_DRIFT"
    FEED_AUGER_JAMMING = "FEED_AUGER_JAMMING"


@dataclass
class FaultInjectionConfig:
    """Configuration for injecting process faults into digital twin."""
    fault_type: IndustrialFaultType = IndustrialFaultType.NONE
    severity: float = 0.80  # Scale in [0.0, 1.0]
    drift_bias: float = 25.0  # Used for sensor drift (°C)

    def __post_init__(self) -> None:
        if not (0.0 <= self.severity <= 1.0):
            raise ValueError(f"Severity must be in [0.0, 1.0]. Got: {self.severity}")


class ProcessFaultSimulator:
    """Injects equipment degradation and process upsets into plant simulations and telemetry."""

    def __init__(self, simulator: Optional[BiomassPlantSimulator] = None) -> None:
        self.simulator = simulator or BiomassPlantSimulator()

    def run_faulted_simulation(
        self,
        fault_config: FaultInjectionConfig,
        feedstock_name: str = "pine_sawdust",
        feed_rate_kg_h: float = 100.0,
        reactor_temp_c: float = 500.0,
        random_seed: Optional[int] = 42,
    ) -> Tuple[SimulationReport, HardwareTelemetryPacket]:
        """Execute simulation with injected process faults and generate telemetry."""
        ft = fault_config.fault_type
        sev = fault_config.severity

        # Modify baseline parameters based on fault type
        mod_feed_rate = feed_rate_kg_h
        mod_temp = reactor_temp_c

        if ft == IndustrialFaultType.FEED_AUGER_JAMMING:
            # Feeder jamming drops feed flow towards near-zero
            mod_feed_rate = max(1.0, feed_rate_kg_h * (1.0 - 0.95 * sev))

        elif ft == IndustrialFaultType.REACTOR_THERMAL_RUNAWAY:
            # Exothermic runaway spikes core reactor temperature
            mod_temp = reactor_temp_c + 180.0 * sev

        # Run base simulation
        report = self.simulator.run_simulation(
            feedstock_name=feedstock_name,
            feed_rate_kg_h=mod_feed_rate,
            reactor_temp_c=mod_temp,
        )

        # Extract telemetry
        telemetry = TelemetryExtractor.extract_from_report(report, add_sensor_noise=True, random_seed=random_seed)

        # Inject equipment-specific telemetry distortions
        if ft == IndustrialFaultType.CYCLONE_DIPLEG_BLOCKAGE:
            # Bed delta-P surges from ~4 kPa to > 12 kPa
            telemetry.PI_101 += float(8.5 * sev)
            # Cyclone exit gas temperature drops slightly due to gas channeling
            telemetry.TI_104 -= float(20.0 * sev)

        elif ft == IndustrialFaultType.CONDENSER_TAR_FOULING:
            # Condenser exit gas temperature spikes from 35°C up to 65°C
            telemetry.TI_105 += float(30.0 * sev)
            # Cooling water demand spikes
            telemetry.FI_102 += float(600.0 * sev)

        elif ft == IndustrialFaultType.THERMOCOUPLE_SENSOR_DRIFT:
            # Sensor bias on reactor thermocouple TI_103
            telemetry.TI_103 += float(fault_config.drift_bias * sev)

        elif ft == IndustrialFaultType.FEED_AUGER_JAMMING:
            # Flow meter reads drop in feed rate, delta-P collapses
            telemetry.FI_101 = float(max(1.0, feed_rate_kg_h * (1.0 - 0.95 * sev)))
            telemetry.PI_101 = float(max(0.5, telemetry.PI_101 * (1.0 - 0.7 * sev)))

        return report, telemetry
