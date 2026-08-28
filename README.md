# AI-Integrated Biomass Recycling & Conversion Plant Digital Twin (V0.7)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Soft Sensors: 6 Virtual Gauges](https://img.shields.io/badge/Soft%20Sensors-6%20Inferential%20Gauges%20(95%25%20UQ)-blueviolet.svg)]()
[![Optimization: NSGA--II Pareto & TOPSIS](https://img.shields.io/badge/Optimization-Pareto%20%26%20TOPSIS%20MCDM-blue.svg)]()
[![Champion ML: Gradient Boosting](https://img.shields.io/badge/Champion%20Model-Gradient%20Boosting%20(R%C2%B2%200.9981)-blueviolet.svg)]()
[![Physics: 100% Mass Conserved](https://img.shields.io/badge/Physics%20Constraint-Simplex%20Projection%20(100%25)-darkgreen.svg)]()
[![Tests: 100% Passed](https://img.shields.io/badge/Tests-67%2F67%20Passed-brightgreen.svg)]()
[![Thermal Status: Self--Sufficient](https://img.shields.io/badge/Thermal%20Status-Autonomous%20(TSI%20111.3%25)-darkgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

A modular, first-principles chemical engineering and digital twin platform for biomass thermal conversion, real-time inferential soft sensors with 95% Uncertainty Quantification (UQ), multi-model AI benchmarking, and AI-driven multiobjective process optimization.

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
* **Multi-Model Machine Learning Benchmarking**: Comparing Random Forest, Extra Trees, Gradient Boosting, HistGB, MLP Neural Network, and Ridge
* **Physics-Informed Constraint Projection**: Guarantees exact $100.00\%$ mass conservation and non-negativity across solid biochar, liquid bio-oil, and gaseous syngas
* **AI-Driven Process Optimization & Pareto Frontier Engine**: SLSQP, Differential Evolution, NSGA-II, and TOPSIS Multi-Criteria Decision Support
* **Industrial Soft Sensors with 95% Uncertainty Quantification**: Real-time inferential estimation of unmeasured lab stream properties (Bio-oil TAN, Moisture, HHV, Syngas LHV, Biochar Yield, TSI) directly from physical telemetry

---

## 2. Industrial Soft Sensor Suite (V0.7)

In commercial conversion plants, lab-based stream analyses suffer from multi-hour sampling delays. The soft sensor suite estimates these unmeasured stream properties in real-time from physical hardware telemetry ($\text{TI-101}$ to $\text{TI-106}$, $\text{FI-101}$ to $\text{FI-103}$, $\text{PI-101}$):

| Tag | Stream Property Measured | Unit | $R^2$ Score | Test RMSE | 95% Prediction Interval Coverage (PICP) |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **`SS_101`** | **Bio-Oil Total Acid Number (TAN)** | $\text{mg KOH/g}$ | **$0.9528$** | $2.69$ | **$93.5\%$** |
| **`SS_102`** | **Bio-Oil Water Content** | $\text{wt}\%$ | **$0.9088$** | $1.94$ | **$95.0\%$** |
| **`SS_103`** | **Bio-Oil Higher Heating Value (HHV)** | $\text{MJ/kg}$ | **$0.7221$** | $0.97$ | **$95.0\%$** |
| **`SS_104`** | **Clean Syngas Volumetric LHV** | $\text{MJ/Nm}^3$ | **$0.9998$** | $0.03$ | **$93.0\%$** |
| **`SS_105`** | **Biochar Solids Yield** | $\text{wt}\%$ | **$0.9462$** | $3.41$ | **$94.0\%$** |
| **`SS_106`** | **Thermal Self-Sufficiency Index (TSI)** | $\%$ | **$0.8712$** | $29.23$ | **$87.0\%$** |

---

## 3. Real-Time Telemetry & Virtual Gauge Dashboard

```text
==============================================================================
       AI-INTEGRATED BIOMASS CONVERSION PLANT - V0.7
    (Industrial Soft Sensor Suite & 95% Uncertainty Quantification)
==============================================================================
Timestamp            : 2026-08-28T19:35:17.282529
Feedstock Assumed    : Pine Sawdust

ONLINE HARDWARE INSTRUMENT TELEMETRY (Physical Sensors)
------------------------------------------------------------------------------
  TI-101 (Dryer Inlet Temp)     :  181.0 °C   | FI-101 (Biomass Feed Rate)   :  100.0 kg/h
  TI-102 (Dryer Exit Temp)      :  105.4 °C   | FI-102 (Cooling Water Rate)  : 1984.2 kg/h
  TI-103 (Reactor Bed Temp)     :  519.5 °C   | FI-103 (Combustion Air Rate) :  101.6 kg/h
  TI-104 (Cyclone Vapor Temp)   :  505.0 °C   | PI-101 (Bed Delta Pressure)  :   4.49 kPa
  TI-105 (Condenser Gas Temp)   :   34.3 °C   | TI-106 (Flue Gas Temp)       : 1398.0 °C

INFERENTIAL SOFT SENSORS (Real-Time Virtual State Estimation)
------------------------------------------------------------------------------
Tag        Stream Property                Estimate   95% Pred Interval    Status
------------------------------------------------------------------------------
SS_101_BIO_OIL_TAN Bio-Oil Total Acid Number      97.53 mg KOH/g [93.38 - 101.67]     NORMAL
SS_102_BIO_OIL_WATER Bio-Oil Water Content          26.81 wt%  [21.38 - 32.24]      NORMAL
SS_103_BIO_OIL_HHV Bio-Oil Higher Heating Value   11.65 MJ/kg [8.18 - 15.11]       HIGH_UNCERTAINTY
SS_104_SYNGAS_LHV Clean Syngas Volumetric LHV    13.96 MJ/Nm³ [13.71 - 14.21]      NORMAL
SS_105_BIOCHAR_YIELD Biochar Solids Yield           33.20 wt%  [24.79 - 41.62]      NORMAL
SS_106_TSI Thermal Self-Sufficiency Index 103.64 %   [60.35 - 146.93]     HIGH_UNCERTAINTY
==============================================================================
```

---

## 4. Software Architecture

```text
ai_biomass_plant/
│
├── models/
│   └── checkpoints/
│       ├── soft_sensors.joblib               # 6 Serialized inferential virtual sensors
│       └── yield_predictor_champion.joblib   # Production champion yield surrogate
│
├── reports/
│   ├── soft_sensor_calibration_report.json   # Soft sensor R², RMSE & 95% UQ coverage
│   ├── process_optimization_report.json      # Optimal operational setpoints
│   ├── pareto_frontier.json                  # Non-dominated Pareto frontier points
│   └── ml_multimodel_benchmark.json          # Multi-model leaderboard & latency report
│
├── src/
│   ├── sensors/
│   │   ├── telemetry.py                      # Hardware telemetry packets & noise injection
│   │   ├── soft_sensor_engine.py             # 6 Inferential virtual sensors with UQ
│   │   ├── calibration.py                    # Training & uncertainty calibration engine
│   │   └── run_soft_sensors.py               # Soft sensor virtual gauge CLI dashboard
│   ├── optimization/                         # SLSQP, Differential Evolution, Pareto & TOPSIS
│   ├── ml/                                   # Surrogate models & physics constraints
│   ├── process/                              # Unit operations & balance engines
│   ├── simulation/
│   │   └── plant_simulator.py                # Hybrid simulation engine orchestrator
│   └── run_simulation.py                     # CLI application entry point
│
├── tests/                                    # 67 Automated Unit & Integration Tests
│   ├── test_telemetry.py
│   ├── test_soft_sensors.py
│   ├── test_calibration.py
│   ├── test_objectives.py
│   ├── test_optimizer.py
│   ├── test_pareto.py
│   ├── test_decision_maker.py
│   └── ...
│
├── pyproject.toml
└── README.md
```

---

## 5. How to Run the Platform

### A. Run Real-Time Inferential Soft Sensor Dashboard
```bash
python -m src.sensors.run_soft_sensors --feedstock pine_sawdust --temp 520
```

### B. Run Simulation with Integrated Soft Sensors
```bash
python -m src.run_simulation --soft-sensors --feedstock olive_pomace
```

### C. Run Soft Sensor Calibration & UQ Benchmark
```bash
python -m src.sensors.calibration
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
* [ ] **V0.8: Anomaly & Fault Detection (Autoencoders / Isolation Forests)**
  * Online detection of sensor drift, cyclone blockages, condenser fouling, and runaway temperatures.
* [ ] **V0.9: Predictive Maintenance (RUL of Augers, Refractory, Filters)**
* [ ] **V1.0: Real-Time Digital Twin Prototype (FastAPI + Streamlit GUI)**
* [ ] **V1.1: Dynamic Closed-Loop Process Control Simulation (MPC / PID)**
* [ ] **V1.2: Plant-Level AI Decision Support (Techno-Economic & LCA Carbon Accounting)**
* [ ] **V2.0: Fully Autonomous AI Biomass Recycling Plant Platform**
