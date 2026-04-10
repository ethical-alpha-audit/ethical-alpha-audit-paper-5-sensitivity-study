
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def validate():
    expected = load_json(BASE_DIR / "config" / "expected_outputs.json")
    actual = load_json(BASE_DIR / "logs" / "actual_manifest.json")

    actual_map = {item["path"]: item for item in actual["files"]}
    failures = []

    for item in expected["files"]:
        path = item["path"]
        required = item.get("required", True)
        expected_hash = item.get("sha256", "")
        actual_item = actual_map.get(path)

        if actual_item is None or not actual_item.get("exists", False):
            if required:
                failures.append(f"Missing required output: {path}")
            continue

        if expected_hash and actual_item["sha256"] != expected_hash:
            failures.append(
                f"Hash mismatch for {path}: expected {expected_hash}, got {actual_item['sha256']}"
            )

    return failures

if __name__ == "__main__":
    failures = validate()
    if failures:
        print("VALIDATION FAILED")
        for failure in failures:
            print(f"- {failure}")
        sys.exit(1)
    print("VALIDATION PASSED")
