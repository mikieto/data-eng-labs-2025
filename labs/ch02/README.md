
# CH02 Lab — Boundary, Change Unit, Evidence, RB-30

This lab belongs to **CH02** of the book.

---

## Learning Objectives

By the end of this lab, you should be able to:

1. Explain, in simple words, what **Boundary**, **Change Unit**, **Evidence**, and **RB-30** mean.
2. Make one tiny, intentional **Change Unit** under `labs/ch02/`.
3. Write down, in your own notes, how you would roll back that Change Unit within a few minutes.

In this first lab, your **Boundary** is also simple:  
you only touch files under `labs/ch02/`.

---

## Before You Start

Make sure your environment is set up according to the **Standard Runtime
(GitHub Codespaces)** described in the root `README.md` of this repository.

Once you can run:

```bash
python labs/ch02/run.py
```

inside that environment and see the output for CH02, you are ready for this lab.

---

## Files in This Lab

Typical files under `labs/ch02/`:

* `README.md` — this guide
* `run.py` — a small script that prints a simple lab manifest

---

## What You Will Do (Day-0 skeleton)

### Step 1 — Run the script and check the initial output

Run:

```bash
python labs/ch02/run.py
```

You should see output similar to this:

```json
{
  "chapter": "CH02",
  "lab": "boundary_change_unit_evidence_rb30",
  "change_unit_example": "original"
}
```

If you see this JSON (or the same keys/values), your environment for this lab
is working.

---

### Step 2 — Make one tiny, intentional Change Unit

Open `labs/ch02/run.py` in your editor and find this line inside the `manifest`
dictionary:

```python
        "change_unit_example": "original",
```

Change only this line to:

```python
        "change_unit_example": "after_first_change",
```

This is your **Change Unit** for this lab: exactly one small, intentional edit.

Now run the script again:

```bash
python labs/ch02/run.py
```

You should now see:

```json
{
  "chapter": "CH02",
  "lab": "boundary_change_unit_evidence_rb30",
  "change_unit_example": "after_first_change"
}
```

If the value changed from `"original"` to `"after_first_change"` and nothing
else broke, your Change Unit is complete.

---

### Step 3 — Think about rollback (RB-30 in miniature)

In your own notes, describe how you would roll back this Change Unit within a
few minutes. For example:

* Use your editor’s undo, or
* Use a Git command such as:

```bash
git restore labs/ch02/run.py
```

The important part is:

* You know **exactly what you changed** (one line), and
* You know **exactly how to undo it quickly**.

That is the smallest possible form of RB-30.

Your short note here is also your first piece of **Evidence**:
it records what you changed and how you would recover.

---

### Why such a tiny Change Unit is enough (for now)

You might feel that this exercise is “too small” or “too obvious”.
That is intentional.

The goal of this first lab is **not** to build anything complex.
The goal is to get used to a simple pattern:

* **1 Change Unit**: you change exactly one small thing on purpose.
* **Always reversible**: you know exactly how to undo it quickly.

Later chapters and labs will:

* Introduce more realistic code changes and data-platform examples.
* Show stronger rollback patterns (for example, using Git tags and RB-30 drills).
* Connect these ideas to `state_snapshot.json` and `ai_generated_change_pack`.

For now, it is completely fine if your Change Unit is only “one extra line”
and your rollback is simply “undo the line or run `git restore`”.

---

## Completion Criteria

You have completed this lab when you can:

* Run `python labs/ch02/run.py` in the standard runtime.
* Perform one tiny, intentional Change Unit under `labs/ch02/`
  (the value of `change_unit_example` changes as expected).
* Explain, in your own words, how you would roll it back quickly and how it
  relates to Boundary / Change Unit / Evidence / RB-30.

