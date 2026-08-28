"""Industrial soft sensor inferential engine with calibrated 95% Uncertainty Quantification (UQ).

Estimates unmeasured chemical & thermodynamic variables from physical telemetry:
1. SS-101: Bio-Oil Total Acid Number (TAN, mg KOH/g)
2. SS-102: Bio-Oil Water Content (wt%)
3. SS-103: Bio-Oil Higher Heating Value (HHV, MJ/kg)
4. SS-104: Clean Syngas Volumetric LHV (MJ/Nm³)
5. SS-105: Biochar Fixed Carbon Retention (wt%)
6. SS-106: Thermal Self-Sufficiency Index (TSI, %)
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
import joblib
import numpy as np
from sklearn.ensemble import ExtraTreesRegressor

from src.sensors.telemetry import HardwareTelemetryPacket


class SoftSensorTarget(str, Enum):
    """Enumeration of industrial soft sensor tags."""
    BIO_OIL_TAN = "SS_101_BIO_OIL_TAN"
    BIO_OIL_WATER = "SS_102_BIO_OIL_WATER"
    BIO_OIL_HHV = "SS_103_BIO_OIL_HHV"
    SYNGAS_LHV = "SS_104_SYNGAS_LHV"
    BIOCHAR_YIELD = "SS_105_BIOCHAR_YIELD"
    THERMAL_SELF_SUFFICIENCY = "SS_106_TSI"


@dataclass
class SoftSensorEstimate:
    """Individual soft sensor estimation reading with uncertainty bounds."""
    tag: str
    name: str
    unit: str
    point_estimate: float
    uncertainty_std: float
    lower_95_ci: float
    upper_95_ci: float
    health_status: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SoftSensorSuite:
    """Multi-target inferential state estimation suite with tree ensemble uncertainty modeling."""

    SENSOR_SPECS: Dict[str, Dict[str, str]] = {
        "SS_101_BIO_OIL_TAN": {
            "name": "Bio-Oil Total Acid Number",
            "unit": "mg KOH/g",
            "feature_col": "bio_oil_tan_mg_koh_g",
        },
        "SS_102_BIO_OIL_WATER": {
            "name": "Bio-Oil Water Content",
            "unit": "wt%",
            "feature_col": "bio_oil_water_pct",
        },
        "SS_103_BIO_OIL_HHV": {
            "name": "Bio-Oil Higher Heating Value",
            "unit": "MJ/kg",
            "feature_col": "bio_oil_hhv_mj_kg",
        },
        "SS_104_SYNGAS_LHV": {
            "name": "Clean Syngas Volumetric LHV",
            "unit": "MJ/Nm³",
            "feature_col": "syngas_lhv_vol_mj_nm3",
        },
        "SS_105_BIOCHAR_YIELD": {
            "name": "Biochar Solids Yield",
            "unit": "wt%",
            "feature_col": "biochar_yield_dry_pct",
        },
        "SS_106_TSI": {
            "name": "Thermal Self-Sufficiency Index",
            "unit": "%",
            "feature_col": "thermal_self_sufficiency_index_pct",
        },
    }

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 12,
        random_state: int = 42,
    ) -> None:
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state
        self.models: Dict[str, ExtraTreesRegressor] = {}
        self.residual_sigmas: Dict[str, float] = {}
        self.is_fitted: bool = False

    def fit(self, X: np.ndarray, y_dict: Dict[str, np.ndarray]) -> SoftSensorSuite:
        """Train individual tree ensemble estimators for each virtual sensor target."""
        for tag, spec in self.SENSOR_SPECS.items():
            target_key = spec["feature_col"]
            if target_key not in y_dict:
                continue

            y = y_dict[target_key]
            model = ExtraTreesRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                min_samples_split=3,
                random_state=self.random_state,
                n_jobs=-1,
            )
            model.fit(X, y)
            self.models[tag] = model

            # Compute empirical residual standard error
            preds = model.predict(X)
            res_sigma = float(np.std(y - preds))
            self.residual_sigmas[tag] = max(1e-4, res_sigma)

        self.is_fitted = True
        return self

    def predict_single(
        self,
        tag: str,
        x_vec: np.ndarray,
    ) -> SoftSensorEstimate:
        """Infer value and 95% uncertainty interval for a single sensor tag."""
        if tag not in self.models:
            raise KeyError(f"Soft sensor '{tag}' not found or not trained.")

        model = self.models[tag]
        spec = self.SENSOR_SPECS[tag]
        res_sigma = self.residual_sigmas.get(tag, 0.05)

        # Reshape to 2D
        if x_vec.ndim == 1:
            x_2d = x_vec.reshape(1, -1)
        else:
            x_2d = x_vec

        # Tree ensemble individual predictions for variance calculation
        tree_preds = np.array([tree.predict(x_2d)[0] for tree in model.estimators_])
        point_est = float(np.mean(tree_preds))
        ensemble_std = float(np.std(tree_preds))

        # Total combined uncertainty (ensemble disagreement + residual noise)
        total_std = float(np.sqrt(ensemble_std ** 2 + res_sigma ** 2))
        ci_lower = float(point_est - 1.96 * total_std)
        ci_upper = float(point_est + 1.96 * total_std)

        # Health status check
        health = "NORMAL"
        if total_std > (0.15 * abs(point_est) + 1e-3):
            health = "HIGH_UNCERTAINTY"

        return SoftSensorEstimate(
            tag=tag,
            name=spec["name"],
            unit=spec["unit"],
            point_estimate=round(point_est, 3),
            uncertainty_std=round(total_std, 3),
            lower_95_ci=round(ci_lower, 3),
            upper_95_ci=round(ci_upper, 3),
            health_status=health,
        )

    def estimate_all(
        self,
        telemetry: HardwareTelemetryPacket,
    ) -> Dict[str, SoftSensorEstimate]:
        """Infer all 6 virtual stream qualities from physical telemetry readings."""
        x_vec = telemetry.to_feature_vector()
        estimates: Dict[str, SoftSensorEstimate] = {}
        for tag in self.models:
            estimates[tag] = self.predict_single(tag, x_vec)
        return estimates

    def save(self, file_path: Union[str, Path]) -> Path:
        """Serialize trained soft sensor models and uncertainty parameters."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "models": self.models,
            "residual_sigmas": self.residual_sigmas,
            "is_fitted": self.is_fitted,
            "n_estimators": self.n_estimators,
            "max_depth": self.max_depth,
        }
        joblib.dump(payload, path)
        return path

    @classmethod
    def load(cls, file_path: Union[str, Path]) -> SoftSensorSuite:
        """Load serialized soft sensor checkpoint."""
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Soft sensor checkpoint not found at: {path}")

        payload = joblib.load(path)
        suite = cls(
            n_estimators=payload.get("n_estimators", 100),
            max_depth=payload.get("max_depth", 12),
        )
        suite.models = payload["models"]
        suite.residual_sigmas = payload["residual_sigmas"]
        suite.is_fitted = payload["is_fitted"]
        return suite
