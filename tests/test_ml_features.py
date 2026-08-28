"""Unit tests for ML feature extraction and dataset preparation pipeline."""

import pytest
import numpy as np
import pandas as pd
from src.data.feedstock import BiomassFeedstock
from src.ml.feature_engineering import FeatureEngineeringPipeline


def test_feature_extraction_single(sample_olive_pomace: BiomassFeedstock) -> None:
    """Verify feature vector dimensions and content from single feedstock state."""
    pipeline = FeatureEngineeringPipeline(scale_features=False)
    feat_vec = pipeline.extract_features_single(
        feedstock=sample_olive_pomace,
        reactor_temp_c=500.0,
        heating_rate_c_min=10.0,
        residence_time_min=20.0,
        feed_rate_wet_kg_h=100.0,
    )

    assert isinstance(feat_vec, np.ndarray)
    assert feat_vec.shape == (1, len(pipeline.FEATURE_NAMES))
    assert feat_vec[0, 0] == sample_olive_pomace.ultimate.carbon
    assert feat_vec[0, 12] == 500.0


def test_dataset_preparation() -> None:
    """Verify DataFrame dataset splitting into train and test splits."""
    pipeline = FeatureEngineeringPipeline(scale_features=False)
    mock_data = {
        col: np.random.uniform(1.0, 50.0, 50) for col in pipeline.FEATURE_NAMES
    }
    for tgt in pipeline.TARGET_NAMES:
        mock_data[tgt] = np.random.uniform(10.0, 50.0, 50)
    mock_data["feedstock_category"] = ["woody_biomass"] * 25 + ["agricultural_residue"] * 25

    df = pd.DataFrame(mock_data)
    splits = pipeline.prepare_dataset(df, test_size=0.20, random_state=42)

    assert splits.X_train.shape[0] == 40
    assert splits.X_test.shape[0] == 10
    assert splits.y_train.shape == (40, 3)
    assert splits.y_test.shape == (10, 3)
