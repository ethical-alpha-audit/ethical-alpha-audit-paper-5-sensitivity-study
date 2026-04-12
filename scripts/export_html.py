"""
HTML export for code-free notebook reading.
Mirrors the Paper 1 / Paper 4 pattern: nbconvert to docs/html/ from config/notebook_plan.json.
"""

import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]


def export_all():
    plan_path = BASE_DIR / "config" / "notebook_plan.json"
    with open(plan_path, "r", encoding="utf-8") as f:
        plan = json.load(f)

    html_dir = BASE_DIR / "docs" / "html"
    html_dir.mkdir(parents=True, exist_ok=True)

    for item in plan["execution_order"]:
        nb_path = BASE_DIR / item["path"]
        html_name = nb_path.stem + ".html"
        html_path = html_dir / html_name

        print(f"  Exporting {item['name']} -> docs/html/{html_name}...", end=" ", flush=True)

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "nbconvert",
                "--to",
                "html",
                "--no-input",
                "--output",
                str(html_path),
                str(nb_path),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("OK")
        else:
            print(f"FAIL: {result.stderr[:200]}")
            return False

    return True


if __name__ == "__main__":
    success = export_all()
    sys.exit(0 if success else 1)
