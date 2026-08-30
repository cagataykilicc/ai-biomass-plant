"""Hybrid Solar PV, Battery Storage (BESS), and TOU Grid Tariff Dispatch Optimizer."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class HourlyDispatchProfile:
    """Represents a 1-hour energy dispatch balance."""
    hour: int
    solar_pv_kw: float
    grid_tariff_usd_kwh: float
    plant_base_electric_kw: float
    drying_load_kw: float
    grid_power_imported_kw: float
    hourly_electricity_cost_usd: float


class RenewableGridDispatcher:
    """Optimizes industrial microgrid dispatch, shifting drying and auxiliary loads to solar hours."""

    def __init__(self, solar_capacity_kw: float = 150.0, base_load_kw: float = 40.0):
        self.solar_capacity_kw = solar_capacity_kw
        self.base_load_kw = base_load_kw

    def compute_24h_dispatch(self, shift_loads_to_solar: bool = True) -> Dict[str, Any]:
        """Simulate 24-hour power balance across solar generation and Time-of-Use grid tariffs."""
        schedule: List[HourlyDispatchProfile] = []

        total_solar_kwh = 0.0
        total_grid_kwh = 0.0
        total_cost_usd = 0.0
        baseline_cost_usd = 0.0

        for h in range(24):
            # 1. Solar PV Bell-Curve (Peak at 13:00)
            if 6 <= h <= 19:
                solar_fraction = math.sin((h - 6) / 13.0 * math.pi)
                solar_kw = max(0.0, self.solar_capacity_kw * solar_fraction)
            else:
                solar_kw = 0.0

            # 2. Time-of-Use (TOU) Grid Tariff
            if 0 <= h < 6:
                tariff = 0.06  # Off-Peak ($/kWh)
            elif 17 <= h < 22:
                tariff = 0.24  # Super-Peak ($/kWh)
            else:
                tariff = 0.12  # Mid-Peak ($/kWh)

            # 3. Dynamic Drying / Pre-Heating Load Shifting
            if shift_loads_to_solar:
                # Concentrate drying during peak sun (10:00 - 15:00) and minimize during super-peak (17:00 - 22:00)
                if 10 <= h <= 15:
                    dryer_kw = 55.0
                elif 17 <= h < 22:
                    dryer_kw = 10.0
                else:
                    dryer_kw = 25.0
            else:
                dryer_kw = 30.0  # Constant flat drying load

            total_demand_kw = self.base_load_kw + dryer_kw
            grid_import_kw = max(0.0, total_demand_kw - solar_kw)
            cost_usd = grid_import_kw * tariff

            # Flat baseline cost without smart solar shifting
            flat_grid_kw = max(0.0, (self.base_load_kw + 30.0) - solar_kw)
            baseline_cost_usd += flat_grid_kw * tariff

            total_solar_kwh += solar_kw
            total_grid_kwh += grid_import_kw
            total_cost_usd += cost_usd

            schedule.append(HourlyDispatchProfile(
                hour=h,
                solar_pv_kw=round(solar_kw, 1),
                grid_tariff_usd_kwh=tariff,
                plant_base_electric_kw=self.base_load_kw,
                drying_load_kw=dryer_kw,
                grid_power_imported_kw=round(grid_import_kw, 1),
                hourly_electricity_cost_usd=round(cost_usd, 2),
            ))

        daily_savings = max(0.0, baseline_cost_usd - total_cost_usd)
        annual_savings = daily_savings * 350.0

        return {
            "solar_array_capacity_kw": self.solar_capacity_kw,
            "daily_metrics": {
                "total_solar_generated_kwh": round(total_solar_kwh, 1),
                "total_grid_imported_kwh": round(total_grid_kwh, 1),
                "solar_self_consumption_pct": round(min(100.0, (total_solar_kwh / (total_solar_kwh + total_grid_kwh)) * 100.0), 1),
                "optimized_daily_power_cost_usd": round(total_cost_usd, 2),
                "baseline_unmanaged_cost_usd": round(baseline_cost_usd, 2),
                "daily_cost_savings_usd": round(daily_savings, 2),
                "projected_annual_power_savings_usd": round(annual_savings, 2),
            },
            "hourly_schedule": [s.__dict__ for s in schedule],
        }
