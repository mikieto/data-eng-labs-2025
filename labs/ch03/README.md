# CH03 Lab — Integration Strategy, SLI/SLO & ROI

## Why this lab exists

In the book, CH03 discusses how to reason about **data integration
strategy** using business impact, SLI/SLO, and ROI — instead of talking
about pipelines only as “technical plumbing”.

This CH03 lab is a **small, self-contained sandbox** that turns that
idea into something you can run:

- A tiny **integration pipeline config** (`integration_pipeline.json`)
  describes which systems you integrate and how much business impact
  each brings.
- A separate **SLI/SLO + ROI config**
  (`sli_slo_config.json`) defines thresholds and targets
  (freshness, coverage, ROI, payback period).
- A Python runner evaluates whether the current integration plan is
  good enough to accept, based on those configs.

There are no external APIs in this lab. Everything lives under
`labs/ch03/` and runs locally.

In other words, `labs/ch03/run.py` acts as a **lab-level guard** for
integration strategy: it never runs a real ETL job; it only evaluates
the plan and outputs an explicit accept/reject decision.

---

## Learning Objectives

By the end of this lab, you will be able to:

- Encode a simple integration pipeline as a config file
  (`integration_pipeline.json`).
- Encode SLI/SLO thresholds and ROI targets in a separate config
  (`sli_slo_config.json`).
- Run an evaluator that:
  - computes basic business metrics (impact, cost, ROI, payback period),
  - checks them against thresholds,
  - produces a single JSON result (`artifacts/result.json`).
- Read the result file and explain **why** a given integration plan is
  accepted or rejected.

This lab runs entirely inside `labs/ch03/` and does **not** modify any
other part of the repository.

---

## Files in This Lab

All paths are relative to the LABS repo root (`data-eng-labs-2025/`).

- **Runner**

  - `labs/ch03/run.py`  
    Entry point for the CH03 integration evaluator.

- **Inputs**

  - `labs/ch03/inputs/integration_pipeline.json`  
    Describes a small integration pipeline:
    which source systems are integrated, how much expected monthly
    impact each brings, and basic SLI values such as freshness and
    coverage.

  - `labs/ch03/inputs/sli_slo_config.json`  
    Describes SLO thresholds and ROI targets:
    how fresh and complete the data should be, how much ROI you expect
    after 12 months, and what payback period is acceptable.

- **Output**

  - `labs/ch03/artifacts/result.json`  
    Evaluation result for the given integration + SLI/SLO config
    (status, checks, metrics, messages), following the common Labs
    result JSON invariants.

---

## What the runner actually does

When you run:

```bash
python labs/ch03/run.py
```

the script will:

1. Read `labs/ch03/inputs/integration_pipeline.json`.

2. Read `labs/ch03/inputs/sli_slo_config.json`.

3. Compute the following metrics:

   - **Business impact**

     - `metrics.total_expected_monthly_impact_usd`  
       Sum of `expected_monthly_revenue_impact_usd` across all sources.

   - **Effort and cost**

     - `metrics.total_integration_effort_days`  
       Sum of `integration_effort_days` across sources.

     - `metrics.total_integration_cost_usd`  
       Effort days × `cost_per_engineer_day_usd`.

   - **SLI values**

     - `metrics.freshness_hours`  
       Expected data freshness.

     - `metrics.coverage_pct`  
       Expected coverage (fraction of entities or events covered).

   - **ROI and payback**

     - `metrics.roi_after_12_months`  
       `(12 × monthly_impact – integration_cost) / integration_cost`.

     - `metrics.payback_period_months`  
       `integration_cost / monthly_impact`.

4. Evaluate the following checks:

   - **`checks.sli_slo_ok`**  
     True when `freshness_hours` and `coverage_pct` meet the thresholds
     in `sli_slo_config.json`.

   - **`checks.roi_ok`**  
     True when `roi_after_12_months` and `payback_period_months` meet
     their targets.

   - **`checks.overall_ok`**  
     True only when both `sli_slo_ok` and `roi_ok` are true.

5. Compute a final `status`:

   - `"accept"` if `checks.overall_ok` is true.
   - `"reject"` otherwise.

6. Write a report to `labs/ch03/artifacts/result.json` with:

   - `chapter`, `status`, `change_id` (scenario id)
   - `checks.sli_slo_ok`, `checks.roi_ok`, `checks.overall_ok`
   - all `metrics.*` values
   - human-readable `messages[]`

The script does **not** talk to any databases or pipelines. It only
evaluates the JSON files inside `labs/ch03/`.

---

## Step 1 — Run the lab once

From the repository root:

```bash
python labs/ch03/run.py
```

You should see that:

- `labs/ch03/artifacts/result.json` is created or updated.
- The `status` field is `"accept"` for the default inputs.
- All `checks.*` flags are `true`.

Open the result file and read:

- `metrics.total_expected_monthly_impact_usd`
- `metrics.total_integration_cost_usd`
- `metrics.roi_after_12_months`
- `metrics.payback_period_months`
- the three `checks.*` flags
- `messages[]`

Try to explain, in your own words, **why** this integration plan is
accepted.

---

## Step 2 — Change the integration plan and run again

Open:

```text
labs/ch03/inputs/integration_pipeline.json
```

and try one experiment at a time:

1. **Increase the effort**

   - Double one source’s `integration_effort_days`.
   - Run the lab again:

     ```bash
     python labs/ch03/run.py
     ```

   - Observe how `metrics.total_integration_cost_usd`,
     `metrics.roi_after_12_months`, and `checks.roi_ok` change.

2. **Reduce the impact**

   - Halve one source’s
     `expected_monthly_revenue_impact_usd`.
   - Run the lab again and see how ROI and payback period change.

Each time, compare the new `result.json` with the previous one.
Ask yourself: *“Would this still be a good integration project to run?”*

---

## Step 3 — Tighten the thresholds and run again

Now open:

```text
labs/ch03/inputs/sli_slo_config.json
```

and look at:

- `slo_thresholds.freshness_hours_max`
- `slo_thresholds.coverage_pct_min`
- `roi_target_after_12_months`
- `payback_period_target_months`

Try:

- Making the SLOs stricter  
  (for example, set `freshness_hours_max` to `2.0` or
  `coverage_pct_min` to `0.995`).

- Making ROI expectations more aggressive  
  (for example, set `roi_target_after_12_months` to `5.0`).

Then run:

```bash
python labs/ch03/run.py
```

and confirm when `checks.sli_slo_ok` or `checks.roi_ok` become `false`
and `status` becomes `"reject"`.

---

## From this lab to real systems

In real data integration and analytics platforms, the three files in
this lab usually live in different places:

- `integration_pipeline.json` is a **summary of your integration plans
  or current pipelines**, generated from your pipeline repo and
  metadata:
  - tools like dbt / Airflow / Dagster / Prefect define the pipelines,
  - CI or a catalog job aggregates their cost, dependencies, and
    expected impact into a small JSON summary.

- `sli_slo_config.json` is a **separate SLI/SLO & ROI catalog** agreed
  with stakeholders:
  - freshness, coverage, and latency targets,
  - expected ROI after N months and acceptable payback period,
  - stored in a dedicated “SLO repo” or a governance table.

- `labs/ch03/run.py` represents a **guard** that reads both:
  - "Given this pipeline plan or current state, and these SLO/ROI
    targets, is this integration still worth doing or keeping?"

In a more complete system you would typically run a CH03-like guard in
two moments:

1. **Before building a new integration**  
   Evaluate a proposed integration plan (estimated effort and impact)
   against your SLO/ROI targets. If it fails, either improve the plan
   or deprioritize the project.

2. **After deploying and observing a pipeline**  
   Aggregate real metrics (freshness, coverage, latency, cost) into a
   JSON summary and check it against the same SLO/ROI config. If it
   violates your targets, trigger alerts, slow down rollout, or roll
   back.

This lab is a **miniature** of that control-plane logic. Once you
understand this small evaluator, it becomes easier to design your own
integration governance:

- Where integration-summary JSONs are produced (CI, catalog jobs),
- Where SLI/SLO & ROI targets live (config repo, data catalog),
- Where guards like CH03 run (CI, change-approval tools, or scheduled
  checks).

---

## Advanced — Possible extensions

- Introduce tiny CSVs under `labs/ch03/raw/**` and derive freshness /
  coverage metrics from sample data instead of fixed values.
- Evaluate multiple candidate pipelines and choose the best one based
  on weighted scores.
- Integrate this evaluator with a higher-level "change pack" flow,
  where an AI proposes new integration combinations to be checked by
  this lab before implementation.
