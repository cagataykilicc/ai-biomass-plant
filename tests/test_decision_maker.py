"""Unit tests for TOPSIS Multi-Criteria Decision Making engine."""

import pytest
from src.optimization.pareto import ParetoOptimizer, ParetoFrontier
from src.optimization.decision_maker import TOPSISDecisionMaker, StakeholderProfile


def test_topsis_solution_ranking() -> None:
    """Verify TOPSIS ranking across non-dominated Pareto solutions."""
    optimizer = ParetoOptimizer(feedstock_name="olive_pomace")
    frontier = optimizer.generate_pareto_frontier(n_candidates=25, random_seed=42)

    # Test ranking for all built-in profiles
    for profile_key in TOPSISDecisionMaker.BUILTIN_PROFILES:
        ranked = TOPSISDecisionMaker.rank_solutions(frontier, profile_name=profile_key)
        assert len(ranked) >= 1
        assert ranked[0]["rank"] == 1
        assert 0.0 <= ranked[0]["closeness_score"] <= 1.0
        # Verify scores are descending
        scores = [r["closeness_score"] for r in ranked]
        assert scores == sorted(scores, reverse=True)


def test_custom_stakeholder_profile() -> None:
    """Verify custom stakeholder weights and validation."""
    custom = StakeholderProfile(
        name="Custom Investor",
        description="Custom margin profile",
        weights={"gross_margin_usd_h": 0.80, "thermal_efficiency_pct": 0.20},
    )
    custom.validate()

    optimizer = ParetoOptimizer(feedstock_name="pine_sawdust")
    frontier = optimizer.generate_pareto_frontier(n_candidates=20, random_seed=42)
    ranked = TOPSISDecisionMaker.rank_solutions(frontier, profile=custom)
    assert len(ranked) >= 1
    assert ranked[0]["profile_name"] == "Custom Investor"
