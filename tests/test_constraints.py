"""Unit tests for PhysicsConstraintProjector."""

import pytest
import numpy as np
from src.ml.constraints import PhysicsConstraintProjector


def test_simplex_projection_1d() -> None:
    """Verify single 1D yield vector projection enforces exactly 100.00% sum and non-negativity."""
    unconstrained = np.array([28.4, 52.1, 23.5])  # sum = 104.0%
    projected = PhysicsConstraintProjector.project_yields(unconstrained)

    assert pytest.approx(np.sum(projected), rel=1e-5) == 100.0
    assert np.all(projected >= 0.0)
    assert projected.shape == (3,)


def test_simplex_projection_batch_with_negative_values() -> None:
    """Verify batch 2D yield projection clips negative predictions and conserves mass."""
    raw_batch = np.array([
        [-5.0, 60.0, 45.0],    # Contains negative value
        [30.0, 50.0, 20.0],    # Exact 100%
        [40.0, 40.0, 40.0],    # 120% sum
        [0.0, 0.0, 0.0],       # Degenerate zero
    ])

    proj_batch = PhysicsConstraintProjector.project_yields(raw_batch)

    assert proj_batch.shape == (4, 3)
    row_sums = np.sum(proj_batch, axis=1)
    for s in row_sums:
        assert pytest.approx(s, rel=1e-5) == 100.0
    assert np.all(proj_batch >= 0.0)


def test_closure_violation_computation() -> None:
    """Verify calculation of raw unconstrained mass closure error."""
    raw = np.array([
        [30.0, 50.0, 20.0],  # Error = 0.0
        [35.0, 50.0, 20.0],  # Error = 5.0
        [25.0, 45.0, 20.0],  # Error = 10.0
    ])
    violations = PhysicsConstraintProjector.compute_closure_violation(raw)
    assert pytest.approx(violations[0], abs=1e-5) == 0.0
    assert pytest.approx(violations[1], abs=1e-5) == 5.0
    assert pytest.approx(violations[2], abs=1e-5) == 10.0
