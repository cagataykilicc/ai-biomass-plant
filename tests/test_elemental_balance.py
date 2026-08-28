"""Unit tests for atom-by-atom elemental mass conservation."""

import pytest
from src.data.feedstock import BiomassFeedstock
from src.simulation.plant_simulator import BiomassPlantSimulator, SimulationReport


def test_elemental_balance_closures(sample_olive_pomace: BiomassFeedstock, plant_simulator: BiomassPlantSimulator) -> None:
    """Verify that C, H, O, N, S, Ash achieve 100.00% closure across the plant."""
    report: SimulationReport = plant_simulator.run_simulation(feedstock_name="olive_pomace", feed_rate_kg_h=100.0)

    elem_summary = report.elemental_balance
    assert elem_summary.overall_status == "PASS"

    for elem_name in ["C", "H", "O", "N", "S", "Ash"]:
        closure_obj = elem_summary.closures[elem_name]
        assert closure_obj.status == "PASS"
        assert pytest.approx(closure_obj.closure_pct, rel=1e-2) == 100.0
        assert closure_obj.closure_error_pct <= 0.5


def test_carbon_partitioning_sum(plant_simulator: BiomassPlantSimulator) -> None:
    """Verify that carbon partitioning across biochar, bio-oil, and syngas sums to 100%."""
    report = plant_simulator.run_simulation(feedstock_name="pine_sawdust", feed_rate_kg_h=150.0)

    c_part = report.elemental_balance.carbon_partitioning_pct
    total_c_part = (
        c_part["biochar_carbon_pct"]
        + c_part["bio_oil_carbon_pct"]
        + c_part["syngas_carbon_pct"]
    )
    assert pytest.approx(total_c_part, rel=1e-2) == 100.0
