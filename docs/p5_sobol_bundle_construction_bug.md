# P5 Sobol bundle — Saltelli construction bug + fix record

**Status**: BUG CONFIRMED 2026-05-04 during WS-3 Phase 3.3a diagnostic;
fix in progress (SALib substitution per Phase 3.3a-bugfix plan).

**Affected file**: `src/analysis/sensitivity.py` (the v3.0 module
delivered in `Sobol 2048 Upgrade Bundle.zip` as `sensitivity_v3.py`).

**Affected releases**: any v2.1 candidate state produced by
`run_sobol_n_progression.py` BEFORE this fix lands. The pre-fix
v2.1 N=2048 results have invalid Sobol indices and must NOT be
used as the basis for manuscript or supplementary edits, ZIP build,
release, or DOI mint.

**Unaffected**: v2.0 release (DOI 10.5281/zenodo.\<existing\>) is
not affected — its Sobol indices were produced by a pseudo-random
Saltelli sampler that, while small-N noisy, did not have this
construction bug.

---

## What was tested (Phase 3.3a diagnostic Checks 1-7)

Triggered by an unexpected post-pipeline finding: the Sobol N=2048
result attributed `safety_gate` near-zero total-order influence
across all four outcomes (`ST(safety_gate)` ≈ 0.000072 on detection
rate; the runner's 3-decimal `:.3f` display rounded this to "0.000",
making the finding look more dramatic than the underlying values).
The v2.0 manuscript reported `ST(safety_gate) = 0.598, 95% CI
[0.432, 0.692]` — a four-orders-of-magnitude divergence.

Per the experiment-authoritative discipline
(`feedback_experiment_authoritative_manuscript_downstream.md` in
EAA portfolio memory): experiment is authoritative IF correctly
implementing what we think it's implementing. Verification needed.

**Check 1 — Sample matrix variance per parameter column**

Method: Generate the actual Saltelli sample matrix used by
`run_sobol_n_progression.py` at N=2048, compare per-column variance
to the uniform-distribution expectation `(b-a)²/12`.

Result: ALL 7 parameter columns match expected variance exactly.
`safety_gate` column variance ratio (observed / expected) = 1.0000
across [0.20, 0.80]. **Sampling per column is correct.**

**Check 2 — Direct safety_gate sensitivity test**

Method: Hold all other parameters at midpoints; sweep safety_gate
across [0.20, 0.80]; observe each output.

Result: outputs respond strongly to `safety_gate`:
- Detection rate: 0.951 → 1.000 (range 4.96% relative)
- Safe throughput: 0.178 → 0.069 (range **76.78%** relative)
- False-negative harm: 70.16 → 0.00 (range **377.62%** relative)
- Friction: 3.746 → 3.975 (range 5.93% relative)

**Outputs ARE sensitive to `safety_gate` when it is varied alone.**
This contradicts the Sobol pipeline's "near-zero ST" finding.

**Check 2b — Comparative gate sweeps (`calibration_gate`, `evidence_gate`)**

Method: Same baseline; sweep `calibration_gate` over [0.2, 0.7] and
`evidence_gate` over [0.2, 0.8]. Compare relative response magnitudes.

Result: comparable magnitudes:
- `safety_gate` FN harm range: 377.62%
- `calibration_gate` FN harm range: 358.34%
- `evidence_gate` FN harm range: 195.95%

All three gates are similarly binding when varied alone at baseline.
**The Sobol asymmetry (ST(calibration_gate)=0.567 vs
ST(safety_gate)=0.000072 — a 7800× ratio) is not justified by the
direct sensitivity tests.**

**Check 3 — S1 vs ST relationship at N=2048**

Method: Per parameter, verify `ST_j ≥ S1_j` (mathematical Saltelli
constraint).

Result: Three "violations" detected (`safety_gate` FN harm,
`safety_gate` friction, `auditability_noise` friction), all at
noise-floor magnitudes (S1 - ST < 1e-3). These are the documented
small-N artefact mentioned in the runbook supplement edit §6.2(v):
"clipping of S1 ≤ ST is enforced where the standalone estimator
violates the Saltelli mathematical constraint." **Estimator math
is OK at substantive magnitudes; violations are noise-floor only.**

**Check 4 — N-progression trajectory for safety_gate**

Method: Extract `ST(safety_gate)` at each N ∈ {128, 256, 512,
1024, 2048} from `outputs/processed/sobol_convergence.json`.

Result: monotonic decay across all four outcomes:
- Detection: 0.000362 → 0.000434 → 0.000276 → 0.000123 → 0.000072
- Throughput: 0.000112 → 0.000026 → 0.000010 → 0.000004 → 0.000002
- FN harm: 0.000314 → 0.000366 → 0.000176 → 0.000057 → 0.000031
- Friction: 0.000090 → 0.000021 → 0.000006 → 0.000001 → 0.000000

The pattern is "decay to small but non-zero" — superficially
consistent with Walter's Phase 3.3a Possibility A interpretation
(monotonic decay → genuine zero at high N). But the values were
NEVER substantively non-zero (already at 0.000362 at N=128, not
the v2.0 manuscript's 0.598). This is suspicious: if the v2.0
N=64 pseudo-random Saltelli result was 0.598, why does the v2.1
N=128 Owen-scrambled result already say 0.000362? The methodology
upgrade should not flip the result by 4 orders of magnitude — it
should refine an already-substantive estimate.

**Check 5 — Per-gate distribution / pass-rate diagnosis**

Method: Compute pass rate for each gate at low / mid / high
thresholds across its bounds. If `safety_gate` distribution makes
it non-binding (e.g., all systems pass regardless of threshold),
the near-zero ST could be scientifically real.

Result: All 5 gates have wide pass-rate ranges across their
bounds (67-78 percentage points of variation):

| Gate | low pass% | mid pass% | high pass% | range |
|---|---:|---:|---:|---:|
| safety_gate | 95.08 | 65.24 | 20.50 | 74.58 pts |
| evidence_gate | 87.99 | 45.98 | 9.56 | 78.43 pts |
| bias_gate | 25.51 | 80.03 | 98.44 | 72.93 pts |
| calibration_gate | 81.94 | 41.90 | 11.43 | 70.51 pts |
| traceability_gate | 93.20 | 63.18 | 25.45 | 67.75 pts |

**`safety_gate` is just as binding as any other gate.** The
distribution-based explanation for near-zero ST FAILS.

**Check 6 — A vs B correlation per column** (the bug)

Method: Replicate the exact `saltelli_sample()` matrix construction:

```python
sampler = qmc.Sobol(d=7, scramble=True, seed=42)
pts = sampler.random(n=2 * 2048)
A = pts[:2048]
B = pts[2048:]
```

Compute Pearson and Spearman correlation between `A[:, j]` and
`B[:, j]` for each parameter column.

Result:

| param | col | pearson r | flag |
|---|---:|---:|---|
| **safety_gate** | **0** | **0.999998** | **❌ HIGH** |
| evidence_gate | 1 | 0.507332 | ❌ HIGH |
| bias_gate | 2 | -0.601195 | ❌ HIGH |
| calibration_gate | 3 | -0.904411 | ❌ HIGH |
| traceability_gate | 4 | 0.617194 | ❌ HIGH |
| auditability_noise | 5 | -0.600090 | ❌ HIGH |
| unsafe_base_rate | 6 | -0.531135 | ❌ HIGH |

**Column 0 (`safety_gate`) has Pearson r = 0.999998 — A and B are
essentially identical for that column.** All other columns also
have |r| > 0.5, indicating correlations across the board, but col 0
is the most extreme case.

**Check 7 — Direct micro-Sobol test**

Method: Take 10 random sample indices from the actual A matrix.
For each index `i`, compute:
- `y_A[i]` = output at A's parameters
- `y_AB_safety[i]` = output at A's parameters EXCEPT col 0 (safety_gate) from B
- `y_AB_calib[i]` = output at A's parameters EXCEPT col 3 (calibration_gate) from B

Per the Saltelli ST estimator: `ST_j = 0.5 * mean((y_A - y_AB_j)²) / Var(y)`.
If parameter j has high influence, `y_AB_j` should differ from `y_A`.

Result for `false_negative_harm`:

| idx | y_A | y_AB_safety | y_AB_calib | (y_A - y_AB_safety)² | (y_A - y_AB_calib)² |
|---:|---:|---:|---:|---:|---:|
| 1145 | 0.864 | 0.864 | 0.864 | 0.0 | 0.0 |
| 386 | 0.000 | 0.000 | 0.000 | 0.0 | 0.0 |
| 1452 | 14.561 | 14.561 | 4.643 | 0.0 | 98.36 |
| 721 | 0.000 | 0.000 | 0.000 | 0.0 | 0.0 |
| 1477 | 0.000 | 0.000 | 0.000 | 0.0 | 0.0 |
| 1188 | 27.164 | 27.164 | 6.212 | 0.0 | 438.96 |
| 2047 | 0.000 | 0.000 | 0.000 | 0.0 | 0.0 |
| 982 | 0.000 | 0.000 | 0.000 | 0.0 | 0.0 |
| 688 | 1.410 | 1.410 | 1.960 | 0.0 | 0.30 |
| 522 | 0.000 | 0.000 | 0.000 | 0.0 | 0.0 |

Mean `(y_A - y_AB_safety)²` = **0.000000** across all 10 samples.
Mean `(y_A - y_AB_calib)²` = 53.76 across the 10 samples.
Ratio: **5.4 × 10¹³** times more "swap effect" for calibration_gate.

**Smoking gun**: `y_A - y_AB_safety = 0` for ALL 10 samples because
A's safety_gate value equals B's safety_gate value (per Check 6
correlation r = 0.999998). The "swap" doesn't actually change any
input. ST(safety_gate) is artificially zero by construction.

---

## Root cause

`src/analysis/sensitivity.py` `saltelli_sample()` constructs the
Saltelli matrix as:

```python
def saltelli_sample(n_base, d, bounds, seed=42, scramble=True):
    sampler = qmc.Sobol(d=d, scramble=scramble, seed=seed)
    pts = sampler.random(n=2 * n_base)
    A = pts[:n_base]            # first half of single sequence
    B = pts[n_base:]            # second half of SAME sequence
    ...
    for j in range(d):
        AB_j = A.copy()
        AB_j[:, j] = B[:, j]
        samples.append(AB_j)
    return np.vstack(samples)
```

The Saltelli (2010) variance-based estimator design **requires A
and B to be statistically independent**. By drawing both from a
single Owen-scrambled Sobol sequence (positions `[0:N]` and
`[N:2N]`), the implementation introduces deterministic correlations
between A's and B's columns. Owen scrambling preserves the global
low-discrepancy property of the sequence; the per-column structure
of consecutive halves remains highly correlated.

When `AB_j` substitutes column j from B into A, the substituted
value is essentially the same as the value being replaced (for
column 0 specifically: identical to ~5 decimal places). The
estimator term `(y_A - y_AB_j)²` then becomes near-zero for ALL
columns, producing biased-toward-zero ST estimates.

**Even with two independent Sobol generators (different seeds),
SciPy's Owen-scrambled Sobol class produces correlated outputs
across instances** for matched N — verified by direct test:

```python
sampler_A = qmc.Sobol(d=7, scramble=True, seed=42)
sampler_B = qmc.Sobol(d=7, scramble=True, seed=43)
A = sampler_A.random(n=2048); B = sampler_B.random(n=2048)
# Pearson |r| > 0.5 across all 7 columns; some > 0.9
```

The fundamental fix requires using SALib's canonical Saltelli
sampler, which constructs A and B via independent Sobol sequences
with proper randomization that preserves Saltelli's independence
assumption.

---

## Implications

### For the delivered Sobol bundle (`Sobol 2048 Upgrade Bundle.zip`)

The `sensitivity_v3.py` module (a drop-in replacement for `src/analysis/sensitivity.py`)
produces **biased ST estimates for all 7 parameters**. The bias is
most extreme for `safety_gate` (col 0; r = 0.999998 between A-B
columns) but pervasive (all 7 columns have |r| > 0.5).

The companion scripts `run_sobol_n_progression.py`,
`finalise_v2_1.py`, `validate_v2_1.py` are **downstream of and
unaffected by** this bug per se — they correctly drive whatever
sample matrix `saltelli_sample()` produces. They do not need fixing.

### For v2.0 vs v2.1 results

| | v2.0 (released) | v2.1 (pre-fix) |
|---|---|---|
| Sampler | pseudo-random Saltelli | Owen-scrambled Sobol (via custom code) |
| N | 64 base samples | 2048 base samples |
| Estimator math | Saltelli (2010) | Saltelli (2010) |
| Sample-matrix construction | independent A and B | A and B halves of same scrambled sequence — **CORRELATED** |
| ST(safety_gate) on detection | 0.598, 95% CI [0.432, 0.692] | 0.000072, 95% CI [0.000032, 0.000134] |
| Validity | small-N noisy but unbiased | precise but **biased** (toward zero) |

**Noisy unbiased > precise biased.** The v2.0 result, despite its
wide CIs from N=64, is closer to truth than the v2.1 N=2048 result
from the buggy implementation. Were v2.1 to be released as-is, the
manuscript would carry a worse Sobol claim than v2.0.

### For the runbook (`Sobol_2048_Upgrade_Runbook.docx`)

The runbook's §5 manuscript-edit templates assume the new pipeline
produces correct (just more precise) Sobol indices that match the
v2.0 narrative structure. They are **NOT safe to apply** against
the buggy v2.1 outputs. After the fix, the templates may be safely
applied if the corrected results match v2.0's qualitative ranking;
if they don't, the templates need adaptation.

### For the experiment-authoritative discipline

This case is a worked example for an extension of the experiment-
authoritative discipline (`feedback_experiment_authoritative_manuscript_downstream.md`):

> Experiment is authoritative IF correctly implementing what we
> think it's implementing. When experiment outputs are produced by
> LLM-pipeline-delivered code, diagnostic verification against
> canonical implementations is essential before treating outputs
> as authoritative. Bundle-internal validation gates check
> downstream artefacts, not upstream computational correctness.

(See EAA portfolio memory; codification at WS-3 Phase 14.)

### For downstream cleanups built on the buggy pipeline (WS-Release-P5 audit scope)

Downstream cleanups built on the (now-known-buggy) Sobol pipeline
deserve scientific audit at WS-Release-P5 hardening pass. Specifically
the Stage 5 P-W01-W03 forbidden-tokens list (`sweet-spot`,
`_FLAGGED`, `152-fold`). Each token was removed under assumptions
that may have rested on the buggy pipeline's apparent validation.
With the bug found and fixed, the removal rationales deserve re-airing:

- Was `sweet-spot` framing's removal driven by reviewer concerns
  about "post-hoc cherry-picking" that the (buggy) Sobol bundle made
  appear weaker than it actually is?
- What was `_FLAGGED`'s removal rationale? Does it rest on the
  questioned pipeline?
- `152-fold` likewise.

The forbidden-tokens list functions as an **audit list at
WS-Release-P5**, not as a settled list of non-issues. The Phase 3.4
manuscript-editing pass for v2.1 release handles operational
disposition; the WS-Release-P5 audit handles full scientific
re-examination.

---

## Companion finding: v2.0 ZIP also contains corrupted manuscript files (Phase 3.4 Step 0 discovery)

A second LLM-pipeline corruption was discovered at WS-3 Phase 3.4
Step 0 (manuscript reading pre-flight). The v2.0 ZIP
(`Paper5 Reproducibility Artefact FINAL.zip`, sha `01cfc5fb...`)
contains DIFFERENT manuscript and supplement files than the
canonical Desktop standalone versions. The ZIP versions appear to
be products of a stripped/re-rendered pipeline pass that:

- Lost most of the manuscript section structure (no `Methods`,
  `Results`, `Discussion`, `Limitations`, `Conclusions`,
  `Declarations`, `Multimedia Appendices`, or `Figure legends`
  headings as separate sections)
- Lost the proper Sobol N=1024 narrative (the runbook §5
  find-strings reference text that does NOT exist in the ZIP
  manuscript)
- Reduced the supplement to a 7-line skeleton (only Appendix A
  "Reserved" and Appendix B "PhysioNet" present; missing
  Appendices A "Aggregation regime dictionary", B "Comparator
  scope", C "SCM coupling", D "Sobol re-executed", E "NSGA-II
  convergence", F "Per-weighting", G "Reproducibility manifest"
  that the canonical version contains)
- Re-introduced `sweet-spot` framing into the manuscript
  (4-5 occurrences in the ZIP version vs 0 occurrences in the
  canonical Desktop version; the canonical Stage 5 P-W01-W03
  cleanup IS reflected in the standalone)

### Verification data

| File | Canonical Desktop | v2.0 ZIP extract |
|---|---:|---:|
| Manuscript size | 23,248 B | 29,506 B |
| Manuscript SHA-256 | `48a794ef...` | `97eb5bb8...` |
| Manuscript char count | 41,896 | 39,639 |
| Manuscript line count | 159 | 100 |
| Manuscript headings | 42 | 14 |
| Supplement size | 15,457 B | 8,880 B |
| Supplement SHA-256 | `743a8bed...` | `8accdcab...` |
| Supplement char count | 15,229 | 2,074 |
| Supplement line count | 99 | 7 |
| Supplement appendices | A-G (7) | A-B skeleton (2) |
| Manuscript runbook §5 find-strings present | 9/9 ✅ | 0/9 ❌ |
| Supplement runbook §6 find-strings present | 4/4 ✅ | 0/4 ❌ |
| Sweet-spot mentions in manuscript | **0** | 4-5 |
| Sweet-spot mentions in supplement | 0 | 0 |

The standalone Desktop versions ARE the canonical v2.0 baseline
that the runbook's §5 + §6 templates were authored against.

### Recovery action (Phase 3.4 Step 0)

1. The `inputs/paper5_sensitivity_study_manuscript.docx` and `inputs/paper5_sensitivity_study_supplementary.docx`
   in the repo were replaced filesystem-only with the canonical
   Desktop standalone versions per the no-commit-manuscripts
   policy. The replacement preserves the canonical content as the
   Phase 3.4 editing baseline.
2. The legacy-tracked status of those two files (per
   `feedback_derivative_artefact_desync.md` Case B) means they
   show as persistent M; the M is NOT staged or committed by
   this commit (consistent with Walter's standing
   no-commit-manuscripts policy).
3. The WS-6 hygiene workstream is the appropriate venue for
   `git rm --cached` of the legacy-tracked entries, alongside
   the broader portfolio legacy-manuscript-untracking item.

### Sweet-spot Patch 3 disposition (operational vs scientific)

The canonical v2.0 manuscript does NOT include sweet-spot framing.
The Patch 3 disposition is therefore framed as TWO distinct decisions:

**Operational disposition (v2.1 release)**: DROP. The v2.1 release
operates on the canonical v2.0 baseline (post-corruption-correction).
The canonical baseline does not include sweet-spot framing. v2.1
release must be internally consistent with that baseline.

**Scientific disposition (v2.2+ or future releases)**: DEFERRED to
WS-Release-P5 Stage 5 cleanup audit. The substantive scientific
question — is sweet-spot a valid finding from the underlying
experimental work (NSGA-II Pareto frontier characterisation;
joint-threshold region selection)? — is NOT determined by the v2.1
operational disposition. The audit will examine NSGA-II output
analytical legitimacy, MCDA literature, Stage 5 P-W01-W03 removal
rationale, post-bugfix Sobol findings, and editorial history. Audit
outcomes determine future-release disposition (restore on principled
basis; permanent omission; partial restoration with revised framing).

The operational disposition is NOT a scientific determination;
conflating the two would treat the manuscript as authoritative over
the experiment, violating the strengthened experiment-authoritative
rule.

### Connection to the strengthened experiment-authoritative discipline

This second corruption finding strengthens the case for the
LLM-pipeline-correctness extension to
`feedback_experiment_authoritative_manuscript_downstream.md`. The
Sobol bundle bug was an UPSTREAM computational corruption (biased
Sobol indices); the manuscript corruption is a DOWNSTREAM
publication-pipeline corruption (re-rendered manuscript losing
structure + content). Both pass surface-level validation gates
(file existence; manifest consistency); both require diagnostic
verification against canonical reference (SALib for Sobol; Desktop
standalone for manuscript) to detect.

The forward checklist below applies to both upstream and downstream
LLM-pipeline failure modes.

## Forward checklist for similar workstreams

When executing a workstream that:

- Operates on LLM-pipeline-delivered computational bundles
  (Stage 7-8 outputs or analogous)
- Includes downstream cleanups built on prior computational results
- Is preceded by validation work whose correctness rests on
  upstream computation that may not have been independently verified

Apply the strengthened experiment-authoritative discipline:

1. **Diagnostic verification of the upstream computation FIRST.**
   Verify against canonical references where they exist (peer-reviewed
   library implementations preferred over custom code). Run
   failure-mode-specific diagnostics (for Sobol: A vs B correlation;
   per-parameter ST not exactly 0 with CI [0,0] unless genuinely
   zero-variance; comparison against weaker but unbiased prior
   results).

2. **Re-examination of downstream cleanups SECOND.** They may need
   to be re-validated against the corrected upstream — or the
   correction may resolve concerns that drove the cleanups in the
   first place.

3. **Manuscript revision THIRD.** Operating on validated computation
   plus re-examined cleanups produces a defensible final state.

Surface-level validation gates (file-existence checks, manifest
integrity, replication reproducibility) do **NOT** substitute for
upstream computational correctness. A pipeline that passes 11
downstream gates can still produce systematically biased upstream
results (this case).

Specifically applies to:

- **WS-Release-P5** (current paper; Stage 5 cleanup audit)
- **WS-4 P8/P9 formal-computational notebooks** (per v5.1 errata
  Item #26: Proposition 1 verification, worked examples,
  architecture comparison via ELECTRE TRI / Sugeno conjunctive /
  lexicographic / vector-valued, capability/justificatory conditions,
  aggregate welfare simulation). These are Stage 7-8 artefacts; the
  discipline applies.

---

## Fix path (Phase 3.3a-bugfix)

**Step 1**: This memo (DONE).

**Step 2**: Re-author `src/analysis/sensitivity.py` as a thin
wrapper around `SALib.sample.saltelli` and `SALib.analyze.sobol`,
preserving the public API:
- `saltelli_sample(n_base, d, bounds, seed, scramble)` → wraps SALib's `saltelli.sample`
- `sobol_analyze(y_all, n_base, d)` → wraps SALib's `sobol.analyze`
- `bootstrap_indices(y_all, n_base, d, n_resamples, seed)` → bootstrap CIs on top of SALib output (or use SALib's built-in bootstrap)
- `run_sobol_analysis(...)` → orchestration, unchanged
- `format_sensitivity_table(...)` → presentation, unchanged

SALib is already installed in `.venv` (verified at WS-3 Phase 3.3a).

**Step 3**: Micro-test the wrapper:
- `saltelli_sample` produces (N*(2+d), d) shape per Saltelli design
- A vs B columns from the wrapper have near-zero correlation (vs the 0.999998 from the buggy implementation)
- Known-answer test: `f(x) = x[0]` should yield S1[0] ≈ 1.0 and S1[i!=0] ≈ 0
- HALT if any micro-test fails

**Step 4**: Re-run `run_sobol_n_progression.py` on the fixed
implementation. Estimated runtime: ~57 min (similar to buggy run).

**Step 5**: Verify the fix landed:
- A vs B correlations on the fixed sample matrix → near zero
- Sobol indices not pathological (no parameter at exactly ST=0)
- Sanity check: does the fixed v2.1 N=2048 ST(safety_gate) fall
  within v2.0's wide CI [0.432, 0.692]? If yes, strong evidence
  the fix is producing correct results. If no, HALT for further
  investigation.

**Step 6**: Commit this memo + fixed `sensitivity.py` + new
(validated) Sobol outputs to `v2-1-from-v2-0` branch as a single
"WS-3 Phase 3.3a-bugfix" commit.

**Step 7**: Resume original WS-3 plan from Phase 3.5 (Okabe-Ito
patch + `finalise_v2_1.py` + `validate_v2_1.py` + 11 gates).

---

## File status (preserved on disk for diagnostic record)

- `src/analysis/sensitivity.py` — **buggy v3.0** (replaced from
  v2 at Phase 3.3 Section 2.2; will be replaced again at
  Phase 3.3a-bugfix Step 2)
- `outputs/processed/sobol_convergence.json` — **INVALID**
  (biased indices; will be overwritten by re-run at Step 4)
- `outputs/tables/sobol_*.csv` — **INVALID** (will be overwritten)
- `logs/sobol_n_progression.log` — preserved for diagnostic
  reference (will be overwritten at Step 4)
- `.tmp/sobol-bundle/sobol-2048/sensitivity_v3.py` — preserved
  in extracted bundle for forensic reference (the buggy original)

## Cross-references

- `src/analysis/sensitivity_v3_buggy.py` (this repo) — the preserved
  buggy implementation as delivered by the Stage 8 Sobol bundle.
  This is the actual code that produced the construction bug
  described in this memo. It is preserved for forensic comparison
  with the corrected `src/analysis/sensitivity.py` (SALib wrapper).
  The two files together document what was found and how it was
  resolved. **Do not import or execute** `sensitivity_v3_buggy.py`
  — it is documentation only.
- `feedback_experiment_authoritative_manuscript_downstream.md`
  (EAA portfolio memory) — canonical discipline rule; will be
  strengthened at Phase 14 of WS-3 to include the LLM-pipeline
  failure mode and the forward checklist above.
- `project_workstream_architecture_2026-05-03.md` (EAA portfolio
  memory) — architecture memo; WS-Release-P5 scope updated at
  Phase 14 to include Stage 5 cleanup audit.
- `eaa_system/v5_1_errata.md` (EAA portfolio operations) — Item 46
  to be added at Phase 14 capturing this discipline as a runbook
  addendum.

## References

- Saltelli, A., et al. (2010). Variance based sensitivity analysis
  of model output. Design and estimator for the total sensitivity
  index. *Computer Physics Communications*, 181(2), 259-270.
- Iwanaga, T., Usher, W., & Herman, J. (2022). Toward SALib 2.0:
  Advancing the accessibility and interpretability of global
  sensitivity analyses. *Socio-Environmental Systems Modelling*, 4.
- Herman, J., & Usher, W. (2017). SALib: An open-source Python
  library for Sensitivity Analysis. *Journal of Open Source
  Software*, 2(9), 97.
- Owen, A. B. (1995). Randomly permuted (t,m,s)-nets and (t,s)-sequences.
  In *Monte Carlo and Quasi-Monte Carlo Methods in Scientific
  Computing* (pp. 299-317).

## Audit trail

| Date | Event | Authority |
|---|---|---|
| 2026-05-04 ~10:46Z | `run_sobol_n_progression.py` (buggy) completes; safety_gate ST=0.000072 surfaces | Pipeline output |
| 2026-05-04 ~11:00Z | Phase 3.3a diagnostic Checks 1-7 executed | Walter spec |
| 2026-05-04 ~11:30Z | Bug confirmed; root cause identified | Diagnostic verdict |
| 2026-05-04 (this memo) | Phase 3.3a-bugfix Step 1 | Walter ack of Option (i) |
| (pending) | Step 2-7 execution | Walter ack of memo content |

---

## Related finding: validator path-assumption mismatch

During Phase 3.5 of WS-3 (final 11-gate validation), `validate_v2_1.py`
was found to have hardcoded paths assuming the runbook's
`p5_workspace/` layout (.docx files alongside `repo/` subdirectory).
Our portfolio convention places canonical .docx files at
`inputs/paper5_sensitivity_study_manuscript.docx` and `inputs/paper5_sensitivity_study_supplementary.docx` (repo-
internal, persistent-M per no-commit-manuscripts policy).

The path mismatch caused validator to read empty strings for
MS and SUPP content. G-2 and G-6 forbidden-tokens checks passed
vacuously across empty strings rather than checking actual content.

Out-of-band verification confirmed canonical inputs were
forbidden-token-clean. Validator was patched at Phase 3.5 to
add canonical-inputs fallback (3-line addition; commit
message at WS-3 Phase 3.5 validate_v2_1.py path-assumption fix).

This is the same family as the Sobol bundle bug:
LLM-pipeline-delivered scripts can have setup assumptions that
don't match downstream portfolio practice. Per Phase 14 record
item 14 (LLM-pipeline output integrity), the discipline is to
patch the script to match actual setup rather than work around
the mismatch.

Forward applicability: when receiving LLM-pipeline-delivered
validation or processing scripts, verify path assumptions against
the actual repo layout before treating script results as
authoritative.
