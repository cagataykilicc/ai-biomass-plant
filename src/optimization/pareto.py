"""Multiobjective optimization and Non-Dominated Sorting Pareto Frontier generator (NSGA-II).

Generates the non-dominated Pareto trade-off surface between competing industrial objectives:
1. Liquid Bio-Oil Yield (%)
2. Solid Biochar Carbon Retention (%)
3. Thermal Self-Sufficiency (TSI %)
4. Gross Operational Profit ($/h)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json
import numpy as np
import pandas as pd

from src.simulation.plant_simulator import BiomassPlantSimulator, SimulationReport
from src.optimization.objectives import EconomicParameters
from src.optimization.problem import DecisionBounds, OptimizationProblem


@dataclass
class ParetoSolution:
    """Individual evaluated solution on the multiobjective landscape."""
    solution_id: int
    decision_vector: List[float]
    setpoints: Dict[str, float]
    objectives: Dict[str, float]
    is_self_sufficient: bool
    rank: int = 1
    crowding_distance: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "solution_id": self.solution_id,
            "setpoints": self.setpoints,
            "objectives": {k: round(v, 3) for k, v in self.objectives.items()},
            "is_self_sufficient": self.is_self_sufficient,
            "rank": self.rank,
            "crowding_distance": round(self.crowding_distance, 4),
        }


@dataclass
class ParetoFrontier:
    """Collection of non-dominated solutions representing the optimal trade-off surface."""
    feedstock_name: str
    solutions: List[ParetoSolution]
    evaluated_candidates_count: int

    def get_non_dominated_solutions(self) -> List[ParetoSolution]:
        return [s for s in self.solutions if s.rank == 1]

    def to_dataframe(self) -> pd.DataFrame:
        rows = []
        for s in self.get_non_dominated_solutions():
            row = {"solution_id": s.solution_id}
            row.update(s.setpoints)
            row.update(s.objectives)
            row["is_self_sufficient"] = s.is_self_sufficient
            rows.append(row)
        return pd.DataFrame(rows)

    def to_dict(self) -> Dict[str, Any]:
        non_dom = self.get_non_dominated_solutions()
        return {
            "feedstock_name": self.feedstock_name,
            "total_evaluated_candidates": self.evaluated_candidates_count,
            "pareto_optimal_count": len(non_dom),
            "pareto_solutions": [s.to_dict() for s in non_dom],
        }

    def save_json(self, file_path: Optional[str] = None) -> Path:
        out = (
            Path(file_path)
            if file_path
            else Path(__file__).resolve().parent.parent.parent / "reports" / "pareto_frontier.json"
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
        return out


class ParetoOptimizer:
    """Multiobjective non-dominated sorting Pareto optimizer."""

    def __init__(
        self,
        feedstock_name: str = "olive_pomace",
        bounds: Optional[DecisionBounds] = None,
        yield_mode: str = "ML_SURROGATE",
        econ_params: Optional[EconomicParameters] = None,
        simulator: Optional[BiomassPlantSimulator] = None,
    ) -> None:
        self.feedstock_name = feedstock_name
        self.bounds = bounds or DecisionBounds()
        self.yield_mode = yield_mode
        self.econ_params = econ_params or EconomicParameters()
        self.simulator = simulator or BiomassPlantSimulator()

    def _dominates(self, obj_a: np.ndarray, obj_b: np.ndarray) -> bool:
        """Check if vector A Pareto-dominates vector B (for maximization)."""
        return bool(np.all(obj_a >= obj_b) and np.any(obj_a > obj_b))

    def _fast_non_dominated_sort(self, candidates: List[ParetoSolution], obj_matrix: np.ndarray) -> List[ParetoSolution]:
        """Perform NSGA-II Fast Non-Dominated Sorting."""
        n = len(candidates)
        domination_counts = np.zeros(n, dtype=int)
        dominated_sets: List[List[int]] = [[] for _ in range(n)]
        fronts: List[List[int]] = [[]]

        for p in range(n):
            for q in range(n):
                if p == q:
                    continue
                if self._dominates(obj_matrix[p], obj_matrix[q]):
                    dominated_sets[p].append(q)
                elif self._dominates(obj_matrix[q], obj_matrix[p]):
                    domination_counts[p] += 1

            if domination_counts[p] == 0:
                candidates[p].rank = 1
                fronts[0].append(p)

        i = 0
        while i < len(fronts) and len(fronts[i]) > 0:
            next_front: List[int] = []
            for p in fronts[i]:
                for q in dominated_sets[p]:
                    domination_counts[q] -= 1
                    if domination_counts[q] == 0:
                        candidates[q].rank = i + 2
                        next_front.append(q)
            i += 1
            if next_front:
                fronts.append(next_front)

        return candidates

    def generate_pareto_frontier(
        self,
        n_candidates: int = 120,
        random_seed: int = 42,
        require_self_sufficient: bool = True,
    ) -> ParetoFrontier:
        """Generate non-dominated Pareto frontier across multiple objectives."""
        rng = np.random.default_rng(random_seed)
        bounds_tuples = self.bounds.get_bounds_tuples()

        problem = OptimizationProblem(
            feedstock_name=self.feedstock_name,
            bounds=self.bounds,
            yield_mode=self.yield_mode,
            econ_params=self.econ_params,
            simulator=self.simulator,
        )

        # 1. Stratified Latin Hypercube Sampling of decision space
        n_dim = len(bounds_tuples)
        lhs_raw = np.empty((n_candidates, n_dim))
        for j in range(n_dim):
            intervals = np.linspace(0, 1, n_candidates + 1)
            pts = rng.uniform(intervals[:-1], intervals[1:])
            rng.shuffle(pts)
            lhs_raw[:, j] = pts

        candidates: List[ParetoSolution] = []
        obj_list: List[List[float]] = []

        for i in range(n_candidates):
            x_vec = np.zeros(n_dim)
            for j, (b_low, b_high) in enumerate(bounds_tuples):
                x_vec[j] = b_low + (b_high - b_low) * lhs_raw[i, j]

            try:
                report: SimulationReport = problem.evaluate_simulation(x_vec)
                econ_dict = self.econ_params.calculate_margin_usd_h(report)
                tsi = report.combustion.thermal_self_sufficiency_index_pct

                if require_self_sufficient and tsi < 99.0:
                    continue  # Filter out non-autonomous operating states

                oil_yield = report.reactor.yields_dry.bio_oil_yield * 100.0
                char_yield = report.reactor.yields_dry.biochar_yield * 100.0
                margin = econ_dict["gross_margin_usd_h"]
                thermal_eff = report.energy_balance.net_thermal_efficiency_pct

                setpoints = {
                    "reactor_temp_c": round(float(x_vec[0]), 2),
                    "heating_rate_c_min": round(float(x_vec[1]), 2),
                    "residence_time_min": round(float(x_vec[2]), 2),
                    "feed_rate_kg_h": round(float(x_vec[3]), 2),
                    "dryer_target_moisture_pct": round(float(x_vec[4]), 2),
                }

                objs = {
                    "bio_oil_yield_dry_pct": float(oil_yield),
                    "biochar_yield_dry_pct": float(char_yield),
                    "gross_margin_usd_h": float(margin),
                    "thermal_efficiency_pct": float(thermal_eff),
                    "thermal_self_sufficiency_index_pct": float(tsi),
                }

                # Objectives vector to maximize: [bio_oil_yield, biochar_yield, gross_margin, thermal_eff]
                obj_arr = [oil_yield, char_yield, margin, thermal_eff]

                sol = ParetoSolution(
                    solution_id=len(candidates) + 1,
                    decision_vector=x_vec.tolist(),
                    setpoints=setpoints,
                    objectives=objs,
                    is_self_sufficient=bool(tsi >= 100.0),
                )
                candidates.append(sol)
                obj_list.append(obj_arr)
            except Exception:
                continue

        if not candidates:
            raise RuntimeError("No feasible candidates satisfied the constraints.")

        obj_matrix = np.array(obj_list, dtype=np.float64)
        ranked_candidates = self._fast_non_dominated_sort(candidates, obj_matrix)

        frontier = ParetoFrontier(
            feedstock_name=self.feedstock_name,
            solutions=ranked_candidates,
            evaluated_candidates_count=n_candidates,
        )
        return frontier
