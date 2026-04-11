# Dependency Reproducibility Assessment

## Summary

Dependency reproducibility is partially specified but not fully pinned.

## Files reviewed

- `requirements.txt`
- `environment.yml`
- `Dockerfile`

## Assessment

- `requirements.txt` uses lower-bound specifiers and floating upper ranges.
- `environment.yml` specifies Python 3.11 but still leaves most package versions open above a minimum bound.
- No lock file, frozen export, or tested fully pinned environment file is present in the repository.

## Reproducibility consequence

A future clean install may resolve different dependency versions from those used to generate the included outputs.

## Recommended remediation path

1. Create a tested lock artefact such as a fully pinned `requirements-lock.txt`, `conda-lock.yml`, or equivalent.
2. Regenerate core outputs in that locked environment.
3. Record the exact environment hash or package list in the reproducibility manifest.
4. Keep the current human-readable dependency files if desired, but pair them with a release lock.

## Fresh-environment validation result

Not fully verified in this hardening pass.
