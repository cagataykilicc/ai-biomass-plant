"""Unit tests for MultiLayerAnomalyDetector (Isolation Forest & PCA reconstruction)."""

import pytest
import numpy as np
from pathlib import Path
from src.sensors.telemetry import HardwareTelemetryPacket
from src.diagnostics.anomaly_detector import MultiLayerAnomalyDetector, AnomalyDetectionResult


def test_anomaly_detector_training_and_detection(tmp_path: Path) -> None:
    """Verify anomaly detector trains on normal telemetry and flags outliers."""
    # Synthetic normal telemetry distribution
    n_samples = 60
    X_normal = np.column_stack([
        np.random.normal(180.0, 1.0, n_samples),  # TI_101
        np.random.normal(105.0, 1.0, n_samples),  # TI_102
        np.random.normal(500.0, 5.0, n_samples),  # TI_103
        np.random.normal(485.0, 5.0, n_samples),  # TI_104
        np.random.normal(35.0, 0.5, n_samples),   # TI_105
        np.random.normal(1350.0, 10.0, n_samples),# TI_106
        np.random.normal(100.0, 2.0, n_samples),  # FI_101
        np.random.normal(200.0, 5.0, n_samples),  # FI_102
        np.random.normal(80.0, 2.0, n_samples),   # FI_103
        np.random.normal(4.5, 0.1, n_samples),    # PI_101
    ])

    detector = MultiLayerAnomalyDetector(n_components_pca=4)
    detector.fit(X_normal)
    assert detector.is_fitted is True

    # Test healthy telemetry packet
    tel_healthy = HardwareTelemetryPacket(
        timestamp="2026-08-28T12:00:00",
        feedstock_name="Pine",
        TI_101=180.0, TI_102=105.0, TI_103=500.0, TI_104=485.0, TI_105=35.0, TI_106=1350.0,
        FI_101=100.0, FI_102=200.0, FI_103=80.0, PI_101=4.5,
    )
    res_healthy = detector.detect(tel_healthy)
    assert isinstance(res_healthy, AnomalyDetectionResult)
    assert res_healthy.overall_anomaly_score < 0.50

    # Test severe anomalous telemetry (thermal runaway + delta-P surge)
    tel_anom = HardwareTelemetryPacket(
        timestamp="2026-08-28T12:05:00",
        feedstock_name="Pine",
        TI_101=180.0, TI_102=105.0, TI_103=720.0, TI_104=690.0, TI_105=65.0, TI_106=1700.0,
        FI_101=10.0, FI_102=900.0, FI_103=150.0, PI_101=15.5,
    )
    res_anom = detector.detect(tel_anom)
    assert res_anom.is_anomaly is True
    assert res_anom.overall_anomaly_score > 0.50

    # Test serialization
    ckpt_file = tmp_path / "detector.joblib"
    detector.save(ckpt_file)
    assert ckpt_file.is_file()

    loaded = MultiLayerAnomalyDetector.load(ckpt_file)
    res_loaded = loaded.detect(tel_healthy)
    assert res_loaded.overall_anomaly_score == res_healthy.overall_anomaly_score
