"""Unit tests for plant-wide mass balance accounting and closure verification."""

import pytest
from src.data.feedstock import BiomassFeedstock
from src.process.drying import BiomassDryer
from src.process.reactor import PyrolysisReactor
from src.process.separation import ProductSeparator
from src.process.mass_balance import MassBalanceEngine, MassBalanceSummary


def test_plant_mass_balance_closure(sample_olive_pomace: BiomassFeedstock) -> None:
    """Verify end-to-end plant mass balance achieves 100.00% closure."""
    feed_rate = 100.0  # kg/h
    dryer = BiomassDryer()
    reactor = PyrolysisReactor()
    separator = ProductSeparator()
    mb_engine = MassBalanceEngine()

    drying_res = dryer.process(feed_rate_kg_h=feed_rate, feedstock=sample_olive_pomace)
    reactor_out = reactor.process(
        dried_feed_rate_kg_h=drying_res.dried_feed_rate_out_kg_h,
        residual_moisture_pct=drying_res.final_moisture_pct,
        feedstock=sample_olive_pomace,
    )
    sep_res = separator.process(reactor_output=reactor_out)

    summary: MassBalanceSummary = mb_engine.compute_plant_mass_balance(
        raw_feed_rate_kg_h=feed_rate,
        feedstock=sample_olive_pomace,
        drying_result=drying_res,
        reactor_output=reactor_out,
        separation_result=sep_res,
    )

    assert summary.status == "PASS"
    assert summary.is_balanced is True
    assert pytest.approx(summary.closure_pct, rel=1e-4) == 100.0
    assert summary.closure_error_pct < 0.01
    assert pytest.approx(summary.total_input_kg_h, rel=1e-4) == 100.0
    assert pytest.approx(summary.total_output_kg_h, rel=1e-4) == 100.0
    assert "S101_RAW_BIOMASS" in summary.streams
    assert "S106_BIOCHAR_PRODUCT" in summary.streams
    assert "S107_BIO_OIL_PRODUCT" in summary.streams
    assert "S108_CLEAN_SYNGAS" in summary.streams
