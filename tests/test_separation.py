"""Unit tests for product separation and condensation model."""

import pytest
from src.data.feedstock import BiomassFeedstock
from src.process.reactor import PyrolysisReactor
from src.process.separation import ProductSeparator, SeparationConfig, SeparationResult


def test_separation_mass_conservation(sample_olive_pomace: BiomassFeedstock) -> None:
    """Verify total mass across cyclone and condenser is conserved."""
    reactor = PyrolysisReactor()
    reactor_out = reactor.process(dried_feed_rate_kg_h=92.391, residual_moisture_pct=8.0, feedstock=sample_olive_pomace)

    separator = ProductSeparator(config=SeparationConfig(cyclone_efficiency=0.98, condenser_efficiency=0.95))
    res: SeparationResult = separator.process(reactor_output=reactor_out)

    # Inflow to separation = reactor_out.total_product_rate_kg_h
    # Outflow from separation = recovered_biochar + fines_loss + recovered_bio_oil + clean_syngas
    total_out = (
        res.recovered_biochar_kg_h
        + res.cyclone_fines_loss_kg_h
        + res.recovered_bio_oil_liquid_kg_h
        + res.clean_syngas_kg_h
    )

    assert pytest.approx(total_out, rel=1e-4) == reactor_out.total_product_rate_kg_h
    assert pytest.approx(res.recovered_biochar_kg_h / reactor_out.char_mass_rate_kg_h, rel=1e-4) == 0.98


def test_condenser_cooling_duty(sample_olive_pomace: BiomassFeedstock) -> None:
    """Verify condenser cooling duty is positive and cooling water flow is calculated."""
    reactor = PyrolysisReactor()
    reactor_out = reactor.process(dried_feed_rate_kg_h=100.0, residual_moisture_pct=8.0, feedstock=sample_olive_pomace)

    separator = ProductSeparator()
    res = separator.process(reactor_output=reactor_out)

    assert res.condenser_cooling_duty_kw > 0.0
    assert res.cooling_water_rate_kg_h > 0.0
    assert res.liquid_bio_oil_hhv_mj_kg > 0.0
