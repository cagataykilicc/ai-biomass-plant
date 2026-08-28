"""Multi-model benchmarking suite and leaderboard generator for biomass yield surrogates.

Trains and compares 6 model families:
- Random Forest
- Extra Trees
- Gradient Boosting
- Hist Gradient Boosting
- Multi-Layer Perceptron (Neural Network)
- Ridge Linear Baseline

Measures R², RMSE, MAE, inference latency, physics closure violation, and selects Champion Model.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

from src.ml.feature_engineering import FeatureEngineeringPipeline
from src.ml.yield_predictor import YieldPredictorModel
from src.ml.evaluator import ModelEvaluator


class MultiModelBenchmark:
    """Orchestrates comparative benchmarking across diverse ML regression architectures."""

    CANDIDATE_MODELS: List[str] = [
        "random_forest",
        "extra_trees",
        "gradient_boosting",
        "hist_gradient_boosting",
        "mlp",
        "ridge",
    ]

    def __init__(
        self,
        dataset_path: Optional[str] = None,
        output_dir: Optional[str] = None,
        random_state: int = 42,
    ) -> None:
        root_dir = Path(__file__).resolve().parent.parent.parent
        self.dataset_path = Path(dataset_path) if dataset_path else root_dir / "data" / "processed" / "synthetic_process_dataset.csv"
        self.output_dir = Path(output_dir) if output_dir else root_dir / "models" / "checkpoints"
        self.report_path = root_dir / "reports" / "ml_multimodel_benchmark.json"
        self.random_state = random_state

    def run_benchmark(self, models: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute full cross-validation, test evaluation, and latency profiling across models."""
        if not self.dataset_path.is_file():
            raise FileNotFoundError(f"Dataset not found: {self.dataset_path}")

        df = pd.read_csv(self.dataset_path)
        eval_models = models or self.CANDIDATE_MODELS
        self.output_dir.mkdir(parents=True, exist_ok=True)

        leaderboard_rows: List[Dict[str, Any]] = []
        detailed_reports: Dict[str, Any] = {}
        fitted_models: Dict[str, YieldPredictorModel] = {}

        print(f"[*] Beginning Multi-Model Benchmark across {len(eval_models)} architectures...")
        print(f"[*] Dataset: {self.dataset_path} ({len(df)} samples)")

        for model_type in eval_models:
            print(f"\n--- Benchmarking: {model_type.upper()} ---")
            scale_features = model_type in ["mlp", "ridge"]
            pipeline = FeatureEngineeringPipeline(scale_features=scale_features)
            splits = pipeline.prepare_dataset(df, test_size=0.20, random_state=self.random_state)

            # 1. 5-Fold Cross Validation
            cv_res = ModelEvaluator.cross_validate(
                X=splits.X_train,
                y=splits.y_train,
                model_type=model_type,
                n_splits=5,
                random_state=self.random_state,
            )

            # 2. Fit Full Model
            model = YieldPredictorModel(model_type=model_type, feature_pipeline=pipeline)
            model.fit(splits.X_train, splits.y_train)

            # 3. Holdout Evaluation
            y_pred_raw = model.predict_raw(splits.X_test)
            y_pred_const = model.predict_constrained(splits.X_test)
            test_res = ModelEvaluator.evaluate_test_set(
                y_true=splits.y_test,
                y_pred_raw=y_pred_raw,
                y_pred_constrained=y_pred_const,
                target_names=splits.target_names,
            )

            # 4. Latency Profiling (1000 inferences)
            t_start = time.perf_counter()
            for _ in range(5):
                _ = model.predict_constrained(splits.X_test)
            t_elapsed = time.perf_counter() - t_start
            latency_us_per_sample = float((t_elapsed / (5 * len(splits.X_test))) * 1e6)

            # 5. Checkpoint saving
            ckpt_path = self.output_dir / f"yield_predictor_{model_type}.joblib"
            model.save(ckpt_path)
            fitted_models[model_type] = model

            r2_test = test_res["aggregate_metrics"]["mean_r2_score_constrained"]
            rmse_test = test_res["aggregate_metrics"]["mean_rmse_constrained"]
            mae_test = test_res["aggregate_metrics"]["mean_mae_constrained"]
            unconst_err = test_res["physics_closure_diagnostics"]["raw_unconstrained_mean_closure_error_pct"]

            # Composite Score (higher is better)
            composite_score = float(r2_test - (0.01 * rmse_test) - (1e-5 * latency_us_per_sample))

            row = {
                "model_type": model_type,
                "cv_r2_score": cv_res["mean_cv_r2_score"],
                "test_r2_score": r2_test,
                "test_rmse_wt_pct": rmse_test,
                "test_mae_wt_pct": mae_test,
                "unconstrained_closure_error_pct": unconst_err,
                "latency_us_per_sample": round(latency_us_per_sample, 1),
                "composite_score": round(composite_score, 4),
                "checkpoint_path": str(ckpt_path),
            }
            leaderboard_rows.append(row)

            detailed_reports[model_type] = {
                "cross_validation": cv_res,
                "holdout_test": test_res,
                "latency_us_per_sample": round(latency_us_per_sample, 1),
            }

            print(f"  > Test R²: {r2_test:.4f} | Test RMSE: {rmse_test:.3f}% | Latency: {latency_us_per_sample:.1f} µs")

        # Sort Leaderboard
        leaderboard_rows.sort(key=lambda x: x["composite_score"], reverse=True)
        champion_model_type = leaderboard_rows[0]["model_type"]
        champion_model = fitted_models[champion_model_type]

        # Save Champion Checkpoint
        champ_ckpt_path = self.output_dir / "yield_predictor_champion.joblib"
        champion_model.save(champ_ckpt_path)

        final_benchmark_report = {
            "metadata": {
                "total_observations": len(df),
                "n_models_evaluated": len(eval_models),
                "champion_model": champion_model_type,
                "champion_checkpoint_path": str(champ_ckpt_path),
            },
            "leaderboard": leaderboard_rows,
            "detailed_reports": detailed_reports,
        }

        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.report_path, "w", encoding="utf-8") as f:
            json.dump(final_benchmark_report, f, indent=2)

        self._print_leaderboard(leaderboard_rows, champion_model_type)
        return final_benchmark_report

    def _print_leaderboard(self, rows: List[Dict[str, Any]], champion: str) -> None:
        """Print clean ASCII leaderboard table."""
        print("\n" + "=" * 80)
        print("          MULTI-MODEL SURROGATE BENCHMARK LEADERBOARD (V0.5)")
        print("=" * 80)
        print(f"{'Rank':<4} {'Model Family':<24} {'CV R²':<8} {'Test R²':<9} {'RMSE (%)':<10} {'MAE (%)':<9} {'Latency (µs)':<12}")
        print("-" * 80)
        for rank, r in enumerate(rows, start=1):
            is_champ = " [CHAMPION]" if r["model_type"] == champion else ""
            name = f"{r['model_type']}{is_champ}"
            print(f"{rank:<4} {name:<24} {r['cv_r2_score']:<8.4f} {r['test_r2_score']:<9.4f} {r['test_rmse_wt_pct']:<10.3f} {r['test_mae_wt_pct']:<9.3f} {r['latency_us_per_sample']:<12.1f}")
        print("=" * 80 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-Model Yield Benchmark Suite")
    parser.add_argument("--dataset", type=str, default=None, help="Dataset CSV path")
    parser.add_argument("--output-dir", type=str, default=None, help="Checkpoints directory")
    args = parser.parse_args()

    benchmark = MultiModelBenchmark(dataset_path=args.dataset, output_dir=args.output_dir)
    benchmark.run_benchmark()


if __name__ == "__main__":
    main()
