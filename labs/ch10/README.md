# CH10 Lab — Scaling & Optimization with Tiny Warehouses

## Why this lab exists

In the book, CH10 discusses **scaling and optimization**: how
workloads map to compute resources and how to spot obvious capacity
issues.

This CH10 lab is a **small, self-contained sandbox** that uses a tiny
warehouse model:

- `inputs/workloads.json` describes workloads with concurrency and
  assigned warehouses.
- `inputs/warehouses.json` describes warehouses with max concurrency
  limits.
- A Python runner checks whether any warehouse is overcommitted.

There is no real data warehouse in this lab. Everything lives under
`labs/ch10/` and runs locally.

---

## Learning Objectives

By the end of this lab, you will be able to:

- Represent workloads and warehouse capacities in simple JSON files.
- Compute per-warehouse concurrency from workload assignments.
- Detect overcommitted warehouses using a tiny check.
- Relate this to larger capacity planning and optimization problems.

This lab runs entirely inside `labs/ch10/` and does **not** modify any
other part of the repository.

---

## Files in This Lab

All paths are relative to the LABS repo root (`data-eng-labs-2025/`).

- **Runner**

  - `labs/ch10/run.py`  
    Entry point for the CH10 scaling & optimization checker.

- **Inputs**

  - `labs/ch10/inputs/workloads.json`  
    Describes each workload’s average concurrency and assigned
    warehouse.

  - `labs/ch10/inputs/warehouses.json`  
    Defines warehouses with their `max_concurrency` limits.

- **Output**

  - `labs/ch10/artifacts/result.json`  
    Capacity check result (status, checks, metrics, messages).

---

## What the runner actually does

When you run:

```bash
python labs/ch10/run.py
```

the script will:

1. Read `workloads.json` and `warehouses.json` under `inputs/`.
2. Aggregate the total requested concurrency per warehouse based on
   workload assignments.
3. Detect any warehouse where `used_concurrency > max_concurrency`.

4. Evaluate the following checks:

   - **`checks.warehouses_defined`**  
     True when there is at least one warehouse.

   - **`checks.workloads_defined`**  
     True when there is at least one workload.

   - **`checks.no_overcommitted_warehouses`**  
     True when no warehouse is overcommitted.

5. Compute a final `status`:

   - `"accept"` if all checks are true.
   - `"reject"` otherwise.

6. Write a report to `labs/ch10/artifacts/result.json` with:

   - `chapter`, `status`, `change_id`
   - `checks.*` flags
   - per-warehouse capacity and used concurrency
   - human-readable `messages[]`

---

## Step 1 — Run the lab once

From the repository root:

```bash
python labs/ch10/run.py
```

You should see that:

- `labs/ch10/artifacts/result.json` is created or updated.
- The `status` field is `"accept"` for the default inputs.
- All `checks.*` flags are `true`.

Open the result file and read:

- `metrics.warehouse_capacity`
- `metrics.warehouse_used_concurrency`
- `metrics.overcommitted`
- the three `checks.*` flags
- `messages[]`

Try to explain, in your own words, **why** this scaling plan is
considered safe in the tiny lab world.

---

## Step 2 — Overcommit a warehouse and run again

Open:

```text
labs/ch10/inputs/workloads.json
```

and try one experiment at a time:

1. **Increase concurrency on a workload**

   - Double the `concurrency` of one workload assigned to
     `"wh_small"`.
   - Run the lab again:

     ```bash
     python labs/ch10/run.py
     ```

   - Observe how `metrics.overcommitted` and
     `checks.no_overcommitted_warehouses` change.

2. **Reduce warehouse capacity**

   - Lower `max_concurrency` for `"wh_small"` in `warehouses.json`.
   - Run the lab again and see if any warehouse becomes
     overcommitted.

Each time, compare the new `result.json` with the previous one.
Ask yourself: *“How would this show up in real warehouse usage and
cost?”*

---

## From this lab to real systems

In real warehouse platforms:

- Capacity and workload patterns are more complex, but the basic idea
  remains the same: match workloads to resources without oversub
