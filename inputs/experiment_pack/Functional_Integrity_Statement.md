# Functional Integrity Statement

No critical runtime logic was intentionally changed.

The only repository edits in this hardening pass were:

- `README.md` for clearer publication-facing documentation
- `scripts/build_figures.py` docstring wording only

Validation evidence available from this pass:

- `python tests/unit_tests.py` passed
- `python tests/validation_tests.py` passed
- representative module imports succeeded

Files classified as HIGH RISK were preserved or left untouched, except for non-executable wording in the wrapper docstring noted above.

Fresh-environment installation was not fully verified in this container, so this statement is bounded: it is not a proof of correctness or full reproducibility, only a record that no test failures were introduced in the checks that were run.

Dependency pinning remains incomplete, and no scientific or algorithmic comment requiring expert verification was rewritten automatically.
