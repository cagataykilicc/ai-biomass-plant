"""Unit tests for single-objective optimization solvers (SLSQP & Differential Evolution)."""

import pytest
from src.optimization.objectives import OptimizationObjective
from src.optimization.problem import OptimizationProblem, DecisionBounds
from src.optimization.optimizer import PlantProcessOptimizer, OptimizationResult


def test_slsqp_optimizer_convergence() -> None:
    """Verify SLSQP local solver converges to valid optimal operating setpoints."""
    problem = OptimizationProblem(
        feedstock_name="olive_pomace",
        objective=OptimizationObjective.MAX_BIO_OIL_YIELD,
        require_self_sufficient=True,
    )
    optimizer = PlantProcessOptimizer(problem=problem)

    res: OptimizationResult = optimizer.optimize_slsqp(max_iter=15)
    assert isinstance(res, OptimizationResult)
    assert res.report is not None
    assert 380.0 <= res.optimal_setpoints["reactor_temp_c"] <= 700.0
    assert res.report.mass_balance.status == "PASS"
    assert res.report.combustion.thermal_self_sufficiency_index_pct >= 95.0


def test_differential_evolution_global_solver() -> None:
    """Verify Differential Evolution global solver finds feasible self-sufficient state."""
    problem = OptimizationProblem(
        feedstock_name="pine_sawdust",
        objective=OptimizationObjective.MAX_ECONOMIC_MARGIN,
        require_self_sufficient=True,
    )
    optimizer = PlantProcessOptimizer(problem=problem)

    res = optimizer.optimize_differential_evolution(max_iter=5, popsize=5, seed=42)
    assert res.optimal_objective_value > 0.0
    assert res.report.combustion.thermal_self_sufficiency_index_pct > 0.0
