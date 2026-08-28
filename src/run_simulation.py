"""Command-line interface (CLI) entry point for the Virtual Biomass Conversion Plant (V0.5).

Usage:
    python -m src.run_simulation
    python -m src.run_simulation --yield-mode ml --model-type champion --feedstock pine_sawdust
    python -m src.run_simulation --yield-mode ml --model-type mlp --temp 520
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from src.simulation.plant_simulator import BiomassPlantSimulator, SimulationReport
from src.utils.config import ConfigManager, PlantScenarioConfig
from src.ml.yield_predictor import YieldPredictorModel


def print_simulation_dashboard(report: SimulationReport) -> None:
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

    w = 68
    border = "=" * w
    sub_border = "-" * w

    print(f"\n{border}")
    print(f"       AI-INTEGRATED BIOMASS CONVERSION PLANT - V0.5")
    print(f" (Multi-Model AI Benchmark, Explainability & Hybrid Digital Twin)")
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

    print(f"\nSYNGAS MOLECULAR SPECIATION")
    print(f"{sub_border}")
    syngas_vols = syngas.molar_fractions
    print(f"Composition (vol%)   : CO: {syngas_vols.get('CO',0)*100:4.1f}% | CO2: {syngas_vols.get('CO2',0)*100:4.1f}% | CH4: {syngas_vols.get('CH4',0)*100:4.1f}% | H2: {syngas_vols.get('H2',0)*100:4.1f}%")
    print(f"Mean Molecular Weight: {syngas.mean_molecular_weight_kg_kmol:.2f} kg/kmol  | Mass LHV: {syngas.lhv_mass_mj_kg:.2f} MJ/kg")

    print(f"\nBIO-OIL CHEMICAL CHARACTERIZATION")
    print(f"{sub_border}")
    fams = bio_oil.chemical_families_pct
    print(f"Organic Groups (wt%) : Acids: {fams.get('carboxylic_acids_pct',0):4.1f}% | Phenolics: {fams.get('phenolics_and_lignin_pct',0):4.1f}% | Sugars: {fams.get('anhydrosugars_pct',0):4.1f}%")
    print(f"Physical Properties  : pH: {bio_oil.predicted_ph:.2f} | TAN: {bio_oil.total_acid_number_mg_koh_g:.1f} mg KOH/g | Density: {bio_oil.density_kg_m3:.0f} kg/m³")

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

    print(f"\nTHERMODYNAMIC KPIS & EXERGY")
    print(f"{sub_border}")
    print(f"Feedstock Chemical   : {eb.feedstock_chemical_power_kw:6.2f} kW (LHV ar: {feedstock.calculate_lhv_as_received():.2f} MJ/kg)")
    print(f"Products Chemical    : {eb.total_products_chemical_power_kw:6.2f} kW  (Energy Recovery: {eb.energy_recovery_ratio_pct:.1f}%)")
    print(f"Net Thermal Effic.   : {eb.net_thermal_efficiency_pct:5.1f} %")
    if eb.exergy:
        print(f"Second-Law Exergy Eff: {eb.exergy.second_law_exergy_efficiency_pct:5.1f} %  (Exergy Destruction: {eb.exergy.total_plant_exergy_destruction_kw:.1f} kW)")

    print(f"\nDIAGNOSTIC STATUS")
    print(f"{sub_border}")
    print(f"Mass Balance Status     : {mb.status}")
    print(f"Elemental Balance Status: {elem.overall_status}")
    print(f"Energy Balance Status   : {eb.status}")

    all_warnings = mb.warnings + elem.warnings + eb.warnings
    if all_warnings:
        print(f"\nADVISORIES & NOTICES:")
        for w_msg in all_warnings:
            print(f" [*] {w_msg}")

    print(f"{border}\n")


def build_parser() -> argparse.ArgumentParser:
    """Build command-line parser."""
    parser = argparse.ArgumentParser(
        description="AI-Integrated Biomass Pyrolysis Plant Simulation Platform (V0.5)"
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
        help="ML surrogate model candidate: champion, random_forest, extra_trees, gradient_boosting, mlp, ridge.",
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
