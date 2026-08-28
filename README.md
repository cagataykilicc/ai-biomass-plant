# AI-Integrated Biomass Recycling & Conversion Plant Digital Twin (V1.0)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Web Platform: Glassmorphism GUI](https://img.shields.io/badge/Web%20Platform-Interactive%20Dark%20Glassmorphism-cyan.svg)]()
[![REST API: Zero--Dependency](https://img.shields.io/badge/REST%20API-Zero--Dependency%20HTTP-blueviolet.svg)]()
[![Predictive Maintenance: 95% RUL](https://img.shields.io/badge/PdM-RUL%20Prognostics%20%26%20Work%20Orders-darkgreen.svg)]()
[![Diagnostics: Tri--Layer FDD](https://img.shields.io/badge/Diagnostics-Tri--Layer%20FDD%20%26%20Alarms-critical.svg)]()
[![Soft Sensors: 6 Virtual Gauges](https://img.shields.io/badge/Soft%20Sensors-6%20Inferential%20Gauges%20(95%25%20UQ)-blueviolet.svg)]()
[![Optimization: NSGA--II Pareto & TOPSIS](https://img.shields.io/badge/Optimization-Pareto%20%26%20TOPSIS%20MCDM-blue.svg)]()
[![Champion ML: Gradient Boosting](https://img.shields.io/badge/Champion%20Model-Gradient%20Boosting%20(R%C2%B2%200.9981)-blueviolet.svg)]()
[![Physics: 100% Mass Conserved](https://img.shields.io/badge/Physics%20Constraint-Simplex%20Projection%20(100%25)-darkgreen.svg)]()
[![Tests: 100% Passed](https://img.shields.io/badge/Tests-84%2F84%20Passed-brightgreen.svg)]()
[![Thermal Status: Self--Sufficient](https://img.shields.io/badge/Thermal%20Status-Autonomous%20(TSI%20111.3%25)-darkgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

A complete, full-stack, first-principles chemical engineering and machine learning **Digital Twin Web Platform** for biomass thermochemical recycling and conversion.

---

## 1. Digital Twin Architecture & Features

The **V1.0 Digital Twin Platform** integrates the complete hierarchy of industrial plant operations into a single interactive web application:

1. **Process Flowsheet & Control Room**: Live setpoint sliders ($T_{reactor}$, $\dot{m}_{feed}$, heating rate, moisture), animated P&ID flowsheet, mass & elemental closures, and energy self-sufficiency gauge (TSI).
2. **Industrial Soft Sensor Suite (95% UQ)**: 6 real-time virtual instruments estimating unmeasured lab properties (Bio-Oil TAN, Moisture, HHV, Syngas LHV, Biochar Yield, TSI) directly from physical telemetry.
3. **Multiobjective Optimization & Pareto Frontier**: Interactive NSGA-II non-dominated trade-off surface (Bio-Oil vs Biochar vs Profit vs Thermal Efficiency) and TOPSIS MCDM stakeholder decision profiles.
4. **Tri-Layer Anomaly Diagnostics & Alarms**: Physical balance residual checks, Isolation Forest, and PCA reconstruction error ($Q$-statistic & Hotelling's $T^2$) diagnosing 5 industrial fault modes with automated NFPA/SIL-2 safety interlocks.
5. **Predictive Maintenance & Fleet RUL**: Physics-informed degradation models for infeed augers, refractory liners, particulate filters, and condensers with automated work orders (parts BOM, labor, and safety LOTO).

---

## 2. Interactive Web Platform UI Preview

```text
+----------------------------------------------------------------------------------------------------+
|  BIOPLANT AI (V1.0) | TI-103: 500.0 °C | FI-101: 100.0 kg/h | TSI: 111.3% [AUTONOMOUS] | MODEL: GB   |
+----------------------------------------------------------------------------------------------------+
| [Control Room]       |  [LIVE ANIMATED PROCESS FLOWSHEET]                                          |
|                      |                                                                             |
|  * Feedstock Selector|   [DRYER D101] ---> [REACTOR R101] ---> [CYCLONE C101] ---> [CONDENSER]    |
|  * Temp Slider       |        ^                 |                     |                  |         |
|  * Feed Rate Slider  |        +-----------------+---------------------+---------[BURNER B101]     |
|  * Moisture Slider   |                                                                             |
|  * Yield Engine (ML) |  Bio-Oil: 48.1 kg/h (48.1%) | Biochar: 27.4 kg/h (27.4%) | TSI: 111.3%     |
+----------------------+-----------------------------------------------------------------------------+
| [Soft Sensors]       |  SS_101 (TAN): 97.5 mg KOH/g [93.4-101.7] | SS_104 (LHV): 13.96 MJ/Nm³     |
| [Pareto Optimizer]   |  Interactive Pareto Curve & TOPSIS Optimal Setpoint ($18.42/h Profit)       |
| [Fault Diagnostics]  |  Injected Fault: Cyclone Blockage -> [WARNING: Trigger N2 Pulse-Jet]        |
| [Predictive Maint]   |  4,500 Hours -> Bottleneck: Reactor Refractory (RUL: 2,826 h) [WO-REACT]    |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. REST API Specification

The built-in multi-threaded HTTP server serves standard JSON REST endpoints on port 8000:

| HTTP Method | Route | Description |
| :--- | :--- | :--- |
| **`GET`** | **`/`** | Serves single-page Dark Glassmorphism Web GUI application |
| **`GET`** | **`/api/status`** | System health status, version `1.0.0`, and active modules |
| **`GET`** | **`/api/feedstocks`** | Feedstock proximate and ultimate analysis library |
| **`POST`** | **`/api/simulate`** | Executes digital twin simulation flowsheet (deterministic or ML) |
| **`POST`** | **`/api/soft-sensors`** | Extracts hardware telemetry and evaluates 6 soft sensors with 95% UQ |
| **`POST`** | **`/api/optimize`** | Solves single-objective or multiobjective Pareto optimization |
| **`POST`** | **`/api/diagnostics`** | Injects equipment fault and returns anomaly scores and alarms |
| **`POST`** | **`/api/maintenance`** | Computes asset wear, 95% RUL, and dispatches work orders |

---

## 4. Software Architecture

```text
ai_biomass_plant/
│
├── src/
│   ├── api/
│   │   ├── handlers.py                       # REST API business logic and route handlers
│   │   └── server.py                         # Multi-threaded HTTP server & static asset host
│   ├── web/
│   │   ├── run_server.py                     # Web GUI server launcher CLI
│   │   └── static/
│   │       ├── index.html                    # Modern 5-tab digital twin dashboard
│   │       ├── styles.css                    # Dark Glassmorphism design system
│   │       └── app.js                        # Reactive frontend controller
│   ├── maintenance/                          # Degradation kinematics & RUL prognostics
│   ├── diagnostics/                          # Fault simulation, anomaly detector & alarms
│   ├── sensors/                              # Hardware telemetry & 6 Soft Sensors (95% UQ)
│   ├── optimization/                         # SLSQP, Differential Evolution, Pareto & TOPSIS
│   ├── ml/                                   # Surrogate models & physics constraints
│   ├── process/                              # Unit operations & balance engines
│   ├── simulation/
│   │   └── plant_simulator.py                # Hybrid simulation engine orchestrator
│   └── run_simulation.py                     # CLI application entry point
│
├── tests/                                    # 84 Automated Unit & Integration Tests
│   ├── test_api.py
│   ├── test_degradation_models.py
│   ├── test_rul_estimator.py
│   ├── test_work_orders.py
│   ├── test_fault_simulator.py
│   ├── test_anomaly_detector.py
│   ├── test_fault_diagnostics.py
│   └── ...
│
├── pyproject.toml
└── README.md
```

---

## 5. How to Launch the Web Platform

### A. Start Digital Twin Web Platform (Interactive Dashboard)
```bash
python -m src.run_simulation --web
# Or directly via web launcher:
python -m src.web.run_server --port 8000 --open-browser
```
Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser.

### B. Run Predictive Maintenance & RUL Dashboard
```bash
python -m src.maintenance.run_maintenance --operating-hours 4500
```

### C. Run Fault Diagnostics & Alarm Triage
```bash
python -m src.diagnostics.run_diagnostics --simulate-fault cyclone_blockage
```

### D. Run Real-Time Inferential Soft Sensor Dashboard
```bash
python -m src.sensors.run_soft_sensors --feedstock pine_sawdust --temp 520
```

### E. Run Process Optimization & TOPSIS Decision Support
```bash
python -m src.optimization.run_optimizer --feedstock pine_sawdust --multiobjective
```

### F. Run Unit Test Suite
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
* [x] **V0.9: Predictive Maintenance (RUL Estimation & Prescriptive Work Orders)** *(Completed)*
* [x] **V1.0: Real-Time Digital Twin Platform & Web GUI Dashboard** *(Completed)*
* [ ] **V1.1: Dynamic Closed-Loop Process Control Simulation (MPC / PID Control)**
  * Transient dynamic modeling, feedback PID control loops for reactor temperature and auger speed, and Model Predictive Control (MPC) trajectory tracking.
* [ ] **V1.2: Plant-Level AI Decision Support (Techno-Economic & LCA Carbon Accounting)**
* [ ] **V2.0: Fully Autonomous AI Biomass Recycling Plant Platform**
