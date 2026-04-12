# Claim Traceability Matrix (P5)

**Repo:** ethical-alpha-audit-paper-5-sensitivity-study  
**Manuscript sources:** `inputs/manuscript.docx`, `inputs/supplementary.pdf` (supplementary supports appendices; primary empirical claims traced below to main text).  
**Updated:** 2026-04-12 (engineer remediation pass)  
**CLAIM EXTRACTION COMPLETE: 32 claims identified for P5** (P5-C01–P5-C32)

| Claim ID | Claim (paraphrase / anchor) | Code / pipeline | Primary outputs | Status |
|----------|----------------------------|-----------------|-----------------|--------|
| P5-C01 | Monte Carlo governance simulation with SCM linking latent traits to harms, signals, lifecycle | `scripts/run_all.py`; `src/scm/causal_model.py`; `scm_functions.yaml` | `outputs/processed/simulation_summary.json` | Traced |
| P5-C02 | 10,000 synthetic systems per evaluation | `config/parameters.yaml` → `simulation.n_systems`; `src/generators/system_generator.py` | `outputs/raw/scenario_results.csv` | Traced |
| P5-C03 | Five scenario families × four threshold profiles × five replicates (100 evaluations) | `scripts/run_all.py` Phase 2; `config/scenarios/scenarios.yaml` | `outputs/raw/scenario_results.csv` | Traced |
| P5-C04 | SCM DAG: 28 nodes, 19 edges (Figure 6) | `config/scm_graph.dot`; `src/scm/causal_model.py` | Console + `outputs/figures/fig6_scm.png` | Traced |
| P5-C05 | Structural equations from versioned `scm_functions.yaml` v1.0 | `scm_functions.yaml`; `apply_scm` | Scenario + summary JSON | Traced |
| P5-C06 | Preregistered analysis plan hash **1fba2e24** | `analysis_plan.yaml`; `src/preregistration/plan.py` | `outputs/processed/simulation_summary.json` (`manifest.plan_hash`) | Traced |
| P5-C07 | NSGA-II: 30 generations, pop 60, 5D thresholds [0.1, 0.9], four objectives | `src/optimisation/nsga2_search.py`; Phase 5 | `outputs/processed/pareto_solutions.csv` | Traced |
| P5-C08 | Sweet-spot: detection ≥70% and safe throughput ≥50% | `scripts/run_all.py`; `identify_sweet_spot` in `nsga2_search.py` | `pareto_solutions.csv` (`in_sweet_spot`) | Traced |
| P5-C09 | Sobol: 7 parameters (5 gates + noise + UBR), 64 base samples | `src/analysis/sensitivity.py`; Phase 7 | `outputs/tables/sobol_*.csv` | Traced |
| P5-C10 | Bootstrap n=500 + Bayesian rate intervals for key metrics | `src/analysis/inference.py`; Phase 9 | `outputs/processed/inference_results.json` | Traced |
| P5-C11 | Lifecycle: 12 periods, drift, re-audit | `src/analysis/lifecycle.py`; Phase 6 | `simulation_summary.json` → `lifecycle_summary` | Traced |
| P5-C12 | Seven internal validation tests (named suite) | `src/validation/validation_suite.py`; Phase 1 | `outputs/logs/validation_report.json` | Traced |
| P5-C13 | Replication protocol within ≤0.01 absolute tolerance | `src/replication/replication.py`; Phase 10 | `reproducibility/replication_report.json` | Traced |
| P5-C14 | Table 1 — four profiles at 20% UBR, moderate audit (detection, throughput, FN harm, friction) | Phase 12 table build; `notebooks/02_results_and_tables.ipynb` | `outputs/tables/table1_thresholds.csv` | Traced |
| P5-C15 | Moderate NC detection **99.8%** vs compensatory **77.2%** | `GovernancePolicyEngine` vs `CompensatoryPolicyEngine`; Phase 3 | `outputs/raw/compensatory_comparison.csv`; summary | Traced |
| P5-C16 | False-negative harm **152×** lower NC vs compensatory (**2.1** vs **323.1**) | Phase 3 | `compensatory_comparison.csv`; manuscript Table 2 narrative | Traced |
| P5-C17 | Throughput: NC moderate **21.3%** vs compensatory **81.2%** | Phase 2–3 | `scenario_results.csv`; `compensatory_comparison.csv` | Traced |
| P5-C18 | Expected unsafe approvals per 100 deployments: NC moderate **0.04** vs compensatory **4.56** (20% base) | Derived in `notebooks/02_results_and_tables.ipynb` | `outputs/tables/table2_per100_deployments.csv` | Traced |
| P5-C19 | **60** Pareto solutions; **20** in sweet-spot (~33%) | Phase 5 | `pareto_solutions.csv`; `fig1_frontier.png` | Traced |
| P5-C20 | Reported Pareto ranges (detection, throughput, FN harm, friction) | Phase 5 + figures | `fig1_frontier.png`; Table 3 / `table2_pareto.csv` | Traced |
| P5-C21 | Sobol: safety gate **ST = 1.00** for unsafe detection rate | `format_sensitivity_table`; Phase 7 | `sobol_unsafe_detection_rate.csv` | Traced |
| P5-C22 | Sobol: safety gate **ST = 1.00** for false-negative harm | Phase 7 | `sobol_false_negative_harm.csv` | Traced |
| P5-C23 | Sobol: safe throughput — calibration gate dominant (**ST ≈ 0.32**) | Phase 7 | `sobol_safe_throughput.csv` | Traced |
| P5-C24 | Sobol: mean friction — safety gate **ST ≈ 0.23** | Phase 7 | `sobol_mean_total_friction.csv` | Traced |
| P5-C25 | Lifecycle: mean final decay **~0.033**, mean cumulative harm **~5.05**, re-audit **~10.1%** | Phase 6 | `simulation_summary.json` | Traced |
| P5-C26 | Bootstrap: detection mean **0.996**, CI **[0.994, 0.998]** | Phase 9 | `inference_results.json` | Traced |
| P5-C27 | Bootstrap: safe throughput **0.210** **[0.203, 0.217]** | Phase 9 | `inference_results.json` | Traced |
| P5-C28 | All seven validation tests passed | Phase 1 | `validation_report.json` | Traced |
| P5-C29 | Deterministic replication: **zero** absolute difference on key metrics | Phase 10 | `replication_report.json` | Traced |
| P5-C30 | Decision Curve Analysis supports policy comparison under preferences | `src/analysis/dca.py`; Phase 8 | `outputs/processed/dca_results.json`; `fig5_dca.png` | Traced |
| P5-C31 | Grid search over safety × evidence gates | `run_grid_search`; Phase 4 | `outputs/processed/grid_results.json` | Traced |
| P5-C32 | Companion historical replay / Core-12 statistics (91.7% sensitivity, specificity 1.000, etc.) | **Cross-repo (P4)** — manuscript cites unified engine; not recomputed in this repo | Escalation: verify against `ethical-alpha-audit-paper-4-historical-replay` frozen artefact | External |

## Compensatory anchoring (explicit + implicit)

- **Explicit:** Abstract, Methods, Results, Tables 1–3, Figures 1 & 6, Discussion — all mapped above.
- **Implicit:** Normative alignment (EU AI Act, FDA references), future interaction / factorial designs — not implemented as numerical claims in this codebase; tracked as narrative-only in manuscript.

## QA notes

- **2026-04-12 — P5 Sensitivity QA (first post-remediation):** `python -m pytest tests/ -q` → **8 passed**. `python reproduce_all.py` → **Step 1** (`scripts/run_all.py`) **completed** (~431 s); console and `outputs/processed/simulation_summary.json` align with P5-C15–P5-C17, P5-C19, P5-C21–P5-C25, P5-C26–P5-C29 on inspection. **Step 2** (`scripts/notebook_runner.py`) **failed** on `notebooks/01_simulation_pipeline.ipynb`: nbclient **“Kernel didn’t respond in 60 seconds”** (kernel startup, not `execution_timeout_seconds`). After Step 1, `python scripts/hash_manifest.py` and `python scripts/validate_outputs.py` → **VALIDATION PASSED**. `table2_per100_deployments.csv` on disk matches P5-C18 numerically (20% base: 0.04 vs 4.56) but was **not** regenerated in this session because notebooks did not execute. No `Status` column updates to **VERIFIED** in this pass (notebook + full `reproduce_all.py` end-to-end not achieved). Portfolio `eaa_system/system_snapshot.json`: P5 still **not-started** / null commit vs repo **be5cb8611dea8b3c38f7d4a1a79034eeae259566** (pre–snapshot-bind).
- Canonical environment per `repro_manifest.json`: **Python 3.11**; hash pins in `config/expected_outputs.json` reflect seed-controlled runs (see file header for platform float caveats).
- One-command pipeline: `python reproduce_all.py` (sets `P5_SKIP_EMBEDDED_SIM=1` before notebooks so `01_simulation_pipeline.ipynb` does not duplicate the ~8 min simulation after Step 1).
- Interactive-only full notebook run: clear `P5_SKIP_EMBEDDED_SIM` and execute `notebooks/01_simulation_pipeline.ipynb` (runs `scripts/run_all.main()`).
