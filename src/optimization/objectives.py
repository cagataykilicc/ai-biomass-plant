"""Objective functions, economic accounting, and thermodynamic KPI evaluations for plant optimization.

Defines single and multiobjective targets:
- Bio-oil recovery maximization
- Biochar carbon sequestration maximization
- Thermal and exergy efficiency maximization
- Gross hourly operational profit margin ($/h)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any

from src.simulation.plant_simulator import SimulationReport


class OptimizationObjective(str, Enum):
    """Enumeration of plant-level optimization targets."""
    MAX_BIO_OIL_YIELD = "MAX_BIO_OIL_YIELD"
    MAX_BIOCHAR_CARBON = "MAX_BIOCHAR_CARBON"
    MAX_THERMAL_EFFICIENCY = "MAX_THERMAL_EFFICIENCY"
    MAX_ECONOMIC_MARGIN = "MAX_ECONOMIC_MARGIN"
    MAX_EXERGY_EFFICIENCY = "MAX_EXERGY_EFFICIENCY"


@dataclass
class EconomicParameters:
    """Techno-economic market parameters and utility unit costs.

    Attributes:
        bio_oil_price_usd_kg: Market selling price for liquid bio-oil ($/kg).
        biochar_price_usd_kg: Market selling price for solid biochar ($/kg).
        syngas_surplus_credit_usd_kwh: Credit value for exported thermal/electrical energy ($/kWh).
        feedstock_cost_usd_tonne: Delivered cost of wet biomass feedstock ($/tonne).
        electricity_cost_usd_kwh: Industrial electrical power tariff ($/kWh).
        supplemental_heat_cost_usd_kwh: Cost of external fuel if TSI < 100% ($/kWh).
    """
    bio_oil_price_usd_kg: float = 0.55
    biochar_price_usd_kg: float = 0.85
    syngas_surplus_credit_usd_kwh: float = 0.05
    feedstock_cost_usd_tonne: float = 45.0
    electricity_cost_usd_kwh: float = 0.14
    supplemental_heat_cost_usd_kwh: float = 0.08

    def calculate_margin_usd_h(self, report: SimulationReport) -> Dict[str, float]:
        """Compute hourly revenues, operating expenses, and net gross margin ($/h)."""
        sep = report.separation
        comb = report.combustion
        eb = report.energy_balance
        cfg = report.scenario_config

        # 1. Revenues ($/h)
        rev_oil = sep.recovered_bio_oil_liquid_kg_h * self.bio_oil_price_usd_kg
        rev_char = sep.recovered_biochar_kg_h * self.biochar_price_usd_kg
        rev_surplus_heat = comb.surplus_heat_available_kw * self.syngas_surplus_credit_usd_kwh
        total_revenue = rev_oil + rev_char + rev_surplus_heat

        # 2. Operating Costs ($/h)
        cost_feedstock = (cfg.feed_rate_kg_h / 1000.0) * self.feedstock_cost_usd_tonne
        cost_electricity = eb.auxiliary_electrical_power_kw * self.electricity_cost_usd_kwh
        cost_supp_heat = comb.net_external_heat_required_kw * self.supplemental_heat_cost_usd_kwh
        total_opex = cost_feedstock + cost_electricity + cost_supp_heat

        # 3. Net Gross Profit ($/h)
        gross_margin = total_revenue - total_opex

        return {
            "revenue_bio_oil_usd_h": round(rev_oil, 3),
            "revenue_biochar_usd_h": round(rev_char, 3),
            "revenue_surplus_heat_usd_h": round(rev_surplus_heat, 3),
            "total_revenue_usd_h": round(total_revenue, 3),
            "cost_feedstock_usd_h": round(cost_feedstock, 3),
            "cost_electricity_usd_h": round(cost_electricity, 3),
            "cost_supplemental_heat_usd_h": round(cost_supp_heat, 3),
            "total_opex_usd_h": round(total_opex, 3),
            "gross_margin_usd_h": round(gross_margin, 3),
        }


class ObjectiveEvaluator:
    """Evaluates optimization objectives from simulation reports."""

    @staticmethod
    def evaluate(
        objective: OptimizationObjective,
        report: SimulationReport,
        econ_params: Optional[EconomicParameters] = None,
    ) -> float:
        """Calculate the scalar performance value to maximize (higher is always better)."""
        econ = econ_params or EconomicParameters()

        if objective == OptimizationObjective.MAX_BIO_OIL_YIELD:
            # Maximize recovered bio-oil mass rate in kg/h
            return float(report.separation.recovered_bio_oil_liquid_kg_h)

        elif objective == OptimizationObjective.MAX_BIOCHAR_CARBON:
            # Maximize recovered biochar mass rate in kg/h
            return float(report.separation.recovered_biochar_kg_h)

        elif objective == OptimizationObjective.MAX_THERMAL_EFFICIENCY:
            # Maximize plant net thermal efficiency in %
            return float(report.energy_balance.net_thermal_efficiency_pct)

        elif objective == OptimizationObjective.MAX_ECONOMIC_MARGIN:
            # Maximize gross profit margin in $/h
            econ_dict = econ.calculate_margin_usd_h(report)
            return float(econ_dict["gross_margin_usd_h"])

        elif objective == OptimizationObjective.MAX_EXERGY_EFFICIENCY:
            # Maximize Second-Law exergy efficiency in %
            ex_eff = (
                report.energy_balance.exergy.second_law_exergy_efficiency_pct
                if report.energy_balance.exergy else 80.0
            )
            return float(ex_eff)

        raise ValueError(f"Unknown optimization objective: {objective}")
