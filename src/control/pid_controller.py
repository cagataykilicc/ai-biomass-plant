"""Industrial digital PID feedback controller with anti-windup clamping and derivative filtering.

Regulates reactor core temperature by modulating combustor firing duty.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class PIDGains:
    """Proportional, integral, derivative, and filter tuning parameters."""
    Kp: float = 1.80       # Proportional gain (% / °C)
    Ki: float = 0.045      # Integral gain (% / °C·s)
    Kd: float = 8.50       # Derivative gain (%·s / °C)
    N: float = 10.0        # First-order derivative filter coefficient (alpha = 1/N = 0.1)


class PIDController:
    """Discrete digital PID controller with anti-windup clamping and noise filtering."""

    def __init__(
        self,
        gains: Optional[PIDGains] = None,
        u_min: float = 0.0,
        u_max: float = 100.0,
        initial_u: float = 55.0,
    ) -> None:
        self.gains = gains or PIDGains()
        self.u_min = u_min
        self.u_max = u_max

        self.integral_sum = initial_u / max(1e-4, self.gains.Ki)  # Pre-bias integrator
        self.prev_error = 0.0
        self.prev_derivative = 0.0
        self.prev_pv = None
        self.last_output = initial_u

    def reset(self, initial_u: float = 55.0) -> None:
        """Reset internal integrator and memory states."""
        self.integral_sum = initial_u / max(1e-4, self.gains.Ki)
        self.prev_error = 0.0
        self.prev_derivative = 0.0
        self.prev_pv = None
        self.last_output = initial_u

    def compute(
        self,
        setpoint: float,
        process_variable: float,
        dt_sec: float = 2.0,
    ) -> float:
        """Compute next control effort u(k) in [u_min, u_max]."""
        error = setpoint - process_variable

        # 1. Proportional Term
        P = self.gains.Kp * error

        # 2. Derivative Term with 1st-Order Low-Pass Filter
        # D_filtered(k) = (Kd * N * (e(k) - e(k-1)) + prev_D) / (1 + N * dt)
        de = error - self.prev_error
        D = (self.gains.Kd * self.gains.N * de + self.prev_derivative) / (1.0 + self.gains.N * dt_sec)

        # 3. Integral Term with Anti-Windup Clamping
        # Unclamped candidate
        u_raw = P + (self.gains.Ki * (self.integral_sum + error * dt_sec)) + D

        # Conditional integration (Anti-Windup): Only integrate if not saturated in the direction of error
        if self.u_min < u_raw < self.u_max:
            self.integral_sum += error * dt_sec
        elif u_raw >= self.u_max and error < 0.0:
            # Saturated high, but error is negative (unwinding)
            self.integral_sum += error * dt_sec
        elif u_raw <= self.u_min and error > 0.0:
            # Saturated low, but error is positive (unwinding)
            self.integral_sum += error * dt_sec

        I = self.gains.Ki * self.integral_sum

        # Compute final clamped output
        u_out = float(np.clip(P + I + D, self.u_min, self.u_max))

        # Store memory states for next step
        self.prev_error = error
        self.prev_derivative = D
        self.prev_pv = process_variable
        self.last_output = u_out

        return u_out
