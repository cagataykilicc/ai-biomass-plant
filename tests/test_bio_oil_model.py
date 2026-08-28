"""Unit tests for bio-oil chemical grouping, acidity, and physical property model."""

import pytest
from src.data.feedstock import BiomassFeedstock
from src.models.bio_oil_model import BioOilPropertyModel, BioOilChemicalGrouping


def test_bio_oil_chemical_groups(sample_olive_pomace: BiomassFeedstock) -> None:
    """Verify bio-oil chemical functional families sum to 100%."""
    model = BioOilPropertyModel()
    grouping: BioOilChemicalGrouping = model.evaluate_bio_oil(
        organics_flow_kg_h=35.0,
        water_flow_kg_h=11.33,
        temperature_c=500.0,
        feedstock=sample_olive_pomace,
        raw_bio_oil_hhv=14.1,
    )

    fams_sum = sum(grouping.chemical_families_pct.values())
    assert pytest.approx(fams_sum, rel=1e-3) == 100.0
    assert grouping.total_liquid_mass_flow_kg_h == 46.33
    assert pytest.approx(grouping.water_content_pct, rel=1e-2) == (11.33 / 46.33 * 100.0)


def test_bio_oil_acidity_and_physical_properties(sample_olive_pomace: BiomassFeedstock) -> None:
    """Verify pH is acidic (2.0 - 3.8) and density is realistic (~1150 - 1250 kg/m3)."""
    model = BioOilPropertyModel()
    grouping = model.evaluate_bio_oil(
        organics_flow_kg_h=35.0,
        water_flow_kg_h=11.33,
        temperature_c=500.0,
        feedstock=sample_olive_pomace,
        raw_bio_oil_hhv=14.1,
    )

    assert 2.0 <= grouping.predicted_ph <= 3.8
    assert grouping.total_acid_number_mg_koh_g > 30.0
    assert 1100.0 <= grouping.density_kg_m3 <= 1250.0
    assert grouping.kinematic_viscosity_cst_40c > 0.0
