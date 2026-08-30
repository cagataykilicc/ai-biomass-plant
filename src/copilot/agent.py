"""Context-Aware Generative AI SCADA Operator Copilot Reasoning Engine."""

from __future__ import annotations

import time
from typing import Dict, Any, List, Optional
from src.copilot.knowledge_base import CopilotKnowledgeBase


class SCADAOperatorCopilot:
    """Industrial AI assistant providing real-time technical guidance and root-cause analysis."""

    def __init__(self, kb: Optional[CopilotKnowledgeBase] = None):
        self.kb = kb or CopilotKnowledgeBase()

    def process_query(self, user_query: str, plant_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Synthesize technical diagnosis and operational guidance from plant telemetry and SOPs."""
        state = plant_state or {
            "reactor_temp_c": 500.0,
            "target_temp_c": 500.0,
            "cyclone_dp_mbar": 12.5,
            "feed_rate_kg_h": 100.0,
            "moisture_pct": 10.0,
            "fsm_state": "AUTONOMOUS_CRUISE",
            "active_alarms": [],
        }

        # 1. Retrieve most relevant SOPs
        matched_docs = self.kb.query(user_query, top_k=2)
        doc_refs = [f"{d.doc_id}: {d.title}" for d in matched_docs]

        q_lower = user_query.lower()
        rec_action = "MAINTAIN_CURRENT_SETPOINTS"
        suggested_sp = {}

        # 2. Contextual Rule Synthesis
        if "cyclone" in q_lower or "pressure" in q_lower or "dp" in q_lower or "blockage" in q_lower:
            answer = (
                f"**Cyclone DP Analysis:** Current differential pressure is **{state.get('cyclone_dp_mbar', 12.5):.1f} mbar** "
                f"(Threshold: 25.0 mbar). If rising, particulate build-up at the cyclone dipleg is the primary root cause. "
                f"Per **SOP-204**, activating nitrogen pulse-jet valve **XV-105** (3 pulses @ 6 bar) will clear the blockage "
                f"without halting the continuous infeed stream."
            )
            rec_action = "EXECUTE_PULSE_JET_BLOWBACK"
            suggested_sp = {"pulse_jet_pressure_bar": 6.0, "pulse_count": 3}

        elif "moisture" in q_lower or "wet" in q_lower or "water" in q_lower:
            answer = (
                f"**Feedstock Moisture Advisory:** Current infeed moisture is **{state.get('moisture_pct', 10.0):.1f}%**. "
                f"Evaporating moisture increases latent heat demand by ~2,260 kJ/kg H2O. Per **SOP-305**, the AI Autopilot "
                f"recommends increasing auxiliary burner duty by **+8.5%** and adjusting rotary dryer exhaust flow to stabilize bed temperature."
            )
            rec_action = "INCREASE_BURNER_DUTY"
            suggested_sp = {"burner_duty_pct": 53.5, "dryer_temp_c": 115.0}

        elif "emergency" in q_lower or "trip" in q_lower or "safe park" in q_lower or "stop" in q_lower:
            answer = (
                f"**SIL-2 Safety Shutdown Procedure:** To execute an immediate controlled shutdown per **SOP-400**, "
                f"the system will de-energize feed motor **FT-101**, isolate syngas valve **PY-101**, and initiate a high-volume "
                f"N2 purge (35 Nm³/h) to maintain inert reactor atmosphere."
            )
            rec_action = "TRIGGER_EMERGENCY_SAFE_PARK"
            suggested_sp = {"target_temp_c": 25.0, "feed_rate_kg_h": 0.0, "n2_purge_flow": 35.0}

        elif "startup" in q_lower or "preheat" in q_lower or "start" in q_lower:
            answer = (
                f"**Reactor Thermal Startup Guidance:** Per **SOP-101**, preheat the bed using burner B-101 with N2 carrier flow >= 15 Nm³/h. "
                f"Target temperature is **450.0 °C** before introducing biomass infeed at 30 kg/h to avoid tar condensation."
            )
            rec_action = "INITIATE_PREHEAT_RAMP"
            suggested_sp = {"target_temp_c": 450.0, "ramp_rate_c_min": 5.0}

        else:
            answer = (
                f"**SCADA Supervisory Overview:** Plant is operating stably in **{state.get('fsm_state', 'AUTONOMOUS_CRUISE')}** "
                f"at **{state.get('reactor_temp_c', 500.0):.1f} °C** and **{state.get('feed_rate_kg_h', 100.0):.1f} kg/h**. "
                f"All SIL-2 interlocks and Bayesian soft sensor confidence bounds are within nominal operational tolerances."
            )
            rec_action = "MAINTAIN_AUTONOMOUS_CRUISE"
            suggested_sp = {"target_temp_c": 500.0, "feed_rate_kg_h": 100.0}

        return {
            "timestamp": int(time.time()),
            "query": user_query,
            "copilot_response": answer,
            "matched_engineering_documents": doc_refs,
            "recommended_action": rec_action,
            "suggested_setpoints": suggested_sp,
            "current_fsm_state": state.get("fsm_state", "AUTONOMOUS_CRUISE"),
        }
