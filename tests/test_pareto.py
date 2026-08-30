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


def test_api_optimize_pareto_integration() -> None:
    """Verify REST API handle_optimize returns correct schema for frontend Canvas rendering."""
    from src.api.handlers import APIRequestHandler

    res = APIRequestHandler.handle_optimize({
        "feedstock": "olive_pomace",
        "mode": "pareto",
        "profile": "bio_oil",
    })

    assert "frontier" in res
    assert len(res["frontier"]) > 0
    assert "top_solution" in res
    assert "topsis_score" in res
    assert res["profile_applied"] == "bio_oil_maximizer"

    sample = res["frontier"][0]
    assert "objectives" in sample
    assert "bio_oil_yield_dry_pct" in sample["objectives"]
    assert "biochar_yield_dry_pct" in sample["objectives"]
    assert "gross_margin_usd_h" in sample["objectives"]
    assert sample["objectives"]["bio_oil_yield_dry_pct"] > 0
    assert sample["objectives"]["biochar_yield_dry_pct"] > 0

