# AI-Integrated Biomass Recycling & Conversion Plant Digital Twin (V0.3)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Architecture: Chemical Engineering & Digital Twin](https://img.shields.io/badge/Architecture-Modular%20Process%20Systems-green.svg)]()
[![Tests: 100% Passed](https://img.shields.io/badge/Tests-47%2F47%20Passed-brightgreen.svg)]()
[![Dataset: 1000+ Observations](https://img.shields.io/badge/Dataset-Latin%20Hypercube%20(1000%2B%20Runs)-blue.svg)]()
[![Thermal Status: Self--Sufficient](https://img.shields.io/badge/Thermal%20Status-Autonomous%20(TSI%20111.8%25)-darkgreen.svg)]()
[![Scientific Integrity: Provenance Verified](https://img.shields.io/badge/Provenance-DOI%20%26%20Lineage%20Tracked-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

A modular, first-principles chemical engineering and digital twin platform for biomass thermal conversion, recycling, and machine learning dataset generation.

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
* **Scientific Data Provenance**: Explicit tracking of literature experimental datasets vs synthetic simulations
* **High-Throughput Synthetic Process Data Generator**: Latin Hypercube Sampling (LHS) with realistic sensor noise
* **Exploratory Data Analysis (EDA)**: Statistical distributions and correlation profiling
* Machine learning surrogate models (*V0.4+*)

---

## 2. Process Flowsheet & Data Pipeline (V0.3)

```text
  +-----------------------------------------------------------------------------------+
  |                              DATA PROVENANCE ENGINE                               |
  |  [ EXPERIMENTAL_LITERATURE (DOI) ]               [ SYNTHETIC_SIMULATED (LHS) ]    |
  +---------------------------------------+-------------------------------------------+
                                          |
                                          v
               +--------------------+
               |  Raw Biomass Feed  | (Pine, Beech, Pomace, Straw, Husk, Bagasse, Miscanthus, Almond)
               | (Moisture: 6-30%)  |
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
              | (T = 350 - 750 °C)   |                                     |
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
                         |
                         v
  +-----------------------------------------------------------------------------------+
  |                        DATASET EXPORT & STATISTICAL PROFILING                     |
  |  `data/processed/synthetic_process_dataset.csv` (1000+ Process Runs)             |
  |  `reports/dataset_profiling_report.json` (Correlation & Multicollinearity Stats)  |
  +-----------------------------------------------------------------------------------+
```

---

## 3. Capabilities & Key Features (V0.3)

* **Scientific Integrity & Provenance (`src/data/provenance.py`)**:
  - Enforces explicit `source_type` labeling (`EXPERIMENTAL_LITERATURE` vs `SYNTHETIC_SIMULATED`).
  - Stores bibliographic metadata (citations, authors, publication year, DOIs) and license tags.
* **Curated Peer-Reviewed Literature Dataset (`data/external/literature_pyrolysis_dataset.csv`)**:
  - Contains validated experimental pyrolysis records from benchmark literature (Neves et al., Akhtar & Amin, Bridgwater, Di Blasi, Phyllis2).
* **Latin Hypercube Synthetic Data Generator (`src/data/synthetic_generator.py`)**:
  - Stratified sampling across 8 biomass feedstock classes.
  - Multi-dimensional continuous sampling ($T \in [350, 750]^\circ\text{C}$, $\beta \in [5, 800]^\circ\text{C/min}$, $\tau \in [0.1, 45]\text{ min}$, moisture $\in [6, 28]\%$, feed rate $\in [50, 500]\text{ kg/h}$).
  - Realistic industrial sensor noise injection (thermocouple $\pm 1.5^\circ\text{C}$, load cell mass $\pm 0.8\%$, GC gas analysis $\pm 1.2\%$).
* **Exploratory Data Analysis Engine (`src/data/eda_analyzer.py`)**:
  - Computes complete feature distributions (mean, std, median, percentiles, skewness).
  - Pearson & Spearman correlation matrices between feedstock chemistry/temperature and product yields/heating values.
  - Generates JSON profiling report (`reports/dataset_profiling_report.json`).
* **47 Automated Unit Tests**: Complete pytest suite covering schemas, provenance, loaders, generator, and physical process units.

---

## 4. Software Architecture

```text
ai_biomass_plant/
│
├── data/
│   ├── external/
│   │   └── literature_pyrolysis_dataset.csv  # Curated experimental literature data
│   ├── processed/
│   │   └── synthetic_process_dataset.csv     # 1000+ LHS synthetic process observations
│   └── raw/
│
├── configs/
│   ├── default_plant.yaml                    # Baseline industrial plant parameters
│   ├── feedstocks/                           # 8 Feedstock library profiles
│   │   ├── olive_pomace.yaml
│   │   ├── pine_sawdust.yaml
│   │   ├── beech_wood.yaml
│   │   ├── wheat_straw.yaml
│   │   ├── rice_husk.yaml
│   │   ├── sugarcane_bagasse.yaml
│   │   ├── miscanthus.yaml
│   │   └── almond_shells.yaml
│   └── scenarios/                            # Operating regimes
│
├── src/
│   ├── data/
│   │   ├── provenance.py                     # Data lineage & provenance tracking
│   │   ├── schema.py                         # ProcessDataRecord tabular schema
│   │   ├── feedstock.py                      # Biomass data models & thermodynamic correlations
│   │   ├── preprocessing.py                  # Feedstock library & loader
│   │   ├── literature_loader.py              # Literature dataset loader & validator
│   │   ├── synthetic_generator.py            # Latin Hypercube Sampling Monte Carlo generator
│   │   └── eda_analyzer.py                   # Statistical profiling & correlation engine
│   ├── process/
│   │   ├── drying.py                         # Thermal biomass drying unit model
│   │   ├── reactor.py                        # Pyrolysis reactor unit model
│   │   ├── separation.py                     # Cyclone particulate separation & condensers
│   │   ├── combustor.py                      # Syngas burner & flue gas heat recovery
│   │   ├── mass_balance.py                   # Stream tracking & mass balance closure
│   │   ├── elemental_balance.py              # Atom-by-atom C/H/O/N/S/Ash conservation
│   │   └── energy_balance.py                 # Heat integration, exergy & thermodynamic KPIs
│   ├── models/
│   │   ├── yield_model.py                    # Multicomponent sigmoidal yield kinetics
│   │   ├── syngas_model.py                   # Molecular syngas speciation & volume properties
│   │   └── bio_oil_model.py                  # Chemical functional grouping, TAN, pH, viscosity
│   ├── simulation/
│   │   └── plant_simulator.py                # End-to-end plant simulation engine
│   ├── utils/
│   │   └── config.py                         # Configuration manager
│   └── run_simulation.py                     # CLI application entry point
│
├── tests/                                    # 47 Unit & Integration Tests
│   ├── conftest.py
│   ├── test_provenance.py
│   ├── test_schema.py
│   ├── test_literature_loader.py
│   ├── test_synthetic_generator.py
│   ├── test_feedstock.py
│   ├── test_drying.py
│   ├── test_yield_model.py
│   ├── test_syngas_model.py
│   ├── test_bio_oil_model.py
│   ├── test_combustor.py
│   ├── test_elemental_balance.py
│   ├── test_reactor.py
│   ├── test_separation.py
│   ├── test_mass_balance.py
│   ├── test_energy_balance.py
│   └── test_simulation_e2e.py
│
├── reports/
│   ├── dataset_profiling_report.json         # Statistical dataset profiling report
│   └── example_simulation_report.json        # Exported simulation output
│
├── pyproject.toml
└── README.md
```

---

## 5. How to Run the Platform

### A. Run Process Simulation
```bash
python -m src.run_simulation
```

### B. Generate Synthetic Dataset (Latin Hypercube Sampling)
```bash
python -m src.data.synthetic_generator --samples 1000 --seed 42
```

### C. Run Exploratory Data Analysis & Statistical Profiler
```bash
python -m src.data.eda_analyzer
```

### D. Run Unit Test Suite
```bash
pytest tests/ -v
```

---

## 6. Key Statistical Correlations from Generated Dataset

From `reports/dataset_profiling_report.json` across 1,000 process runs:

| Input Variable | Target Output | Pearson Correlation ($r$) | Physical Meaning |
| :--- | :--- | :---: | :--- |
| **Reactor Temperature ($T$)** | Biochar Yield (%) | **-0.864** | Strong thermal decomposition of char matrix |
| **Reactor Temperature ($T$)** | Syngas Yield (%) | **+0.972** | Surge in gas cracking and primary devolatilization |
| **Feedstock Carbon (%)** | Bio-Oil HHV (MJ/kg) | **+0.737** | Higher organic carbon enriches liquid energy density |
| **Feedstock Ash (%)** | Biochar Yield (%) | **+0.279** | Inorganic minerals concentrate into solid char |
| **Reactor Temperature ($T$)** | Self-Sufficiency (TSI) | **+0.936** | High gas yields provide surplus heat in combustor |

---

## 7. Long-Term Roadmap

* [x] **V0.1: Deterministic Process Flowsheet Model** *(Completed)*
* [x] **V0.2: Improved Mass, Elemental & Energy Balances & Heat Integration** *(Completed)*
* [x] **V0.3: Experimental Literature & Synthetic Dataset Generation** *(Completed)*
* [ ] **V0.4: Machine Learning Product Yield Prediction**
  * Training Random Forests, Extra Trees, XGBoost, and LightGBM models on curated dataset.
* [ ] **V0.5: Multi-Model Benchmark & Physics-Informed Neural Networks (PINNs)**
* [ ] **V0.6: AI-Driven Multiobjective Process Optimization (Optuna / Pyomo)**
* [ ] **V0.7: Soft Sensors for Real-Time State Estimation**
* [ ] **V0.8: Anomaly & Fault Detection (Autoencoders / Isolation Forests)**
* [ ] **V0.9: Predictive Maintenance (RUL of Augers, Refractory, Filters)**
* [ ] **V1.0: Real-Time Digital Twin Prototype (FastAPI + Streamlit GUI)**
* [ ] **V1.1: Dynamic Closed-Loop Process Control Simulation (MPC / PID)**
* [ ] **V1.2: Plant-Level AI Decision Support (Techno-Economic & LCA Carbon Accounting)**
* [ ] **V2.0: Fully Autonomous AI Biomass Recycling Plant Platform**
