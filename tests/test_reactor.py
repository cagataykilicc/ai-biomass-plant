"""Unit tests for the pyrolysis reactor unit operation."""

import pytest
from src.data.feedstock import BiomassFeedstock
from src.process.reactor import PyrolysisReactor, ReactorConfig, ReactorOutput


def test_reactor_mass_conservation(sample_olive_pomace: BiomassFeedstock) -> None:
    """Verify total mass out equals total mass in to reactor."""
    reactor = PyrolysisReactor(config=ReactorConfig(temperature_c=500.0))
    dried_feed_rate = 92.391  # kg/h
    residual_moisture = 8.0   # wt%

    output: ReactorOutput = reactor.process(
        dried_feed_rate_kg_h=dried_feed_rate,
        residual_moisture_pct=residual_moisture,
        feedstock=sample_olive_pomace,
    )

    # Inflow = Outflow
    assert pytest.approx(output.total_product_rate_kg_h, rel=1e-4) == dried_feed_rate
    # Total product is char + bio-oil vapors + syngas
    calc_sum = output.char_mass_rate_kg_h + output.total_bio_oil_vapors_kg_h + output.syngas_mass_rate_kg_h
    assert pytest.approx(calc_sum, rel=1e-4) == dried_feed_rate


def test_reactor_thermal_duty(sample_olive_pomace: BiomassFeedstock) -> None:
    """Verify reactor thermal duty is positive and includes sensible + reaction + loss."""
    reactor = PyrolysisReactor(config=ReactorConfig(temperature_c=500.0, reaction_enthalpy_kj_kg=300.0))
    output = reactor.process(
        dried_feed_rate_kg_h=100.0,
        residual_moisture_pct=8.0,
        feedstock=sample_olive_pomace,
    )

    assert output.reactor_thermal_duty_kw > 0.0
    assert output.sensible_heating_duty_kw > 0.0
    assert output.reaction_duty_kw > 0.0
    assert output.heat_loss_kw > 0.0
    assert pytest.approx(
        output.reactor_thermal_duty_kw, rel=1e-4
    ) == (output.sensible_heating_duty_kw + output.reaction_duty_kw + output.heat_loss_kw)


def test_reactor_temperature_override(sample_olive_pomace: BiomassFeedstock) -> None:
    """Test runtime temperature override on reactor."""
    reactor = PyrolysisReactor()
    out_500 = reactor.process(dried_feed_rate_kg_h=100.0, residual_moisture_pct=8.0, feedstock=sample_olive_pomace, temp_override=500.0)
    out_650 = reactor.process(dried_feed_rate_kg_h=100.0, residual_moisture_pct=8.0, feedstock=sample_olive_pomace, temp_override=650.0)

    assert out_500.operating_temperature_c == 500.0
    assert out_650.operating_temperature_c == 650.0
    assert out_650.reactor_thermal_duty_kw > out_500.reactor_thermal_duty_kw
