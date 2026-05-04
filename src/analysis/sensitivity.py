"""Global Sensitivity Analysis using Sobol variance decomposition.

v3.1 (2026-05, Phase 3.3a-bugfix): WRAPPER over SALib's canonical
Saltelli sampler and Sobol analyzer. Replaces the v3.0 custom
implementation that violated the Saltelli design's independence
assumption (A and B halves of a single Owen-scrambled Sobol sequence
were correlated; column 0 had Pearson r = 0.999998, biasing all ST
estimates toward zero).

The v2 public API is preserved:
    saltelli_sample(n_base, d, bounds, seed, scramble) -> ndarray
    sobol_analyze(y_all, n_base, d) -> (S1, ST)
    bootstrap_indices(y_all, n_base, d, n_resamples, seed) -> dict
    run_sobol_analysis(...) -> dict[outcome -> DataFrame]
    format_sensitivity_table(sobol_results, assumed_params) -> dict

Implementation:
    - saltelli_sample wraps SALib.sample.sobol.sample (the modern,
      non-deprecated function; the older saltelli.sample is deprecated
      since SALib 1.4.6).
    - sobol_analyze wraps SALib.analyze.sobol.analyze.
    - bootstrap_indices uses SALib.analyze.sobol.analyze with
      num_resamples + conf_level=0.95 + keep_resamples=True; returns
      percentile-based (lo, hi) = (np.percentile(2.5), np.percentile(97.5))
      from the bootstrap distribution. This preserves the v3.0 percentile
      semantics (rather than SALib's default symmetric half-width via
      S1_conf), giving methodologically rigorous representation of
      bootstrap uncertainty especially near distribution boundaries.
    - run_sobol_analysis and format_sensitivity_table are orchestration
      and presentation; unchanged from v3.0.

References
----------
- Saltelli, A., et al. (2010). Variance based sensitivity analysis of
  model output. Computer Physics Communications, 181(2), 259-270.
- Iwanaga, T., Usher, W., & Herman, J. (2022). Toward SALib 2.0.
  Socio-Environmental Systems Modelling, 4.
- Herman, J., & Usher, W. (2017). SALib: an open-source Python library
  for sensitivity analysis. Journal of Open Source Software, 2(9), 97.

Bug record
----------
See ``docs/p5_sobol_bundle_construction_bug.md`` in the P5 repo for
the full diagnostic trail (Phase 3.3a Checks 1-7), root-cause analysis,
fix rationale, and downstream cleanup audit scope (WS-Release-P5).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from SALib.sample import sobol as _salib_sobol_sample
from SALib.analyze import sobol as _salib_sobol_analyze


def _build_problem(d: int, bounds: list, names: list | None = None) -> dict:
    """Build SALib problem-definition dict."""
    if names is None:
        names = [f"x{i}" for i in range(d)]
    return {
        "num_vars": d,
        "names": list(names),
        "bounds": [list(b) for b in bounds],
    }


def saltelli_sample(n_base, d, bounds, seed=42, scramble=True):
    """Generate a Saltelli sampling matrix using SALib's Sobol sampler.

    Wraps :func:`SALib.sample.sobol.sample` with calc_second_order=False
    to match the v3.0 public API (matrix shape ``((2 + d) * n_base, d)``).

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
    samples : ndarray, shape ((2 + d) * n_base, d)
        SALib-constructed Saltelli matrix in original parameter scale.
        Internal layout differs from the v3.0 custom implementation;
        consumers should pass the full matrix to :func:`sobol_analyze`
        rather than slicing manually.
    """
    problem = _build_problem(d, bounds)
    samples = _salib_sobol_sample.sample(
        problem,
        N=n_base,
        calc_second_order=False,
        scramble=scramble,
        seed=seed,
    )
    return samples


def sobol_analyze(y_all, n_base, d):
    """Compute first-order (S1) and total-order (ST) Sobol indices.

    Wraps :func:`SALib.analyze.sobol.analyze` with the canonical
    Saltelli (2010) variance-based estimator. SALib's implementation
    correctly handles the Saltelli matrix construction (no A/B
    independence violation as in the v3.0 custom estimator).

    Parameters
    ----------
    y_all : ndarray, shape ((2 + d) * n_base,)
        Output values evaluated at the full Saltelli sample matrix
        produced by :func:`saltelli_sample`.
    n_base : int
        Base sample size N (used by SALib internally to recover the
        matrix layout; passed for API compatibility).
    d : int
        Number of input parameters.

    Returns
    -------
    S1, ST : ndarray, shape (d,)
        First-order and total-order Sobol indices.
    """
    var_total = np.var(y_all)
    if var_total < 1e-12:
        return np.zeros(d), np.zeros(d)
    # SALib's analyze requires problem dict; bounds are not used by the
    # estimator math but the function expects the dict shape.
    problem = _build_problem(d, [[0.0, 1.0]] * d)
    Si = _salib_sobol_analyze.analyze(
        problem,
        np.asarray(y_all, dtype=float),
        calc_second_order=False,
        num_resamples=10,        # central-estimate call; bootstrap done separately
        conf_level=0.95,
        print_to_console=False,
    )
    return np.asarray(Si["S1"]), np.asarray(Si["ST"])


def bootstrap_indices(y_all, n_base, d, n_resamples=200, seed=42):
    """Percentile bootstrap 95% CIs on S1 and ST.

    Uses SALib's ``sobol.analyze`` with ``keep_resamples=True`` to obtain
    the full bootstrap distribution of S1 and ST estimates (one per
    resample, per parameter), then computes 2.5th and 97.5th percentiles
    along the resample axis. This preserves the v3.0 implementation's
    percentile-CI intent (rather than the symmetric half-width
    approximation from SALib's default ``S1_conf``).

    Percentile CIs are preferred for parameter estimates near distribution
    boundaries (Sobol indices in [0, 1]) where the bootstrap distribution
    can be skewed and symmetric half-width CIs would extend out of range.

    Parameters
    ----------
    y_all : ndarray
        Output array as for :func:`sobol_analyze`.
    n_base : int
        Base sample size N (passed for API symmetry; SALib infers from
        the y_all length and problem dict).
    d : int
        Number of input parameters.
    n_resamples : int
        Number of bootstrap resamples (default 200, matching v3.0).
    seed : int
        Seed for the bootstrap RNG (reproducibility).

    Returns
    -------
    dict with keys S1_lo, S1_hi, ST_lo, ST_hi, each ndarray shape (d,).
    Lo and hi are the 2.5th and 97.5th percentiles of the bootstrap
    distribution.
    """
    problem = _build_problem(d, [[0.0, 1.0]] * d)
    Si = _salib_sobol_analyze.analyze(
        problem,
        np.asarray(y_all, dtype=float),
        calc_second_order=False,
        num_resamples=n_resamples,
        conf_level=0.95,
        keep_resamples=True,
        print_to_console=False,
        seed=seed,
    )
    # SALib v1.5.2 returns S1_conf_all and ST_conf_all as
    # (n_resamples, d)-shaped arrays of bootstrap S1/ST estimates.
    S1_resamples = np.asarray(Si["S1_conf_all"])
    ST_resamples = np.asarray(Si["ST_conf_all"])
    return {
        "S1_lo": np.percentile(S1_resamples, 2.5, axis=0),
        "S1_hi": np.percentile(S1_resamples, 97.5, axis=0),
        "ST_lo": np.percentile(ST_resamples, 2.5, axis=0),
        "ST_hi": np.percentile(ST_resamples, 97.5, axis=0),
    }


def run_sobol_analysis(evaluate_fn, param_names=None, param_bounds=None,
                       n_samples=2048, seed=42, n_bootstrap=200,
                       output_names=None, scramble=True):
    """Run Sobol global sensitivity analysis with SALib-canonical
    sampling and bootstrap confidence intervals.

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
