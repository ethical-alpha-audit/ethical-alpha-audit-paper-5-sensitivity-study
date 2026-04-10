# Reproducibility Statement

## How to reproduce

From the repository root, with dependencies installed per `requirements.txt`:

```bash
python reproduce_all.py
```

This executes the full 13-phase simulation, runs 4 presentation notebooks, computes SHA-256 hashes of all data output files, and validates them against `config/expected_outputs.json`. A passing result (`ALL STEPS PASSED`) confirms identical reproduction.

Expected execution time: ~5 minutes (271 seconds on the reference platform).

## Determinism guarantees

- `PYTHONHASHSEED=0` enforced by harness at startup
- All RNG uses `numpy.random.RandomState(seed)` with deterministic seed derivation
- Base seed: 42 (from `config/parameters.yaml`)
- Derived seeds: SHA-256 hash of base seed + identifiers (scenario, profile, replicate)
- NSGA-II evolutionary process: fully deterministic under same seed
- Sobol quasi-random sampling: deterministic under same seed
- Bootstrap inference: deterministic under same seed
- Replication protocol: two identical-seed builds → zero absolute difference

## Stochastic policy

**Exact reproduction mode.** All outputs are deterministic given identical code, configuration, and platform. The replication protocol verifies this by running two builds with the same seed and confirming 0.0 absolute difference across all four key metrics.

Cross-platform tolerance: ≤0.01 absolute on key metrics, due to floating-point library variations. Figures may differ at the pixel level across platforms but are validated via input data integrity (SHA-256 on underlying datasets).

## Validation without execution

```bash
python scripts/validate_outputs.py
```

Requires only Python stdlib. Verifies checked-in reference outputs match expected hashes. This confirms the reference outputs were produced by the canonical pipeline without requiring re-execution.

## Three-layer validation

1. **Internal:** 7 automated validity tests (safety monotonicity, bias-harm linkage, etc.)
2. **Replication:** Independent two-build verification with ≤0.01 tolerance
3. **Output integrity:** SHA-256 hash comparison of all data outputs

## Output lineage

- `outputs/` is empty in the repository and populated by fresh execution
- `reference_outputs/` contains pre-baked comparison targets (committed to Git)
- Generated outputs are never committed to Git (excluded by `.gitignore`)
- `config/expected_outputs.json` contains the SHA-256 hashes that fresh outputs must match
