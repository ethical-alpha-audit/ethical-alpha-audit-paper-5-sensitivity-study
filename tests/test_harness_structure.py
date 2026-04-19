"""Structural tests for the Paper 5 reproducibility repository."""
from pathlib import Path
import json


BASE = Path(__file__).resolve().parents[1]


def test_harness_files_exist():
    required = [
        BASE / "reproduce_all.py",
        BASE / "config" / "notebook_plan.json",
        BASE / "config" / "expected_outputs.json",
        BASE / "config" / "expected_input_bundles.json",
        BASE / "config" / "harness_settings.json",
        BASE / "config" / "trace_map.json",
    ]
    for path in required:
        assert path.exists(), f"Missing required harness file: {path}"


def test_scripts_exist():
    scripts = [
        BASE / "scripts" / "run_all.py",
        BASE / "scripts" / "notebook_runner.py",
        BASE / "scripts" / "hash_manifest.py",
        BASE / "scripts" / "validate_outputs.py",
        BASE / "scripts" / "export_html.py",
    ]
    for path in scripts:
        assert path.exists(), f"Missing required script: {path}"


def test_src_modules_exist():
    modules = [
        "generators/system_generator.py", "generators/observation_model.py",
        "scm/causal_model.py", "policy/governance_engine.py",
        "metrics/friction_model.py", "analysis/sensitivity.py",
        "analysis/inference.py", "analysis/lifecycle.py",
        "analysis/dca.py", "analysis/extreme_risk.py",
        "optimisation/nsga2_search.py", "plotting/figures.py",
        "validation/validation_suite.py", "replication/replication.py",
        "preregistration/plan.py", "utils/helpers.py",
    ]
    for mod in modules:
        path = BASE / "src" / mod
        assert path.exists(), f"Missing src module: {path}"


def test_config_files_exist():
    configs = [
        BASE / "config" / "parameters.yaml",
        BASE / "config" / "scm_graph.dot",
        BASE / "config" / "scenarios" / "scenarios.yaml",
        BASE / "thresholds" / "threshold_profiles.yaml",
        BASE / "analysis_plan.yaml",
        BASE / "scm_functions.yaml",
        BASE / "decision_curve_weights.yaml",
    ]
    for path in configs:
        assert path.exists(), f"Missing config file: {path}"


def test_notebooks_exist():
    nbs = [
        "01_simulation_pipeline.ipynb",
        "02_results_and_tables.ipynb",
        "03_figures.ipynb",
        "04_sensitivity_and_inference.ipynb",
    ]
    for nb in nbs:
        path = BASE / "notebooks" / nb
        assert path.exists(), f"Missing notebook: {path}"


def test_reference_outputs_exist():
    refs = list((BASE / "reference_outputs").rglob("*"))
    data_files = [f for f in refs if f.is_file()]
    assert len(data_files) == 11, f"Expected 11 reference outputs, found {len(data_files)}"


def test_canonical_n_systems():
    import yaml
    params = yaml.safe_load((BASE / "config" / "parameters.yaml").read_text())
    assert params["simulation"]["n_systems"] == 10000, \
        f"n_systems must be 10000, got {params['simulation']['n_systems']}"


def test_notebook_html_exports_exist():
    """Static HTML exports for reviewer-readable notebooks (parity with other paper repos)."""
    html_dir = BASE / "docs" / "html"
    assert html_dir.is_dir(), "Missing docs/html/"
    expected = [
        "01_simulation_pipeline.html",
        "02_results_and_tables.html",
        "03_figures.html",
        "04_sensitivity_and_inference.html",
    ]
    for name in expected:
        path = html_dir / name
        assert path.is_file(), f"Missing HTML export: {path}"


def test_notebook_plan_valid():
    plan = json.loads((BASE / "config" / "notebook_plan.json").read_text())
    assert len(plan["execution_order"]) == 4
    names = [item["name"] for item in plan["execution_order"]]
    assert names[0].startswith("01_")
    assert names[-1].startswith("04_")


if __name__ == "__main__":
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for t in tests:
        try:
            t()
            print(f"PASS: {t.__name__}")
        except AssertionError as e:
            print(f"FAIL: {t.__name__}: {e}")
        except Exception as e:
            print(f"ERROR: {t.__name__}: {e}")
