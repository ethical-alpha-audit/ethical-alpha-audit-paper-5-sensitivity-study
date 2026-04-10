
import hashlib
import json
from pathlib import Path
from datetime import datetime, UTC

BASE_DIR = Path(__file__).resolve().parents[1]

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def build_manifest():
    config_path = BASE_DIR / "config" / "expected_outputs.json"
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    manifest = {"generated_at": datetime.now(UTC).isoformat(), "files": []}
    for item in config["files"]:
        file_path = BASE_DIR / item["path"]
        if file_path.exists():
            manifest["files"].append({
                "path": item["path"],
                "sha256": sha256_file(file_path),
                "exists": True
            })
        else:
            manifest["files"].append({
                "path": item["path"],
                "sha256": "",
                "exists": False
            })

    out_path = BASE_DIR / "logs" / "actual_manifest.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    return out_path

if __name__ == "__main__":
    path = build_manifest()
    print(f"Manifest written to {path}")
