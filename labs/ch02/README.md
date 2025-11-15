# CH02 Lab — Boundary, Change Unit, and RB-30 (Tiny World)

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

- `labs/ch02/run.py` — the lab runner (entry point).
- `labs/ch02/inputs/boundary_config.json` — fixed boundary and limits.
- `labs/ch02/inputs/change_request.json` — a small change request you can edit.
- `labs/ch02/artifacts/ch02_result.json` — result JSON created by the runner.

---

## Step 1 — Run the lab once

From the repository root:

```bash
python labs/ch02/run.py
```

You should see that:

- `labs/ch02/artifacts/ch02_result.json` is created or updated.
- The `status` field is `"accept"` for the default change request.

Open the result file and read:

- `summary.files_count` and `summary.total_lines_added`
- `checks.boundary_ok`, `checks.unit_ok`, and `checks.rb30_ok`
- `messages[]`

---

## Step 2 — Edit one thing and run again

Now open:

```text
labs/ch02/inputs/change_request.json
```

Try one of these small experiments:

1. **Break the boundary**

- Change the file path to a different chapter, for example:

```json
"path": "labs/ch03/demo.txt"
```

- Save the file, then run:

```bash
python labs/ch02/run.py
```

- Observe how `checks.boundary_ok` and `status` change.

2. **Break the Change Unit limits**

- Set `lines_added` to a large number, for example `200`.
- Run the lab again and see how `checks.unit_ok` and `status` change.

3. **Break RB-30**

- Remove the `rb30_anchor` field or change its `"type"` to an unsupported value.
- Run the lab again and confirm that `checks.rb30_ok` is now `false`.

Each time, compare the new `ch02_result.json` with the previous result.

---

## Step 3 — From this lab to real systems

In real data platforms:

- The **boundary** is often defined in configuration (allowed schemas, paths, or roles).
- The **Change Unit** is a small, reviewable set of changes (files / lines / operations).
- **RB-30** is implemented through tags, clones, or time travel, so that any
  failed change can be rolled back quickly.

This tiny CH02 lab is a miniature of that world: you practice the same ideas
with a very small, deterministic JSON-based exercise.
