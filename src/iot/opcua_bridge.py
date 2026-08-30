"""OPC-UA (IEC 62541) Address Space Model and Node Tree Bridge."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class OPCUANode:
    """Represents an individual node in the OPC-UA information model."""
    node_id: str
    browse_name: str
    display_name: str
    node_class: str  # "Object", "Variable", "Method"
    data_type: Optional[str] = None  # "Double", "Boolean", "String", "Int32"
    value: Any = None
    access_level: str = "CurrentRead"  # "CurrentRead", "CurrentRead | CurrentWrite"
    engineering_unit: str = ""
    eu_range_min: float = 0.0
    eu_range_max: float = 1000.0
    children: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "nodeId": self.node_id,
            "browseName": self.browse_name,
            "displayName": self.display_name,
            "nodeClass": self.node_class,
        }
        if self.node_class == "Variable":
            d.update({
                "dataType": self.data_type,
                "value": self.value,
                "accessLevel": self.access_level,
                "engineeringUnit": self.engineering_unit,
                "euRange": [self.eu_range_min, self.eu_range_max],
            })
        if self.children:
            d["children"] = self.children
        return d


class OPCUAAddressSpace:
    """Manages the hierarchical OPC-UA address space for BIOPLANT AI."""

    def __init__(self, namespace_uri: str = "http://bioplant.ai/opcua/v2/"):
        self.namespace_uri = namespace_uri
        self.namespace_index = 2
        self.nodes: Dict[str, OPCUANode] = {}
        self._build_standard_address_space()

    def _build_standard_address_space(self) -> None:
        """Construct the hierarchical industrial plant node hierarchy."""
        # Root & Main Object Nodes
        self.add_node(OPCUANode("ns=2;s=BioPlant", "BioPlant", "BioPlant Digital Twin Platform", "Object", children=[
            "ns=2;s=BioPlant.ProcessData",
            "ns=2;s=BioPlant.Setpoints",
            "ns=2;s=BioPlant.SoftSensors",
            "ns=2;s=BioPlant.Alarms",
            "ns=2;s=BioPlant.Methods",
        ]))

        # 1. ProcessData Object & Variables
        self.add_node(OPCUANode("ns=2;s=BioPlant.ProcessData", "ProcessData", "Real-Time Telemetry", "Object", children=[
            "ns=2;s=BioPlant.ProcessData.ReactorTemp",
            "ns=2;s=BioPlant.ProcessData.BiomassFeedRate",
            "ns=2;s=BioPlant.ProcessData.CyclonePressureDrop",
            "ns=2;s=BioPlant.ProcessData.ThermalSelfSufficiency",
        ]))
        self.add_node(OPCUANode("ns=2;s=BioPlant.ProcessData.ReactorTemp", "ReactorTemp", "TI-103 Reactor Core Temperature", "Variable", "Double", 500.0, "CurrentRead", "°C", 0.0, 1200.0))
        self.add_node(OPCUANode("ns=2;s=BioPlant.ProcessData.BiomassFeedRate", "BiomassFeedRate", "FT-101 Biomass Infeed Rate", "Variable", "Double", 100.0, "CurrentRead", "kg/h", 0.0, 1000.0))
        self.add_node(OPCUANode("ns=2;s=BioPlant.ProcessData.CyclonePressureDrop", "CyclonePressureDrop", "PI-102 Cyclone Diff Pressure", "Variable", "Double", 12.5, "CurrentRead", "mbar", 0.0, 100.0))
        self.add_node(OPCUANode("ns=2;s=BioPlant.ProcessData.ThermalSelfSufficiency", "ThermalSelfSufficiency", "TSI Energy Self Sufficiency", "Variable", "Double", 114.5, "CurrentRead", "%", 0.0, 300.0))

        # 2. Setpoints Object & Variables (Read/Write)
        self.add_node(OPCUANode("ns=2;s=BioPlant.Setpoints", "Setpoints", "Supervisory Setpoints", "Object", children=[
            "ns=2;s=BioPlant.Setpoints.TemperatureTarget",
            "ns=2;s=BioPlant.Setpoints.FeedRateTarget",
        ]))
        self.add_node(OPCUANode("ns=2;s=BioPlant.Setpoints.TemperatureTarget", "TemperatureTarget", "Reactor Temperature Setpoint", "Variable", "Double", 500.0, "CurrentRead | CurrentWrite", "°C", 200.0, 800.0))
        self.add_node(OPCUANode("ns=2;s=BioPlant.Setpoints.FeedRateTarget", "FeedRateTarget", "Biomass Feed Rate Setpoint", "Variable", "Double", 100.0, "CurrentRead | CurrentWrite", "kg/h", 10.0, 500.0))

        # 3. SoftSensors Object & Variables
        self.add_node(OPCUANode("ns=2;s=BioPlant.SoftSensors", "SoftSensors", "Inferential Soft Sensor Suite (95% UQ)", "Object", children=[
            "ns=2;s=BioPlant.SoftSensors.BioOilTAN",
            "ns=2;s=BioPlant.SoftSensors.BioOilMoisture",
            "ns=2;s=BioPlant.SoftSensors.SyngasLHV",
        ]))
        self.add_node(OPCUANode("ns=2;s=BioPlant.SoftSensors.BioOilTAN", "BioOilTAN", "Inferential Total Acid Number", "Variable", "Double", 82.4, "CurrentRead", "mg KOH/g", 0.0, 200.0))
        self.add_node(OPCUANode("ns=2;s=BioPlant.SoftSensors.BioOilMoisture", "BioOilMoisture", "Inferential Bio-Oil Moisture", "Variable", "Double", 21.3, "CurrentRead", "wt%", 0.0, 50.0))
        self.add_node(OPCUANode("ns=2;s=BioPlant.SoftSensors.SyngasLHV", "SyngasLHV", "Inferential Syngas Lower Heating Value", "Variable", "Double", 14.8, "CurrentRead", "MJ/Nm3", 0.0, 30.0))

        # 4. Alarms Object
        self.add_node(OPCUANode("ns=2;s=BioPlant.Alarms", "Alarms", "SIL-2 Safety Alarms", "Object", children=[
            "ns=2;s=BioPlant.Alarms.SIL2InterlockTripped",
            "ns=2;s=BioPlant.Alarms.CycloneClogged",
        ]))
        self.add_node(OPCUANode("ns=2;s=BioPlant.Alarms.SIL2InterlockTripped", "SIL2InterlockTripped", "Emergency SIL-2 Safety Trip Active", "Variable", "Boolean", False, "CurrentRead"))
        self.add_node(OPCUANode("ns=2;s=BioPlant.Alarms.CycloneClogged", "CycloneClogged", "Cyclone Dipleg Obstruction Detected", "Variable", "Boolean", False, "CurrentRead"))

        # 5. Methods Object
        self.add_node(OPCUANode("ns=2;s=BioPlant.Methods", "Methods", "Executable Remote Procedure Calls", "Object", children=[
            "ns=2;s=BioPlant.Methods.TriggerPulseJet",
            "ns=2;s=BioPlant.Methods.ResetSafetyAlarms",
        ]))
        self.add_node(OPCUANode("ns=2;s=BioPlant.Methods.TriggerPulseJet", "TriggerPulseJet", "Execute Nitrogen Blowback Pulse-Jet", "Method"))
        self.add_node(OPCUANode("ns=2;s=BioPlant.Methods.ResetSafetyAlarms", "ResetSafetyAlarms", "Acknowledge and Clear Safety Interlocks", "Method"))

    def add_node(self, node: OPCUANode) -> None:
        """Register a node in the address space."""
        self.nodes[node.node_id] = node

    def get_node(self, node_id: str) -> Optional[OPCUANode]:
        """Retrieve node by NodeId."""
        return self.nodes.get(node_id)

    def write_variable(self, node_id: str, value: Any) -> None:
        """Update node variable value."""
        node = self.nodes.get(node_id)
        if not node:
            raise KeyError(f"NodeId '{node_id}' not found in OPC-UA address space.")
        if node.node_class != "Variable":
            raise ValueError(f"Cannot write value to node '{node_id}' of class '{node.node_class}'.")
        node.value = value

    def update_from_telemetry(self, telemetry: Dict[str, Any]) -> None:
        """Synchronize OPC-UA process variables with latest telemetry."""
        if "reactor_temp_c" in telemetry:
            self.write_variable("ns=2;s=BioPlant.ProcessData.ReactorTemp", float(telemetry["reactor_temp_c"]))
        if "feed_rate_kg_h" in telemetry:
            self.write_variable("ns=2;s=BioPlant.ProcessData.BiomassFeedRate", float(telemetry["feed_rate_kg_h"]))
        if "tsi_pct" in telemetry:
            self.write_variable("ns=2;s=BioPlant.ProcessData.ThermalSelfSufficiency", float(telemetry["tsi_pct"]))
        if "cyclone_dp_mbar" in telemetry:
            self.write_variable("ns=2;s=BioPlant.ProcessData.CyclonePressureDrop", float(telemetry["cyclone_dp_mbar"]))

    def export_address_space_tree(self) -> Dict[str, Any]:
        """Export full address space tree structure for client visualization."""
        return {
            "server_uri": "opc.tcp://127.0.0.1:4840/bioplant/server/",
            "namespace": self.namespace_uri,
            "namespace_index": self.namespace_index,
            "nodes_count": len(self.nodes),
            "nodes": {nid: n.to_dict() for nid, n in self.nodes.items()},
        }
