"""Plant-wide energy and exergy balance accounting, heat integration, and Second-Law efficiency.

Integrates thermal and electrical utility demands, chemical energy recovery,
syngas combustor heat integration, and Second-Law exergy destruction calculations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import math

from src.process.drying import DryingResult
from src.process.reactor import ReactorOutput
from src.process.separation import SeparationResult
from src.process.combustor import CombustionResult
from src.data.feedstock import BiomassFeedstock


@dataclass
class ExergyBalanceSummary:
    """Second-Law thermodynamic exergy flows and unit destruction rates (kW)."""
    feedstock_chemical_exergy_kw: float
    biochar_exergy_kw: float
    bio_oil_exergy_kw: float
    syngas_exergy_kw: float
    total_products_exergy_kw: float
    drying_exergy_loss_kw: float
    reactor_exergy_destruction_kw: float
    condenser_exergy_destruction_kw: float
    combustor_exergy_destruction_kw: float
    total_plant_exergy_destruction_kw: float
    second_law_exergy_efficiency_pct: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feedstock_chemical_exergy_kw": round(self.feedstock_chemical_exergy_kw, 2),
            "total_products_exergy_kw": round(self.total_products_exergy_kw, 2),
            "biochar_exergy_kw": round(self.biochar_exergy_kw, 2),
            "bio_oil_exergy_kw": round(self.bio_oil_exergy_kw, 2),
            "syngas_exergy_kw": round(self.syngas_exergy_kw, 2),
            "total_plant_exergy_destruction_kw": round(self.total_plant_exergy_destruction_kw, 2),
            "second_law_exergy_efficiency_pct": round(self.second_law_exergy_efficiency_pct, 2),
        }


@dataclass
class EnergyBalanceSummary:
    """Complete energy balance, heat integration, and performance metrics."""
    # Thermal & Electrical Demands (kW)
    drying_thermal_duty_kw: float
    reactor_thermal_duty_kw: float
    condenser_cooling_duty_kw: float
    auxiliary_electrical_power_kw: float
    gross_thermal_demand_kw: float

    # Heat Integration & Combustor Utilization
    heat_recovered_from_syngas_kw: float
    net_external_heat_required_kw: float
    surplus_thermal_power_kw: float
    thermal_self_sufficiency_index_pct: float
    is_thermally_self_sufficient: bool
    total_net_external_power_kw: float

    # Chemical Energy Rates (kW based on LHV)
    feedstock_chemical_power_kw: float
    biochar_chemical_power_kw: float
    bio_oil_chemical_power_kw: float
    syngas_chemical_power_kw: float
    total_products_chemical_power_kw: float

    # First-Law KPIs
    energy_recovery_ratio_pct: float
    bio_oil_energy_share_pct: float
    biochar_energy_share_pct: float
    syngas_energy_share_pct: float
    gross_thermal_efficiency_pct: float
    net_thermal_efficiency_pct: float
    specific_energy_demand_kwh_kg_feed: float

    # Second-Law Exergy Summary
    exergy: Optional[ExergyBalanceSummary] = None

    # Status & Warnings
    status: str = "PASS"
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "duties_kw": {
                "drying_thermal_duty_kw": round(self.drying_thermal_duty_kw, 3),
                "reactor_thermal_duty_kw": round(self.reactor_thermal_duty_kw, 3),
                "condenser_cooling_duty_kw": round(self.condenser_cooling_duty_kw, 3),
                "auxiliary_electrical_power_kw": round(self.auxiliary_electrical_power_kw, 3),
                "gross_thermal_demand_kw": round(self.gross_thermal_demand_kw, 3),
                "heat_recovered_from_syngas_kw": round(self.heat_recovered_from_syngas_kw, 3),
                "net_external_heat_required_kw": round(self.net_external_heat_required_kw, 3),
                "surplus_thermal_power_kw": round(self.surplus_thermal_power_kw, 3),
                "total_net_external_power_kw": round(self.total_net_external_power_kw, 3),
            },
            "heat_integration": {
                "thermal_self_sufficiency_index_pct": round(self.thermal_self_sufficiency_index_pct, 2),
                "is_thermally_self_sufficient": self.is_thermally_self_sufficient,
            },
            "chemical_energy_rates_kw": {
                "feedstock_chemical_power_kw": round(self.feedstock_chemical_power_kw, 3),
                "biochar_chemical_power_kw": round(self.biochar_chemical_power_kw, 3),
                "bio_oil_chemical_power_kw": round(self.bio_oil_chemical_power_kw, 3),
                "syngas_chemical_power_kw": round(self.syngas_chemical_power_kw, 3),
                "total_products_chemical_power_kw": round(self.total_products_chemical_power_kw, 3),
            },
            "kpis": {
                "energy_recovery_ratio_pct": round(self.energy_recovery_ratio_pct, 2),
                "bio_oil_energy_share_pct": round(self.bio_oil_energy_share_pct, 2),
                "biochar_energy_share_pct": round(self.biochar_energy_share_pct, 2),
                "syngas_energy_share_pct": round(self.syngas_energy_share_pct, 2),
                "net_thermal_efficiency_pct": round(self.net_thermal_efficiency_pct, 2),
                "specific_energy_demand_kwh_kg_feed": round(self.specific_energy_demand_kwh_kg_feed, 4),
            },
            "exergy": self.exergy.to_dict() if self.exergy else None,
            "status": self.status,
            "warnings": self.warnings,
        }


class EnergyBalanceEngine:
    """Plant-wide energy and exergy balance calculator with heat integration."""

    def __init__(self) -> None:
        pass

    def compute_plant_energy_balance(
        self,
        raw_feed_rate_kg_h: float,
        feedstock: BiomassFeedstock,
        drying_result: DryingResult,
        reactor_output: ReactorOutput,
        separation_result: SeparationResult,
        combustion_result: Optional[CombustionResult] = None,
    ) -> EnergyBalanceSummary:
        """Compute First and Second Law energy balances and heat integration.

        Args:
            raw_feed_rate_kg_h: Raw biomass feed rate (kg/h).
            feedstock: BiomassFeedstock definition with LHV/HHV.
            drying_result: Outputs from drying unit.
            reactor_output: Outputs from pyrolysis reactor unit.
            separation_result: Outputs from separation unit.
            combustion_result: Optional outputs from syngas combustor unit.

        Returns:
            EnergyBalanceSummary with full utility duties, self-sufficiency, and exergy.
        """
        # 1. Thermal and Utility Duties (kW)
        q_dry_kw = drying_result.thermal_duty_actual_kw
        q_pyro_kw = reactor_output.reactor_thermal_duty_kw
        q_cool_kw = separation_result.condenser_cooling_duty_kw
        p_elec_kw = drying_result.electrical_power_kw + separation_result.assumptions.get("auxiliary_power_kw", 1.5)
        gross_thermal_demand_kw = q_dry_kw + q_pyro_kw

        # 2. Heat Integration via Syngas Combustor
        if combustion_result is not None:
            q_recovered_kw = combustion_result.thermal_heat_recovered_kw
            net_ext_heat_kw = combustion_result.net_external_heat_required_kw
            surplus_heat_kw = combustion_result.surplus_heat_available_kw
            tsi_pct = combustion_result.thermal_self_sufficiency_index_pct
            is_self_sufficient = combustion_result.is_thermally_self_sufficient
        else:
            q_recovered_kw = 0.0
            net_ext_heat_kw = gross_thermal_demand_kw
            surplus_heat_kw = 0.0
            tsi_pct = 0.0
            is_self_sufficient = False

        total_net_external_power_kw = net_ext_heat_kw + p_elec_kw

        # 3. Chemical Energy Inflow (kW)
        lhv_feed_ar_mj_kg = feedstock.calculate_lhv_as_received()
        e_feed_chem_kw = (raw_feed_rate_kg_h * lhv_feed_ar_mj_kg * 1000.0) / 3600.0

        # 4. Chemical Energy Outflow in Products (kW)
        lhv_char_mj_kg = reactor_output.char_hhv_mj_kg * 0.95
        e_char_chem_kw = (separation_result.recovered_biochar_kg_h * lhv_char_mj_kg * 1000.0) / 3600.0

        lhv_oil_mj_kg = max(0.0, separation_result.liquid_bio_oil_hhv_mj_kg * 0.90)
        e_oil_chem_kw = (separation_result.recovered_bio_oil_liquid_kg_h * lhv_oil_mj_kg * 1000.0) / 3600.0

        lhv_gas_mj_kg = reactor_output.syngas_lhv_mj_kg
        e_gas_chem_kw = (separation_result.clean_syngas_kg_h * lhv_gas_mj_kg * 1000.0) / 3600.0

        e_products_total_kw = e_char_chem_kw + e_oil_chem_kw + e_gas_chem_kw

        # 5. First-Law Energy KPIs
        energy_recovery_pct = (e_products_total_kw / e_feed_chem_kw * 100.0) if e_feed_chem_kw > 0 else 0.0
        oil_energy_share_pct = (e_oil_chem_kw / e_feed_chem_kw * 100.0) if e_feed_chem_kw > 0 else 0.0
        char_energy_share_pct = (e_char_chem_kw / e_feed_chem_kw * 100.0) if e_feed_chem_kw > 0 else 0.0
        syngas_energy_share_pct = (e_gas_chem_kw / e_feed_chem_kw * 100.0) if e_feed_chem_kw > 0 else 0.0

        gross_thermal_eff_pct = (
            ((e_products_total_kw - (gross_thermal_demand_kw + p_elec_kw)) / e_feed_chem_kw * 100.0)
            if e_feed_chem_kw > 0 else 0.0
        )

        net_efficiency_pct = (
            ((e_products_total_kw - total_net_external_power_kw) / e_feed_chem_kw * 100.0)
            if e_feed_chem_kw > 0 else 0.0
        )

        sec_kwh_kg = (total_net_external_power_kw / raw_feed_rate_kg_h) if raw_feed_rate_kg_h > 0 else 0.0

        # 6. Second-Law Exergy Balance (Szargut statistical chemical exergy correlation)
        # Ratio of chemical exergy to LHV for solid biomass (Szargut / Kotas correlation)
        c_wt = feedstock.ultimate.carbon / 100.0
        h_wt = feedstock.ultimate.hydrogen / 100.0
        o_wt = feedstock.ultimate.oxygen / 100.0
        n_wt = feedstock.ultimate.nitrogen / 100.0

        phi_bio = 1.0437 + (0.1882 * (h_wt / max(0.01, c_wt))) - (0.053 * (o_wt / max(0.01, c_wt))) + (0.040 * (n_wt / max(0.01, c_wt)))
        ex_feed_kw = e_feed_chem_kw * phi_bio

        # Product exergies
        ex_char_kw = e_char_chem_kw * 1.06
        ex_oil_kw = e_oil_chem_kw * 1.04
        ex_gas_kw = e_gas_chem_kw * 0.98
        ex_products_total_kw = ex_char_kw + ex_oil_kw + ex_gas_kw

        # Exergy destruction in units
        ex_dest_dry = q_dry_kw * (1.0 - (298.15 / 378.15))
        ex_dest_pyro = q_pyro_kw * (1.0 - (298.15 / (reactor_output.operating_temperature_c + 273.15))) + (e_feed_chem_kw - e_products_total_kw) * 0.15
        ex_dest_cond = q_cool_kw * (1.0 - (298.15 / 333.15))
        ex_dest_comb = (combustion_result.thermal_heat_released_kw * 0.30) if combustion_result else 0.0

        total_ex_dest = ex_dest_dry + ex_dest_pyro + ex_dest_cond + ex_dest_comb
        second_law_eff = (ex_products_total_kw / (ex_feed_kw + total_net_external_power_kw) * 100.0) if (ex_feed_kw + total_net_external_power_kw) > 0 else 0.0

        exergy_summary = ExergyBalanceSummary(
            feedstock_chemical_exergy_kw=ex_feed_kw,
            biochar_exergy_kw=ex_char_kw,
            bio_oil_exergy_kw=ex_oil_kw,
            syngas_exergy_kw=ex_gas_kw,
            total_products_exergy_kw=ex_products_total_kw,
            drying_exergy_loss_kw=ex_dest_dry,
            reactor_exergy_destruction_kw=ex_dest_pyro,
            condenser_exergy_destruction_kw=ex_dest_cond,
            combustor_exergy_destruction_kw=ex_dest_comb,
            total_plant_exergy_destruction_kw=total_ex_dest,
            second_law_exergy_efficiency_pct=second_law_eff,
        )

        warnings: List[str] = []
        status = "PASS"

        if is_self_sufficient:
            warnings.append("Plant operates in full thermal self-sufficiency via syngas heat recovery.")

        return EnergyBalanceSummary(
            drying_thermal_duty_kw=q_dry_kw,
            reactor_thermal_duty_kw=q_pyro_kw,
            condenser_cooling_duty_kw=q_cool_kw,
            auxiliary_electrical_power_kw=p_elec_kw,
            gross_thermal_demand_kw=gross_thermal_demand_kw,
            heat_recovered_from_syngas_kw=q_recovered_kw,
            net_external_heat_required_kw=net_ext_heat_kw,
            surplus_thermal_power_kw=surplus_heat_kw,
            thermal_self_sufficiency_index_pct=tsi_pct,
            is_thermally_self_sufficient=is_self_sufficient,
            total_net_external_power_kw=total_net_external_power_kw,
            feedstock_chemical_power_kw=e_feed_chem_kw,
            biochar_chemical_power_kw=e_char_chem_kw,
            bio_oil_chemical_power_kw=e_oil_chem_kw,
            syngas_chemical_power_kw=e_gas_chem_kw,
            total_products_chemical_power_kw=e_products_total_kw,
            energy_recovery_ratio_pct=energy_recovery_pct,
            bio_oil_energy_share_pct=oil_energy_share_pct,
            biochar_energy_share_pct=char_energy_share_pct,
            syngas_energy_share_pct=syngas_energy_share_pct,
            gross_thermal_efficiency_pct=gross_thermal_eff_pct,
            net_thermal_efficiency_pct=net_efficiency_pct,
            specific_energy_demand_kwh_kg_feed=sec_kwh_kg,
            exergy=exergy_summary,
            status=status,
            warnings=warnings,
        )
