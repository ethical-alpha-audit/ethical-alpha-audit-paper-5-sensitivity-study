# Optimising Governance Friction in Medical AI: A Monte Carlo Study of Audit Thresholds
[![DOI](https://zenodo.org/badge/1194633489.svg)](https://doi.org/10.5281/zenodo.19499805)

> **Paper 5** of the Ethical Alpha Audit research programme
>
> Author: Walter Brown — Ethical Alpha Audit Ltd; NHS England
> ORCID: [0000-0002-6050-8522](https://orcid.org/0000-0002-6050-8522)

## Reviewer quick validation (no execution required)

```bash
python scripts/validate_outputs.py
```

**Expected result:** `VALIDATION PASSED`

This checks every data output file against its pinned SHA-256 digest. No notebook execution, no dependencies beyond Python stdlib. A passing result confirms the checked-in reference outputs are byte-identical to those produced by the deterministic pipeline.

**To re-execute the full pipeline** (requires dependencies):

```bash
pip install -r requirements.txt
python reproduce_all.py
```

Expected execution time: **~5 minutes** (271 seconds on the reference platform).

## What this repository reproduces

This repository contains the complete computational pipeline for the Paper 5 manuscript. It reproduces all quantitative findings from a Monte Carlo simulation of governance friction in medical AI deployment:

| Output | Key Result |
|--------|------------|
| Table 1 | 4 threshold profiles: moderate achieves 99.9% detection, 21.3% throughput |
| Table 2 | 0.04 unsafe per 100 deployments (NC) vs 4.56 (compensatory) |
| Table 3 | 60 Pareto-optimal configurations; 20 in policy sweet-spot |
| Figures 1–6 | Pareto frontier, heatmap, sensitivity, drift, DCA, SCM DAG |
| Sobol analysis | Safety gate ST = 1.00 for detection and harm |
| Lifecycle | 0.033 mean decay, 10.1% re-audit rate over 12 periods |
| Inference | Detection CI [0.994, 0.998], replication: 0.0 absolute difference |

## Repository structure

```
config/              Configuration files (parameters, thresholds, scenarios, harness)
docs/                Methods note, provenance, reproducibility statement
notebooks/           4 Jupyter notebooks (orchestration + presentation)
outputs/             Generated outputs (empty until execution)
reference_outputs/   Pre-baked reference targets for validation
reproducibility/     Generated manifests (empty until execution)
scripts/             Execution scripts (run_all.py, harness)
src/                 Source modules (16 scientific computation modules)
tests/               Unit and structural tests
thresholds/          Threshold profile definitions
```

## Notebooks

| # | Notebook | Purpose |
|---|----------|---------|
| 01 | `01_simulation_pipeline.ipynb` | Execute full 13-phase pipeline |
| 02 | `02_results_and_tables.ipynb` | Display Tables 1–3, derive Table 2 |
| 03 | `03_figures.ipynb` | Display Figures 1–6 |
| 04 | `04_sensitivity_and_inference.ipynb` | Sobol indices, bootstrap CIs, DCA detail |

## Simulation pipeline (13 phases)

1. Internal validation (7 tests)
2. Baseline simulation (100 evaluations: 5 scenarios × 4 profiles × 5 replicates)
3. Non-compensatory vs compensatory comparison
4. Grid search (6×6 safety × evidence)
5. NSGA-II multi-objective optimisation (30 generations, population 60)
6. Lifecycle simulation (12 time periods)
7. Sobol global sensitivity analysis (7 parameters, 64 base samples)
8. Decision Curve Analysis (5 policies)
9. Statistical inference (500 bootstrap resamples + Bayesian intervals)
10. Independent replication protocol
11. Figure generation (6 figures)
12. Table generation
13. Run manifest and summary

## Canonical parameters

- **n_systems:** 10,000 per evaluation
- **Random seed:** 42
- **PYTHONHASHSEED:** 0
- **Python:** 3.11

## Docker

```bash
docker build -t eaa-p5 .
docker run -v $(pwd)/outputs:/app/outputs eaa-p5
```

## Environment

```bash
conda env create -f environment.yml
conda activate governance-friction-sim
```

## License

MIT
