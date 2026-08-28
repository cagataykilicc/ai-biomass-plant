"""Plant simulation engine orchestrating unit operations and plant balances.

Executes end-to-end simulation workflows:
Feedstock Ingestion & Validation -> Drying -> Pyrolysis Reactor -> Separation -> Mass & Energy Balances -> KPIs.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import json

from src.data.feedstock import BiomassFeedstock
from src.data.preprocessing import FeedstockLibrary
from src.process.drying import BiomassDryer, DryingResult
from src.process.reactor import PyrolysisReactor, ReactorOutput
from src.process.separation import ProductSeparator, SeparationResult
from src.process.mass_balance import MassBalanceEngine, MassBalanceSummary
from src.process.energy_balance import EnergyBalanceEngine, EnergyBalanceSummary
from src.utils.config import PlantScenarioConfig


@dataclass
class SimulationReport:
    """Consolidated simulation result report for the entire plant."""
    scenario_config: PlantScenarioConfig
    feedstock: BiomassFeedstock
    drying: DryingResult
    reactor: ReactorOutput
    separation: SeparationResult
    mass_balance: MassBalanceSummary
    energy_balance: EnergyBalanceSummary
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": {
                "version": "0.1.0",
                "timestamp": self.timestamp,
                "plant_status": "OPERATIONAL",
                "mass_balance_status": self.mass_balance.status,
                "energy_balance_status": self.energy_balance.status,
            },
            "feedstock": self.feedstock.to_dict(),
            "drying_section": self.drying.to_dict(),
            "reactor_section": self.reactor.to_dict(),
            "separation_section": self.separation.to_dict(),
            "mass_balance": self.mass_balance.to_dict(),
            "energy_balance": self.energy_balance.to_dict(),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class BiomassPlantSimulator:
    """Core simulation orchestrator for the virtual biomass conversion plant."""

    def __init__(self, feedstock_library: Optional[FeedstockLibrary] = None) -> None:
        self.feedstock_library = feedstock_library or FeedstockLibrary()
        self.mass_balance_engine = MassBalanceEngine()
        self.energy_balance_engine = EnergyBalanceEngine()

    def run_simulation(
        self,
        scenario: Optional[PlantScenarioConfig] = None,
        feedstock_name: Optional[str] = None,
        feed_rate_kg_h: Optional[float] = None,
        moisture_pct: Optional[float] = None,
        reactor_temp_c: Optional[float] = None,
        heating_rate_c_min: Optional[float] = None,
        residence_time_min: Optional[float] = None,
    ) -> SimulationReport:
        """Run an end-to-end plant simulation.

        Args:
            scenario: Optional PlantScenarioConfig object.
            feedstock_name: Optional override for feedstock identifier.
            feed_rate_kg_h: Optional override for wet feed rate (kg/h).
            moisture_pct: Optional override for feed moisture content (wt%).
            reactor_temp_c: Optional override for reactor temperature (°C).
            heating_rate_c_min: Optional override for heating rate (°C/min).
            residence_time_min: Optional override for residence time (min).

        Returns:
            SimulationReport with detailed stream, unit, and balance information.
        """
        # 1. Resolve Scenario Configuration
        cfg = scenario or PlantScenarioConfig()

        if feedstock_name is not None:
            cfg.feedstock_name = feedstock_name
        if feed_rate_kg_h is not None:
            cfg.feed_rate_kg_h = feed_rate_kg_h
        if moisture_pct is not None:
            cfg.moisture_pct_override = moisture_pct
        if reactor_temp_c is not None:
            cfg.reactor.temperature_c = reactor_temp_c
        if heating_rate_c_min is not None:
            cfg.reactor.heating_rate_c_min = heating_rate_c_min
        if residence_time_min is not None:
            cfg.reactor.residence_time_min = residence_time_min

        cfg.validate()

        # 2. Ingest and Validate Feedstock
        feedstock = self.feedstock_library.load_feedstock(
            name_or_path=cfg.feedstock_name,
            moisture_override=cfg.moisture_pct_override,
            particle_size_override=cfg.particle_size_mm_override,
        )

        # 3. Step 1: Drying / Pretreatment Unit
        dryer = BiomassDryer(config=cfg.drying)
        drying_result = dryer.process(
            feed_rate_kg_h=cfg.feed_rate_kg_h,
            feedstock=feedstock,
        )

        # 4. Step 2: Pyrolysis Reactor Unit
        reactor = PyrolysisReactor(config=cfg.reactor)
        reactor_output = reactor.process(
            dried_feed_rate_kg_h=drying_result.dried_feed_rate_out_kg_h,
            residual_moisture_pct=drying_result.final_moisture_pct,
            feedstock=feedstock,
            temp_override=cfg.reactor.temperature_c,
            heating_rate_override=cfg.reactor.heating_rate_c_min,
            residence_time_override=cfg.reactor.residence_time_min,
        )

        # 5. Step 3: Product Separation & Condensation Unit
        separator = ProductSeparator(config=cfg.separation)
        separation_result = separator.process(
            reactor_output=reactor_output,
        )

        # 6. Step 4: Mass Balance Verification
        mass_balance_summary = self.mass_balance_engine.compute_plant_mass_balance(
            raw_feed_rate_kg_h=cfg.feed_rate_kg_h,
            feedstock=feedstock,
            drying_result=drying_result,
            reactor_output=reactor_output,
            separation_result=separation_result,
        )

        # 7. Step 5: Energy Balance & KPI Accounting
        energy_balance_summary = self.energy_balance_engine.compute_plant_energy_balance(
            raw_feed_rate_kg_h=cfg.feed_rate_kg_h,
            feedstock=feedstock,
            drying_result=drying_result,
            reactor_output=reactor_output,
            separation_result=separation_result,
        )

        timestamp_str = datetime.now(timezone.utc).isoformat()

        return SimulationReport(
            scenario_config=cfg,
            feedstock=feedstock,
            drying=drying_result,
            reactor=reactor_output,
            separation=separation_result,
            mass_balance=mass_balance_summary,
            energy_balance=energy_balance_summary,
            timestamp=timestamp_str,
        )
