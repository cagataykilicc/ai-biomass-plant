"""Multi-target Machine Learning surrogate model for biomass pyrolysis yield prediction.

Wraps scikit-learn ensemble regressors (Random Forest, Extra Trees, MultiOutput Gradient Boosting)
with automatic physics-informed constraint projection and model serialization.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import joblib
import numpy as np
from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor,
)
from sklearn.multioutput import MultiOutputRegressor

from src.data.feedstock import BiomassFeedstock
from src.ml.feature_engineering import FeatureEngineeringPipeline
from src.ml.constraints import PhysicsConstraintProjector


class YieldPredictorModel:
    """Multi-target machine learning surrogate regressor for biochar, bio-oil, and syngas yields."""

    SUPPORTED_MODELS = ["random_forest", "extra_trees", "gradient_boosting"]

    def __init__(
        self,
        model_type: str = "random_forest",
        model_kwargs: Optional[Dict[str, Any]] = None,
        feature_pipeline: Optional[FeatureEngineeringPipeline] = None,
    ) -> None:
        if model_type not in self.SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model_type '{model_type}'. Choose from: {self.SUPPORTED_MODELS}")

        self.model_type = model_type
        self.model_kwargs = model_kwargs or self._get_default_kwargs(model_type)
        self.feature_pipeline = feature_pipeline or FeatureEngineeringPipeline(scale_features=False)
        self.estimator = self._init_estimator(model_type, self.model_kwargs)
        self.is_fitted: bool = False

    def _get_default_kwargs(self, model_type: str) -> Dict[str, Any]:
        if model_type in ["random_forest", "extra_trees"]:
            return {
                "n_estimators": 150,
                "max_depth": 14,
                "min_samples_split": 4,
                "min_samples_leaf": 2,
                "random_state": 42,
                "n_jobs": -1,
            }
        elif model_type == "gradient_boosting":
            return {
                "n_estimators": 120,
                "max_depth": 5,
                "learning_rate": 0.08,
                "random_state": 42,
            }
        return {}

    def _init_estimator(self, model_type: str, kwargs: Dict[str, Any]):
        if model_type == "random_forest":
            return RandomForestRegressor(**kwargs)
        elif model_type == "extra_trees":
            return ExtraTreesRegressor(**kwargs)
        elif model_type == "gradient_boosting":
            base_gb = GradientBoostingRegressor(**kwargs)
            return MultiOutputRegressor(base_gb)
        raise ValueError(f"Unknown model_type: {model_type}")

    def fit(self, X: np.ndarray, y: np.ndarray) -> YieldPredictorModel:
        """Train the surrogate model on features X and multi-target yields y."""
        self.estimator.fit(X, y)
        self.is_fitted = True
        return self

    def predict_raw(self, X: np.ndarray) -> np.ndarray:
        """Generate raw, unconstrained yield predictions from the underlying ML model."""
        if not self.is_fitted:
            raise RuntimeError("Model is not fitted. Call .fit() or load a pretrained model checkpoint.")
        return self.estimator.predict(X)

    def predict_constrained(self, X: np.ndarray) -> np.ndarray:
        """Generate physics-constrained yield predictions guaranteed to sum to 100.00%."""
        raw = self.predict_raw(X)
        return PhysicsConstraintProjector.project_yields(raw)

    def predict_feedstock_yields(
        self,
        feedstock: BiomassFeedstock,
        reactor_temp_c: float,
        heating_rate_c_min: float,
        residence_time_min: float,
        feed_rate_wet_kg_h: float = 100.0,
        enforce_physics: bool = True,
    ) -> Dict[str, float]:
        """Predict yields for a single feedstock and operating state.

        Returns:
            Dictionary containing biochar_yield, bio_oil_yield, syngas_yield (dry wt fraction in [0, 1]).
        """
        X = self.feature_pipeline.extract_features_single(
            feedstock=feedstock,
            reactor_temp_c=reactor_temp_c,
            heating_rate_c_min=heating_rate_c_min,
            residence_time_min=residence_time_min,
            feed_rate_wet_kg_h=feed_rate_wet_kg_h,
        )
        if enforce_physics:
            preds = self.predict_constrained(X)[0]
        else:
            preds = self.predict_raw(X)[0]

        return {
            "biochar_yield": float(preds[0] / 100.0),
            "bio_oil_yield": float(preds[1] / 100.0),
            "syngas_yield": float(preds[2] / 100.0),
            "biochar_yield_pct": float(round(preds[0], 2)),
            "bio_oil_yield_pct": float(round(preds[1], 2)),
            "syngas_yield_pct": float(round(preds[2], 2)),
        }

    def save(self, file_path: Union[str, Path]) -> Path:
        """Serialize model artifact to disk using joblib."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "model_type": self.model_type,
            "model_kwargs": self.model_kwargs,
            "estimator": self.estimator,
            "is_fitted": self.is_fitted,
            "feature_pipeline": self.feature_pipeline,
        }
        joblib.dump(payload, path)
        return path

    @classmethod
    def load(cls, file_path: Union[str, Path]) -> YieldPredictorModel:
        """Load serialized model artifact from disk."""
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Model checkpoint not found at: {path}")

        payload = joblib.load(path)
        model = cls(
            model_type=payload["model_type"],
            model_kwargs=payload["model_kwargs"],
            feature_pipeline=payload["feature_pipeline"],
        )
        model.estimator = payload["estimator"]
        model.is_fitted = payload["is_fitted"]
        return model
