"""Unit tests for RULEstimator and fleet prognostic assessments."""

import pytest
from src.maintenance.rul_estimator import RULEstimator, FleetMaintenanceSummary, AssetRULSummary


def test_fleet_rul_assessment() -> None:
    """Verify fleet-wide RUL calculation and 95% confidence intervals."""
    fleet = RULEstimator.assess_fleet(operating_hours=4000.0)

    assert isinstance(fleet, FleetMaintenanceSummary)
    assert len(fleet.assets) == 4
    assert fleet.minimum_fleet_rul_hours > 0.0
    assert fleet.most_critical_asset_id in fleet.assets

    for a_id, a in fleet.assets.items():
        assert isinstance(a, AssetRULSummary)
        assert a.rul_95_ci_lower_hours <= a.estimated_rul_hours <= a.rul_95_ci_upper_hours
        assert a.maintenance_urgency in ["HEALTHY", "PLANNED_MAINTENANCE", "URGENT_INTERVENTION", "CRITICAL_REPLACEMENT"]


def test_rul_monotonic_decrease() -> None:
    """Verify estimated RUL decreases monotonically as operating hours advance."""
    fleet_early = RULEstimator.assess_fleet(operating_hours=1000.0)
    fleet_late = RULEstimator.assess_fleet(operating_hours=8000.0)

    assert fleet_early.minimum_fleet_rul_hours > fleet_late.minimum_fleet_rul_hours
    assert fleet_late.assets["AUGER_A101"].current_health_index_pct < fleet_early.assets["AUGER_A101"].current_health_index_pct
