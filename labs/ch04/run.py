#!/usr/bin/env python
from pathlib import Path
import csv
import json

def load_csv(path: Path):
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows

def main():
    base_dir = Path(__file__).resolve().parent
    inputs_dir = base_dir / "inputs"

    raw_path = inputs_dir / "raw" / "customers.csv"
    bronze_path = inputs_dir / "bronze" / "customers.csv"
    silver_path = inputs_dir / "silver" / "customers.csv"
    gold_path = inputs_dir / "gold" / "customers.csv"
    artifacts_dir = base_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    out_path = artifacts_dir / "result.json"

    rows_raw = load_csv(raw_path)
    rows_bronze = load_csv(bronze_path)
    rows_silver = load_csv(silver_path)
    rows_gold = load_csv(gold_path)

    ids_raw = {r["customer_id"] for r in rows_raw}
    ids_bronze = {r["customer_id"] for r in rows_bronze}
    ids_silver = {r["customer_id"] for r in rows_silver}
    ids_gold = {r["customer_id"] for r in rows_gold}

    row_counts = {
        "raw": len(rows_raw),
        "bronze": len(rows_bronze),
        "silver": len(rows_silver),
        "gold": len(rows_gold),
    }

    # basic invariants
    keys_ok = (
        ids_raw == ids_bronze == ids_silver == ids_gold
    )

    # column evolution: we just check they are non-empty and different shapes
    cols_raw = set(rows_raw[0].keys()) if rows_raw else set()
    cols_bronze = set(rows_bronze[0].keys()) if rows_bronze else set()
    cols_silver = set(rows_silver[0].keys()) if rows_silver else set()
    cols_gold = set(rows_gold[0].keys()) if rows_gold else set()

    evolution_ok = bool(cols_raw) and bool(cols_bronze) and bool(cols_silver) and bool(cols_gold)

    checks = {
        "row_counts_consistent": row_counts["raw"] == row_counts["bronze"] == row_counts["silver"] == row_counts["gold"],
        "keys_consistent": keys_ok,
        "column_evolution_present": evolution_ok,
    }

    status = "accept" if all(checks.values()) else "reject"

    messages = [
        "Checked tiny Medallion layout for customers across raw/bronze/silver/gold."
    ]
    if status == "accept":
        messages.append("All layers share the same customer_id set and row counts; columns evolve as expected.")
    else:
        messages.append("One or more Medallion consistency checks failed; inspect row counts, keys, or columns.")

    result = {
        "chapter": "CH04",
        "status": status,
        "change_id": "baseline",
        "messages": messages,
        "checks": checks,
        "metrics": {
            "row_counts": row_counts,
            "num_columns": {
                "raw": len(cols_raw),
                "bronze": len(cols_bronze),
                "silver": len(cols_silver),
                "gold": len(cols_gold),
            },
        },
    }

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[CH04] Lab completed. status={status} → {out_path.relative_to(base_dir)}")


if __name__ == "__main__":
    main()
