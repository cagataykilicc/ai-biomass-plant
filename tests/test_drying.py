"""Unit tests for the biomass drying and pretreatment model."""

import pytest
from src.data.feedstock import BiomassFeedstock
from src.process.drying import BiomassDryer, DryingConfig, DryingResult


def test_standard_drying_mass_balance(sample_olive_pomace: BiomassFeedstock) -> None:
    """Verify water removal and dry solid conservation."""
    dryer = BiomassDryer(config=DryingConfig(target_moisture_pct=8.0))
    feed_rate = 100.0  # kg/h
    # Initial moisture = 15.0% -> dry matter = 85.0 kg/h
    # Target moisture = 8.0% -> exit mass = 85 / (1 - 0.08) = 92.391 kg/h
    # Evaporated water = 100 - 92.391 = 7.609 kg/h
    res: DryingResult = dryer.process(feed_rate_kg_h=feed_rate, feedstock=sample_olive_pomace)

    assert pytest.approx(res.feed_rate_in_kg_h, rel=1e-4) == 100.0
    assert pytest.approx(res.dry_matter_kg_h, rel=1e-4) == 85.0
    assert pytest.approx(res.dried_feed_rate_out_kg_h + res.water_evaporated_kg_h, rel=1e-4) == 100.0
    assert pytest.approx(res.dried_feed_rate_out_kg_h, rel=1e-3) == 92.391
    assert pytest.approx(res.water_evaporated_kg_h, rel=1e-3) == 7.609
    assert res.final_moisture_pct == 8.0


def test_dryer_already_dry_feedstock(sample_olive_pomace: BiomassFeedstock) -> None:
    """When feedstock is already drier than target moisture, no water is evaporated."""
    sample_olive_pomace.proximate.moisture = 5.0
    dryer = BiomassDryer(config=DryingConfig(target_moisture_pct=8.0))

    res = dryer.process(feed_rate_kg_h=100.0, feedstock=sample_olive_pomace)
    assert res.water_evaporated_kg_h == 0.0
    assert res.dried_feed_rate_out_kg_h == 100.0
    assert res.thermal_duty_actual_kw == 0.0


def test_drying_energy_demands(sample_olive_pomace: BiomassFeedstock) -> None:
    """Verify drying thermal duty is positive and follows latent + sensible requirements."""
    dryer = BiomassDryer(config=DryingConfig(target_moisture_pct=8.0, thermal_efficiency=0.75))
    res = dryer.process(feed_rate_kg_h=100.0, feedstock=sample_olive_pomace)

    # With ~7.6 kg/h water removed and ~2257 kJ/kg latent heat, thermal duty should be ~6 to 10 kW
    assert res.thermal_duty_actual_kw > 0.0
    assert 5.0 <= res.thermal_duty_actual_kw <= 12.0
    assert res.specific_energy_kj_per_kg_water > 2257.0  # Must exceed pure latent heat due to sensible loads & efficiency


def test_drying_invalid_inputs(sample_olive_pomace: BiomassFeedstock) -> None:
    """Test validation and error handling in drying unit."""
    dryer = BiomassDryer()
    with pytest.raises(ValueError, match="Feed rate must be positive"):
        dryer.process(feed_rate_kg_h=-10.0, feedstock=sample_olive_pomace)

    with pytest.raises(ValueError, match="Target moisture must be in"):
        DryingConfig(target_moisture_pct=105.0)

    with pytest.raises(ValueError, match="Thermal efficiency must be in"):
        DryingConfig(thermal_efficiency=-0.5)
