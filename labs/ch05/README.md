# CH05 Lab — Mini Single Change Highway

## Why this lab exists

In real data platforms, a change does not go straight from
"someone edited a file" to "production is updated".

Instead, changes travel through a **Single Change Highway**:
a fixed sequence of stages such as:

1. `validate` — check that the change is well-formed.
2. `dry_run` — simulate the change without touching production.
3. `gate` — decide whether the change is allowed to proceed.
4. `apply` — execute the change against production systems.
5. `export` — publish results and update downstream systems.
6. `rb30_verify` — confirm that you can still roll back within 30 minutes.

This lab gives you a tiny, fully deterministic playground version of
that highway. You will:

- Read a small pipeline configuration (`pipeline.yml`) that lists the stages.
- Run a Python script that checks if the pipeline is safe and complete.
- Edit the pipeline and immediately see which safety rails break.

The goal is **intuition**, not performance.

- In a real project, each stage would run tools such as dbt, Terraform,
  or Snowflake commands.
- In this lab, the runner only **evaluates the stage list** and writes a
  JSON report. It never touches any external system.

---

## Learning Objectives

By the end of this lab, you will be able to:

- Explain the idea of a Single Change Highway for data platform changes.
- Read a tiny pipeline configuration that encodes the
  `validate → dry_run → gate → apply → export → rb30_verify` flow.
- See how changing the pipeline configuration affects whether the
  mini-highway is accepted or rejected.

This lab runs entirely inside `labs/ch05/` and does **not** modify any other
part of the repository.

---

## Prerequisites

- The root README explains how to open this repo in **VS Code + devcontainer**
  or **GitHub Codespaces**. Please complete that setup first.
- Make sure you can run:

  ```bash
  python --version
  ```

  inside the devcontainer or Codespaces terminal.

---

## Files in This Lab

- `labs/ch05/run.py` — the lab runner (entry point).
- `labs/ch05/inputs/pipeline.yml` — tiny pipeline configuration.
- `labs/ch05/artifacts/result.json` — result JSON created by the runner.

You do **not** need to install any extra libraries. The runner uses only
the Python standard library.

---

## What the runner actually does

When you run:

```bash
python labs/ch05/run.py
```

the script will:

1. Read `labs/ch05/inputs/pipeline.yml`.
2. Parse three things:
   - `name`
   - `description`
   - `stages` (a list of stage names)
3. Compare the `stages` list to the canonical highway:

   ```text
   validate → dry_run → gate → apply → export → rb30_verify
   ```

4. Compute:

   - Are all required stages present?
   - Are there any unknown stages?
   - Do the canonical stages appear in the correct order?
   - Is `rb30_verify` present at the end of the pipeline?

5. Write a report to `labs/ch05/artifacts/result.json` with:

   - `metrics.stage_count`, `metrics.unknown_stages`, `metrics.missing_stages`
   - `checks.order_ok`, `checks.required_stages_ok`, `checks.rb30_ok`
   - `status` (`"accept"` or `"reject"`)
   - human-readable `messages[]`

The script does **not** run any external commands. It only evaluates the
configuration and writes a deterministic JSON result.

---

## Step 1 — Run the lab once

From the repository root:

```bash
python labs/ch05/run.py
```

You should see that:

- `labs/ch05/artifacts/result.json` is created or updated.
- The `status` field is `"accept"` for the default pipeline configuration.

Open the result file and read:

- `metrics.stage_count`, `metrics.unknown_stages`, `metrics.missing_stages`
- `checks.order_ok`, `checks.required_stages_ok`, and `checks.rb30_ok`
- `messages[]`

Try to explain, in your own words, why the pipeline is accepted.

---

## Step 2 — Change the pipeline and run again

Now open:

```text
labs/ch05/inputs/pipeline.yml
```

The default content is:

```yaml
name: ch05_mini_highway
description: "Tiny Single Change Highway for CH05 lab."
stages:
  - validate
  - dry_run
  - gate
  - apply
  - export
  - rb30_verify
```

Try one experiment at a time:

1. **Break the order**

   - Swap two stages, for example:

     ```yaml
     stages:
       - validate
       - gate
       - dry_run
       - apply
       - export
       - rb30_verify
     ```

   - Save the file, then run:

     ```bash
     python labs/ch05/run.py
     ```

   - Observe how `checks.order_ok` and `status` change.

2. **Remove a stage**

   - Remove `dry_run` or `export` from the list of stages.
   - Run the lab again and see how `checks.required_stages_ok` and
     `metrics.missing_stages` change.

3. **Break RB-30**

   - Remove `rb30_verify` from the end of the pipeline, or move it to
     the middle.
   - Run the lab again and confirm that `checks.rb30_ok` is now `false`.

4. **Add an unknown stage**

   - Add a non-canonical stage, for example:

     ```yaml
     stages:
       - validate
       - dry_run
       - custom_step
       - gate
       - apply
       - export
       - rb30_verify
     ```

   - Run the lab and see how `metrics.unknown_stages` and `status` change.

Each time, compare the new `result.json` with the previous result and
ask yourself: *“What kind of bug would this represent in a real system?”*

---

## Step 3 — From this lab to real systems

In a real platform, a Single Change Highway might be implemented using:

- CI/CD workflows (for example, GitHub Actions or GitLab CI),
- an orchestrator (for example, Airflow, Argo, or Prefect),
- or a custom Python service.

Each stage would typically:

- `validate`:
  - run code style checks,
  - run unit tests or data quality checks,
  - check configuration syntax.
- `dry_run`:
  - run `terraform plan`,
  - run `dbt build` in a non-production target,
  - simulate changes against a clone or time-travel snapshot.
- `gate`:
  - evaluate policy rules,
  - check approvals,
  - enforce limits on scope and risk.
- `apply`:
  - run DDL statements,
  - apply dbt models to production,
  - apply Terraform changes.
- `export`:
  - refresh data marts or dashboards,
  - notify downstream systems,
  - update metrics or catalogs.
- `rb30_verify`:
  - confirm that there is a known rollback procedure,
  - ensure backups or clones are fresh,
  - verify that rollback time will be under 30 minutes.

This CH05 lab does not run any of those tools. Instead, it focuses on a
single question:

> “Does our pipeline configuration have the right *shape* to support a
> safe Single Change Highway?”

Once you understand this small lab, it is easier to reason about the
larger systems described in the chapter: they follow the same pattern,
just with more details filled in.
