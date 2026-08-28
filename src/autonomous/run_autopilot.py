"""CLI runner and mission operations dashboard for the Autonomous AI Biomass Plant.

Usage:
    python -m src.autonomous.run_autopilot --mission
    python -m src.autonomous.run_autopilot --quick-demo
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from src.autonomous.stress_test import AutonomousStressTestRunner


def print_mission_dashboard(report: Dict[str, Any]) -> None:
    """Print ANSI formatted autonomous flight qualification leaderboard."""
    w = 82
    border = "=" * w
    sub_border = "-" * w

    print(f"\n{border}")
    print(f"       AI-INTEGRATED BIOMASS CONVERSION PLANT - V2.0")
    print(f"     (Fully Autonomous AI Autopilot Mission Qualification)")
    print(f"{border}")
    print(f"Mission Title       : {report['mission_title']}")
    print(f"Total Flight Time   : {report['total_duration_hours']:.1f} Hours (240 Minutes)")
    print(f"Overall Mission     : [{report['overall_status']}]")

    print(f"\nMISSION PHASES FLIGHT TIMELINE")
    print(f"{sub_border}")
    print(f"{'Phase':<38} {'Window':<14} {'Temp Trange':<14} {'End FSM State'}")
    print(f"{sub_border}")

    for p in report["phases"]:
        t_range = f"{p['start_temp_c']:.0f} -> {p['end_temp_c']:.0f}°C"
        print(f"{p['phase_name']:<38} {p['time_window_min']:<14} {t_range:<14} [{p['fsm_state_at_end']}]")

    print(f"{sub_border}")
    print(f"Flight Recorder Log : {report['flight_recorder_log_path']}")
    print(f"{border}\n")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Autonomous Autopilot Mission Qualification (V2.0)")
    parser.add_argument("--mission", action="store_true", default=True, help="Execute full 4-hour qualification mission")
    parser.add_argument("--dt", type=float, default=2.0, help="Simulation time step in seconds (default: 2.0)")
    parser.add_argument("--output", type=str, default=None, help="Output flight log path")
    args = parser.parse_args()

    runner = AutonomousStressTestRunner(dt_sec=args.dt)
    rep = runner.run_4hour_mission(export_path=args.output)
    print_mission_dashboard(rep)
    print(f"[OK] 4-Hour Autonomous Mission completed successfully.")


if __name__ == "__main__":
    main()
