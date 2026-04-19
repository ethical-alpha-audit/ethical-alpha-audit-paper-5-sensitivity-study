"""Claim coverage gate: docs/claim_traceability.md must enumerate VERIFIED / External rows only."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pandas as pd
import yaml

BASE = Path(__file__).resolve().parents[1]


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _parse_claim_rows(text: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for raw in text.splitlines():
        s = raw.strip()
        if not s.startswith("|") or "P5-C" not in s:
            continue
        if s.startswith("| Claim ID |"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 5 or not cells[0].startswith("P5-C"):
            continue
        rows.append((cells[0], cells[-1]))
    return rows


def test_claim_traceability_matrix_complete():
    md = (BASE / "docs" / "claim_traceability.md").read_text(encoding="utf-8")
    parsed = _parse_claim_rows(md)
    assert parsed, "expected at least one P5-C row in claim_traceability.md"
    allowed = {"VERIFIED", "External"}
    bad = [(cid, st) for cid, st in parsed if st not in allowed]
    assert not bad, f"claims must be VERIFIED or External only: {bad}"
    ids = [cid for cid, _ in parsed]
    assert len(ids) == len(set(ids)), f"duplicate claim ids: {ids}"


def test_claim_count_header_matches_table():
    md = (BASE / "docs" / "claim_traceability.md").read_text(encoding="utf-8")
    m = re.search(r"(\d+)\s+claims identified for P5", md)
    assert m, "missing claims count line in claim_traceability.md"
    declared = int(m.group(1))
    parsed = _parse_claim_rows(md)
    assert len(parsed) == declared, f"table has {len(parsed)} rows but header says {declared}"


def test_experiment_pack_manifest_hashes():
    cfg = json.loads((BASE / "config" / "expected_input_bundles.json").read_text(encoding="utf-8"))
    for bundle in cfg["bundles"]:
        root = BASE / bundle["root"]
        manifest_path = BASE / bundle["manifest"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for entry in manifest["files"]:
            rel = entry["path"]
            expected = entry["sha256"]
            fp = root / rel
            assert fp.is_file(), f"missing bundled file {fp}"
            assert _sha256_file(fp) == expected, f"sha256 mismatch for {fp}"


def test_weighting_sensitivity_artefacts_align():
    """P5-C33: README summary matches frozen CSV/JSON harm ratios."""
    readme = (BASE / "inputs" / "experiment_pack" / "README.txt").read_text(encoding="utf-8")
    df = pd.read_csv(BASE / "inputs" / "experiment_pack" / "outputs" / "weighting_comparison.csv")
    assert len(df) == 5
    assert df["harm_ratio"].min() == 50.3
    assert df["harm_ratio"].max() == 249.2
    for _, row in df.iterrows():
        wid = row["weighting_id"]
        r = float(row["harm_ratio"])
        pat = rf"{re.escape(wid)}[^\n]*{r:.1f}"
        assert re.search(pat, readme), f"README missing {wid} ratio near {r}"
    data = json.loads(
        (BASE / "inputs" / "experiment_pack" / "outputs" / "weighting_results.json").read_text(
            encoding="utf-8"
        )
    )
    by_id = {x["weighting_id"]: x["harm_ratio"] for x in data["results"]}
    for _, row in df.iterrows():
        assert by_id[row["weighting_id"]] == row["harm_ratio"]


def test_physionet_scope_binding_present():
    """P5-C34: auditable scope file and synthetic observation code paths exist."""
    scope_path = BASE / "inputs" / "statement_bindings" / "physionet_reference_scope.yaml"
    assert scope_path.is_file()
    doc = yaml.safe_load(scope_path.read_text(encoding="utf-8"))
    assert doc.get("binding_version")
    scope = doc.get("scope") or {}
    assert scope.get("empirical_basis") == "synthetic_scm_pipeline"
    assert (BASE / "config" / "parameters.yaml").is_file()
    assert (BASE / "src" / "generators" / "observation_model.py").is_file()
