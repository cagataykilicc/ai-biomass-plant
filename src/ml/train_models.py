"""Model training and evaluation pipeline for ML biomass yield surrogates.

Usage:
    python -m src.ml.train_models
    python -m src.ml.train_models --model extra_trees --dataset data/processed/synthetic_process_dataset.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd

from src.ml.feature_engineering import FeatureEngineeringPipeline
from src.ml.yield_predictor import YieldPredictorModel
from src.ml.evaluator import ModelEvaluator


def run_training_pipeline(
    dataset_path: Optional[str] = None,
    model_type: str = "random_forest",
    output_model_path: Optional[str] = None,
    report_output_path: Optional[str] = None,
    test_size: float = 0.20,
    random_state: int = 42,
) -> Dict[str, Any]:
    """Execute complete model training, CV benchmarking, and artifact serialization."""
    root_dir = Path(__file__).resolve().parent.parent.parent
    ds_file = Path(dataset_path) if dataset_path else root_dir / "data" / "processed" / "synthetic_process_dataset.csv"
    mod_file = Path(output_model_path) if output_model_path else root_dir / "models" / "checkpoints" / "yield_predictor_rf.joblib"
    rep_file = Path(report_output_path) if report_output_path else root_dir / "reports" / "ml_yield_benchmark_report.json"

    if not ds_file.is_file():
        raise FileNotFoundError(f"Training dataset not found: {ds_file}. Run synthetic generator first.")

    print(f"[*] Loading training dataset from: {ds_file}")
    df = pd.read_csv(ds_file)
    print(f"[*] Total dataset records: {len(df)}")

    # 1. Feature Engineering & Dataset Splitting
    pipeline = FeatureEngineeringPipeline(scale_features=False)
    splits = pipeline.prepare_dataset(df, test_size=test_size, random_state=random_state)
    print(f"[*] Train set: {splits.X_train.shape[0]} samples | Test set: {splits.X_test.shape[0]} samples")

    # 2. 5-Fold Cross Validation
    print(f"[*] Running 5-fold cross-validation for {model_type}...")
    cv_results = ModelEvaluator.cross_validate(
        X=splits.X_train,
        y=splits.y_train,
        model_type=model_type,
        n_splits=5,
        random_state=random_state,
    )
    print(f"[*] Cross-Validation Mean R²: {cv_results['mean_cv_r2_score']:.4f} (± {cv_results['std_cv_r2_score']:.4f})")

    # 3. Model Fitting on Complete Training Split
    print(f"[*] Training full {model_type} model...")
    model = YieldPredictorModel(model_type=model_type, feature_pipeline=pipeline)
    model.fit(splits.X_train, splits.y_train)

    # 4. Evaluation on Holdout Test Set
    print("[*] Evaluating on holdout test set...")
    y_test_pred_raw = model.predict_raw(splits.X_test)
    y_test_pred_const = model.predict_constrained(splits.X_test)

    eval_results = ModelEvaluator.evaluate_test_set(
        y_true=splits.y_test,
        y_pred_raw=y_test_pred_raw,
        y_pred_constrained=y_test_pred_const,
        target_names=splits.target_names,
    )

    # 5. Save Model Checkpoint
    saved_model_path = model.save(mod_file)
    print(f"[OK] Model checkpoint saved -> {saved_model_path}")

    # 6. Save Benchmark Report
    benchmark_report = {
        "metadata": {
            "model_type": model_type,
            "training_samples": int(splits.X_train.shape[0]),
            "test_samples": int(splits.X_test.shape[0]),
            "n_features": len(splits.feature_names),
            "features": splits.feature_names,
            "targets": splits.target_names,
            "model_checkpoint_path": str(saved_model_path),
        },
        "cross_validation_results": cv_results,
        "holdout_test_evaluation": eval_results,
    }

    rep_file.parent.mkdir(parents=True, exist_ok=True)
    with open(rep_file, "w", encoding="utf-8") as f:
        json.dump(benchmark_report, f, indent=2)
    print(f"[OK] Benchmark evaluation report saved -> {rep_file}")

    print("\n" + "=" * 60)
    print("      ML YIELD SURROGATE MODEL BENCHMARK RESULTS")
    print("=" * 60)
    print(f"Mean Test R² Score        : {eval_results['aggregate_metrics']['mean_r2_score_constrained']:.4f}")
    print(f"Mean Test RMSE (wt%)      : {eval_results['aggregate_metrics']['mean_rmse_constrained']:.4f} %")
    print(f"Mean Test MAE (wt%)       : {eval_results['aggregate_metrics']['mean_mae_constrained']:.4f} %")
    print(f"Unconstrained Closure Err : {eval_results['physics_closure_diagnostics']['raw_unconstrained_mean_closure_error_pct']:.3f} % (Max: {eval_results['physics_closure_diagnostics']['raw_unconstrained_max_closure_error_pct']:.3f} %)")
    print(f"Constrained Closure Err   : {eval_results['physics_closure_diagnostics']['constrained_mean_closure_error_pct']:.6f} % (Max: {eval_results['physics_closure_diagnostics']['constrained_max_closure_error_pct']:.6f} %)")
    print(f"Physics Mass Conservation : {'GUARANTEED (100.00% Exact)' if eval_results['physics_closure_diagnostics']['mass_conservation_guaranteed'] else 'FAILED'}")
    print("=" * 60 + "\n")

    return benchmark_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Train ML Yield Surrogate Model")
    parser.add_argument("--model", type=str, default="random_forest", choices=["random_forest", "extra_trees", "gradient_boosting"])
    parser.add_argument("--dataset", type=str, default=None, help="Path to CSV dataset")
    parser.add_argument("--output-model", type=str, default=None, help="Path for saved model checkpoint")
    parser.add_argument("--report", type=str, default=None, help="Path for benchmark report JSON")
    args = parser.parse_args()

    run_training_pipeline(
        dataset_path=args.dataset,
        model_type=args.model,
        output_model_path=args.output_model,
        report_output_path=args.report,
    )


if __name__ == "__main__":
    main()
