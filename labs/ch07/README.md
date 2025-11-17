
# CH07 Lab — AI-generated Change Pack Evaluator

## Why this lab exists

In this lab, `labs/ch07/run.py` is a **gate** that evaluates an AI-generated change pack against chapter, RB-30, boundary, and basic model-metrics rules.

In this book’s design, we often **treat AI (or humans) as proposing structured change plans** instead of editing files directly. Those plans are then evaluated by guards before any real system is updated. This lab shows that pattern with an explicit `ai_generated_change_pack` format.

This CH07 lab is a **safe, self-contained sandbox** that shows a
version of that idea:

- A small **Labs Global Snapshot** (`state_snapshot.json`) describes the
  current lab world (models, thresholds, and a tiny “map” of chapters).
- A sample **AI-generated change pack** proposes to promote a candidate
  model.
- A Python runner evaluates whether the change pack is safe enough to
  accept, based on schema, chapter, RB-30, boundary, and metrics.

There are no external APIs in this lab. The "AI" part is represented
only by the JSON file `ai_generated_change_pack_example.json`.

CH07 is the **only chapter** that reads this snapshot. Other labs do
not depend on it.

In other words, `labs/ch07/run.py` acts as the **lab-level gate**
for AI-generated change packs: it never applies changes itself; it only
evaluates them and outputs an explicit accept/reject decision.

> **Fusion-Mart perspective.** For Fusion-Mart, you can imagine this gate deciding whether an AI-proposed model change—such as a new recommendation or fraud-detection model—is safe to promote, based on the snapshot of the current models and their agreed thresholds.

---

## Learning Objectives

By the end of this lab, you will be able to:

- Explain why we use `ai_generated_change_pack` instead of letting AI
  edit repository files directly.
- Read a small `state_snapshot.json` that describes a lab-scale model
  world and its thresholds.
- Read a sample `ai_generated_change_pack` and see how it is evaluated
  against the snapshot.
- Observe how small edits to the change pack or snapshot cause the
  guards to accept or reject the proposal.

This lab runs entirely inside `labs/ch07/` and does **not** modify any
other part of the repository.

---

## Files in This Lab

All paths are relative to the LABS repo root (`data-eng-labs-2025/`).

- **Runner**

  - `labs/ch07/run.py`  
    Entry point for the CH07 evaluator.

- **Inputs**

  - `labs/ch07/inputs/state_snapshot.json`  
    The **Labs Global Snapshot** — a compact JSON “map” of the
    lab world. For now it is prepared for you; it summarizes a few
    chapters and defines boundary and metrics used by this lab.

  - `labs/ch07/inputs/ai_generated_change_pack_example.json`  
    Example of an AI-generated change pack (what an external LLM+human
    would propose, based on the snapshot and a short natural-language brief about the desired change).

- **Output**

  - `labs/ch07/artifacts/result.json`  
    Evaluation result for the given snapshot + change pack
    (status, checks, metrics, messages).

- **Design note (optional reading)**

  - `labs/ch07/CH07_lab_min_spec.md`  
    A minimal design spec for this lab. Read this if you want to see
    how CH07 fits into the short natural-language brief about the desired change → snapshot → change pack
    pattern.

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

   * **`schema_ok`**
     Required top-level keys are present and basic types are correct
     (`kind`, `chapter`, `mode`, `rb30_anchor`, `metrics`, `changes`).

   * **`chapter_ok`**
     The pack targets chapter `"CH07"` and `"mode": "labs"`.
     If `snapshot.chapters` exists, it is also checked for consistency.

   * **`rb30_ok`**
     `rb30_anchor` has a valid `type` (`"tag"`, `"swap"`, or `"tt"`)
     and a non-empty `ref`.

   * **`boundary_ok`**
     Each change’s `target` is allowed according to
     `snapshot.boundary.allowed_targets`.

   * **`metrics_ok`**
     The candidate model AUC is above a minimum threshold and is not
     worse than the current model AUC by more than the allowed delta.

4. Compute a final `status` (`"accept"` or `"reject"`) based on all
   checks.

5. Write a report to `labs/ch07/artifacts/result.json` with:

   * `metrics.change_count` and `metrics.boundary_targets`
   * `checks.schema_ok`, `checks.chapter_ok`, `checks.rb30_ok`,
     `checks.boundary_ok`, `checks.metrics_ok`
   * `metrics.current_auc`, `metrics.candidate_auc`, `metrics.delta_auc`
   * `status` and human-readable `messages[]`

The script does **not** call any LLMs. It only evaluates the JSON files
inside `labs/ch07/`.

---

## Step 1 — Run the lab once

From the repository root:

```bash
python labs/ch07/run.py
```

You should see that:

* `labs/ch07/artifacts/result.json` is created or updated.
* The `status` field is `"accept"` for the default inputs.
* All `checks.*` flags are `true`.

Open the result file and read:

* `metrics.change_count`, `metrics.boundary_targets`
* the five `checks.*` flags
* `metrics.*`
* `messages[]`

Try to explain, in your own words, **why** the change pack is accepted.

---

## Step 2 — Edit the change pack and run again

Open:

```text
labs/ch07/inputs/ai_generated_change_pack_example.json
```

and try one experiment at a time:

1. **Break the boundary**

   * Change `"target": "production"` to a different value
     (for example `"target": "dev"`).

   * Run the lab again:

     ```bash
     python labs/ch07/run.py
     ```

   * Observe how `checks.boundary_ok` and `status` change.

2. **Break RB-30**

   * Remove the `rb30_anchor` object, or set an invalid type:

     ```json
     "rb30_anchor": {"type": "unknown", "ref": "pre-ch07-lab-001"}
     ```

   * Run the lab again and see how `checks.rb30_ok` and `status`
     change.

3. **Break the schema**

   * Remove one of the required top-level keys (for example
     `"changes"`) from the change pack.
   * Run the lab and see how `checks.schema_ok` and `messages[]`
     change.

Each time, compare the new `result.json` with the previous one.
Ask yourself: *“What kind of risk would this represent in a real
MLOps system?”*

---

## Step 3 — Edit the snapshot and run again (optional)

Now open:

```text
labs/ch07/inputs/state_snapshot.json
```

and look at:

* `boundary.allowed_targets`
* `metrics.current_model`, `metrics.candidate_model`
* `metrics.min_auc`, `metrics.max_delta_auc`

Try:

* Making the candidate model worse than the current one
  (for example set `candidate_model.auc` to `0.80`).
* Tightening the thresholds (for example set `min_auc` to `0.95`).

Then run:

```bash
python labs/ch07/run.py
```

and confirm that `checks.metrics_ok` becomes `false` and `status` is
`"reject"`.

---

## From this lab to real systems

In real MLOps + AI-governance setups:

* The **state snapshot** is generated by the platform and describes
  the current state of models, data, and thresholds.
* The **AI-generated change pack** is produced by an external LLM
  (plus human review), based on that snapshot and a human-written brief.
* A set of **guards** evaluates the pack before any real change is
  applied.

In practice, an external LLM receives a **state snapshot + a short natural-language brief about the desired change + this JSON schema**. It then produces an `ai_generated_change_pack`, and gates like this lab decide whether to accept it.

Typical guards include:

* Schema and chapter checks (is this pack even well-formed?).
* Boundary checks (does it stay within allowed scopes and targets?).
* RB-30 checks (can we roll back quickly if something goes wrong?).
* Metrics and safety checks (will this change degrade model quality
  or violate thresholds?).

This CH07 lab is a **miniature** of that process. Once you understand
this small evaluator, it becomes much easier to follow the larger
examples in the chapter and to imagine how your own systems could adopt
AI-generated change packs safely.

---

## Advanced — Regenerating the Labs Global Snapshot

For readers, `state_snapshot.json` is provided as-is.

If you are authoring or extending the labs, you can regenerate a
Labs Global Snapshot by aggregating `labs/chXX/artifacts/result.json`
files:

```bash
bash labs/ch07/snapshot_labs.sh
```

This writes a fresh snapshot to:

```text
labs/ch07/inputs/state_snapshot.json
```

This script is a **dev helper**, not part of the reader’s GA flow.
Readers can safely ignore it and simply use the snapshot included in
the repository.
