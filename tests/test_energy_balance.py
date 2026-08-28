"""Unit tests for plant-wide energy balance, heat integration, and exergy KPIs."""

import pytest
from src.data.feedstock import BiomassFeedstock
from src.process.drying import BiomassDryer
from src.process.reactor import PyrolysisReactor
from src.process.separation import ProductSeparator
from src.models.syngas_model import SyngasSpeciationModel
from src.process.combustor import SyngasCombustor
from src.process.energy_balance import EnergyBalanceEngine, EnergyBalanceSummary


def test_plant_energy_balance_without_combustor(sample_olive_pomace: BiomassFeedstock) -> None:
    """Verify energy balance calculations without heat integration."""
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
    assert eb.gross_thermal_demand_kw > 0.0
    assert eb.total_net_external_power_kw > 0.0
    assert eb.feedstock_chemical_power_kw > 0.0
    assert eb.total_products_chemical_power_kw > 0.0
    assert 70.0 <= eb.energy_recovery_ratio_pct <= 100.0
    assert eb.exergy is not None
    assert eb.exergy.second_law_exergy_efficiency_pct > 0.0


def test_plant_energy_balance_with_heat_integration(sample_olive_pomace: BiomassFeedstock) -> None:
    """Verify energy balance calculations with syngas combustor heat integration."""
    feed_rate = 100.0  # kg/h
    dryer = BiomassDryer()
    reactor = PyrolysisReactor()
    separator = ProductSeparator()
    syngas_model = SyngasSpeciationModel()
    combustor = SyngasCombustor()
    eb_engine = EnergyBalanceEngine()

    drying_res = dryer.process(feed_rate_kg_h=feed_rate, feedstock=sample_olive_pomace)
    reactor_out = reactor.process(
        dried_feed_rate_kg_h=drying_res.dried_feed_rate_out_kg_h,
        residual_moisture_pct=drying_res.final_moisture_pct,
        feedstock=sample_olive_pomace,
    )
    sep_res = separator.process(reactor_output=reactor_out)
    syngas_comp = syngas_model.predict_speciation(
        temperature_c=reactor_out.operating_temperature_c,
        syngas_mass_flow_kg_h=sep_res.clean_syngas_kg_h,
    )

    gross_thermal = drying_res.thermal_duty_actual_kw + reactor_out.reactor_thermal_duty_kw
    comb_res = combustor.process(syngas=syngas_comp, total_plant_thermal_demand_kw=gross_thermal)

    eb: EnergyBalanceSummary = eb_engine.compute_plant_energy_balance(
        raw_feed_rate_kg_h=feed_rate,
        feedstock=sample_olive_pomace,
        drying_result=drying_res,
        reactor_output=reactor_out,
        separation_result=sep_res,
        combustion_result=comb_res,
    )

    assert eb.heat_recovered_from_syngas_kw > 0.0
    assert eb.thermal_self_sufficiency_index_pct > 0.0
    assert eb.total_net_external_power_kw < (eb.gross_thermal_demand_kw + eb.auxiliary_electrical_power_kw)
