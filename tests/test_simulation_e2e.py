"""End-to-end integration and simulation workflow tests."""

import pytest
from src.simulation.plant_simulator import BiomassPlantSimulator, SimulationReport
from src.utils.config import PlantScenarioConfig


def test_default_simulation_run(plant_simulator: BiomassPlantSimulator) -> None:
    """Run full simulation pipeline with default parameters."""
    report: SimulationReport = plant_simulator.run_simulation()

    assert report.mass_balance.status == "PASS"
    assert report.energy_balance.status == "PASS"
    assert report.mass_balance.closure_error_pct < 0.01

    # Check products
    assert report.separation.recovered_biochar_kg_h > 0.0
    assert report.separation.recovered_bio_oil_liquid_kg_h > 0.0
    assert report.separation.clean_syngas_kg_h > 0.0
    assert report.drying.water_evaporated_kg_h > 0.0

    # Serialization test
    report_dict = report.to_dict()
    assert "metadata" in report_dict
    assert report_dict["metadata"]["mass_balance_status"] == "PASS"


@pytest.mark.parametrize("feedstock_name", ["olive_pomace", "pine_sawdust", "wheat_straw", "rice_husk"])
def test_simulation_all_feedstocks(plant_simulator: BiomassPlantSimulator, feedstock_name: str) -> None:
    """Verify that all standard feedstocks run successfully and pass mass balance."""
    report = plant_simulator.run_simulation(feedstock_name=feedstock_name, feed_rate_kg_h=150.0)
    assert report.mass_balance.status == "PASS"
    assert pytest.approx(report.mass_balance.closure_pct, rel=1e-3) == 100.0


def test_simulation_parameter_overrides(plant_simulator: BiomassPlantSimulator) -> None:
    """Verify parameter overrides propagate through simulation."""
    report = plant_simulator.run_simulation(
        feedstock_name="pine_sawdust",
        feed_rate_kg_h=200.0,
        moisture_pct=10.0,
        reactor_temp_c=550.0,
        heating_rate_c_min=50.0,
        residence_time_min=5.0,
    )
    assert report.scenario_config.feed_rate_kg_h == 200.0
    assert report.feedstock.proximate.moisture == 10.0
    assert report.reactor.operating_temperature_c == 550.0
    assert report.mass_balance.total_input_kg_h == 200.0
    assert report.mass_balance.status == "PASS"
