"""Feature engineering, data preprocessing, and transformation pipeline for ML yield modeling.

Extracts standard features from feedstock ultimate/proximate analysis and process conditions,
handles scaling, and prepares train/test partitions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

from src.data.feedstock import BiomassFeedstock


@dataclass
class DatasetSplits:
    """Container for partitioned and scaled training/testing arrays."""
    X_train: np.ndarray
    X_test: np.ndarray
    y_train: np.ndarray
    y_test: np.ndarray
    feature_names: List[str]
    target_names: List[str]


class FeatureEngineeringPipeline:
    """Feature transformation and preprocessing pipeline for biomass conversion models."""

    FEATURE_NAMES: List[str] = [
        "carbon_pct",
        "hydrogen_pct",
        "oxygen_pct",
        "nitrogen_pct",
        "sulfur_pct",
        "ash_pct",
        "moisture_ar_pct",
        "volatile_matter_pct",
        "fixed_carbon_pct",
        "particle_size_mm",
        "bulk_density_kg_m3",
        "feedstock_hhv_dry_mj_kg",
        "reactor_temp_c",
        "heating_rate_c_min",
        "residence_time_min",
        "feed_rate_wet_kg_h",
    ]

    TARGET_NAMES: List[str] = [
        "biochar_yield_dry_pct",
        "bio_oil_yield_dry_pct",
        "syngas_yield_dry_pct",
    ]

    def __init__(self, scale_features: bool = False) -> None:
        self.scale_features = scale_features
        self.scaler: Optional[StandardScaler] = StandardScaler() if scale_features else None
        self.is_fitted: bool = False

    def extract_features_single(
        self,
        feedstock: BiomassFeedstock,
        reactor_temp_c: float,
        heating_rate_c_min: float,
        residence_time_min: float,
        feed_rate_wet_kg_h: float = 100.0,
    ) -> np.ndarray:
        """Extract 1D feature vector for a single operating point.

        Returns:
            2D numpy array with shape (1, n_features).
        """
        row = [
            float(feedstock.ultimate.carbon),
            float(feedstock.ultimate.hydrogen),
            float(feedstock.ultimate.oxygen),
            float(feedstock.ultimate.nitrogen),
            float(feedstock.ultimate.sulfur),
            float(feedstock.ultimate.ash),
            float(feedstock.proximate.moisture),
            float(feedstock.proximate.volatile_matter),
            float(feedstock.proximate.fixed_carbon),
            float(feedstock.physical.particle_size_mm),
            float(feedstock.physical.bulk_density_kg_m3),
            float(feedstock.calculate_hhv_dry()),
            float(reactor_temp_c),
            float(heating_rate_c_min),
            float(residence_time_min),
            float(feed_rate_wet_kg_h),
        ]
        X = np.array([row], dtype=np.float64)
        if self.scale_features and self.is_fitted and self.scaler is not None:
            return self.scaler.transform(X)
        return X

    def prepare_dataset(
        self,
        df: pd.DataFrame,
        test_size: float = 0.20,
        random_state: int = 42,
    ) -> DatasetSplits:
        """Extract features and targets from DataFrame, partition, and optionally scale."""
        # Verify required columns
        for feat in self.FEATURE_NAMES:
            if feat not in df.columns:
                raise KeyError(f"Required feature '{feat}' missing from input DataFrame.")
        for tgt in self.TARGET_NAMES:
            if tgt not in df.columns:
                raise KeyError(f"Required target '{tgt}' missing from input DataFrame.")

        X = df[self.FEATURE_NAMES].values.astype(np.float64)
        y = df[self.TARGET_NAMES].values.astype(np.float64)

        strat_col = df["feedstock_category"] if "feedstock_category" in df.columns else None

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=random_state,
            stratify=strat_col,
        )

        if self.scale_features and self.scaler is not None:
            X_train = self.scaler.fit_transform(X_train)
            X_test = self.scaler.transform(X_test)
            self.is_fitted = True

        return DatasetSplits(
            X_train=X_train,
            X_test=X_test,
            y_train=y_train,
            y_test=y_test,
            feature_names=self.FEATURE_NAMES,
            target_names=self.TARGET_NAMES,
        )
