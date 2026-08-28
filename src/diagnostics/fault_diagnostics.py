"""Supervised equipment fault diagnosis and root-cause attribution engine.

Classifies anomalous process states into specific industrial failure modes:
1. CYCLONE_DIPLEG_BLOCKAGE (Cyclone C101)
2. CONDENSER_TAR_FOULING (Condenser Train HX102)
3. REACTOR_THERMAL_RUNAWAY (Pyrolysis Reactor R101)
4. THERMOCOUPLE_SENSOR_DRIFT (Sensor Instrumentation)
5. FEED_AUGER_JAMMING (Feed System H101)
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

from src.sensors.telemetry import HardwareTelemetryPacket
from src.diagnostics.fault_simulator import IndustrialFaultType, FaultInjectionConfig, ProcessFaultSimulator
from src.diagnostics.anomaly_detector import AnomalyDetectionResult


@dataclass
class DiagnosticClassificationResult:
    """Diagnostic identification of root cause and affected equipment."""
    predicted_fault: IndustrialFaultType
    confidence_probability: float
    fault_probabilities: Dict[str, float]
    affected_equipment_tag: str
    root_cause_explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "predicted_fault": self.predicted_fault.value,
            "confidence_probability": round(self.confidence_probability, 4),
            "fault_probabilities": {k: round(v, 4) for k, v in self.fault_probabilities.items()},
            "affected_equipment_tag": self.affected_equipment_tag,
            "root_cause_explanation": self.root_cause_explanation,
        }


class FaultDiagnosticEngine:
    """Classifies anomalous telemetry patterns into specific physical failure modes."""

    EQUIPMENT_MAP: Dict[IndustrialFaultType, Tuple[str, str]] = {
        IndustrialFaultType.NONE: (
            "PLANT_NORMAL",
            "Process operating within normal design envelope."
        ),
        IndustrialFaultType.CYCLONE_DIPLEG_BLOCKAGE: (
            "CYCLONE_C101",
            "Severe particulate accumulation in cyclone dipleg causing differential pressure surge."
        ),
        IndustrialFaultType.CONDENSER_TAR_FOULING: (
            "CONDENSER_HX102",
            "Heavy wax and tar deposition on tube bundles causing thermal transfer degradation."
        ),
        IndustrialFaultType.REACTOR_THERMAL_RUNAWAY: (
            "REACTOR_R101",
            "Uncontrolled exothermic temperature excursion in pyrolysis bed core."
        ),
        IndustrialFaultType.THERMOCOUPLE_SENSOR_DRIFT: (
            "INSTRUMENT_TI103",
            "Calibration bias or thermoelectric decalibration detected on temperature transmitter."
        ),
        IndustrialFaultType.FEED_AUGER_JAMMING: (
            "FEEDER_AUGER_A101",
            "Mechanical obstruction or motor stall in biomass feed auger conveyor."
        ),
    }

    def __init__(self, random_state: int = 42) -> None:
        self.random_state = random_state
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=8,
            random_state=random_state,
        )
        self.is_fitted: bool = False

    def train_on_synthetic_faults(
        self,
        fault_simulator: Optional[ProcessFaultSimulator] = None,
        samples_per_fault: int = 40,
    ) -> FaultDiagnosticEngine:
        """Generate synthetic faulted dataset and train diagnostic classifier."""
        sim = fault_simulator or ProcessFaultSimulator()
        X_train_list: List[np.ndarray] = []
        y_train_list: List[str] = []

        # Normal baseline samples
        for _ in range(samples_per_fault):
            t_rand = float(np.random.uniform(450.0, 550.0))
            f_rand = float(np.random.uniform(80.0, 120.0))
            rep, tel = sim.run_faulted_simulation(
                FaultInjectionConfig(IndustrialFaultType.NONE),
                reactor_temp_c=t_rand,
                feed_rate_kg_h=f_rand,
            )
            X_train_list.append(tel.to_feature_vector())
            y_train_list.append(IndustrialFaultType.NONE.value)

        # Faulted samples for all 5 fault modes
        fault_modes = [
            IndustrialFaultType.CYCLONE_DIPLEG_BLOCKAGE,
            IndustrialFaultType.CONDENSER_TAR_FOULING,
            IndustrialFaultType.REACTOR_THERMAL_RUNAWAY,
            IndustrialFaultType.THERMOCOUPLE_SENSOR_DRIFT,
            IndustrialFaultType.FEED_AUGER_JAMMING,
        ]

        for fm in fault_modes:
            for _ in range(samples_per_fault):
                sev = float(np.random.uniform(0.40, 1.0))
                t_rand = float(np.random.uniform(450.0, 550.0))
                f_rand = float(np.random.uniform(80.0, 120.0))
                rep, tel = sim.run_faulted_simulation(
                    FaultInjectionConfig(fm, severity=sev),
                    reactor_temp_c=t_rand,
                    feed_rate_kg_h=f_rand,
                )
                X_train_list.append(tel.to_feature_vector())
                y_train_list.append(fm.value)

        X_mat = np.array(X_train_list, dtype=np.float64)
        y_vec = np.array(y_train_list)

        self.classifier.fit(X_mat, y_vec)
        self.is_fitted = True
        return self

    def diagnose(
        self,
        telemetry: HardwareTelemetryPacket,
        anomaly_result: Optional[AnomalyDetectionResult] = None,
    ) -> DiagnosticClassificationResult:
        """Classify fault type and provide root cause explanation."""
        if not self.is_fitted:
            raise RuntimeError("Diagnostic classifier is not fitted. Train or load checkpoint first.")

        # If anomaly detector reports normal, default to NONE
        if anomaly_result is not None and not anomaly_result.is_anomaly:
            eq_tag, expl = self.EQUIPMENT_MAP[IndustrialFaultType.NONE]
            return DiagnosticClassificationResult(
                predicted_fault=IndustrialFaultType.NONE,
                confidence_probability=1.0 - anomaly_result.overall_anomaly_score,
                fault_probabilities={IndustrialFaultType.NONE.value: 1.0},
                affected_equipment_tag=eq_tag,
                root_cause_explanation=expl,
            )

        x_vec = telemetry.to_feature_vector().reshape(1, -1)
        pred_label = self.classifier.predict(x_vec)[0]
        probs = self.classifier.predict_proba(x_vec)[0]
        classes = self.classifier.classes_

        prob_dict = {classes[i]: float(probs[i]) for i in range(len(classes))}
        top_prob = float(np.max(probs))

        fault_enum = IndustrialFaultType(pred_label)
        eq_tag, expl = self.EQUIPMENT_MAP.get(fault_enum, ("UNKNOWN_EQUIPMENT", "Unclassified operational upset."))

        return DiagnosticClassificationResult(
            predicted_fault=fault_enum,
            confidence_probability=top_prob,
            fault_probabilities=prob_dict,
            affected_equipment_tag=eq_tag,
            root_cause_explanation=expl,
        )

    def save(self, file_path: Union[str, Path]) -> Path:
        """Serialize classifier checkpoint."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "classifier": self.classifier,
            "is_fitted": self.is_fitted,
        }
        joblib.dump(payload, path)
        return path

    @classmethod
    def load(cls, file_path: Union[str, Path]) -> FaultDiagnosticEngine:
        """Load serialized classifier checkpoint."""
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Fault classifier checkpoint not found at: {path}")

        payload = joblib.load(path)
        engine = cls()
        engine.classifier = payload["classifier"]
        engine.is_fitted = payload["is_fitted"]
        return engine
