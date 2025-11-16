
# CH06 Lab — Data Governance with a Tiny Data Vault

## Why this lab exists

In the book, CH06 uses a **Data Vault-style model** (hub + satellite)
to reason about data governance: which business keys exist, which
attributes are tracked, and where gaps can appear.

This CH06 lab is a **small, self-contained sandbox** showing how
governance issues surface when transactions reference policies that
are missing or partially modeled in the vault:

- `labs/ch06/inputs/raw/transactions.csv` contains a tiny set of policy transactions.
- `labs/ch06/inputs/vault/hub_policy.csv` lists known policies (the hub).
- `labs/ch06/inputs/vault/sat_policy_details.csv` tracks policy attributes (the satellite).

A Python runner checks for missing hub keys and satellite orphans,
then reports the result as JSON.

---

## Learning Objectives

By the end of this lab, you will be able to:

- Explain how a hub/satellite structure captures business keys and
  attributes.
- Detect governance gaps such as:
  - transactions referencing policies not present in the hub,
  - satellites that have no corresponding hub,
  - hub records without satellites.
- Read a tiny governance report as JSON and interpret its meaning.

This lab runs entirely inside `labs/ch06/` and does **not** modify any
other part of the repository.

---

## Files in This Lab

All paths are relative to the LABS repo root (`data-eng-labs-2025/`).

- **Runner**

  - `labs/ch06/run.py`  
    Entry point for the CH06 Data Vault governance checker.

- **Inputs**

  - `labs/ch06/inputs/raw/transactions.csv`  
    Tiny set of transactions referring to `policy_id`.

  - `labs/ch06/inputs/vault/hub_policy.csv`  
    Hub table with one row per `policy_id`.

  - `labs/ch06/inputs/vault/sat_policy_details.csv`  
    Satellite table with attributes per `policy_id`.

- **Output**

  - `labs/ch06/artifacts/result.json`  
    Governance check result (status, checks, metrics, messages).

---

## What the runner actually does

When you run:

```bash
python labs/ch06/run.py
```

the script will:

1. Read the three CSV files under `labs/ch06/inputs/raw/` and `labs/ch06/inputs/vault/`.

2. Compute:

   * The set of `policy_id` values in transactions, hub, and satellite.
   * Lists of:

     * policies in transactions but missing in hub,
     * satellite policies with no hub (orphans),
     * hub policies with no satellite.

3. Evaluate the following checks:

   * **`checks.all_transactions_have_hub`**
     True when every policy in transactions exists in the hub.

   * **`checks.no_orphan_satellite`**
     True when every satellite row has a matching hub row.

   * **`checks.all_hubs_have_satellite`**
     True when every hub policy appears in the satellite.

4. Compute a final `status`:

   * `"accept"` if all checks are true.
   * `"reject"` otherwise.

5. Write a report to `labs/ch06/artifacts/result.json` with:

   * `chapter`, `status`, `change_id`
   * `checks.*` flags
   * counts of transactions, hub policies, and satellite rows
   * lists of missing/orphan keys
   * human-readable `messages[]`

---

## Step 1 — Run the lab once

From the repository root:

```bash
python labs/ch06/run.py
```

You should see that:

* `labs/ch06/artifacts/result.json` is created or updated.
* The `status` field is `"accept"` for the default inputs.
* All `checks.*` flags are `true`.

Open the result file and read:

* `metrics.counts`
* `metrics.missing_in_hub`, `metrics.orphan_sat`, `metrics.missing_sat`
* the three `checks.*` flags
* `messages[]`

Try to explain, in your own words, **why** this tiny Data Vault is
considered consistent.

---

## Step 2 — Introduce governance gaps and run again

Try one experiment at a time:

1. **Break hub coverage**

   * Add a row to `labs/ch06/inputs/raw/transactions.csv` with a new `policy_id` that
     does not appear in `labs/ch06/inputs/vault/hub_policy.csv`.

   * Run the lab again:

     ```bash
     python labs/ch06/run.py
     ```

   * Observe how `metrics.missing_in_hub` and
     `checks.all_transactions_have_hub` change.

2. **Create orphan satellites**

   * Add a row to `labs/ch06/inputs/vault/sat_policy_details.csv` with a `policy_id`
     that does not exist in `labs/ch06/inputs/vault/hub_policy.csv`.
   * Run the lab again and observe `metrics.orphan_sat` and
     `checks.no_orphan_satellite`.

Each time, compare the new `result.json` with the previous one.
Ask yourself: *“What kind of risk would this represent in a real
governed Data Vault?”*

---

## From this lab to real systems

In real governance setups:

* Hubs and satellites are often spread across many tables and
  schemas, sometimes across environments.
* Periodic checks (like this lab) are used to detect modeling gaps
  and regressions as systems evolve.

This lab is a **miniature** of those governance checks: once you
understand it, you can imagine scaling the same pattern to more
entities, more attributes, and more complex rules.

---

## Advanced — Possible extensions

* Add effective dates and check for temporal gaps in satellites.
* Add reference data (e.g. policy types) and enrich the checks.

