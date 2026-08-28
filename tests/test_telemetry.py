"""Unit tests for HardwareTelemetryPacket and TelemetryExtractor."""

import pytest
from src.data.feedstock import BiomassFeedstock
from src.simulation.plant_simulator import BiomassPlantSimulator
from src.sensors.telemetry import TelemetryExtractor, HardwareTelemetryPacket


def test_telemetry_extraction_from_simulation(plant_simulator: BiomassPlantSimulator) -> None:
    """Verify hardware sensor telemetry packet is correctly extracted with noise."""
    report = plant_simulator.run_simulation(feedstock_name="olive_pomace", feed_rate_kg_h=100.0)
    packet = TelemetryExtractor.extract_from_report(report, add_sensor_noise=True, random_seed=42)

    assert isinstance(packet, HardwareTelemetryPacket)
    assert packet.feedstock_name == "Olive Pomace"
    assert 400.0 <= packet.TI_103 <= 600.0  # Reactor bed temp
    assert 50.0 <= packet.FI_101 <= 150.0   # Feed rate
    assert packet.PI_101 > 0.0              # Delta P

    vec = packet.to_feature_vector()
    assert vec.shape == (10,)
    assert len(packet.to_dict()) >= 10
