"""Unit tests for ISO 14040/14044 LCA and Carbon Sequestration engine."""

import pytest
from src.simulation.plant_simulator import BiomassPlantSimulator
from src.economics.lca_engine import LCACarbonEngine, PlantLCAProfile


def test_lca_carbon_accounting_and_net_negative_balance() -> None:
    """Verify cradle-to-gate Scope 1-2-3 emissions and carbon negative biochar sequestration."""
    sim = BiomassPlantSimulator()
    report = sim.run_simulation(feedstock_name="pine_sawdust", feed_rate_kg_h=100.0)

    lca = LCACarbonEngine(corc_price_usd_tonne=65.0)
    profile = lca.evaluate_lca(report)

    assert isinstance(profile, PlantLCAProfile)
    assert profile.scope_emissions.scope_1_direct_co2e_kg_yr > 0.0
    assert profile.scope_emissions.scope_2_electricity_co2e_kg_yr > 0.0
    assert profile.scope_emissions.scope_3_supply_chain_co2e_kg_yr > 0.0
    assert profile.sequestration.co2_sequestered_tonnes_yr > 0.0
    assert profile.sequestration.annual_carbon_credit_revenue_usd > 0.0
    # Biomass conversion with biochar permanence is net carbon negative
    assert profile.is_carbon_negative is True
    assert profile.net_ghg_balance_co2e_kg_yr < 0.0
    assert profile.carbon_intensity_g_co2e_per_mj_bio_oil < 0.0
