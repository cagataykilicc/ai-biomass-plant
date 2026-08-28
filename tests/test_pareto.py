"""Unit tests for multiobjective Pareto frontier optimization."""

import pytest
import numpy as np
from src.optimization.pareto import ParetoOptimizer, ParetoFrontier, ParetoSolution


def test_pareto_dominance_logic() -> None:
    """Verify non-dominated sorting logic."""
    optimizer = ParetoOptimizer(feedstock_name="olive_pomace")

    vec_a = np.array([50.0, 30.0, 100.0])
    vec_b = np.array([45.0, 25.0, 80.0])   # A strictly dominates B
    vec_c = np.array([40.0, 35.0, 110.0])  # Non-dominated with A

    assert optimizer._dominates(vec_a, vec_b) is True
    assert optimizer._dominates(vec_b, vec_a) is False
    assert optimizer._dominates(vec_a, vec_c) is False
    assert optimizer._dominates(vec_c, vec_a) is False


def test_pareto_frontier_generation() -> None:
    """Verify generation of non-dominated Pareto frontier."""
    optimizer = ParetoOptimizer(feedstock_name="pine_sawdust")
    frontier: ParetoFrontier = optimizer.generate_pareto_frontier(n_candidates=20, random_seed=42)

    non_dom = frontier.get_non_dominated_solutions()
    assert len(non_dom) >= 1
    assert frontier.evaluated_candidates_count == 20

    df = frontier.to_dataframe()
    assert len(df) == len(non_dom)
    assert "bio_oil_yield_dry_pct" in df.columns
    assert "thermal_self_sufficiency_index_pct" in df.columns
