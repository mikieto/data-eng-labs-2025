# CH07 Lab — AI-generated Change Pack Evaluator (Day-0 / Phase-1)

## Why this lab exists

In the later chapters, we use AI to propose changes as
`ai_generated_change_pack` JSON objects, instead of letting the AI
edit files directly. Those change packs are then evaluated by guards
before any real system is updated.

This lab gives you a tiny, lab-only version of that idea:

- A small **state snapshot** describes the current and candidate model
  and a few thresholds.
- A sample **AI-generated change pack** proposes to promote a candidate
  model.
- A Python runner evaluates whether the change pack is safe enough
  to accept, based on schema, boundary, RB-30, and metrics.

There are no external APIs in this lab. The "AI" part is represented
only by the JSON file `ai_generated_change_pack_example.json`.

---

## Learning Objectives

By the end of this lab, you will be able to:

- Explain why we use `ai_generated_change_pack` instead of letting AI
  edit repository files directly.
- Read a tiny `state_snapshot.json` that describes the lab-scale model
  world and its thresholds.
- Read a sample `ai_generated_change_pack` and see how it is evaluated
  against the snapshot.
- Observe how small edits to the change pack JSON cause the guards to
  accept or reject the proposal.

This lab runs entirely inside `labs/ch07/` and does **not** modify any
other part of the repository.

---

## Files in This Lab

- `labs/ch07/run.py` — the lab runner (entry point).
- `labs/ch07/inputs/state_snapshot.json` — tiny lab-scale snapshot
  describing the current and candidate model, thresholds, and boundary.
- `labs/ch07/inputs/ai_generated_change_pack_example.json` — sample
  AI-generated change pack for this lab.
- `labs/ch07/artifacts/ch07_result.json` — result JSON created by
  the runner.

You do **not** need to install any extra libraries. The runner uses only
the Python standard library.

---

## What the runner actually does

When you run:

```bash
python labs/ch07/run.py
```

the script will:

1. Read `labs/ch07/inputs/state_snapshot.json`.
2. Read `labs/ch07/inputs/ai_generated_change_pack_example.json`.
3. Evaluate the change pack with the following checks:

   - **schema_ok**: required top-level keys are present and basic types
     are correct (`kind`, `chapter`, `mode`, `rb30_anchor`, `summary`,
     `changes`).
   - **chapter_ok**: the change pack targets chapter `CH07` and matches
     the snapshot.
   - **rb30_ok**: `rb30_anchor` has a valid `type` (`tag`, `swap`, or
     `tt`) and a non-empty `ref`.
   - **boundary_ok**: each change targets an environment listed in
     `snapshot.boundary.allowed_targets`.
   - **metrics_ok**: the candidate model AUC is above a minimum threshold
     and is not worse than the current model AUC by more than the
     allowed delta.

4. Write a report to `labs/ch07/artifacts/ch07_result.json` with:

   - `summary.change_count` and `summary.boundary_targets`
   - `checks.schema_ok`, `checks.chapter_ok`, `checks.rb30_ok`,
     `checks.boundary_ok`, `checks.metrics_ok`
   - `status` (`"accept"` or `"reject"`)
   - human-readable `messages[]`

The script does **not** call any LLMs. It only evaluates the JSON files
inside `labs/ch07/`.

---

## Step 1 — Run the lab once

From the repository root:

```bash
python labs/ch07/run.py
```

You should see that:

- `labs/ch07/artifacts/ch07_result.json` is created or updated.
- The `status` field is `"accept"` for the default inputs.

Open the result file and read:

- `summary.change_count`, `summary.boundary_targets`
- the five `checks.*` flags
- `messages[]`

Try to explain, in your own words, why the change pack is accepted.

---

## Step 2 — Edit the change pack and run again

Now open:

```text
labs/ch07/inputs/ai_generated_change_pack_example.json
```

and try one experiment at a time:

1. **Break the boundary**

   - Change `"target": "production"` to a different value
     (for example `"target": "dev"`).
   - Run the lab again:

     ```bash
     python labs/ch07/run.py
     ```

   - Observe how `checks.boundary_ok` and `status` change.

2. **Break RB-30**

   - Remove the `rb30_anchor` object, or set an invalid type:

     ```json
     "rb30_anchor": {"type": "unknown", "ref": "pre-ch07-lab-001"}
     ```

   - Run the lab again and see how `checks.rb30_ok` and `status`
     change.

3. **Break the metrics guard**

   - Edit `labs/ch07/inputs/state_snapshot.json` and make the
     candidate model worse than the current model, for example:

     ```json
     "candidate_model": {"id": "ch07_model_v2", "auc": 0.80}
     ```

   - Run the lab again and confirm that `checks.metrics_ok` is now
     `false`.

4. **Break the schema**

   - Remove one of the required top-level keys (for example
     `"changes"`) from the change pack.
   - Run the lab and see how `checks.schema_ok` and `messages[]`
     change.

Each time, compare the new `ch07_result.json` with the previous result.
Ask yourself: *“What kind of risk would this represent in a real
MLOps system?”*

---

## Step 3 — From this lab to real systems

In real MLOps + AI-governance setups:

- The **state snapshot** is generated by the platform and describes
  the current state of models, data, and thresholds.
- The **AI-generated change pack** is produced by an external LLM
  (plus human review), based on that snapshot.
- A set of **guards** evaluates the pack before any real change is
  applied.

Typical guards include:

- Schema and chapter checks (is this pack even well-formed?).
- Boundary checks (does it stay within allowed scopes and targets?).
- RB-30 checks (can we roll back quickly if something goes wrong?).
- Metrics and safety checks (will this change degrade model quality
  or violate thresholds?).

This CH07 lab is a miniature of that process. Once you understand
this small evaluator, it becomes much easier to follow the larger
examples in the chapter and to imagine how your own systems could
adopt AI-generated change packs safely.
