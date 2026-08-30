"""3D Spatial Plant Geometry, Component Topology, and Flow Conduit Graph Generator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class SpatialComponentNode:
    """Represents a 3D equipment asset with bounding coordinates, dimensions, and telemetry binding."""
    id: str
    name: str
    category: str  # "VESSEL", "CYCLONE", "HEAT_EXCHANGER", "HOPPER", "BURNER"
    position: List[float]  # [x, y, z] in meters
    dimensions: List[float]  # [width, height, depth] or [radius, height, 0]
    color_hex: str
    telemetry_tag: str
    description: str


class PlantSpatialModel:
    """Generates the structured 3D spatial twin asset hierarchy for Three.js WebGL visualization."""

    def __init__(self):
        self.components: List[SpatialComponentNode] = [
            SpatialComponentNode(
                id="IN_HOPPER_101",
                name="Biomass Infeed Silo & Metering Screw",
                category="HOPPER",
                position=[-4.0, 1.8, 0.0],
                dimensions=[1.2, 2.4, 1.2],
                color_hex="#8b5a2b",
                telemetry_tag="FT-101 (100 kg/h)",
                description="Hermetic biomass hopper with variable-speed metering screw feeder.",
            ),
            SpatialComponentNode(
                id="REACTOR_R101",
                name="Fluidized Bed Fast Pyrolysis Reactor",
                category="VESSEL",
                position=[0.0, 2.6, 0.0],
                dimensions=[1.4, 3.8, 1.4],
                color_hex="#00f0ff",
                telemetry_tag="TI-103 (500.0 °C)",
                description="Thermochemical conversion reactor with continuous nitrogen fluidization.",
            ),
            SpatialComponentNode(
                id="BURNER_B101",
                name="Recycled Syngas Fired Combustor",
                category="BURNER",
                position=[0.0, 0.4, 0.0],
                dimensions=[1.6, 1.0, 1.6],
                color_hex="#ff0055",
                telemetry_tag="BURNER (45% Firing)",
                description="External jacket combustor utilizing non-condensable syngas for process heat.",
            ),
            SpatialComponentNode(
                id="CYCLONE_CY101",
                name="High-Efficiency Separation Cyclone",
                category="CYCLONE",
                position=[2.8, 3.2, 0.0],
                dimensions=[0.9, 2.6, 0.9],
                color_hex="#ffb800",
                telemetry_tag="PI-102 (12.5 mbar)",
                description="Centrifugal separation cyclone recovering solid biochar particulates.",
            ),
            SpatialComponentNode(
                id="BIOCHAR_BIN_101",
                name="Biochar Inert Quench & Collection Silo",
                category="HOPPER",
                position=[2.8, 0.6, 0.0],
                dimensions=[1.0, 1.4, 1.0],
                color_hex="#333333",
                telemetry_tag="RUL (100% Health)",
                description="Water-cooled biochar receptacle with nitrogen purge barrier.",
            ),
            SpatialComponentNode(
                id="CONDENSER_HX102",
                name="Shell-and-Tube Bio-Oil Condenser",
                category="HEAT_EXCHANGER",
                position=[5.2, 2.0, 0.0],
                dimensions=[1.1, 3.2, 1.1],
                color_hex="#00ff88",
                telemetry_tag="TI-104 (45.0 °C)",
                description="Two-stage direct contact fractional condenser quenching pyrolysis vapors.",
            ),
        ]

        self.flow_conduits = [
            {"from": "IN_HOPPER_101", "to": "REACTOR_R101", "medium": "Solid Biomass Feed", "color": "#e0a96d"},
            {"from": "REACTOR_R101", "to": "CYCLONE_CY101", "medium": "Vapor & Char Stream", "color": "#00f0ff"},
            {"from": "CYCLONE_CY101", "to": "BIOCHAR_BIN_101", "medium": "Solid Biochar", "color": "#ffb800"},
            {"from": "CYCLONE_CY101", "to": "CONDENSER_HX102", "medium": "Clean Pyrolysis Vapors", "color": "#00f0ff"},
            {"from": "CONDENSER_HX102", "to": "BURNER_B101", "medium": "Recycled Syngas Fuel", "color": "#ff0055"},
        ]

    def export_spatial_graph(self) -> Dict[str, Any]:
        """Export full 3D spatial hierarchy and coordinate anchors for Three.js rendering."""
        return {
            "coordinate_system": "Y_UP_RIGHT_HANDED",
            "unit": "meters",
            "bounding_box": {"min": [-6.0, 0.0, -3.0], "max": [7.0, 6.0, 3.0]},
            "camera_default": {"position": [0.0, 4.0, 10.0], "target": [0.5, 2.0, 0.0]},
            "nodes": [
                {
                    "id": c.id,
                    "name": c.name,
                    "category": c.category,
                    "position": c.position,
                    "dimensions": c.dimensions,
                    "color_hex": c.color_hex,
                    "telemetry_tag": c.telemetry_tag,
                    "description": c.description,
                }
                for c in self.components
            ],
            "conduits": self.flow_conduits,
        }
