# AI-Integrated Biomass Recycling & Conversion Plant Digital Twin (V0.4)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![ML Model: Random Forest Surrogate](https://img.shields.io/badge/ML%20Surrogate-R%C2%B2%20%3D%200.9942-blueviolet.svg)]()
[![Physics: 100% Mass Conserved](https://img.shields.io/badge/Physics%20Constraint-Simplex%20Projection%20(100%25)-darkgreen.svg)]()
[![Tests: 100% Passed](https://img.shields.io/badge/Tests-54%2F54%20Passed-brightgreen.svg)]()
[![Dataset: 1000+ Observations](https://img.shields.io/badge/Dataset-Latin%20Hypercube%20(1000%2B%20Runs)-blue.svg)]()
[![Thermal Status: Self--Sufficient](https://img.shields.io/badge/Thermal%20Status-Autonomous%20(TSI%20109.8%25)-darkgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

A modular, first-principles chemical engineering and digital twin platform for biomass thermal conversion, recycling, and physics-constrained machine learning surrogate modeling.

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
* **Multi-Target Machine Learning Yield Surrogate**: Multi-output ensemble regressors predicting biochar, bio-oil, and syngas yields
* **Thermodynamic Physics Constraint Projection**: Simplex projection layer guaranteeing exact $100.00\%$ mass conservation and non-negativity ($\sum \tilde{y}_i \equiv 100\%$)
* **Hybrid Digital Twin Simulation**: Seamless toggling between first-principles kinetics and ML surrogate models

---

## 2. Process Flowsheet & Machine Learning Architecture (V0.4)

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
  +-----------------------------------------------------------------+      |
  |             PYROLYSIS REACTOR ENGINE (R101)                     |      |
  |                                                                 |      |
  |   [ Mode A: Kinetic Model ]       [ Mode B: ML Surrogate ]      |      |
  |   Multicomponent Sigmoidal        Random Forest Multi-Output    |      |
  |              |                                 |                |      |
  |              +---------------> <---------------+                |      |
  |                                |                                |      |
  |                                v                                |      |
  |              [ PHYSICS CONSTRAINT PROJECTION ]                  |      |
  |              Strict Non-Negativity: y_i >= 0                    |      |
  |              Exact Mass Conservation: sum(y_i) == 100.00%       |      |
  +-------------------------------+---------------------------------+      |
                                  | [ Hot Effluent S104 ]                  |
                                  v                                        |
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

## 3. Machine Learning Model Benchmark (V0.4)

Trained on 1,000 Latin Hypercube process observations ($80/20$ train/test split, 5-fold cross-validation):

| Metric | Cross-Validation (5-Fold) | Holdout Test Set ($N=200$) |
| :--- | :---: | :---: |
| **Mean $R^2$ Score** | **$0.9914 \pm 0.0009$** | **$0.9942$** |
| **Mean RMSE** | $1.12\text{ wt}\%$ | **$0.9828\text{ wt}\%$** |
| **Mean MAE** | $0.81\text{ wt}\%$ | **$0.7054\text{ wt}\%$** |
| **Raw Unconstrained Closure Error** | - | $0.001\text{ wt}\%$ |
| **Constrained Closure Error** | **$0.000000\%$** | **$0.000000\%$** |
| **First-Law Mass Conservation** | **GUARANTEED** | **GUARANTEED ($100.00\%$)** |

### Per-Target Holdout Test Performance
* **Biochar Yield**: $R^2 = 0.9984$, $\text{RMSE} = 0.44\text{ wt}\%$, $\text{MAE} = 0.31\text{ wt}\%$
* **Bio-Oil Yield**: $R^2 = 0.9912$, $\text{RMSE} = 1.34\text{ wt}\%$, $\text{MAE} = 0.98\text{ wt}\%$
* **Syngas Yield**: $R^2 = 0.9930$, $\text{RMSE} = 1.17\text{ wt}\%$, $\text{MAE} = 0.83\text{ wt}\%$

---

## 4. Software Architecture

```text
ai_biomass_plant/
│
├── models/
│   └── checkpoints/
│       └── yield_predictor_rf.joblib         # Serialized trained ML model checkpoint
│
├── reports/
│   ├── ml_yield_benchmark_report.json        # Detailed R², RMSE, MAE & CV report
│   ├── dataset_profiling_report.json         # Statistical dataset profiling report
│   └── example_simulation_report.json        # Exported simulation output
│
├── data/
│   ├── external/
│   │   └── literature_pyrolysis_dataset.csv  # Curated experimental literature data
│   └── processed/
│       └── synthetic_process_dataset.csv     # 1000+ LHS synthetic process observations
│
├── src/
│   ├── ml/
│   │   ├── feature_engineering.py            # Feature transformation & scaling pipeline
│   │   ├── constraints.py                    # Physics-informed 100% mass conservation projection
│   │   ├── yield_predictor.py                # Multi-target ML surrogate regressor model
│   │   ├── evaluator.py                      # Performance evaluator & cross-validator
│   │   └── train_models.py                   # Model training and benchmark CLI
│   ├── process/
│   │   ├── reactor.py                        # Pyrolysis reactor supporting deterministic & ML modes
│   │   ├── drying.py                         # Thermal biomass drying unit model
│   │   ├── separation.py                     # Cyclone particulate separation & condensers
│   │   ├── combustor.py                      # Syngas burner & flue gas heat recovery
│   │   ├── mass_balance.py                   # Stream tracking & mass balance closure
│   │   ├── elemental_balance.py              # Atom-by-atom C/H/O/N/S/Ash conservation
│   │   └── energy_balance.py                 # Heat integration, exergy & thermodynamic KPIs
│   ├── simulation/
│   │   └── plant_simulator.py                # Hybrid simulation engine orchestrator
│   └── run_simulation.py                     # CLI application entry point
│
├── tests/                                    # 54 Automated Unit & Integration Tests
│   ├── test_constraints.py
│   ├── test_ml_features.py
│   ├── test_yield_predictor.py
│   ├── test_hybrid_simulation.py
│   └── ...
│
├── pyproject.toml
└── README.md
```

---

## 5. How to Run the Platform

### A. Run Simulation with ML Surrogate Engine
```bash
python -m src.run_simulation --yield-mode ml --feedstock olive_pomace --temp 500
```

### B. Run Simulation with Deterministic Kinetic Engine
```bash
python -m src.run_simulation --yield-mode deterministic --feedstock pine_sawdust --temp 520
```

### C. Retrain ML Surrogate Models & Generate Benchmark Report
```bash
python -m src.ml.train_models --model random_forest
```

### D. Run Complete Test Suite
```bash
pytest tests/ -v
```

---

## 6. Long-Term Roadmap

* [x] **V0.1: Deterministic Process Flowsheet Model** *(Completed)*
* [x] **V0.2: Improved Mass, Elemental & Energy Balances & Heat Integration** *(Completed)*
* [x] **V0.3: Experimental Literature & Synthetic Dataset Generation** *(Completed)*
* [x] **V0.4: Machine Learning Product Yield Prediction & Physics Constraints** *(Completed)*
* [ ] **V0.5: Multi-Model Benchmark & Physics-Informed Neural Networks (PINNs)**
  * Benchmarking Random Forest, Extra Trees, XGBoost, LightGBM, CatBoost, and MLP PyTorch architectures.
* [ ] **V0.6: AI-Driven Multiobjective Process Optimization (Optuna / Pyomo)**
* [ ] **V0.7: Soft Sensors for Real-Time State Estimation**
* [ ] **V0.8: Anomaly & Fault Detection (Autoencoders / Isolation Forests)**
* [ ] **V0.9: Predictive Maintenance (RUL of Augers, Refractory, Filters)**
* [ ] **V1.0: Real-Time Digital Twin Prototype (FastAPI + Streamlit GUI)**
* [ ] **V1.1: Dynamic Closed-Loop Process Control Simulation (MPC / PID)**
* [ ] **V1.2: Plant-Level AI Decision Support (Techno-Economic & LCA Carbon Accounting)**
* [ ] **V2.0: Fully Autonomous AI Biomass Recycling Plant Platform**
