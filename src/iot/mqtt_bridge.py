"""MQTT Sparkplug B Operational Edge Protocol Bridge and Payload Formatter."""

from __future__ import annotations

import time
import json
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class SparkplugMetric:
    """Sparkplug B compliant metric item."""
    name: str
    value: Any
    data_type: str
    eng_unit: str = ""
    timestamp_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "dataType": self.data_type,
            "timestamp": self.timestamp_ms,
            "properties": {"engUnit": self.eng_unit} if self.eng_unit else {},
        }


@dataclass
class SparkplugBPayload:
    """Sparkplug B payload container."""
    timestamp_ms: int
    seq_number: int
    metrics: List[SparkplugMetric]

    def to_json(self) -> str:
        return json.dumps({
            "timestamp": self.timestamp_ms,
            "seq": self.seq_number,
            "metrics": [m.to_dict() for m in self.metrics],
        }, indent=2)


class MQTTOperationalBridge:
    """Simulates an industrial MQTT Sparkplug B edge broker bridge."""

    def __init__(self, group_id: str = "BiomassRecycling", edge_node_id: str = "BioPlant_Edge_01", device_id: str = "Pyrolysis_Reactor_Unit"):
        self.group_id = group_id
        self.edge_node_id = edge_node_id
        self.device_id = device_id
        self._seq = 0
        self._is_connected = True
        self._last_published_payload: Optional[Dict[str, Any]] = None

    def get_topic(self, message_type: str) -> str:
        """Construct standard Sparkplug B topic path: spBv1.0/group/msg_type/node/device."""
        return f"spBv1.0/{self.group_id}/{message_type}/{self.edge_node_id}/{self.device_id}"

    def build_dbirth_payload(self, current_telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Device Birth (DBIRTH) certificate defining all published telemetry metrics."""
        self._seq = 0
        metrics = [
            SparkplugMetric("Process/ReactorTemp", float(current_telemetry.get("reactor_temp_c", 500.0)), "Float", "°C"),
            SparkplugMetric("Process/FeedRate", float(current_telemetry.get("feed_rate_kg_h", 100.0)), "Float", "kg/h"),
            SparkplugMetric("Process/TSI", float(current_telemetry.get("tsi_pct", 100.0)), "Float", "%"),
            SparkplugMetric("Sensors/CycloneDP", float(current_telemetry.get("cyclone_dp_mbar", 12.5)), "Float", "mbar"),
            SparkplugMetric("Alarms/FaultActive", bool(current_telemetry.get("fault_active", False)), "Boolean"),
            SparkplugMetric("Actuators/PulseJetState", bool(current_telemetry.get("pulse_jet_active", False)), "Boolean"),
            SparkplugMetric("System/FSMState", str(current_telemetry.get("fsm_state", "AUTONOMOUS_CRUISE")), "String"),
        ]
        payload = SparkplugBPayload(
            timestamp_ms=int(time.time() * 1000),
            seq_number=self._seq,
            metrics=metrics,
        )
        data = {
            "topic": self.get_topic("DBIRTH"),
            "qos": 1,
            "retain": True,
            "payload": json.loads(payload.to_json()),
        }
        self._last_published_payload = data
        return data

    def build_ddata_payload(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Generate periodic telemetry update (DDATA) payload."""
        self._seq = (self._seq + 1) % 256
        metrics = [
            SparkplugMetric("Process/ReactorTemp", float(telemetry.get("reactor_temp_c", 500.0)), "Float", "°C"),
            SparkplugMetric("Process/FeedRate", float(telemetry.get("feed_rate_kg_h", 100.0)), "Float", "kg/h"),
            SparkplugMetric("Process/TSI", float(telemetry.get("tsi_pct", 100.0)), "Float", "%"),
            SparkplugMetric("Sensors/CycloneDP", float(telemetry.get("cyclone_dp_mbar", 12.5)), "Float", "mbar"),
            SparkplugMetric("Actuators/PulseJetState", bool(telemetry.get("pulse_jet_active", False)), "Boolean"),
            SparkplugMetric("System/FSMState", str(telemetry.get("fsm_state", "AUTONOMOUS_CRUISE")), "String"),
        ]
        payload = SparkplugBPayload(
            timestamp_ms=int(time.time() * 1000),
            seq_number=self._seq,
            metrics=metrics,
        )
        data = {
            "topic": self.get_topic("DDATA"),
            "qos": 0,
            "retain": False,
            "payload": json.loads(payload.to_json()),
        }
        self._last_published_payload = data
        return data

    def handle_ncmd(self, command_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process received Node Command (NCMD) payload (e.g. setpoint updates, pulse-jet trigger)."""
        metrics = command_payload.get("metrics", [])
        executed_commands = []
        for m in metrics:
            name = m.get("name")
            val = m.get("value")
            executed_commands.append(f"Applied {name} = {val}")

        return {
            "status": "COMMANDS_ACKNOWLEDGED",
            "topic": self.get_topic("NCMD"),
            "timestamp": int(time.time() * 1000),
            "executed_commands": executed_commands,
        }

    def get_bridge_status(self) -> Dict[str, Any]:
        """Return operational status of MQTT broker bridge."""
        return {
            "connected": self._is_connected,
            "broker_host": "mqtt.bioplant-edge.local",
            "broker_port": 1883,
            "sparkplug_spec": "spBv1.0",
            "group_id": self.group_id,
            "node_id": self.edge_node_id,
            "device_id": self.device_id,
            "current_seq": self._seq,
            "last_payload": self._last_published_payload,
        }
