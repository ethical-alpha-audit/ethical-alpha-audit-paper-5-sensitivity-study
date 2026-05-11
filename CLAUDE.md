# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Paper 5 of the Ethical Alpha Audit research programme: a Monte Carlo simulation of governance friction in medical AI deployment. The repository is a **reproducibility artefact** for a manuscript — it exists to regenerate every quantitative claim (tables, figures, sensitivity analyses) byte-identically from a fixed seed. Treat code, configuration, and reference outputs as part of a frozen computational pipeline whose outputs are pinned by SHA-256.

## Common commands

```bash
# Validate pinned outputs without executing the pipeline (stdlib only)
python scripts/validate_outputs.py             # expects: VALIDATION PASSED

# Full reproduction: run pipeline → execute notebooks → hash → validate → export HTML (~5 min)
python reproduce_all.py

# Pipeline only (no notebooks, no validation)
python scripts/run_all.py

# Re-execute the presentation notebooks against existing outputs/
P5_SKIP_EMBEDDED_SIM=1 python scripts/notebook_runner.py   # env var skips re-running phase 1 inside nb 01

# Unit tests (no pytest config — run as scripts)
python tests/unit_tests.py
python tests/validation_tests.py
python tests/test_harness_structure.py
python tests/test_claim_coverage.py

# Refresh the actual-output hash manifest (writes logs/actual_manifest.json)
python scripts/hash_manifest.py
```

Python 3.11 is required. Install with `pip install -r requirements.txt` (pinned versions; `requirements.lock.txt` is the authoritative lockfile) or `conda env create -f environment.yml`.

## Reproducibility contract (read before changing anything)

This repository's purpose is byte-identical reproduction. Several rules follow from that:

- **`outputs/` is regenerated, never committed.** `reference_outputs/` is the committed comparison target. `config/expected_outputs.json` pins SHA-256 hashes that fresh outputs must match exactly.
- **Determinism is enforced via `PYTHONHASHSEED=0` and base seed 42** (from `config/parameters.yaml`). All RNG goes through `numpy.random.RandomState(seed)`; derived seeds come from `src/utils/helpers.py:derive_seed` (SHA-256 of base seed + identifiers). NSGA-II, Sobol sampling, and bootstrap inference are all deterministic under the same seed.
- **`n_systems = 10000` is canonical** in `parameters.yaml`. Do not raise it (would invalidate hashes); reductions inside `run_all.py` for optimisation (3000) and sensitivity (2000) phases are intentional and load-bearing — see `docs/provenance.md`.
- **Touching anything in `src/`, `config/parameters.yaml`, `thresholds/threshold_profiles.yaml`, `scm_functions.yaml`, or `analysis_plan.yaml` will change output hashes.** When that's intentional, regenerate `reference_outputs/`, update `config/expected_outputs.json` via `scripts/hash_manifest.py`, and confirm `validate_outputs.py` passes.
- **Manuscript files are working-tree-only.** `.gitignore` blocks `inputs/*.docx` and `inputs/*.pdf` — required on disk for downstream workflows but must never enter git history.
- **Claim traceability is gated by a test.** `tests/test_claim_coverage.py` enforces that `docs/claim_traceability.md` enumerates only VERIFIED / External rows. Update the traceability table when adding/removing claims (P5-C-* IDs).

## Architecture

The pipeline is a 13-phase linear orchestration in `scripts/run_all.py`. There is no service layer, no plugin system, and no alternative engines — `run_all.py` calling into `src/` is the single computational authority (`docs/provenance.md`).

### Data flow

```
parameters.yaml ── system_generator ──┐
                                       ├─► SCM (causal_model) ──► observation_model ──► extreme_risk
correlation matrix (Gaussian copula) ─┘                                                       │
                                                                                              ▼
threshold_profiles.yaml ──► governance_engine (non-comp gates + compensatory comparator) ─► outcomes
                                                                                              │
                                                                                              ▼
                                                                                       friction_model
                                                                                              │
                                                                                              ▼
            ┌─── lifecycle (drift over 12 periods) ──┐
            ├─── nsga2_search (60 pop × 30 gen) ──────┤
            ├─── sensitivity (Sobol, 7 params) ──────┼─► figures/ + tables/
            ├─── dca (decision curve analysis) ──────┤
            ├─── inference (bootstrap + Bayesian) ────┤
            └─── replication (two-build identity) ───┘
```

### Module map (under `src/`)

| Module | Role |
|---|---|
| `generators/system_generator.py` | Generate 10k synthetic AI systems via Gaussian copula with Beta marginals |
| `generators/observation_model.py` | Layer measurement noise, evidence-regime effects, adversarial misreporting on latent traits |
| `scm/causal_model.py` | Load DAG from `config/scm_graph.dot`; apply structural equations from `scm_functions.yaml` |
| `policy/governance_engine.py` | `GovernancePolicyEngine` (non-compensable five-gate model) and `CompensatoryPolicyEngine` (comparator) |
| `metrics/friction_model.py` | Audit / delay / monitoring / escalation / documentation costs |
| `analysis/lifecycle.py` | 12-period drift + re-audit simulation |
| `analysis/extreme_risk.py` | Generalised Pareto tail-risk model (tail_index=0.3, 95th-pct threshold) |
| `analysis/sensitivity.py` | Sobol global sensitivity via SALib (Saltelli sampling) |
| `analysis/inference.py` | Bootstrap CIs (500 resamples) + Bayesian rate intervals |
| `analysis/dca.py` | Vickers & Elkin (2006) decision curve analysis |
| `optimisation/nsga2_search.py` | pymoo NSGA-II over 5-D threshold space, 4 objectives; `identify_sweet_spot` filters Pareto solutions |
| `validation/validation_suite.py` | 7 internal validity checks (safety monotonicity, bias-harm linkage, etc.) run as Phase 1 |
| `replication/replication.py` | Two-build identical-seed protocol; passes only at 0.0 absolute difference on key metrics |
| `preregistration/plan.py` | Loads `analysis_plan.yaml`, computes plan hash (recorded in run manifest) |
| `plotting/figures.py` | Generates the six manuscript figures from pipeline outputs |
| `utils/helpers.py` | `sigmoid`, `derive_seed`, `dict_hash`, YAML/JSON IO, timestamps |

### Configuration authorities

- `config/parameters.yaml` — all distribution parameters, SCM coefficients, friction costs, scenario grid (parameters tagged `assumed` vs `sourced`)
- `thresholds/threshold_profiles.yaml` — the four policy profiles (permissive / moderate / strict / very_strict); **sole** authority
- `analysis_plan.yaml` — pre-registered hypotheses (H1–H4), estimands, and reporting plan; hash committed via `run_manifest.json`
- `scm_functions.yaml` v1.0 — versioned library of structural equation forms
- `config/scm_graph.dot` — 28-node, 19-edge DAG (loaded by `causal_model.load_scm_graph`)
- `config/harness_settings.json` — seeds, timeouts, fail-fast flag for the reproduction harness
- `config/notebook_plan.json` — execution order and expected outputs for the four notebooks
- `config/expected_outputs.json` — pinned SHA-256 hashes that fresh outputs must match
- `config/trace_map.json` — maps each output artefact to the phase, script, notebook, and RTM target IDs that produced/consume it

### Notebooks

`notebooks/` contains four notebooks driven by `scripts/notebook_runner.py`. Notebook 01 embeds the full pipeline for standalone use; in `reproduce_all.py` the env var `P5_SKIP_EMBEDDED_SIM=1` causes it to consume the artefacts already produced by `run_all.py` rather than re-running the simulation. Do not break this contract.

### Platform notes

- The pipeline runs on Windows; `notebook_runner.py` installs `WindowsSelectorEventLoopPolicy` and a 180–600s startup timeout for cold Jupyter kernels.
- The shell available here is PowerShell; use PowerShell syntax (`$env:VAR`, backtick line continuation) for shell commands. Bash via the Bash tool also works for POSIX scripts.
- Figures are excluded from hash validation (platform-dependent rendering); their inputs are hash-validated upstream.
