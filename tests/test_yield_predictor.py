"""Unit tests for ML YieldPredictorModel training, inference, and serialization."""

import pytest
import numpy as np
from pathlib import Path
from src.data.feedstock import BiomassFeedstock
from src.ml.yield_predictor import YieldPredictorModel
from src.ml.feature_engineering import FeatureEngineeringPipeline


def test_yield_predictor_fit_and_predict(sample_olive_pomace: BiomassFeedstock, tmp_path: Path) -> None:
    """Verify model training, single-instance prediction, and disk serialization."""
    pipeline = FeatureEngineeringPipeline(scale_features=False)
    n_samples = 40
    n_features = len(pipeline.FEATURE_NAMES)

    # Synthetic mock training data
    X_train = np.random.uniform(10.0, 60.0, (n_samples, n_features))
    # Synthetic yields that sum to ~100%
    y_char = np.random.uniform(20.0, 35.0, (n_samples, 1))
    y_oil = np.random.uniform(40.0, 60.0, (n_samples, 1))
    y_gas = 100.0 - y_char - y_oil
    y_train = np.hstack([y_char, y_oil, y_gas])

    model = YieldPredictorModel(model_type="random_forest", feature_pipeline=pipeline)
    model.fit(X_train, y_train)

    assert model.is_fitted is True

    # Test single-point prediction
    res = model.predict_feedstock_yields(
        feedstock=sample_olive_pomace,
        reactor_temp_c=500.0,
        heating_rate_c_min=10.0,
        residence_time_min=20.0,
        enforce_physics=True,
    )

    assert "biochar_yield" in res
    assert "bio_oil_yield" in res
    assert "syngas_yield" in res
    assert pytest.approx(res["biochar_yield"] + res["bio_oil_yield"] + res["syngas_yield"], rel=1e-5) == 1.0

    # Test serialization
    ckpt_path = tmp_path / "test_model.joblib"
    model.save(ckpt_path)
    assert ckpt_path.is_file()

    loaded_model = YieldPredictorModel.load(ckpt_path)
    assert loaded_model.is_fitted is True
    res_loaded = loaded_model.predict_feedstock_yields(
        feedstock=sample_olive_pomace,
        reactor_temp_c=500.0,
        heating_rate_c_min=10.0,
        residence_time_min=20.0,
    )
    assert pytest.approx(res["biochar_yield"], rel=1e-4) == res_loaded["biochar_yield"]
