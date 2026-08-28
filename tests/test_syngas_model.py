"""Unit tests for thermodynamic syngas speciation and molecular properties."""

import pytest
from src.data.feedstock import BiomassFeedstock
from src.models.syngas_model import SyngasSpeciationModel, SyngasComposition


def test_syngas_speciation_unity_sum() -> None:
    """Verify that molar fractions and mass fractions sum to 1.0."""
    model = SyngasSpeciationModel()
    comp: SyngasComposition = model.predict_speciation(
        temperature_c=500.0,
        syngas_mass_flow_kg_h=25.0,
        carrier_gas_n2_kg_h=0.0,
    )

    molar_sum = sum(comp.molar_fractions.values())
    mass_sum = sum(comp.mass_fractions.values())
    assert pytest.approx(molar_sum, rel=1e-4) == 1.0
    assert pytest.approx(mass_sum, rel=1e-4) == 1.0
    assert pytest.approx(comp.total_mass_flow_kg_h, rel=1e-4) == 25.0


def test_temperature_speciation_trends() -> None:
    """Verify physical gas speciation trends across temperatures."""
    model = SyngasSpeciationModel()
    comp_low = model.predict_speciation(temperature_c=380.0, syngas_mass_flow_kg_h=20.0)
    comp_high = model.predict_speciation(temperature_c=750.0, syngas_mass_flow_kg_h=20.0)

    # Low temperature pyrolysis has higher CO2 fraction (decarboxylation)
    assert comp_low.molar_fractions["CO2"] > comp_high.molar_fractions["CO2"]
    # High temperature pyrolysis surges in H2 and CO (secondary cracking)
    assert comp_high.molar_fractions["H2"] > comp_low.molar_fractions["H2"]
    assert comp_high.molar_fractions["CO"] > comp_low.molar_fractions["CO"]


def test_syngas_heating_value_and_volume() -> None:
    """Verify standard volume flow rate and heating values."""
    model = SyngasSpeciationModel()
    comp = model.predict_speciation(temperature_c=500.0, syngas_mass_flow_kg_h=22.81)

    assert comp.standard_volume_flow_nm3_h > 0.0
    # Mean molecular weight should be around 26 - 34 kg/kmol (mix of CO, CO2, CH4, H2)
    assert 22.0 <= comp.mean_molecular_weight_kg_kmol <= 36.0
    # Volumetric LHV should be positive (~6 to 14 MJ/Nm3)
    assert 5.0 <= comp.lhv_vol_mj_nm3 <= 18.0
    assert comp.hhv_vol_mj_nm3 > comp.lhv_vol_mj_nm3


def test_syngas_carrier_gas_addition() -> None:
    """Verify N2 carrier gas dilution behaves correctly."""
    model = SyngasSpeciationModel()
    comp_no_n2 = model.predict_speciation(temperature_c=500.0, syngas_mass_flow_kg_h=20.0, carrier_gas_n2_kg_h=0.0)
    comp_with_n2 = model.predict_speciation(temperature_c=500.0, syngas_mass_flow_kg_h=20.0, carrier_gas_n2_kg_h=5.0)

    assert comp_with_n2.total_mass_flow_kg_h == 25.0
    assert comp_with_n2.molar_fractions["N2"] > 0.0
    assert comp_with_n2.lhv_vol_mj_nm3 < comp_no_n2.lhv_vol_mj_nm3
