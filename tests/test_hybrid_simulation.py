"""Unit tests for hybrid plant simulation comparing deterministic and ML surrogate modes."""

import pytest
import numpy as np
from src.data.feedstock import BiomassFeedstock
from src.ml.yield_predictor import YieldPredictorModel
from src.ml.feature_engineering import FeatureEngineeringPipeline
from src.simulation.plant_simulator import BiomassPlantSimulator, SimulationReport


def test_hybrid_simulation_modes(sample_olive_pomace: BiomassFeedstock) -> None:
    """Verify plant simulation executes cleanly in both DETERMINISTIC and ML_SURROGATE modes."""
    # Create and fit a dummy fast ML model
    pipeline = FeatureEngineeringPipeline(scale_features=False)
    X_dummy = np.random.uniform(10.0, 60.0, (20, len(pipeline.FEATURE_NAMES)))
    y_dummy = np.tile([28.0, 48.0, 24.0], (20, 1))
    ml_model = YieldPredictorModel(model_type="random_forest", feature_pipeline=pipeline)
    ml_model.fit(X_dummy, y_dummy)

    sim = BiomassPlantSimulator(ml_yield_predictor=ml_model)

    # 1. Run Deterministic Mode
    rep_det: SimulationReport = sim.run_simulation(
        feedstock_name="olive_pomace",
        feed_rate_kg_h=100.0,
        yield_mode="DETERMINISTIC",
    )
    assert rep_det.reactor.yield_engine_used == "DETERMINISTIC"
    assert rep_det.mass_balance.status == "PASS"
    assert rep_det.elemental_balance.overall_status == "PASS"

    # 2. Run ML Surrogate Mode
    rep_ml: SimulationReport = sim.run_simulation(
        feedstock_name="olive_pomace",
        feed_rate_kg_h=100.0,
        yield_mode="ML_SURROGATE",
    )
    assert rep_ml.reactor.yield_engine_used == "ML_SURROGATE"
    assert rep_ml.mass_balance.status == "PASS"
    assert rep_ml.elemental_balance.overall_status == "PASS"
    assert rep_ml.combustion.thermal_self_sufficiency_index_pct > 0.0
