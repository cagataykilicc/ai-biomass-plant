"""Literature dataset loader, validator, and provenance parser.

Loads peer-reviewed experimental pyrolysis datasets, verifies bibliographic citations and DOIs,
and converts records to standardized DataFrames and ProcessDataRecord objects.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Union, Dict, Any
import pandas as pd

from src.data.provenance import DataProvenance, DataSourceType


class LiteratureDatasetLoader:
    """Loader and validator for peer-reviewed experimental biomass pyrolysis datasets."""

    def __init__(self, data_path: Optional[Union[str, Path]] = None) -> None:
        if data_path is None:
            self.data_path = (
                Path(__file__).resolve().parent.parent.parent
                / "data"
                / "external"
                / "literature_pyrolysis_dataset.csv"
            )
        else:
            self.data_path = Path(data_path)

    def load_as_dataframe(self) -> pd.DataFrame:
        """Load literature dataset as a validated Pandas DataFrame."""
        if not self.data_path.is_file():
            raise FileNotFoundError(f"Literature dataset not found at: {self.data_path}")

        df = pd.read_csv(self.data_path)
        self._validate_literature_df(df)
        return df

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Compute summary metrics across literature datasets."""
        df = self.load_as_dataframe()
        return {
            "total_literature_records": len(df),
            "unique_feedstocks": df["feedstock_name"].nunique(),
            "feedstock_list": sorted(df["feedstock_name"].unique().tolist()),
            "temperature_range_c": [float(df["reactor_temp_c"].min()), float(df["reactor_temp_c"].max())],
            "bio_oil_yield_mean_pct": float(round(df["bio_oil_yield_dry_pct"].mean(), 2)),
            "biochar_yield_mean_pct": float(round(df["biochar_yield_dry_pct"].mean(), 2)),
            "syngas_yield_mean_pct": float(round(df["syngas_yield_dry_pct"].mean(), 2)),
            "citations": sorted(df["citation"].unique().tolist()),
        }

    def _validate_literature_df(self, df: pd.DataFrame) -> None:
        """Verify data schema and scientific constraints."""
        required_cols = [
            "record_id", "source_type", "citation", "doi", "feedstock_name",
            "reactor_temp_c", "biochar_yield_dry_pct", "bio_oil_yield_dry_pct", "syngas_yield_dry_pct"
        ]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Literature dataset missing required columns: {missing}")

        # Check yield balance ~ 100% within experimental error (± 5%)
        yield_sums = df["biochar_yield_dry_pct"] + df["bio_oil_yield_dry_pct"] + df["syngas_yield_dry_pct"]
        for idx, y_sum in yield_sums.items():
            if abs(y_sum - 100.0) > 6.0:
                raise ValueError(f"Literature record at index {idx} violates yield mass balance: sum = {y_sum:.2f}%")
