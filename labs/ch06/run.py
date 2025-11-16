#!/usr/bin/env python
from pathlib import Path
import csv
import json

def load_csv(path: Path):
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def main():
    base_dir = Path(__file__).resolve().parent
    inputs_dir = base_dir / "inputs"

    raw_path = inputs_dir / "raw" / "transactions.csv"
    hub_path = inputs_dir / "vault" / "hub_policy.csv"
    sat_path = inputs_dir / "vault" / "sat_policy_details.csv"
    artifacts_dir = base_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    out_path = artifacts_dir / "result.json"

    txns = load_csv(raw_path)
    hubs = load_csv(hub_path)
    sats = load_csv(sat_path)

    policy_ids_txn = {r["policy_id"] for r in txns}
    policy_ids_hub = {r["policy_id"] for r in hubs}
    policy_ids_sat = {r["policy_id"] for r in sats}

    missing_in_hub = sorted(policy_ids_txn - policy_ids_hub)
    orphan_sat = sorted(policy_ids_sat - policy_ids_hub)
    missing_sat = sorted(policy_ids_hub - policy_ids_sat)

    checks = {
        "all_transactions_have_hub": len(missing_in_hub) == 0,
        "no_orphan_satellite": len(orphan_sat) == 0,
        "all_hubs_have_satellite": len(missing_sat) == 0,
    }

    status = "accept" if all(checks.values()) else "reject"

    messages = [
        "Checked Data Vault governance for policy hub/satellite against transactions."
    ]
    if status == "accept":
        messages.append("All transaction policies are present in the hub, and all hubs have matching satellites.")
    else:
        if missing_in_hub:
            messages.append(f"Policies in transactions missing in hub: {missing_in_hub}")
        if orphan_sat:
            messages.append(f"Orphan satellite rows (no hub): {orphan_sat}")
        if missing_sat:
            messages.append(f"Hub policies without satellite: {missing_sat}")

    result = {
        "chapter": "CH06",
        "status": status,
        "change_id": "baseline",
        "messages": messages,
        "checks": checks,
        "metrics": {
            "counts": {
                "transactions": len(txns),
                "hub_policies": len(hubs),
                "sat_policies": len(sats),
            },
            "missing_in_hub": missing_in_hub,
            "orphan_sat": orphan_sat,
            "missing_sat": missing_sat,
        },
    }

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[CH06] Lab completed. status={status} → {out_path.relative_to(base_dir)}")


if __name__ == "__main__":
    main()
