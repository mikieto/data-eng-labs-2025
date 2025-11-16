#!/usr/bin/env python
from pathlib import Path
import json

def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def main():
    base_dir = Path(__file__).resolve().parent
    inputs_dir = base_dir / "inputs"
    artifacts_dir = base_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    out_path = artifacts_dir / "result.json"

    workloads_cfg = load_json(inputs_dir / "workloads.json")
    warehouses_cfg = load_json(inputs_dir / "warehouses.json")

    workloads = workloads_cfg.get("workloads", [])
    warehouses = warehouses_cfg.get("warehouses", [])

    wh_cap = {w["id"]: int(w.get("max_concurrency", 0)) for w in warehouses}
    wh_used = {w_id: 0 for w_id in wh_cap.keys()}

    for wl in workloads:
        wh_id = wl.get("assigned_warehouse")
        conc = int(wl.get("concurrency", 0))
        if wh_id in wh_used:
            wh_used[wh_id] += conc

    overcommitted = {
        wh_id: {"used": used, "max": wh_cap.get(wh_id, 0)}
        for wh_id, used in wh_used.items()
        if used > wh_cap.get(wh_id, 0)
    }

    checks = {
        "warehouses_defined": len(warehouses) > 0,
        "workloads_defined": len(workloads) > 0,
        "no_overcommitted_warehouses": len(overcommitted) == 0,
    }

    status = "accept" if all(checks.values()) else "reject"

    messages = [
        "Checked a tiny scaling plan: workloads mapped to warehouses with max concurrency limits."
    ]
    if status == "accept":
        messages.append("No warehouse is overcommitted given current workload concurrency.")
    else:
        if overcommitted:
            messages.append(f"Overcommitted warehouses detected: {overcommitted}")

    result = {
        "chapter": "CH10",
        "status": status,
        "change_id": "baseline",
        "messages": messages,
        "checks": checks,
        "metrics": {
            "warehouse_capacity": wh_cap,
            "warehouse_used_concurrency": wh_used,
            "overcommitted": overcommitted,
        },
    }

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[CH10] Lab completed. status={status} → {out_path.relative_to(base_dir)}")


if __name__ == "__main__":
    main()
