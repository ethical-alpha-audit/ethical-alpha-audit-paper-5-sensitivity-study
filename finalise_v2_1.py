#!/usr/bin/env python3
"""Stage 8 post-Sobol housekeeping: regenerate Figure 3, refresh manifest.

Run from the repo root AFTER run_sobol_n_progression.py:
    python finalise_v2_1.py
"""
import os
import json
import hashlib
import shutil
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(".").resolve()

# =========================================================
# 1. REGENERATE FIGURE 3 from N=2048 results
# =========================================================
print("=" * 60)
print("Step 1/3: Regenerate Figure 3 (Sobol N=2048)")
print("=" * 60)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
})

sobol = json.load(open(REPO / "outputs" / "processed" / "sobol_convergence.json"))
PRIMARY_N = str(sobol["config"]["primary_N"])
PARAMS = sobol["config"]["param_names"]
OUTCOMES = [("unsafe_detection_rate", "Unsafe Detection Rate"),
            ("safe_throughput", "Safe Throughput"),
            ("false_negative_harm", "False Negative Harm"),
            ("mean_total_friction", "Mean Total Friction")]
BAR_COLOR = "#0072B2"

fig, axes = plt.subplots(1, 4, figsize=(18, 5))
for ax, (oc_key, oc_label) in zip(axes, OUTCOMES):
    rec = sobol["results"][PRIMARY_N][oc_key]
    st = np.array(rec["ST"])
    ci_lo = np.array(rec["ST_ci_lo"])
    ci_hi = np.array(rec["ST_ci_hi"])
    order = np.argsort(-st)
    params_sorted = [PARAMS[i] for i in order]
    st_sorted = st[order]
    err_lo = (st - ci_lo)[order]
    err_hi = (ci_hi - st)[order]
    y_pos = np.arange(len(params_sorted))
    ax.barh(y_pos, st_sorted, xerr=[err_lo, err_hi],
            color=BAR_COLOR, edgecolor="none",
            error_kw={"ecolor": "#333333", "capsize": 3, "elinewidth": 0.8})
    ax.set_yticks(y_pos)
    ax.set_yticklabels(params_sorted)
    ax.invert_yaxis()
    ax.set_xlabel("Total-order Sobol Index")
    ax.set_title(oc_label)
    ax.set_xlim(0, max(0.7, st_sorted.max() * 1.15))
    ax.grid(True, axis="x", alpha=0.25, linestyle=":")
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

plt.tight_layout()
fig_path = REPO / "outputs" / "figures" / "fig3_sensitivity.png"
fig_path.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(fig_path, dpi=300, bbox_inches="tight")
plt.close()
print(f"  Wrote {fig_path}")

legacy = REPO / "inputs" / "experiment_pack" / "outputs" / "figures" / "fig3_sensitivity.png"
if legacy.parent.exists():
    shutil.copy(fig_path, legacy)
    print(f"  Mirrored to {legacy}")


# =========================================================
# 2. REFRESH MANIFEST.sha256
# =========================================================
print("\n" + "=" * 60)
print("Step 2/3: Refresh MANIFEST.sha256")
print("=" * 60)

manifest = []
for f in sorted((REPO / "outputs").rglob("*")):
    if f.is_file() and not f.name.startswith("."):
        manifest.append(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  "
                        f"{f.relative_to(REPO).as_posix()}")
for f in sorted((REPO / "reproducibility").rglob("*")):
    if f.is_file() and not f.name.startswith("."):
        manifest.append(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  "
                        f"{f.relative_to(REPO).as_posix()}")
for extra in ['config/parameters.yaml', 'thresholds/threshold_profiles.yaml',
              'analysis_plan.yaml', 'scm_functions.yaml', 'VERSION',
              'repro_manifest.json']:
    p = REPO / extra
    if p.exists():
        manifest.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {extra}")
for f in sorted((REPO / "docs").rglob("*.md")):
    manifest.append(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  "
                    f"{f.relative_to(REPO).as_posix()}")

text = "\n".join(manifest) + "\n"
(REPO / "MANIFEST.sha256").write_text(text)
mhash = hashlib.sha256(text.encode()).hexdigest()
print(f"  MANIFEST.sha256: {len(manifest)} entries, hash {mhash[:16]}")


# =========================================================
# 3. UPDATE repro_manifest.json + VERSION
# =========================================================
print("\n" + "=" * 60)
print("Step 3/3: Update repro_manifest.json + VERSION")
print("=" * 60)

repro = json.load(open(REPO / "repro_manifest.json"))
repro["version"] = "2.1.1"
repro["manifest_sha256"] = mhash
repro["sobol_primary_n"] = 2048
repro["sobol_sampler"] = "scipy.stats.qmc.Sobol (Owen-scrambled)"
repro["sobol_n_progression"] = [128, 256, 512, 1024, 2048]
# Accuracy patch (WS-3 Phase 3.7 ack of stale-content findings):
# compute_backend was stale — claimed no SALib dependency, but
# Phase 3.3a-bugfix substituted SALib for primary Sobol computation.
repro["compute_backend"] = (
    "Python 3.11 with numpy/pandas/scipy/networkx; SALib v1.5.2 for "
    "Sobol total-order estimator (Saltelli-design independent A/B sample "
    "matrices; bootstrap percentile CIs)"
)
# Item 15 symmetric application (WS-3 Phase 3.7 + Phase 14 record Item 18):
# Workflow-stage scaffolding fields removed. These describe HOW the
# artefact was produced (which pipeline stage); they do not serve
# downstream users and they do not appear in publication-layer release
# metadata. Investigation confirmed zero consumers across .py/.json/
# .yaml/.md/.ipynb/.sh/.bat/.ps1 and validate_v2_1.py 11 gates.
# Substantive content of stage8_summary is redundantly captured in the
# dedicated descriptive fields above (sobol_primary_n, sobol_sampler,
# sobol_n_progression). Verification-state and content-fingerprint
# fields preserved (replication_verified, replication_zero_abs_diff,
# manifest_sha256, analysis_plan_hash) — these describe what the
# artefact IS, not how it was produced.
for stale_key in ("stage7_complete", "stage7_timestamp",
                  "stage7_figures_regenerated",
                  "stage8_complete", "stage8_summary"):
    repro.pop(stale_key, None)
json.dump(repro, open(REPO / "repro_manifest.json", "w"), indent=2)
(REPO / "VERSION").write_text("2.1.1\n")
print(f"  repro_manifest.json updated (version 2.1.1)")
print(f"  VERSION set to 2.1.1")

# Print the new headline values for use in manuscript / supplement updates
print("\n" + "=" * 60)
print("HEADLINE VALUES FOR MANUSCRIPT UPDATE")
print("=" * 60)
sg = PARAMS.index("safety_gate")
r = sobol["results"][PRIMARY_N]["unsafe_detection_rate"]
print(f"  ST(safety_gate) on detection rate = {r['ST'][sg]:.3f} "
      f"[95% CI {r['ST_ci_lo'][sg]:.3f}, {r['ST_ci_hi'][sg]:.3f}]")
print()
print("  N-progression (ST(safety_gate)):")
for n in sobol["config"]["N_grid"]:
    r = sobol["results"][str(n)]["unsafe_detection_rate"]
    print(f"    N={n:5d}: ST={r['ST'][sg]:.3f} "
          f"[{r['ST_ci_lo'][sg]:.3f}, {r['ST_ci_hi'][sg]:.3f}]")
