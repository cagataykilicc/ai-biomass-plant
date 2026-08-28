"""CLI runner and terminal dashboard for dynamic process control simulation and benchmarking.

Usage:
    python -m src.control.run_control --controller mpc
    python -m src.control.run_control --benchmark
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from src.control.benchmark_control import ControlBenchmarkSuite, ControlBenchmarkMetrics


def print_benchmark_dashboard(report: Dict[str, Any]) -> None:
    """Print ANSI formatted control performance leaderboard."""
    w = 78
    border = "=" * w
    sub_border = "-" * w

    print(f"\n{border}")
    print(f"       AI-INTEGRATED BIOMASS CONVERSION PLANT - V1.1")
    print(f" (Dynamic Closed-Loop Process Control: Open-Loop vs PID vs MPC)")
    print(f"{border}")
    conds = report["test_conditions"]
    print(f"Simulation Horizon       : {conds['simulation_duration_sec'] / 60:.0f} Minutes (dt = {conds['dt_sec']:.1f}s)")
    print(f"Setpoint Step Profile    : {conds['setpoint_step_delta_c']}")
    print(f"Disturbance Profile      : {conds['moisture_disturbance_delta_pct']}")

    print(f"\nCONTROL PERFORMANCE BENCHMARK LEADERBOARD")
    print(f"{sub_border}")
    print(f"{'Controller':<14} {'IAE (°C·s)':<14} {'ITAE (°C·s²)':<16} {'Overshoot %':<14} {'Settling (s)'}")
    print(f"{sub_border}")

    for name, m in report["controllers"].items():
        print(f"{name:<14} {m['iae']:<14,.1f} {m['itae']:<16,.1f} {m['peak_overshoot_pct']:<14.2f} {m['settling_time_sec']:<10.1f}")

    print(f"{sub_border}")
    print(f"Champion Architecture   : [{report['champion_controller']}]")
    print(f"MPC vs PID Improvement   : -{report['mpc_vs_pid_iae_reduction_pct']}% Cumulative Tracking Error (IAE)")
    print(f"{border}\n")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Process Control and Dynamic MPC Simulation (V1.1)")
    parser.add_argument("--controller", type=str, default="mpc", choices=["open_loop", "pid", "mpc"], help="Controller type")
    parser.add_argument("--setpoint", type=float, default=520.0, help="Target setpoint (°C)")
    parser.add_argument("--benchmark", action="store_true", help="Run comparative benchmark suite across all controllers")
    parser.add_argument("--output", type=str, default=None, help="Output report JSON file path")
    args = parser.parse_args()

    suite = ControlBenchmarkSuite()

    if args.benchmark:
        rep = suite.run_all_benchmarks(report_path=args.output)
        print_benchmark_dashboard(rep)
        print(f"[OK] Control benchmark report exported to reports/control_benchmark_report.json")
    else:
        states, metrics = suite.run_simulation(controller_type=args.controller, setpoint_step_c=args.setpoint)
        print(f"\n[*] Simulated 60-min dynamic trajectory for [{args.controller.upper()}]:")
        print(f"    IAE: {metrics.iae:,.1f} °C·s | ITAE: {metrics.itae:,.1f} | Overshoot: {metrics.peak_overshoot_pct:.2f}% | Settling: {metrics.settling_time_sec:.1f}s")
        print(f"    Final State: {states[-1].reactor_temp_c:.2f}°C (Control Effort: {states[-1].control_effort_pct:.1f}%)\n")


if __name__ == "__main__":
    main()
