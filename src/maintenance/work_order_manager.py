"""Prescriptive maintenance turnaround planning and automated work order generation.

Creates formal industrial work orders (WO) with spare parts BOM, estimated labor hours,
and Safety Lockout / Tagout (LOTO) isolation protocols.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, Any, List, Optional

from src.maintenance.rul_estimator import AssetRULSummary, FleetMaintenanceSummary


class MaintenanceUrgency(str, Enum):
    """Maintenance dispatch urgency levels."""
    HEALTHY = "HEALTHY"
    PLANNED_MAINTENANCE = "PLANNED_MAINTENANCE"
    URGENT_INTERVENTION = "URGENT_INTERVENTION"
    CRITICAL_REPLACEMENT = "CRITICAL_REPLACEMENT"


@dataclass
class WorkOrder:
    """Industrial work order specification for plant maintenance crews."""
    work_order_id: str
    asset_id: str
    asset_name: str
    urgency: MaintenanceUrgency
    target_operating_hours: float
    health_index_pct: float
    estimated_rul_hours: float
    estimated_labor_hours: float
    required_spare_parts: List[Dict[str, Any]]
    total_parts_cost_usd: float
    safety_loto_protocol: str
    scope_of_work: str

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["urgency"] = self.urgency.value
        return d


class WorkOrderManager:
    """Generates prescriptive maintenance work orders based on fleet RUL assessments."""

    JOB_TEMPLATES: Dict[str, Dict[str, Any]] = {
        "AUGER_A101": {
            "labor_hours": 12.0,
            "parts": [
                {"part_no": "A101-FLT-HARDOX", "description": "Hardox 500 Replacement Auger Flight Segment", "qty": 4, "unit_cost_usd": 450.0},
                {"part_no": "BRG-22218-E", "description": "Spherical Roller Drive Bearing", "qty": 2, "unit_cost_usd": 280.0},
                {"part_no": "SL-VITON-100", "description": "High-Temp Viton Shaft Seal Kit", "qty": 2, "unit_cost_usd": 95.0},
            ],
            "loto": "LOTO Procedure E-04: Lockout main 480V motor drive breaker; depressurize biomass feed hopper; verify zero mechanical motion.",
            "scope": "Decouple drive gearbox; extract auger shaft; gauge flight wear; weld replacement Hardox flight segments; repack bearings and seals.",
        },
        "REACTOR_R101_LINER": {
            "labor_hours": 36.0,
            "parts": [
                {"part_no": "REF-CAST-1600", "description": "High-Alumina Low-Cement Castable Refractory (25kg bag)", "qty": 18, "unit_cost_usd": 85.0},
                {"part_no": "ANC-SS310-V", "description": "Stainless 310 V-Anchor Fastener Kit", "qty": 50, "unit_cost_usd": 12.0},
                {"part_no": "GSK-GRAF-R101", "description": "Expanded Graphite Main Flange Gasket Set", "qty": 1, "unit_cost_usd": 620.0},
            ],
            "loto": "LOTO Procedure P-01: Isolate combustor syngas feed; continuous N2 purge until combustible gas < 1.0%; verify vessel temp < 40°C.",
            "scope": "Open reactor main manway; chisel out spalled refractory; weld new 310 anchors; gunite castable refractory; execute 24h dry-out cure.",
        },
        "FILTER_F101": {
            "labor_hours": 8.0,
            "parts": [
                {"part_no": "FIL-CER-DIA50", "description": "Silicon Carbide Porous Ceramic Filter Candles (1.5m)", "qty": 12, "unit_cost_usd": 320.0},
                {"part_no": "GSK-MICA-F101", "description": "Mica/Ceramic High-Temperature Tube Sheet Gasket", "qty": 12, "unit_cost_usd": 45.0},
            ],
            "loto": "LOTO Procedure F-02: Isolate hot syngas line; lock pulse-jet accumulator valves; verify depressurization to 0.0 kPa.",
            "scope": "Remove filter vessel top cover; unscrew blinded SiC candles; vacuum vessel hopper; install new candles with fresh mica gaskets; leak test at 50 kPa.",
        },
        "CONDENSER_HX102": {
            "labor_hours": 16.0,
            "parts": [
                {"part_no": "TUBE-316L-19MM", "description": "SS316L Seamless Condenser Tubes (19mm OD x 2.5m)", "qty": 24, "unit_cost_usd": 110.0},
                {"part_no": "SOLV-TERP-200L", "description": "Industrial Terpene Bio-Oil Degreasing Solvent Drum", "qty": 2, "unit_cost_usd": 380.0},
                {"part_no": "GSK-PTFE-HX102", "description": "PTFE Envelope Channel Cover Gasket", "qty": 2, "unit_cost_usd": 210.0},
            ],
            "loto": "LOTO Procedure C-03: Drain and lock cooling water lines; isolate bio-oil collection lines; lock nitrogen purge manifold.",
            "scope": "Unbolt channel head covers; circulate terpene solvent wash; ultrasonic thickness testing on tube bundle; plug/roll corroded tubes; hydrostatic test to 6 bar.",
        },
    }

    @classmethod
    def generate_work_orders(
        cls,
        fleet_summary: FleetMaintenanceSummary,
    ) -> List[WorkOrder]:
        """Generate prescriptive work orders for any asset requiring maintenance intervention."""
        orders: List[WorkOrder] = []

        for asset_id, summary in fleet_summary.assets.items():
            urgency_str = summary.maintenance_urgency
            if urgency_str == "HEALTHY":
                continue

            urgency_enum = MaintenanceUrgency(urgency_str)
            tmpl = cls.JOB_TEMPLATES.get(asset_id, {
                "labor_hours": 10.0,
                "parts": [],
                "loto": "Standard LOTO Isolation",
                "scope": "Inspect and recondition asset.",
            })

            parts_list = tmpl["parts"]
            total_parts_cost = float(sum(p["qty"] * p["unit_cost_usd"] for p in parts_list))

            wo_id = f"WO-{asset_id[:5]}-{int(fleet_summary.current_operating_hours):05d}"

            wo = WorkOrder(
                work_order_id=wo_id,
                asset_id=asset_id,
                asset_name=summary.asset_name,
                urgency=urgency_enum,
                target_operating_hours=fleet_summary.current_operating_hours,
                health_index_pct=summary.current_health_index_pct,
                estimated_rul_hours=summary.estimated_rul_hours,
                estimated_labor_hours=tmpl["labor_hours"],
                required_spare_parts=parts_list,
                total_parts_cost_usd=round(total_parts_cost, 2),
                safety_loto_protocol=tmpl["loto"],
                scope_of_work=tmpl["scope"],
            )
            orders.append(wo)

        # Sort by urgency (critical first)
        urgency_rank = {
            MaintenanceUrgency.CRITICAL_REPLACEMENT: 1,
            MaintenanceUrgency.URGENT_INTERVENTION: 2,
            MaintenanceUrgency.PLANNED_MAINTENANCE: 3,
            MaintenanceUrgency.HEALTHY: 4,
        }
        orders.sort(key=lambda o: urgency_rank.get(o.urgency, 99))
        return orders
