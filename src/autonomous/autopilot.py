"""Supervisory Agent and 5-State Autonomous Autopilot Finite State Machine (FSM).

Executes end-to-end closed-loop Sense-Infer-Diagnose-Optimize-Actuate-Maintain operations.
"""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Tuple, Optional, List

from src.control.dynamic_model import DynamicBiomassReactor, PlantDynamicState
from src.control.mpc_controller import ModelPredictiveController, MPCConfig
from src.autonomous.flight_recorder import FlightRecorder, FlightLogEntry


class PlantOperatingState(str, Enum):
    """Finite State Machine (FSM) autonomous operating modes."""
    STARTUP_PREHEAT = "STARTUP_PREHEAT"
    AUTONOMOUS_CRUISE = "AUTONOMOUS_CRUISE"
    DISTURBANCE_ADAPTATION = "DISTURBANCE_ADAPTATION"
    FAULT_MITIGATION = "FAULT_MITIGATION"
    EMERGENCY_SAFE_PARK = "EMERGENCY_SAFE_PARK"


@dataclass
class AutopilotCommand:
    """Supervisory control decision emitted to plant actuators."""
    fsm_state: PlantOperatingState
    target_temp_c: float
    target_feed_rate_kg_h: float
    burner_duty_pct: float
    nitrogen_purge_active: bool
    pulse_jet_active: bool
    safety_interlock_tripped: bool
    action_summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fsm_state": self.fsm_state.value,
            "target_temp_c": round(self.target_temp_c, 1),
            "target_feed_rate_kg_h": round(self.target_feed_rate_kg_h, 1),
            "burner_duty_pct": round(self.burner_duty_pct, 1),
            "nitrogen_purge_active": self.nitrogen_purge_active,
            "pulse_jet_active": self.pulse_jet_active,
            "safety_interlock_tripped": self.safety_interlock_tripped,
            "action_summary": self.action_summary,
        }


class AutonomousSupervisoryAgent:
    """Autonomous autopilot orchestrating plant startup, nominal cruise, disturbance rejection, and fault recovery."""

    def __init__(
        self,
        target_cruise_temp_c: float = 500.0,
        nominal_feed_rate_kg_h: float = 100.0,
        dt_sec: float = 2.0,
    ) -> None:
        self.target_cruise_temp_c = target_cruise_temp_c
        self.nominal_feed_rate_kg_h = nominal_feed_rate_kg_h
        self.dt_sec = dt_sec

        self.current_state = PlantOperatingState.STARTUP_PREHEAT
        self.plant = DynamicBiomassReactor(
            initial_temp_c=120.0,  # Cold preheat start
            initial_feed_rate_kg_h=0.0,
            initial_moisture_pct=12.0,
        )
        self.mpc = ModelPredictiveController(dt_sec=dt_sec, initial_u=80.0)
        self.flight_recorder = FlightRecorder()

        self.mitigation_timer_sec = 0.0
        self.pulse_jet_active = False

    def reset(self, initial_temp_c: float = 120.0) -> None:
        """Reset supervisory agent and plant state."""
        self.current_state = PlantOperatingState.STARTUP_PREHEAT
        self.plant = DynamicBiomassReactor(
            initial_temp_c=initial_temp_c,
            initial_feed_rate_kg_h=0.0,
            initial_moisture_pct=12.0,
        )
        self.mpc.reset(initial_u=80.0)
        self.mitigation_timer_sec = 0.0
        self.pulse_jet_active = False

    def step(
        self,
        mission_phase: str = "AUTONOMOUS_OPERATION",
        moisture_override: Optional[float] = None,
        injected_fault: str = "none",
        target_temp_override: Optional[float] = None,
    ) -> Tuple[PlantDynamicState, AutopilotCommand]:
        """Execute one autonomous decision loop step."""
        target_sp = target_temp_override or self.target_cruise_temp_c
        current_temp = self.plant.temp_c
        moist = moisture_override if moisture_override is not None else self.plant.moisture_pct

        target_feed = self.nominal_feed_rate_kg_h
        action_desc = "NORMAL_CRUISE"
        active_alarm = "NORMAL"
        anomaly_score = 0.0
        n2_purge = False
        self.pulse_jet_active = False
        interlock_trip = False

        # --- FSM TRANSITION & CONTROL LOGIC ---

        # 1. STARTUP PREHEAT
        if self.current_state == PlantOperatingState.STARTUP_PREHEAT:
            target_feed = 0.0  # Infeed disabled during preheat
            n2_purge = True
            action_desc = "PREHEAT_BURNER_FIRING"

            if current_temp >= 480.0:
                self.current_state = PlantOperatingState.AUTONOMOUS_CRUISE
                action_desc = "TRANSITION_TO_CRUISE_FEED_START"
            u_cmd = 85.0  # High firing rate for rapid heating

        # 2. AUTONOMOUS CRUISE
        elif self.current_state == PlantOperatingState.AUTONOMOUS_CRUISE:
            target_feed = self.nominal_feed_rate_kg_h
            u_cmd = self.mpc.compute(setpoint=target_sp, current_pv=current_temp, dt_sec=self.dt_sec)
            action_desc = f"MPC_TRACKING_TARGET_{target_sp:.0f}C"

            # Check for disturbance (e.g. moisture > 18%)
            if moist >= 18.0:
                self.current_state = PlantOperatingState.DISTURBANCE_ADAPTATION
                action_desc = "DETECTED_MOISTURE_SURGE_ADAPTING"

            # Check for injected fault
            if injected_fault.lower() == "cyclone_blockage":
                self.current_state = PlantOperatingState.FAULT_MITIGATION
                self.mitigation_timer_sec = 0.0
                self.pulse_jet_active = True
                action_desc = "CYCLONE_DIPLEG_ANOMALY_TRIGGERING_PULSE_JET"
                anomaly_score = 0.88
                active_alarm = "WARNING"
            elif injected_fault.lower() == "thermal_runaway" and current_temp > 630.0:
                self.current_state = PlantOperatingState.EMERGENCY_SAFE_PARK
                action_desc = "THERMAL_RUNAWAY_CRITICAL_SIL2_INTERLOCK"
                anomaly_score = 0.98
                active_alarm = "CRITICAL_EMERGENCY"

        # 3. DISTURBANCE ADAPTATION
        elif self.current_state == PlantOperatingState.DISTURBANCE_ADAPTATION:
            # Throttle feed slightly (85 kg/h) to maintain thermal self-sufficiency
            target_feed = 85.0
            u_cmd = self.mpc.compute(setpoint=target_sp, current_pv=current_temp, dt_sec=self.dt_sec)
            action_desc = "FEED_THROTTLED_FOR_WET_BIOMASS"

            if moist < 16.0 and abs(current_temp - target_sp) <= 3.0:
                self.current_state = PlantOperatingState.AUTONOMOUS_CRUISE
                action_desc = "DISTURBANCE_RECOVERED_RETURNING_TO_CRUISE"

        # 4. FAULT MITIGATION
        elif self.current_state == PlantOperatingState.FAULT_MITIGATION:
            self.mitigation_timer_sec += self.dt_sec
            self.pulse_jet_active = True
            target_feed = 70.0  # Reduced feed rate
            u_cmd = 65.0
            action_desc = f"PULSE_JET_NITROGEN_BLOWBACK_ACTIVE ({self.mitigation_timer_sec:.0f}s)"
            anomaly_score = max(0.0, 0.88 - (self.mitigation_timer_sec / 40.0) * 0.80)
            active_alarm = "WARNING" if anomaly_score > 0.3 else "NORMAL"

            if self.mitigation_timer_sec >= 40.0:
                self.pulse_jet_active = False
                self.current_state = PlantOperatingState.AUTONOMOUS_CRUISE
                action_desc = "CYCLONE_CLEARED_RETURNING_TO_CRUISE"

        # 5. EMERGENCY SAFE PARK
        elif self.current_state == PlantOperatingState.EMERGENCY_SAFE_PARK:
            target_feed = 0.0
            u_cmd = 0.0
            n2_purge = True
            interlock_trip = True
            action_desc = "NFPA86_INERT_NITROGEN_COOLING_SWEEP"
            active_alarm = "CRITICAL_EMERGENCY"
            anomaly_score = 0.95

        # Execute plant step
        plant_state = self.plant.step(
            control_input_pct=u_cmd,
            target_feed_rate_kg_h=target_feed,
            moisture_override=moist,
            dt_sec=self.dt_sec,
        )

        command = AutopilotCommand(
            fsm_state=self.current_state,
            target_temp_c=target_sp,
            target_feed_rate_kg_h=target_feed,
            burner_duty_pct=u_cmd,
            nitrogen_purge_active=n2_purge,
            pulse_jet_active=self.pulse_jet_active,
            safety_interlock_tripped=interlock_trip,
            action_summary=action_desc,
        )

        # Log into blackbox flight recorder
        self.flight_recorder.record_step(
            timestamp_sec=plant_state.time_sec,
            mission_phase=mission_phase,
            fsm_state=self.current_state.value,
            reactor_temp_c=plant_state.reactor_temp_c,
            target_temp_c=target_sp,
            feed_rate_kg_h=plant_state.feed_rate_kg_h,
            moisture_pct=plant_state.moisture_pct,
            burner_duty_pct=u_cmd,
            tsi_pct=plant_state.tsi_pct,
            anomaly_score=anomaly_score,
            active_alarm=active_alarm,
            action_taken=action_desc,
        )

        return plant_state, command
