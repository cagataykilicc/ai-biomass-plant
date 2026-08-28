"""Unit tests for experimental literature dataset loader."""

import pytest
import pandas as pd
from src.data.literature_loader import LiteratureDatasetLoader


def test_literature_dataset_loading() -> None:
    """Verify literature dataset loads with all required scientific fields."""
    loader = LiteratureDatasetLoader()
    df = loader.load_as_dataframe()

    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 10
    assert "doi" in df.columns
    assert "citation" in df.columns
    assert "bio_oil_yield_dry_pct" in df.columns

    # Verify all records are non-synthetic
    assert (df["is_synthetic"] == False).all()


def test_literature_summary_statistics() -> None:
    """Verify summary metrics calculation across literature records."""
    loader = LiteratureDatasetLoader()
    stats = loader.get_summary_statistics()

    assert stats["total_literature_records"] >= 10
    assert stats["unique_feedstocks"] >= 5
    assert len(stats["citations"]) >= 4
    assert stats["temperature_range_c"][0] >= 350.0
    assert stats["temperature_range_c"][1] <= 700.0
