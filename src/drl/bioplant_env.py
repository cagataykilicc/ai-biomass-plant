"""Gymnasium-Compatible Industrial Biomass Pyrolysis Digital Twin Environment (BioPlant-v1)."""

from __future__ import annotations

import math
import random
from typing import Dict, Any, Tuple, List, Optional


class BioPlantEnv:
    """Non-linear transient dynamic simulation environment for Deep Reinforcement Learning."""

    def __init__(
        self,
        target_temp_c: float = 500.0,
        nominal_feed_kg_h: float = 100.0,
        dt_sec: float = 2.0,
        max_steps: int = 100,
    ):
        self.target_temp_c = target_temp_c
        self.nominal_feed_kg_h = nominal_feed_kg_h
        self.dt_sec = dt_sec
        self.max_steps = max_steps

        # State Variables
        self.current_step = 0
        self.reactor_temp_c = 480.0
        self.d_temp_dt = 0.0
        self.feed_rate_kg_h = 100.0
        self.burner_duty_pct = 45.0
        self.cyclone_dp_mbar = 12.0
        self.moisture_pct = 10.0
        self.tsi_pct = 110.0
        self.alarm_active = False

        # Action space bounds
        self.action_low = [-10.0, -15.0, 0.0]  # [d_burner, d_feed, pulse_jet]
        self.action_high = [10.0, 15.0, 1.0]

    def reset(self, seed: Optional[int] = None) -> Tuple[List[float], Dict[str, Any]]:
        """Reset the environment to initial conditions."""
        if seed is not None:
            random.seed(seed)

        self.current_step = 0
        self.reactor_temp_c = 480.0 + random.uniform(-10.0, 10.0)
        self.d_temp_dt = 0.0
        self.feed_rate_kg_h = self.nominal_feed_kg_h
        self.burner_duty_pct = 45.0
        self.cyclone_dp_mbar = 12.0 + random.uniform(-2.0, 2.0)
        self.moisture_pct = 10.0 + random.uniform(-2.0, 4.0)
        self.tsi_pct = 112.0
        self.alarm_active = False

        obs = self._get_observation()
        info = {
            "reactor_temp_c": self.reactor_temp_c,
            "target_temp_c": self.target_temp_c,
            "tsi_pct": self.tsi_pct,
            "step": self.current_step,
        }
        return obs, info

    def step(self, action: List[float]) -> Tuple[List[float], float, bool, bool, Dict[str, Any]]:
        """Execute one dynamic control action step."""
        self.current_step += 1

        # Clip actions to continuous boundaries
        d_burner = max(self.action_low[0], min(self.action_high[0], float(action[0])))
        d_feed = max(self.action_low[1], min(self.action_high[1], float(action[1])))
        pulse_jet = float(action[2]) > 0.5

        # Update Actuators
        self.burner_duty_pct = max(0.0, min(100.0, self.burner_duty_pct + d_burner))
        self.feed_rate_kg_h = max(20.0, min(200.0, self.feed_rate_kg_h + d_feed))

        # Random external moisture shock at step 20-30
        if 20 <= self.current_step <= 30:
            self.moisture_pct = min(25.0, self.moisture_pct + random.uniform(0.2, 0.8))
        else:
            self.moisture_pct = max(8.0, self.moisture_pct - 0.2)

        # Pulse-jet blowback clears cyclone DP
        if pulse_jet or self.cyclone_dp_mbar > 28.0:
            self.cyclone_dp_mbar = max(10.0, self.cyclone_dp_mbar - 8.0)
        else:
            self.cyclone_dp_mbar += random.uniform(-0.1, 0.3)

        # First-principles thermal balance differential update
        q_burner = self.burner_duty_pct * 12.5  # kW thermal
        q_feed_sensible = (self.feed_rate_kg_h / 3600.0) * 1.6 * (self.reactor_temp_c - 25.0)
        q_moisture_latent = (self.feed_rate_kg_h * (self.moisture_pct / 100.0) / 3600.0) * 2260.0
        q_loss = 0.08 * (self.reactor_temp_c - 25.0)

        net_q = q_burner - (q_feed_sensible + q_moisture_latent + q_loss)
        thermal_mass_mc = 450.0  # kJ/°C effective thermal capacity

        new_d_temp = (net_q / thermal_mass_mc) * self.dt_sec
        self.reactor_temp_c += new_d_temp
        self.d_temp_dt = new_d_temp / self.dt_sec

        # Update TSI
        heat_recovered = (q_burner * 0.82)
        total_in = q_burner + 5.0
        self.tsi_pct = round((heat_recovered / total_in) * 100.0 + 15.0, 1)

        # Check safety trip
        safety_violation = False
        if self.reactor_temp_c > 620.0 or self.reactor_temp_c < 350.0:
            safety_violation = True
            self.alarm_active = True

        # Calculate reward
        temp_err = self.reactor_temp_c - self.target_temp_c
        reward = (
            -1.0 * ((temp_err / 10.0) ** 2)
            - 0.05 * (d_burner ** 2)
            + 0.5 * (self.tsi_pct / 100.0)
            - (50.0 if safety_violation else 0.0)
        )

        terminated = safety_violation
        truncated = self.current_step >= self.max_steps
        obs = self._get_observation()

        info = {
            "step": self.current_step,
            "reactor_temp_c": round(self.reactor_temp_c, 2),
            "target_temp_c": self.target_temp_c,
            "temp_error_c": round(temp_err, 2),
            "burner_duty_pct": round(self.burner_duty_pct, 1),
            "feed_rate_kg_h": round(self.feed_rate_kg_h, 1),
            "cyclone_dp_mbar": round(self.cyclone_dp_mbar, 1),
            "moisture_pct": round(self.moisture_pct, 1),
            "tsi_pct": self.tsi_pct,
            "reward": round(reward, 3),
            "safety_violation": safety_violation,
        }

        return obs, reward, terminated, truncated, info

    def _get_observation(self) -> List[float]:
        """Normalized 8-dimensional observation state vector."""
        return [
            round((self.reactor_temp_c - self.target_temp_c) / 50.0, 4),
            round(self.d_temp_dt / 5.0, 4),
            round(self.cyclone_dp_mbar / 30.0, 4),
            round(self.moisture_pct / 30.0, 4),
            round(self.tsi_pct / 150.0, 4),
            round(self.feed_rate_kg_h / 200.0, 4),
            round(self.burner_duty_pct / 100.0, 4),
            1.0 if self.alarm_active else 0.0,
        ]
