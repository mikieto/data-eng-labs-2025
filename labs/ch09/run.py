#!/usr/bin/env python
from pathlib import Path
import csv
import json

def load_csv(path: Path):
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def main():
    base_dir = Path(__file__).resolve().parent
    onprem_dir = base_dir / "onprem"
    cloud_dir = base_dir / "cloud"
    inputs_dir = base_dir / "inputs"
    artifacts_dir = base_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    out_path = artifacts_dir / "result.json"

    plan = load_json(inputs_dir / "ch09_migration_plan.json")
    tables = plan.get("tables", [])

    missing_onprem = []
    missing_cloud = []

    for t in tables:
        name = t.get("name")
        if not name:
            continue
        onprem_path = onprem_dir / f"{name}.csv"
        cloud_path = cloud_dir / f"{name}.csv"
        if not onprem_path.exists():
            missing_onprem.append(name)
        if t.get("mode") in ("dual_write", "cutover"):
            if not cloud_path.exists():
                missing_cloud.append(name)

    # For simplicity, we check only 'customers' row counts when both exist
    row_mismatch = {}
    for t in tables:
        name = t.get("name")
        if not name:
            continue
        onprem_path = onprem_dir / f"{name}.csv"
        cloud_path = cloud_dir / f"{name}.csv"
        if onprem_path.exists() and cloud_path.exists():
            onprem_rows = load_csv(onprem_path)
            cloud_rows = load_csv(cloud_path)
            if len(onprem_rows) != len(cloud_rows):
                row_mismatch[name] = {
                    "onprem": len(onprem_rows),
                    "cloud": len(cloud_rows),
                }

    checks = {
        "all_plan_tables_exist_onprem": len(missing_onprem) == 0,
        "all_dual_or_cutover_tables_exist_in_cloud": len(missing_cloud) == 0,
        "no_rowcount_mismatch_for_migrated_tables": len(row_mismatch) == 0,
    }

    status = "accept" if all(checks.values()) else "reject"

    messages = [
        "Checked a tiny cloud migration plan for on-prem / cloud coexistence."
    ]
    if status == "accept":
        messages.append("All planned tables exist in both worlds with matching row counts.")
    else:
        if missing_onprem:
            messages.append(f"Plan references tables missing on-prem: {missing_onprem}")
        if missing_cloud:
            messages.append(f"Plan requires tables missing in cloud: {missing_cloud}")
        if row_mismatch:
            messages.append(f"Row-count mismatches detected: {row_mismatch}")

    result = {
        "chapter": "CH09",
        "status": status,
        "change_id": plan.get("plan_id", "baseline"),
        "messages": messages,
        "checks": checks,
        "metrics": {
            "missing_onprem": missing_onprem,
            "missing_cloud": missing_cloud,
            "row_mismatch": row_mismatch,
        },
    }

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[CH09] Lab completed. status={status} → {out_path.relative_to(base_dir)}")


if __name__ == "__main__":
    main()
