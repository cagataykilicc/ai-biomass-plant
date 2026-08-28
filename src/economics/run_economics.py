"""CLI runner and terminal dashboard for Techno-Economic Analysis (TEA) and LCA Carbon Accounting.

Usage:
    python -m src.economics.run_economics --feedstock olive_pomace
    python -m src.economics.run_economics --feedstock pine_sawdust --corc-price 75.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from src.simulation.plant_simulator import BiomassPlantSimulator
from src.economics.tea_engine import TechnoEconomicEngine
from src.economics.lca_engine import LCACarbonEngine


def evaluate_plant_economics_and_lca(
    feedstock_name: str = "olive_pomace",
    feed_rate_kg_h: float = 100.0,
    reactor_temp_c: float = 500.0,
    bio_oil_price_usd_kg: float = 0.65,
    biochar_price_usd_kg: float = 0.45,
    feedstock_price_usd_tonne: float = 65.0,
    corc_price_usd_tonne: float = 65.0,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute flowsheet simulation, evaluate TEA financials, and compute LCA carbon intensity."""
    sim = BiomassPlantSimulator()
    report = sim.run_simulation(
        feedstock_name=feedstock_name,
        feed_rate_kg_h=feed_rate_kg_h,
        reactor_temp_c=reactor_temp_c,
    )

    tea = TechnoEconomicEngine(
        bio_oil_price_usd_kg=bio_oil_price_usd_kg,
        biochar_price_usd_kg=biochar_price_usd_kg,
        feedstock_price_usd_tonne=feedstock_price_usd_tonne,
    )
    lca = LCACarbonEngine(corc_price_usd_tonne=corc_price_usd_tonne)

    capex = tea.evaluate_capex(report)
    opex = tea.evaluate_opex(report, capex)
    lca_prof = lca.evaluate_lca(report)
    
    # Financial valuation including voluntary carbon credit revenue
    corc_revenue = lca_prof.sequestration.annual_carbon_credit_revenue_usd
    financials = tea.evaluate_financials(report, capex, opex, carbon_credit_revenue_usd_yr=corc_revenue)

    full_report = {
        "plant_overview": {
            "feedstock": report.feedstock.name,
            "feed_rate_kg_h": feed_rate_kg_h,
            "annual_biomass_feed_tonnes": (feed_rate_kg_h * 8000.0) / 1000.0,
            "reactor_temp_c": reactor_temp_c,
            "operating_hours_yr": 8000.0,
        },
        "capital_expenditure_capex": capex.to_dict(),
        "operational_expenditure_opex": opex.to_dict(),
        "financial_viability_dcf": financials.to_dict(),
        "life_cycle_assessment_lca": lca_prof.to_dict(),
    }

    out_file = (
        Path(output_path)
        if output_path
        else Path(__file__).resolve().parent.parent.parent / "reports" / "techno_economic_lca_report.json"
    )
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)

    return full_report


def print_economics_dashboard(report: Dict[str, Any]) -> None:
    """Render ANSI terminal summary dashboard."""
    w = 78
    border = "=" * w
    sub_border = "-" * w

    print(f"\n{border}")
    print(f"       AI-INTEGRATED BIOMASS CONVERSION PLANT - V1.2")
    print(f" (Techno-Economic Assessment & ISO 14040/14044 LCA Carbon Accounting)")
    print(f"{border}")

    ov = report["plant_overview"]
    cap = report["capital_expenditure_capex"]
    op = report["operational_expenditure_opex"]
    fin = report["financial_viability_dcf"]
    lca = report["life_cycle_assessment_lca"]

    print(f"Feedstock Profile       : {ov['feedstock']} ({ov['feed_rate_kg_h']} kg/h | {ov['annual_biomass_feed_tonnes']:,.0f} t/yr)")
    print(f"Reactor Operating Temp  : {ov['reactor_temp_c']:.0f} °C")

    print(f"\nCAPITAL & OPERATING EXPENDITURE (Guthrie Factorial)")
    print(f"{sub_border}")
    print(f"Total Purchased Equipment (PEC) : ${cap['purchased_equipment_cost_usd']:,.2f}")
    print(f"Fixed Capital Investment (FCI)  : ${cap['fixed_capital_investment_usd']:,.2f}")
    print(f"Total Capital Investment (TCI)  : ${cap['total_capital_investment_usd']:,.2f}")
    print(f"Annual OPEX (8,000 h/yr)        : ${op['total_opex_usd_yr']:,.2f} (${op['unit_opex_usd_per_tonne_feed']:.2f}/t feed)")

    print(f"\n20-YEAR DISCOUNTED CASH FLOW & FINANCIAL VIABILITY (10% Discount Rate)")
    print(f"{sub_border}")
    print(f"Annual Gross Revenue            : ${fin['annual_gross_revenue_usd']:,.2f}")
    print(f"Net Present Value (NPV)         : ${fin['net_present_value_usd']:,.2f}")
    print(f"Internal Rate of Return (IRR)   : {fin['internal_rate_of_return_pct']:.2f}%")
    print(f"Discounted Payback Period       : {fin['discounted_payback_years']:.2f} Years")
    print(f"Levelized Cost of Bio-Oil (LCOB): ${fin['levelized_cost_bio_oil_usd_kg']:.4f}/kg (${fin['levelized_cost_bio_oil_usd_mj']:.4f}/MJ)")
    print(f"Commercial Project Status       : {'[VIABLE - MEETS 10% HURDLE RATE]' if fin['is_financially_viable'] else '[DEFICIT]'}")

    print(f"\nISO 14040/14044 LCA & CARBON SEQUESTRATION PROFILE")
    print(f"{sub_border}")
    sc = lca["scope_emissions"]
    seq = lca["sequestration"]
    print(f"Scope 1 Direct Emissions        : {sc['scope_1_direct_co2e_kg_yr']:,.1f} kg CO2eq/yr")
    print(f"Scope 2 Grid Power Emissions    : {sc['scope_2_electricity_co2e_kg_yr']:,.1f} kg CO2eq/yr")
    print(f"Scope 3 Supply Chain Emissions  : {sc['scope_3_supply_chain_co2e_kg_yr']:,.1f} kg CO2eq/yr")
    print(f"Total Gross Emissions           : {sc['total_gross_emissions_co2e_kg_yr']:,.1f} kg CO2eq/yr")
    print(f"Biochar Carbon Sequestration    : -{seq['co2_sequestered_kg_yr']:,.1f} kg CO2eq/yr ({seq['co2_sequestered_tonnes_yr']:,.1f} t CO2/yr)")
    print(f"Certified CORC Credit Revenue   : +${seq['annual_carbon_credit_revenue_usd']:,.2f}/yr (@ ${seq['corc_credit_price_usd_tonne']:.0f}/t CO2)")
    print(f"Net Life Cycle GHG Balance      : {lca['net_ghg_balance_co2e_kg_yr']:,.1f} kg CO2eq/yr")
    print(f"Net Carbon Intensity (Bio-Oil)  : {lca['carbon_intensity_g_co2e_per_mj_bio_oil']:.2f} g CO2eq/MJ")
    print(f"Net Carbon Removal Efficiency   : {lca['net_removal_kg_co2e_per_tonne_feed']:.1f} kg CO2eq removed / tonne biomass")
    print(f"Climate Impact Status           : {'[NET CARBON NEGATIVE (CARBON REMOVAL SYSTEM)]' if lca['is_carbon_negative'] else '[NET EMITTING]'}")
    print(f"{border}\n")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Techno-Economic Analysis & LCA Carbon Accounting (V1.2)")
    parser.add_argument("--feedstock", type=str, default="olive_pomace", help="Feedstock profile name")
    parser.add_argument("--feed-rate", type=float, default=100.0, help="Wet feed rate (kg/h)")
    parser.add_argument("--temp", type=float, default=500.0, help="Pyrolysis reactor temperature (°C)")
    parser.add_argument("--oil-price", type=float, default=0.65, help="Bio-oil market price ($/kg)")
    parser.add_argument("--char-price", type=float, default=0.45, help="Biochar market price ($/kg)")
    parser.add_argument("--feed-cost", type=float, default=65.0, help="Feedstock cost ($/tonne)")
    parser.add_argument("--corc-price", type=float, default=65.0, help="Carbon removal credit price ($/tonne CO2)")
    parser.add_argument("--output", type=str, default=None, help="Output report JSON file path")
    args = parser.parse_args()

    rep = evaluate_plant_economics_and_lca(
        feedstock_name=args.feedstock,
        feed_rate_kg_h=args.feed_rate,
        reactor_temp_c=args.temp,
        bio_oil_price_usd_kg=args.oil_price,
        biochar_price_usd_kg=args.char_price,
        feedstock_price_usd_tonne=args.feed_cost,
        corc_price_usd_tonne=args.corc_price,
        output_path=args.output,
    )
    print_economics_dashboard(rep)
    print(f"[OK] Full Techno-Economic & LCA report exported to reports/techno_economic_lca_report.json")


if __name__ == "__main__":
    main()
