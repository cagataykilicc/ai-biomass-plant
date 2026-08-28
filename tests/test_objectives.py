"""Unit tests for optimization objectives and economic accounting."""

import pytest
from src.data.feedstock import BiomassFeedstock
from src.simulation.plant_simulator import BiomassPlantSimulator, SimulationReport
from src.optimization.objectives import OptimizationObjective, ObjectiveEvaluator, EconomicParameters


def test_economic_margin_evaluation(sample_olive_pomace: BiomassFeedstock, plant_simulator: BiomassPlantSimulator) -> None:
    """Verify economic profit calculation and objective evaluations."""
    report = plant_simulator.run_simulation(feedstock_name="olive_pomace", feed_rate_kg_h=100.0)
    econ = EconomicParameters(bio_oil_price_usd_kg=0.55, biochar_price_usd_kg=0.85)

    econ_dict = econ.calculate_margin_usd_h(report)
    assert econ_dict["total_revenue_usd_h"] > 0.0
    assert econ_dict["total_opex_usd_h"] > 0.0
    assert "gross_margin_usd_h" in econ_dict

    # Test all objective evaluations
    for obj in [
        OptimizationObjective.MAX_BIO_OIL_YIELD,
        OptimizationObjective.MAX_BIOCHAR_CARBON,
        OptimizationObjective.MAX_THERMAL_EFFICIENCY,
        OptimizationObjective.MAX_ECONOMIC_MARGIN,
        OptimizationObjective.MAX_EXERGY_EFFICIENCY,
    ]:
        val = ObjectiveEvaluator.evaluate(obj, report, econ)
        assert isinstance(val, float)
        assert val > 0.0
