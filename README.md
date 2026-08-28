# AI-Integrated Biomass Recycling & Conversion Plant Digital Twin

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Architecture: Chemical Engineering & Digital Twin](https://img.shields.io/badge/Architecture-Modular%20Process%20Systems-green.svg)]()
[![Tests: 100% Passed](https://img.shields.io/badge/Tests-29%2F29%20Passed-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

A modular, first-principles chemical engineering and digital twin platform for biomass thermal conversion and recycling processes.

---

## 1. Project Objective

The objective is to progressively develop a realistic digital representation of a commercial-scale biomass conversion plant that seamlessly unifies:

* Rigorous chemical engineering calculations & thermodynamics
* Multi-stage process unit operations (drying, pyrolysis, cyclone, condensation)
* First-principles mass and energy balance verification
* Parametric sensitivity and process scenario management
* Machine learning integration & soft sensors (*future roadmap*)
* AI-driven multiobjective optimization & predictive maintenance (*future roadmap*)
* Plant-level digital twin supervisory control (*future roadmap*)

---

## 2. Process Flowsheet (V0.1)

```text
               +--------------------+
               |  Raw Biomass Feed  |
               | (Moisture: 10-50%) |
               +---------+----------+
                         |
                         v
              +----------------------+
              |  Drying Unit (D101)  | ----> [ Water Vapor Exhaust S105 ]
              |    (T = 105 °C)      |
              +----------+-----------+
                         |
                         v [ Dried Biomass S103 ]
              +----------------------+
              |  Pyrolysis Reactor   |
              |       (R101)         |
              | (T = 300 - 800 °C)   |
              +----------+-----------+
                         |
                         v [ Hot Multiphase Effluent S104 ]
              +----------------------+
              |  Cyclone Separator   | ----> [ Recovered Biochar S106 ]
              |       (C101)         | ----> [ Particulate Fines Loss S109 ]
              +----------+-----------+
                         |
                         v [ Hot Clean Vapors ]
              +----------------------+
              |  Condenser Train     | ----> [ Liquid Bio-Oil S107 ]
              |    (E101 / E102)     | ----> [ Clean Fuel Syngas S108 ]
              +----------------------+
```

---

## 3. Current Capabilities (Version 0.1)

* **Structured Feedstock Modeling**: Complete Ultimate (C, H, O, N, S, Ash), Proximate (Moisture, VM, FC, Ash), and Physical properties (particle size, bulk density, porosity).
* **Unified Thermodynamic Properties**: Channiwala & Parikh (2002) HHV correlation, Lower Heating Value (LHV) conversion for dry and as-received bases, temperature-dependent specific heat capacities $C_p(T)$.
* **Thermodynamic Drying Model**: Sensible solid/liquid heating, latent heat of vaporization ($\Delta H_{vap} = 2257 \text{ kJ/kg}$), steam superheating, thermal efficiency, and auxiliary electric power.
* **Phenomenological Pyrolysis Reactor & Yield Kinetics**: Multi-component sigmoidal kinetic correlations linking temperature ($300\text{--}800^\circ\text{C}$), heating rate ($\beta = 1\text{--}1000^\circ\text{C/min}$), and residence time to biochar, bio-oil, and syngas yields.
* **Strict Mass Conservation**: Normalized yields ($Y_{char} + Y_{oil} + Y_{gas} = 1.000000$), ash partitioning, and water distribution.
* **Separation & Condensation Train**: Cyclone particulate capture ($\eta_{cyc} \ge 98\%$), multi-stage condenser bio-oil recovery ($\eta_{cond} \ge 96\%$), cooling duties, and cooling water utility sizing.
* **Mass & Energy Balances**: 100.00% stream-by-stream closure verification, chemical power accounting, Net Thermal Efficiency, and Energy Recovery Ratio.
* **CLI & Scenario Engine**: YAML-based configuration management and interactive terminal dashboard.

---

## 4. Governing Chemical Engineering Equations

### 4.1 Feedstock Higher & Lower Heating Values (HHV / LHV)

* **Channiwala & Parikh (2002) Unified HHV Equation (Dry Basis)**:
  $$HHV_{dry} = 0.3491\,C + 1.1783\,H + 0.1005\,S - 0.1034\,O - 0.0151\,N - 0.0211\,Ash \quad (\text{MJ/kg})$$
* **Lower Heating Value (Dry Basis)**:
  $$LHV_{dry} = HHV_{dry} - 2.442 \times \left( \frac{8.936 \times H}{100} \right) \quad (\text{MJ/kg})$$
* **As-Received Lower Heating Value**:
  $$LHV_{ar} = LHV_{dry} \times (1 - w) - 2.442 \times w \quad (\text{MJ/kg})$$
  *(where $w = \text{Moisture} / 100$)*

* **Biomass Temperature-Dependent Specific Heat Capacity ($C_p$)**:
  $$C_{p,bio}(T) = 1.112 + 0.00485\,T \quad (\text{kJ/kg}\cdot\text{K}, \; T \in [20, 800]^\circ\text{C})$$

---

### 4.2 Biomass Drying Unit Operation

* **Evaporated Moisture Flow**:
  $$\dot{m}_{water,evap} = \dot{m}_{feed,ar} \times \left( \frac{w_{in} - w_{out}}{100 - w_{out}} \right) \quad (\text{kg/h})$$
* **Dried Biomass Flow**:
  $$\dot{m}_{dried} = \dot{m}_{feed,ar} - \dot{m}_{water,evap} = \frac{\dot{m}_{feed,ar}(1 - w_{in}/100)}{1 - w_{out}/100} \quad (\text{kg/h})$$
* **Thermal Energy Requirement**:
  $$Q_{dry,th} = \dot{m}_{dry\_matter} C_{p,bio}(T_{dry} - T_0) + \dot{m}_{evap} \left[ C_{p,w}(100 - T_0) + \Delta H_{vap} + C_{p,steam}(T_{dry} - 100) \right]$$
  $$Q_{dry,actual} = \frac{Q_{dry,th}}{\eta_{dryer}} \quad (\text{kW})$$

---

### 4.3 Pyrolysis Product Yields & Reaction Enthalpy

* **DAF Biochar Yield**:
  $$y_{char,base}(T) = y_{char,min} + \frac{y_{char,max} - y_{char,min}}{1 + \exp\left(\frac{T - T_{char,mid}}{s_{char}}\right)}$$
* **DAF Syngas Yield**:
  $$y_{gas,base}(T) = y_{gas,min} + \frac{y_{gas,max} - y_{gas,min}}{1 + \exp\left(-\frac{T - T_{gas,mid}}{s_{gas}}\right)}$$
* **DAF Bio-Oil Yield & Normalization**:
  $$y_{oil,raw} = \max(0.05, 1.0 - y_{char} - y_{gas})$$
  $$Y_{i,daf} = \frac{y_i}{\sum y_j} \implies Y_{char,daf} + Y_{oil,daf} + Y_{gas,daf} \equiv 1.000000$$
* **Reactor Thermal Duty**:
  $$Q_{pyro} = \dot{m}_{dry} C_{p,bio}(T_{pyro} - T_{dry}) + \dot{m}_{residual\_w} C_{p,steam}(T_{pyro} - T_{dry}) + \dot{m}_{dry} \Delta H_{rxn} + Q_{loss} \quad (\text{kW})$$

---

### 4.4 Plant Performance KPIs

* **Mass Balance Closure**:
  $$\text{Closure}_{\%} = \frac{\sum \dot{m}_{out}}{\sum \dot{m}_{in}} \times 100\% \equiv 100.00\%$$
* **Energy Recovery Ratio**:
  $$\eta_{energy} = \frac{\dot{E}_{char} + \dot{E}_{oil} + \dot{E}_{gas}}{\dot{E}_{feedstock,ar}} \times 100\%$$
* **Net Thermal Efficiency**:
  $$\eta_{net} = \frac{\dot{E}_{products} - (Q_{dry} + Q_{pyro} + P_{elec})}{\dot{E}_{feedstock,ar}} \times 100\%$$

---

## 5. Software Architecture

```text
ai_biomass_plant/
│
├── configs/                          # Plant and scenario configuration files
│   ├── default_plant.yaml            # Baseline industrial plant parameters
│   ├── feedstocks/                   # Standardized biomass library
│   │   ├── olive_pomace.yaml
│   │   ├── pine_sawdust.yaml
│   │   ├── wheat_straw.yaml
│   │   └── rice_husk.yaml
│   └── scenarios/                    # Operating regimes (fast, slow, standard)
│       ├── olive_pomace_standard.yaml
│       ├── pine_sawdust_fast_pyrolysis.yaml
│       └── wheat_straw_biochar_focus.yaml
│
├── src/
│   ├── data/                         # Feedstock models & preprocessing
│   │   ├── feedstock.py              # Ultimate/Proximate/Physical dataclasses & correlations
│   │   └── preprocessing.py          # Feedstock library & loader
│   ├── process/                      # Core unit operations & balances
│   │   ├── drying.py                 # Thermal biomass drying unit model
│   │   ├── reactor.py                # Pyrolysis reactor unit model
│   │   ├── separation.py             # Cyclone particulate separation & condensers
│   │   ├── mass_balance.py           # Stream tracking & mass balance closure
│   │   └── energy_balance.py         # Utility duties & thermodynamic KPIs
│   ├── models/                       # Yield kinetics & empirical modeling
│   │   └── yield_model.py            # Multicomponent sigmoidal yield kinetics
│   ├── optimization/                 # (Reserved for V0.6+)
│   ├── control/                      # (Reserved for V1.1+)
│   ├── simulation/                   # Orchestration
│   │   └── plant_simulator.py        # End-to-end plant simulation engine
│   ├── utils/                        # Utilities & config parsers
│   │   └── config.py                 # Configuration manager
│   └── run_simulation.py             # CLI application entry point
│
├── tests/                            # Comprehensive unit & integration tests
│   ├── conftest.py                   # Pytest fixtures
│   ├── test_feedstock.py             # Feedstock validation & HHV tests
│   ├── test_drying.py                # Drying mass/energy tests
│   ├── test_yield_model.py           # Kinetic yield normalization tests
│   ├── test_reactor.py               # Reactor unit tests
│   ├── test_separation.py            # Separation & cooling tests
│   ├── test_mass_balance.py          # Mass closure verification tests
│   ├── test_energy_balance.py        # Energy balance tests
│   └── test_simulation_e2e.py        # End-to-end multi-feedstock tests
│
├── pyproject.toml                    # Package metadata & pytest config
└── README.md                         # Documentation
```

---

## 6. Installation & Quickstart

### Prerequisites
* Python 3.11+
* Git

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd ai_biomass_plant

# Install dependencies
pip install -e .
```

---

## 7. How to Run the Model

### Run Default Baseline Simulation
```bash
python -m src.run_simulation
```

### Run a Scenario Profile
```bash
python -m src.run_simulation --config configs/scenarios/pine_sawdust_fast_pyrolysis.yaml
```

### Run Custom Parameters via CLI
```bash
python -m src.run_simulation \
    --feedstock olive_pomace \
    --feed-rate 150 \
    --moisture 18 \
    --temp 520 \
    --heating-rate 25 \
    --residence-time 15
```

### Output JSON Report for Data Pipelines
```bash
python -m src.run_simulation --feedstock pine_sawdust --json
```

---

## 8. Example Output

```text
============================================================
       AI-INTEGRATED BIOMASS CONVERSION PLANT - V0.1
============================================================
Feedstock            : Olive Pomace (agricultural_residue)
Feed Rate (Wet)      : 100.0 kg/h
Initial Moisture     : 15.0 wt%
Target Exit Moisture : 8.0 wt%
Reactor Temperature  : 500.0 °C
Heating Rate         : 10.0 °C/min
Residence Time       : 20.0 min

PRODUCTS & RECOVERY
------------------------------------------------------------
Recovered Bio-oil    :  46.33 kg/h  (HHV: 14.1 MJ/kg, Water: 25.5%)
Recovered Biochar    :  22.90 kg/h  (HHV: 23.3 MJ/kg)
Clean Syngas         :  22.81 kg/h  (LHV: 9.7 MJ/kg)
Dryer Exhaust Water  :   7.61 kg/h
Cyclone Fines Loss   :   0.35 kg/h

YIELDS (Dry Basis)
------------------------------------------------------------
Bio-oil Yield        :  48.1 wt%
Biochar Yield        :  27.4 wt%
Syngas Yield         :  24.6 wt%

MASS BALANCE
------------------------------------------------------------
Total Input          : 100.00 kg/h
Total Output         : 100.00 kg/h
Closure              : 100.00 %  (Deviation: 0.0000%)

ENERGY & THERMAL DUTIES
------------------------------------------------------------
Drying Thermal Duty  :  11.73 kW  (  42.2 MJ/h)
Reactor Thermal Duty :  35.39 kW  ( 127.4 MJ/h)
Condenser Cooling    :  32.68 kW
Auxiliary Electrical :   3.00 kW
Total External Power :  50.12 kW

PROCESS THERMODYNAMIC KPIS
------------------------------------------------------------
Feedstock Chem Power : 445.56 kW (LHV ar: 16.04 MJ/kg)
Products Chem Power  : 364.92 kW
Energy Recovery      :  81.9 %
Bio-oil Energy Share :  36.5 %
Biochar Energy Share :  31.7 %
Syngas Energy Share  :  13.7 %
Net Thermal Effic.   :  70.7 %

DIAGNOSTIC STATUS
------------------------------------------------------------
Input Validation     : PASS
Mass Balance Status  : PASS
Energy Balance Status: PASS
============================================================
```

---

## 9. Running Tests

Run the full pytest suite:

```bash
pytest tests/ -v
```

---

## 10. Long-Term Development Roadmap

* [x] **V0.1: Deterministic First-Principles Process Model** *(Completed)*
  * Feedstock property engine, drying model, pyrolysis reactor kinetics, separation train, mass/energy balance closure, and CLI.
* [ ] **V0.2: Advanced Thermodynamic & Elemental Balances**
  * Equilibrium gas composition ($CO, CO_2, H_2, CH_4$) via Gibbs free energy minimization, tar condensation kinetics, detailed elemental C/H/O atom accounting.
* [ ] **V0.3: Empirical Literature & Synthetic Dataset Generation**
  * Monte Carlo process simulation, uncertainty propagation, high-throughput operating parameter exploration.
* [ ] **V0.4: Machine Learning Product Yield Prediction**
  * Integration of Random Forests, XGBoost, and neural surrogate models trained on literature pyrolysis datasets.
* [ ] **V0.5: Multi-Model ML Benchmark & Physics-Informed Neural Networks (PINNs)**
  * Comparing classical empirical models vs gradient-boosted trees vs PINNs enforcing mass conservation.
* [ ] **V0.6: AI-Driven Multiobjective Process Optimization**
  * Pareto front optimization (maximizing bio-oil yield vs minimizing thermal duty) using Optuna / genetic algorithms.
* [ ] **V0.7: Soft Sensors for Real-Time State Estimation**
  * Virtual sensors for bio-oil moisture, syngas calorific value, and biochar fixed carbon.
* [ ] **V0.8: Anomaly & Fault Detection**
  * Autoencoders and statistical process monitoring for cyclone clogging, thermocouple drift, and condenser fouling.
* [ ] **V0.9: Predictive Maintenance**
  * RUL (Remaining Useful Life) estimation for reactor auger screw, refractory degradation, and filter bag aging.
* [ ] **V1.0: Real-Time Digital Twin Prototype**
  * Synchronized streaming telemetry, digital twin shadow state, and web dashboard (Streamlit / FastAPI).
* [ ] **V1.1: Dynamic Process Control Simulation**
  * Closed-loop PID & Model Predictive Control (MPC) for reactor temperature and feed rate regulation.
* [ ] **V1.2: Plant-Level AI Decision Support**
  * Feedstock blending optimization, techno-economic analysis (TEA), and Life Cycle Assessment (LCA) carbon accounting.
* [ ] **V2.0: Fully Autonomous AI Biomass Recycling Plant Platform**
  * Industrial SCADA integration, self-optimizing adaptive controls, and fleet-wide plant coordination.
