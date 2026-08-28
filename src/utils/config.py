"""Configuration management and scenario loader for biomass plant simulations.

Handles YAML parsing, schema validation, scenario overrides, and plant baseline parameters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional, Union
import yaml

from src.process.drying import DryingConfig
from src.process.reactor import ReactorConfig
from src.process.separation import SeparationConfig


@dataclass
class PlantScenarioConfig:
    """Complete operating scenario configuration for the biomass plant."""
    feedstock_name: str = "olive_pomace"
    feed_rate_kg_h: float = 100.0
    moisture_pct_override: Optional[float] = 15.0
    particle_size_mm_override: Optional[float] = 2.0
    
    # Unit configurations
    drying: DryingConfig = field(default_factory=DryingConfig)
    reactor: ReactorConfig = field(default_factory=ReactorConfig)
    separation: SeparationConfig = field(default_factory=SeparationConfig)

    def validate(self) -> None:
        """Validate scenario bounds."""
        if self.feed_rate_kg_h <= 0.0:
            raise ValueError(f"Feed rate must be > 0 kg/h. Got: {self.feed_rate_kg_h}")
        if self.moisture_pct_override is not None and not (0.0 <= self.moisture_pct_override <= 90.0):
            raise ValueError(f"Moisture override must be in [0, 90] wt%. Got: {self.moisture_pct_override}")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PlantScenarioConfig:
        feedstock_name = data.get("feedstock", {}).get("name", data.get("feedstock_name", "olive_pomace"))
        feed_rate = float(data.get("feed_rate_kg_h", data.get("feedstock", {}).get("feed_rate_kg_h", 100.0)))
        moisture_override = data.get("feedstock", {}).get("moisture_pct")
        if moisture_override is None and "moisture_pct" in data:
            moisture_override = data["moisture_pct"]

        particle_override = data.get("feedstock", {}).get("particle_size_mm")

        # Drying section
        dry_data = data.get("drying", {})
        drying = DryingConfig(
            target_moisture_pct=float(dry_data.get("target_moisture_pct", 8.0)),
            dryer_temperature_c=float(dry_data.get("dryer_temperature_c", 105.0)),
            ambient_temperature_c=float(dry_data.get("ambient_temperature_c", 25.0)),
            thermal_efficiency=float(dry_data.get("thermal_efficiency", 0.75)),
            specific_electrical_consumption_kwh_tonne=float(dry_data.get("specific_electrical_consumption_kwh_tonne", 15.0)),
        )

        # Reactor section
        rxn_data = data.get("reactor", {})
        reactor = ReactorConfig(
            temperature_c=float(rxn_data.get("temperature_c", data.get("temperature_c", 500.0))),
            heating_rate_c_min=float(rxn_data.get("heating_rate_c_min", data.get("heating_rate_c_min", 10.0))),
            residence_time_min=float(rxn_data.get("residence_time_min", data.get("residence_time_min", 20.0))),
            reaction_enthalpy_kj_kg=float(rxn_data.get("reaction_enthalpy_kj_kg", 300.0)),
            heat_loss_fraction=float(rxn_data.get("heat_loss_fraction", 0.08)),
            carrier_gas_flow_kg_h=float(rxn_data.get("carrier_gas_flow_kg_h", 0.0)),
        )

        # Separation section
        sep_data = data.get("separation", {})
        separation = SeparationConfig(
            cyclone_efficiency=float(sep_data.get("cyclone_efficiency", 0.985)),
            condenser_efficiency=float(sep_data.get("condenser_efficiency", 0.960)),
            condenser_exit_temp_c=float(sep_data.get("condenser_exit_temp_c", 35.0)),
            cooling_water_inlet_c=float(sep_data.get("cooling_water_inlet_c", 20.0)),
            cooling_water_outlet_c=float(sep_data.get("cooling_water_outlet_c", 32.0)),
        )

        cfg = cls(
            feedstock_name=feedstock_name,
            feed_rate_kg_h=feed_rate,
            moisture_pct_override=float(moisture_override) if moisture_override is not None else None,
            particle_size_mm_override=float(particle_override) if particle_override is not None else None,
            drying=drying,
            reactor=reactor,
            separation=separation,
        )
        cfg.validate()
        return cfg


class ConfigManager:
    """Helper to load and resolve simulation configuration files."""

    @staticmethod
    def load_config_file(config_path: Union[str, Path]) -> PlantScenarioConfig:
        path = Path(config_path)
        if not path.is_file():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        return PlantScenarioConfig.from_dict(data)

    @staticmethod
    def get_default_config() -> PlantScenarioConfig:
        return PlantScenarioConfig(
            feedstock_name="olive_pomace",
            feed_rate_kg_h=100.0,
            moisture_pct_override=15.0,
            particle_size_mm_override=2.0,
        )
