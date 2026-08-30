"""Multi-Criteria Decision Making (MCDM) using the TOPSIS method for Pareto solution selection.

TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution) ranks non-dominated
operating states based on customizable commercial stakeholder preference profiles.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import numpy as np

from src.optimization.pareto import ParetoFrontier, ParetoSolution


@dataclass
class StakeholderProfile:
    """Weight configuration defining stakeholder priorities."""
    name: str
    description: str
    weights: Dict[str, float]

    def validate(self) -> None:
        total = sum(self.weights.values())
        if not (0.95 <= total <= 1.05):
            raise ValueError(f"Weights in profile '{self.name}' must sum to 1.0 (got {total:.2f})")


class TOPSISDecisionMaker:
    """Applies TOPSIS algorithm to select the best operating point from a Pareto frontier."""

    BUILTIN_PROFILES: Dict[str, StakeholderProfile] = {
        "bio_oil_maximizer": StakeholderProfile(
            name="Bio-Oil Maximizer",
            description="Prioritizes liquid bio-oil yield for chemical/fuel refinery supply.",
            weights={
                "bio_oil_yield_dry_pct": 0.85,
                "gross_margin_usd_h": 0.10,
                "thermal_efficiency_pct": 0.05,
            },
        ),
        "biochar_carbon_priority": StakeholderProfile(
            name="Carbon Sequestration Priority",
            description="Prioritizes solid biochar yield for soil amendment and certified carbon removal.",
            weights={
                "biochar_yield_dry_pct": 0.85,
                "gross_margin_usd_h": 0.10,
                "thermal_efficiency_pct": 0.05,
            },
        ),
        "economic_profit_priority": StakeholderProfile(
            name="Economic Profit Maximizer",
            description="Maximizes gross operational profit margin ($/h) with self-sufficiency.",
            weights={
                "gross_margin_usd_h": 0.85,
                "bio_oil_yield_dry_pct": 0.10,
                "thermal_efficiency_pct": 0.05,
            },
        ),
        "balanced_sustainability": StakeholderProfile(
            name="Balanced Sustainability",
            description="Harmonizes bio-oil yield, carbon retention, thermal efficiency, and margin.",
            weights={
                "bio_oil_yield_dry_pct": 0.35,
                "biochar_yield_dry_pct": 0.35,
                "gross_margin_usd_h": 0.20,
                "thermal_efficiency_pct": 0.10,
            },
        ),
    }

    @classmethod
    def rank_solutions(
        cls,
        frontier: ParetoFrontier,
        profile: Optional[StakeholderProfile] = None,
        profile_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Rank Pareto solutions using TOPSIS and return ordered list with closeness scores."""
        solutions = frontier.get_non_dominated_solutions()
        if not solutions:
            solutions = frontier.solutions

        if profile is None:
            key = (profile_name or "balanced_sustainability").lower()
            if key not in cls.BUILTIN_PROFILES:
                key = "balanced_sustainability"
            selected_profile = cls.BUILTIN_PROFILES[key]
        else:
            selected_profile = profile

        selected_profile.validate()
        criteria_keys = list(selected_profile.weights.keys())
        w_vector = np.array([selected_profile.weights[k] for k in criteria_keys], dtype=np.float64)

        # 1. Build Decision Matrix (N x M)
        n = len(solutions)
        m = len(criteria_keys)
        X = np.zeros((n, m), dtype=np.float64)

        for i, sol in enumerate(solutions):
            for j, key in enumerate(criteria_keys):
                X[i, j] = sol.objectives.get(key, 0.0)

        # 2. Min-Max Range Normalization (prevents scale bias between % and $)
        x_min = np.min(X, axis=0)
        x_max = np.max(X, axis=0)
        denom = np.where(x_max == x_min, 1.0, x_max - x_min)
        R = (X - x_min) / denom

        # 3. Weighted Normalized Decision Matrix
        V = R * w_vector

        # 4. Ideal Best (A+) and Ideal Worst (A-)
        A_plus = np.max(V, axis=0)
        A_minus = np.min(V, axis=0)

        # 5. Euclidean Distances
        S_plus = np.sqrt(np.sum((V - A_plus) ** 2, axis=1))
        S_minus = np.sqrt(np.sum((V - A_minus) ** 2, axis=1))

        # 6. Relative Closeness to Ideal Solution: C_i = S- / (S+ + S-)
        denom_s = S_plus + S_minus
        denom_s = np.where(denom_s == 0, 1.0, denom_s)
        closeness = S_minus / denom_s

        # 7. Sort by descending closeness
        ranked_results = []
        for i, sol in enumerate(solutions):
            res_item = {
                "rank": 0,
                "solution_id": sol.solution_id,
                "closeness_score": round(float(closeness[i]), 4),
                "profile_name": selected_profile.name,
                "setpoints": sol.setpoints,
                "objectives": sol.objectives,
                "is_self_sufficient": sol.is_self_sufficient,
            }
            ranked_results.append(res_item)

        ranked_results.sort(key=lambda x: x["closeness_score"], reverse=True)
        for r_idx, item in enumerate(ranked_results, start=1):
            item["rank"] = r_idx

        return ranked_results

    @classmethod
    def get_best_solution(
        cls,
        frontier: ParetoFrontier,
        profile_name: str = "balanced_sustainability",
    ) -> Dict[str, Any]:
        """Convenience method returning top-ranked solution for a profile."""
        ranked = cls.rank_solutions(frontier, profile_name=profile_name)
        return ranked[0] if ranked else {}
