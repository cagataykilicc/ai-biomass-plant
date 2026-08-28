# AI-Integrated Biomass Recycling & Conversion Plant Digital Twin (V0.6)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Optimization: NSGA--II Pareto & TOPSIS](https://img.shields.io/badge/Optimization-Pareto%20%26%20TOPSIS%20MCDM-blue.svg)]()
[![Champion ML: Gradient Boosting](https://img.shields.io/badge/Champion%20Model-Gradient%20Boosting%20(R%C2%B2%200.9981)-blueviolet.svg)]()
[![Physics: 100% Mass Conserved](https://img.shields.io/badge/Physics%20Constraint-Simplex%20Projection%20(100%25)-darkgreen.svg)]()
[![Tests: 100% Passed](https://img.shields.io/badge/Tests-64%2F64%20Passed-brightgreen.svg)]()
[![Thermal Status: Self--Sufficient](https://img.shields.io/badge/Thermal%20Status-Autonomous%20(TSI%20109.8%25)-darkgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

A modular, first-principles chemical engineering and digital twin platform for biomass thermal conversion, multi-model AI benchmarking, and AI-driven multiobjective process optimization.

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
* **Chemical Feature Importance**: Permutation and Gini sensitivity ranking
* **AI-Driven Process Optimization**: SLSQP and Differential Evolution global solvers
* **Multiobjective Non-Dominated Sorting (NSGA-II)**: Constructing Pareto Trade-off Frontiers between Liquid Bio-oil, Solid Biochar, Profit, and Energy Autonomy
* **TOPSIS Multi-Criteria Decision Support**: Automatically recommending optimal operating setpoints tailored to specific commercial stakeholder profiles

---

## 2. Process Optimization & Decision Framework (V0.6)

```text
  +-----------------------------------------------------------------------------------+
  |                       AI-DRIVEN PROCESS OPTIMIZATION ENGINE                       |
  |  Decision Variables: T (380-700°C), Beta (5-500°C/min), Tau (0.5-40min), Feed, w  |
  +---------------------------------------+-------------------------------------------+
                                          |
                                          v
               +----------------------------------------------------+
               |           HYBRID DIGITAL TWIN SIMULATOR            |
               |  (Gradient Boosting Champion + Simplex Projection) |
               +--------------------------+-------------------------+
                                          |
                                          v
               +----------------------------------------------------+
               |         THERMODYNAMIC CONSTRAINT ENFORCEMENT       |
               |   * Thermal Self-Sufficiency (TSI >= 100.0%)       |
               |   * Exact Mass Conservation (Closure == 100.00%)   |
               |   * Product Quality Bounds (pH >= 2.0, TAN <= 120) |
               +--------------------------+-------------------------+
                                          |
                         +----------------+----------------+
                         |                                 |
                         v                                 v
        +---------------------------------+  +---------------------------------+
        |   SINGLE-OBJECTIVE SOLVERS      |  |  MULTIOBJECTIVE PARETO ENGINE   |
        |  * Max Bio-Oil Yield            |  |  * Non-Dominated Sorting        |
        |  * Max Biochar Carbon Storage   |  |  * Crowding Distance Diversity  |
        |  * Max Gross Margin ($/h)       |  |  * Trade-off Frontier           |
        |  * Max Exergy Efficiency        |  +----------------+----------------+
        +---------------------------------+                   |
                                                              v
                                             +---------------------------------+
                                             |    TOPSIS MCDM DECISION MAKER   |
                                             |  * Bio-Oil Maximizer            |
                                             |  * Carbon Removal Priority      |
                                             |  * Economic Profit Priority     |
                                             |  * Balanced Sustainability      |
                                             +---------------------------------+
```

---

## 3. TOPSIS Decision Support Recommendations

From `reports/process_optimization_report.json` across non-dominated Pareto solutions:

| Stakeholder Profile | Recommended Temperature | Recommended Heating Rate | Residence Time | Predicted Bio-Oil Yield | Predicted Biochar Yield | Gross Margin ($/h) | Self-Sufficiency (TSI) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Bio-Oil Maximizer** | **$495.5^\circ\text{C}$** | $485.1^\circ\text{C/min}$ | $2.7\text{ min}$ | **$52.1\text{ wt}\%$** | $24.5\text{ wt}\%$ | **$\$111.30\text{/h}$** | **$110.2\%$ [Autonomous]** |
| **Carbon Sequestration Priority** | **$491.6^\circ\text{C}$** | $18.0^\circ\text{C/min}$ | $37.3\text{ min}$ | $50.4\text{ wt}\%$ | **$26.5\text{ wt}\%$** | $\$110.95\text{/h}$ | **$99.9\%$ [Autonomous]** |
| **Economic Profit Maximizer** | **$495.5^\circ\text{C}$** | $485.1^\circ\text{C/min}$ | $2.7\text{ min}$ | **$52.1\text{ wt}\%$** | $24.5\text{ wt}\%$ | **$\$111.30\text{/h}$** | **$110.2\%$ [Autonomous]** |
| **Balanced Sustainability** | **$491.6^\circ\text{C}$** | $18.0^\circ\text{C/min}$ | $37.3\text{ min}$ | $50.4\text{ wt}\%$ | **$26.5\text{ wt}\%$** | $\$110.95\text{/h}$ | **$99.9\%$ [Autonomous]** |

---

## 4. Software Architecture

```text
ai_biomass_plant/
│
├── reports/
│   ├── process_optimization_report.json      # Single & multiobjective optimization report
│   ├── pareto_frontier.json                  # Non-dominated Pareto frontier points
│   ├── ml_multimodel_benchmark.json          # Multi-model leaderboard & latency report
│   └── feature_importance.json               # Permutation & Gini feature importance
│
├── src/
│   ├── optimization/
│   │   ├── objectives.py                     # Objective functions & economic margin model
│   │   ├── problem.py                        # Decision bounds & non-linear constraints
│   │   ├── optimizer.py                      # Single-objective SLSQP & Differential Evolution
│   │   ├── pareto.py                         # Non-dominated sorting & Pareto front generator
│   │   ├── decision_maker.py                 # TOPSIS Multi-Criteria Decision Making engine
│   │   └── run_optimizer.py                  # Optimization CLI runner
│   ├── ml/
│   │   ├── benchmark.py                      # Multi-model benchmarking suite
│   │   ├── explainability.py                 # Feature importance analysis
│   │   ├── feature_engineering.py            # Feature transformation pipeline
│   │   ├── constraints.py                    # Physics-informed mass conservation projection
│   │   ├── yield_predictor.py                # Multi-target ML surrogate suite
│   │   ├── evaluator.py                      # Performance evaluator & cross-validator
│   │   └── train_models.py                   # Model training and benchmark CLI
│   ├── process/                              # Unit operations & balance engines
│   ├── simulation/
│   │   └── plant_simulator.py                # Hybrid simulation engine orchestrator
│   └── run_simulation.py                     # CLI application entry point
│
├── tests/                                    # 64 Automated Unit & Integration Tests
│   ├── test_objectives.py
│   ├── test_optimizer.py
│   ├── test_pareto.py
│   ├── test_decision_maker.py
│   ├── test_multimodel_benchmark.py
│   ├── test_explainability.py
│   ├── test_mlp_model.py
│   └── ...
│
├── pyproject.toml
└── README.md
```

---

## 5. How to Run the Optimization Engine

### A. Run Single-Objective Bio-Oil Maximization
```bash
python -m src.optimization.run_optimizer --feedstock olive_pomace --objective max_bio_oil
```

### B. Run Multiobjective Pareto Optimization with TOPSIS Decision Support
```bash
python -m src.optimization.run_optimizer --feedstock pine_sawdust --multiobjective
```

### C. Run Digital Twin with Optimization Shortcut
```bash
python -m src.run_simulation --optimize max_profit --feedstock wheat_straw
```

### D. Run Unit Test Suite
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
* [ ] **V0.7: Soft Sensors for Real-Time State Estimation**
  * Estimating unmeasured stream variables (syngas LHV, bio-oil TAN, moisture, char carbon) from standard process instrumentation.
* [ ] **V0.8: Anomaly & Fault Detection (Autoencoders / Isolation Forests)**
* [ ] **V0.9: Predictive Maintenance (RUL of Augers, Refractory, Filters)**
* [ ] **V1.0: Real-Time Digital Twin Prototype (FastAPI + Streamlit GUI)**
* [ ] **V1.1: Dynamic Closed-Loop Process Control Simulation (MPC / PID)**
* [ ] **V1.2: Plant-Level AI Decision Support (Techno-Economic & LCA Carbon Accounting)**
* [ ] **V2.0: Fully Autonomous AI Biomass Recycling Plant Platform**
