# Publication Cleanup Report

- Repository name: governance-friction-simulation
- Audit timestamp (UTC): 2026-03-14T21:57:38Z
- Cleanup objective: publication hardening focused on comments, docstrings, README clarity, and non-executable narrative text.

## Inventory summary

- Source code files: 64
- Test files: 3
- Config files: 8
- Documentation files: 2
- Metadata / reproducibility files: 2
- Packaging / environment files: 2
- Output artefacts checked but not edited: 20

## Files edited

- README.md
- scripts/build_figures.py

## Files not edited

All other repository files were preserved unchanged because they were execution-relevant, output-relevant, or higher-risk than the likely editorial gain justified.

## SAFE / CAUTION / HIGH RISK file table

| Path | Risk | Reason |
|---|---|---|
| `Dockerfile` | HIGH RISK | Configuration or environment file that affects execution or reproducibility. |
| `LICENSE` | HIGH RISK | Licensing text must be preserved exactly. |
| `README.md` | SAFE | Narrative documentation only. |
| `analysis_plan.yaml` | HIGH RISK | Configuration or environment file that affects execution or reproducibility. |
| `config/parameters.yaml` | HIGH RISK | Configuration or environment file that affects execution or reproducibility. |
| `config/scenarios/scenarios.yaml` | HIGH RISK | Configuration or environment file that affects execution or reproducibility. |
| `config/scm_graph.dot` | HIGH RISK | Configuration or environment file that affects execution or reproducibility. |
| `decision_curve_weights.yaml` | HIGH RISK | Configuration or environment file that affects execution or reproducibility. |
| `environment.yml` | HIGH RISK | Configuration or environment file that affects execution or reproducibility. |
| `outputs/figures/fig1_frontier.png` | HIGH RISK | Generated artefact or reproducibility fixture. |
| `outputs/figures/fig2_heatmap.png` | HIGH RISK | Generated artefact or reproducibility fixture. |
| `outputs/figures/fig3_sensitivity.png` | HIGH RISK | Generated artefact or reproducibility fixture. |
| `outputs/figures/fig4_drift.png` | HIGH RISK | Generated artefact or reproducibility fixture. |
| `outputs/figures/fig5_dca.png` | HIGH RISK | Generated artefact or reproducibility fixture. |
| `outputs/figures/fig6_scm.png` | HIGH RISK | Generated artefact or reproducibility fixture. |
| `outputs/logs/validation_report.json` | HIGH RISK | Generated artefact or reproducibility fixture. |
| `outputs/processed/dca_results.json` | HIGH RISK | Generated artefact or reproducibility fixture. |
| `outputs/processed/grid_results.json` | HIGH RISK | Generated artefact or reproducibility fixture. |
| `outputs/processed/inference_results.json` | HIGH RISK | Generated artefact or reproducibility fixture. |
| `outputs/processed/pareto_solutions.csv` | HIGH RISK | Generated artefact or reproducibility fixture. |
| `outputs/processed/simulation_summary.json` | HIGH RISK | Generated artefact or reproducibility fixture. |
| `outputs/raw/compensatory_comparison.csv` | HIGH RISK | Generated artefact or reproducibility fixture. |
| `outputs/raw/scenario_results.csv` | HIGH RISK | Generated artefact or reproducibility fixture. |
| `outputs/tables/sobol_false_negative_harm.csv` | HIGH RISK | Generated artefact or reproducibility fixture. |
| `outputs/tables/sobol_mean_total_friction.csv` | HIGH RISK | Generated artefact or reproducibility fixture. |
| `outputs/tables/sobol_safe_throughput.csv` | HIGH RISK | Generated artefact or reproducibility fixture. |
| `outputs/tables/sobol_unsafe_detection_rate.csv` | HIGH RISK | Generated artefact or reproducibility fixture. |
| `outputs/tables/table1_thresholds.csv` | HIGH RISK | Generated artefact or reproducibility fixture. |
| `outputs/tables/table2_pareto.csv` | HIGH RISK | Generated artefact or reproducibility fixture. |
| `reproducibility/replication_report.json` | HIGH RISK | Generated artefact or reproducibility fixture. |
| `reproducibility/run_manifest.json` | HIGH RISK | Generated artefact or reproducibility fixture. |
| `requirements.txt` | HIGH RISK | Configuration or environment file that affects execution or reproducibility. |
| `scm_functions.yaml` | HIGH RISK | Configuration or environment file that affects execution or reproducibility. |
| `scripts/build_figures.py` | CAUTION | Entry-point script or execution wrapper. |
| `scripts/run_all.py` | HIGH RISK | Entry-point script or execution wrapper. |
| `scripts/run_inference.py` | HIGH RISK | Entry-point script or execution wrapper. |
| `scripts/run_optimisation.py` | HIGH RISK | Entry-point script or execution wrapper. |
| `scripts/run_replication.py` | HIGH RISK | Entry-point script or execution wrapper. |
| `scripts/run_simulation.py` | HIGH RISK | Entry-point script or execution wrapper. |
| `scripts/run_validation.py` | HIGH RISK | Entry-point script or execution wrapper. |
| `src/__init__.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/__pycache__/__init__.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/analysis/__init__.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/analysis/__pycache__/__init__.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/analysis/__pycache__/dca.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/analysis/__pycache__/extreme_risk.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/analysis/__pycache__/inference.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/analysis/__pycache__/lifecycle.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/analysis/__pycache__/sensitivity.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/analysis/dca.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/analysis/extreme_risk.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/analysis/inference.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/analysis/lifecycle.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/analysis/sensitivity.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/calibration/__init__.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/generators/__init__.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/generators/__pycache__/__init__.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/generators/__pycache__/observation_model.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/generators/__pycache__/system_generator.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/generators/observation_model.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/generators/system_generator.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/metrics/__init__.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/metrics/__pycache__/__init__.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/metrics/__pycache__/friction_model.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/metrics/friction_model.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/optimisation/__init__.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/optimisation/__pycache__/__init__.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/optimisation/__pycache__/nsga2_search.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/optimisation/nsga2_search.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/plotting/__init__.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/plotting/__pycache__/__init__.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/plotting/__pycache__/figures.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/plotting/figures.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/policy/__init__.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/policy/__pycache__/__init__.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/policy/__pycache__/governance_engine.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/policy/governance_engine.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/preregistration/__init__.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/preregistration/__pycache__/__init__.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/preregistration/__pycache__/plan.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/preregistration/plan.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/replication/__init__.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/replication/__pycache__/__init__.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/replication/__pycache__/replication.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/replication/replication.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/scm/__init__.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/scm/__pycache__/__init__.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/scm/__pycache__/causal_model.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/scm/causal_model.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/utils/__init__.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/utils/__pycache__/__init__.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/utils/__pycache__/helpers.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/utils/helpers.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/validation/__init__.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/validation/__pycache__/__init__.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/validation/__pycache__/validation_suite.cpython-313.pyc` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `src/validation/validation_suite.py` | CAUTION | Source code; documentation edits must avoid affecting doctests, help text, or string-based expectations. |
| `tests/__init__.py` | CAUTION | Text changes can affect assertions, expected messages, or test semantics. |
| `tests/unit_tests.py` | CAUTION | Text changes can affect assertions, expected messages, or test semantics. |
| `tests/validation_tests.py` | CAUTION | Text changes can affect assertions, expected messages, or test semantics. |
| `thresholds/threshold_profiles.yaml` | HIGH RISK | Configuration or environment file that affects execution or reproducibility. |

## Validations run

- Python unit tests: passed (`python tests/unit_tests.py`)
- Validation suite: passed (`python tests/validation_tests.py`)
- Import smoke checks for representative modules: passed

## Validations not completed

- Fresh-environment installation was not fully completed in this container, so installation reproducibility was assessed from dependency declarations rather than a successful clean install.
- Full end-to-end pipeline execution via `scripts/run_all.py` was not confirmed in this hardening pass.

## Remaining issues

- Dependency declarations are loosely bounded rather than exactly pinned.
- No lock file is present.
- Fresh-environment reproducibility remains only partially evidenced.
- Many execution-relevant files remain classified as CAUTION or HIGH RISK and were intentionally preserved.

## Manual review list

- `requirements.txt`
- `environment.yml`
- `Dockerfile`
- `analysis_plan.yaml`
- all files under `config/`, `thresholds/`, `outputs/`, and `reproducibility/`
- all execution scripts other than the minimal wrapper-docstring edit in `scripts/build_figures.py`
