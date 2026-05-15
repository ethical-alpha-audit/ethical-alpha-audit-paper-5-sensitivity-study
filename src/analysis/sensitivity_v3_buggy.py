"""Global Sensitivity Analysis using Sobol variance decomposition.

============================================================================
PRESERVED FORENSIC ARTEFACT — DO NOT IMPORT OR EXECUTE.

This file is the v3.0 implementation as delivered by the Stage 8 Sobol
bundle (Sobol_2048_Upgrade_Bundle.zip). It contains the construction
bug discovered at WS-3 Phase 3.3a: the saltelli_sample function uses
halves of a single Owen-scrambled Sobol sequence as A and B matrices,
which violates the Saltelli (2010) design's independence assumption.
A vs B correlation was Pearson r = 0.999998 for column 0 and |r| > 0.5
for all 7 columns, biasing all ST estimates toward zero.

The corrected implementation lives at sibling file `sensitivity.py`
(SALib wrapper). The two files are preserved together so that future
readers can study the actual buggy code alongside the corrected
implementation.

Full diagnostic trail, root-cause analysis, fix rationale, and forward
checklist for similar workstreams: see
`docs/p5_sobol_bundle_construction_bug.md` in this repo.

DO NOT REVERT to this implementation. DO NOT CALL these functions.
This file is for documentation and pedagogical purposes only.
============================================================================

v3.0 (2026-04, Stage 8): replaces the v1/v2 pseudo-random saltelli_sample
fallback with a true Owen-scrambled Sobol low-discrepancy sequence via
scipy.stats.qmc.Sobol (SciPy >= 1.7). API is backward-compatible with v2:
saltelli_sample, sobol_analyze, run_sobol_analysis, format_sensitivity_table
all retain their v2 signatures. New: bootstrap_indices for explicit CIs.
"""
import numpy as np
import pandas as pd
from scipy.stats import qmc


def saltelli_sample(n_base, d, bounds, seed=42, scramble=True):
    """Generate a Saltelli sampling matrix using a true Sobol sequence.

    Parameters
    ----------
    n_base : int
        Base sample size N. Total Saltelli evaluations = N * (2 + d).
        N should ideally be a power of 2 (Sobol balance property).
    d : int
        Number of input parameters.
    bounds : list of [lo, hi]
        Per-parameter bounds, length d.
    seed : int
        Seed for the Sobol scrambling RNG (reproducibility).
    scramble : bool
        Owen scrambling on the Sobol sequence (recommended; default True).

    Returns
    -------
    samples : ndarray, shape ((2 + d) * N, d)
        Stacked [A; B; AB_1; AB_2; ...; AB_d] matrices in original parameter scale.
    """
    sampler = qmc.Sobol(d=d, scramble=scramble, seed=seed)
    pts = sampler.random(n=2 * n_base)
    A = pts[:n_base]
    B = pts[n_base:]

    bounds = np.asarray(bounds, dtype=float)
    A = A * (bounds[:, 1] - bounds[:, 0]) + bounds[:, 0]
    B = B * (bounds[:, 1] - bounds[:, 0]) + bounds[:, 0]

    samples = [A, B]
    for j in range(d):
        AB_j = A.copy()
        AB_j[:, j] = B[:, j]
        samples.append(AB_j)
    return np.vstack(samples)


def sobol_analyze(y_all, n_base, d):
    """Compute first-order (S1) and total-order (ST) Sobol indices.

    Saltelli (2010) variance-based estimators:
        S1[j] = mean(y_B * (y_AB_j - y_A)) / Var(y)
        ST[j] = 0.5 * mean((y_A - y_AB_j)^2) / Var(y)

    Returns
    -------
    S1, ST : ndarray, shape (d,)
    """
    y_A = y_all[:n_base]
    y_B = y_all[n_base : 2 * n_base]
    var_total = np.var(np.concatenate([y_A, y_B]))
    if var_total < 1e-12:
        return np.zeros(d), np.zeros(d)

    S1 = np.zeros(d)
    ST = np.zeros(d)
    for j in range(d):
        y_AB_j = y_all[(2 + j) * n_base : (3 + j) * n_base]
        S1[j] = np.mean(y_B * (y_AB_j - y_A)) / var_total
        ST[j] = 0.5 * np.mean((y_A - y_AB_j) ** 2) / var_total
    return S1, ST


def bootstrap_indices(y_all, n_base, d, n_resamples=200, seed=42):
    """Bootstrap 95% CIs on S1 and ST by resampling the base index set.

    Returns dict with keys S1_lo, S1_hi, ST_lo, ST_hi (each shape (d,)).
    """
    rng = np.random.RandomState(seed)
    S1_b = np.zeros((n_resamples, d))
    ST_b = np.zeros((n_resamples, d))
    n_total = (2 + d) * n_base

    for b in range(n_resamples):
        idx = rng.choice(n_base, size=n_base, replace=True)
        y_r = np.zeros(n_total)
        y_r[:n_base] = y_all[:n_base][idx]
        y_r[n_base : 2 * n_base] = y_all[n_base : 2 * n_base][idx]
        for j in range(d):
            base_off = (2 + j) * n_base
            y_r[base_off : base_off + n_base] = y_all[base_off : base_off + n_base][idx]
        s1, st = sobol_analyze(y_r, n_base, d)
        S1_b[b] = s1
        ST_b[b] = st

    return {
        "S1_lo": np.percentile(S1_b, 2.5, axis=0),
        "S1_hi": np.percentile(S1_b, 97.5, axis=0),
        "ST_lo": np.percentile(ST_b, 2.5, axis=0),
        "ST_hi": np.percentile(ST_b, 97.5, axis=0),
    }


def run_sobol_analysis(evaluate_fn, param_names=None, param_bounds=None,
                       n_samples=2048, seed=42, n_bootstrap=200,
                       output_names=None, scramble=True):
    """Run Sobol global sensitivity analysis with Owen-scrambled Sobol points
    and bootstrap confidence intervals.

    Parameters
    ----------
    evaluate_fn : callable(dict) -> dict
        Takes a parameter dict, returns a dict of outcome metrics.
    n_samples : int
        Base sample size N (default 2048).
    """
    if param_names is None:
        param_names = ['safety_gate', 'evidence_gate', 'bias_gate',
                       'calibration_gate', 'traceability_gate',
                       'auditability_noise', 'unsafe_base_rate']
    if param_bounds is None:
        param_bounds = [[0.2, 0.8], [0.2, 0.8], [0.1, 0.7],
                        [0.2, 0.7], [0.2, 0.7], [0.02, 0.15], [0.05, 0.35]]
    if output_names is None:
        output_names = ['unsafe_detection_rate', 'safe_throughput',
                        'false_negative_harm', 'mean_total_friction']

    d = len(param_names)
    samples = saltelli_sample(n_samples, d, param_bounds, seed=seed, scramble=scramble)
    outputs = {name: np.zeros(len(samples)) for name in output_names}

    for i, params in enumerate(samples):
        param_dict = dict(zip(param_names, params))
        try:
            metrics = evaluate_fn(param_dict)
            for name in output_names:
                outputs[name][i] = metrics.get(name, 0.0)
        except Exception:
            pass

    results = {}
    for name in output_names:
        S1, ST = sobol_analyze(outputs[name], n_samples, d)
        ci = bootstrap_indices(outputs[name], n_samples, d,
                               n_resamples=n_bootstrap, seed=seed + 99)
        results[name] = pd.DataFrame({
            'parameter': param_names,
            'S1': np.clip(S1, -0.5, 1.5),
            'S1_ci_lo': ci['S1_lo'],
            'S1_ci_hi': ci['S1_hi'],
            'ST': np.clip(ST, 0, 2.0),
            'ST_ci_lo': ci['ST_lo'],
            'ST_ci_hi': ci['ST_hi'],
        }).sort_values('ST', ascending=False)
    return results


def format_sensitivity_table(sobol_results, assumed_params=None):
    """Format Sobol results as a ranked table, flagging assumed parameters."""
    if assumed_params is None:
        assumed_params = set()
    tables = {}
    for outcome, df in sobol_results.items():
        df = df.copy()
        df['status'] = df['parameter'].apply(
            lambda p: 'ASSUMED' if p in assumed_params else 'configured'
        )
        df['rank'] = range(1, len(df) + 1)
        tables[outcome] = df
    return tables
