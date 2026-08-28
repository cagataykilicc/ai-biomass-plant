"""Unit tests for SoftSensorSuite and 95% Uncertainty Quantification intervals."""

import pytest
import numpy as np
from pathlib import Path
from src.sensors.telemetry import HardwareTelemetryPacket
from src.sensors.soft_sensor_engine import SoftSensorSuite, SoftSensorEstimate


def test_soft_sensor_suite_fit_and_inference(tmp_path: Path) -> None:
    """Verify soft sensor training, 95% interval calculation, and serialization."""
    n_samples = 40
    n_features = 10
    X_mock = np.random.uniform(50.0, 500.0, (n_samples, n_features))

    y_mock = {
        "bio_oil_tan_mg_koh_g": np.random.uniform(80.0, 110.0, n_samples),
        "bio_oil_water_pct": np.random.uniform(20.0, 30.0, n_samples),
        "bio_oil_hhv_mj_kg": np.random.uniform(12.0, 16.0, n_samples),
        "syngas_lhv_vol_mj_nm3": np.random.uniform(10.0, 16.0, n_samples),
        "biochar_yield_dry_pct": np.random.uniform(20.0, 35.0, n_samples),
        "thermal_self_sufficiency_index_pct": np.random.uniform(90.0, 130.0, n_samples),
    }

    suite = SoftSensorSuite(n_estimators=30, max_depth=6, random_state=42)
    suite.fit(X_mock, y_mock)
    assert suite.is_fitted is True

    telemetry = HardwareTelemetryPacket(
        timestamp="2026-08-28T12:00:00",
        feedstock_name="Mock Pine",
        TI_101=180.0, TI_102=105.0, TI_103=500.0, TI_104=485.0, TI_105=35.0, TI_106=1350.0,
        FI_101=100.0, FI_102=150.0, FI_103=80.0, PI_101=4.5,
    )

    estimates = suite.estimate_all(telemetry)
    assert len(estimates) == 6

    for tag, est in estimates.items():
        assert isinstance(est, SoftSensorEstimate)
        assert est.lower_95_ci <= est.point_estimate <= est.upper_95_ci
        assert est.uncertainty_std > 0.0
        assert est.health_status in ["NORMAL", "HIGH_UNCERTAINTY"]

    # Test serialization
    ckpt_file = tmp_path / "test_ss.joblib"
    suite.save(ckpt_file)
    assert ckpt_file.is_file()

    loaded = SoftSensorSuite.load(ckpt_file)
    assert loaded.is_fitted is True
    est2 = loaded.predict_single("SS_101_BIO_OIL_TAN", telemetry.to_feature_vector())
    assert est2.point_estimate == estimates["SS_101_BIO_OIL_TAN"].point_estimate
