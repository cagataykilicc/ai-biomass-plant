"""Feature importance, sensitivity analysis, and scientific model explainability.

Extracts MDI (Gini) and Permutation Feature Importance to explain chemical and operational
drivers of product yields in biomass conversion.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance

from src.ml.feature_engineering import FeatureEngineeringPipeline
from src.ml.yield_predictor import YieldPredictorModel


class FeatureImportanceAnalyzer:
    """Computes and analyzes feature importances for biomass conversion ML surrogates."""

    def __init__(
        self,
        model: Optional[YieldPredictorModel] = None,
        dataset_path: Optional[str] = None,
    ) -> None:
        root_dir = Path(__file__).resolve().parent.parent.parent
        self.dataset_path = Path(dataset_path) if dataset_path else root_dir / "data" / "processed" / "synthetic_process_dataset.csv"
        self.report_path = root_dir / "reports" / "feature_importance.json"

        if model is None:
            champ_ckpt = root_dir / "models" / "checkpoints" / "yield_predictor_champion.joblib"
            if not champ_ckpt.is_file():
                champ_ckpt = root_dir / "models" / "checkpoints" / "yield_predictor_rf.joblib"
            self.model = YieldPredictorModel.load(champ_ckpt)
        else:
            self.model = model

    def analyze(self, n_repeats: int = 10, random_state: int = 42) -> Dict[str, Any]:
        """Compute MDI and Permutation Importance across all features and targets."""
        if not self.dataset_path.is_file():
            raise FileNotFoundError(f"Dataset not found: {self.dataset_path}")

        df = pd.read_csv(self.dataset_path)
        pipeline = FeatureEngineeringPipeline(scale_features=self.model.feature_pipeline.scale_features)
        splits = pipeline.prepare_dataset(df, test_size=0.20, random_state=random_state)

        feature_names = splits.feature_names
        target_names = splits.target_names

        # 1. Model-Agnostic Permutation Importance on Test Set
        perm_res = permutation_importance(
            self.model.estimator,
            splits.X_test,
            splits.y_test,
            n_repeats=n_repeats,
            random_state=random_state,
            scoring="r2",
        )

        perm_importances: Dict[str, Dict[str, float]] = {}
        for idx, feat in enumerate(feature_names):
            perm_importances[feat] = {
                "mean_importance": round(float(perm_res.importances_mean[idx]), 4),
                "std_importance": round(float(perm_res.importances_std[idx]), 4),
            }

        # Sort features by permutation importance
        sorted_perm = sorted(
            perm_importances.items(),
            key=lambda x: x[1]["mean_importance"],
            reverse=True,
        )

        # 2. Tree MDI Feature Importance (if supported)
        tree_importances: Optional[Dict[str, float]] = None
        if hasattr(self.model.estimator, "feature_importances_"):
            mdi_raw = self.model.estimator.feature_importances_
            tree_importances = {
                feat: round(float(mdi_raw[idx]), 4) for idx, feat in enumerate(feature_names)
            }

        # 3. Chemical Domain Interpretation
        top_drivers = [item[0] for item in sorted_perm[:5]]
        domain_insights = {
            "primary_process_driver": top_drivers[0] if top_drivers else "reactor_temp_c",
            "top_5_influential_features": top_drivers,
            "chemical_interpretation": (
                "Reactor temperature (reactor_temp_c) dominates thermal devolatilization and cracking. "
                "Feedstock proximate composition (volatile_matter_pct, ash_pct, fixed_carbon_pct) and "
                "organic carbon content (carbon_pct) control primary phase partitioning and energy recovery."
            ),
        }

        report = {
            "metadata": {
                "model_type": self.model.model_type,
                "n_test_samples": int(splits.X_test.shape[0]),
                "n_repeats": n_repeats,
            },
            "domain_insights": domain_insights,
            "permutation_importance_ranked": [
                {"feature": feat, "mean_importance": d["mean_importance"], "std": d["std_importance"]}
                for feat, d in sorted_perm
            ],
            "tree_mdi_importance": tree_importances,
        }

        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        self._print_importance_table(sorted_perm, self.model.model_type)
        return report

    def _print_importance_table(self, sorted_perm: List[Any], model_type: str) -> None:
        """Print clean ASCII feature importance ranking."""
        print("\n" + "=" * 65)
        print(f"   FEATURE IMPORTANCE & EXPLAINABILITY REPORT ({model_type.upper()})")
        print("=" * 65)
        print(f"{'Rank':<5} {'Feature Name':<28} {'Mean Drop in R²':<18} {'Std':<8}")
        print("-" * 65)
        for rank, (feat, data) in enumerate(sorted_perm, start=1):
            print(f"{rank:<5} {feat:<28} {data['mean_importance']:<18.4f} {data['std_importance']:<8.4f}")
        print("=" * 65 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Feature Importance & Explainability Engine")
    parser.add_argument("--dataset", type=str, default=None, help="Dataset CSV path")
    args = parser.parse_args()

    analyzer = FeatureImportanceAnalyzer(dataset_path=args.dataset)
    analyzer.analyze()


if __name__ == "__main__":
    main()
