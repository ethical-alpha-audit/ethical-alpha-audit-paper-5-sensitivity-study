# SCM Dependency Audit
**Repository:** ethical-alpha-audit-paper-5-sensitivity-study
**Version:** v2.0

## Purpose
This document audits the Structural Causal Model (SCM) implemented in
`src/scm/causal_model.py` and identifies all latent-variable dependencies
across the harm-generation function and the audit observation model. This
audit is the foundation for the Methods §"SCM coupling disclosure" subsection
in the main paper and for Appendix C of the supplementary materials.

## SCM specification (canonical)
Function library: `scm_functions.yaml` (v1.0)

The SCM is a directed acyclic graph with 28 nodes and 19 edges. Latent traits
generate harms and audit signals through the following structural equations.

### Harm-generation pathway
| Equation | Functional form | Inputs | Output |
|---|---|---|---|
| Baseline harm | `sigmoid(intercept + slope * (1 - intrinsic_safety))` with intercept = −3.0, slope = 4.0 | `intrinsic_safety` | `baseline_harm` |
| Subgroup amplification | `base + sensitivity * bias_harm_index` with base = 1.0, sensitivity = 2.0 | `bias_harm_index` | `subgroup_multiplier` |
| Stress failure | Bernoulli(`sigmoid(base_logit + robustness_effect * stress_robustness)`) with base_logit = log(0.05/0.95), robustness_effect = −3.0 | `stress_robustness` | `stress_failure` |
| Realised harm | `baseline_harm * subgroup_multiplier + 0.5 * stress_failure` | three above | `realised_harm` |

### Audit observation pathway
| Equation | Functional form | Inputs | Output |
|---|---|---|---|
| Observed safety | `intrinsic_safety + N(0, sd) - misreporting_scale * gaming_capability` with sd = 0.05, misreporting_scale = 0.15 | `intrinsic_safety`, `gaming_capability` | `observed_intrinsic_safety` |
| Observed evidence | `evidence_strength + N(0, sd_evidence)` (regime-dependent sd) | `evidence_strength` | `observed_evidence_strength` |
| Observed bias | `bias_harm_index + N(0, sd)` | `bias_harm_index` | `observed_bias_harm_index` |
| Observed calibration | `uncertainty_calibration + N(0, sd)` | `uncertainty_calibration` | `observed_uncertainty_calibration` |
| Observed traceability | `traceability_integrity + N(0, sd)` | `traceability_integrity` | `observed_traceability_integrity` |

## Dependency audit: shared latent variables
The following latent variables enter both the harm-generation pathway and the
audit observation pathway:

| Latent variable | Used in harm function? | Used in audit observation? | Coupling |
|---|---|---|---|
| `intrinsic_safety` | Yes (baseline_harm) | Yes (observed_intrinsic_safety, fed to safety_gate) | **SHARED INPUT** |
| `bias_harm_index` | Yes (subgroup_multiplier) | Yes (observed_bias_harm_index, fed to bias_gate) | **SHARED INPUT** |
| `stress_robustness` | Yes (stress_failure) | No | independent |
| `evidence_strength` | No | Yes (evidence_gate) | observation-only |
| `uncertainty_calibration` | No | Yes (calibration_gate) | observation-only |
| `traceability_integrity` | No | Yes (traceability_gate) | observation-only |
| `gaming_capability` | No | Yes (modulates observed_intrinsic_safety) | observation-only |

## Implication for architecture comparison
The architecture comparison reported in the main paper (Table 2 / Architecture
comparison subsection / regime AR2) operates a non-compensatory gate
(`safety_gate`) on `observed_intrinsic_safety`. Because `intrinsic_safety`
also drives `baseline_harm`, the safety gate is a structurally informative
predictor of harm under the SCM as specified.

A weighted-average composite scoring rule that allocates only 30% of weight to
`observed_intrinsic_safety` (and 70% to four other observed quantities, only
one of which — `observed_bias_harm_index` — has any direct linkage to the
harm pathway) operates under a structurally less-favourable signal-to-harm
mapping than the non-compensatory gate.

The architecture-comparison ratio reported in the main paper is therefore
conditional on this coupling. The **decoupled-variant experiment** (Phase 5
of `stage7_orchestrator.py`; output at `outputs/raw/scm_decoupled_comparison.csv`
and `outputs/processed/scm_coupling_sensitivity.json`) provides a sensitivity
quantification by replacing `intrinsic_safety` with an independently-drawn
`harm_latent ~ Beta(2.5, 2.0)` in the baseline_harm function, while leaving
the audit observation model unchanged. The decoupled-variant ratio at the
specified seed is reported in the supplementary materials (Appendix C).

## Acceptance criterion
The architecture-comparison ratio under the coupled SCM and the architecture-
comparison ratio under the decoupled SCM are both honestly reported. Neither
is claimed as architecture-invariant; the difference between them is the
quantitative measure of the coupling's contribution.
