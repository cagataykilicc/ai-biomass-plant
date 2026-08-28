"""CLI interface and interactive diagnostics dashboard for anomaly detection and fault triage.

Usage:
    python -m src.diagnostics.run_diagnostics --simulate-fault cyclone_blockage --severity 0.85
    python -m src.diagnostics.run_diagnostics --train-models
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import numpy as np
import pandas as pd

from src.sensors.telemetry import TelemetryExtractor, HardwareTelemetryPacket
from src.diagnostics.fault_simulator import IndustrialFaultType, FaultInjectionConfig, ProcessFaultSimulator
from src.diagnostics.anomaly_detector import MultiLayerAnomalyDetector, AnomalyDetectionResult
from src.diagnostics.fault_diagnostics import FaultDiagnosticEngine, DiagnosticClassificationResult
from src.diagnostics.alarm_manager import AlarmManager, SafetyActionProtocol, AlarmPriority


def train_diagnostic_models() -> Tuple[MultiLayerAnomalyDetector, FaultDiagnosticEngine]:
    """Train anomaly detector and fault classifier checkpoints."""
    root_dir = Path(__file__).resolve().parent.parent.parent
    data_path = root_dir / "data" / "processed" / "synthetic_process_dataset.csv"
    chk_dir = root_dir / "models" / "checkpoints"
    chk_dir.mkdir(parents=True, exist_ok=True)

    print("[*] Training Anomaly Detector on baseline process telemetry...")
    df = pd.read_csv(data_path)
    from src.sensors.calibration import SoftSensorCalibrator
    X_normal, _ = SoftSensorCalibrator()._extract_telemetry_features(df)

    detector = MultiLayerAnomalyDetector()
    detector.fit(X_normal)
    det_path = chk_dir / "anomaly_detector.joblib"
    detector.save(det_path)
    print(f"[OK] Anomaly detector saved to {det_path}")

    print("[*] Training Fault Diagnostic Classifier on synthetic industrial fault modes...")
    classifier = FaultDiagnosticEngine()
    classifier.train_on_synthetic_faults(samples_per_fault=50)
    clf_path = chk_dir / "fault_classifier.joblib"
    classifier.save(clf_path)
    print(f"[OK] Fault diagnostic classifier saved to {clf_path}")

    return detector, classifier


def load_or_train_models() -> Tuple[MultiLayerAnomalyDetector, FaultDiagnosticEngine]:
    """Load pretrained diagnostic checkpoints or train if missing."""
    root_dir = Path(__file__).resolve().parent.parent.parent
    det_path = root_dir / "models" / "checkpoints" / "anomaly_detector.joblib"
    clf_path = root_dir / "models" / "checkpoints" / "fault_classifier.joblib"

    if det_path.is_file() and clf_path.is_file():
        try:
            return MultiLayerAnomalyDetector.load(det_path), FaultDiagnosticEngine.load(clf_path)
        except Exception:
            pass

    return train_diagnostic_models()


def print_diagnostics_dashboard(
    telemetry: HardwareTelemetryPacket,
    fault_cfg: FaultInjectionConfig,
    anomaly_res: AnomalyDetectionResult,
    diag_res: DiagnosticClassificationResult,
    alarm: SafetyActionProtocol,
) -> None:
    """Print ANSI formatted diagnostics and alarm dashboard to stdout."""
    w = 78
    border = "=" * w
    sub_border = "-" * w

    print(f"\n{border}")
    print(f"       AI-INTEGRATED BIOMASS CONVERSION PLANT - V0.8")
    print(f"  (Process Anomaly Detection, Equipment Diagnostics & Safety Alarms)")
    print(f"{border}")
    print(f"Simulated Injected State : [{fault_cfg.fault_type.value}] (Severity: {fault_cfg.severity * 100:.0f}%)")
    print(f"Timestamp                : {telemetry.timestamp}")

    print(f"\nANOMALY DETECTION DIAGNOSTICS (Tri-Layer Analysis)")
    print(f"{sub_border}")
    status_str = "[ALERT: ANOMALY DETECTED]" if anomaly_res.is_anomaly else "[NORMAL OPERATIONS]"
    print(f"Overall Anomaly State    : {status_str} (Score: {anomaly_res.overall_anomaly_score:.3f} / 1.000)")
    print(f"Isolation Forest Trigger : {'YES' if anomaly_res.isolation_forest_anomaly else 'NO'} (Outlier Score: {anomaly_res.isolation_forest_score:.3f})")
    q_str = f"Q = {anomaly_res.pca_q_statistic:.2f} (Limit 99%: {anomaly_res.pca_q_limit_99:.2f}) -> {'EXCEEDED' if anomaly_res.pca_q_exceeded else 'NORMAL'}"
    t2_str = f"T² = {anomaly_res.pca_t2_statistic:.2f} (Limit 99%: {anomaly_res.pca_t2_limit_99:.2f}) -> {'EXCEEDED' if anomaly_res.pca_t2_exceeded else 'NORMAL'}"
    print(f"PCA Residual Statistics  : {q_str}")
    print(f"Hotelling's T² Distance  : {t2_str}")
    print(f"Top Contributing Sensors : " + ", ".join([f"{item['sensor_tag']} (res²={item['squared_residual']:.2f})" for item in anomaly_res.top_contributing_sensors[:3]]))

    print(f"\nROOT CAUSE DIAGNOSIS & EQUIPMENT ATTRIBUTION")
    print(f"{sub_border}")
    print(f"Diagnosed Failure Mode   : [{diag_res.predicted_fault.value}] (Confidence: {diag_res.confidence_probability * 100:.1f}%)")
    print(f"Affected Unit Operation  : {diag_res.affected_equipment_tag}")
    print(f"Diagnostic Explanation   : {diag_res.root_cause_explanation}")

    print(f"\nAUTOMATED ALARM & SAFETY MITIGATION PROTOCOL")
    print(f"{sub_border}")
    p_color = f"[{alarm.priority.value}]"
    print(f"Alarm ID & Severity      : {alarm.alarm_id} -> {p_color}")
    print(f"Headline Advisory        : {alarm.headline_message}")
    print(f"Recommended Operator Act : {alarm.recommended_operator_action}")
    print(f"Automated Interlock Trip : {alarm.automated_interlock_action}")
    print(f"Safety Standard Code     : {alarm.safety_standard_reference}")
    print(f"{border}\n")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Plant Fault Diagnostics and Alarm Manager (V0.8)")
    parser.add_argument(
        "--simulate-fault",
        type=str,
        default="cyclone_blockage",
        choices=["none", "cyclone_blockage", "condenser_fouling", "thermal_runaway", "sensor_drift", "feed_jam"],
        help="Simulated industrial fault mode",
    )
    parser.add_argument("--severity", type=float, default=0.85, help="Fault severity in [0.0, 1.0]")
    parser.add_argument("--train-models", action="store_true", help="Retrain anomaly and fault models")
    parser.add_argument("--output", type=str, default=None, help="Output JSON report path")
    args = parser.parse_args()

    if args.train_models:
        train_diagnostic_models()
        return

    detector, classifier = load_or_train_models()

    # Map CLI arg to enum
    f_map = {
        "none": IndustrialFaultType.NONE,
        "cyclone_blockage": IndustrialFaultType.CYCLONE_DIPLEG_BLOCKAGE,
        "condenser_fouling": IndustrialFaultType.CONDENSER_TAR_FOULING,
        "thermal_runaway": IndustrialFaultType.REACTOR_THERMAL_RUNAWAY,
        "sensor_drift": IndustrialFaultType.THERMOCOUPLE_SENSOR_DRIFT,
        "feed_jam": IndustrialFaultType.FEED_AUGER_JAMMING,
    }
    fault_type = f_map.get(args.simulate_fault.lower(), IndustrialFaultType.NONE)
    fault_cfg = FaultInjectionConfig(fault_type=fault_type, severity=args.severity)

    sim = ProcessFaultSimulator()
    report, telemetry = sim.run_faulted_simulation(fault_cfg)

    anomaly_res = detector.detect(telemetry, report)
    diag_res = classifier.diagnose(telemetry, anomaly_res)
    alarm = AlarmManager.evaluate_alarm(anomaly_res, diag_res)

    print_diagnostics_dashboard(telemetry, fault_cfg, anomaly_res, diag_res, alarm)

    report_payload = {
        "simulation_context": {
            "fault_injected": fault_type.value,
            "severity": args.severity,
            "timestamp": telemetry.timestamp,
        },
        "telemetry": telemetry.to_dict(),
        "anomaly_detection": anomaly_res.to_dict(),
        "fault_diagnosis": diag_res.to_dict(),
        "alarm_protocol": alarm.to_dict(),
    }

    out_file = (
        Path(args.output)
        if args.output
        else Path(__file__).resolve().parent.parent.parent / "reports" / "fault_detection_report.json"
    )
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report_payload, f, indent=2)
    print(f"[OK] Fault detection report written to {out_file}")


if __name__ == "__main__":
    main()
