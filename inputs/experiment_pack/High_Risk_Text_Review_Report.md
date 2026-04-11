# High-Risk Text Review Report

## Summary

High-risk files were preserved unless an edit was clearly harmless. This repository contains multiple files where even text-only changes could affect execution, reproducibility, or manuscript-linked artefacts.

## Flagged high-risk areas

| Path / Area | Why it is risky | Automated cleanup decision | Recommended manual remediation |
|---|---|---|---|
| `requirements.txt` | Dependency resolution affects fresh installs and numerical reproducibility. | Not edited. | Add a locked requirements file or equivalent resolver output grounded in tested versions. |
| `environment.yml` | Environment solver input controls package versions and platform behaviour. | Not edited. | Export a tested lock or explicit package build set for release. |
| `Dockerfile` | Build instructions affect runtime and reproducibility. | Not edited. | Verify container build in a clean runner and document the image digest used for release. |
| `analysis_plan.yaml` | Protocol text may be consumed programmatically or relied on for preregistration integrity. | Not edited. | Review manually only if protocol language is demonstrably stale. |
| `config/`, `thresholds/`, `decision_curve_weights.yaml`, `scm_functions.yaml` | Configuration text controls thresholds, SCM behaviour, and simulation assumptions. | Not edited. | Treat as scientific logic, not editorial prose. Amend only with author sign-off. |
| `outputs/` and `reproducibility/` | Generated artefacts may act as manuscript fixtures or validation references. | Not edited. | Regenerate only in a controlled release workflow and retain provenance hashes. |
| `scripts/run_all.py` and other execution scripts | Entry-point text and inline comments sit adjacent to execution logic. | Not edited except for a wrapper docstring in `scripts/build_figures.py`. | Review manually if user-facing CLI/help text needs refinement. |

## AI-detection summary

### Cleaned

- `README.md`: tightened structure, removed low-value narrative looseness, and clarified reproducibility limitations.
- `scripts/build_figures.py`: replaced a potentially misleading wrapper docstring with a more accurate description.

### Flagged or preserved

- No high-confidence assistant-style chatter or hallucinated parameter/return descriptions were found in source modules during the scan.
- Scientific, algorithmic, threshold, and configuration explanations were preserved to avoid unsupported rewrites.

## Dependency risk notes

The repository uses lower-bound version specifiers such as `numpy>=1.24` and `pandas>=2.0`, with no lock file. That is acceptable for general setup but weaker than journal-grade exact replay.

## Scientific-claim verification notes

No scientific comments or docstrings were rewritten where the repository did not directly evidence the claim. Higher-risk scientific narrative remains for author review rather than automated normalization.
