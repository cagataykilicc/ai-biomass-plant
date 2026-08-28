"""Transient non-linear lumped capacitance dynamic model of the biomass conversion plant.

Models differential thermal energy balances, feeder motor lags, and disturbance injections.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Tuple
import numpy as np


@dataclass
class PlantDynamicState:
    """Snapshot of plant state at a discrete simulation time instant."""
    time_sec: float
    reactor_temp_c: float
    feed_rate_kg_h: float
    burner_heat_kw: float
    moisture_pct: float
    syngas_flow_nm3_h: float
    tsi_pct: float
    control_effort_pct: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time_sec": round(self.time_sec, 1),
            "time_min": round(self.time_sec / 60.0, 2),
            "reactor_temp_c": round(self.reactor_temp_c, 2),
            "feed_rate_kg_h": round(self.feed_rate_kg_h, 2),
            "burner_heat_kw": round(self.burner_heat_kw, 2),
            "moisture_pct": round(self.moisture_pct, 2),
            "syngas_flow_nm3_h": round(self.syngas_flow_nm3_h, 2),
            "tsi_pct": round(self.tsi_pct, 1),
            "control_effort_pct": round(self.control_effort_pct, 2),
        }


class DynamicBiomassReactor:
    """Non-linear lumped parameter dynamic simulation model for pyrolysis reactor and heat integration."""

    # Lumped thermal parameters
    BED_MASS_KG = 180.0             # Bed inventory mass (kg)
    CP_BED_KJ_KG_K = 1.35           # Effective bed specific heat (kJ/kg·K)
    UA_LOSSES_KW_K = 0.045          # Ambient heat loss coefficient (kW/K)
    T_AMBIENT_C = 25.0              # Ambient temperature (°C)
    DELTA_H_PYRO_KJ_KG = 320.0      # Endothermic pyrolysis reaction enthalpy (kJ/kg dry)
    
    # Time constants
    TAU_AUGER_SEC = 15.0            # Feeder motor acceleration time constant (s)
    TAU_BURNER_SEC = 35.0           # Combustor / flue gas heat transfer lag (s)
    MAX_BURNER_HEAT_KW = 85.0       # Max firing duty (kW)

    def __init__(
        self,
        initial_temp_c: float = 500.0,
        initial_feed_rate_kg_h: float = 100.0,
        initial_moisture_pct: float = 12.0,
    ) -> None:
        self.temp_c = initial_temp_c
        self.feed_rate_kg_h = initial_feed_rate_kg_h
        self.moisture_pct = initial_moisture_pct
        self.burner_heat_kw = 45.0  # Steady-state baseline firing
        self.time_sec = 0.0

    def step(
        self,
        control_input_pct: float,
        target_feed_rate_kg_h: float = 100.0,
        moisture_override: Optional[float] = None,
        dt_sec: float = 2.0,
    ) -> PlantDynamicState:
        """Advance dynamic simulation forward by dt_sec with applied control input."""
        u_clamped = float(np.clip(control_input_pct, 0.0, 100.0))
        if moisture_override is not None:
            self.moisture_pct = moisture_override

        # 1. Feeder Lag Dynamics: d(m_feed)/dt = (target - m_feed) / tau_feed
        dm_feed = (target_feed_rate_kg_h - self.feed_rate_kg_h) / self.TAU_AUGER_SEC
        self.feed_rate_kg_h += dm_feed * dt_sec
        self.feed_rate_kg_h = float(max(0.0, self.feed_rate_kg_h))

        # 2. Burner / Combustor Dynamics: d(Q_burner)/dt = (u * Q_max - Q_burner) / tau_burner
        target_heat = (u_clamped / 100.0) * self.MAX_BURNER_HEAT_KW
        dQ_burner = (target_heat - self.burner_heat_kw) / self.TAU_BURNER_SEC
        self.burner_heat_kw += dQ_burner * dt_sec
        self.burner_heat_kw = float(max(0.0, self.burner_heat_kw))

        # 3. Reactor Thermal Energy Balance
        # Net Heat Inflow = Q_burner_heat (kW)
        # Heat Demands (kW):
        #   - Sensible heating of biomass: m_feed (kg/s) * cp * (T_bed - T_in)
        #   - Moisture evaporation: m_feed * moisture% * h_fg / 3600
        #   - Endothermic cracking: m_feed * (1 - moisture%) * Delta_H / 3600
        #   - Heat losses to ambient: UA * (T_bed - T_amb)
        m_feed_kg_s = self.feed_rate_kg_h / 3600.0
        q_sensible = m_feed_kg_s * 1.5 * (self.temp_c - 100.0)  # dried at ~100°C
        q_evap = m_feed_kg_s * (self.moisture_pct / 100.0) * 2260.0  # Latent heat of vaporization
        q_rxn = m_feed_kg_s * (1.0 - self.moisture_pct / 100.0) * self.DELTA_H_PYRO_KJ_KG
        q_loss = self.UA_LOSSES_KW_K * (self.temp_c - self.T_AMBIENT_C)

        total_demand_kw = q_sensible + q_evap + q_rxn + q_loss

        # Thermal Capacitance: C_total = M_bed * cp_bed (kJ/K)
        c_total_kj_k = self.BED_MASS_KG * self.CP_BED_KJ_KG_K

        # dT/dt = (Q_in - Q_demand) / C_total
        dT_dt = (self.burner_heat_kw - total_demand_kw) / c_total_kj_k
        self.temp_c += float(dT_dt * dt_sec)
        self.temp_c = float(np.clip(self.temp_c, 100.0, 900.0))

        self.time_sec += dt_sec

        # Approximate real-time syngas & TSI
        syngas_flow = 16.5 * (self.feed_rate_kg_h / 100.0) * (self.temp_c / 500.0)
        tsi_pct = float(self.burner_heat_kw / max(1.0, total_demand_kw) * 100.0)

        return PlantDynamicState(
            time_sec=self.time_sec,
            reactor_temp_c=self.temp_c,
            feed_rate_kg_h=self.feed_rate_kg_h,
            burner_heat_kw=self.burner_heat_kw,
            moisture_pct=self.moisture_pct,
            syngas_flow_nm3_h=syngas_flow,
            tsi_pct=tsi_pct,
            control_effort_pct=u_clamped,
        )
