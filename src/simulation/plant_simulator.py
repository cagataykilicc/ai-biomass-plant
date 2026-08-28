"""Plant simulation engine orchestrating unit operations, elemental balances, ML models, and heat integration.

Executes end-to-end simulation workflows:
Feedstock -> Drying -> Pyrolysis Reactor (Deterministic or ML Surrogate) -> Separation ->
Syngas Speciation & Bio-oil Grouping -> Combustor & Heat Integration -> Mass & Elemental Balances -> Energy & Exergy Accounting.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path
import json

from src.data.feedstock import BiomassFeedstock
from src.data.preprocessing import FeedstockLibrary
from src.process.drying import BiomassDryer, DryingResult
from src.process.reactor import PyrolysisReactor, ReactorOutput
from src.process.separation import ProductSeparator, SeparationResult
from src.process.combustor import SyngasCombustor, CombustionResult
from src.process.mass_balance import MassBalanceEngine, MassBalanceSummary
from src.process.elemental_balance import ElementalBalanceEngine, PlantElementalBalanceSummary
from src.process.energy_balance import EnergyBalanceEngine, EnergyBalanceSummary
from src.models.syngas_model import SyngasSpeciationModel, SyngasComposition
from src.models.bio_oil_model import BioOilPropertyModel, BioOilChemicalGrouping
from src.ml.yield_predictor import YieldPredictorModel
from src.utils.config import PlantScenarioConfig


@dataclass
class SimulationReport:
    """Consolidated simulation result report for the entire plant."""
    scenario_config: PlantScenarioConfig
    feedstock: BiomassFeedstock
    drying: DryingResult
    reactor: ReactorOutput
    separation: SeparationResult
    syngas: SyngasComposition
    bio_oil: BioOilChemicalGrouping
    combustion: CombustionResult
    mass_balance: MassBalanceSummary
    elemental_balance: PlantElementalBalanceSummary
    energy_balance: EnergyBalanceSummary
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": {
                "version": "0.4.0",
                "timestamp": self.timestamp,
                "plant_status": "OPERATIONAL",
                "yield_engine_used": self.reactor.yield_engine_used,
                "mass_balance_status": self.mass_balance.status,
                "elemental_balance_status": self.elemental_balance.overall_status,
                "energy_balance_status": self.energy_balance.status,
                "thermal_self_sufficiency": self.combustion.is_thermally_self_sufficient,
            },
            "feedstock": self.feedstock.to_dict(),
            "drying_section": self.drying.to_dict(),
            "reactor_section": self.reactor.to_dict(),
            "separation_section": self.separation.to_dict(),
            "syngas_speciation": self.syngas.to_dict(),
            "bio_oil_characterization": self.bio_oil.to_dict(),
            "combustor_heat_integration": self.combustion.to_dict(),
            "mass_balance": self.mass_balance.to_dict(),
            "elemental_balance": self.elemental_balance.to_dict(),
            "energy_balance": self.energy_balance.to_dict(),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class BiomassPlantSimulator:
    """Core simulation orchestrator for the virtual biomass conversion plant."""

    def __init__(
        self,
        feedstock_library: Optional[FeedstockLibrary] = None,
        ml_yield_predictor: Optional[YieldPredictorModel] = None,
    ) -> None:
        self.feedstock_library = feedstock_library or FeedstockLibrary()
        self.syngas_model = SyngasSpeciationModel()
        self.bio_oil_model = BioOilPropertyModel()
        self.mass_balance_engine = MassBalanceEngine()
        self.elemental_balance_engine = ElementalBalanceEngine()
        self.energy_balance_engine = EnergyBalanceEngine()
        self.ml_yield_predictor = ml_yield_predictor or self._try_load_default_ml_model()

    def _try_load_default_ml_model(self) -> Optional[YieldPredictorModel]:
        """Try loading default trained ML yield surrogate if present."""
        default_ckpt = Path(__file__).resolve().parent.parent.parent / "models" / "checkpoints" / "yield_predictor_rf.joblib"
        if default_ckpt.is_file():
            try:
                return YieldPredictorModel.load(default_ckpt)
            except Exception:
                return None
        return None

    def run_simulation(
        self,
        scenario: Optional[PlantScenarioConfig] = None,
        feedstock_name: Optional[str] = None,
        feed_rate_kg_h: Optional[float] = None,
        moisture_pct: Optional[float] = None,
        reactor_temp_c: Optional[float] = None,
        heating_rate_c_min: Optional[float] = None,
        residence_time_min: Optional[float] = None,
        yield_mode: Optional[str] = None,
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
            yield_mode: Optional override for yield engine ("DETERMINISTIC" vs "ML_SURROGATE").

        Returns:
            SimulationReport with detailed stream, unit, speciation, and balance information.
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
        if yield_mode is not None:
            cfg.reactor.yield_mode = yield_mode.upper()

        cfg.validate()

        # 2. Ingest and Validate Feedstock
        feedstock = self.feedstock_library.load_feedstock(
            name_or_path=cfg.feedstock_name,
            moisture_override=cfg.moisture_pct_override,
            particle_size_override=cfg.particle_size_mm_override,
        )

        # 3. Step 1: Drying / Pretreatment Unit (D101)
        dryer = BiomassDryer(config=cfg.drying)
        drying_result = dryer.process(
            feed_rate_kg_h=cfg.feed_rate_kg_h,
            feedstock=feedstock,
        )

        # 4. Step 2: Pyrolysis Reactor Unit (R101)
        reactor = PyrolysisReactor(
            config=cfg.reactor,
            ml_yield_predictor=self.ml_yield_predictor,
        )
        reactor_output = reactor.process(
            dried_feed_rate_kg_h=drying_result.dried_feed_rate_out_kg_h,
            residual_moisture_pct=drying_result.final_moisture_pct,
            feedstock=feedstock,
            temp_override=cfg.reactor.temperature_c,
            heating_rate_override=cfg.reactor.heating_rate_c_min,
            residence_time_override=cfg.reactor.residence_time_min,
            yield_mode_override=cfg.reactor.yield_mode,
        )

        # 5. Step 3: Product Separation & Condensation Unit (C101, E101)
        separator = ProductSeparator(config=cfg.separation)
        separation_result = separator.process(
            reactor_output=reactor_output,
        )

        # 6. Step 4: Syngas Molecular Speciation & Thermodynamics
        syngas_comp = self.syngas_model.predict_speciation(
            temperature_c=reactor_output.operating_temperature_c,
            syngas_mass_flow_kg_h=separation_result.clean_syngas_kg_h - reactor_output.carrier_gas_kg_h,
            carrier_gas_n2_kg_h=reactor_output.carrier_gas_kg_h,
            feedstock=feedstock,
        )

        # 7. Step 5: Bio-oil Chemical Grouping & Property Characterization
        bio_oil_grouping = self.bio_oil_model.evaluate_bio_oil(
            organics_flow_kg_h=separation_result.bio_oil_organics_kg_h,
            water_flow_kg_h=separation_result.bio_oil_water_kg_h,
            temperature_c=reactor_output.operating_temperature_c,
            feedstock=feedstock,
            raw_bio_oil_hhv=separation_result.liquid_bio_oil_hhv_mj_kg,
        )

        # 8. Step 6: Syngas Combustor & Heat Integration (B101, HX101)
        gross_thermal_demand = drying_result.thermal_duty_actual_kw + reactor_output.reactor_thermal_duty_kw
        combustor = SyngasCombustor(config=cfg.combustor)
        combustion_result = combustor.process(
            syngas=syngas_comp,
            total_plant_thermal_demand_kw=gross_thermal_demand,
        )

        # 9. Step 7: Plant-wide Overall Mass Balance
        mass_balance_summary = self.mass_balance_engine.compute_plant_mass_balance(
            raw_feed_rate_kg_h=cfg.feed_rate_kg_h,
            feedstock=feedstock,
            drying_result=drying_result,
            reactor_output=reactor_output,
            separation_result=separation_result,
        )

        # 10. Step 8: Atom-by-Atom Elemental Conservation (C, H, O, N, S, Ash)
        elemental_balance_summary = self.elemental_balance_engine.compute_elemental_balance(
            raw_feed_rate_kg_h=cfg.feed_rate_kg_h,
            feedstock=feedstock,
            drying_result=drying_result,
            reactor_output=reactor_output,
            separation_result=separation_result,
            syngas_comp=syngas_comp,
            bio_oil_grouping=bio_oil_grouping,
        )

        # 11. Step 9: Energy Balance, Combustor Integration & Exergy Accounting
        energy_balance_summary = self.energy_balance_engine.compute_plant_energy_balance(
            raw_feed_rate_kg_h=cfg.feed_rate_kg_h,
            feedstock=feedstock,
            drying_result=drying_result,
            reactor_output=reactor_output,
            separation_result=separation_result,
            combustion_result=combustion_result,
        )

        timestamp_str = datetime.now(timezone.utc).isoformat()

        return SimulationReport(
            scenario_config=cfg,
            feedstock=feedstock,
            drying=drying_result,
            reactor=reactor_output,
            separation=separation_result,
            syngas=syngas_comp,
            bio_oil=bio_oil_grouping,
            combustion=combustion_result,
            mass_balance=mass_balance_summary,
            elemental_balance=elemental_balance_summary,
            energy_balance=energy_balance_summary,
            timestamp=timestamp_str,
        )
