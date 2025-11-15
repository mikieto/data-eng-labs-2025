#!/usr/bin/env python3
"""
CH07 lab runner — AI-generated Change Pack Evaluator (Day-0 / Phase-1).

This runner reads:
  - a tiny lab-scale state snapshot (state_snapshot.json)
  - a sample AI-generated change pack (ai_generated_change_pack_example.json)

and evaluates whether the change pack is *safe enough* to accept,
based on a minimal set of checks:

  - schema_ok: basic required keys and types are present
  - chapter_ok: the pack targets the correct chapter / world
  - rb30_ok: an RB-30 anchor is present and well-formed
  - boundary_ok: the proposed changes stay within allowed targets
  - metrics_ok: the candidate model quality meets thresholds from the snapshot

The result is written to:
  labs/ch07/artifacts/ch07_result.json

This is a closed lab. The runner does NOT call any external LLM APIs.
It only evaluates the JSON files inside labs/ch07/.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


HERE = Path(__file__).resolve().parent
INPUTS_DIR = HERE / "inputs"
ARTIFACTS_DIR = HERE / "artifacts"

ALLOWED_RB30_TYPES = {"tag", "swap", "tt"}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def ensure_artifacts_dir() -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def evaluate_change_pack(
    snapshot: Dict[str, Any],
    pack: Dict[str, Any],
) -> Dict[str, Any]:
    """Evaluate a tiny AI-generated change pack against a lab-scale snapshot."""
    # Basic schema checks
    schema_ok, schema_messages = check_schema(pack)
    chapter_ok = (
        isinstance(pack.get("chapter"), str)
        and pack.get("chapter") == snapshot.get("chapter") == "CH07"
    )
    rb30_ok = check_rb30(pack.get("rb30_anchor"))
    boundary_ok, boundary_targets, boundary_messages = check_boundary(
        snapshot, pack
    )
    metrics_ok, metrics_messages = check_metrics(snapshot)

    status = (
        "accept"
        if (schema_ok and chapter_ok and rb30_ok and boundary_ok and metrics_ok)
        else "reject"
    )

    messages: List[str] = []
    messages.extend(schema_messages)
    messages.append(
        "Change pack targets chapter CH07 and matches the lab snapshot."
        if chapter_ok
        else "Change pack chapter does not match the lab snapshot (expected CH07)."
    )
    messages.append(
        "RB-30 anchor is present and well-formed."
        if rb30_ok
        else "RB-30 anchor is missing or invalid."
    )
    messages.extend(boundary_messages)
    messages.extend(metrics_messages)

    change_list = pack.get("changes") or []
    change_count = len(change_list)

    return {
        "chapter": "CH07",
        "summary": {
            "change_count": change_count,
            "boundary_targets": sorted(boundary_targets),
        },
        "checks": {
            "schema_ok": bool(schema_ok),
            "chapter_ok": bool(chapter_ok),
            "rb30_ok": bool(rb30_ok),
            "boundary_ok": bool(boundary_ok),
            "metrics_ok": bool(metrics_ok),
        },
        "status": status,
        "messages": messages,
    }


def check_schema(pack: Dict[str, Any]) -> Tuple[bool, List[str]]:
    messages: List[str] = []
    required_top_keys = [
        "kind",
        "chapter",
        "mode",
        "rb30_anchor",
        "summary",
        "changes",
    ]
    missing_keys = [k for k in required_top_keys if k not in pack]
    kind_ok = pack.get("kind") == "ai_generated_change_pack"
    mode_ok = pack.get("mode") in {"text", "labs"}

    if missing_keys:
        messages.append(
            "Change pack is missing required keys: " + ", ".join(missing_keys)
        )
    if not kind_ok:
        messages.append(
            "Change pack 'kind' must be 'ai_generated_change_pack'."
        )
    if not mode_ok:
        messages.append(
            "Change pack 'mode' should be either 'text' or 'labs' (labs for this lab)."
        )

    changes = pack.get("changes")
    if not isinstance(changes, list) or not changes:
        messages.append("Change pack must contain at least one change.")

    schema_ok = (
        not missing_keys
        and kind_ok
        and mode_ok
        and isinstance(changes, list)
        and bool(changes)
    )

    if schema_ok:
        messages.insert(0, "Basic change pack schema looks valid.")

    return schema_ok, messages


def check_rb30(rb30_anchor: Any) -> bool:
    if not isinstance(rb30_anchor, dict):
        return False
    rb_type = rb30_anchor.get("type")
    ref = rb30_anchor.get("ref")
    if rb_type not in ALLOWED_RB30_TYPES:
        return False
    if not isinstance(ref, str) or not ref.strip():
        return False
    return True


def check_boundary(
    snapshot: Dict[str, Any],
    pack: Dict[str, Any],
) -> Tuple[bool, List[str], List[str]]:
    messages: List[str] = []
    boundary = snapshot.get("boundary") or {}
    allowed_targets = set(boundary.get("allowed_targets") or [])
    # Day-0: we do not expand allowed_paths; we simply check targets.

    changes = pack.get("changes") or []
    targets_seen: List[str] = []
    invalid_targets: List[str] = []

    for change in changes:
        if not isinstance(change, dict):
            invalid_targets.append("<non-dict-change>")
            continue
        target = change.get("target")
        if target is None:
            invalid_targets.append("<missing-target>")
            continue
        targets_seen.append(str(target))
        if target not in allowed_targets:
            invalid_targets.append(str(target))

    if not allowed_targets:
        messages.append(
            "Snapshot boundary.allowed_targets is empty; cannot evaluate targets."
        )
        boundary_ok = False
    elif invalid_targets:
        messages.append(
            "Some changes target environments outside the allowed_targets: "
            + ", ".join(sorted(set(invalid_targets)))
        )
        boundary_ok = False
    else:
        messages.append(
            "All change targets are within the allowed_targets defined in the snapshot."
        )
        boundary_ok = True

    return boundary_ok, targets_seen, messages


def check_metrics(snapshot: Dict[str, Any]) -> Tuple[bool, List[str]]:
    messages: List[str] = []

    current = snapshot.get("current_model") or {}
    candidate = snapshot.get("candidate_model") or {}
    thresholds = snapshot.get("thresholds") or {}

    try:
        current_auc = float(current.get("auc"))
        candidate_auc = float(candidate.get("auc"))
    except (TypeError, ValueError):
        messages.append(
            "Could not read numeric AUC values for current or candidate model."
        )
        return False, messages

    min_candidate_auc = float(thresholds.get("min_candidate_auc", 0.0))
    min_improvement = float(thresholds.get("min_improvement", 0.0))

    abs_ok = candidate_auc >= min_candidate_auc
    rel_ok = (candidate_auc - current_auc) >= min_improvement

    if abs_ok:
        messages.append(
            f"Candidate AUC {candidate_auc:.3f} is above the minimum threshold {min_candidate_auc:.3f}."
        )
    else:
        messages.append(
            f"Candidate AUC {candidate_auc:.3f} is below the minimum threshold {min_candidate_auc:.3f}."
        )

    if rel_ok:
        messages.append(
            f"Candidate AUC {candidate_auc:.3f} is not worse than current AUC {current_auc:.3f} "
            f"by more than the allowed delta ({min_improvement:.3f})."
        )
    else:
        messages.append(
            f"Candidate AUC {candidate_auc:.3f} is too low compared to current AUC {current_auc:.3f} "
            f"given the allowed delta ({min_improvement:.3f})."
        )

    metrics_ok = abs_ok and rel_ok
    return metrics_ok, messages


def main() -> None:
    snapshot_path = INPUTS_DIR / "state_snapshot.json"
    pack_path = INPUTS_DIR / "ai_generated_change_pack_example.json"

    snapshot = load_json(snapshot_path)
    pack = load_json(pack_path)

    result = evaluate_change_pack(snapshot, pack)

    ensure_artifacts_dir()
    artifacts_path = ARTIFACTS_DIR / "ch07_result.json"
    with artifacts_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Human-friendly one-line summary
    print(f"[CH07] Lab completed. status={result['status']} → {artifacts_path}")


if __name__ == "__main__":
    main()
