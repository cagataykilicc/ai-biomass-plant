"""Unit tests for syngas combustor, excess air, and plant heat integration."""

import pytest
from src.models.syngas_model import SyngasSpeciationModel
from src.process.combustor import SyngasCombustor, CombustorConfig, CombustionResult


def test_combustor_heat_release_and_stoichiometry() -> None:
    """Verify combustion air sizing, thermal heat release, and flue gas temperature."""
    syngas_model = SyngasSpeciationModel()
    syngas = syngas_model.predict_speciation(temperature_c=500.0, syngas_mass_flow_kg_h=22.81)

    combustor = SyngasCombustor(config=CombustorConfig(excess_air_ratio=1.20, combustion_efficiency=0.985))
    total_thermal_demand = 47.12  # kW

    res: CombustionResult = combustor.process(
        syngas=syngas,
        total_plant_thermal_demand_kw=total_thermal_demand,
    )

    assert res.thermal_heat_released_kw > 0.0
    assert res.thermal_heat_recovered_kw > 0.0
    assert res.actual_combustion_air_rate_kg_h > res.stoichiometric_air_rate_kg_h
    assert pytest.approx(res.actual_combustion_air_rate_kg_h / res.stoichiometric_air_rate_kg_h, rel=1e-3) == 1.20

    # Flue gas temperature should be in a realistic flame/combustion window (600 - 1300 °C)
    assert 600.0 <= res.flue_gas_actual_temp_c <= 1400.0
    assert res.flue_gas_mass_flow_kg_h == (syngas.total_mass_flow_kg_h + res.actual_combustion_air_rate_kg_h)
    assert res.thermal_self_sufficiency_index_pct > 0.0


def test_thermal_self_sufficiency_logic() -> None:
    """Verify TSI threshold logic for surplus vs deficit."""
    syngas_model = SyngasSpeciationModel()
    syngas = syngas_model.predict_speciation(temperature_c=500.0, syngas_mass_flow_kg_h=22.81)
    combustor = SyngasCombustor()

    # Small demand: should be autonomous (surplus > 0, net external = 0)
    res_low_demand = combustor.process(syngas=syngas, total_plant_thermal_demand_kw=10.0)
    assert res_low_demand.is_thermally_self_sufficient is True
    assert res_low_demand.net_external_heat_required_kw == 0.0
    assert res_low_demand.surplus_heat_available_kw > 0.0

    # Huge demand: should require external fuel
    res_high_demand = combustor.process(syngas=syngas, total_plant_thermal_demand_kw=500.0)
    assert res_high_demand.is_thermally_self_sufficient is False
    assert res_high_demand.net_external_heat_required_kw > 0.0
    assert res_high_demand.surplus_heat_available_kw == 0.0
