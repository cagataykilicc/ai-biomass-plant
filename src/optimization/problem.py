"""Decision parameter bounds, non-linear constraint definitions, and optimization problem formulation.

Encapsulates decision space vector mappings:
x = [reactor_temp_c, heating_rate_c_min, residence_time_min, feed_rate_kg_h, target_moisture_pct]
and enforces physical thermodynamic constraints (TSI >= 100%, quality limits).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional
import numpy as np

from src.simulation.plant_simulator import BiomassPlantSimulator, SimulationReport
from src.utils.config import PlantScenarioConfig
from src.optimization.objectives import OptimizationObjective, ObjectiveEvaluator, EconomicParameters


@dataclass
class DecisionBounds:
    """Continuous variable bounds for industrial biomass plant operation."""
    temp_min_c: float = 380.0
    temp_max_c: float = 700.0
    heating_rate_min_c_min: float = 5.0
    heating_rate_max_c_min: float = 500.0
    residence_time_min: float = 0.5
    residence_time_max: float = 40.0
    feed_rate_min_kg_h: float = 50.0
    feed_rate_max_kg_h: float = 300.0
    moisture_target_min_pct: float = 4.0
    moisture_target_max_pct: float = 12.0

    def get_bounds_tuples(self) -> List[Tuple[float, float]]:
        return [
            (self.temp_min_c, self.temp_max_c),
            (self.heating_rate_min_c_min, self.heating_rate_max_c_min),
            (self.residence_time_min, self.residence_time_max),
            (self.feed_rate_min_kg_h, self.feed_rate_max_kg_h),
            (self.moisture_target_min_pct, self.moisture_target_max_pct),
        ]

    def get_initial_guess(self) -> np.ndarray:
        return np.array([
            (self.temp_min_c + self.temp_max_c) / 2.0,
            10.0,
            20.0,
            100.0,
            8.0,
        ], dtype=np.float64)


class OptimizationProblem:
    """Evaluates objective functions and non-linear physical constraints for an operating state."""

    def __init__(
        self,
        feedstock_name: str = "olive_pomace",
        objective: OptimizationObjective = OptimizationObjective.MAX_BIO_OIL_YIELD,
        bounds: Optional[DecisionBounds] = None,
        require_self_sufficient: bool = True,
        yield_mode: str = "ML_SURROGATE",
        econ_params: Optional[EconomicParameters] = None,
        simulator: Optional[BiomassPlantSimulator] = None,
    ) -> None:
        self.feedstock_name = feedstock_name
        self.objective = objective
        self.bounds = bounds or DecisionBounds()
        self.require_self_sufficient = require_self_sufficient
        self.yield_mode = yield_mode
        self.econ_params = econ_params or EconomicParameters()
        self.simulator = simulator or BiomassPlantSimulator()

    def vector_to_scenario(self, x: np.ndarray) -> PlantScenarioConfig:
        """Map optimization decision vector x to PlantScenarioConfig."""
        temp_c = float(np.clip(x[0], self.bounds.temp_min_c, self.bounds.temp_max_c))
        hr_c_min = float(np.clip(x[1], self.bounds.heating_rate_min_c_min, self.bounds.heating_rate_max_c_min))
        res_time = float(np.clip(x[2], self.bounds.residence_time_min, self.bounds.residence_time_max))
        feed_rate = float(np.clip(x[3], self.bounds.feed_rate_min_kg_h, self.bounds.feed_rate_max_kg_h))
        moist_target = float(np.clip(x[4], self.bounds.moisture_target_min_pct, self.bounds.moisture_target_max_pct))

        cfg = PlantScenarioConfig(
            feedstock_name=self.feedstock_name,
            feed_rate_kg_h=feed_rate,
        )
        cfg.drying.target_moisture_pct = moist_target
        cfg.reactor.temperature_c = temp_c
        cfg.reactor.heating_rate_c_min = hr_c_min
        cfg.reactor.residence_time_min = res_time
        cfg.reactor.yield_mode = self.yield_mode
        return cfg

    def evaluate_simulation(self, x: np.ndarray) -> SimulationReport:
        """Run plant simulation for vector x."""
        cfg = self.vector_to_scenario(x)
        return self.simulator.run_simulation(
            scenario=cfg,
            feedstock_name=self.feedstock_name,
            feed_rate_kg_h=cfg.feed_rate_kg_h,
            reactor_temp_c=cfg.reactor.temperature_c,
            heating_rate_c_min=cfg.reactor.heating_rate_c_min,
            residence_time_min=cfg.reactor.residence_time_min,
            yield_mode=self.yield_mode,
        )

    def evaluate_objective(self, x: np.ndarray) -> float:
        """Calculate unpenalized scalar objective value (higher is better)."""
        report = self.evaluate_simulation(x)
        return ObjectiveEvaluator.evaluate(self.objective, report, self.econ_params)

    def evaluate_penalized_loss(self, x: np.ndarray) -> float:
        """Calculate penalized minimization loss for gradient/metaheuristic solvers."""
        try:
            report = self.evaluate_simulation(x)
            obj_val = ObjectiveEvaluator.evaluate(self.objective, report, self.econ_params)
            
            # Constraints: g_k(x) >= 0
            penalty = 0.0
            if self.require_self_sufficient:
                tsi = report.combustion.thermal_self_sufficiency_index_pct
                if tsi < 100.0:
                    # Penalty proportional to energy deficit
                    deficit = 100.0 - tsi
                    penalty += 50.0 * (deficit ** 2)

            # Maximize objective <=> Minimize (-objective + penalty)
            return float(-obj_val + penalty)
        except Exception:
            return 1e6
