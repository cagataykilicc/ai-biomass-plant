"""Unit tests for plant-wide energy balance and thermodynamic KPIs."""

import pytest
from src.data.feedstock import BiomassFeedstock
from src.process.drying import BiomassDryer
from src.process.reactor import PyrolysisReactor
from src.process.separation import ProductSeparator
from src.process.energy_balance import EnergyBalanceEngine, EnergyBalanceSummary


def test_plant_energy_balance(sample_olive_pomace: BiomassFeedstock) -> None:
    """Verify energy balance calculations and sanity of thermodynamic KPIs."""
    feed_rate = 100.0  # kg/h
    dryer = BiomassDryer()
    reactor = PyrolysisReactor()
    separator = ProductSeparator()
    eb_engine = EnergyBalanceEngine()

    drying_res = dryer.process(feed_rate_kg_h=feed_rate, feedstock=sample_olive_pomace)
    reactor_out = reactor.process(
        dried_feed_rate_kg_h=drying_res.dried_feed_rate_out_kg_h,
        residual_moisture_pct=drying_res.final_moisture_pct,
        feedstock=sample_olive_pomace,
    )
    sep_res = separator.process(reactor_output=reactor_out)

    eb: EnergyBalanceSummary = eb_engine.compute_plant_energy_balance(
        raw_feed_rate_kg_h=feed_rate,
        feedstock=sample_olive_pomace,
        drying_result=drying_res,
        reactor_output=reactor_out,
        separation_result=sep_res,
    )

    assert eb.status == "PASS"
    assert eb.drying_thermal_duty_kw > 0.0
    assert eb.reactor_thermal_duty_kw > 0.0
    assert eb.total_external_energy_input_kw > 0.0
    assert eb.feedstock_chemical_power_kw > 0.0
    assert eb.total_products_chemical_power_kw > 0.0
    # Energy recovery ratio should typically be 75 - 95%
    assert 70.0 <= eb.energy_recovery_ratio_pct <= 100.0
    # Product energy shares sum to ~energy_recovery_ratio_pct
    share_sum = eb.bio_oil_energy_share_pct + eb.biochar_energy_share_pct + eb.syngas_energy_share_pct
    assert pytest.approx(share_sum, rel=1e-2) == eb.energy_recovery_ratio_pct
