"""Physics-informed mass conservation and constraint projection layer for ML predictions.

Enforces First-Law thermodynamic mass balance conservation on ML predicted product yields:
1. Non-negativity: y_i >= 0
2. Exact Closure: sum(y_i) == 100.00%
"""

from __future__ import annotations

from typing import Union, Tuple
import numpy as np


class PhysicsConstraintProjector:
    """Projects unconstrained ML yield regressions onto the physical simplex (mass conservation)."""

    DEFAULT_FALLBACK_YIELDS = np.array([30.0, 50.0, 20.0], dtype=np.float64)

    @classmethod
    def project_yields(cls, raw_yields: np.ndarray) -> np.ndarray:
        """Project raw model predictions to strictly satisfy 100.00% mass conservation.

        Args:
            raw_yields: 1D array of shape (3,) or 2D array of shape (N, 3).
                Expected order: [biochar_yield_dry_pct, bio_oil_yield_dry_pct, syngas_yield_dry_pct].

        Returns:
            Projected numpy array of identical shape where every row sums to 100.00% and elements >= 0.
        """
        arr = np.asarray(raw_yields, dtype=np.float64)
        is_1d = arr.ndim == 1

        if is_1d:
            arr = arr.reshape(1, -1)

        if arr.shape[1] != 3:
            raise ValueError(f"Expected 3 target yield columns (char, oil, gas). Got shape: {arr.shape}")

        # 1. Non-negativity rectification
        clipped = np.clip(arr, a_min=0.0, a_max=100.0)

        # 2. Row-wise sum calculation
        row_sums = np.sum(clipped, axis=1, keepdims=True)

        # 3. Simplex projection (normalization to 100%)
        # Guard against degenerate zero rows
        zero_mask = (row_sums.squeeze(axis=1) <= 1e-6)
        
        projected = np.empty_like(clipped)
        safe_sums = np.where(row_sums == 0, 1.0, row_sums)
        projected = (clipped / safe_sums) * 100.0

        if np.any(zero_mask):
            projected[zero_mask] = cls.DEFAULT_FALLBACK_YIELDS

        if is_1d:
            return projected.flatten()
        return projected

    @classmethod
    def compute_closure_violation(cls, raw_yields: np.ndarray) -> np.ndarray:
        """Compute absolute closure error in percentage points: |sum(y_i) - 100.0|."""
        arr = np.asarray(raw_yields, dtype=np.float64)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        row_sums = np.sum(arr, axis=1)
        return np.abs(row_sums - 100.0)
