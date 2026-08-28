"""CLI interface and real-time virtual gauge dashboard for industrial soft sensors.

Usage:
    python -m src.sensors.run_soft_sensors --temp 520 --feed-rate 100
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from src.simulation.plant_simulator import BiomassPlantSimulator
from src.sensors.telemetry import TelemetryExtractor, HardwareTelemetryPacket
from src.sensors.soft_sensor_engine import SoftSensorSuite, SoftSensorEstimate


def print_soft_sensor_dashboard(
    telemetry: HardwareTelemetryPacket,
    estimates: Dict[str, SoftSensorEstimate],
) -> None:
    """Format and print real-time inferential sensor dashboard to stdout."""
    w = 78
    border = "=" * w
    sub_border = "-" * w

    print(f"\n{border}")
    print(f"       AI-INTEGRATED BIOMASS CONVERSION PLANT - V0.7")
    print(f"    (Industrial Soft Sensor Suite & 95% Uncertainty Quantification)")
    print(f"{border}")
    print(f"Timestamp            : {telemetry.timestamp}")
    print(f"Feedstock Assumed    : {telemetry.feedstock_name}")

    print(f"\nONLINE HARDWARE INSTRUMENT TELEMETRY (Physical Sensors)")
    print(f"{sub_border}")
    print(f"  TI-101 (Dryer Inlet Temp)     : {telemetry.TI_101:6.1f} °C   | FI-101 (Biomass Feed Rate)   : {telemetry.FI_101:6.1f} kg/h")
    print(f"  TI-102 (Dryer Exit Temp)      : {telemetry.TI_102:6.1f} °C   | FI-102 (Cooling Water Rate)  : {telemetry.FI_102:6.1f} kg/h")
    print(f"  TI-103 (Reactor Bed Temp)     : {telemetry.TI_103:6.1f} °C   | FI-103 (Combustion Air Rate) : {telemetry.FI_103:6.1f} kg/h")
    print(f"  TI-104 (Cyclone Vapor Temp)   : {telemetry.TI_104:6.1f} °C   | PI-101 (Bed Delta Pressure)  : {telemetry.PI_101:6.2f} kPa")
    print(f"  TI-105 (Condenser Gas Temp)   : {telemetry.TI_105:6.1f} °C   | TI-106 (Flue Gas Temp)       : {telemetry.TI_106:6.1f} °C")

    print(f"\nINFERENTIAL SOFT SENSORS (Real-Time Virtual State Estimation)")
    print(f"{sub_border}")
    print(f"{'Tag':<10} {'Stream Property':<30} {'Estimate':<10} {'95% Pred Interval':<20} {'Status'}")
    print(f"{sub_border}")

    for tag, est in estimates.items():
        ci_str = f"[{est.lower_95_ci:.2f} - {est.upper_95_ci:.2f}]"
        val_str = f"{est.point_estimate:.2f} {est.unit}"
        print(f"{tag:<10} {est.name:<30} {val_str:<10} {ci_str:<20} {est.health_status}")

    print(f"{border}\n")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Industrial Soft Sensor Live Dashboard")
    parser.add_argument("--feedstock", type=str, default="pine_sawdust", help="Biomass feedstock name")
    parser.add_argument("--feed-rate", type=float, default=100.0, help="Wet feed rate (kg/h)")
    parser.add_argument("--temp", type=float, default=500.0, help="Reactor bed temperature (°C)")
    parser.add_argument("--json", action="store_true", help="Print JSON telemetry and estimates")
    args = parser.parse_args()

    # 1. Run simulation to extract hardware telemetry
    sim = BiomassPlantSimulator()
    rep = sim.run_simulation(
        feedstock_name=args.feedstock,
        feed_rate_kg_h=args.feed_rate,
        reactor_temp_c=args.temp,
    )
    telemetry = TelemetryExtractor.extract_from_report(rep, add_sensor_noise=True)

    # 2. Load trained soft sensors
    chk_path = Path(__file__).resolve().parent.parent.parent / "models" / "checkpoints" / "soft_sensors.joblib"
    if not chk_path.is_file():
        from src.sensors.calibration import SoftSensorCalibrator
        print("[*] Soft sensor checkpoint not found. Calibrating now...")
        SoftSensorCalibrator().calibrate()

    suite = SoftSensorSuite.load(chk_path)
    estimates = suite.estimate_all(telemetry)

    if args.json:
        payload = {
            "telemetry": telemetry.to_dict(),
            "estimates": {k: v.to_dict() for k, v in estimates.items()},
        }
        print(json.dumps(payload, indent=2))
    else:
        print_soft_sensor_dashboard(telemetry, estimates)


if __name__ == "__main__":
    main()
