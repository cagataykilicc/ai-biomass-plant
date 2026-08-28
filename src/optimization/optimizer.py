"""Single-objective process optimization algorithms using Scipy SLSQP and Differential Evolution.

Finds globally optimal operational setpoints satisfying First-Law mass balances and
combustor thermal self-sufficiency constraints (TSI >= 100%).
"""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Dict, Any, Optional, Union
import numpy as np
from scipy.optimize import minimize, differential_evolution

from src.simulation.plant_simulator import SimulationReport
from src.optimization.objectives import OptimizationObjective, EconomicParameters
from src.optimization.problem import OptimizationProblem, DecisionBounds


@dataclass
class OptimizationResult:
    """Optimal process operating solution and associated KPIs."""
    success: bool
    objective: OptimizationObjective
    feedstock_name: str
    optimal_setpoints: Dict[str, float]
    optimal_objective_value: float
    report: SimulationReport
    economic_breakdown: Dict[str, float]
    solver_name: str
    iterations: int
    execution_time_sec: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "objective": self.objective.value,
            "feedstock_name": self.feedstock_name,
            "optimal_setpoints": self.optimal_setpoints,
            "optimal_objective_value": round(self.optimal_objective_value, 3),
            "solver_name": self.solver_name,
            "iterations": self.iterations,
            "execution_time_sec": round(self.execution_time_sec, 3),
            "economic_breakdown": self.economic_breakdown,
            "key_kpis": {
                "bio_oil_yield_dry_pct": self.report.reactor.yields_dry.bio_oil_yield * 100.0,
                "biochar_yield_dry_pct": self.report.reactor.yields_dry.biochar_yield * 100.0,
                "syngas_yield_dry_pct": self.report.reactor.yields_dry.syngas_yield * 100.0,
                "recovered_bio_oil_kg_h": self.report.separation.recovered_bio_oil_liquid_kg_h,
                "recovered_biochar_kg_h": self.report.separation.recovered_biochar_kg_h,
                "thermal_self_sufficiency_index_pct": self.report.combustion.thermal_self_sufficiency_index_pct,
                "net_thermal_efficiency_pct": self.report.energy_balance.net_thermal_efficiency_pct,
            },
        }


class PlantProcessOptimizer:
    """Solves plant-level single-objective optimization problems."""

    def __init__(self, problem: OptimizationProblem) -> None:
        self.problem = problem

    def optimize_slsqp(
        self,
        initial_guess: Optional[np.ndarray] = None,
        max_iter: int = 100,
    ) -> OptimizationResult:
        """Local optimization using Sequential Least Squares Programming (SLSQP)."""
        t0 = time.perf_counter()
        x0 = initial_guess if initial_guess is not None else self.problem.bounds.get_initial_guess()
        bounds = self.problem.bounds.get_bounds_tuples()

        res = minimize(
            fun=self.problem.evaluate_penalized_loss,
            x0=x0,
            method="SLSQP",
            bounds=bounds,
            options={"maxiter": max_iter, "ftol": 1e-4},
        )

        t_elapsed = time.perf_counter() - t0
        x_opt = res.x
        report = self.problem.evaluate_simulation(x_opt)
        obj_val = self.problem.evaluate_objective(x_opt)
        econ_dict = self.problem.econ_params.calculate_margin_usd_h(report)

        setpoints = {
            "reactor_temp_c": round(float(x_opt[0]), 2),
            "heating_rate_c_min": round(float(x_opt[1]), 2),
            "residence_time_min": round(float(x_opt[2]), 2),
            "feed_rate_kg_h": round(float(x_opt[3]), 2),
            "dryer_target_moisture_pct": round(float(x_opt[4]), 2),
        }

        return OptimizationResult(
            success=bool(res.success),
            objective=self.problem.objective,
            feedstock_name=self.problem.feedstock_name,
            optimal_setpoints=setpoints,
            optimal_objective_value=float(obj_val),
            report=report,
            economic_breakdown=econ_dict,
            solver_name="SLSQP",
            iterations=int(res.nit) if hasattr(res, "nit") else 0,
            execution_time_sec=t_elapsed,
        )

    def optimize_differential_evolution(
        self,
        max_iter: int = 30,
        popsize: int = 10,
        seed: int = 42,
    ) -> OptimizationResult:
        """Global non-convex optimization using Differential Evolution."""
        t0 = time.perf_counter()
        bounds = self.problem.bounds.get_bounds_tuples()

        res = differential_evolution(
            func=self.problem.evaluate_penalized_loss,
            bounds=bounds,
            maxiter=max_iter,
            popsize=popsize,
            seed=seed,
            tol=1e-3,
            mutation=(0.5, 1.0),
            recombination=0.7,
        )

        t_elapsed = time.perf_counter() - t0
        x_opt = res.x
        report = self.problem.evaluate_simulation(x_opt)
        obj_val = self.problem.evaluate_objective(x_opt)
        econ_dict = self.problem.econ_params.calculate_margin_usd_h(report)

        setpoints = {
            "reactor_temp_c": round(float(x_opt[0]), 2),
            "heating_rate_c_min": round(float(x_opt[1]), 2),
            "residence_time_min": round(float(x_opt[2]), 2),
            "feed_rate_kg_h": round(float(x_opt[3]), 2),
            "dryer_target_moisture_pct": round(float(x_opt[4]), 2),
        }

        return OptimizationResult(
            success=bool(res.success),
            objective=self.problem.objective,
            feedstock_name=self.problem.feedstock_name,
            optimal_setpoints=setpoints,
            optimal_objective_value=float(obj_val),
            report=report,
            economic_breakdown=econ_dict,
            solver_name="Differential_Evolution",
            iterations=int(res.nit),
            execution_time_sec=t_elapsed,
        )

    def optimize(self, solver: str = "differential_evolution") -> OptimizationResult:
        """Execute single-objective optimization with requested solver."""
        if solver.lower() in ["slsqp", "local"]:
            return self.optimize_slsqp()
        return self.optimize_differential_evolution()
