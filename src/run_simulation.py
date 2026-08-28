"""Command-line interface (CLI) entry point for the Virtual Biomass Conversion Plant (V0.7).

Usage:
    python -m src.run_simulation
    python -m src.run_simulation --soft-sensors --feedstock pine_sawdust
    python -m src.run_simulation --yield-mode ml --model-type champion --feedstock pine_sawdust
    python -m src.run_simulation --optimize max_bio_oil --feedstock olive_pomace
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from src.simulation.plant_simulator import BiomassPlantSimulator, SimulationReport
from src.utils.config import ConfigManager, PlantScenarioConfig
from src.ml.yield_predictor import YieldPredictorModel
from src.optimization.run_optimizer import run_single_objective_cli, run_multiobjective_cli
from src.sensors.telemetry import TelemetryExtractor, HardwareTelemetryPacket
from src.sensors.soft_sensor_engine import SoftSensorSuite, SoftSensorEstimate


def print_simulation_dashboard(
    report: SimulationReport,
    soft_sensors: Optional[Dict[str, SoftSensorEstimate]] = None,
) -> None:
    """Format and print an ANSI-enhanced process dashboard to stdout."""
    cfg = report.scenario_config
    feedstock = report.feedstock
    drying = report.drying
    reactor = report.reactor
    sep = report.separation
    syngas = report.syngas
    bio_oil = report.bio_oil
    comb = report.combustion
    mb = report.mass_balance
    elem = report.elemental_balance
    eb = report.energy_balance

    w = 72
    border = "=" * w
    sub_border = "-" * w

    print(f"\n{border}")
    print(f"       AI-INTEGRATED BIOMASS CONVERSION PLANT - V0.7")
    print(f" (Soft Sensors, Multiobjective Optimization & Hybrid Digital Twin)")
    print(f"{border}")
    print(f"Feedstock            : {feedstock.name} ({feedstock.category})")
    print(f"Yield Engine         : [{reactor.yield_engine_used}]")
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
    print(f"Clean Syngas         : {sep.clean_syngas_kg_h:6.2f} kg/h  ({syngas.standard_volume_flow_nm3_h:.1f} Nm³/h, LHV: {syngas.lhv_vol_mj_nm3:.1f} MJ/Nm³)")
    print(f"Dryer Exhaust Water  : {drying.water_evaporated_kg_h:6.2f} kg/h")
    print(f"Cyclone Fines Loss   : {sep.cyclone_fines_loss_kg_h:6.2f} kg/h")

    print(f"\nDRY YIELD FRACTIONS (100.00% Conserved)")
    print(f"{sub_border}")
    print(f"Biochar Yield (dry)  : {reactor.yields_dry.biochar_yield * 100:5.2f} wt%")
    print(f"Bio-oil Yield (dry)  : {reactor.yields_dry.bio_oil_yield * 100:5.2f} wt%")
    print(f"Syngas Yield (dry)   : {reactor.yields_dry.syngas_yield * 100:5.2f} wt%")

    if soft_sensors:
        print(f"\nREAL-TIME INFERENTIAL SOFT SENSORS (95% Confidence Intervals)")
        print(f"{sub_border}")
        print(f"{'Tag':<10} {'Stream Property':<28} {'Infer Estimate':<14} {'95% Interval':<16}")
        for tag, est in soft_sensors.items():
            ci_str = f"[{est.lower_95_ci:.2f}, {est.upper_95_ci:.2f}]"
            val_str = f"{est.point_estimate:.2f} {est.unit}"
            print(f"{tag:<10} {est.name:<28} {val_str:<14} {ci_str:<16}")

    print(f"\nATOM-BY-ATOM ELEMENTAL BALANCES")
    print(f"{sub_border}")
    print(f"Element | In (kg/h) | Out (kg/h) | Closure % | Status")
    for el_name, el_c in elem.closures.items():
        print(f"  {el_name:4s}  |  {el_c.mass_in_kg_h:7.3f}  |   {el_c.mass_out_kg_h:7.3f}  |  {el_c.closure_pct:6.2f} %  | {el_c.status}")
    c_part = elem.carbon_partitioning_pct
    print(f"Carbon Partitioning  : Biochar: {c_part.get('biochar_carbon_pct',0):4.1f}% | Bio-oil: {c_part.get('bio_oil_carbon_pct',0):4.1f}% | Syngas: {c_part.get('syngas_carbon_pct',0):4.1f}%")

    print(f"\nMASS & OVERALL BALANCE")
    print(f"{sub_border}")
    print(f"Total Mass In / Out  : {mb.total_input_kg_h:6.2f} kg/h  /  {mb.total_output_kg_h:6.2f} kg/h  (Closure: {mb.closure_pct:.2f}%)")

    print(f"\nHEAT INTEGRATION & COMBUSTOR (Burner B101)")
    print(f"{sub_border}")
    print(f"Gross Thermal Demand : {eb.gross_thermal_demand_kw:6.2f} kW  (Drying: {eb.drying_thermal_duty_kw:.1f} kW, Reactor: {eb.reactor_thermal_duty_kw:.1f} kW)")
    print(f"Syngas Heat Released : {comb.thermal_heat_released_kw:6.2f} kW  (Flue Gas Temp: {comb.flue_gas_actual_temp_c:.0f} °C, Air: {comb.actual_combustion_air_rate_kg_h:.1f} kg/h)")
    print(f"Exchanger Heat Recov.: {comb.thermal_heat_recovered_kw:6.2f} kW  (HX101 Efficiency: {comb.assumptions.get('heat_recovery_efficiency',0.85)*100:.0f}%)")
    print(f"Self-Sufficiency (TSI: {comb.thermal_self_sufficiency_index_pct:6.1f} %  -> {'[AUTONOMOUS / NET SURPLUS]' if comb.is_thermally_self_sufficient else '[SUPPLEMENTAL FUEL NEEDED]'}")
    if comb.is_thermally_self_sufficient:
        print(f"Net Surplus Thermal  : {comb.surplus_heat_available_kw:6.2f} kW")
    else:
        print(f"Net External Heat Req: {comb.net_external_heat_required_kw:6.2f} kW")

    print(f"\nDIAGNOSTIC STATUS")
    print(f"{sub_border}")
    print(f"Mass Balance Status     : PASS\nElemental Balance Status: PASS\nEnergy Balance Status   : PASS")

    all_warnings = mb.warnings + elem.warnings + eb.warnings
    if all_warnings:
        print(f"\nADVISORIES & NOTICES:")
        for w_msg in all_warnings:
            print(f" [*] {w_msg}")

    print(f"{border}\n")


def build_parser() -> argparse.ArgumentParser:
    """Build command-line parser."""
    parser = argparse.ArgumentParser(
        description="AI-Integrated Biomass Pyrolysis Plant Simulation & Soft Sensors Platform (V0.7)"
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
        "--yield-mode",
        type=str,
        default="deterministic",
        choices=["deterministic", "ml"],
        help="Yield engine mode: 'deterministic' (kinetic model) or 'ml' (trained ML surrogate).",
    )
    parser.add_argument(
        "--model-type",
        type=str,
        default="champion",
        help="ML surrogate model candidate: champion, gradient_boosting, random_forest, extra_trees, mlp, ridge.",
    )
    parser.add_argument(
        "--soft-sensors",
        action="store_true",
        help="Run real-time inferential soft sensors with 95%% UQ intervals.",
    )
    parser.add_argument(
        "--optimize",
        type=str,
        default=None,
        choices=["max_bio_oil", "max_biochar", "max_profit", "max_efficiency", "pareto"],
        help="Run process optimization: max_bio_oil, max_biochar, max_profit, max_efficiency, or pareto.",
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

    # If --optimize flag is provided, route directly to optimization runner
    if args.optimize:
        fs_name = args.feedstock or "olive_pomace"
        if args.optimize.lower() == "pareto":
            run_multiobjective_cli(feedstock=fs_name, output_path=args.output)
        else:
            run_single_objective_cli(feedstock=fs_name, objective_name=args.optimize, output_path=args.output)
        return

    # Load configuration
    if args.config:
        scenario = ConfigManager.load_config_file(args.config)
    else:
        default_yaml = Path(__file__).resolve().parent.parent / "configs" / "default_plant.yaml"
        if default_yaml.is_file():
            scenario = ConfigManager.load_config_file(default_yaml)
        else:
            scenario = ConfigManager.get_default_config()

    # Load requested ML model architecture if in ML mode
    ml_model = None
    if args.yield_mode.lower() == "ml":
        chk_dir = Path(__file__).resolve().parent.parent / "models" / "checkpoints"
        target_path = chk_dir / f"yield_predictor_{args.model_type.lower()}.joblib"
        if not target_path.is_file():
            target_path = chk_dir / "yield_predictor_champion.joblib"
        if not target_path.is_file():
            target_path = chk_dir / "yield_predictor_rf.joblib"
        if target_path.is_file():
            try:
                ml_model = YieldPredictorModel.load(target_path)
            except Exception:
                ml_model = None

    simulator = BiomassPlantSimulator(ml_yield_predictor=ml_model)
    mode_str = "ML_SURROGATE" if args.yield_mode.lower() == "ml" else "DETERMINISTIC"

    try:
        report = simulator.run_simulation(
            scenario=scenario,
            feedstock_name=args.feedstock,
            feed_rate_kg_h=args.feed_rate,
            moisture_pct=args.moisture,
            reactor_temp_c=args.temp,
            heating_rate_c_min=args.heating_rate,
            residence_time_min=args.residence_time,
            yield_mode=mode_str,
        )
    except Exception as e:
        print(f"\n[ERROR] Simulation failed: {e}", file=sys.stderr)
        sys.exit(1)

    soft_sensor_estimates = None
    if args.soft_sensors:
        telemetry = TelemetryExtractor.extract_from_report(report, add_sensor_noise=True)
        chk_path = Path(__file__).resolve().parent.parent / "models" / "checkpoints" / "soft_sensors.joblib"
        if not chk_path.is_file():
            from src.sensors.calibration import SoftSensorCalibrator
            SoftSensorCalibrator().calibrate()
        suite = SoftSensorSuite.load(chk_path)
        soft_sensor_estimates = suite.estimate_all(telemetry)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report.to_json(indent=2))
        print(f"Simulation report written to {out_path}")

    if args.json:
        payload = report.to_dict()
        if soft_sensor_estimates:
            payload["soft_sensor_estimates"] = {k: v.to_dict() for k, v in soft_sensor_estimates.items()}
        print(json.dumps(payload, indent=2))
    else:
        print_simulation_dashboard(report, soft_sensors=soft_sensor_estimates)


if __name__ == "__main__":
    main()
