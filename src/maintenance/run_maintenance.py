"""CLI interface and fleet prognostics dashboard for predictive maintenance (PdM).

Usage:
    python -m src.maintenance.run_maintenance --operating-hours 4500
    python -m src.maintenance.run_maintenance --operating-hours 8200
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

from src.maintenance.rul_estimator import RULEstimator, FleetMaintenanceSummary, AssetRULSummary
from src.maintenance.work_order_manager import WorkOrderManager, WorkOrder


def print_maintenance_dashboard(
    fleet: FleetMaintenanceSummary,
    work_orders: List[WorkOrder],
) -> None:
    """Print ANSI formatted predictive maintenance and RUL dashboard to stdout."""
    w = 78
    border = "=" * w
    sub_border = "-" * w

    print(f"\n{border}")
    print(f"       AI-INTEGRATED BIOMASS CONVERSION PLANT - V0.9")
    print(f" (Predictive Maintenance, 95% RUL Prognostics & Work Order Dispatch)")
    print(f"{border}")
    print(f"Cumulative Operating Time: {fleet.current_operating_hours:,.1f} Hours")
    print(f"Plant Bottleneck Asset   : {fleet.most_critical_asset_id} (RUL: {fleet.minimum_fleet_rul_hours:,.1f} h)")

    print(f"\nFLEET ASSET HEALTH & REMAINING USEFUL LIFE (RUL) PROGNOSTICS")
    print(f"{sub_border}")
    print(f"{'Asset ID':<20} {'Health':<8} {'Wear State':<20} {'Est RUL':<12} {'95% Conf Interval':<18}")
    print(f"{sub_border}")

    for asset_id, a in fleet.assets.items():
        deg = a.degradation_state
        wear_str = f"{deg.current_wear_value:.2f} / {deg.wear_threshold_eol:.1f} {deg.unit}"
        rul_str = f"{a.estimated_rul_hours:,.0f} h"
        ci_str = f"[{a.rul_95_ci_lower_hours:,.0f} - {a.rul_95_ci_upper_hours:,.0f}] h"
        print(f"{asset_id:<20} {a.current_health_index_pct:5.1f}%  {wear_str:<20} {rul_str:<12} {ci_str:<18}")

    print(f"\nPRESCRIPTIVE WORK ORDERS & TURNAROUND DISPATCH")
    print(f"{sub_border}")
    if not work_orders:
        print("  [*] All plant assets operating in HEALTHY nominal window. No active work orders.")
    else:
        for idx, wo in enumerate(work_orders, start=1):
            print(f"\n[{idx}] Work Order: {wo.work_order_id} -> [{wo.urgency.value}]")
            print(f"    Asset Target        : {wo.asset_name} ({wo.asset_id})")
            print(f"    Current Health      : {wo.health_index_pct:.1f}% | Est Remaining Life: {wo.estimated_rul_hours:,.0f} h")
            print(f"    Scope of Work       : {wo.scope_of_work}")
            print(f"    Est Labor & Parts   : {wo.estimated_labor_hours:.0f} Technician Hours | ${wo.total_parts_cost_usd:,.2f} Parts BOM")
            print(f"    Required Spare Parts: " + ", ".join([f"{p['part_no']} (x{p['qty']})" for p in wo.required_spare_parts]))
            print(f"    Safety LOTO Protocol: {wo.safety_loto_protocol}")

    print(f"\n{border}\n")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Plant Predictive Maintenance and RUL Dashboard (V0.9)")
    parser.add_argument("--operating-hours", type=float, default=4500.0, help="Current cumulative plant operating hours")
    parser.add_argument("--feed-rate", type=float, default=100.0, help="Average biomass feed rate (kg/h)")
    parser.add_argument("--temp", type=float, default=500.0, help="Average reactor temperature (°C)")
    parser.add_argument("--output", type=str, default=None, help="Output JSON report path")
    args = parser.parse_args()

    fleet = RULEstimator.assess_fleet(
        operating_hours=args.operating_hours,
        feed_rate_kg_h=args.feed_rate,
        reactor_temp_c=args.temp,
    )
    work_orders = WorkOrderManager.generate_work_orders(fleet)

    print_maintenance_dashboard(fleet, work_orders)

    report_payload = {
        "fleet_summary": fleet.to_dict(),
        "active_work_orders": [wo.to_dict() for wo in work_orders],
    }

    out_file = (
        Path(args.output)
        if args.output
        else Path(__file__).resolve().parent.parent.parent / "reports" / "predictive_maintenance_report.json"
    )
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report_payload, f, indent=2)
    print(f"[OK] Predictive maintenance report written to {out_file}")


if __name__ == "__main__":
    main()
