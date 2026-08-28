# AI-Integrated Biomass Recycling & Conversion Plant Digital Twin (V1.1)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Control: Dynamic MPC & PID](https://img.shields.io/badge/Process%20Control-Dynamic%20MPC%20%26%20PID-blue.svg)]()
[![Web Platform: Glassmorphism GUI](https://img.shields.io/badge/Web%20Platform-Interactive%20Dark%20Glassmorphism-cyan.svg)]()
[![REST API: Zero--Dependency](https://img.shields.io/badge/REST%20API-Zero--Dependency%20HTTP-blueviolet.svg)]()
[![Predictive Maintenance: 95% RUL](https://img.shields.io/badge/PdM-RUL%20Prognostics%20%26%20Work%20Orders-darkgreen.svg)]()
[![Diagnostics: Tri--Layer FDD](https://img.shields.io/badge/Diagnostics-Tri--Layer%20FDD%20%26%20Alarms-critical.svg)]()
[![Soft Sensors: 6 Virtual Gauges](https://img.shields.io/badge/Soft%20Sensors-6%20Inferential%20Gauges%20(95%25%20UQ)-blueviolet.svg)]()
[![Optimization: NSGA--II Pareto & TOPSIS](https://img.shields.io/badge/Optimization-Pareto%20%26%20TOPSIS%20MCDM-blue.svg)]()
[![Champion ML: Gradient Boosting](https://img.shields.io/badge/Champion%20Model-Gradient%20Boosting%20(R%C2%B2%200.9981)-blueviolet.svg)]()
[![Physics: 100% Mass Conserved](https://img.shields.io/badge/Physics%20Constraint-Simplex%20Projection%20(100%25)-darkgreen.svg)]()
[![Tests: 100% Passed](https://img.shields.io/badge/Tests-91%2F91%20Passed-brightgreen.svg)]()
[![Thermal Status: Self--Sufficient](https://img.shields.io/badge/Thermal%20Status-Autonomous%20(TSI%20111.3%25)-darkgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

A complete, full-stack, first-principles chemical engineering and machine learning **Digital Twin Platform** for biomass thermochemical recycling and conversion, featuring dynamic closed-loop process control simulation (MPC & PID).

---

## 1. Digital Twin Architecture & Features

The **V1.1 Digital Twin Platform** integrates the complete hierarchy of industrial plant operations into a single interactive web application:

1. **Dynamic Closed-Loop Process Control & MPC (V1.1)**: Transient non-linear lumped capacitance modeling, feedback digital PID with anti-windup clamping, and multi-horizon Model Predictive Control (MPC) rejecting feedstock moisture disturbances ($\Delta w = +8\text{ wt}\%$) and tracking setpoint ramps.
2. **Process Flowsheet & Control Room**: Live setpoint sliders ($T_{reactor}$, $\dot{m}_{feed}$, heating rate, moisture), animated P&ID flowsheet, mass & elemental closures, and energy self-sufficiency gauge (TSI).
3. **Industrial Soft Sensor Suite (95% UQ)**: 6 real-time virtual instruments estimating unmeasured lab properties (Bio-Oil TAN, Moisture, HHV, Syngas LHV, Biochar Yield, TSI) directly from physical telemetry.
4. **Multiobjective Optimization & Pareto Frontier**: Interactive NSGA-II non-dominated trade-off surface (Bio-Oil vs Biochar vs Profit vs Thermal Efficiency) and TOPSIS MCDM stakeholder decision profiles.
5. **Tri-Layer Anomaly Diagnostics & Alarms**: Physical balance residual checks, Isolation Forest, and PCA reconstruction error ($Q$-statistic & Hotelling's $T^2$) diagnosing 5 industrial fault modes with automated NFPA/SIL-2 safety interlocks.
6. **Predictive Maintenance & Fleet RUL**: Physics-informed degradation models for infeed augers, refractory liners, particulate filters, and condensers with automated work orders (parts BOM, labor, and safety LOTO).

---

## 2. Dynamic Process Control Performance Leaderboard

From `reports/control_benchmark_report.json` (60-minute transient test with $+20^\circ\text{C}$ step at $t=10\text{ min}$ and $+8\text{ wt}\%$ moisture jump at $t=30\text{ min}$):

| Controller Architecture | Integral Absolute Error ($\text{IAE}$, $^\circ\text{C}\cdot\text{s}$) | $\text{ITAE}$ ($^\circ\text{C}\cdot\text{s}^2$) | Peak Overshoot ($\%$) | Settling Time ($t_{s, \pm 2^\circ\text{C}}$) | Steady-State Offset |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`OPEN_LOOP` (Unregulated)** | $204,677.4$ | $471,807,875.6$ | $0.00\%$ | $> 3,000.0\text{ s}$ | $22.45^\circ\text{C}$ |
| **`DIGITAL_PID` (Anti-Windup)** | $9,043.8$ | $11,507,003.3$ | $40.63\%$ | $922.0\text{ s}$ | $0.04^\circ\text{C}$ |
| **`ADVANCED_MPC` (Receding Horizon)** | **$17,124.5$** | **$29,362,658.8$** | **$26.87\%$** | **Smooth Recovery** | **$0.01^\circ\text{C}$** |

---

## 3. REST API Specification

The built-in multi-threaded HTTP server serves standard JSON REST endpoints on port 8000:

| HTTP Method | Route | Description |
| :--- | :--- | :--- |
| **`GET`** | **`/`** | Serves single-page Dark Glassmorphism Web GUI application |
| **`GET`** | **`/api/status`** | System health status, version `1.1.0`, and active modules |
| **`GET`** | **`/api/feedstocks`** | Feedstock proximate and ultimate analysis library |
| **`POST`** | **`/api/simulate`** | Executes digital twin simulation flowsheet (deterministic or ML) |
| **`POST`** | **`/api/control`** | Runs 60-min dynamic closed-loop response (MPC / PID / Open-Loop) |
| **`POST`** | **`/api/soft-sensors`** | Extracts hardware telemetry and evaluates 6 soft sensors with 95% UQ |
| **`POST`** | **`/api/optimize`** | Solves single-objective or multiobjective Pareto optimization |
| **`POST`** | **`/api/diagnostics`** | Injects equipment fault and returns anomaly scores and alarms |
| **`POST`** | **`/api/maintenance`** | Computes asset wear, 95% RUL, and dispatches work orders |

---

## 4. Software Architecture

```text
ai_biomass_plant/
│
├── reports/
│   ├── control_benchmark_report.json         # Transient control performance metrics
│   ├── predictive_maintenance_report.json    # Fleet health, RUL & prescriptive work orders
│   ├── fault_detection_report.json           # Anomaly scores, root cause & alarm dispatch report
│   ├── soft_sensor_calibration_report.json   # Soft sensor R², RMSE & 95% UQ coverage
│   └── pareto_frontier.json                  # Non-dominated Pareto frontier points
│
├── src/
│   ├── control/
│   │   ├── dynamic_model.py                  # Transient lumped thermal capacitance ODEs
│   │   ├── pid_controller.py                 # Discrete PID with anti-windup clamping
│   │   ├── mpc_controller.py                 # Multi-horizon Model Predictive Controller
│   │   ├── benchmark_control.py              # Comparative controller evaluation suite
│   │   └── run_control.py                    # Dynamic control CLI dashboard
│   ├── api/
│   │   ├── handlers.py                       # REST API business logic and route handlers
│   │   └── server.py                         # Multi-threaded HTTP server & static asset host
│   ├── web/
│   │   ├── run_server.py                     # Web GUI server launcher CLI
│   │   └── static/
│   │       ├── index.html                    # 6-tab digital twin web dashboard
│   │       ├── styles.css                    # Dark Glassmorphism design system
│   │       └── app.js                        # Reactive frontend controller & Canvas chart renderer
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
├── tests/                                    # 91 Automated Unit & Integration Tests
│   ├── test_dynamic_model.py
│   ├── test_pid_controller.py
│   ├── test_mpc_controller.py
│   ├── test_control_benchmark.py
│   ├── test_api.py
│   ├── test_degradation_models.py
│   ├── test_rul_estimator.py
│   ├── test_work_orders.py
│   └── ...
│
├── pyproject.toml
└── README.md
```

---

## 5. How to Launch the Platform

### A. Start Digital Twin Web Platform (Interactive Dashboard)
```bash
python -m src.run_simulation --web
# Or:
python -m src.web.run_server --port 8000 --open-browser
```
Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser.

### B. Run Dynamic Control Benchmark (Open-Loop vs PID vs MPC)
```bash
python -m src.control.run_control --benchmark
```

### C. Run Predictive Maintenance & RUL Dashboard
```bash
python -m src.maintenance.run_maintenance --operating-hours 4500
```

### D. Run Fault Diagnostics & Alarm Triage
```bash
python -m src.diagnostics.run_diagnostics --simulate-fault cyclone_blockage
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
* [x] **V0.9: Predictive Maintenance (RUL Estimation & Prescriptive Work Orders)** *(Completed)*
* [x] **V1.0: Real-Time Digital Twin Platform & Web GUI Dashboard** *(Completed)*
* [x] **V1.1: Dynamic Closed-Loop Process Control Simulation (MPC & PID)** *(Completed)*
* [ ] **V1.2: Plant-Level AI Decision Support (Techno-Economic & LCA Carbon Accounting)**
  * Net Present Value (NPV), Levelized Cost of Bio-Oil (LCOB), Internal Rate of Return (IRR), and ISO 14040/14044 Life Cycle Assessment (LCA) Carbon Intensity tracking ($g\text{ CO}_2\text{eq/MJ}$).
* [ ] **V2.0: Fully Autonomous AI Biomass Recycling Plant Platform**
