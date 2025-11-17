# CH08 Lab — DevOps & Collaboration on a Tiny CI/CD Pipeline

## Why this lab exists

In this lab, `labs/ch08/run.py` is a **gate** that checks a tiny CI/CD pipeline for guards and owner teams on every stage.

In the book, CH08 focuses on **DevOps & collaboration**: how a small
CI/CD pipeline encodes guards and ownership, and how that affects
reliability and accountability.

This CH08 lab is a **small, self-contained sandbox** that lets you
practice reading and checking a tiny pipeline definition:

- `inputs/pipeline.json` defines a few stages, their guards, and
  owner teams.
- A Python runner checks whether every stage has at least one guard
  and an owner.
- The result is written as JSON under `artifacts/result.json`.

There are no real CI/CD tools in this lab. Everything lives under
`labs/ch08/` and runs locally.

> **Fusion-Mart perspective.** In the Fusion-Mart case study, this tiny CI/CD pipeline stands in for the deployment path of Fusion-Mart’s data and ML workloads, and this lab is the gate that ensures every stage has guards and clear ownership before real releases can flow through it.

---

## Learning Objectives

By the end of this lab, you will be able to:

- Read a tiny CI/CD pipeline definition as JSON.
- Explain why each stage should have:
  - at least one guard (e.g. tests, lint, approvals),
  - a clear owner team.
- Run a simple pipeline governance check and interpret the result.

This lab runs entirely inside `labs/ch08/` and does **not** modify any
other part of the repository.

---

## Files in This Lab

All paths are relative to the LABS repo root (`data-eng-labs-2025/`).

- **Runner**

  - `labs/ch08/run.py`  
    Entry point for the CH08 DevOps & collaboration checker.

- **Inputs**

  - `labs/ch08/inputs/pipeline.json`  
    Defines a small pipeline with stages, guards, and owner teams.

- **Output**

  - `labs/ch08/artifacts/result.json`  
    Governance check result (status, checks, metrics, messages).

---

## What the runner actually does

When you run:

```bash
python labs/ch08/run.py
```

the script will:

1. Read `labs/ch08/inputs/pipeline.json`.

2. Compute:

   - The number of stages.
   - How many guards each stage has.
   - Which owner team is responsible for each stage.

3. Evaluate the following checks:

   - **`checks.has_stages`**  
     True when there is at least one stage.

   - **`checks.all_stages_have_guard`**  
     True when every stage has at least one guard.

   - **`checks.all_stages_have_owner`**  
     True when every stage has an `owner_team`.

4. Compute a final `status`:

   - `"accept"` if all checks are true.
   - `"reject"` otherwise.

5. Write a report to `labs/ch08/artifacts/result.json` with:

   - `chapter`, `status`, `change_id`
   - `checks.*` flags
   - per-stage guard counts and owners
   - human-readable `messages[]`

---

## Step 1 — Run the lab once

From the repository root:

```bash
python labs/ch08/run.py
```

You should see that:

- `labs/ch08/artifacts/result.json` is created or updated.
- The `status` field is `"accept"` for the default inputs.
- All `checks.*` flags are `true`.

Open the result file and read:

- `metrics.stage_count`
- `metrics.guards_per_stage`
- `metrics.owner_teams`
- the three `checks.*` flags
- `messages[]`

Try to explain, in your own words, **why** this pipeline passes the
basic governance checks.

---

## Step 2 — Break coverage and run again

Open:

```text
labs/ch08/inputs/pipeline.json
```

and try one experiment at a time:

1. **Remove guards from a stage**

   - Set `"guards": []` for one stage.
   - Run the lab again:

     ```bash
     python labs/ch08/run.py
     ```

   - Observe how `metrics.missing_guards` and
     `checks.all_stages_have_guard` change.

2. **Remove owner from a stage**

   - Remove the `owner_team` field for one stage.
   - Run the lab again and observe `metrics.missing_owners` and
     `checks.all_stages_have_owner`.

Each time, compare the new `result.json` with the previous one.
Ask yourself: *“Who would be paged / responsible if this stage fails
in a real CI/CD setup?”*

---

## From this lab to real systems

In real DevOps setups:

- Pipelines are defined in YAML/JSON (or UI) and version-controlled.
- Guards and owners determine how failures are caught and who
  responds.
- Simple checks like this lab’s can be run in CI to prevent “orphan
  stages” without guards or owners.

This lab is a **miniature** of that governance pattern: you can scale
it up by adding more metadata per stage and stricter rules.

---

## Advanced — Possible extensions

- Add guard types (tests, security, performance) and require certain
  combinations per environment.
- Enforce that some stages must be owned by specific teams.
