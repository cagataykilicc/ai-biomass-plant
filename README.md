# AI-Integrated Biomass Recycling & Conversion Plant Digital Twin (V1.2)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Economics: Guthrie TEA & 20-Yr DCF](https://img.shields.io/badge/Economics-Guthrie%20TEA%20%26%2020--Yr%20DCF-gold.svg)]()
[![LCA: ISO 14040/14044 Carbon](https://img.shields.io/badge/LCA-ISO%2014040%2F14044%20Carbon%20Negative-darkgreen.svg)]()
[![Control: Dynamic MPC & PID](https://img.shields.io/badge/Process%20Control-Dynamic%20MPC%20%26%20PID-blue.svg)]()
[![Web Platform: Glassmorphism GUI](https://img.shields.io/badge/Web%20Platform-Interactive%20Dark%20Glassmorphism-cyan.svg)]()
[![REST API: Zero--Dependency](https://img.shields.io/badge/REST%20API-Zero--Dependency%20HTTP-blueviolet.svg)]()
[![Predictive Maintenance: 95% RUL](https://img.shields.io/badge/PdM-RUL%20Prognostics%20%26%20Work%20Orders-darkgreen.svg)]()
[![Diagnostics: Tri--Layer FDD](https://img.shields.io/badge/Diagnostics-Tri--Layer%20FDD%20%26%20Alarms-critical.svg)]()
[![Soft Sensors: 6 Virtual Gauges](https://img.shields.io/badge/Soft%20Sensors-6%20Inferential%20Gauges%20(95%25%20UQ)-blueviolet.svg)]()
[![Optimization: NSGA--II Pareto & TOPSIS](https://img.shields.io/badge/Optimization-Pareto%20%26%20TOPSIS%20MCDM-blue.svg)]()
[![Champion ML: Gradient Boosting](https://img.shields.io/badge/Champion%20Model-Gradient%20Boosting%20(R%C2%B2%200.9981)-blueviolet.svg)]()
[![Physics: 100% Mass Conserved](https://img.shields.io/badge/Physics%20Constraint-Simplex%20Projection%20(100%25)-darkgreen.svg)]()
[![Tests: 100% Passed](https://img.shields.io/badge/Tests-95%2F95%20Passed-brightgreen.svg)]()
[![Thermal Status: Self--Sufficient](https://img.shields.io/badge/Thermal%20Status-Autonomous%20(TSI%20111.3%25)-darkgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

A complete, full-stack, first-principles chemical engineering and machine learning **Digital Twin Platform** for biomass thermochemical recycling, process control, techno-economic feasibility (TEA), and ISO 14040/14044 Life Cycle Assessment (LCA) carbon accounting.

---

## 1. Digital Twin Architecture & Features

The **V1.2 Digital Twin Platform** integrates the complete hierarchy of industrial plant operations into a single interactive web application:

1. **Techno-Economic Assessment & LCA Carbon Accounting (V1.2)**:
   - **Guthrie Factorial CAPEX/OPEX**: Sizing and costing for all 8 major equipment units with direct/indirect installation multipliers.
   - **20-Year Discounted Cash Flow (DCF)**: 10% discount rate, 25% tax rate, 7-year MACRS depreciation evaluating Net Present Value ($\text{NPV} = +\$657,833$), $\text{IRR} = 24.88\%$, and Levelized Cost of Bio-Oil ($\text{LCOB} = \$0.3534/\text{kg}$).
   - **ISO 14040/14044 Cradle-to-Gate LCA**: Scope 1 direct, Scope 2 grid electricity, Scope 3 biomass supply chain, and IPCC Tier 1 solid biochar carbon permanence ($>80\%$ stability for $>100$ years) demonstrating verified **Net-Negative Carbon Intensity ($-40.88\text{ g CO}_2\text{eq/MJ}$)**.
2. **Dynamic Closed-Loop Process Control & MPC**: Transient non-linear lumped capacitance modeling, feedback digital PID with anti-windup clamping, and multi-horizon Model Predictive Control (MPC) rejecting feedstock moisture disturbances ($\Delta w = +8\text{ wt}\%$) and tracking setpoint ramps.
3. **Process Flowsheet & Control Room**: Live setpoint sliders ($T_{reactor}$, $\dot{m}_{feed}$, heating rate, moisture), animated P&ID flowsheet, mass & elemental closures, and energy self-sufficiency gauge (TSI).
4. **Industrial Soft Sensor Suite (95% UQ)**: 6 real-time virtual instruments estimating unmeasured lab properties (Bio-Oil TAN, Moisture, HHV, Syngas LHV, Biochar Yield, TSI) directly from physical telemetry.
5. **Multiobjective Optimization & Pareto Frontier**: Interactive NSGA-II non-dominated trade-off surface (Bio-Oil vs Biochar vs Profit vs Thermal Efficiency) and TOPSIS MCDM stakeholder decision profiles.
6. **Tri-Layer Anomaly Diagnostics & Alarms**: Physical balance residual checks, Isolation Forest, and PCA reconstruction error ($Q$-statistic & Hotelling's $T^2$) diagnosing 5 industrial fault modes with automated NFPA/SIL-2 safety interlocks.
7. **Predictive Maintenance & Fleet RUL**: Physics-informed degradation models for infeed augers, refractory liners, particulate filters, and condensers with automated work orders (parts BOM, labor, and safety LOTO).

---

## 2. Techno-Economic & LCA Carbon Profile Preview

From `reports/techno_economic_lca_report.json` (Olive Pomace @ $100\text{ kg/h}$ / $800\text{ t/yr}$):

```text
==============================================================================
       AI-INTEGRATED BIOMASS CONVERSION PLANT - V1.2
 (Techno-Economic Assessment & ISO 14040/14044 LCA Carbon Accounting)
==============================================================================
Feedstock Profile       : Olive Pomace (100.0 kg/h | 800 t/yr)
Reactor Operating Temp  : 500 °C

CAPITAL & OPERATING EXPENDITURE (Guthrie Factorial)
------------------------------------------------------------------------------
Total Purchased Equipment (PEC) : $308,000.00
Fixed Capital Investment (FCI)  : $554,400.00
Total Capital Investment (TCI)  : $609,840.00
Annual OPEX (8,000 h/yr)        : $169,048.00 ($211.31/t feed)

20-YEAR DISCOUNTED CASH FLOW & FINANCIAL VIABILITY (10% Discount Rate)
------------------------------------------------------------------------------
Annual Gross Revenue            : $350,631.15
Net Present Value (NPV)         : $657,833.50
Internal Rate of Return (IRR)   : 24.88%
Discounted Payback Period       : 5.12 Years
Levelized Cost of Bio-Oil (LCOB): $0.3534/kg ($0.0202/MJ)
Commercial Project Status       : [VIABLE - MEETS 10% HURDLE RATE]

ISO 14040/14044 LCA & CARBON SEQUESTRATION PROFILE
------------------------------------------------------------------------------
Scope 1 Direct Emissions        : 11,610.0 kg CO2eq/yr
Scope 2 Grid Power Emissions    : 106,400.0 kg CO2eq/yr
Scope 3 Supply Chain Emissions  : 36,000.0 kg CO2eq/yr
Total Gross Emissions           : 154,010.0 kg CO2eq/yr
Biochar Carbon Sequestration    : -419,199.6 kg CO2eq/yr (419.2 t CO2/yr)
Certified CORC Credit Revenue   : +$27,247.97/yr (@ $65/t CO2)
Net Life Cycle GHG Balance      : -265,189.6 kg CO2eq/yr
Net Carbon Intensity (Bio-Oil)  : -40.88 g CO2eq/MJ
Net Carbon Removal Efficiency   : 331.5 kg CO2eq removed / tonne biomass
Climate Impact Status           : [NET CARBON NEGATIVE (CARBON REMOVAL SYSTEM)]
==============================================================================
```

---

## 3. REST API Specification

The built-in multi-threaded HTTP server serves standard JSON REST endpoints on port 8000:

| HTTP Method | Route | Description |
| :--- | :--- | :--- |
| **`GET`** | **`/`** | Serves single-page Dark Glassmorphism Web GUI application |
| **`GET`** | **`/api/status`** | System health status, version `1.2.0`, and active modules |
| **`GET`** | **`/api/feedstocks`** | Feedstock proximate and ultimate analysis library |
| **`POST`** | **`/api/simulate`** | Executes digital twin simulation flowsheet (deterministic or ML) |
| **`POST`** | **`/api/economics`** | Runs 20-yr DCF NPV/IRR/LCOB and ISO 14040/14044 LCA carbon metrics |
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
│   ├── techno_economic_lca_report.json       # 20-yr DCF, NPV, IRR, LCOB & Scope 1-2-3 emissions
│   ├── control_benchmark_report.json         # Transient control performance metrics
│   ├── predictive_maintenance_report.json    # Fleet health, RUL & prescriptive work orders
│   ├── fault_detection_report.json           # Anomaly scores, root cause & alarm dispatch report
│   ├── soft_sensor_calibration_report.json   # Soft sensor R², RMSE & 95% UQ coverage
│   └── pareto_frontier.json                  # Non-dominated Pareto frontier points
│
├── src/
│   ├── economics/
│   │   ├── tea_engine.py                     # Guthrie factorial Capex/Opex, 20-yr DCF, NPV, IRR, LCOB
│   │   ├── lca_engine.py                     # ISO 14040/14044 Scope 1-2-3 LCA & Carbon Sequestration
│   │   └── run_economics.py                  # CLI financial & carbon analysis runner
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
│   │       ├── index.html                    # 7-tab digital twin web dashboard
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
├── tests/                                    # 95 Automated Unit & Integration Tests
│   ├── test_tea_engine.py
│   ├── test_lca_engine.py
│   ├── test_dynamic_model.py
│   ├── test_pid_controller.py
│   ├── test_mpc_controller.py
│   ├── test_control_benchmark.py
│   ├── test_api.py
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

### B. Run Techno-Economic & LCA Carbon Accounting Dashboard
```bash
python -m src.economics.run_economics --feedstock olive_pomace
```

### C. Run Dynamic Control Benchmark (Open-Loop vs PID vs MPC)
```bash
python -m src.control.run_control --benchmark
```

### D. Run Predictive Maintenance & RUL Dashboard
```bash
python -m src.maintenance.run_maintenance --operating-hours 4500
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
* [x] **V1.2: Plant-Level AI Decision Support (Techno-Economic & LCA Carbon Accounting)** *(Completed)*
* [ ] **V2.0: Fully Autonomous AI Biomass Recycling Plant Platform**
  * Autonomous self-optimizing supervisory agent, closed-loop telemetry streaming, automated setpoint dispatch, and end-to-end plant operations autopilot.
