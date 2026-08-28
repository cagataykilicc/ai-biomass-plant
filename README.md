# AI-Integrated Biomass Recycling & Conversion Plant Digital Twin (V2.0)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Autonomous: AI Autopilot & FSM](https://img.shields.io/badge/Autonomous%20Platform-AI%20Autopilot%20%26%20FSM%20(V2.0)-gold.svg)]()
[![Flight Recorder: Blackbox Telemetry](https://img.shields.io/badge/Blackbox-Flight%20Recorder%20%26%20Historian-blueviolet.svg)]()
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
[![Tests: 100% Passed](https://img.shields.io/badge/Tests-100%2F100%20Passed-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

A complete, full-stack, first-principles chemical engineering, machine learning, and **Fully Autonomous Plant Platform (V2.0)** for biomass thermochemical recycling, supervisory autopilot finite state machine (FSM) control, blackbox flight telemetry, techno-economic feasibility (TEA), and ISO 14040/14044 Life Cycle Assessment (LCA) carbon accounting.

---

## 1. Digital Twin Architecture & Features

The **V2.0 Autonomous Plant Platform** integrates the complete hierarchy of industrial plant operations into a single interactive web application:

1. **Autonomous Supervisory Agent & Autopilot FSM (V2.0)**:
   - **Continuous Closed-Loop Operation**: Sense $\rightarrow$ Infer (Soft Sensors) $\rightarrow$ Diagnose (Tri-Layer FDD) $\rightarrow$ Optimize (NSGA-II & TOPSIS) $\rightarrow$ Actuate (MPC) $\rightarrow$ Maintain (RUL).
   - **5-State Finite State Machine**: `STARTUP_PREHEAT`, `AUTONOMOUS_CRUISE`, `DISTURBANCE_ADAPTATION`, `FAULT_MITIGATION`, and `EMERGENCY_SAFE_PARK`.
   - **Self-Healing Fault Recovery**: Autonomous nitrogen pulse-jet blowback clearing cyclone blockages without tripping the reactor.
2. **Blackbox Flight Recorder & Historian (V2.0)**:
   - Captures high-resolution telemetry, virtual soft sensor estimates, control efforts, and safety alarms into `reports/autonomous_flight_log.json`.
3. **4-Hour Multi-Phase Autonomous Stress Test Qualification (V2.0)**:
   - Simulates a 240-minute operational mission spanning Cold Startup, Nominal Cruise, Feed Moisture Jump, Cyclone Blockage self-clearing, Commercial Setpoint Shift, and Orderly Safe Park.
4. **Techno-Economic Assessment & LCA Carbon Accounting (TEA/LCA)**:
   - Guthrie Factorial Total Capital Investment ($TCI = \$609,840$), 20-Year Discounted Cash Flow ($NPV = +\$657,833$, $IRR = 24.88\%$, $LCOB = \$0.3534/\text{kg}$).
   - ISO 14040/14044 Scope 1-2-3 carbon accounting and IPCC Tier 1 solid biochar carbon permanence ($-40.88\text{ g CO}_2\text{eq/MJ}$ Net Carbon Negative).
5. **Dynamic Process Control & MPC**: Discrete PID with anti-windup clamping and multi-horizon Model Predictive Control.
6. **Process Flowsheet & Control Room**: Live setpoint sliders, animated P&ID flowsheet, mass & elemental closures, and energy self-sufficiency gauge (TSI).
7. **Industrial Soft Sensor Suite (95% UQ)**: 6 real-time virtual instruments estimating unmeasured lab properties from physical telemetry.
8. **Multiobjective Optimization & Pareto Frontier**: Interactive NSGA-II non-dominated trade-off surface and TOPSIS MCDM stakeholder decision profiles.
9. **Tri-Layer Anomaly Diagnostics & Alarms**: Physical balance residual checks, Isolation Forest, and PCA reconstruction error ($Q$-statistic & Hotelling's $T^2$).
10. **Predictive Maintenance & Fleet RUL**: Physics-informed degradation kinematics for infeed augers, refractory liners, particulate filters, and condensers with prescriptive work orders.

---

## 2. 4-Hour Autonomous Flight Qualification Leaderboard

From `reports/autonomous_flight_log.json`:

```text
==================================================================================
       AI-INTEGRATED BIOMASS CONVERSION PLANT - V2.0
     (Fully Autonomous AI Autopilot Mission Qualification)
==================================================================================
Mission Title       : 4-Hour Autonomous Operational Qualification Mission
Total Flight Time   : 4.0 Hours (240 Minutes)
Overall Mission     : [MISSION_SUCCESS]

MISSION PHASES FLIGHT TIMELINE
----------------------------------------------------------------------------------
Phase                                  Window         Temp Trange    End FSM State
----------------------------------------------------------------------------------
Phase 1: Cold Startup & Thermal Ramp   0 - 25 min     120 -> 483°C   [AUTONOMOUS_CRUISE]
Phase 2: Autonomous Nominal Cruise     25 - 75 min    483 -> 497°C   [AUTONOMOUS_CRUISE]
Phase 3: High-Moisture Feed Disturbance 75 - 130 min   497 -> 503°C   [DISTURBANCE_ADAPTATION]
Phase 4: Cyclone Blockage Fault & Pulse-Jet Mitigation 130 - 180 min  503 -> 497°C   [AUTONOMOUS_CRUISE]
Phase 5: Commercial Setpoint Shift (Biochar Carbon Max) 180 - 220 min  497 -> 422°C   [AUTONOMOUS_CRUISE]
Phase 6: Orderly Safe Park & Cool-Down 220 - 240 min  422 -> 241°C   [AUTONOMOUS_CRUISE]
----------------------------------------------------------------------------------
Flight Recorder Log : reports/autonomous_flight_log.json
==================================================================================
```

---

## 3. REST API Specification

The built-in multi-threaded HTTP server serves standard JSON REST endpoints on port 8000:

| HTTP Method | Route | Description |
| :--- | :--- | :--- |
| **`GET`** | **`/`** | Serves single-page Dark Glassmorphism Web GUI application |
| **`GET`** | **`/api/status`** | System health status, version `2.0.0`, and active modules |
| **`GET`** | **`/api/feedstocks`** | Feedstock proximate and ultimate analysis library |
| **`POST`** | **`/api/simulate`** | Executes digital twin simulation flowsheet (deterministic or ML) |
| **`POST`** | **`/api/autopilot/step`** | Advances closed-loop autonomous autopilot FSM by one step |
| **`POST`** | **`/api/autopilot/mission`** | Executes full 4-hour qualification stress test mission |
| **`POST`** | **`/api/economics`** | Runs 20-yr DCF NPV/IRR/LCOB and ISO 14040/14044 LCA carbon metrics |
| **`POST`** | **`/api/control`** | Runs 60-min dynamic closed-loop response (MPC / PID / Open-Loop) |
| **`POST`** | **`/api/soft-sensors`** | Extracts hardware telemetry and evaluates 6 soft sensors with 95% UQ |
| **`POST`** | **`/api/optimize`** | Solves single-objective or multiobjective Pareto optimization |
| **`POST`** | **`/api/diagnostics`** | Injects equipment fault and returns anomaly scores and alarms |
| **`POST`** | **`/api/maintenance`** | Computes asset wear, 95% RUL, and dispatches work orders |

---

## 4. How to Launch the Platform

### A. Start Digital Twin Web Platform (Interactive 8-Tab Dashboard)
```bash
python -m src.run_simulation --web
# Or:
python -m src.web.run_server --port 8000 --open-browser
```
Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser.

### B. Execute Autonomous Autopilot Mission Qualification
```bash
python -m src.autonomous.run_autopilot --mission
```

### C. Run Techno-Economic & LCA Carbon Accounting Dashboard
```bash
python -m src.economics.run_economics --feedstock olive_pomace
```

### D. Run Dynamic Control Benchmark (Open-Loop vs PID vs MPC)
```bash
python -m src.control.run_control --benchmark
```

### E. Run Unit Test Suite
```bash
pytest tests/ -v
```

---

## 5. Completed Roadmap

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
* [x] **V2.0: Fully Autonomous AI Biomass Recycling Plant Platform** *(Completed)*
