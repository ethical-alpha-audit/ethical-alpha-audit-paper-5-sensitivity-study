
import json
import os
import time
from pathlib import Path
import nbformat
from nbclient import NotebookClient

BASE_DIR = Path(__file__).resolve().parents[1]

def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def clear_notebook_outputs(nb):
    for cell in nb.cells:
        if cell.get("cell_type") == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
    return nb

def run_notebook(notebook_path: Path, timeout: int, clear_outputs: bool = True):
    if not notebook_path.exists():
        return {"status": "error", "message": f"Notebook missing: {notebook_path}"}

    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    if clear_outputs:
        nb = clear_notebook_outputs(nb)

    os.environ["PYTHONHASHSEED"] = "0"

    client = NotebookClient(
        nb,
        timeout=timeout,
        kernel_name="python3",
        resources={"metadata": {"path": str(BASE_DIR)}}
    )

    start = time.time()
    try:
        executed = client.execute()
        duration = round(time.time() - start, 3)
        with open(notebook_path, "w", encoding="utf-8") as f:
            nbformat.write(executed, f)
        return {"status": "ok", "message": f"Executed {notebook_path.name}", "duration_seconds": duration}
    except Exception as exc:
        duration = round(time.time() - start, 3)
        return {"status": "error", "message": str(exc), "duration_seconds": duration}

def execute_all():
    settings = load_json(BASE_DIR / "config" / "harness_settings.json")
    plan = load_json(BASE_DIR / "config" / "notebook_plan.json")
    results = []

    timeout = int(settings["execution_timeout_seconds"])
    clear_outputs = bool(settings["clear_outputs_before_run"])

    for item in plan["execution_order"]:
        path = BASE_DIR / item["path"]
        result = run_notebook(path, timeout=timeout, clear_outputs=clear_outputs)
        result["notebook"] = item["path"]
        results.append(result)
        if settings["fail_fast"] and result["status"] != "ok":
            break

    return results

if __name__ == "__main__":
    for result in execute_all():
        print(result)
