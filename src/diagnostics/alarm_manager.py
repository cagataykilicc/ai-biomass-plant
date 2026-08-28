"""Industrial alarm management, severity triage, and automated safety mitigation protocols.

Dispatches actionable chemical engineering emergency procedures for diagnosed faults.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, Any, List, Optional

from src.diagnostics.fault_simulator import IndustrialFaultType
from src.diagnostics.anomaly_detector import AnomalyDetectionResult
from src.diagnostics.fault_diagnostics import DiagnosticClassificationResult


class AlarmPriority(str, Enum):
    """Industrial alarm severity levels."""
    NORMAL = "NORMAL"
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL_EMERGENCY = "CRITICAL_EMERGENCY"


@dataclass
class SafetyActionProtocol:
    """Actionable safety advisory and automated mitigation response."""
    alarm_id: str
    priority: AlarmPriority
    fault_type: IndustrialFaultType
    affected_equipment: str
    headline_message: str
    recommended_operator_action: str
    automated_interlock_action: str
    safety_standard_reference: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alarm_id": self.alarm_id,
            "priority": self.priority.value,
            "fault_type": self.fault_type.value,
            "affected_equipment": self.affected_equipment,
            "headline_message": self.headline_message,
            "recommended_operator_action": self.recommended_operator_action,
            "automated_interlock_action": self.automated_interlock_action,
            "safety_standard_reference": self.safety_standard_reference,
        }


class AlarmManager:
    """Evaluates process anomalies and generates prioritized alarm responses."""

    PROTOCOLS: Dict[IndustrialFaultType, Dict[str, Any]] = {
        IndustrialFaultType.NONE: {
            "priority": AlarmPriority.NORMAL,
            "headline": "Plant operating within nominal safety specifications.",
            "operator_action": "Continue regular shift monitoring.",
            "interlock_action": "None required.",
            "standard": "ISO 9001 Normal Operations",
        },
        IndustrialFaultType.CYCLONE_DIPLEG_BLOCKAGE: {
            "priority": AlarmPriority.WARNING,
            "headline": "Cyclone C101 Dipleg Blockage / Ash Bridge Detected",
            "operator_action": "Inspect cyclone sight glass. Actuate manual pneumatic knocker. Check char collection airlock.",
            "interlock_action": "Trigger automated high-pressure nitrogen pulse-jet knocker on cyclone dipleg cone.",
            "standard": "NFPA 652 Standard on the Fundamentals of Combustible Dust",
        },
        IndustrialFaultType.CONDENSER_TAR_FOULING: {
            "priority": AlarmPriority.WARNING,
            "headline": "Condenser Train HX102 Tube Fouling / Heat Transfer Loss",
            "operator_action": "Increase secondary chilled glycol flow. Prepare online solvent flush circuit.",
            "interlock_action": "Ramp cooling water circulation pump to 100% duty.",
            "standard": "TEMA Standards for Shell and Tube Heat Exchangers",
        },
        IndustrialFaultType.REACTOR_THERMAL_RUNAWAY: {
            "priority": AlarmPriority.CRITICAL_EMERGENCY,
            "headline": "CRITICAL: Pyrolysis Reactor R101 Thermal Excursion (>650°C)",
            "operator_action": "Immediate emergency shutdown (ESD). Evacuate unit perimeter. Verify nitrogen inerting.",
            "interlock_action": "Trip Emergency Starve: Stop biomass feed auger, open combustor flue bypass, inject continuous N2 purge.",
            "standard": "NFPA 86 Standard for Ovens and Furnaces / IEC 61508 SIL-2",
        },
        IndustrialFaultType.THERMOCOUPLE_SENSOR_DRIFT: {
            "priority": AlarmPriority.INFO,
            "headline": "Instrument Calibration Bias Detected on TI-103",
            "operator_action": "Dispatch I&C technician to inspect terminal connections and verify calibration with handheld calibrator.",
            "interlock_action": "Switch temperature control loop to redundant backup sensor TI-103B.",
            "standard": "ISA-75 Instrumentation Standards",
        },
        IndustrialFaultType.FEED_AUGER_JAMMING: {
            "priority": AlarmPriority.WARNING,
            "headline": "Biomass Feed Auger Conveyor A101 Jamming / Starvation",
            "operator_action": "Inspect feed hopper for tramp material, foreign metal, or oversized wood chunks.",
            "interlock_action": "Execute 3-second reverse auger unjamming cycle. If torque exceeds 150%, trip motor drive.",
            "standard": "CEMA Conveyor Equipment Safety Standards",
        },
    }

    @classmethod
    def evaluate_alarm(
        cls,
        anomaly_res: AnomalyDetectionResult,
        diagnostic_res: DiagnosticClassificationResult,
    ) -> SafetyActionProtocol:
        """Generate prioritized safety action protocol based on anomaly and diagnosis."""
        fault_type = diagnostic_res.predicted_fault
        proto_data = cls.PROTOCOLS.get(fault_type, cls.PROTOCOLS[IndustrialFaultType.NONE])

        # Escalate priority if overall anomaly score is severe
        priority = proto_data["priority"]
        if anomaly_res.overall_anomaly_score > 0.85 and priority == AlarmPriority.WARNING:
            priority = AlarmPriority.CRITICAL_EMERGENCY

        alarm_id = f"ALM-{fault_type.value[:6]}-{int(anomaly_res.overall_anomaly_score * 100):02d}"

        return SafetyActionProtocol(
            alarm_id=alarm_id,
            priority=priority,
            fault_type=fault_type,
            affected_equipment=diagnostic_res.affected_equipment_tag,
            headline_message=proto_data["headline"],
            recommended_operator_action=proto_data["operator_action"],
            automated_interlock_action=proto_data["interlock_action"],
            safety_standard_reference=proto_data["standard"],
        )
