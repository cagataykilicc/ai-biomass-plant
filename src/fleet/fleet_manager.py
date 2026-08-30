"""Regional Multi-Reactor Decentralized Fleet Orchestrator and Agricultural Harvest Scheduler."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class PlantNodeState:
    """Represents real-time operational status and metrics of a decentralized plant node."""
    plant_id: str
    name: str
    location: str
    feedstock: str
    feed_rate_kg_h: float
    capacity_kg_h: float
    reactor_temp_c: float
    status: str  # "ONLINE_AUTONOMOUS", "PREHEATING", "DISTURBANCE_ADAPTATION", "MAINTENANCE"
    oee_pct: float
    daily_feed_tonnes: float
    daily_bio_oil_m3: float
    daily_co2e_sequestered_t: float
    current_fsm_state: str = "AUTONOMOUS_CRUISE"
    active_alarms_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plant_id": self.plant_id,
            "name": self.name,
            "location": self.location,
            "feedstock": self.feedstock,
            "feed_rate_kg_h": round(self.feed_rate_kg_h, 1),
            "capacity_kg_h": round(self.capacity_kg_h, 1),
            "utilization_pct": round((self.feed_rate_kg_h / self.capacity_kg_h) * 100.0, 1) if self.capacity_kg_h > 0 else 0.0,
            "reactor_temp_c": round(self.reactor_temp_c, 1),
            "status": self.status,
            "oee_pct": round(self.oee_pct, 1),
            "daily_feed_tonnes": round(self.daily_feed_tonnes, 2),
            "daily_bio_oil_m3": round(self.daily_bio_oil_m3, 2),
            "daily_co2e_sequestered_t": round(self.daily_co2e_sequestered_t, 2),
            "current_fsm_state": self.current_fsm_state,
            "active_alarms_count": self.active_alarms_count,
        }


class RegionalFleetManager:
    """Centralized coordinator orchestrating distributed biomass conversion facilities."""

    def __init__(self):
        self.plants: Dict[str, PlantNodeState] = {
            "PLANT_01": PlantNodeState(
                plant_id="PLANT_01",
                name="Aegean Olive Agri-Hub",
                location="Izmir, Turkey (38.42° N, 27.14° E)",
                feedstock="olive_pomace",
                feed_rate_kg_h=150.0,
                capacity_kg_h=200.0,
                reactor_temp_c=500.0,
                status="ONLINE_AUTONOMOUS",
                oee_pct=94.5,
                daily_feed_tonnes=3.60,
                daily_bio_oil_m3=1.95,
                daily_co2e_sequestered_t=4.12,
                current_fsm_state="AUTONOMOUS_CRUISE",
                active_alarms_count=0,
            ),
            "PLANT_02": PlantNodeState(
                plant_id="PLANT_02",
                name="Nordic Forestry Biomass Hub",
                location="Umeå, Sweden (63.82° N, 20.26° E)",
                feedstock="pine_sawdust",
                feed_rate_kg_h=220.0,
                capacity_kg_h=250.0,
                reactor_temp_c=520.0,
                status="ONLINE_AUTONOMOUS",
                oee_pct=96.8,
                daily_feed_tonnes=5.28,
                daily_bio_oil_m3=3.10,
                daily_co2e_sequestered_t=5.95,
                current_fsm_state="AUTONOMOUS_CRUISE",
                active_alarms_count=0,
            ),
            "PLANT_03": PlantNodeState(
                plant_id="PLANT_03",
                name="Anatolian Cereal Residue Hub",
                location="Konya, Turkey (37.87° N, 32.49° E)",
                feedstock="wheat_straw",
                feed_rate_kg_h=120.0,
                capacity_kg_h=180.0,
                reactor_temp_c=480.0,
                status="ONLINE_AUTONOMOUS",
                oee_pct=91.2,
                daily_feed_tonnes=2.88,
                daily_bio_oil_m3=1.40,
                daily_co2e_sequestered_t=3.45,
                current_fsm_state="AUTONOMOUS_CRUISE",
                active_alarms_count=0,
            ),
        }

    def get_fleet_summary(self) -> Dict[str, Any]:
        """Aggregate operational KPIs across all active plant facilities."""
        total_feed_t = sum(p.daily_feed_tonnes for p in self.plants.values())
        total_oil_m3 = sum(p.daily_bio_oil_m3 for p in self.plants.values())
        total_co2e_t = sum(p.daily_co2e_sequestered_t for p in self.plants.values())
        avg_oee = sum(p.oee_pct for p in self.plants.values()) / len(self.plants) if self.plants else 0.0
        total_current_feed_kg_h = sum(p.feed_rate_kg_h for p in self.plants.values())
        total_capacity_kg_h = sum(p.capacity_kg_h for p in self.plants.values())

        return {
            "timestamp": int(time.time()),
            "fleet_size": len(self.plants),
            "fleet_status": "ALL_NODES_OPERATIONAL",
            "fleet_kpis": {
                "total_current_throughput_kg_h": round(total_current_feed_kg_h, 1),
                "total_nameplate_capacity_kg_h": round(total_capacity_kg_h, 1),
                "fleet_utilization_pct": round((total_current_feed_kg_h / total_capacity_kg_h) * 100.0, 1) if total_capacity_kg_h > 0 else 0.0,
                "fleet_average_oee_pct": round(avg_oee, 2),
                "daily_aggregated_feed_tonnes": round(total_feed_t, 2),
                "daily_aggregated_bio_oil_m3": round(total_oil_m3, 2),
                "daily_permanent_co2e_sinks_tonnes": round(total_co2e_t, 2),
            },
            "plants": {pid: p.to_dict() for pid, p in self.plants.items()},
        }

    def dispatch_plant_setpoint(self, plant_id: str, setpoints: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch new operational setpoint commands to a specific plant node."""
        if plant_id not in self.plants:
            raise KeyError(f"Plant ID '{plant_id}' not found in registered fleet nodes.")

        plant = self.plants[plant_id]
        if "feed_rate_kg_h" in setpoints:
            rate = float(setpoints["feed_rate_kg_h"])
            plant.feed_rate_kg_h = max(0.0, min(plant.capacity_kg_h, rate))
            plant.daily_feed_tonnes = (plant.feed_rate_kg_h * 24.0) / 1000.0

        if "reactor_temp_c" in setpoints:
            plant.reactor_temp_c = max(300.0, min(750.0, float(setpoints["reactor_temp_c"])))

        if "status" in setpoints:
            plant.status = str(setpoints["status"])

        return {
            "status": "DISPATCH_CONFIRMED",
            "plant_id": plant_id,
            "updated_node": plant.to_dict(),
        }

    def optimize_seasonal_harvest_schedule(self, season: str = "AUTUMN") -> Dict[str, Any]:
        """Dynamically allocate fleet throughput based on regional agricultural harvest availability."""
        season = season.upper()
        # Seasonal allocation multipliers
        if season in ("AUTUMN", "WINTER"):
            # Olive harvest season in Mediterranean
            self.plants["PLANT_01"].feed_rate_kg_h = 190.0
            self.plants["PLANT_02"].feed_rate_kg_h = 220.0
            self.plants["PLANT_03"].feed_rate_kg_h = 100.0
        elif season == "SUMMER":
            # Cereal/Wheat harvest peak in Anatolia
            self.plants["PLANT_01"].feed_rate_kg_h = 110.0
            self.plants["PLANT_02"].feed_rate_kg_h = 230.0
            self.plants["PLANT_03"].feed_rate_kg_h = 175.0
        else:  # SPRING
            self.plants["PLANT_01"].feed_rate_kg_h = 130.0
            self.plants["PLANT_02"].feed_rate_kg_h = 240.0
            self.plants["PLANT_03"].feed_rate_kg_h = 130.0

        for p in self.plants.values():
            p.daily_feed_tonnes = (p.feed_rate_kg_h * 24.0) / 1000.0

        return {
            "season": season,
            "strategy": f"Seasonal harvest load balancing for {season}",
            "fleet_summary": self.get_fleet_summary(),
        }
