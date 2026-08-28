"""Industrial hardware sensor telemetry modeling and signal extraction.

Standardizes instrument tags:
- TI-101: Dryer inlet gas temperature (°C)
- TI-102: Dryer exit biomass temperature (°C)
- TI-103: Pyrolysis reactor bed core temperature (°C)
- TI-104: Cyclone exit vapor temperature (°C)
- TI-105: Condenser exit gas temperature (°C)
- TI-106: Combustor flue gas temperature (°C)
- FI-101: Biomass wet feed rate (kg/h)
- FI-102: Condenser cooling water flow rate (kg/h)
- FI-103: Combustor combustion air intake flow rate (kg/h)
- PI-101: Reactor differential pressure (kPa)
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, List, Optional, ClassVar
import numpy as np

from src.simulation.plant_simulator import SimulationReport


@dataclass
class HardwareTelemetryPacket:
    """Standardized industrial process telemetry data packet."""
    timestamp: str
    feedstock_name: str
    TI_101: float  # Dryer inlet gas temp (°C)
    TI_102: float  # Dryer exit biomass temp (°C)
    TI_103: float  # Reactor bed temp (°C)
    TI_104: float  # Cyclone exit vapor temp (°C)
    TI_105: float  # Condenser exit gas temp (°C)
    TI_106: float  # Combustor flue gas temp (°C)
    FI_101: float  # Wet biomass feed rate (kg/h)
    FI_102: float  # Condenser cooling water rate (kg/h)
    FI_103: float  # Combustor air rate (kg/h)
    PI_101: float  # Reactor differential pressure (kPa)

    FEATURE_TAGS: ClassVar[List[str]] = [
        "TI_101", "TI_102", "TI_103", "TI_104", "TI_105", "TI_106",
        "FI_101", "FI_102", "FI_103", "PI_101"
    ]

    def to_feature_vector(self) -> np.ndarray:
        """Convert telemetry packet to numerical input vector for soft sensors."""
        return np.array([
            self.TI_101,
            self.TI_102,
            self.TI_103,
            self.TI_104,
            self.TI_105,
            self.TI_106,
            self.FI_101,
            self.FI_102,
            self.FI_103,
            self.PI_101,
        ], dtype=np.float64)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TelemetryExtractor:
    """Generates industrial hardware telemetry packets from digital twin simulation reports."""

    @staticmethod
    def extract_from_report(
        report: SimulationReport,
        add_sensor_noise: bool = True,
        random_seed: Optional[int] = None,
    ) -> HardwareTelemetryPacket:
        """Synthesize physical instrument readings from a completed process simulation."""
        rng = np.random.default_rng(random_seed)

        # Baseline physical true states
        t_dry_in = 180.0
        t_dry_out = report.drying.dryer_temperature_c
        t_reactor = report.reactor.operating_temperature_c
        t_cyclone = t_reactor - 15.0  # Slight thermal loss across cyclone body
        t_cond_exit = report.scenario_config.separation.condenser_exit_temp_c
        t_flue = report.combustion.flue_gas_actual_temp_c

        f_feed = report.scenario_config.feed_rate_kg_h
        # Cooling water mass flow rate (kg/h) for ~15°C water temp rise
        cooling_duty_kw = report.separation.condenser_cooling_duty_kw
        f_cooling_water = (cooling_duty_kw * 3600.0) / (4.184 * 15.0) if cooling_duty_kw > 0 else 0.0
        f_air = report.combustion.actual_combustion_air_rate_kg_h
        p_diff = 3.5 + 0.01 * f_feed  # Bed delta-P in kPa

        if add_sensor_noise:
            t_dry_in += float(rng.normal(0.0, 1.2))
            t_dry_out += float(rng.normal(0.0, 0.8))
            t_reactor += float(rng.normal(0.0, 1.5))
            t_cyclone += float(rng.normal(0.0, 1.5))
            t_cond_exit += float(rng.normal(0.0, 0.5))
            t_flue += float(rng.normal(0.0, 3.0))
            f_feed += float(rng.normal(0.0, 0.5))
            f_cooling_water += float(rng.normal(0.0, 5.0))
            f_air += float(rng.normal(0.0, 0.8))
            p_diff += float(rng.normal(0.0, 0.05))

        return HardwareTelemetryPacket(
            timestamp=datetime.now().isoformat(),
            feedstock_name=report.feedstock.name,
            TI_101=round(t_dry_in, 2),
            TI_102=round(t_dry_out, 2),
            TI_103=round(t_reactor, 2),
            TI_104=round(t_cyclone, 2),
            TI_105=round(t_cond_exit, 2),
            TI_106=round(t_flue, 2),
            FI_101=round(max(0.0, f_feed), 2),
            FI_102=round(max(0.0, f_cooling_water), 2),
            FI_103=round(max(0.0, f_air), 2),
            PI_101=round(max(0.1, p_diff), 3),
        )
