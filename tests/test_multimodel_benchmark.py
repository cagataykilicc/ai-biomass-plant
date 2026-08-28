"""Unit tests for MultiModelBenchmark suite and leaderboard generation."""

import pytest
import pandas as pd
from pathlib import Path
from src.ml.benchmark import MultiModelBenchmark
from src.data.synthetic_generator import SyntheticProcessDataGenerator, SyntheticGeneratorConfig


def test_multimodel_benchmark_execution(tmp_path: Path) -> None:
    """Verify benchmark runs across multiple candidate models and outputs leaderboard."""
    # Generate small temporary dataset
    cfg = SyntheticGeneratorConfig(n_samples=40, random_seed=42)
    gen = SyntheticProcessDataGenerator(config=cfg)
    records = gen.generate_dataset(n_samples=40)
    df = pd.DataFrame([r.to_flat_dict() for r in records])

    data_file = tmp_path / "test_data.csv"
    df.to_csv(data_file, index=False)

    ckpt_dir = tmp_path / "checkpoints"
    benchmark = MultiModelBenchmark(dataset_path=str(data_file), output_dir=str(ckpt_dir))

    # Run quick benchmark with RF, Extra Trees, Ridge
    test_models = ["random_forest", "extra_trees", "ridge"]
    res = benchmark.run_benchmark(models=test_models)

    assert "leaderboard" in res
    assert len(res["leaderboard"]) == 3
    assert "champion_model" in res["metadata"]
    assert res["metadata"]["champion_model"] in test_models

    # Verify champion checkpoint exists
    champ_path = ckpt_dir / "yield_predictor_champion.joblib"
    assert champ_path.is_file()
