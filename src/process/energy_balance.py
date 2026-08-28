"""Plant-wide energy balance, thermal duty accounting, and thermodynamic KPI analysis.

Integrates thermal and electrical requirements across drying, pyrolysis reactor,
condensation train, and compares product chemical energy recovery vs feedstock energy inputs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List

from src.process.drying import DryingResult
from src.process.reactor import ReactorOutput
from src.process.separation import SeparationResult
from src.data.feedstock import BiomassFeedstock


@dataclass
class EnergyBalanceSummary:
    """Complete energy balance and performance metrics across the conversion plant."""
    # Thermal & Electrical Utility Demands (kW)
    drying_thermal_duty_kw: float
    reactor_thermal_duty_kw: float
    condenser_cooling_duty_kw: float
    auxiliary_electrical_power_kw: float
    total_external_energy_input_kw: float

    # Chemical Energy Rates (kW based on LHV)
    feedstock_chemical_power_kw: float
    biochar_chemical_power_kw: float
    bio_oil_chemical_power_kw: float
    syngas_chemical_power_kw: float
    total_products_chemical_power_kw: float

    # Key Performance Indicators (KPIs)
    energy_recovery_ratio_pct: float     # Total chemical energy in products / chemical energy in feed (%)
    bio_oil_energy_share_pct: float      # Chemical energy in bio-oil / chemical energy in feed (%)
    biochar_energy_share_pct: float      # Chemical energy in biochar / chemical energy in feed (%)
    syngas_energy_share_pct: float       # Chemical energy in syngas / chemical energy in feed (%)
    net_thermal_efficiency_pct: float    # (Product chemical energy - external heat/elec) / feed chemical energy (%)
    specific_energy_demand_kwh_kg_feed: float

    # Status & Warnings
    status: str
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "duties_kw": {
                "drying_thermal_duty_kw": round(self.drying_thermal_duty_kw, 3),
                "reactor_thermal_duty_kw": round(self.reactor_thermal_duty_kw, 3),
                "condenser_cooling_duty_kw": round(self.condenser_cooling_duty_kw, 3),
                "auxiliary_electrical_power_kw": round(self.auxiliary_electrical_power_kw, 3),
                "total_external_energy_input_kw": round(self.total_external_energy_input_kw, 3),
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
            "status": self.status,
            "warnings": self.warnings,
        }


class EnergyBalanceEngine:
    """Plant-wide energy and exergy balance calculator."""

    def __init__(self) -> None:
        pass

    def compute_plant_energy_balance(
        self,
        raw_feed_rate_kg_h: float,
        feedstock: BiomassFeedstock,
        drying_result: DryingResult,
        reactor_output: ReactorOutput,
        separation_result: SeparationResult,
    ) -> EnergyBalanceSummary:
        """Compute complete thermal, electrical, and chemical energy balances.

        Args:
            raw_feed_rate_kg_h: Raw biomass feed rate (kg/h).
            feedstock: BiomassFeedstock definition with calculated LHV/HHV.
            drying_result: Result from drying unit.
            reactor_output: Result from pyrolysis reactor unit.
            separation_result: Result from separation unit.

        Returns:
            EnergyBalanceSummary with full utility duties and efficiency KPIs.
        """
        # 1. Thermal and Utility Duties (kW)
        q_dry_kw = drying_result.thermal_duty_actual_kw
        q_pyro_kw = reactor_output.reactor_thermal_duty_kw
        q_cool_kw = separation_result.condenser_cooling_duty_kw
        p_elec_kw = drying_result.electrical_power_kw + separation_result.assumptions.get("auxiliary_power_kw", 1.5)

        total_external_kw = q_dry_kw + q_pyro_kw + p_elec_kw

        # 2. Chemical Energy Inflow (kW)
        lhv_feed_ar_mj_kg = feedstock.calculate_lhv_as_received()
        e_feed_chem_kw = (raw_feed_rate_kg_h * lhv_feed_ar_mj_kg * 1000.0) / 3600.0

        # 3. Chemical Energy Outflow in Products (kW)
        # Biochar LHV approx = HHV_char - 2.442 * (8.936 * H_char / 100) (approx 95% of HHV for low-H char)
        lhv_char_mj_kg = reactor_output.char_hhv_mj_kg * 0.95
        e_char_chem_kw = (separation_result.recovered_biochar_kg_h * lhv_char_mj_kg * 1000.0) / 3600.0

        # Bio-oil LHV
        lhv_oil_mj_kg = max(0.0, separation_result.liquid_bio_oil_hhv_mj_kg * 0.90)
        e_oil_chem_kw = (separation_result.recovered_bio_oil_liquid_kg_h * lhv_oil_mj_kg * 1000.0) / 3600.0

        # Syngas LHV
        lhv_gas_mj_kg = reactor_output.syngas_lhv_mj_kg
        e_gas_chem_kw = (separation_result.clean_syngas_kg_h * lhv_gas_mj_kg * 1000.0) / 3600.0

        e_products_total_kw = e_char_chem_kw + e_oil_chem_kw + e_gas_chem_kw

        # 4. Energy KPIs
        energy_recovery_pct = (e_products_total_kw / e_feed_chem_kw * 100.0) if e_feed_chem_kw > 0 else 0.0
        oil_energy_share_pct = (e_oil_chem_kw / e_feed_chem_kw * 100.0) if e_feed_chem_kw > 0 else 0.0
        char_energy_share_pct = (e_char_chem_kw / e_feed_chem_kw * 100.0) if e_feed_chem_kw > 0 else 0.0
        gas_energy_share_pct = (e_gas_chem_kw / e_feed_chem_kw * 100.0) if e_feed_chem_kw > 0 else 0.0

        net_efficiency_pct = (
            ((e_products_total_kw - total_external_kw) / e_feed_chem_kw * 100.0)
            if e_feed_chem_kw > 0 else 0.0
        )

        sec_kwh_kg = (total_external_kw / raw_feed_rate_kg_h) if raw_feed_rate_kg_h > 0 else 0.0

        warnings: List[str] = []
        status = "PASS"

        if total_external_kw > (0.35 * e_feed_chem_kw) and e_feed_chem_kw > 0:
            warnings.append(
                f"High parasitic thermal demand: external energy input is {total_external_kw/e_feed_chem_kw*100:.1f}% of feed LHV."
            )

        return EnergyBalanceSummary(
            drying_thermal_duty_kw=q_dry_kw,
            reactor_thermal_duty_kw=q_pyro_kw,
            condenser_cooling_duty_kw=q_cool_kw,
            auxiliary_electrical_power_kw=p_elec_kw,
            total_external_energy_input_kw=total_external_kw,
            feedstock_chemical_power_kw=e_feed_chem_kw,
            biochar_chemical_power_kw=e_char_chem_kw,
            bio_oil_chemical_power_kw=e_oil_chem_kw,
            syngas_chemical_power_kw=e_gas_chem_kw,
            total_products_chemical_power_kw=e_products_total_kw,
            energy_recovery_ratio_pct=energy_recovery_pct,
            bio_oil_energy_share_pct=oil_energy_share_pct,
            biochar_energy_share_pct=char_energy_share_pct,
            syngas_energy_share_pct=gas_energy_share_pct,
            net_thermal_efficiency_pct=net_efficiency_pct,
            specific_energy_demand_kwh_kg_feed=sec_kwh_kg,
            status=status,
            warnings=warnings,
        )
