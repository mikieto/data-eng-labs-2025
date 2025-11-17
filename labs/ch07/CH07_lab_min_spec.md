
---

## CH07 Lab – Minimal Specification

> **One-liner**
> CH07 Lab is a **safe sandbox** for evaluating AI-generated change packs against a small, shared “Labs Global Snapshot” without letting AI touch real repositories.

---

### 0. Purpose & Non-goals

**Purpose**

* Provide a **single, concrete example** of the
  **brief → snapshot → AI-generated change pack → evaluator** flow.
* Show how to treat **AI proposals (including code suggestions) as data**, not as direct file edits.
* Give a reusable pattern for later labs (CH03–CH10) without forcing them to adopt snapshots immediately.

**Non-goals**

* Do **not** apply change packs to any real repo (OPS or LABS).
  CH07 only **evaluates**.
* Do **not** call real LLM APIs from `labs/ch07/run.py`.
  AI proposals are provided as JSON files.
* Do **not** depend on any external services or libraries (standard library only).
* Do **not** require other chapters to read `state_snapshot.json`.
  Snapshot reading is **CH07 only**.

---

### 1. File & Directory Layout (CH07 world)

All paths are relative to the LABS repo root `data-eng-labs-2025/`.

* **Runner**

  * `labs/ch07/run.py`  
    Entry point for the CH07 Lab evaluator.

* **Inputs**

  * `labs/ch07/inputs/state_snapshot.json`  
    Labs Global Snapshot (small “map” of the labs world, aggregated from `labs/chXX/artifacts/result.json`).

  * `labs/ch07/inputs/ai_generated_change_pack_example.json`  
    Example of an AI-generated change pack (produced outside this repo).

* **Output**

  * `labs/ch07/artifacts/result.json`  
    Evaluation result for the given snapshot + change pack.

CH07 Lab must not read or write outside `labs/ch07/**`.

---

### 2. Inputs

#### 2.1 Labs Global Snapshot – `state_snapshot.json`

**Role**

* Acts as **Labs Global Snapshot** for Day-0: a compact, and intentionally slightly messy, JSON that summarizes the current lab world.
* Conceptually an aggregation of **each chapter’s `artifacts/result.json`**, but the exact aggregation logic is left to `snapshot_labs.sh` or manual preparation.

**Minimum content (Day-0)**

* `meta`: generation info (who generated this, when, from what source).
* `chapters`: map of chapter IDs to small summaries (at least CH02/03/04/05/06/07/08/09/10).
* `boundary`: configuration for allowed targets and environments relevant to CH07.
* `metrics`: small set of model metrics used by CH07 evaluator (e.g. AUC for current vs candidate model, thresholds, etc.).

The exact schema can evolve. CH07 evaluator must **fail closed** (reject) when required fields are missing or invalid.

#### 2.2 AI-Generated Change Pack – `ai_generated_change_pack_example.json`

**Role**

* Represents what an external LLM+Human pair would propose, based on:

  * a **short natural-language brief** about the desired change, and
  * `state_snapshot.json` as input context.

**Minimum shape (Day-0)**

```jsonc
{
  "kind": "ai_generated_change_pack",
  "chapter": "CH07",
  "mode": "labs",
  "rb30_anchor": { "type": "tag", "ref": "pre-ch07-lab-001" },
  "metrics": {
    "reason": "Promote candidate model ch07_model_v2 to production.",
    "confidence": 0.82
  },
  "changes": [
    {
      "type": "model_promotion",
      "target": "production",
      "from_model_id": "ch07_model_v1",
      "to_model_id": "ch07_model_v2",
      "expected_auc": 0.94
      // optional:
      // "code_snippets": [...],
      // "notes": [...]
    }
  ]
}
```

**Important constraints**

* Top-level is **JSON only**; no free-form long text blobs.
* Each `changes[*]` may include **structured code suggestions** (e.g. `code_snippets[]`) as **data**, but:

  * CH07 evaluator does **not** execute or apply them.
  * They are just part of the evaluation payload.

---

### 3. Output – `labs/ch07/artifacts/result.json`

**Location**

* Always written to:
  `labs/ch07/artifacts/result.json`

**Shape (Day-0)**

Minimum recommended structure:

```jsonc
{
  "chapter": "CH07",
  "status": "accept",            // or "reject"
  "change_id": "baseline",       // or another ID, or null
  "metrics": {
    "current_auc": 0.92,
    "candidate_auc": 0.94,
    "min_auc": 0.90,
    "max_delta_auc": 0.05,
    "delta_auc": 0.02,
    "change_count": 1,
    "boundary_targets": ["production"]
  },
  "checks": {
    "schema_ok": true,
    "chapter_ok": true,
    "rb30_ok": true,
    "boundary_ok": true,
    "metrics_ok": true
  },
  "messages": [
    "Candidate model AUC (0.94) >= min_threshold (0.90).",
    "Candidate is not worse than current model by more than allowed delta.",
    "All change targets are within allowed_targets."
  ]
}
```

**Invariants**

* If any check fails, `status` **must** be `"reject"`.
* `messages[]` must be human-readable explanations of why the pack was accepted or rejected.

---

### 4. Runner Contract – `labs/ch07/run.py`

**Invocation**

From LABS repo root:

```bash
python labs/ch07/run.py
```

**Behavior**

1. Read `labs/ch07/inputs/state_snapshot.json`.

2. Read `labs/ch07/inputs/ai_generated_change_pack_example.json`.

3. Perform the following checks:

   * `schema_ok`
     Required top-level keys in change pack exist and have expected basic types.

   * `chapter_ok`
     `chapter == "CH07"`, `mode == "labs"`, matches the snapshot’s notion of CH07 if applicable.

   * `rb30_ok`
     `rb30_anchor.type` is one of `{ "tag", "swap", "tt" }` and `ref` is non-empty.

   * `boundary_ok`
     All change targets are allowed according to `snapshot.boundary.allowed_targets`.

   * `metrics_ok`
     Candidate metrics from snapshot satisfy thresholds (for example, candidate AUC ≥ minimum and not worse than current by more than the allowed delta).

4. Compute final `status` = `"accept"` or `"reject"` using all checks.

5. Write `labs/ch07/artifacts/result.json`.

**Non-behavior**

* Do **not**:

  * Call external LLMs.
  * Modify any files outside `labs/ch07/**`.
  * Execute or apply any code contained in `code_snippets[]`.

---

### 5. Invariants & Safety

* **Isolation**

  * CH07 Lab is fully contained in `labs/ch07/**`.
  * No writes to `ops/**`, `docs/**` or other chapters’ directories.

* **Determinism**

  * Given the same `state_snapshot.json` and change pack JSON,
    `result.json` must be deterministic.

* **Fail-safe**

  * On parse errors, missing keys, or unexpected values, evaluator should:

    * Set the corresponding `checks.*` to `false`,
    * Set `status = "reject"`,
    * Add clear messages to `messages[]`.

* **Read access to snapshot**

  * Only CH07 Labs reads `labs/ch07/inputs/state_snapshot.json`.
    Other chapters do not depend on this file.

---

### 6. Relation to External LLM & Human Brief

Although not implemented inside the repo, the intended flow is:

1. **Brief** (outside the repo)
   A human writes a short natural-language brief describing:

   * the desired change (e.g. “promote candidate model v2 to production”),
   * guardrails and constraints,
   * acceptance criteria at a high level.

2. **Snapshot** (LABS side)
   `labs/ch07/inputs/state_snapshot.json` is prepared or refreshed to reflect the current Labs world.

3. **External environment** (outside the repo)

   * An LLM receives:

     * the brief text, and
     * `state_snapshot.json` as JSON context,
     * plus the JSON schema documented in this spec.

   * The LLM produces an `ai_generated_change_pack` JSON
     (optionally including `code_snippets[]`).

4. **Human** copies or saves that JSON as
   `labs/ch07/inputs/ai_generated_change_pack_example.json`.

5. Run the evaluator:

   ```bash
   python labs/ch07/run.py
   ```

6. Human reads `labs/ch07/artifacts/result.json` and decides whether to:

   * accept/reject the proposal, and
   * manually apply it on the OPS side (if applicable).

CH07 Lab **teaches this pattern** without yet wiring the full automation.

---

### 7. Future Extensions (out of scope for Day-0, but compatible)

* Support additional checks (e.g., safety policies, more metrics, multiple environments).
* Add more structured fields to `changes[*]` (e.g., `config_patches`, `sql_diff`, `yaml_patch`).
* Wire CH03/CH05/CH10 Labs so that their `result.json` is actually the source for parts of `state_snapshot.json`.
* Add a small CLI wrapper (outside this lab) to generate change packs via a real LLM API.

