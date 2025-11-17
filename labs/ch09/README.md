# CH09 Lab — Cloud Migration & Coexistence

## Why this lab exists

In this lab, `labs/ch09/run.py` is a **gate** that validates a tiny migration plan by checking table presence and row counts on-prem and in the cloud.

In the book, CH09 covers **cloud migration and coexistence**: how to
move tables from on-prem to cloud while keeping systems safe during
dual-running or cutover.

This CH09 lab is a **small, self-contained sandbox** that focuses on
a single table (`customers`) and a tiny migration plan:

- `onprem/**` holds the on-prem copy of the table.
- `cloud/**` holds the cloud copy.
- `inputs/ch09_migration_plan.json` describes how each table should
  be migrated (e.g. dual-write or cutover).

A Python runner checks for missing tables and simple row-count
mismatches, then reports the result as JSON.

> **Fusion-Mart perspective.** For Fusion-Mart, this lab represents a migration gate for moving core tables like `customers` from on-prem to cloud, checking table presence and row counts on both sides before any real cutover is allowed.

---

## Learning Objectives

By the end of this lab, you will be able to:

- Read a tiny migration plan describing which tables move and how.
- Check whether all planned tables exist in both on-prem and cloud
  locations.
- Detect simple data mismatches (row counts) between the two worlds.
- Relate this tiny example to larger migration and coexistence plans.

This lab runs entirely inside `labs/ch09/` and does **not** modify any
other part of the repository.

---

## Files in This Lab

All paths are relative to the LABS repo root (`data-eng-labs-2025/`).

- **Runner**

  - `labs/ch09/run.py`  
    Entry point for the CH09 cloud migration checker.

- **Inputs**

  - `labs/ch09/onprem/customers.csv`  
    On-prem customers table.

  - `labs/ch09/cloud/customers.csv`  
    Cloud customers table (target of migration).

  - `labs/ch09/inputs/ch09_migration_plan.json`  
    Migration plan describing tables and modes (e.g. `"dual_write"`
    or `"cutover"`).

- **Output**

  - `labs/ch09/artifacts/result.json`  
    Migration check result (status, checks, metrics, messages).

---

## What the runner actually does

When you run:

```bash
python labs/ch09/run.py
```

the script will:

1. Read `ch09_migration_plan.json` under `inputs/`.
2. For each table in the plan:
   - verify that the on-prem CSV exists,
   - if mode is `dual_write` or `cutover`, verify that the cloud CSV
     exists.
3. For tables present in both on-prem and cloud:
   - compare row counts and record any mismatches.

4. Evaluate the following checks:

   - **`checks.all_plan_tables_exist_onprem`**  
     True when every table in the plan exists in `onprem/**`.

   - **`checks.all_dual_or_cutover_tables_exist_in_cloud`**  
     True when every table that should run in cloud also exists in
     `cloud/**`.

   - **`checks.no_rowcount_mismatch_for_migrated_tables`**  
     True when all tables present in both worlds have matching row
     counts.

5. Compute a final `status`:

   - `"accept"` if all checks are true.
   - `"reject"` otherwise.

6. Write a report to `labs/ch09/artifacts/result.json` with:

   - `chapter`, `status`, `change_id`
   - `checks.*` flags
   - lists of missing tables and row-count mismatches
   - human-readable `messages[]`

---

## Step 1 — Run the lab once

From the repository root:

```bash
python labs/ch09/run.py
```

You should see that:

- `labs/ch09/artifacts/result.json` is created or updated.
- The `status` field is `"accept"` for the default inputs.
- All `checks.*` flags are `true`.

Open the result file and read:

- `metrics.missing_onprem`
- `metrics.missing_cloud`
- `metrics.row_mismatch`
- the three `checks.*` flags
- `messages[]`

Try to explain, in your own words, **why** this migration plan is
considered safe in the tiny lab world.

---

## Step 2 — Introduce migration issues and run again

Try one experiment at a time:

1. **Remove the cloud table**

   - Delete `cloud/customers.csv`.
   - Run the lab again and observe
     `checks.all_dual_or_cutover_tables_exist_in_cloud` and
     `metrics.missing_cloud`.

2. **Break row-count consistency**

   - Add or remove a row only in `cloud/customers.csv`.
   - Run the lab again and observe
     `checks.no_rowcount_mismatch_for_migrated_tables` and
     `metrics.row_mismatch`.

Each time, compare the new `result.json` with the previous one.
Ask yourself: *“What kind of incident would this represent in a real
coexistence setup?”*

---

## From this lab to real systems

In real migrations:

- Plans are often written as spreadsheets, YAML/JSON, or tickets.
- Simple automated checks (like this lab) can run before cutover
  to detect missing tables or basic mismatches.

This lab is a **miniature** of those checks: you can extend it to
more tables, more metadata, and stricter rules.

---

## Advanced — Possible extensions

- Add more tables (orders, invoices) and extend the migration plan.
- Add checksum or hash comparisons instead of only row counts.
