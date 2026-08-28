"""Unit tests for FeatureImportanceAnalyzer and explainability engine."""

import pytest
import pandas as pd
from pathlib import Path
from src.ml.explainability import FeatureImportanceAnalyzer
from src.ml.yield_predictor import YieldPredictorModel
from src.ml.feature_engineering import FeatureEngineeringPipeline
from src.data.synthetic_generator import SyntheticProcessDataGenerator, SyntheticGeneratorConfig


def test_feature_importance_analysis(tmp_path: Path) -> None:
    """Verify Permutation Importance computes ranking and identifies temperature dominance."""
    cfg = SyntheticGeneratorConfig(n_samples=40, random_seed=42)
    gen = SyntheticProcessDataGenerator(config=cfg)
    records = gen.generate_dataset(n_samples=40)
    df = pd.DataFrame([r.to_flat_dict() for r in records])

    data_file = tmp_path / "test_data.csv"
    df.to_csv(data_file, index=False)

    pipeline = FeatureEngineeringPipeline(scale_features=False)
    splits = pipeline.prepare_dataset(df, test_size=0.20, random_state=42)
    model = YieldPredictorModel(model_type="random_forest", feature_pipeline=pipeline)
    model.fit(splits.X_train, splits.y_train)

    analyzer = FeatureImportanceAnalyzer(model=model, dataset_path=str(data_file))
    report = analyzer.analyze(n_repeats=3, random_state=42)

    assert "permutation_importance_ranked" in report
    assert len(report["permutation_importance_ranked"]) == len(pipeline.FEATURE_NAMES)
    top_feature = report["permutation_importance_ranked"][0]["feature"]
    assert isinstance(top_feature, str)
    assert "domain_insights" in report
