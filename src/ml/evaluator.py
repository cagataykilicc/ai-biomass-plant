"""Model evaluation, benchmarking, and thermodynamic validation metrics.

Calculates R², RMSE, MAE, cross-validation statistics, and First-Law closure violation errors.
"""

from __future__ import annotations

from typing import Dict, Any, List, Tuple
import numpy as np
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import KFold

from src.ml.constraints import PhysicsConstraintProjector
from src.ml.yield_predictor import YieldPredictorModel


class ModelEvaluator:
    """Evaluates ML surrogate regression performance and physical constraint adherence."""

    @staticmethod
    def evaluate_test_set(
        y_true: np.ndarray,
        y_pred_raw: np.ndarray,
        y_pred_constrained: np.ndarray,
        target_names: List[str],
    ) -> Dict[str, Any]:
        """Compute performance metrics comparing raw vs physics-constrained predictions."""
        metrics: Dict[str, Any] = {
            "per_target_metrics": {},
            "aggregate_metrics": {},
            "physics_closure_diagnostics": {},
        }

        r2_raw_list = []
        r2_const_list = []
        rmse_const_list = []
        mae_const_list = []

        for i, name in enumerate(target_names):
            y_t = y_true[:, i]
            y_p_raw = y_pred_raw[:, i]
            y_p_const = y_pred_constrained[:, i]

            r2_r = float(r2_score(y_t, y_p_raw))
            r2_c = float(r2_score(y_t, y_p_const))
            rmse_c = float(np.sqrt(mean_squared_error(y_t, y_p_const)))
            mae_c = float(mean_absolute_error(y_t, y_p_const))

            r2_raw_list.append(r2_r)
            r2_const_list.append(r2_c)
            rmse_const_list.append(rmse_c)
            mae_const_list.append(mae_c)

            metrics["per_target_metrics"][name] = {
                "r2_score_raw": round(r2_r, 4),
                "r2_score_constrained": round(r2_c, 4),
                "rmse_constrained_wt_pct": round(rmse_c, 4),
                "mae_constrained_wt_pct": round(mae_c, 4),
            }

        metrics["aggregate_metrics"] = {
            "mean_r2_score_constrained": round(float(np.mean(r2_const_list)), 4),
            "mean_rmse_constrained": round(float(np.mean(rmse_const_list)), 4),
            "mean_mae_constrained": round(float(np.mean(mae_const_list)), 4),
        }

        # Physical closure error diagnostics on raw predictions
        raw_violations = PhysicsConstraintProjector.compute_closure_violation(y_pred_raw)
        const_violations = PhysicsConstraintProjector.compute_closure_violation(y_pred_constrained)

        metrics["physics_closure_diagnostics"] = {
            "raw_unconstrained_mean_closure_error_pct": round(float(np.mean(raw_violations)), 4),
            "raw_unconstrained_max_closure_error_pct": round(float(np.max(raw_violations)), 4),
            "constrained_mean_closure_error_pct": round(float(np.mean(const_violations)), 6),
            "constrained_max_closure_error_pct": round(float(np.max(const_violations)), 6),
            "mass_conservation_guaranteed": bool(np.max(const_violations) < 1e-4),
        }

        return metrics

    @staticmethod
    def cross_validate(
        X: np.ndarray,
        y: np.ndarray,
        model_type: str = "random_forest",
        n_splits: int = 5,
        random_state: int = 42,
    ) -> Dict[str, Any]:
        """Perform K-Fold Cross Validation on ML surrogate."""
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
        fold_r2_scores = []
        fold_maes = []

        for fold, (train_idx, val_idx) in enumerate(kf.split(X, y)):
            X_tr, X_val = X[train_idx], X[val_idx]
            y_tr, y_val = y[train_idx], y[val_idx]

            model = YieldPredictorModel(model_type=model_type)
            model.fit(X_tr, y_tr)
            y_val_pred = model.predict_constrained(X_val)

            r2 = float(r2_score(y_val, y_val_pred))
            mae = float(mean_absolute_error(y_val, y_val_pred))
            fold_r2_scores.append(r2)
            fold_maes.append(mae)

        return {
            "n_folds": n_splits,
            "mean_cv_r2_score": round(float(np.mean(fold_r2_scores)), 4),
            "std_cv_r2_score": round(float(np.std(fold_r2_scores)), 4),
            "mean_cv_mae": round(float(np.mean(fold_maes)), 4),
            "fold_r2_scores": [round(s, 4) for s in fold_r2_scores],
        }
