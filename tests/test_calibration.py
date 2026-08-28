"""Unit tests for SoftSensorCalibrator and calibration report generation."""

import pytest
import pandas as pd
from pathlib import Path
from src.sensors.calibration import SoftSensorCalibrator
from src.data.synthetic_generator import SyntheticProcessDataGenerator, SyntheticGeneratorConfig


def test_soft_sensor_calibrator_run(tmp_path: Path) -> None:
    """Verify soft sensor calibration pipeline trains on dataset and outputs metrics."""
    cfg = SyntheticGeneratorConfig(n_samples=50, random_seed=42)
    gen = SyntheticProcessDataGenerator(config=cfg)
    records = gen.generate_dataset(n_samples=50)
    df = pd.DataFrame([r.to_flat_dict() for r in records])

    data_file = tmp_path / "test_data.csv"
    df.to_csv(data_file, index=False)

    ckpt_file = tmp_path / "soft_sensors.joblib"
    report_file = tmp_path / "report.json"

    calibrator = SoftSensorCalibrator(
        dataset_path=str(data_file),
        checkpoint_path=str(ckpt_file),
        report_path=str(report_file),
    )
    res = calibrator.calibrate(test_size=0.20)

    assert "sensor_benchmarks" in res
    assert len(res["sensor_benchmarks"]) == 6
    assert ckpt_file.is_file()
    assert report_file.is_file()

    for tag, bm in res["sensor_benchmarks"].items():
        assert "r2_score" in bm
        assert "prediction_interval_coverage_pct" in bm
