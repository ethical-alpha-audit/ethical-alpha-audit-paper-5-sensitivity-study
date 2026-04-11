# Governance Friction Simulation

**Optimising Governance Friction in Medical AI: A Monte Carlo Study of Audit Thresholds**

A reproducible computational study of the trade-off frontier between governance stringency and safe innovation throughput in medical AI deployment.

## Overview

This repository contains a simulation and analysis pipeline for evaluating audit-threshold governance in medical AI systems. The implementation includes:

- a Structural Causal Model (SCM) linking latent system traits to harms and governance signals
- non-compensable governance gates (Tier-1 policy) and a compensatory scoring comparator
- NSGA-II multi-objective optimisation for Pareto-optimal threshold profiles
- Sobol global sensitivity analysis for parameter influence ranking
- lifecycle dynamics including performance drift, re-audit triggers, and monitoring
- extreme tail-risk modelling via the Generalized Pareto Distribution
- Decision Curve Analysis for policy selection under varying harm-benefit preferences
- an independent replication protocol with tolerance-based verification

## Repository layout

```text
governance-friction-simulation/
├── config/                 # Configuration files
├── thresholds/             # Threshold profile definitions
├── src/                    # Source code modules
├── scripts/                # Execution entry points
├── tests/                  # Unit and validation tests
├── outputs/                # Example generated outputs
└── reproducibility/        # Run manifests and replication artefacts
```

## Environment setup

Python 3.11 is specified in `environment.yml`.

### pip

```bash
pip install -r requirements.txt
```

### conda

```bash
conda env create -f environment.yml
conda activate governance-friction-sim
```

## Core commands

Run the full pipeline:

```bash
python scripts/run_all.py
```

Run the unit tests:

```bash
python tests/unit_tests.py
```

Run the validation suite:

```bash
python tests/validation_tests.py
```

## Docker

```bash
docker build -t governance-sim .
docker run -v $(pwd)/outputs:/app/outputs governance-sim
```

## Reproducibility notes

Outputs are seeded deterministically by the codebase. The run manifest in `reproducibility/run_manifest.json` records configuration hashes, the analysis plan hash, and execution metadata. The replication protocol verifies whether independent builds reproduce key metrics within the declared tolerance band.

Dependency declarations are currently version-bounded rather than fully pinned. This supports environment recreation but does not guarantee byte-identical installs across time.

## Outputs

The repository includes example outputs under `outputs/`, including figures, processed summaries, raw scenario results, tables, and validation artefacts.

## Citation

If you use this simulation in research outputs, cite the accompanying manuscript.

## License

This repository is released under the MIT License. See `LICENSE` for the full license text.
