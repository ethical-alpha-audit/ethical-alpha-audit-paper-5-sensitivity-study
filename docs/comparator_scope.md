# Comparator Scope Statement
**Repository:** ethical-alpha-audit-paper-5-sensitivity-study
**Version:** v2.0

## Statement
The compensatory comparator implemented in this study is **a single
weighted-average composite scoring rule** with weights 30/20/20/15/15 across
safety, evidence, bias, calibration, and traceability, applied to a single
composite threshold (mean of the first three threshold values from the
threshold profile).

This implementation is one instance within the broader compensatory family of
decision-rule architectures. It is the simplest and most widely-cited form of
compensatory aggregation in multi-criteria decision making.

## What is implemented
- File: `src/policy/governance_engine.py` → class `CompensatoryPolicyEngine`
- Default weights: {safety: 0.30, evidence: 0.20, bias: 0.20, calibration: 0.15, traceability: 0.15}
- Approval rule: `sum(weight_k * observed_signal_k) >= mean(first_three_thresholds)`

## What is NOT implemented (out of scope)
- Constrained MCDA with hard floors (e.g., ELECTRE outranking with veto thresholds)
- Lexicographic ordering rules
- Bayesian expected-utility frameworks with explicit utility functions
- Compensatory rules with non-linear aggregation (e.g., geometric mean,
  Choquet integral, ordered weighted average)
- Compensatory rules with conditional thresholds or context-dependent weights

These alternative compensatory architectures are out of scope of the present
study. Comparison against any of them is part of continued methodological
development of the framework. Until those comparisons are run, no claim in
the present paper generalises beyond the weighted-average composite
implementation.

## Weighting-scheme sensitivity (within the implemented comparator)
Sensitivity of the architecture-comparison ratio to the choice of weights
within the weighted-average composite class is reported in
`outputs/processed/weighting_scheme_results.csv`. Five weighting configurations
were evaluated: baseline (30/20/20/15/15), safety-heavy (50/15/15/10/10),
safety-minimal (10/25/25/20/20), uniform (20/20/20/20/20), and evidence-heavy
(20/40/15/15/10).

## Forbidden generalisation
The architecture-comparison ratio reported in the main paper must not be cited
as evidence of "non-compensatory advantage over compensatory architectures"
in general. The only supported claim is "non-compensatory advantage over the
weighted-average composite at the implemented weights".
