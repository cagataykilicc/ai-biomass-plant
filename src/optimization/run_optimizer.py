"""CLI interface and reporting engine for plant process optimization and Pareto analysis.

Usage:
    python -m src.optimization.run_optimizer --feedstock olive_pomace --objective max_bio_oil
    python -m src.optimization.run_optimizer --feedstock pine_sawdust --multiobjective
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from src.optimization.objectives import OptimizationObjective, EconomicParameters
from src.optimization.problem import OptimizationProblem, DecisionBounds
from src.optimization.optimizer import PlantProcessOptimizer
from src.optimization.pareto import ParetoOptimizer, ParetoFrontier
from src.optimization.decision_maker import TOPSISDecisionMaker


def run_single_objective_cli(
    feedstock: str = "olive_pomace",
    objective_name: str = "max_bio_oil",
    solver: str = "differential_evolution",
    require_self_sufficient: bool = True,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute single-objective optimization."""
    obj_map = {
        "max_bio_oil": OptimizationObjective.MAX_BIO_OIL_YIELD,
        "max_biochar": OptimizationObjective.MAX_BIOCHAR_CARBON,
        "max_profit": OptimizationObjective.MAX_ECONOMIC_MARGIN,
        "max_efficiency": OptimizationObjective.MAX_THERMAL_EFFICIENCY,
        "max_exergy": OptimizationObjective.MAX_EXERGY_EFFICIENCY,
    }
    target_obj = obj_map.get(objective_name.lower(), OptimizationObjective.MAX_BIO_OIL_YIELD)

    problem = OptimizationProblem(
        feedstock_name=feedstock,
        objective=target_obj,
        require_self_sufficient=require_self_sufficient,
        yield_mode="ML_SURROGATE",
    )
    optimizer = PlantProcessOptimizer(problem=problem)

    print(f"[*] Solving Single-Objective Optimization: {target_obj.value}...")
    print(f"[*] Feedstock: {feedstock} | Solver: {solver.upper()} | Self-Sufficiency Required: {require_self_sufficient}")

    res = optimizer.optimize(solver=solver)

    # Print results dashboard
    w = 68
    border = "=" * w
    print(f"\n{border}")
    print(f"       AI PROCESS OPTIMIZATION RESULTS ({target_obj.value})")
    print(f"{border}")
    print(f"Feedstock            : {res.feedstock_name}")
    print(f"Solver Engine        : {res.solver_name} ({res.iterations} iterations in {res.execution_time_sec:.2f}s)")
    print(f"Optimization Status  : {'CONVERGED (SUCCESS)' if res.success else 'STOPPED'}")

    print("\nOPTIMAL OPERATIONAL SETPOINTS:")
    print("-" * w)
    for sp_name, sp_val in res.optimal_setpoints.items():
        print(f"  * {sp_name:<28}: {sp_val}")

    print("\nRESULTING PROCESS KPIS:")
    print("-" * w)
    rep = res.report
    print(f"  * Bio-Oil Recovery        : {rep.separation.recovered_bio_oil_liquid_kg_h:.2f} kg/h ({rep.reactor.yields_dry.bio_oil_yield*100:.1f} wt% dry)")
    print(f"  * Biochar Recovery        : {rep.separation.recovered_biochar_kg_h:.2f} kg/h ({rep.reactor.yields_dry.biochar_yield*100:.1f} wt% dry)")
    print(f"  * Clean Syngas Rate       : {rep.separation.clean_syngas_kg_h:.2f} kg/h ({rep.reactor.yields_dry.syngas_yield*100:.1f} wt% dry)")
    print(f"  * Thermal Self-Sufficiency: {rep.combustion.thermal_self_sufficiency_index_pct:.1f} %  -> {'[AUTONOMOUS]' if rep.combustion.is_thermally_self_sufficient else '[EXTERNAL FUEL NEEDED]'}")
    print(f"  * Net Thermal Efficiency  : {rep.energy_balance.net_thermal_efficiency_pct:.1f} %")
    print(f"  * Gross Hourly Margin     : ${res.economic_breakdown['gross_margin_usd_h']:.2f} / hour")
    print(f"{border}\n")

    res_dict = res.to_dict()
    if output_path:
        out_file = Path(output_path)
    else:
        out_file = Path(__file__).resolve().parent.parent.parent / "reports" / "process_optimization_report.json"

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(res_dict, f, indent=2)
    print(f"[OK] Optimization report written to {out_file}")
    return res_dict


def run_multiobjective_cli(
    feedstock: str = "olive_pomace",
    n_candidates: int = 120,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute multiobjective Pareto frontier optimization and TOPSIS decision support."""
    pareto_opt = ParetoOptimizer(feedstock_name=feedstock)
    print(f"[*] Generating Multiobjective Pareto Frontier ({n_candidates} candidates)...")
    frontier: ParetoFrontier = pareto_opt.generate_pareto_frontier(n_candidates=n_candidates)
    pareto_sols = frontier.get_non_dominated_solutions()
    print(f"[OK] Discovered {len(pareto_sols)} non-dominated Pareto optimal solutions.")

    # Save Pareto frontier JSON
    pareto_path = frontier.save_json()
    print(f"[OK] Pareto frontier saved to {pareto_path}")

    # Run TOPSIS Decision Maker across all built-in stakeholder profiles
    topsis_recommendations: Dict[str, Any] = {}
    print("\n" + "=" * 75)
    print("      TOPSIS MULTI-CRITERIA DECISION SUPPORT RECOMMENDATIONS")
    print("=" * 75)

    for p_key, p_obj in TOPSISDecisionMaker.BUILTIN_PROFILES.items():
        best_sol = TOPSISDecisionMaker.get_best_solution(frontier, profile_name=p_key)
        topsis_recommendations[p_key] = best_sol

        print(f"\nStakeholder Profile: [{p_obj.name}]")
        print(f"Description: {p_obj.description}")
        sp = best_sol.get("setpoints", {})
        objs = best_sol.get("objectives", {})
        print(f"  Recommended Setpoints: T = {sp.get('reactor_temp_c')} °C, Beta = {sp.get('heating_rate_c_min')} °C/min, Tau = {sp.get('residence_time_min')} min")
        print(f"  Predicted Outcomes   : Bio-oil = {objs.get('bio_oil_yield_dry_pct')}% | Biochar = {objs.get('biochar_yield_dry_pct')}% | Margin = ${objs.get('gross_margin_usd_h')}/h | TSI = {objs.get('thermal_self_sufficiency_index_pct')}%")

    print("\n" + "=" * 75 + "\n")

    report_payload = {
        "feedstock_name": feedstock,
        "pareto_frontier_summary": frontier.to_dict(),
        "topsis_recommendations": topsis_recommendations,
    }

    out_file = Path(output_path) if output_path else Path(__file__).resolve().parent.parent.parent / "reports" / "process_optimization_report.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report_payload, f, indent=2)
    print(f"[OK] Multiobjective optimization report saved to {out_file}")
    return report_payload


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Plant Process Optimization and Pareto Decision Engine")
    parser.add_argument("--feedstock", type=str, default="olive_pomace", help="Feedstock profile name")
    parser.add_argument("--objective", type=str, default="max_bio_oil", choices=["max_bio_oil", "max_biochar", "max_profit", "max_efficiency", "max_exergy"])
    parser.add_argument("--solver", type=str, default="differential_evolution", choices=["differential_evolution", "slsqp"])
    parser.add_argument("--multiobjective", action="store_true", help="Generate full Pareto frontier and run TOPSIS MCDM")
    parser.add_argument("--output", type=str, default=None, help="Output JSON report path")
    args = parser.parse_args()

    if args.multiobjective:
        run_multiobjective_cli(feedstock=args.feedstock, output_path=args.output)
    else:
        run_single_objective_cli(
            feedstock=args.feedstock,
            objective_name=args.objective,
            solver=args.solver,
            output_path=args.output,
        )


if __name__ == "__main__":
    main()
