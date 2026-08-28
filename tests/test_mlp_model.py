"""Unit tests for Multi-Layer Perceptron (MLP) neural network yield surrogate."""

import pytest
import numpy as np
from src.data.feedstock import BiomassFeedstock
from src.ml.yield_predictor import YieldPredictorModel
from src.ml.feature_engineering import FeatureEngineeringPipeline


def test_mlp_model_training_and_inference(sample_olive_pomace: BiomassFeedstock) -> None:
    """Verify MLP neural network regressor trains, scales features, and predicts on simplex."""
    pipeline = FeatureEngineeringPipeline(scale_features=True)
    n_samples = 50
    n_features = len(pipeline.FEATURE_NAMES)

    X_mock = np.random.uniform(5.0, 50.0, (n_samples, n_features))
    y_char = np.random.uniform(20.0, 30.0, (n_samples, 1))
    y_oil = np.random.uniform(45.0, 55.0, (n_samples, 1))
    y_gas = 100.0 - y_char - y_oil
    y_mock = np.hstack([y_char, y_oil, y_gas])

    mlp_model = YieldPredictorModel(model_type="mlp", feature_pipeline=pipeline)
    mlp_model.fit(X_mock, y_mock)

    assert mlp_model.is_fitted is True

    preds = mlp_model.predict_feedstock_yields(
        feedstock=sample_olive_pomace,
        reactor_temp_c=500.0,
        heating_rate_c_min=10.0,
        residence_time_min=20.0,
        enforce_physics=True,
    )

    assert "biochar_yield" in preds
    assert "bio_oil_yield" in preds
    assert "syngas_yield" in preds
    assert pytest.approx(preds["biochar_yield"] + preds["bio_oil_yield"] + preds["syngas_yield"], rel=1e-5) == 1.0
