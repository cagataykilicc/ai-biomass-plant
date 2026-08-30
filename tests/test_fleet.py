"""Automated unit and integration tests for Multi-Plant Fleet Management, CORC Arbitrage, and Renewable Coupling."""

import pytest
from src.fleet.fleet_manager import RegionalFleetManager, PlantNodeState
from src.fleet.corc_trader import CORCArbitrageEngine, CarbonMarketQuote
from src.fleet.renewable_coupling import RenewableGridDispatcher, HourlyDispatchProfile
from src.api.handlers import APIRequestHandler


def test_regional_fleet_manager_kpis_and_dispatch() -> None:
    """Verify fleet aggregation metrics and remote setpoint dispatching."""
    fm = RegionalFleetManager()
    summary = fm.get_fleet_summary()

    assert summary["fleet_size"] == 3
    assert summary["fleet_status"] == "ALL_NODES_OPERATIONAL"
    kpis = summary["fleet_kpis"]
    assert kpis["total_current_throughput_kg_h"] == 150.0 + 220.0 + 120.0  # 490.0 kg/h
    assert kpis["daily_aggregated_feed_tonnes"] > 10.0
    assert kpis["daily_permanent_co2e_sinks_tonnes"] > 12.0
    assert 90.0 <= kpis["fleet_average_oee_pct"] <= 100.0

    # Test single plant setpoint dispatch
    res = fm.dispatch_plant_setpoint("PLANT_01", {"feed_rate_kg_h": 180.0, "reactor_temp_c": 510.0})
    assert res["status"] == "DISPATCH_CONFIRMED"
    assert fm.plants["PLANT_01"].feed_rate_kg_h == 180.0
    assert fm.plants["PLANT_01"].reactor_temp_c == 510.0

    # Test invalid plant
    with pytest.raises(KeyError):
        fm.dispatch_plant_setpoint("PLANT_99", {"feed_rate_kg_h": 100.0})


def test_seasonal_harvest_optimization() -> None:
    """Verify seasonal load allocation across Mediterranean, Nordic, and Anatolian agricultural hubs."""
    fm = RegionalFleetManager()

    # 1. Summer harvest peak in Anatolia (Wheat straw)
    res_summer = fm.optimize_seasonal_harvest_schedule("SUMMER")
    assert res_summer["season"] == "SUMMER"
    assert fm.plants["PLANT_03"].feed_rate_kg_h == 175.0

    # 2. Autumn/Winter harvest peak in Mediterranean (Olive pomace)
    res_autumn = fm.optimize_seasonal_harvest_schedule("AUTUMN")
    assert res_autumn["season"] == "AUTUMN"
    assert fm.plants["PLANT_01"].feed_rate_kg_h == 190.0


def test_corc_arbitrage_engine_dynamics() -> None:
    """Verify market pricing response and optimal pyrolysis temperature shifting."""
    # 1. High CORC Carbon Removal Price ($140 / t CO2) -> Should favor Biochar Carbon Removal (420°C)
    high_corc_quote = CarbonMarketQuote(spot_corc_usd_tonne=140.0, bio_oil_usd_kg=0.55, biochar_usd_kg=0.45)
    trader_high = CORCArbitrageEngine(high_corc_quote)
    res_high = trader_high.evaluate_arbitrage_modes(feed_rate_kg_h=100.0)

    assert res_high["recommended_mode"] == "MAX_CORC_CARBON_REMOVAL"
    assert res_high["optimal_setpoint_temp_c"] == 420.0

    # 2. Low CORC Price ($35 / t CO2) + High Bio-Oil Price ($1.10 / kg) -> Should favor Bio-Oil Yield (530°C)
    low_corc_quote = CarbonMarketQuote(spot_corc_usd_tonne=35.0, bio_oil_usd_kg=1.10, biochar_usd_kg=0.30)
    trader_low = CORCArbitrageEngine(low_corc_quote)
    res_low = trader_low.evaluate_arbitrage_modes(feed_rate_kg_h=100.0)

    assert res_low["recommended_mode"] == "MAX_BIO_OIL_YIELD"
    assert res_low["optimal_setpoint_temp_c"] == 530.0


def test_renewable_grid_coupling_and_load_shifting() -> None:
    """Verify 24-hour solar PV generation curve and TOU tariff cost reductions."""
    dispatcher = RenewableGridDispatcher(solar_capacity_kw=150.0, base_load_kw=40.0)

    # 1. Compute unmanaged baseline vs smart solar shifted dispatch
    smart_res = dispatcher.compute_24h_dispatch(shift_loads_to_solar=True)
    flat_res = dispatcher.compute_24h_dispatch(shift_loads_to_solar=False)

    m = smart_res["daily_metrics"]
    assert m["total_solar_generated_kwh"] > 400.0
    assert m["daily_cost_savings_usd"] >= 0.0
    assert m["projected_annual_power_savings_usd"] > 0.0
    assert len(smart_res["hourly_schedule"]) == 24


def test_api_fleet_handlers() -> None:
    """Verify REST API handlers for fleet status, dispatching, CORC arbitrage, and renewables."""
    # 1. Fleet Status
    status = APIRequestHandler.handle_fleet_status()
    assert "fleet_kpis" in status
    assert "plants" in status

    # 2. Fleet Dispatch
    disp_res = APIRequestHandler.handle_fleet_dispatch({
        "plant_id": "PLANT_02",
        "setpoints": {"reactor_temp_c": 525.0},
    })
    assert disp_res["status"] == "DISPATCH_CONFIRMED"

    # 3. CORC Arbitrage
    arb_res = APIRequestHandler.handle_corc_arbitrage({
        "corc_price": 120.0,
        "oil_price": 0.60,
    })
    assert "recommended_mode" in arb_res
    assert "arbitrage_analysis" in arb_res

    # 4. Renewable Dispatch
    rnd_res = APIRequestHandler.handle_renewable_dispatch({"shift_loads": True})
    assert "daily_metrics" in rnd_res
    assert "hourly_schedule" in rnd_res
