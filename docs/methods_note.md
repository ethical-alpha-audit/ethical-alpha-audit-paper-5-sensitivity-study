# Methods Note (v2.0)
**Repository:** ethical-alpha-audit-paper-5-sensitivity-study

## Summary of methodological choices

This document records key methodological choices made during Stage 7 repository
re-execution and their rationale. These notes complement the Methods section
of the main paper.

### 1. Sobol global sensitivity (RC-02 Plan A)
- Original execution used N = 64 base samples (576 total Saltelli samples) and
  hard-coded confidence-interval values (S1_conf = ST_conf = 0.05). The
  resulting indices (notably ST(safety_gate) ≈ 1.00 on detection rate) were
  unstable artefacts of insufficient sampling.
- Stage 7 re-execution: N-progression over N ∈ {64, 128, 256, 512, 1024} with
  a 50–200-resample bootstrap on each index value. At N = 1024 (primary), all
  CIs are tight enough to interpret. The N-progression diagnostic is archived
  in `outputs/processed/sobol_convergence.json` and demonstrates convergence
  of ST(safety_gate) to ≈ 0.6 with 95% bootstrap CI within [0.43, 0.69].
- Sobol n_systems (per-sample evaluation budget): 400 at N=1024 (compute
  budget); 1,500 at N ≤ 512.

### 2. NSGA-II multi-seed convergence (RC-06)
- Original execution reported 60 candidate Pareto-optimal solutions at the
  search budget specified (population 60, 30 generations) without convergence
  diagnostics.
- Stage 7 re-execution: 3 seeds (42, 123, 7777) with per-generation hypervolume
  trajectory computed against reference point (1.0, 1.0) on (1−detection,
  1−throughput). Frontier overlap is computed pairwise as the fraction of
  seed-A Pareto points within tolerance 0.05 of nearest seed-B point.
- Per-seed Pareto count and final hypervolume are archived in
  `outputs/processed/pareto_seed_stability.csv` and the full HV trajectory
  in `outputs/processed/nsga2_convergence.json`.

### 3. Decoupled-variant SCM (RC-04 Plan A)
- The implemented variant introduces an independent latent `harm_latent ~
  Beta(2.5, 2.0)` to drive baseline_harm in place of intrinsic_safety.
- The safety-gate observation continues to derive from intrinsic_safety with
  measurement noise, so the observed safety signal contains no information
  about harm in the variant.
- Result is reported alongside the coupled-SCM result for direct sensitivity
  quantification (`outputs/processed/scm_coupling_sensitivity.json`).

### 4. Weighting-scheme sensitivity (RC-03)
- Five weighted-average composite weighting schemes evaluated against the
  baseline non-compensatory architecture under regime AR2 conditions
  (paired runs, base rate 20%, 5 replicates each).

### 5. Lifecycle aggregation (RC-12)
- The `mean_cumulative_drift` field has been added to the lifecycle summary
  (`outputs/processed/lifecycle_summary_v2.json`). Per-period drift
  trajectories are archived at `outputs/processed/lifecycle_per_period.csv`.
- Detailed lifecycle interpretation in the main paper remains downscoped per
  RC-12 fallback decision; numerical aggregates are provided for traceability
  but no detailed lifecycle inference is made in the main text.

### 6. Sweet-spot framing removal (RC-14 Plan B)
- The `identify_sweet_spot` function in `src/optimisation/nsga2_search.py` has
  been deprecated; `outputs/processed/pareto_solutions.csv` no longer carries
  an `in_sweet_spot` column. Reference outputs (legacy) have been stripped
  of this column.

### 7. Companion-paper severance (RC-05)
- All references to unpublished companion papers have been removed from the
  repository documentation. The framework is positioned as a stand-alone
  methodological contribution with no load-bearing dependency on companion
  programme content.
