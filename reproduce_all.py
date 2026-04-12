#!/usr/bin/env python3
"""
Reproducibility Entrypoint — Paper 5: Governance Friction Simulation
====================================================================
One-command pipeline:
  Step 1: Run full simulation (scripts/run_all.py)
  Step 2: Execute presentation notebooks
  Step 3: Generate SHA-256 output manifest
  Step 4: Validate outputs against expected hashes
  Step 5: Export notebooks to HTML (docs/html/) for reviewer-readable static copies
"""

import json
import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def run_step(label, cmd):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, cwd=BASE_DIR, text=True)
    if result.returncode != 0:
        print(f"FAIL: {label}")
        sys.exit(result.returncode)
    print(f"OK: {label}")


def main():
    settings = json.loads(
        (BASE_DIR / "config" / "harness_settings.json").read_text(encoding="utf-8")
    )
    os.environ["PYTHONHASHSEED"] = str(settings["python_hash_seed"])

    print("=" * 60)
    print("  PAPER 5 — GOVERNANCE FRICTION SIMULATION")
    print("  Reproducibility Pipeline")
    print("=" * 60)

    # Step 1: Run full simulation pipeline
    run_step(
        "Step 1/5: Simulation pipeline",
        [sys.executable, "scripts/run_all.py"],
    )

    # Step 2: Execute presentation notebooks (avoid re-running the full simulation in 01_* —
    # Step 1 already produced outputs; see notebooks/01_simulation_pipeline.ipynb)
    os.environ["P5_SKIP_EMBEDDED_SIM"] = "1"
    run_step(
        "Step 2/5: Notebook execution",
        [sys.executable, "scripts/notebook_runner.py"],
    )

    # Step 3: Generate output hash manifest
    run_step(
        "Step 3/5: Manifest generation",
        [sys.executable, "scripts/hash_manifest.py"],
    )

    # Step 4: Validate outputs against expected hashes
    run_step(
        "Step 4/5: Output validation",
        [sys.executable, "scripts/validate_outputs.py"],
    )

    # Step 5: HTML export (parity with other paper repositories)
    run_step(
        "Step 5/5: HTML export",
        [sys.executable, "scripts/export_html.py"],
    )

    print("\n" + "=" * 60)
    print("  ALL STEPS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
