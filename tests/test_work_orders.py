"""Unit tests for WorkOrderManager and prescriptive maintenance planning."""

import pytest
from src.maintenance.rul_estimator import RULEstimator
from src.maintenance.work_order_manager import WorkOrderManager, WorkOrder, MaintenanceUrgency


def test_work_order_generation_at_high_hours() -> None:
    """Verify prescriptive work orders with spare parts BOM and safety LOTO are generated."""
    # At 7500 operating hours, critical components require maintenance
    fleet = RULEstimator.assess_fleet(operating_hours=7500.0)
    work_orders = WorkOrderManager.generate_work_orders(fleet)

    assert len(work_orders) >= 1
    wo = work_orders[0]
    assert isinstance(wo, WorkOrder)
    assert wo.urgency in [MaintenanceUrgency.PLANNED_MAINTENANCE, MaintenanceUrgency.URGENT_INTERVENTION, MaintenanceUrgency.CRITICAL_REPLACEMENT]
    assert len(wo.required_spare_parts) >= 1
    assert wo.total_parts_cost_usd > 0.0
    assert "LOTO" in wo.safety_loto_protocol
    assert len(wo.scope_of_work) > 10
