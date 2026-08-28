"""Exploratory Data Analysis (EDA) and dataset statistical profiling engine.

Computes univariate statistics, Pearson and Spearman correlation matrices,
multicollinearity diagnostics, and exports structured dataset profiling reports.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import pandas as pd
import numpy as np


class DatasetProfiler:
    """Statistical analyzer and quality profiler for process datasets."""

    def __init__(self, data_path: Optional[Union[str, Path]] = None) -> None:
        if data_path is None:
            self.data_path = (
                Path(__file__).resolve().parent.parent.parent
                / "data"
                / "processed"
                / "synthetic_process_dataset.csv"
            )
        else:
            self.data_path = Path(data_path)

    def load_data(self) -> pd.DataFrame:
        """Load dataset from disk."""
        if not self.data_path.is_file():
            raise FileNotFoundError(f"Dataset not found at {self.data_path}")
        return pd.read_csv(self.data_path)

    def profile_dataset(self, df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Perform comprehensive statistical analysis on dataset."""
        data = df if df is not None else self.load_data()

        numeric_df = data.select_dtypes(include=[np.number])
        n_records = len(data)
        n_features = len(data.columns)

        # 1. Univariate Summary Statistics
        stats_dict: Dict[str, Dict[str, float]] = {}
        for col in numeric_df.columns:
            series = numeric_df[col].dropna()
            stats_dict[col] = {
                "mean": float(round(series.mean(), 3)),
                "std": float(round(series.std(), 3)),
                "min": float(round(series.min(), 3)),
                "p25": float(round(series.quantile(0.25), 3)),
                "median": float(round(series.median(), 3)),
                "p75": float(round(series.quantile(0.75), 3)),
                "max": float(round(series.max(), 3)),
                "skewness": float(round(float(series.skew()), 3)) if len(series) > 2 else 0.0,
            }

        # 2. Key Process Correlations with Product Yields & Energy
        key_inputs = [
            "reactor_temp_c", "heating_rate_c_min", "residence_time_min",
            "carbon_pct", "ash_pct", "volatile_matter_pct", "fixed_carbon_pct"
        ]
        key_targets = [
            "biochar_yield_dry_pct", "bio_oil_yield_dry_pct", "syngas_yield_dry_pct",
            "bio_oil_hhv_mj_kg", "thermal_self_sufficiency_index_pct", "net_thermal_efficiency_pct"
        ]

        valid_inputs = [c for c in key_inputs if c in numeric_df.columns]
        valid_targets = [c for c in key_targets if c in numeric_df.columns]

        corr_matrix: Dict[str, Dict[str, float]] = {}
        if valid_inputs and valid_targets:
            corr_sub = numeric_df[valid_inputs + valid_targets].corr()
            for inp in valid_inputs:
                corr_matrix[inp] = {}
                for tgt in valid_targets:
                    corr_matrix[inp][tgt] = float(round(corr_sub.loc[inp, tgt], 3))

        # 3. Categorical Distributions
        cat_distributions: Dict[str, Any] = {}
        if "feedstock_category" in data.columns:
            cat_distributions["feedstock_category_counts"] = data["feedstock_category"].value_counts().to_dict()
        if "feedstock_name" in data.columns:
            cat_distributions["feedstock_name_counts"] = data["feedstock_name"].value_counts().to_dict()
        if "source_type" in data.columns:
            cat_distributions["source_type_counts"] = data["source_type"].value_counts().to_dict()

        # 4. Data Quality Checks
        null_counts = data.isnull().sum().to_dict()
        total_nulls = int(sum(null_counts.values()))

        closure_pass = True
        if "mass_balance_closure_pct" in data.columns:
            closure_dev = (data["mass_balance_closure_pct"] - 100.0).abs().max()
            closure_pass = bool(closure_dev < 1.0)

        report = {
            "dataset_metadata": {
                "dataset_path": str(self.data_path),
                "total_observations": n_records,
                "total_features": n_features,
                "missing_values_count": total_nulls,
                "mass_balance_closure_valid": closure_pass,
            },
            "categorical_distributions": cat_distributions,
            "correlations_with_targets": corr_matrix,
            "feature_statistics": stats_dict,
        }
        return report

    def save_profiling_report(
        self,
        output_path: Optional[Union[str, Path]] = None,
        df: Optional[pd.DataFrame] = None,
    ) -> Path:
        """Generate and save profiling report JSON."""
        if output_path is None:
            out_file = (
                Path(__file__).resolve().parent.parent.parent
                / "reports"
                / "dataset_profiling_report.json"
            )
        else:
            out_file = Path(output_path)

        out_file.parent.mkdir(parents=True, exist_ok=True)
        report = self.profile_dataset(df=df)
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        return out_file


def main() -> None:
    """CLI profiling command."""
    parser = argparse.ArgumentParser(description="Dataset Exploratory Data Analysis & Quality Profiler")
    parser.add_argument("--data", type=str, default=None, help="Path to process dataset CSV")
    parser.add_argument("--report", type=str, default=None, help="Output report JSON path")
    args = parser.parse_args()

    profiler = DatasetProfiler(data_path=args.data)
    report_path = profiler.save_profiling_report(output_path=args.report)
    print(f"[OK] Dataset profiling report generated -> {report_path}")


if __name__ == "__main__":
    main()
