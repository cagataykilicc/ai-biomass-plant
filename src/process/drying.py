"""Biomass drying and pretreatment unit operation model.

Models thermal moisture removal, mass reduction, and thermodynamic energy demands
(sensible heating of solids and moisture, latent heat of vaporization, superheating of steam,
and parasitic electrical consumption).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import math

from src.data.feedstock import BiomassFeedstock, FeedstockValidationError


# Standard physical constants for water/steam thermodynamics
CP_LIQUID_WATER_KJ_KG_K = 4.184       # Specific heat of liquid water (kJ/(kg*K))
CP_WATER_STEAM_KJ_KG_K = 2.010        # Specific heat of water vapor/steam (kJ/(kg*K))
DELTA_H_VAP_WATER_100C_KJ_KG = 2257.0 # Latent heat of vaporization of water at 100 °C (kJ/kg)


@dataclass
class DryingConfig:
    """Operating parameters and design assumptions for biomass dryer.

    Attributes:
        target_moisture_pct: Target moisture in dried biomass exiting dryer (wt%).
        dryer_temperature_c: Exhaust/operating temperature of drying chamber (°C).
        ambient_temperature_c: Baseline ambient ambient temperature (°C).
        thermal_efficiency: Fraction of thermal heat effectively transferred to biomass (0 < eta <= 1.0).
        specific_electrical_consumption_kwh_tonne: Auxiliary power for motors/fans per tonne wet feed.
    """
    target_moisture_pct: float = 8.0
    dryer_temperature_c: float = 105.0
    ambient_temperature_c: float = 25.0
    thermal_efficiency: float = 0.75
    specific_electrical_consumption_kwh_tonne: float = 15.0

    def __post_init__(self) -> None:
        if not (0.0 <= self.target_moisture_pct < 100.0):
            raise ValueError(f"Target moisture must be in [0, 100) wt%. Got: {self.target_moisture_pct}")
        if self.dryer_temperature_c <= self.ambient_temperature_c:
            raise ValueError(
                f"Dryer temperature ({self.dryer_temperature_c} °C) must exceed ambient temperature ({self.ambient_temperature_c} °C)."
            )
        if not (0.0 < self.thermal_efficiency <= 1.0):
            raise ValueError(f"Thermal efficiency must be in (0, 1.0]. Got: {self.thermal_efficiency}")


@dataclass
class DryingResult:
    """Results from biomass drying unit operation.

    Contains mass flows, water evaporated, thermal/electrical energy duties,
    and specific energy consumption metrics.
    """
    feed_rate_in_kg_h: float
    dried_feed_rate_out_kg_h: float
    water_evaporated_kg_h: float
    initial_moisture_pct: float
    final_moisture_pct: float
    dry_matter_kg_h: float
    thermal_duty_th_kw: float
    thermal_duty_actual_kw: float
    thermal_duty_actual_mj_h: float
    electrical_power_kw: float
    specific_energy_kj_per_kg_water: float
    dryer_temperature_c: float
    assumptions: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feed_rate_in_kg_h": round(self.feed_rate_in_kg_h, 3),
            "dried_feed_rate_out_kg_h": round(self.dried_feed_rate_out_kg_h, 3),
            "water_evaporated_kg_h": round(self.water_evaporated_kg_h, 3),
            "initial_moisture_pct": round(self.initial_moisture_pct, 2),
            "final_moisture_pct": round(self.final_moisture_pct, 2),
            "dry_matter_kg_h": round(self.dry_matter_kg_h, 3),
            "thermal_duty_actual_kw": round(self.thermal_duty_actual_kw, 3),
            "thermal_duty_actual_mj_h": round(self.thermal_duty_actual_mj_h, 3),
            "electrical_power_kw": round(self.electrical_power_kw, 3),
            "specific_energy_kj_per_kg_water": round(self.specific_energy_kj_per_kg_water, 2),
            "dryer_temperature_c": self.dryer_temperature_c,
            "assumptions": self.assumptions,
        }


class BiomassDryer:
    """Biomass drying unit operation simulator."""

    def __init__(self, config: Optional[DryingConfig] = None) -> None:
        self.config = config or DryingConfig()

    def process(
        self,
        feed_rate_kg_h: float,
        feedstock: BiomassFeedstock,
        target_moisture_override: Optional[float] = None,
        dryer_temp_override: Optional[float] = None,
    ) -> DryingResult:
        """Simulate drying of wet biomass feed to target moisture content.

        Args:
            feed_rate_kg_h: Inflow rate of raw as-received biomass (kg/h).
            feedstock: BiomassFeedstock instance containing proximate moisture and thermodynamic properties.
            target_moisture_override: Optional override for target exit moisture (wt%).
            dryer_temp_override: Optional override for dryer temperature (°C).

        Returns:
            DryingResult containing mass flows and energy requirements.
        """
        if feed_rate_kg_h <= 0:
            raise ValueError(f"Feed rate must be positive (> 0 kg/h). Got: {feed_rate_kg_h}")

        w_in = feedstock.proximate.moisture
        target_w = target_moisture_override if target_moisture_override is not None else self.config.target_moisture_pct
        t_dryer = dryer_temp_override if dryer_temp_override is not None else self.config.dryer_temperature_c
        t_amb = self.config.ambient_temperature_c
        eta_th = self.config.thermal_efficiency

        if target_w >= w_in:
            # Feedstock is already drier than or equal to target moisture; no water removal needed
            w_out = w_in
            m_water_evap = 0.0
            m_out = feed_rate_kg_h
            m_dry_matter = feed_rate_kg_h * (1.0 - w_in / 100.0)
            q_th_total_kj_h = 0.0
            q_actual_kw = 0.0
            q_actual_mj_h = 0.0
            sec_kj_kg = 0.0
            elec_kw = 0.0
        else:
            w_out = target_w
            # Mass of dry matter is conserved: m_dry = m_in * (1 - w_in/100)
            m_dry_matter = feed_rate_kg_h * (1.0 - w_in / 100.0)
            # Exit mass: m_out = m_dry / (1 - w_out/100)
            m_out = m_dry_matter / (1.0 - w_out / 100.0)
            m_water_evap = feed_rate_kg_h - m_out

            # Thermodynamic heat calculations
            # 1. Mean biomass specific heat capacity between T_amb and T_dryer
            t_mean = (t_amb + t_dryer) / 2.0
            cp_bio = feedstock.specific_heat_capacity(t_mean)
            q_sens_solid = m_dry_matter * cp_bio * (t_dryer - t_amb)

            # 2. Sensible heating of retained water
            m_water_retained = m_out * (w_out / 100.0)
            q_sens_retained_water = m_water_retained * CP_LIQUID_WATER_KJ_KG_K * (min(100.0, t_dryer) - t_amb)

            # 3. Sensible heating of evaporated water from T_amb to 100 °C
            q_sens_evap_water = m_water_evap * CP_LIQUID_WATER_KJ_KG_K * (100.0 - t_amb)

            # 4. Latent heat of vaporization of water at 100 °C
            q_lat_evap = m_water_evap * DELTA_H_VAP_WATER_100C_KJ_KG

            # 5. Sensible superheating of steam above 100 °C (if T_dryer > 100)
            if t_dryer > 100.0:
                q_sens_steam = m_water_evap * CP_WATER_STEAM_KJ_KG_K * (t_dryer - 100.0)
            else:
                q_sens_steam = 0.0

            q_th_total_kj_h = q_sens_solid + q_sens_retained_water + q_sens_evap_water + q_lat_evap + q_sens_steam
            
            # Actual thermal heat duty considering thermal efficiency
            q_actual_kj_h = q_th_total_kj_h / eta_th
            q_actual_kw = q_actual_kj_h / 3600.0
            q_actual_mj_h = q_actual_kj_h / 1000.0

            # Specific Energy Consumption (kJ / kg water removed)
            sec_kj_kg = q_actual_kj_h / m_water_evap if m_water_evap > 0 else 0.0

            # Auxiliary electrical power (fans, conveyors, drum rotation)
            elec_kw = (feed_rate_kg_h / 1000.0) * self.config.specific_electrical_consumption_kwh_tonne

        assumptions = {
            "cp_liquid_water_kj_kg_k": CP_LIQUID_WATER_KJ_KG_K,
            "cp_steam_kj_kg_k": CP_WATER_STEAM_KJ_KG_K,
            "latent_heat_vap_kj_kg": DELTA_H_VAP_WATER_100C_KJ_KG,
            "ambient_temp_c": t_amb,
            "dryer_thermal_efficiency": eta_th,
            "dry_matter_conservation": True,
        }

        return DryingResult(
            feed_rate_in_kg_h=feed_rate_kg_h,
            dried_feed_rate_out_kg_h=m_out,
            water_evaporated_kg_h=m_water_evap,
            initial_moisture_pct=w_in,
            final_moisture_pct=w_out,
            dry_matter_kg_h=m_dry_matter,
            thermal_duty_th_kw=q_th_total_kj_h / 3600.0,
            thermal_duty_actual_kw=q_actual_kw,
            thermal_duty_actual_mj_h=q_actual_mj_h,
            electrical_power_kw=elec_kw,
            specific_energy_kj_per_kg_water=sec_kj_kg,
            dryer_temperature_c=t_dryer,
            assumptions=assumptions,
        )
