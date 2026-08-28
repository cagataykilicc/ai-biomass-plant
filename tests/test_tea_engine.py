"""Unit tests for Techno-Economic Analysis (TEA) and 20-year DCF engine."""

import pytest
from src.simulation.plant_simulator import BiomassPlantSimulator
from src.economics.tea_engine import TechnoEconomicEngine, CapitalExpenditureSummary, OperationalExpenditureSummary


def test_capex_and_guthrie_estimation() -> None:
    """Verify equipment sizing and Guthrie Total Capital Investment calculation."""
    sim = BiomassPlantSimulator()
    report = sim.run_simulation(feedstock_name="olive_pomace", feed_rate_kg_h=100.0)

    tea = TechnoEconomicEngine()
    capex = tea.evaluate_capex(report)

    assert isinstance(capex, CapitalExpenditureSummary)
    assert capex.purchased_equipment_cost_usd > 100000.0
    assert capex.fixed_capital_investment_usd > capex.purchased_equipment_cost_usd
    assert capex.total_capital_investment_usd > capex.fixed_capital_investment_usd
    assert len(capex.equipment_list) == 8


def test_dcf_npv_and_financial_viability() -> None:
    """Verify 20-year DCF, NPV, and levelized cost of bio-oil metrics."""
    sim = BiomassPlantSimulator()
    report = sim.run_simulation(feedstock_name="olive_pomace", feed_rate_kg_h=100.0)

    tea = TechnoEconomicEngine(bio_oil_price_usd_kg=0.65, biochar_price_usd_kg=0.45)
    capex = tea.evaluate_capex(report)
    opex = tea.evaluate_opex(report, capex)
    fin = tea.evaluate_financials(report, capex, opex)

    assert fin.annual_gross_revenue_usd > 0.0
    assert fin.discounted_payback_years > 0.0
    assert fin.levelized_cost_bio_oil_usd_kg > 0.0
    assert fin.levelized_cost_bio_oil_usd_mj > 0.0
