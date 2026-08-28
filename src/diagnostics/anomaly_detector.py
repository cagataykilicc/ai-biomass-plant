"""Tri-layer process anomaly detection engine combining physical residuals, Isolation Forest, and PCA reconstruction.

Layers:
1. Physical Conservation Residuals (Mass, elemental, and heat integration closures).
2. Unsupervised Isolation Forest spatial anomaly scoring.
3. PCA Reconstruction Error: Squared Prediction Error (SPE / Q-statistic) and Hotelling's T² with 99% UCL.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from src.sensors.telemetry import HardwareTelemetryPacket
from src.simulation.plant_simulator import SimulationReport


@dataclass
class AnomalyDetectionResult:
    """Consolidated anomaly detection diagnostics across all detection layers."""
    is_anomaly: bool
    overall_anomaly_score: float  # [0.0, 1.0] (0 = healthy normal, 1 = severe anomaly)
    isolation_forest_anomaly: bool
    isolation_forest_score: float
    pca_q_statistic: float
    pca_q_limit_99: float
    pca_q_exceeded: bool
    pca_t2_statistic: float
    pca_t2_limit_99: float
    pca_t2_exceeded: bool
    physical_residual_violation: bool
    top_contributing_sensors: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MultiLayerAnomalyDetector:
    """Tri-layer anomaly detection system for industrial biomass conversion digital twins."""

    def __init__(
        self,
        n_components_pca: int = 5,
        contamination: float = 0.05,
        random_state: int = 42,
    ) -> None:
        self.n_components_pca = n_components_pca
        self.contamination = contamination
        self.random_state = random_state

        self.scaler = StandardScaler()
        self.pca = PCA(n_components=n_components_pca, random_state=random_state)
        self.iforest = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=120,
        )
        self.q_limit_99: float = 1.0
        self.t2_limit_99: float = 1.0
        self.is_fitted: bool = False

    def fit(self, X_normal: np.ndarray) -> MultiLayerAnomalyDetector:
        """Train anomaly detectors on normal baseline operating telemetry."""
        # 1. Scale data
        X_scaled = self.scaler.fit_transform(X_normal)

        # 2. Fit Isolation Forest
        self.iforest.fit(X_scaled)

        # 3. Fit PCA and compute 99% Upper Control Limits (UCL) for Q and T²
        self.pca.fit(X_scaled)
        X_proj = self.pca.transform(X_scaled)
        X_recon = self.pca.inverse_transform(X_proj)

        # Q-statistic (SPE): Reconstruction residual sum of squares
        q_stats = np.sum((X_scaled - X_recon) ** 2, axis=1)
        self.q_limit_99 = float(np.percentile(q_stats, 99.0))

        # Hotelling's T²: Mahalanobis distance in principal subspace
        eigenvalues = np.maximum(1e-4, self.pca.explained_variance_)
        t2_stats = np.sum((X_proj ** 2) / eigenvalues, axis=1)
        self.t2_limit_99 = float(np.percentile(t2_stats, 99.0))

        self.is_fitted = True
        return self

    def detect(
        self,
        telemetry: HardwareTelemetryPacket,
        report: Optional[SimulationReport] = None,
    ) -> AnomalyDetectionResult:
        """Run multi-layer anomaly detection on an incoming telemetry packet."""
        if not self.is_fitted:
            raise RuntimeError("Anomaly detector is not fitted. Call .fit() or load a pretrained checkpoint.")

        x_raw = telemetry.to_feature_vector().reshape(1, -1)
        x_scaled = self.scaler.transform(x_raw)

        # 1. Isolation Forest Evaluation
        # decision_function yields negative for anomalies, positive for normal
        if_raw_score = float(self.iforest.decision_function(x_scaled)[0])
        # Transform into normalized anomaly likelihood in [0, 1]
        if_anomaly_score = float(1.0 / (1.0 + np.exp(6.0 * if_raw_score)))
        if_flag = bool(self.iforest.predict(x_scaled)[0] == -1)

        # 2. PCA Reconstruction Evaluation
        x_proj = self.pca.transform(x_scaled)
        x_recon = self.pca.inverse_transform(x_proj)

        # Q-statistic & Sensor Residual Contributions
        residuals = (x_scaled - x_recon)[0]
        q_stat = float(np.sum(residuals ** 2))
        q_flag = bool(q_stat > self.q_limit_99)

        # Hotelling's T²
        eigenvalues = np.maximum(1e-4, self.pca.explained_variance_)
        t2_stat = float(np.sum((x_proj[0] ** 2) / eigenvalues))
        t2_flag = bool(t2_stat > self.t2_limit_99)

        # Feature contribution rankings
        contribs = []
        tags = HardwareTelemetryPacket.FEATURE_TAGS
        for i, tag in enumerate(tags):
            contribs.append({
                "sensor_tag": tag,
                "squared_residual": round(float(residuals[i] ** 2), 4),
            })
        contribs.sort(key=lambda item: item["squared_residual"], reverse=True)

        # 3. First-Principles Balance Check
        phys_flag = False
        if report is not None:
            mb_closure = report.mass_balance.closure_pct
            if abs(mb_closure - 100.0) > 2.5:
                phys_flag = True

        # Composite Anomaly Decision
        overall_score = float(np.clip(
            0.40 * if_anomaly_score +
            0.30 * min(2.0, q_stat / self.q_limit_99) / 2.0 +
            0.20 * min(2.0, t2_stat / self.t2_limit_99) / 2.0 +
            0.10 * (1.0 if phys_flag else 0.0),
            0.0, 1.0
        ))

        is_anomaly = bool(overall_score >= 0.45 or q_flag or if_flag or phys_flag)

        return AnomalyDetectionResult(
            is_anomaly=is_anomaly,
            overall_anomaly_score=round(overall_score, 4),
            isolation_forest_anomaly=if_flag,
            isolation_forest_score=round(if_anomaly_score, 4),
            pca_q_statistic=round(q_stat, 4),
            pca_q_limit_99=round(self.q_limit_99, 4),
            pca_q_exceeded=q_flag,
            pca_t2_statistic=round(t2_stat, 4),
            pca_t2_limit_99=round(self.t2_limit_99, 4),
            pca_t2_exceeded=t2_flag,
            physical_residual_violation=phys_flag,
            top_contributing_sensors=contribs[:4],
        )

    def save(self, file_path: Union[str, Path]) -> Path:
        """Serialize anomaly detector artifact to disk."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "scaler": self.scaler,
            "pca": self.pca,
            "iforest": self.iforest,
            "q_limit_99": self.q_limit_99,
            "t2_limit_99": self.t2_limit_99,
            "is_fitted": self.is_fitted,
        }
        joblib.dump(payload, path)
        return path

    @classmethod
    def load(cls, file_path: Union[str, Path]) -> MultiLayerAnomalyDetector:
        """Load serialized anomaly detector checkpoint."""
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Anomaly detector checkpoint not found at: {path}")

        payload = joblib.load(path)
        det = cls()
        det.scaler = payload["scaler"]
        det.pca = payload["pca"]
        det.iforest = payload["iforest"]
        det.q_limit_99 = payload["q_limit_99"]
        det.t2_limit_99 = payload["t2_limit_99"]
        det.is_fitted = payload["is_fitted"]
        return det
