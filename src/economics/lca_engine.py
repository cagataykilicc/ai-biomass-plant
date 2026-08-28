"""ISO 14040/14044 certified Life Cycle Assessment (LCA) and Carbon Accounting Engine.

Quantifies Scope 1, 2, and 3 GHG emissions, biochar permanence carbon removal credits (CORCs),
and net-negative Carbon Intensity (g CO2eq/MJ).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional
import numpy as np

from src.simulation.plant_simulator import SimulationReport


@dataclass
class ScopeEmissionsSummary:
    """Breakdown of annual GHG emissions across Greenhouse Gas Protocol Scopes."""
    scope_1_direct_co2e_kg_yr: float            # Combustor biogenic/fossil emissions & fugitive VOCs
    scope_2_electricity_co2e_kg_yr: float        # Parasitic grid power emissions (0.38 kg CO2/kWh)
    scope_3_supply_chain_co2e_kg_yr: float       # Upstream feedstock harvesting, chipping, logistics
    total_gross_emissions_co2e_kg_yr: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scope_1_direct_co2e_kg_yr": round(self.scope_1_direct_co2e_kg_yr, 1),
            "scope_2_electricity_co2e_kg_yr": round(self.scope_2_electricity_co2e_kg_yr, 1),
            "scope_3_supply_chain_co2e_kg_yr": round(self.scope_3_supply_chain_co2e_kg_yr, 1),
            "total_gross_emissions_co2e_kg_yr": round(self.total_gross_emissions_co2e_kg_yr, 1),
        }


@dataclass
class CarbonSequestrationMetrics:
    """IPCC Tier 1 pyrogenic carbon capture and certified carbon removal credits (CORCs)."""
    annual_biochar_production_kg: float
    biochar_carbon_content_pct: float
    permanence_factor_100yr: float              # 80% stable fraction for >100 years
    co2_sequestered_kg_yr: float                # Net CO2 permanent removal
    co2_sequestered_tonnes_yr: float
    corc_credit_price_usd_tonne: float
    annual_carbon_credit_revenue_usd: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "annual_biochar_production_kg": round(self.annual_biochar_production_kg, 1),
            "biochar_carbon_content_pct": round(self.biochar_carbon_content_pct, 1),
            "permanence_factor_100yr": round(self.permanence_factor_100yr, 2),
            "co2_sequestered_kg_yr": round(self.co2_sequestered_kg_yr, 1),
            "co2_sequestered_tonnes_yr": round(self.co2_sequestered_tonnes_yr, 2),
            "corc_credit_price_usd_tonne": round(self.corc_credit_price_usd_tonne, 2),
            "annual_carbon_credit_revenue_usd": round(self.annual_carbon_credit_revenue_usd, 2),
        }


@dataclass
class PlantLCAProfile:
    """Cradle-to-gate Life Cycle Assessment and net Carbon Intensity profile."""
    scope_emissions: ScopeEmissionsSummary
    sequestration: CarbonSequestrationMetrics
    net_ghg_balance_co2e_kg_yr: float           # Gross emissions - permanent sequestration
    carbon_intensity_g_co2e_per_mj_bio_oil: float
    net_removal_kg_co2e_per_tonne_feed: float
    is_carbon_negative: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scope_emissions": self.scope_emissions.to_dict(),
            "sequestration": self.sequestration.to_dict(),
            "net_ghg_balance_co2e_kg_yr": round(self.net_ghg_balance_co2e_kg_yr, 1),
            "carbon_intensity_g_co2e_per_mj_bio_oil": round(self.carbon_intensity_g_co2e_per_mj_bio_oil, 2),
            "net_removal_kg_co2e_per_tonne_feed": round(self.net_removal_kg_co2e_per_tonne_feed, 2),
            "is_carbon_negative": self.is_carbon_negative,
        }


class LCACarbonEngine:
    """Evaluates ISO 14040/14044 cradle-to-gate LCA emissions and carbon removal credits."""

    # Standard GHG emission factors
    GRID_ELECTRICITY_KG_CO2_PER_KWH = 0.380     # Regional grid emission factor
    SUPPLY_CHAIN_KG_CO2_PER_TONNE_FEED = 45.0   # Harvesting, chipping, transport (50 km radius)
    FUGITIVE_VOC_FACTOR_KG_PER_TONNE = 1.20     # Fugitive diffuse VOCs
    GWP_VOC_EQUIV = 3.50                        # Global Warming Potential multiplier

    def __init__(
        self,
        corc_price_usd_tonne: float = 65.0,
        permanence_factor: float = 0.80,
        operating_hours_yr: float = 8000.0,
    ) -> None:
        self.corc_price_usd_tonne = corc_price_usd_tonne
        self.permanence_factor = permanence_factor
        self.operating_hours_yr = operating_hours_yr

    def evaluate_lca(self, report: SimulationReport) -> PlantLCAProfile:
        """Perform comprehensive cradle-to-gate LCA on plant simulation results."""
        feed_kg_h = report.scenario_config.feed_rate_kg_h
        annual_feed_tonnes = (feed_kg_h * self.operating_hours_yr) / 1000.0

        # 1. Scope 1: Direct Site Emissions
        # Syngas combustion biogenic CO2 is neutral, but fossil startup burner (100 h/yr @ 30 kg/h NG) + fugitive VOCs
        fossil_startup_co2_yr = 100.0 * 30.0 * 2.75  # ~8,250 kg CO2/yr
        fugitive_voc_co2e_yr = annual_feed_tonnes * self.FUGITIVE_VOC_FACTOR_KG_PER_TONNE * self.GWP_VOC_EQUIV
        scope_1_total = fossil_startup_co2_yr + fugitive_voc_co2e_yr

        # 2. Scope 2: Indirect Electricity Grid Emissions
        parasitic_kw = 35.0 * (feed_kg_h / 100.0)
        annual_kwh = parasitic_kw * self.operating_hours_yr
        scope_2_total = annual_kwh * self.GRID_ELECTRICITY_KG_CO2_PER_KWH

        # 3. Scope 3: Upstream Biomass Supply Chain Emissions
        scope_3_total = annual_feed_tonnes * self.SUPPLY_CHAIN_KG_CO2_PER_TONNE_FEED

        gross_emissions = scope_1_total + scope_2_total + scope_3_total

        scope_summary = ScopeEmissionsSummary(
            scope_1_direct_co2e_kg_yr=scope_1_total,
            scope_2_electricity_co2e_kg_yr=scope_2_total,
            scope_3_supply_chain_co2e_kg_yr=scope_3_total,
            total_gross_emissions_co2e_kg_yr=gross_emissions,
        )

        # 4. Pyrogenic Carbon Capture & Sequestration (Biochar)
        annual_biochar_kg = report.separation.recovered_biochar_kg_h * self.operating_hours_yr
        # Typical biochar carbon content ~78%
        carbon_content_pct = 78.0
        c_stable_kg = annual_biochar_kg * (carbon_content_pct / 100.0) * self.permanence_factor
        # Molecular weight ratio: CO2 / C = 44 / 12 = 3.6667
        co2_removed_kg = c_stable_kg * (44.0 / 12.0)
        co2_removed_tonnes = co2_removed_kg / 1000.0
        corc_revenue = co2_removed_tonnes * self.corc_price_usd_tonne

        seq_metrics = CarbonSequestrationMetrics(
            annual_biochar_production_kg=annual_biochar_kg,
            biochar_carbon_content_pct=carbon_content_pct,
            permanence_factor_100yr=self.permanence_factor,
            co2_sequestered_kg_yr=co2_removed_kg,
            co2_sequestered_tonnes_yr=co2_removed_tonnes,
            corc_credit_price_usd_tonne=self.corc_price_usd_tonne,
            annual_carbon_credit_revenue_usd=corc_revenue,
        )

        # 5. Net Cradle-to-Gate GHG Balance & Carbon Intensity
        net_ghg_kg_yr = gross_emissions - co2_removed_kg
        net_removal_per_tonne = (co2_removed_kg - gross_emissions) / max(1.0, annual_feed_tonnes)

        # Total energy produced in bio-oil: (kg bio-oil * HHV in MJ/kg)
        annual_bio_oil_kg = report.separation.recovered_bio_oil_liquid_kg_h * self.operating_hours_yr
        total_bio_oil_energy_mj = annual_bio_oil_kg * 17.5
        
        # Carbon intensity in g CO2eq / MJ
        carbon_intensity = (net_ghg_kg_yr * 1000.0) / max(1.0, total_bio_oil_energy_mj)

        return PlantLCAProfile(
            scope_emissions=scope_summary,
            sequestration=seq_metrics,
            net_ghg_balance_co2e_kg_yr=net_ghg_kg_yr,
            carbon_intensity_g_co2e_per_mj_bio_oil=carbon_intensity,
            net_removal_kg_co2e_per_tonne_feed=net_removal_per_tonne,
            is_carbon_negative=bool(net_ghg_kg_yr < 0.0),
        )
