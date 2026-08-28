"""Model Predictive Controller (MPC) for multi-horizon optimal trajectory tracking.

Solves constrained quadratic programming (QP) optimization over receding horizons.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import numpy as np


@dataclass
class MPCConfig:
    """Horizon lengths, penalty weights, and actuator constraints."""
    prediction_horizon_Np: int = 15     # Lookahead steps (30 seconds)
    control_horizon_Nc: int = 5         # Control decision steps (10 seconds)
    weight_tracking_Q: float = 1.50     # Output error penalty
    weight_effort_R: float = 0.02       # Steady-state effort penalty
    weight_slew_S: float = 0.15         # Control rate-of-change (slew) penalty
    u_min: float = 0.0
    u_max: float = 100.0
    max_slew_per_step: float = 8.0      # Max % change per control step


class ModelPredictiveController:
    """Receding horizon Model Predictive Controller for plant thermal regulation."""

    def __init__(
        self,
        config: Optional[MPCConfig] = None,
        process_gain_k: float = 2.10,     # °C per % burner duty
        time_constant_tau: float = 40.0,  # Effective thermal lag (s)
        dt_sec: float = 2.0,
        initial_u: float = 55.0,
    ) -> None:
        self.cfg = config or MPCConfig()
        self.dt_sec = dt_sec
        self.u_prev = initial_u

        # Discrete FOPDT model: T(k+1) = a * T(k) + b * u(k)
        self.a = float(np.exp(-dt_sec / time_constant_tau))
        self.b = float(process_gain_k * (1.0 - self.a))
        self.d_hat = 0.0  # Estimated unmeasured disturbance offset

    def reset(self, initial_u: float = 55.0) -> None:
        """Reset MPC state history."""
        self.u_prev = initial_u
        self.d_hat = 0.0

    def compute(
        self,
        setpoint: float,
        current_pv: float,
        dt_sec: Optional[float] = None,
    ) -> float:
        """Execute receding horizon quadratic programming optimization and return u(k)."""
        dt = dt_sec or self.dt_sec
        Np = self.cfg.prediction_horizon_Np
        Nc = self.cfg.control_horizon_Nc

        # 1. State Estimation & Disturbance Observer
        # Update unmeasured disturbance: d_hat = current_pv - model_predicted_pv
        pred_pv = self.a * current_pv + self.b * self.u_prev
        self.d_hat = float(0.85 * self.d_hat + 0.15 * (current_pv - pred_pv))

        # 2. Build Dynamic Prediction Matrix
        # Free response: y_free(k+i) starting from current_pv with constant u_prev
        y_free = np.zeros(Np)
        t_curr = current_pv
        for i in range(Np):
            t_curr = self.a * t_curr + self.b * self.u_prev + self.d_hat
            y_free[i] = t_curr

        # Step response dynamic matrix G (Np x Nc)
        G = np.zeros((Np, Nc))
        step_resp = np.zeros(Np)
        val = 0.0
        for i in range(Np):
            val = self.a * val + self.b * 1.0
            step_resp[i] = val

        for j in range(Nc):
            G[j:, j] = step_resp[:Np - j]

        # 3. Formulate Quadratic Optimization:
        # min_du 0.5 * du^T * H * du + f^T * du
        # H = 2 * (G^T * Q * G + S * I)
        # f = 2 * (G^T * Q * (y_free - setpoint))
        Q_mat = self.cfg.weight_tracking_Q * np.eye(Np)
        S_mat = self.cfg.weight_slew_S * np.eye(Nc)

        H = 2.0 * (G.T @ Q_mat @ G + S_mat)
        error_vec = y_free - setpoint
        f = 2.0 * (G.T @ Q_mat @ error_vec)

        # 4. Unconstrained Analytical Solution: du* = - H^-1 * f
        try:
            du_opt = -np.linalg.solve(H, f)
        except np.linalg.LinAlgError:
            du_opt = np.zeros(Nc)

        # Extract first move du[0]
        du_0 = float(du_opt[0])

        # 5. Apply Slew-Rate and Actuator Box Constraints
        du_clamped = float(np.clip(du_0, -self.cfg.max_slew_per_step, self.cfg.max_slew_per_step))
        u_new = float(np.clip(self.u_prev + du_clamped, self.cfg.u_min, self.cfg.u_max))

        self.u_prev = u_new
        return u_new
