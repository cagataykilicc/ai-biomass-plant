# AI-Integrated Biomass Recycling & Conversion Plant Digital Twin (V0.8)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Diagnostics: Tri--Layer FDD](https://img.shields.io/badge/Diagnostics-Tri--Layer%20FDD%20%26%20Alarms-critical.svg)]()
[![Soft Sensors: 6 Virtual Gauges](https://img.shields.io/badge/Soft%20Sensors-6%20Inferential%20Gauges%20(95%25%20UQ)-blueviolet.svg)]()
[![Optimization: NSGA--II Pareto & TOPSIS](https://img.shields.io/badge/Optimization-Pareto%20%26%20TOPSIS%20MCDM-blue.svg)]()
[![Champion ML: Gradient Boosting](https://img.shields.io/badge/Champion%20Model-Gradient%20Boosting%20(R%C2%B2%200.9981)-blueviolet.svg)]()
[![Physics: 100% Mass Conserved](https://img.shields.io/badge/Physics%20Constraint-Simplex%20Projection%20(100%25)-darkgreen.svg)]()
[![Tests: 100% Passed](https://img.shields.io/badge/Tests-71%2F71%20Passed-brightgreen.svg)]()
[![Thermal Status: Self--Sufficient](https://img.shields.io/badge/Thermal%20Status-Autonomous%20(TSI%20111.3%25)-darkgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

A modular, first-principles chemical engineering and digital twin platform for biomass thermal conversion, real-time inferential soft sensors, process anomaly detection, equipment fault diagnosis, and automated alarm management.

---

## 1. Project Objective

The objective is to develop an industrial-grade digital twin of a commercial biomass conversion plant that progressively unifies:

* Rigorous chemical engineering calculations & thermodynamics
* Multi-stage unit operations (drying, pyrolysis reactor, cyclone, condenser train, syngas combustor)
* Atom-by-atom elemental mass conservation ($C, H, O, N, S, Ash$)
* Molecular syngas speciation ($CO, CO_2, CH_4, H_2, C_2H_6, H_2O, N_2$)
* Bio-oil chemical grouping (phenolics, acids, furans, sugars) & acidity ($TAN, \text{pH}$)
* Syngas burner heat integration & Thermal Self-Sufficiency Index (TSI)
* Second-Law Exergy analysis and destruction tracking
* **Multi-Model Machine Learning Benchmarking**: Gradient Boosting Champion ($R^2 = 0.9981$)
* **Physics-Informed Constraint Projection**: Exact $100.00\%$ mass conservation across solid, liquid, and gas phases
* **AI-Driven Process Optimization & Pareto Frontier Engine**: SLSQP, Differential Evolution, NSGA-II, and TOPSIS MCDM
* **Industrial Soft Sensors with 95% UQ**: Real-time inferential estimation of unmeasured lab properties (Bio-oil TAN, Moisture, HHV, Syngas LHV, Char Yield, TSI)
* **Tri-Layer Anomaly Detection & Fault Diagnosis**: Physical conservation residuals, Isolation Forest, and PCA reconstruction error ($Q$-statistic & Hotelling's $T^2$) diagnosing 5 industrial failure modes with automated safety mitigation protocols

---

## 2. Process Anomaly Detection & Fault Diagnosis (V0.8)

```text
  +-----------------------------------------------------------------------------------+
  |                       ONLINE HARDWARE SENSOR TELEMETRY                            |
  |  TI-101..106 (Temperatures), FI-101..103 (Flows), PI-101 (Bed Differential Pres)  |
  +---------------------------------------+-------------------------------------------+
                                          |
                                          v
               +----------------------------------------------------+
               |         TRI-LAYER ANOMALY DETECTION ENGINE         |
               |  * Layer 1: Mass/Elemental Conservation Residuals  |
               |  * Layer 2: Isolation Forest Spatial Outlier Score |
               |  * Layer 3: PCA Reconstruction Error (SPE Q & T²)  |
               +--------------------------+-------------------------+
                                          |
                                          v
               +----------------------------------------------------+
               |      ROOT CAUSE FAULT DIAGNOSTIC CLASSIFIER        |
               |  * Cyclone C101 Dipleg Blockage (Delta-P Surge)    |
               |  * Condenser Train HX102 Tar/Wax Fouling           |
               |  * Pyrolysis Reactor R101 Thermal Excursion        |
               |  * Instrument Calibration Bias / Sensor Drift      |
               |  * Feed Auger A101 Jamming & Fuel Starvation       |
               +--------------------------+-------------------------+
                                          |
                                          v
               +----------------------------------------------------+
               |       AUTOMATED ALARM MANAGER & SAFETY ACTIONS     |
               |  * Severity Triage: INFO, WARNING, CRITICAL_ESD    |
               |  * Automatic Interlocks (N2 Purge, Starve Trip)    |
               |  * Compliance: NFPA 86, NFPA 652, IEC 61508 SIL-2  |
               +----------------------------------------------------+
```

---

## 3. Industrial Fault Modes & Safety Mitigations

| Failure Mode | Affected Equipment | Primary Telemetry Signature | Automated Interlock Action | Standard Code |
| :--- | :---: | :--- | :--- | :--- |
| **`CYCLONE_DIPLEG_BLOCKAGE`** | **`CYCLONE_C101`** | Bed $\Delta P$ surges ($> 12\text{ kPa}$), char carryover | Trigger automated high-pressure $N_2$ pulse-jet knocker | **NFPA 652** |
| **`CONDENSER_TAR_FOULING`** | **`CONDENSER_HX102`** | Gas exit temp spikes ($> 50^\circ\text{C}$), high cooling demand | Ramp cooling water pump to $100\%$ duty; prep solvent flush | **TEMA / API 660** |
| **`REACTOR_THERMAL_RUNAWAY`**| **`REACTOR_R101`** | Core bed temp excursion ($> 650^\circ\text{C}$) | **Trip Emergency Starve**: Cut feed auger, bypass flue, $N_2$ flood | **NFPA 86 / SIL-2** |
| **`THERMOCOUPLE_SENSOR_DRIFT`**| **`INSTRUMENT_TI103`** | Steady temperature offset bias ($\pm 25^\circ\text{C}$) | Switch temperature control loop to redundant sensor `TI-103B` | **ISA-75** |
| **`FEED_AUGER_JAMMING`** | **`FEEDER_AUGER_A101`** | Biomass feed collapses ($\dot{m} \rightarrow 0$), $\Delta P$ drops | Execute 3-sec reverse auger cycle; trip motor if torque $> 150\%$ | **CEMA Safety** |

---

## 4. Software Architecture

```text
ai_biomass_plant/
│
├── models/
│   └── checkpoints/
│       ├── anomaly_detector.joblib           # Multi-layer anomaly detector (IForest + PCA)
│       ├── fault_classifier.joblib           # Supervised root-cause diagnostic classifier
│       ├── soft_sensors.joblib               # 6 Serialized inferential virtual sensors
│       └── yield_predictor_champion.joblib   # Production champion yield surrogate
│
├── reports/
│   ├── fault_detection_report.json           # Anomaly scores, root cause & alarm dispatch report
│   ├── soft_sensor_calibration_report.json   # Soft sensor R², RMSE & 95% UQ coverage
│   ├── process_optimization_report.json      # Optimal operational setpoints
│   └── pareto_frontier.json                  # Non-dominated Pareto frontier points
│
├── src/
│   ├── diagnostics/
│   │   ├── fault_simulator.py                # 5 Industrial fault injection modes
│   │   ├── anomaly_detector.py               # Tri-layer anomaly detection (IForest, PCA, Balances)
│   │   ├── fault_diagnostics.py              # Root cause classifier & equipment attribution
│   │   ├── alarm_manager.py                  # Alarm priority triage & safety mitigation advice
│   │   └── run_diagnostics.py                # Diagnostics CLI dashboard
│   ├── sensors/                              # Hardware telemetry & 6 Soft Sensors (95% UQ)
│   ├── optimization/                         # SLSQP, Differential Evolution, Pareto & TOPSIS
│   ├── ml/                                   # Surrogate models & physics constraints
│   ├── process/                              # Unit operations & balance engines
│   ├── simulation/
│   │   └── plant_simulator.py                # Hybrid simulation engine orchestrator
│   └── run_simulation.py                     # CLI application entry point
│
├── tests/                                    # 71 Automated Unit & Integration Tests
│   ├── test_fault_simulator.py
│   ├── test_anomaly_detector.py
│   ├── test_fault_diagnostics.py
│   ├── test_alarm_manager.py
│   ├── test_telemetry.py
│   ├── test_soft_sensors.py
│   ├── test_calibration.py
│   └── ...
│
├── pyproject.toml
└── README.md
```

---

## 5. How to Run the Platform

### A. Run Simulated Fault Diagnostics & Safety Alarm Dispatch
```bash
python -m src.diagnostics.run_diagnostics --simulate-fault cyclone_blockage --severity 0.85
```

### B. Run Thermal Runaway Emergency Simulation
```bash
python -m src.diagnostics.run_diagnostics --simulate-fault thermal_runaway --severity 0.90
```

### C. Run Real-Time Inferential Soft Sensor Dashboard
```bash
python -m src.sensors.run_soft_sensors --feedstock pine_sawdust --temp 520
```

### D. Run Process Optimization & TOPSIS Decision Support
```bash
python -m src.optimization.run_optimizer --feedstock pine_sawdust --multiobjective
```

### E. Run Unit Test Suite
```bash
pytest tests/ -v
```

---

## 6. Long-Term Roadmap

* [x] **V0.1: Deterministic Process Flowsheet Model** *(Completed)*
* [x] **V0.2: Improved Mass, Elemental & Energy Balances & Heat Integration** *(Completed)*
* [x] **V0.3: Experimental Literature & Synthetic Dataset Generation** *(Completed)*
* [x] **V0.4: Machine Learning Product Yield Prediction & Physics Constraints** *(Completed)*
* [x] **V0.5: Multi-Model Benchmark & Physics-Informed ML Comparisons** *(Completed)*
* [x] **V0.6: AI-Driven Multiobjective Process Optimization (Pareto & TOPSIS)** *(Completed)*
* [x] **V0.7: Soft Sensors for Real-Time State Estimation (95% UQ)** *(Completed)*
* [x] **V0.8: Process Anomaly & Fault Detection (Autoencoders, Isolation Forests & Alarms)** *(Completed)*
* [ ] **V0.9: Predictive Maintenance (RUL of Augers, Refractory, Filters)**
  * Remaining Useful Life (RUL) estimation using degradation trajectory models and survival analysis.
* [ ] **V1.0: Real-Time Digital Twin Prototype (FastAPI + Streamlit GUI)**
* [ ] **V1.1: Dynamic Closed-Loop Process Control Simulation (MPC / PID)**
* [ ] **V1.2: Plant-Level AI Decision Support (Techno-Economic & LCA Carbon Accounting)**
* [ ] **V2.0: Fully Autonomous AI Biomass Recycling Plant Platform**
