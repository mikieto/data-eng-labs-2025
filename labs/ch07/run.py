#!/usr/bin/env python
"""
CH07 Lab Day-0 / Phase-1 runner

- Reads Labs Global Snapshot (labs/ch07/inputs/state_snapshot.json)
- Reads AI-generated change pack (labs/ch07/inputs/ai_generated_change_pack_example.json)
- Evaluates the pack against schema, chapter, RB-30, boundary, and metrics
- Writes labs/ch07/artifacts/result.json

This runner never:
- calls external LLMs
- modifies files outside labs/ch07/**
- executes code contained in the change pack
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


CH07_DIR = Path(__file__).resolve().parent
INPUTS_DIR = CH07_DIR / "inputs"
ARTIFACTS_DIR = CH07_DIR / "artifacts"

SNAPSHOT_PATH = INPUTS_DIR / "state_snapshot.json"
CHANGE_PACK_PATH = INPUTS_DIR / "ai_generated_change_pack_example.json"
RESULT_PATH = ARTIFACTS_DIR / "result.json"


def load_json(path: Path, errors: List[str]) -> Dict[str, Any]:
    if not path.exists():
        errors.append(f"File not found: {path}")
        return {}

    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:  # noqa: BLE001
        errors.append(f"Failed to parse JSON at {path}: {e}")
        return {}


def check_schema(change_pack: Dict[str, Any], messages: List[str]) -> bool:
    required_top_level = ["kind", "chapter", "mode", "rb30_anchor", "summary", "changes"]
    ok = True

    for key in required_top_level:
        if key not in change_pack:
            messages.append(f"[schema] Missing required key: {key}")
            ok = False

    if change_pack.get("kind") != "ai_generated_change_pack":
        messages.append(
            f"[schema] kind must be 'ai_generated_change_pack', got: {change_pack.get('kind')!r}"
        )
        ok = False

    if not isinstance(change_pack.get("changes"), list):
        messages.append("[schema] 'changes' must be a list.")
        ok = False

    return ok


def check_chapter(change_pack: Dict[str, Any], snapshot: Dict[str, Any], messages: List[str]) -> bool:
    ok = True

    chapter = change_pack.get("chapter")
    mode = change_pack.get("mode")

    if chapter != "CH07":
        messages.append(f"[chapter] chapter must be 'CH07', got: {chapter!r}")
        ok = False

    if mode != "labs":
        messages.append(f"[chapter] mode must be 'labs', got: {mode!r}")
        ok = False

    # Optional: if snapshot has a chapters.CH07 entry, we can check consistency
    chapters = snapshot.get("chapters", {})
    if chapters and "CH07" not in chapters:
        messages.append("[chapter] snapshot.chapters is present but does not contain CH07.")
        # not fatal, but worth flagging
    return ok


def check_rb30(change_pack: Dict[str, Any], messages: List[str]) -> bool:
    ok = True
    anchor = change_pack.get("rb30_anchor")

    if not isinstance(anchor, dict):
        messages.append("[rb30] rb30_anchor must be an object.")
        return False

    anchor_type = anchor.get("type")
    anchor_ref = anchor.get("ref")

    allowed_types = {"tag", "swap", "tt"}
    if anchor_type not in allowed_types:
        messages.append(
            f"[rb30] rb30_anchor.type must be one of {sorted(allowed_types)}, got: {anchor_type!r}"
        )
        ok = False

    if not anchor_ref or not isinstance(anchor_ref, str):
        messages.append("[rb30] rb30_anchor.ref must be a non-empty string.")
        ok = False

    return ok


def check_boundary(
    change_pack: Dict[str, Any],
    snapshot: Dict[str, Any],
    messages: List[str],
) -> bool:
    ok = True

    boundary = snapshot.get("boundary") or {}
    allowed_targets = boundary.get("allowed_targets")

    if not isinstance(allowed_targets, list) or not allowed_targets:
        messages.append("[boundary] snapshot.boundary.allowed_targets must be a non-empty list.")
        return False

    allowed_set = set(str(t) for t in allowed_targets)
    targets_in_pack = set()

    for change in change_pack.get("changes", []):
        target = change.get("target")
        if target is None:
            messages.append("[boundary] change missing 'target' field.")
            ok = False
            continue
        targets_in_pack.add(str(target))
        if str(target) not in allowed_set:
            messages.append(
                f"[boundary] target {target!r} is not in allowed_targets={sorted(allowed_set)}."
            )
            ok = False

    if targets_in_pack:
        messages.append(
            f"[boundary] targets in pack: {sorted(targets_in_pack)}, "
            f"allowed_targets: {sorted(allowed_set)}"
        )

    return ok


def _extract_metrics(snapshot: Dict[str, Any]) -> Tuple[float | None, float | None, float | None, float | None]:
    """Return (current_auc, candidate_auc, min_auc, max_delta)."""
    metrics = snapshot.get("metrics") or {}
    current = (metrics.get("current_model") or {}).get("auc")
    candidate = (metrics.get("candidate_model") or {}).get("auc")
    min_auc = metrics.get("min_auc")
    max_delta = metrics.get("max_delta_auc")
    return current, candidate, min_auc, max_delta


def check_metrics(snapshot: Dict[str, Any], messages: List[str]) -> Tuple[bool, Dict[str, float]]:
    current_auc, candidate_auc, min_auc, max_delta = _extract_metrics(snapshot)

    info: Dict[str, float] = {}

    # If any critical field is missing, fail closed.
    if current_auc is None or candidate_auc is None or min_auc is None or max_delta is None:
        messages.append(
            "[metrics] Missing one of current_auc, candidate_auc, min_auc, max_delta_auc "
            "in snapshot.metrics; rejecting for safety."
        )
        return False, info

    info = {
        "current_auc": float(current_auc),
        "candidate_auc": float(candidate_auc),
        "min_auc": float(min_auc),
        "max_delta_auc": float(max_delta),
    }

    ok = True

    if info["candidate_auc"] < info["min_auc"]:
        messages.append(
            f"[metrics] candidate_auc={info['candidate_auc']:.3f} < "
            f"min_auc={info['min_auc']:.3f}."
        )
        ok = False

    delta = info["candidate_auc"] - info["current_auc"]
    info["delta_auc"] = delta

    if delta < -info["max_delta_auc"]:
        messages.append(
            f"[metrics] candidate is worse than current by {delta:.3f}, "
            f"allowed degradation is {info['max_delta_auc']:.3f}."
        )
        ok = False

    if ok:
        messages.append(
            "[metrics] Candidate model satisfies min_auc and max_delta_auc constraints."
        )

    return ok, info


def main() -> int:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    messages: List[str] = []
    load_errors: List[str] = []

    snapshot = load_json(SNAPSHOT_PATH, load_errors)
    change_pack = load_json(CHANGE_PACK_PATH, load_errors)

    for err in load_errors:
        messages.append(f"[io] {err}")

    # Default checks to False if I/O failed
    if load_errors:
        checks = {
            "schema_ok": False,
            "chapter_ok": False,
            "rb30_ok": False,
            "boundary_ok": False,
            "metrics_ok": False,
        }
        metrics_info: Dict[str, float] = {}
        status = "reject"
    else:
        schema_ok = check_schema(change_pack, messages)
        chapter_ok = check_chapter(change_pack, snapshot, messages)
        rb30_ok = check_rb30(change_pack, messages)
        boundary_ok = check_boundary(change_pack, snapshot, messages)
        metrics_ok, metrics_info = check_metrics(snapshot, messages)

        checks = {
            "schema_ok": schema_ok,
            "chapter_ok": chapter_ok,
            "rb30_ok": rb30_ok,
            "boundary_ok": boundary_ok,
            "metrics_ok": metrics_ok,
        }

        status = "accept" if all(checks.values()) else "reject"

    # Simple summary
    changes = change_pack.get("changes") if isinstance(change_pack, dict) else []
    change_count = len(changes) if isinstance(changes, list) else 0
    boundary_targets = sorted({c.get("target") for c in changes if isinstance(c, dict) and "target" in c})

    result = {
        "chapter": "CH07",
        "status": status,
        "change_id": None,  # can be wired to STR IDs later
        "summary": {
            "change_count": change_count,
            "boundary_targets": boundary_targets,
        },
        "checks": checks,
        "metrics": metrics_info,
        "messages": messages,
    }

    with RESULT_PATH.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[CH07] Wrote evaluation result to {RESULT_PATH} (status={status}).")
    return 0 if status == "accept" else 1


if __name__ == "__main__":
    raise SystemExit(main())
