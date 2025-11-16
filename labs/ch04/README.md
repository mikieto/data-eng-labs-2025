
# CH04 Lab — Tiny Medallion Consistency Check

## Why this lab exists

In the book, CH04 introduces a **tiny Medallion architecture**
(raw → bronze → silver → gold) as a way to reason about data quality,
schema evolution, and survivability of downstream tables.

This CH04 lab is a **small, self-contained sandbox** that lets you
practice those ideas on a single customer table:

- Small CSVs under `inputs/raw/`, `inputs/bronze/`, `inputs/silver/`,
  and `inputs/gold/` show how the same logical entity (customer)
  flows across the layers.
- A Python runner checks row counts, key coverage, and basic column
  evolution across the layers.
- The result is written as JSON under `artifacts/result.json`.

There are no external systems in this lab. Everything lives under
`labs/ch04/` and runs locally.

---

## Learning Objectives

By the end of this lab, you will be able to:

- Explain the role of raw/bronze/silver/gold in a tiny Medallion
  setup.
- Inspect how a single table evolves across layers (columns and
  derived attributes).
- Run a simple consistency check across layers and interpret the
  result JSON.
- Relate these tiny checks to real-world Medallion-style platforms.

This lab runs entirely inside `labs/ch04/` and does **not** modify any
other part of the repository.

---

## Files in This Lab

All paths are relative to the LABS repo root (`data-eng-labs-2025/`).

- **Runner**

  - `labs/ch04/run.py`  
    Entry point for the CH04 Medallion consistency checker.

- **Inputs (tables)**

  - `labs/ch04/inputs/raw/customers.csv`  
    Raw customer table (minimal columns).

  - `labs/ch04/inputs/bronze/customers.csv`  
    Bronze layer with cleaned and slightly enriched customer data.

  - `labs/ch04/inputs/silver/customers.csv`  
    Silver layer with additional attributes (e.g. `is_active`).

  - `labs/ch04/inputs/gold/customers.csv`  
    Gold layer with a tiny dimensional view (e.g. customer segments).

- **Output**

  - `labs/ch04/artifacts/result.json`  
    Consistency check result for the tiny Medallion (status, checks,
    metrics, messages).

---

## What the runner actually does

When you run:

```bash
python labs/ch04/run.py
```

the script will:

1. Read `customers.csv` from `inputs/raw/`, `inputs/bronze/`,
   `inputs/silver/`, and `inputs/gold/`.

2. Compute:

   * Row counts per layer (raw/bronze/silver/gold).
   * The set of `customer_id` values per layer.
   * Simple column sets per layer (number of columns).

3. Evaluate the following checks:

   * **`checks.row_counts_consistent`**
     True when all four layers have the same row count.

   * **`checks.keys_consistent`**
     True when the `customer_id` set is the same across all layers.

   * **`checks.column_evolution_present`**
     True when each layer has at least one column and there is a
     visible evolution in shape between layers.

4. Compute a final `status`:

   * `"accept"` if all checks are true.
   * `"reject"` otherwise.

5. Write a report to `labs/ch04/artifacts/result.json` with:

   * `chapter`, `status`, `change_id`
   * `checks.*` flags
   * `metrics.row_counts` and `metrics.num_columns`
   * human-readable `messages[]`

---

## Step 1 — Run the lab once

From the repository root:

```bash
python labs/ch04/run.py
```

You should see that:

* `labs/ch04/artifacts/result.json` is created or updated.
* The `status` field is `"accept"` for the default inputs.
* All `checks.*` flags are `true`.

Open the result file and read:

* `metrics.row_counts`
* `metrics.num_columns`
* the three `checks.*` flags
* `messages[]`

Try to explain, in your own words, **why** this tiny Medallion is
considered consistent.

---

## Step 2 — Break consistency and run again

Open:

```text
labs/ch04/inputs/raw/customers.csv
```

and try one experiment at a time:

1. **Remove one row in one layer**

   * Delete a customer row from `labs/ch04/inputs/bronze/customers.csv`
     only.

   * Run the lab again:

     ```bash
     python labs/ch04/run.py
     ```

   * Observe how `metrics.row_counts` and `checks.row_counts_consistent`
     change.

2. **Break keys**

   * Change one `customer_id` only in `labs/ch04/inputs/gold/customers.csv`.
   * Run the lab again and observe `checks.keys_consistent` and
     `status`.

Each time, compare the new `result.json` with the previous one.
Ask yourself: *“What kind of risk would this represent in a real
Medallion-style platform?”*

---

## From this lab to real systems

In real data platforms using a Medallion pattern:

* **raw/bronze/silver/gold** usually live across different storage
  locations or even technologies.
* Consistency checks (row counts, keys, schema evolution) are often
  implemented as scheduled jobs or CI checks around ETL.

This lab is a **miniature** of that idea: it focuses on a single
table and a few simple checks, but the pattern scales to many tables
and more complex rules.

---

## Advanced — Possible extensions

* Add more tables (e.g. orders, products) and extend the checker.
* Add stronger schema checks (e.g. column types, allowed values).
* Export summary statistics to a catalog or dashboard.

