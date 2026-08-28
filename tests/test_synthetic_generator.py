"""Unit tests for Latin Hypercube synthetic process dataset generator."""

import pytest
import pandas as pd
from src.data.synthetic_generator import SyntheticProcessDataGenerator, SyntheticGeneratorConfig
from src.data.eda_analyzer import DatasetProfiler


def test_synthetic_generator_batch() -> None:
    """Verify LHS generator creates valid records within parameter bounds."""
    cfg = SyntheticGeneratorConfig(n_samples=25, random_seed=42, inject_sensor_noise=False)
    generator = SyntheticProcessDataGenerator(config=cfg)

    records = generator.generate_dataset(n_samples=25)
    assert len(records) == 25

    df = pd.DataFrame([r.to_flat_dict() for r in records])
    assert (df["reactor_temp_c"] >= 350.0).all()
    assert (df["reactor_temp_c"] <= 750.0).all()
    assert (df["biochar_yield_dry_pct"] > 0.0).all()
    assert (df["bio_oil_yield_dry_pct"] > 0.0).all()
    assert (df["syngas_yield_dry_pct"] > 0.0).all()
    assert (df["is_synthetic"] == True).all()


def test_dataset_profiler_and_report() -> None:
    """Verify statistical profiler computes univariate stats and correlation matrix."""
    cfg = SyntheticGeneratorConfig(n_samples=30, random_seed=42)
    generator = SyntheticProcessDataGenerator(config=cfg)
    records = generator.generate_dataset(n_samples=30)
    df = pd.DataFrame([r.to_flat_dict() for r in records])

    profiler = DatasetProfiler()
    report = profiler.profile_dataset(df=df)

    assert "dataset_metadata" in report
    assert report["dataset_metadata"]["total_observations"] == 30
    assert "correlations_with_targets" in report
    assert "feature_statistics" in report
    assert "reactor_temp_c" in report["feature_statistics"]
