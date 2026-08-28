# AI-Integrated Biomass Recycling & Conversion Plant Digital Twin (V0.2)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Architecture: Chemical Engineering & Digital Twin](https://img.shields.io/badge/Architecture-Modular%20Process%20Systems-green.svg)]()
[![Tests: 100% Passed](https://img.shields.io/badge/Tests-40%2F40%20Passed-brightgreen.svg)]()
[![Thermal Status: Self--Sufficient](https://img.shields.io/badge/Thermal%20Status-Autonomous%20(TSI%20111.8%25)-darkgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

A modular, first-principles chemical engineering and digital twin platform for biomass conversion and recycling.

---

## 1. Project Objective

The objective is to progressively develop an industrial-grade digital twin of a commercial biomass conversion plant that unifies:

* Rigorous chemical engineering calculations & thermodynamics
* Multi-stage unit operations (drying, pyrolysis reactor, cyclone, condenser train, syngas combustor)
* Atom-by-atom elemental mass conservation ($C, H, O, N, S, Ash$)
* Molecular syngas speciation ($CO, CO_2, CH_4, H_2, C_2H_6, H_2O, N_2$)
* Bio-oil chemical grouping (phenolics, acids, furans, sugars) & acidity ($TAN, \text{pH}$)
* Syngas burner heat integration & Thermal Self-Sufficiency Index (TSI)
* Second-Law Exergy analysis and destruction tracking
* Machine learning surrogates & digital twin control (*future roadmap*)

---

## 2. Process Flowsheet & Heat Integration (V0.2)

```text
               +--------------------+
               |  Raw Biomass Feed  |
               | (Moisture: 10-50%) |
               +---------+----------+
                         |
                         v
              +----------------------+  Flue Gas Heat Recovery (HX101)
              |  Drying Unit (D101)  | <===================================+
              |    (T = 105 °C)      |                                     |
              +----------+-----------+                                     |
                         | [ Dried Biomass S103 ]                          |
                         v                                                 |
              +----------------------+                                     |
              |  Pyrolysis Reactor   |                                     |
              |       (R101)         |                                     |
              | (T = 300 - 800 °C)   |                                     |
              +----------+-----------+                                     |
                         | [ Hot Effluent S104 ]                           |
                         v                                                 |
              +----------------------+                                     |
              |  Cyclone Separator   | ----> [ Recovered Biochar S106 ]    |
              |       (C101)         | ----> [ Cyclone Fines Loss S109 ]   |
              +----------+-----------+                                     |
                         | [ Clean Vapors ]                                |
                         v                                                 |
              +----------------------+                                     |
              |  Condenser Train     | ----> [ Liquid Bio-Oil S107 ]       |
              |    (E101 / E102)     |       (Acids, Phenolics, Sugars)    |
              +----------+-----------+                                     |
                         | [ Clean Syngas S108 ]                           |
                         | (CO, CO2, CH4, H2, C2H6)                        |
                         v                                                 |
              +----------------------+                                     |
              |  Syngas Combustor    | ------------------------------------+
              |       (B101)         | (Flue gas: 800 - 1400 °C)
              +----------------------+ (Thermal Self-Sufficiency: TSI > 100%)
```

---

## 3. Capabilities & Key Features (V0.2)

* **Atom-by-Atom Elemental Balances**: Exact conservation of C, H, O, N, S, and Ash across biochar, liquid bio-oil (aqueous and organic phases), syngas, and dryer exhaust with 100.00% closure.
* **Molecular Syngas Speciation**: Predicts $CO, CO_2, CH_4, H_2, C_2H_6, H_2O, N_2$ volume fractions, mean molecular weight ($MW_{mix}$), standard volume flow ($\text{Nm}^3/\text{h}$), and volumetric heating values ($\text{MJ/Nm}^3$).
* **Bio-oil Characterization**: Functional chemical family partitioning (carboxylic acids, phenolics/lignin, furans, anhydrosugars, carbonyls), Total Acid Number (TAN), pH prediction, density, and kinematic viscosity.
* **Syngas Combustor & Heat Integration**: Sizing of burner B101 with excess air ($\lambda = 1.20$), adiabatic/actual flame temperature, and heat recovery exchanger (HX101) supplying 100% of drying and reactor thermal loads.
* **Thermal Self-Sufficiency Index (TSI)**: Identifies whether the plant operates autonomously with net surplus energy or requires supplementary external fuel.
* **Second-Law Exergy Analysis**: Szargut statistical chemical exergy calculations and component exergy destruction tracking.
* **40 Automated Unit Tests**: 100% pass rate in pytest across all engineering units and integration workflows.

---

## 4. Governing Chemical Engineering Equations

### 4.1 Elemental Mass Conservation
For each element $k \in \{C, H, O, N, S, Ash\}$:
$$\dot{m}_{k,in} = \dot{m}_{k,char} + \dot{m}_{k,bio\_oil} + \dot{m}_{k,syngas} + \dot{m}_{k,dryer\_exhaust} + \dot{m}_{k,loss}$$
$$\text{Closure}_{k} = \frac{\dot{m}_{k,out}}{\dot{m}_{k,in}} \times 100\% \equiv 100.00\%$$

### 4.2 Syngas Molecular Equilibrium & Speciation
* **Normal Volumetric Flow Rate**:
  $$\dot{V}_{gas} = \left( \sum \frac{\dot{m}_i}{MW_i} \right) \times 22.414 \quad (\text{Nm}^3/\text{h})$$
* **Volumetric Lower Heating Value**:
  $$LHV_{vol} = \sum y_i LHV_{vol,i} \quad (\text{MJ/Nm}^3)$$

### 4.3 Syngas Combustion & Waste Heat Recovery
* **Combustion Stoichiometry**:
  $$CO + \frac{1}{2}O_2 \rightarrow CO_2, \quad H_2 + \frac{1}{2}O_2 \rightarrow H_2O, \quad CH_4 + 2O_2 \rightarrow CO_2 + 2H_2O, \quad C_2H_6 + 3.5O_2 \rightarrow 2CO_2 + 3H_2O$$
* **Combustion Heat Release**:
  $$Q_{comb} = \frac{\dot{m}_{syngas} \times LHV_{syngas}}{3.6} \times \eta_{comb} \quad (\text{kW})$$
* **Recovered Flue Gas Duty**:
  $$Q_{rec} = Q_{comb} \times \eta_{rec} \quad (\text{kW})$$
* **Thermal Self-Sufficiency Index (TSI)**:
  $$\text{TSI}_{\%} = \frac{Q_{rec}}{Q_{dry} + Q_{pyro}} \times 100\%$$

### 4.4 Second-Law Exergy Balance
* **Biomass Chemical Exergy (Szargut Correlation)**:
  $$e_{ch,bio} = \beta \times LHV_{dry} \quad \text{where } \beta = 1.0437 + 0.1882\frac{H}{C} - 0.053\frac{O}{C} + 0.04\frac{N}{C}$$
* **Exergy Efficiency**:
  $$\psi_{exergy} = \frac{\dot{Ex}_{products}}{\dot{Ex}_{feedstock} + \dot{Ex}_{net\_external}} \times 100\%$$

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
│   │   ├── combustor.py              # Syngas burner & flue gas heat recovery
│   │   ├── mass_balance.py           # Stream tracking & mass balance closure
│   │   ├── elemental_balance.py      # Atom-by-atom C/H/O/N/S/Ash conservation
│   │   └── energy_balance.py         # Heat integration, exergy & thermodynamic KPIs
│   ├── models/                       # Yield kinetics & speciation modeling
│   │   ├── yield_model.py            # Multicomponent sigmoidal yield kinetics
│   │   ├── syngas_model.py           # Molecular syngas speciation & volume properties
│   │   └── bio_oil_model.py          # Chemical functional grouping, TAN, pH, viscosity
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
│   ├── test_syngas_model.py          # Syngas speciation & volumetric tests
│   ├── test_bio_oil_model.py         # Bio-oil chemical grouping & pH tests
│   ├── test_combustor.py             # Combustor thermal & stoichiometry tests
│   ├── test_elemental_balance.py     # Atom-by-atom elemental closure tests
│   ├── test_reactor.py               # Reactor unit tests
│   ├── test_separation.py            # Separation & cooling tests
│   ├── test_mass_balance.py          # Mass closure verification tests
│   ├── test_energy_balance.py        # Energy balance, heat integration & exergy tests
│   └── test_simulation_e2e.py        # End-to-end multi-feedstock tests
│
├── pyproject.toml                    # Package metadata & pytest config
└── README.md                         # Documentation
```

---

## 6. How to Run the Model

### Run Baseline Simulation
```bash
python -m src.run_simulation
```

### Run Fast Pyrolysis Scenario
```bash
python -m src.run_simulation --config configs/scenarios/pine_sawdust_fast_pyrolysis.yaml
```

### Run Custom Feedstock with JSON Export
```bash
python -m src.run_simulation --feedstock rice_husk --temp 550 --json
```

---

## 7. Example Output (V0.2 Dashboard)

```text
====================================================================
       AI-INTEGRATED BIOMASS CONVERSION PLANT - V0.2
   (Thermodynamics, Elemental Balances & Heat Integration)
====================================================================
Feedstock            : Olive Pomace (agricultural_residue)
Feed Rate (Wet)      : 100.0 kg/h
Initial Moisture     : 15.0 wt%
Target Exit Moisture : 8.0 wt%
Reactor Temperature  : 500.0 °C
Heating Rate         : 10.0 °C/min
Residence Time       : 20.0 min

PRODUCTS & RECOVERY
--------------------------------------------------------------------
Recovered Bio-oil    :  46.33 kg/h  (HHV: 14.1 MJ/kg, Water: 25.5%)
Recovered Biochar    :  22.90 kg/h  (HHV: 23.3 MJ/kg)
Clean Syngas         :  22.81 kg/h  (16.9 Nm³/h, LHV: 13.4 MJ/Nm³)
Dryer Exhaust Water  :   7.61 kg/h
Cyclone Fines Loss   :   0.35 kg/h

SYNGAS MOLECULAR SPECIATION
--------------------------------------------------------------------
Composition (vol%)   : CO: 44.5% | CO2: 31.6% | CH4: 12.6% | H2:  4.7%
Mean Molecular Weight: 30.20 kg/kmol  | Mass LHV: 9.93 MJ/kg

BIO-OIL CHEMICAL CHARACTERIZATION
--------------------------------------------------------------------
Organic Groups (wt%) : Acids: 14.5% | Phenolics: 32.0% | Sugars: 23.8%
Physical Properties  : pH: 2.21 | TAN: 100.6 mg KOH/g | Density: 1164 kg/m³

ATOM-BY-ATOM ELEMENTAL BALANCES
--------------------------------------------------------------------
Element | In (kg/h) | Out (kg/h) | Closure % | Status
  C     |   42.670  |    42.670  |  100.00 %  | PASS
  H     |    6.949  |     6.949  |  100.00 %  | PASS
  O     |   47.151  |    47.151  |  100.00 %  | PASS
  N     |    1.190  |     1.190  |  100.00 %  | PASS
  S     |    0.085  |     0.085  |  100.00 %  | PASS
  Ash   |    1.955  |     1.955  |  100.00 %  | PASS
Carbon Partitioning  : Biochar: 34.6% | Bio-oil: 44.7% | Syngas: 20.7%

MASS & OVERALL BALANCE
--------------------------------------------------------------------
Total Mass In / Out  : 100.00 kg/h  /  100.00 kg/h  (Closure: 100.00%)

HEAT INTEGRATION & COMBUSTOR (Burner B101)
--------------------------------------------------------------------
Gross Thermal Demand :  47.12 kW  (Drying: 11.7 kW, Reactor: 35.4 kW)
Syngas Heat Released :  61.97 kW  (Flue Gas Temp: 1400 °C, Air: 81.1 kg/h)
Exchanger Heat Recov.:  52.67 kW  (HX101 Efficiency: 85%)
Self-Sufficiency (TSI:  111.8 %  -> [AUTONOMOUS / NET SURPLUS]
Net Surplus Thermal  :   5.56 kW

THERMODYNAMIC KPIS & EXERGY
--------------------------------------------------------------------
Feedstock Chemical   : 445.56 kW (LHV ar: 16.04 MJ/kg)
Products Chemical    : 364.92 kW  (Energy Recovery: 81.9%)
Net Thermal Effic.   :  81.2 %
Second-Law Exergy Eff:  82.3 %  (Exergy Destruction: 58.3 kW)

DIAGNOSTIC STATUS
--------------------------------------------------------------------
Mass Balance Status     : PASS
Elemental Balance Status: PASS
Energy Balance Status   : PASS

ADVISORIES & NOTICES:
 [*] Plant operates in full thermal self-sufficiency via syngas heat recovery.
====================================================================
```

---

## 8. Unit Testing Suite

```bash
pytest tests/ -v
```
All **40 tests** pass in **0.06s**.

---

## 9. Long-Term Roadmap

* [x] **V0.1: Deterministic Process Flowsheet Model** *(Completed)*
* [x] **V0.2: Improved Mass, Elemental & Energy Balances & Heat Integration** *(Completed)*
* [ ] **V0.3: Experimental Literature & Synthetic Dataset Generation**
  * High-throughput Monte Carlo sampling, parameter distributions, data validation schemas.
* [ ] **V0.4: Machine Learning Product Yield Prediction**
  * Random Forests, XGBoost, and LightGBM models trained on curated pyrolysis dataset.
* [ ] **V0.5: Multi-Model Benchmark & Physics-Informed Neural Networks (PINNs)**
* [ ] **V0.6: AI-Driven Multiobjective Process Optimization (Optuna / Pyomo)**
* [ ] **V0.7: Soft Sensors for Real-Time State Estimation**
* [ ] **V0.8: Anomaly & Fault Detection (Autoencoders / Isolation Forests)**
* [ ] **V0.9: Predictive Maintenance (RUL of Augers, Refractory, Filters)**
* [ ] **V1.0: Real-Time Digital Twin Prototype (FastAPI + Streamlit)**
* [ ] **V1.1: Dynamic Closed-Loop Process Control Simulation (MPC / PID)**
* [ ] **V1.2: Plant-Level AI Decision Support (Techno-Economic & LCA Carbon Accounting)**
* [ ] **V2.0: Fully Autonomous AI Biomass Recycling Plant Platform**
