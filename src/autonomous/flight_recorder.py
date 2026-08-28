"""High-resolution Blackbox Flight Recorder and telemetry historian.

Logs state transitions, soft sensor inferences, anomaly scores, controller moves,
and safety actions during autonomous operations.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional


@dataclass
class FlightLogEntry:
    """Discrete flight telemetry snapshot."""
    timestamp_sec: float
    time_min: float
    mission_phase: str
    fsm_state: str
    reactor_temp_c: float
    target_temp_c: float
    feed_rate_kg_h: float
    moisture_pct: float
    burner_duty_pct: float
    tsi_pct: float
    anomaly_score: float
    active_alarm: str
    action_taken: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp_sec": round(self.timestamp_sec, 1),
            "time_min": round(self.time_min, 2),
            "mission_phase": self.mission_phase,
            "fsm_state": self.fsm_state,
            "reactor_temp_c": round(self.reactor_temp_c, 2),
            "target_temp_c": round(self.target_temp_c, 2),
            "feed_rate_kg_h": round(self.feed_rate_kg_h, 2),
            "moisture_pct": round(self.moisture_pct, 2),
            "burner_duty_pct": round(self.burner_duty_pct, 2),
            "tsi_pct": round(self.tsi_pct, 1),
            "anomaly_score": round(self.anomaly_score, 4),
            "active_alarm": self.active_alarm,
            "action_taken": self.action_taken,
        }


class FlightRecorder:
    """Blackbox telemetry recorder maintaining historical flight trajectory logs."""

    def __init__(self, max_entries: int = 10000) -> None:
        self.max_entries = max_entries
        self.entries: List[FlightLogEntry] = []
        self.events: List[Dict[str, Any]] = []

    def record_step(
        self,
        timestamp_sec: float,
        mission_phase: str,
        fsm_state: str,
        reactor_temp_c: float,
        target_temp_c: float,
        feed_rate_kg_h: float,
        moisture_pct: float,
        burner_duty_pct: float,
        tsi_pct: float,
        anomaly_score: float = 0.0,
        active_alarm: str = "NORMAL",
        action_taken: str = "STEADY_TRACKING",
    ) -> FlightLogEntry:
        """Append telemetry snapshot to blackbox log."""
        entry = FlightLogEntry(
            timestamp_sec=timestamp_sec,
            time_min=timestamp_sec / 60.0,
            mission_phase=mission_phase,
            fsm_state=fsm_state,
            reactor_temp_c=reactor_temp_c,
            target_temp_c=target_temp_c,
            feed_rate_kg_h=feed_rate_kg_h,
            moisture_pct=moisture_pct,
            burner_duty_pct=burner_duty_pct,
            tsi_pct=tsi_pct,
            anomaly_score=anomaly_score,
            active_alarm=active_alarm,
            action_taken=action_taken,
        )
        if len(self.entries) >= self.max_entries:
            self.entries.pop(0)
        self.entries.append(entry)

        if active_alarm != "NORMAL" or "TRANSITION" in action_taken or "MITIGATION" in action_taken:
            self.events.append({
                "timestamp_sec": round(timestamp_sec, 1),
                "time_min": round(timestamp_sec / 60.0, 2),
                "fsm_state": fsm_state,
                "alarm": active_alarm,
                "action": action_taken,
            })

        return entry

    def export_json(self, file_path: Optional[str] = None) -> Path:
        """Export full flight recording to JSON file."""
        out = (
            Path(file_path)
            if file_path
            else Path(__file__).resolve().parent.parent.parent / "reports" / "autonomous_flight_log.json"
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "flight_recorder_version": "2.0.0",
            "total_recorded_points": len(self.entries),
            "total_flight_duration_min": round(self.entries[-1].time_min, 2) if self.entries else 0.0,
            "critical_events_count": len(self.events),
            "critical_events": self.events,
            "telemetry_stream": [e.to_dict() for e in self.entries[::2]],  # 50% subsampled for disk efficiency
        }
        with open(out, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return out
