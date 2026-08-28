"""Calibration, uncertainty benchmarking, and accuracy evaluation for industrial soft sensors.

Evaluates R², RMSE, MAE, and Prediction Interval Coverage Probability (PICP) for 95% UQ intervals.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score, root_mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split

from src.sensors.telemetry import HardwareTelemetryPacket
from src.sensors.soft_sensor_engine import SoftSensorSuite


class SoftSensorCalibrator:
    """Trains, benchmarks, and calibrates uncertainty bounds for soft sensors."""

    def __init__(
        self,
        dataset_path: Optional[str] = None,
        checkpoint_path: Optional[str] = None,
        report_path: Optional[str] = None,
        random_state: int = 42,
    ) -> None:
        root_dir = Path(__file__).resolve().parent.parent.parent
        self.dataset_path = Path(dataset_path) if dataset_path else root_dir / "data" / "processed" / "synthetic_process_dataset.csv"
        self.checkpoint_path = Path(checkpoint_path) if checkpoint_path else root_dir / "models" / "checkpoints" / "soft_sensors.joblib"
        self.report_path = Path(report_path) if report_path else root_dir / "reports" / "soft_sensor_calibration_report.json"
        self.random_state = random_state

    def _extract_telemetry_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, List[str]]:
        """Construct hardware sensor telemetry feature matrix from raw process dataset."""
        n = len(df)
        t_dry_in = np.full(n, 180.0)
        t_dry_out = df["dryer_temp_c"].values
        t_reactor = df["reactor_temp_c"].values
        t_cyclone = t_reactor - 15.0
        t_cond_exit = np.full(n, 35.0)
        
        # Approximate flue gas temp from syngas yield
        t_flue = np.clip(1200.0 + 8.0 * df["syngas_yield_dry_pct"].values, 900.0, 1500.0)
        f_feed = df["feed_rate_wet_kg_h"].values
        
        # Cooling water mass flow
        f_cooling = (df["bio_oil_yield_dry_pct"].values * f_feed * 0.8) + 120.0
        f_air = f_feed * 0.8
        p_diff = 3.5 + 0.01 * f_feed

        X = np.column_stack([
            t_dry_in, t_dry_out, t_reactor, t_cyclone, t_cond_exit, t_flue,
            f_feed, f_cooling, f_air, p_diff
        ])
        return X, HardwareTelemetryPacket.FEATURE_TAGS

    def calibrate(self, test_size: float = 0.20) -> Dict[str, Any]:
        """Train soft sensor suite, calibrate UQ intervals, and compute validation metrics."""
        if not self.dataset_path.is_file():
            raise FileNotFoundError(f"Dataset not found: {self.dataset_path}")

        df = pd.read_csv(self.dataset_path)
        X_all, feature_names = self._extract_telemetry_features(df)

        # Prepare 6 target arrays
        y_targets: Dict[str, np.ndarray] = {
            "bio_oil_tan_mg_koh_g": df["bio_oil_tan_mg_koh_g"].values,
            "bio_oil_water_pct": df["bio_oil_water_pct"].values,
            "bio_oil_hhv_mj_kg": df["bio_oil_hhv_mj_kg"].values,
            "syngas_lhv_vol_mj_nm3": df["syngas_lhv_vol_mj_nm3"].values,
            "biochar_yield_dry_pct": df["biochar_yield_dry_pct"].values,
            "thermal_self_sufficiency_index_pct": df["thermal_self_sufficiency_index_pct"].values,
        }

        # Train/Test Split
        indices = np.arange(len(df))
        train_idx, test_idx = train_test_split(indices, test_size=test_size, random_state=self.random_state)

        X_train, X_test = X_all[train_idx], X_all[test_idx]
        y_train_dict = {k: v[train_idx] for k, v in y_targets.items()}
        y_test_dict = {k: v[test_idx] for k, v in y_targets.items()}

        suite = SoftSensorSuite(random_state=self.random_state)
        suite.fit(X_train, y_train_dict)

        # Evaluate performance on test set
        benchmarks: Dict[str, Any] = {}
        print("\n" + "=" * 80)
        print("          INDUSTRIAL SOFT SENSOR CALIBRATION & UQ REPORT (V0.7)")
        print("=" * 80)
        print(f"{'Tag':<22} {'Target Name':<28} {'R²':<8} {'RMSE':<9} {'MAE':<9} {'95% PICP':<9}")
        print("-" * 80)

        for tag, spec in suite.SENSOR_SPECS.items():
            target_key = spec["feature_col"]
            y_true = y_test_dict[target_key]
            
            # Test inference with uncertainty bounds
            n_test = len(X_test)
            preds = np.zeros(n_test)
            lower_ci = np.zeros(n_test)
            upper_ci = np.zeros(n_test)

            for i in range(n_test):
                est = suite.predict_single(tag, X_test[i])
                preds[i] = est.point_estimate
                lower_ci[i] = est.lower_95_ci
                upper_ci[i] = est.upper_95_ci

            r2 = float(r2_score(y_true, preds))
            rmse = float(root_mean_squared_error(y_true, preds))
            mae = float(mean_absolute_error(y_true, preds))

            # Prediction Interval Coverage Probability (PICP)
            within_ci = np.logical_and(y_true >= lower_ci, y_true <= upper_ci)
            picp_pct = float(np.mean(within_ci) * 100.0)

            benchmarks[tag] = {
                "name": spec["name"],
                "unit": spec["unit"],
                "r2_score": round(r2, 4),
                "rmse": round(rmse, 4),
                "mae": round(mae, 4),
                "prediction_interval_coverage_pct": round(picp_pct, 2),
            }

            print(f"{tag:<22} {spec['name']:<28} {r2:<8.4f} {rmse:<9.3f} {mae:<9.3f} {picp_pct:<9.1f}%")

        print("=" * 80 + "\n")

        # Save model and report
        suite.save(self.checkpoint_path)
        print(f"[OK] Soft sensor models saved to {self.checkpoint_path}")

        report_payload = {
            "metadata": {
                "total_observations": len(df),
                "train_samples": len(train_idx),
                "test_samples": len(test_idx),
                "checkpoint_path": str(self.checkpoint_path),
            },
            "sensor_benchmarks": benchmarks,
        }

        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.report_path, "w", encoding="utf-8") as f:
            json.dump(report_payload, f, indent=2)
        print(f"[OK] Calibration report saved to {self.report_path}")

        return report_payload


def main() -> None:
    calibrator = SoftSensorCalibrator()
    calibrator.calibrate()


if __name__ == "__main__":
    main()
