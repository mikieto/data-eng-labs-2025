
# CH02 Lab — Boundary, Change Unit, and RB-30 (Tiny World)

## Why this lab exists

In this lab, `labs/ch02/run.py` is a **gate** that evaluates tiny change requests against the boundary, Change Unit limits, and an RB-30 anchor.

In real projects, we want three things at the same time:

1. **A clear boundary** for each change (where it is allowed to touch).
2. **A small, reviewable Change Unit** instead of “big bang” edits.
3. **An RB-30 anchor** so we can roll back quickly if something goes wrong.

This CH02 lab gives you a tiny, fully deterministic sandbox where you can
practice these ideas with JSON files instead of a production data platform.

> **Fusion-Mart perspective.** In the Fusion-Mart case study, this lab acts as the gate for any small platform change—such as adjusting a pricing rule or adding a new event field—so each change stays inside a clear boundary and keeps a proven RB-30 rollback.

---

## Learning Objectives

By the end of this lab, you will be able to:

- Describe a tiny boundary for a change (allowed paths + limits).
- Check whether a change request stays inside that boundary.
- Confirm that an RB-30 anchor is present for safe rollback.

This lab runs entirely inside `labs/ch02/` and does **not** modify any other
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

* `labs/ch02/run.py` — the lab runner (entry point).
* `labs/ch02/inputs/boundary_config.json` — fixed boundary and limits.
* `labs/ch02/inputs/change_request.json` — a small change request you can edit.
* `labs/ch02/artifacts/result.json` — result JSON created by the runner.

---

## What the runner actually does

When you run:

```bash
python labs/ch02/run.py
```

the runner will:

1. Load `boundary_config.json` (the allowed paths and limits).
2. Load `change_request.json` (the proposed change).
3. Check whether the change:

   * stays inside the configured boundary,
   * stays within the Change Unit limits, and
   * contains a valid RB-30 anchor.
4. Write all results into `labs/ch02/artifacts/result.json`, including:

   * overall `status`,
   * detailed `checks.*` flags,
   * metrics like `metrics.files_count`,
   * and human-readable `messages[]`.

The code never touches files outside `labs/ch02/**`.

---

## Step 1 — Run the lab once

From the repository root:

```bash
python labs/ch02/run.py
```

You should see that:

* `labs/ch02/artifacts/result.json` is created or updated.
* The `status` field is `"accept"` for the default change request.

Open the result file and read:

* `metrics.files_count` and `metrics.total_lines_added`
* `checks.boundary_ok`, `checks.unit_ok`, and `checks.rb30_ok`
* `messages[]`

---

## Step 2 — Edit one thing and run again

Now open:

```text
labs/ch02/inputs/change_request.json
```

Try one of these small experiments:

1. **Break the boundary**

   * Change the file path to a different chapter, for example:

   ```json
   "path": "labs/ch03/demo.txt"
   ```

   * Save the file, then run:

   ```bash
   python labs/ch02/run.py
   ```

   * Observe how `checks.boundary_ok` and `status` change.

2. **Break the Change Unit limits**

   * Set `lines_added` to a large number, for example `200`.
   * Run the lab again and see how `checks.unit_ok` and `status` change.

3. **Break RB-30**

   * Remove the `rb30_anchor` field or change its `"type"` to an unsupported value.
   * Run the lab again and confirm that `checks.rb30_ok` is now `false`.

Each time, compare the new `result.json` with the previous result.

---

## Step 3 — Resetting to the Day-0 state (RB-30 for this lab)

If your experiments leave the lab in a broken state and you want to return to
the original Day-0 state for CH02 labs, you can reset your working tree to the
RB-30 anchor tag:

```bash
git reset --hard ch02-labs-v1
```

> ⚠️ This discards local changes.
> If you are using GitHub Codespaces, you can also simply delete and recreate
> the Codespace to get back to a clean Day-0 state.

---

## From this lab to real systems

In real data platforms:

* The **boundary** is often defined in configuration (allowed schemas, paths, or roles).
* The **Change Unit** is a small, reviewable set of changes (files / lines / operations).
* **RB-30** is implemented through tags, clones, or time travel, so that any
  failed change can be rolled back quickly.

This tiny CH02 lab is a miniature of that world: you practice the same ideas
with a very small, deterministic JSON-based exercise.

