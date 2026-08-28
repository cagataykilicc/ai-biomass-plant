# AI-Integrated Biomass Recycling & Conversion Plant Digital Twin (V0.5)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Champion ML: Gradient Boosting](https://img.shields.io/badge/Champion%20Model-Gradient%20Boosting%20(R%C2%B2%200.9981)-blueviolet.svg)]()
[![Physics: 100% Mass Conserved](https://img.shields.io/badge/Physics%20Constraint-Simplex%20Projection%20(100%25)-darkgreen.svg)]()
[![Tests: 100% Passed](https://img.shields.io/badge/Tests-57%2F57%20Passed-brightgreen.svg)]()
[![Explainability: Permutation & Gini](https://img.shields.io/badge/Explainability-Permutation%20%26%20MDI-brightgreen.svg)]()
[![Thermal Status: Self--Sufficient](https://img.shields.io/badge/Thermal%20Status-Autonomous%20(TSI%20129.3%25)-darkgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

A modular, first-principles chemical engineering and digital twin platform for biomass thermal conversion, multi-model AI benchmarking, and chemical explainability.

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
* **Feature Importance & Chemical Explainability**: Quantifies the dominant chemical and operating drivers of product selectivity
* **Automated Champion Model Deployment**: Production registry of candidate and champion surrogates

---

## 2. Multi-Model Benchmark Leaderboard (V0.5)

Trained and cross-validated ($K=5$) on 1,000 process observations ($80/20$ train/test split):

| Rank | Model Family | Cross-Validation $R^2$ | Holdout Test $R^2$ | Test RMSE (wt%) | Test MAE (wt%) | Inference Latency ($\mu\text{s}$) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **1** | **Gradient Boosting [CHAMPION]** | **$0.9964$** | **$0.9981$** | **$0.565$** | **$0.403$** | **$4.3$** |
| 2 | Hist Gradient Boosting | $0.9960$ | $0.9974$ | $0.658$ | $0.465$ | $11.9$ |
| 3 | Multi-Layer Perceptron (MLP) | $0.9910$ | $0.9948$ | $0.938$ | $0.680$ | **$1.0$** |
| 4 | Extra Trees | $0.9931$ | $0.9951$ | $0.879$ | $0.636$ | $124.7$ |
| 5 | Random Forest | $0.9914$ | $0.9942$ | $0.983$ | $0.705$ | $138.2$ |
| 6 | Ridge (Linear Baseline) | $0.7100$ | $0.7069$ | $6.376$ | $5.354$ | $0.2$ |

---

## 3. Chemical Feature Importance & Explainability (Champion Model)

Permutation Feature Importance analysis on holdout test set ($N=200, \text{repeats}=10$):

| Rank | Feature | Mean Drop in $R^2$ | Physical & Chemical Engineering Role |
| :---: | :--- | :---: | :--- |
| **1** | `reactor_temp_c` | **$1.8095$** | Dominates thermal cracking, secondary reactions & devolatilization |
| **2** | `residence_time_min` | **$0.0748$** | Controls vapor secondary residence time and liquid repolymerization |
| **3** | `ash_pct` | **$0.0207$** | Inorganic catalytic activity and solid char mineral concentration |
| **4** | `heating_rate_c_min` | **$0.0066$** | Dictates fast vs slow pyrolysis kinetic pathways |
| **5** | `carbon_pct` | **$0.0033$** | Determines organic matrix density and bio-oil heating value |
| **6** | `volatile_matter_pct` | **$0.0033$** | Governs combustible volatile evolution |
| **7** | `feedstock_hhv_dry_mj_kg`| **$0.0017$** | Sets input chemical exergy baseline |

---

## 4. Software Architecture

```text
ai_biomass_plant/
│
├── models/
│   └── checkpoints/
│       ├── yield_predictor_champion.joblib   # Production champion (Gradient Boosting)
│       ├── yield_predictor_gradient_boosting.joblib
│       ├── yield_predictor_hist_gradient_boosting.joblib
│       ├── yield_predictor_mlp.joblib
│       ├── yield_predictor_extra_trees.joblib
│       ├── yield_predictor_random_forest.joblib
│       └── yield_predictor_ridge.joblib
│
├── reports/
│   ├── ml_multimodel_benchmark.json          # Multi-model leaderboard & latency report
│   ├── feature_importance.json               # Permutation & Gini feature importance
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
│   │   ├── benchmark.py                      # Multi-model benchmarking & leaderboard suite
│   │   ├── explainability.py                 # Feature importance & sensitivity analysis
│   │   ├── feature_engineering.py            # Feature transformation & scaling pipeline
│   │   ├── constraints.py                    # Physics-informed 100% mass conservation projection
│   │   ├── yield_predictor.py                # Multi-target ML surrogate suite (6 model types)
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
├── tests/                                    # 57 Automated Unit & Integration Tests
│   ├── test_multimodel_benchmark.py
│   ├── test_explainability.py
│   ├── test_mlp_model.py
│   ├── test_constraints.py
│   ├── test_yield_predictor.py
│   ├── test_hybrid_simulation.py
│   └── ...
│
├── pyproject.toml
└── README.md
```

---

## 5. How to Run the Platform

### A. Run Simulation with Champion ML Surrogate
```bash
python -m src.run_simulation --yield-mode ml --model-type champion --feedstock pine_sawdust --temp 520
```

### B. Run Simulation with MLP Neural Network Surrogate
```bash
python -m src.run_simulation --yield-mode ml --model-type mlp --feedstock olive_pomace --temp 500
```

### C. Run Multi-Model Benchmark Suite
```bash
python -m src.ml.benchmark
```

### D. Run Feature Importance & Explainability Engine
```bash
python -m src.ml.explainability
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
* [ ] **V0.6: AI-Driven Multiobjective Process Optimization (Optuna / Pyomo)**
  * Maximizing liquid bio-oil / biochar yield while maintaining 100% combustor thermal self-sufficiency.
* [ ] **V0.7: Soft Sensors for Real-Time State Estimation**
* [ ] **V0.8: Anomaly & Fault Detection (Autoencoders / Isolation Forests)**
* [ ] **V0.9: Predictive Maintenance (RUL of Augers, Refractory, Filters)**
* [ ] **V1.0: Real-Time Digital Twin Prototype (FastAPI + Streamlit GUI)**
* [ ] **V1.1: Dynamic Closed-Loop Process Control Simulation (MPC / PID)**
* [ ] **V1.2: Plant-Level AI Decision Support (Techno-Economic & LCA Carbon Accounting)**
* [ ] **V2.0: Fully Autonomous AI Biomass Recycling Plant Platform**
