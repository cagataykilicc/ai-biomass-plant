"""Command-line interface (CLI) entry point for the Virtual Biomass Pyrolysis Plant.

Usage:
    python -m src.run_simulation
    python -m src.run_simulation --config configs/scenarios/olive_pomace_standard.yaml
    python -m src.run_simulation --feedstock pine_sawdust --feed-rate 200 --temp 520 --moisture 12
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from src.simulation.plant_simulator import BiomassPlantSimulator, SimulationReport
from src.utils.config import ConfigManager, PlantScenarioConfig


def print_simulation_dashboard(report: SimulationReport) -> None:
    """Format and print an ANSI-enhanced process dashboard to stdout."""
    cfg = report.scenario_config
    feedstock = report.feedstock
    drying = report.drying
    reactor = report.reactor
    sep = report.separation
    mb = report.mass_balance
    eb = report.energy_balance

    w = 60
    border = "=" * w
    sub_border = "-" * w

    print(f"\n{border}")
    print(f"       AI-INTEGRATED BIOMASS CONVERSION PLANT - V0.1")
    print(f"{border}")
    print(f"Feedstock            : {feedstock.name} ({feedstock.category})")
    print(f"Feed Rate (Wet)      : {cfg.feed_rate_kg_h:.1f} kg/h")
    print(f"Initial Moisture     : {feedstock.proximate.moisture:.1f} wt%")
    print(f"Target Exit Moisture : {drying.final_moisture_pct:.1f} wt%")
    print(f"Reactor Temperature  : {reactor.operating_temperature_c:.1f} °C")
    print(f"Heating Rate         : {cfg.reactor.heating_rate_c_min:.1f} °C/min")
    print(f"Residence Time       : {cfg.reactor.residence_time_min:.1f} min")

    print(f"\nPRODUCTS & RECOVERY")
    print(f"{sub_border}")
    print(f"Recovered Bio-oil    : {sep.recovered_bio_oil_liquid_kg_h:6.2f} kg/h  (HHV: {sep.liquid_bio_oil_hhv_mj_kg:.1f} MJ/kg, Water: {sep.bio_oil_water_content_pct:.1f}%)")
    print(f"Recovered Biochar    : {sep.recovered_biochar_kg_h:6.2f} kg/h  (HHV: {reactor.char_hhv_mj_kg:.1f} MJ/kg)")
    print(f"Clean Syngas         : {sep.clean_syngas_kg_h:6.2f} kg/h  (LHV: {reactor.syngas_lhv_mj_kg:.1f} MJ/kg)")
    print(f"Dryer Exhaust Water  : {drying.water_evaporated_kg_h:6.2f} kg/h")
    print(f"Cyclone Fines Loss   : {sep.cyclone_fines_loss_kg_h:6.2f} kg/h")

    print(f"\nYIELDS (Dry Basis)")
    print(f"{sub_border}")
    print(f"Bio-oil Yield        : {reactor.yields_dry.bio_oil_yield * 100:5.1f} wt%")
    print(f"Biochar Yield        : {reactor.yields_dry.bio_char_yield * 100 if hasattr(reactor.yields_dry, 'bio_char_yield') else reactor.yields_dry.biochar_yield * 100:5.1f} wt%")
    print(f"Syngas Yield         : {reactor.yields_dry.syngas_yield * 100:5.1f} wt%")

    print(f"\nMASS BALANCE")
    print(f"{sub_border}")
    print(f"Total Input          : {mb.total_input_kg_h:6.2f} kg/h")
    print(f"Total Output         : {mb.total_output_kg_h:6.2f} kg/h")
    print(f"Closure              : {mb.closure_pct:6.2f} %  (Deviation: {mb.closure_error_pct:.4f}%)")

    print(f"\nENERGY & THERMAL DUTIES")
    print(f"{sub_border}")
    print(f"Drying Thermal Duty  : {eb.drying_thermal_duty_kw:6.2f} kW  ({eb.drying_thermal_duty_kw * 3.6:6.1f} MJ/h)")
    print(f"Reactor Thermal Duty : {eb.reactor_thermal_duty_kw:6.2f} kW  ({eb.reactor_thermal_duty_kw * 3.6:6.1f} MJ/h)")
    print(f"Condenser Cooling    : {eb.condenser_cooling_duty_kw:6.2f} kW")
    print(f"Auxiliary Electrical : {eb.auxiliary_electrical_power_kw:6.2f} kW")
    print(f"Total External Power : {eb.total_external_energy_input_kw:6.2f} kW")

    print(f"\nPROCESS THERMODYNAMIC KPIS")
    print(f"{sub_border}")
    print(f"Feedstock Chem Power : {eb.feedstock_chemical_power_kw:6.2f} kW (LHV ar: {feedstock.calculate_lhv_as_received():.2f} MJ/kg)")
    print(f"Products Chem Power  : {eb.total_products_chemical_power_kw:6.2f} kW")
    print(f"Energy Recovery      : {eb.energy_recovery_ratio_pct:5.1f} %")
    print(f"Bio-oil Energy Share : {eb.bio_oil_energy_share_pct:5.1f} %")
    print(f"Biochar Energy Share : {eb.biochar_energy_share_pct:5.1f} %")
    print(f"Syngas Energy Share  : {eb.syngas_energy_share_pct:5.1f} %")
    print(f"Net Thermal Effic.   : {eb.net_thermal_efficiency_pct:5.1f} %")

    print(f"\nDIAGNOSTIC STATUS")
    print(f"{sub_border}")
    print(f"Input Validation     : PASS")
    print(f"Mass Balance Status  : {mb.status}")
    print(f"Energy Balance Status: {eb.status}")

    if mb.warnings or eb.warnings:
        print(f"\nWARNINGS & ADVISORIES:")
        for w_msg in mb.warnings + eb.warnings:
            print(f" [!] {w_msg}")

    print(f"{border}\n")


def build_parser() -> argparse.ArgumentParser:
    """Build command-line parser."""
    parser = argparse.ArgumentParser(
        description="AI-Integrated Biomass Pyrolysis Plant Simulation Platform (V0.1)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to scenario YAML configuration file.",
    )
    parser.add_argument(
        "--feedstock",
        type=str,
        default=None,
        help="Feedstock profile name (e.g. olive_pomace, pine_sawdust, wheat_straw, rice_husk).",
    )
    parser.add_argument(
        "--feed-rate",
        type=float,
        default=None,
        help="Wet biomass feed rate in kg/h (e.g. 100.0).",
    )
    parser.add_argument(
        "--moisture",
        type=float,
        default=None,
        help="Feedstock initial moisture content in wt%% (e.g. 15.0).",
    )
    parser.add_argument(
        "--temp",
        type=float,
        default=None,
        help="Reactor pyrolysis temperature in °C (e.g. 500.0).",
    )
    parser.add_argument(
        "--heating-rate",
        type=float,
        default=None,
        help="Reactor heating rate in °C/min (e.g. 10.0).",
    )
    parser.add_argument(
        "--residence-time",
        type=float,
        default=None,
        help="Reactor residence time in min (e.g. 20.0).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print raw JSON simulation output to stdout.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Save simulation results JSON to specified file path.",
    )
    return parser


def main() -> None:
    """CLI execution entrypoint."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = build_parser()
    args = parser.parse_args()

    # Load configuration
    if args.config:
        scenario = ConfigManager.load_config_file(args.config)
    else:
        # Check if default_plant.yaml exists
        default_yaml = Path(__file__).resolve().parent.parent / "configs" / "default_plant.yaml"
        if default_yaml.is_file():
            scenario = ConfigManager.load_config_file(default_yaml)
        else:
            scenario = ConfigManager.get_default_config()

    simulator = BiomassPlantSimulator()

    try:
        report = simulator.run_simulation(
            scenario=scenario,
            feedstock_name=args.feedstock,
            feed_rate_kg_h=args.feed_rate,
            moisture_pct=args.moisture,
            reactor_temp_c=args.temp,
            heating_rate_c_min=args.heating_rate,
            residence_time_min=args.residence_time,
        )
    except Exception as e:
        print(f"\n[ERROR] Simulation failed: {e}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report.to_json(indent=2))
        print(f"Simulation report written to {out_path}")

    if args.json:
        print(report.to_json(indent=2))
    else:
        print_simulation_dashboard(report)


if __name__ == "__main__":
    main()
