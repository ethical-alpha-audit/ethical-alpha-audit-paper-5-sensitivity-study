#!/usr/bin/env python3
"""Sobol N-progression runner — Stage 8 upgrade (true Sobol sequence).

Runs Sobol global sensitivity at N in {128, 256, 512, 1024, 2048} on the
full simulation pipeline. Uses checkpointing so a crash mid-run resumes
from the last checkpoint. Writes:

    outputs/processed/sobol_convergence.json   (full N-progression)
    outputs/tables/sobol_<outcome>.csv         (primary N=2048 results)

Run from the repo root:
    python run_sobol_n_progression.py

Estimated wall time on a modern laptop (Python 3.11, no GIL contention):
    ~4-6 minutes for N=128..1024
    ~5-7 minutes for N=2048
    Total: ~10-15 minutes
"""
import sys
import os
import json
import time
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(".").resolve()
sys.path.insert(0, str(REPO))
os.environ["PYTHONHASHSEED"] = "0"

from src.utils.helpers import load_yaml
from src.generators.system_generator import generate_systems, classify_systems
from src.generators.observation_model import apply_observation_model
from src.scm.causal_model import apply_scm
from src.policy.governance_engine import GovernancePolicyEngine, evaluate_policy_outcomes
from src.metrics.friction_model import compute_friction
from src.analysis.sensitivity import saltelli_sample, sobol_analyze, bootstrap_indices

CONFIG = load_yaml("config/parameters.yaml")
PARAM_NAMES = ["safety_gate", "evidence_gate", "bias_gate", "calibration_gate",
               "traceability_gate", "auditability_noise", "unsafe_base_rate"]
PARAM_BOUNDS = [[0.2, 0.8], [0.2, 0.8], [0.1, 0.7], [0.2, 0.7],
                [0.2, 0.7], [0.02, 0.15], [0.05, 0.35]]
N_GRID = [128, 256, 512, 1024, 2048]
N_BOOT = 200
SOBOL_N_SYS = 2000
OUTCOMES = ["unsafe_detection_rate", "safe_throughput",
            "false_negative_harm", "mean_total_friction"]
PRIMARY_N = 2048

CKPT_DIR = REPO / "logs" / "sobol_ckpt"
CKPT_DIR.mkdir(parents=True, exist_ok=True)


def evaluate(params, seed=42):
    """One end-to-end pipeline evaluation under a parameter dict."""
    profile = {n: float(params[n]) for n in
               ["safety_gate", "evidence_gate", "bias_gate",
                "calibration_gate", "traceability_gate"]}
    rng = np.random.RandomState(seed)
    df = generate_systems(CONFIG, SOBOL_N_SYS, seed=seed)
    df = classify_systems(df, CONFIG, unsafe_base_rate=float(params["unsafe_base_rate"]))
    df = apply_scm(df, CONFIG.get("scm", {}), rng)
    obs_cfg = dict(CONFIG.get("observation", {}))
    obs_cfg["measurement_noise_sd"] = float(params["auditability_noise"])
    df = apply_observation_model(df, obs_cfg, evidence_regime="mixed", rng=rng)
    eng = GovernancePolicyEngine(profile)
    pres = eng.evaluate(df)
    out = evaluate_policy_outcomes(df, pres)
    fric = compute_friction(df, pres, CONFIG.get("friction", {}), profile)
    out["mean_total_friction"] = fric["mean_total_friction"]
    return out


def run_at_n(n, seed=42):
    print(f"\n=== Sobol at N={n} ===", flush=True)
    t0 = time.time()
    d = len(PARAM_NAMES)
    samples = saltelli_sample(n, d, PARAM_BOUNDS, seed=seed, scramble=True)
    n_total = len(samples)
    print(f"  Total Saltelli evaluations: {n_total}", flush=True)

    ckpt_path = CKPT_DIR / f"sobol_N{n}.pkl"
    out_arr = {oc: np.zeros(n_total) for oc in OUTCOMES}
    start_i = 0
    if ckpt_path.exists():
        with open(ckpt_path, "rb") as f:
            ck = pickle.load(f)
        if ck["n_total"] == n_total:
            out_arr = ck["out_arr"]
            start_i = ck["i"]
            print(f"  Resuming from i={start_i}", flush=True)

    for i in range(start_i, n_total):
        pd_ = dict(zip(PARAM_NAMES, samples[i]))
        try:
            m = evaluate(pd_, seed=42)
            for oc in OUTCOMES:
                out_arr[oc][i] = m.get(oc, 0.0)
        except Exception as e:
            if i < 3:
                print(f"  WARN at i={i}: {e}", flush=True)
        if (i + 1) % 500 == 0:
            with open(ckpt_path, "wb") as f:
                pickle.dump({"i": i + 1, "n_total": n_total, "out_arr": out_arr}, f)
            elapsed = time.time() - t0
            rate = (i + 1 - start_i) / max(elapsed, 1e-3)
            eta = (n_total - i - 1) / max(rate, 0.1)
            print(f"  {i+1}/{n_total} ({rate:.1f}/s, ETA {eta:.0f}s)", flush=True)

    print(f"  Evals done in {time.time()-t0:.1f}s", flush=True)

    results = {}
    for oc in OUTCOMES:
        S1, ST = sobol_analyze(out_arr[oc], n, d)
        ci = bootstrap_indices(out_arr[oc], n, d, n_resamples=N_BOOT, seed=seed + 99)
        results[oc] = {
            "parameter": PARAM_NAMES,
            "S1": np.clip(S1, -0.5, 1.5).tolist(),
            "S1_ci_lo": ci["S1_lo"].tolist(),
            "S1_ci_hi": ci["S1_hi"].tolist(),
            "ST": np.clip(ST, 0, 2.0).tolist(),
            "ST_ci_lo": ci["ST_lo"].tolist(),
            "ST_ci_hi": ci["ST_hi"].tolist(),
        }
    if ckpt_path.exists():
        ckpt_path.unlink()
    return results, n_total


# Run all N levels
all_results = {}
for n in N_GRID:
    res, _ = run_at_n(n)
    all_results[str(n)] = res
    sg = PARAM_NAMES.index("safety_gate")
    r = res["unsafe_detection_rate"]
    print(f"  -> ST(safety_gate)={r['ST'][sg]:.3f} "
          f"CI[{r['ST_ci_lo'][sg]:.3f}, {r['ST_ci_hi'][sg]:.3f}]",
          flush=True)

# Save N-progression file
output = {
    "config": {
        "N_grid": N_GRID,
        "primary_N": PRIMARY_N,
        "n_bootstrap": N_BOOT,
        "sobol_n_systems": SOBOL_N_SYS,
        "param_names": PARAM_NAMES,
        "param_bounds": PARAM_BOUNDS,
        "sampler": "scipy.stats.qmc.Sobol (Owen-scrambled)",
        "regime": "AR_sobol_progression_v3",
    },
    "results": all_results,
}
out_path = REPO / "outputs" / "processed" / "sobol_convergence.json"
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w") as f:
    json.dump(output, f, indent=2)
print(f"\nWrote {out_path}")

# Save N=2048 as primary CSV outputs
for oc in OUTCOMES:
    rec = all_results[str(PRIMARY_N)][oc]
    df = pd.DataFrame({
        "parameter": rec["parameter"],
        "S1": rec["S1"], "S1_ci_lo": rec["S1_ci_lo"], "S1_ci_hi": rec["S1_ci_hi"],
        "ST": rec["ST"], "ST_ci_lo": rec["ST_ci_lo"], "ST_ci_hi": rec["ST_ci_hi"],
        "status": ["ASSUMED" if p in ("auditability_noise", "unsafe_base_rate")
                   else "configured" for p in rec["parameter"]],
        "regime": "AR_sobol_N2048",
    }).sort_values("ST", ascending=False).reset_index(drop=True)
    df["rank"] = range(1, len(df) + 1)
    csv_path = REPO / "outputs" / "tables" / f"sobol_{oc}.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
print(f"Wrote outputs/tables/sobol_*.csv (primary N={PRIMARY_N})")

# Summary report for manuscript / supplement updates
print("\n" + "=" * 70)
print("N-progression summary: ST(safety_gate) on detection_rate")
print("=" * 70)
sg = PARAM_NAMES.index("safety_gate")
for n in N_GRID:
    r = all_results[str(n)]["unsafe_detection_rate"]
    print(f"  N={n:5d}: ST={r['ST'][sg]:.3f}  "
          f"CI[{r['ST_ci_lo'][sg]:.3f}, {r['ST_ci_hi'][sg]:.3f}]")

print("\n" + "=" * 70)
print(f"N={PRIMARY_N} — full ST ranking on detection_rate (with 95% bootstrap CI)")
print("=" * 70)
r = all_results[str(PRIMARY_N)]["unsafe_detection_rate"]
order = sorted(range(len(PARAM_NAMES)), key=lambda i: -r["ST"][i])
for i in order:
    print(f"  {PARAM_NAMES[i]:25s}: ST={r['ST'][i]:.3f}  "
          f"CI[{r['ST_ci_lo'][i]:.3f}, {r['ST_ci_hi'][i]:.3f}]")

print("\n" + "=" * 70)
print(f"N={PRIMARY_N} — full ST ranking across all outcomes")
print("=" * 70)
for oc_key, oc_label in [("unsafe_detection_rate", "Detection"),
                          ("safe_throughput", "Throughput"),
                          ("false_negative_harm", "FN harm"),
                          ("mean_total_friction", "Friction")]:
    r = all_results[str(PRIMARY_N)][oc_key]
    print(f"\n  {oc_label}:")
    order = sorted(range(len(PARAM_NAMES)), key=lambda i: -r["ST"][i])
    for i in order:
        print(f"    {PARAM_NAMES[i]:25s}: ST={r['ST'][i]:.3f}  "
              f"[{r['ST_ci_lo'][i]:.3f}, {r['ST_ci_hi'][i]:.3f}]")
