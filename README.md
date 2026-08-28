# AI-Integrated Biomass Recycling & Conversion Plant Digital Twin (V0.9)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Predictive Maintenance: 95% RUL](https://img.shields.io/badge/PdM-RUL%20Prognostics%20%26%20Work%20Orders-darkgreen.svg)]()
[![Diagnostics: Tri--Layer FDD](https://img.shields.io/badge/Diagnostics-Tri--Layer%20FDD%20%26%20Alarms-critical.svg)]()
[![Soft Sensors: 6 Virtual Gauges](https://img.shields.io/badge/Soft%20Sensors-6%20Inferential%20Gauges%20(95%25%20UQ)-blueviolet.svg)]()
[![Optimization: NSGA--II Pareto & TOPSIS](https://img.shields.io/badge/Optimization-Pareto%20%26%20TOPSIS%20MCDM-blue.svg)]()
[![Champion ML: Gradient Boosting](https://img.shields.io/badge/Champion%20Model-Gradient%20Boosting%20(R%C2%B2%200.9981)-blueviolet.svg)]()
[![Physics: 100% Mass Conserved](https://img.shields.io/badge/Physics%20Constraint-Simplex%20Projection%20(100%25)-darkgreen.svg)]()
[![Tests: 100% Passed](https://img.shields.io/badge/Tests-77%2F77%20Passed-brightgreen.svg)]()
[![Thermal Status: Self--Sufficient](https://img.shields.io/badge/Thermal%20Status-Autonomous%20(TSI%20111.3%25)-darkgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

A modular, first-principles chemical engineering and digital twin platform for biomass thermal conversion, predictive maintenance (PdM) with 95% Remaining Useful Life (RUL) estimation, real-time inferential soft sensors, process anomaly detection, equipment fault diagnosis, and multiobjective process optimization.

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
* **Physics-Informed Constraint Projection**: Exact $100.00\%$ mass conservation
* **AI-Driven Process Optimization & Pareto Frontier Engine**: SLSQP, Differential Evolution, NSGA-II, and TOPSIS MCDM
* **Industrial Soft Sensors with 95% UQ**: Real-time inferential estimation of unmeasured lab stream properties
* **Tri-Layer Anomaly Detection & Fault Diagnosis**: Isolation Forest, PCA reconstruction error ($Q$ & $T^2$), and NFPA/IEC safety alarms
* **Predictive Maintenance & RUL Prognostics**: Physics-informed degradation models for infeed augers, refractory liners, particulate filters, and condensers with automated work order generation

---

## 2. Predictive Maintenance & Asset Prognostics (V0.9)

```text
  +-----------------------------------------------------------------------------------+
  |                       OPERATING ASSET WEAR & DEGRADATION                          |
  |  Auger Flight Thinning, Refractory Spalling, Filter Blinding, Condenser Corrosion  |
  +---------------------------------------+-------------------------------------------+
                                          |
                                          v
               +----------------------------------------------------+
               |         PHYSICS-INFORMED DEGRADATION KINETICS      |
               |  * Archard Abrasive Wear: dW/dt = f(m, Ash, Vib)   |
               |  * Refractory Spalling: dD/dt = f(T_bed, N_cycles) |
               |  * Filter Blinding: dP(t) = dP_0 * (1 + k*t)^1.35  |
               |  * Acid Corrosion: dC/dt = f(TAN, Moisture)        |
               +--------------------------+-------------------------+
                                          |
                                          v
               +----------------------------------------------------+
               |      HEALTH INDEX & RUL PROGNOSTICS ENGINE (95% UQ)|
               |  * Dynamic Health Index HI(t) in [100%, 0%]        |
               |  * Remaining Useful Life (RUL in Operating Hours)  |
               |  * Calibrated 95% Confidence Interval [Lo, Hi]     |
               |  * Fleet Bottleneck Identification                 |
               +--------------------------+-------------------------+
                                          |
                                          v
               +----------------------------------------------------+
               |       PRESCRIPTIVE WORK ORDER & LOTO MANAGER       |
               |  * Urgency Triage: HEALTHY, PLANNED, URGENT, CRIT  |
               |  * Spare Parts Bill of Materials (BOM) & Inventory |
               |  * Estimated Labor Hours & Technician Crew Sizing  |
               |  * Safety Lockout / Tagout (LOTO) Protocols        |
               +----------------------------------------------------+
```

---

## 3. Fleet Health & RUL Summary at 4,500 Operating Hours

From `reports/predictive_maintenance_report.json`:

| Asset ID | Component Name | Current Health ($HI\%$) | Physical Wear State | Estimated RUL | 95% Confidence Interval | Urgency Level |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`AUGER_A101`** | **Biomass Infeed Auger Screw** | $49.3\%$ | $3.04\text{ / }6.0\text{ mm}$ wear | $4,376\text{ h}$ | $[3,697 - 5,054]\text{ h}$ | `PLANNED_MAINTENANCE` |
| **`REACTOR_R101_LINER`** | **Refractory Bed Liner [BOTTLENECK]** | **$38.6\%$** | $24.57\text{ / }40.0\text{ mm}$ loss | **$2,826\text{ h}$** | **$[2,360 - 3,292]\text{ h}$** | **`PLANNED_MAINTENANCE`** |
| **`FILTER_F101`** | **Syngas Ceramic Filter** | $48.3\%$ | $7.17\text{ / }12.0\text{ kPa}$ $\Delta P$ | $4,204\text{ h}$ | $[3,549 - 4,859]\text{ h}$ | `PLANNED_MAINTENANCE` |
| **`CONDENSER_HX102`** | **Condenser Tube Bundle** | $55.0\%$ | $0.68\text{ / }1.5\text{ mm}$ corrosion | $5,500\text{ h}$ | $[4,667 - 6,333]\text{ h}$ | `PLANNED_MAINTENANCE` |

---

## 4. Software Architecture

```text
ai_biomass_plant/
│
├── reports/
│   ├── predictive_maintenance_report.json    # Fleet health, RUL & prescriptive work orders
│   ├── fault_detection_report.json           # Anomaly scores, root cause & alarm dispatch report
│   ├── soft_sensor_calibration_report.json   # Soft sensor R², RMSE & 95% UQ coverage
│   ├── process_optimization_report.json      # Optimal operational setpoints
│   └── pareto_frontier.json                  # Non-dominated Pareto frontier points
│
├── src/
│   ├── maintenance/
│   │   ├── degradation_models.py             # Wear trajectory models for 4 critical assets
│   │   ├── rul_estimator.py                  # Health index & RUL with 95% confidence intervals
│   │   ├── work_order_manager.py             # Work order generator with BOM & safety LOTO
│   │   └── run_maintenance.py                # Predictive maintenance CLI dashboard
│   ├── diagnostics/                          # Fault simulation, anomaly detector & alarms
│   ├── sensors/                              # Hardware telemetry & 6 Soft Sensors (95% UQ)
│   ├── optimization/                         # SLSQP, Differential Evolution, Pareto & TOPSIS
│   ├── ml/                                   # Surrogate models & physics constraints
│   ├── process/                              # Unit operations & balance engines
│   ├── simulation/
│   │   └── plant_simulator.py                # Hybrid simulation engine orchestrator
│   └── run_simulation.py                     # CLI application entry point
│
├── tests/                                    # 77 Automated Unit & Integration Tests
│   ├── test_degradation_models.py
│   ├── test_rul_estimator.py
│   ├── test_work_orders.py
│   ├── test_fault_simulator.py
│   ├── test_anomaly_detector.py
│   ├── test_fault_diagnostics.py
│   ├── test_alarm_manager.py
│   └── ...
│
├── pyproject.toml
└── README.md
```

---

## 5. How to Run the Platform

### A. Run Predictive Maintenance & RUL Dashboard
```bash
python -m src.maintenance.run_maintenance --operating-hours 4500
```

### B. Run Simulation with Integrated Maintenance Health Assessment
```bash
python -m src.run_simulation --predictive-maintenance --operating-hours 5200 --feedstock pine_sawdust
```

### C. Run Fault Diagnostics & Alarm Triage
```bash
python -m src.diagnostics.run_diagnostics --simulate-fault cyclone_blockage --severity 0.85
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
* [ ] **V1.0: Real-Time Digital Twin Prototype (FastAPI Backend + Streamlit Web GUI Dashboard)**
  * Unified interactive web interface with live flowsheet visualization, real-time PID controls, scenario analysis, and live soft sensor telemetry.
* [ ] **V1.1: Dynamic Closed-Loop Process Control Simulation (MPC / PID)**
* [ ] **V1.2: Plant-Level AI Decision Support (Techno-Economic & LCA Carbon Accounting)**
* [ ] **V2.0: Fully Autonomous AI Biomass Recycling Plant Platform**
