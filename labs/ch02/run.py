#!/usr/bin/env python3
"""
CH02 lab runner.

Reads a tiny boundary configuration and a simple change request,
evaluates the request against boundary, unit limits, and RB-30,
and writes a deterministic JSON result to artifacts/result.json.
"""

import json
from pathlib import Path
from typing import Any, Dict, List


HERE = Path(__file__).resolve().parent
INPUTS_DIR = HERE / "inputs"
ARTIFACTS_DIR = HERE / "artifacts"


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def ensure_artifacts_dir() -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def evaluate_change_request(
    boundary_config: Dict[str, Any],
    change_request: Dict[str, Any],
) -> Dict[str, Any]:
    # Summary metrics
    files = change_request.get("files", [])
    files_count = len(files)
    total_lines_added = 0

    for f in files:
        hunks: List[Dict[str, Any]] = f.get("hunks", [])
        for h in hunks:
            total_lines_added += int(h.get("lines_added", 0))

    # Boundary check: all paths must start with one of the allowed prefixes.
    allowed_prefixes = boundary_config.get("allowed_path_prefixes", [])
    boundary_ok = True
    for f in files:
        path = f.get("path", "")
        if not any(path.startswith(prefix) for prefix in allowed_prefixes):
            boundary_ok = False
            break

    # Unit limits check: number of files and total lines added.
    limits = boundary_config.get("limits", {})
    max_files = int(limits.get("max_files_changed", 0) or 0)
    max_lines = int(limits.get("max_lines_added", 0) or 0)

    unit_ok = True
    if max_files and files_count > max_files:
        unit_ok = False
    if max_lines and total_lines_added > max_lines:
        unit_ok = False

    # RB-30 check: anchor present and type in allowed list.
    rb30_cfg = boundary_config.get("rb30", {})
    required = bool(rb30_cfg.get("required", True))
    allowed_types = rb30_cfg.get("allowed_anchor_types", [])

    anchor = change_request.get("rb30_anchor")
    if not required and anchor is None:
        rb30_ok = True
    elif anchor is None:
        rb30_ok = False
    else:
        anchor_type = anchor.get("type")
        rb30_ok = (not allowed_types) or (anchor_type in allowed_types)

    # Overall status
    status = "accept" if (boundary_ok and unit_ok and rb30_ok) else "reject"

    return {
        "chapter": change_request.get("chapter", "CH02"),
        "change_id": change_request.get("change_id"),
        "metrics": {
            "files_count": files_count,
            "total_lines_added": total_lines_added,
            "within_limits": bool(unit_ok),
        },
        "checks": {
            "boundary_ok": bool(boundary_ok),
            "unit_ok": bool(unit_ok),
            "rb30_ok": bool(rb30_ok),
        },
        "status": status,
        "messages": build_messages(boundary_ok, unit_ok, rb30_ok),
    }


def build_messages(boundary_ok: bool, unit_ok: bool, rb30_ok: bool) -> List[str]:
    messages: List[str] = []

    if boundary_ok:
        messages.append("All file paths stay within allowed prefixes.")
    else:
        messages.append("Some file paths are outside the allowed prefixes.")

    if unit_ok:
        messages.append("Change stays within the configured Change Unit limits.")
    else:
        messages.append("Change exceeds the configured Change Unit limits.")

    if rb30_ok:
        messages.append("RB-30 anchor is present and allowed.")
    else:
        messages.append("RB-30 anchor is missing or uses a disallowed type.")

    return messages


def main() -> None:
    boundary_config_path = INPUTS_DIR / "boundary_config.json"
    change_request_path = INPUTS_DIR / "change_request.json"

    boundary_config = load_json(boundary_config_path)
    change_request = load_json(change_request_path)

    result = evaluate_change_request(boundary_config, change_request)

    ensure_artifacts_dir()
    artifacts_path = ARTIFACTS_DIR / "result.json"
    with artifacts_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Human-friendly one-line summary（パスは Path から算出）
    display_path = artifacts_path.relative_to(HERE)
    print(f"[CH02] Lab completed. status={result['status']} → {display_path}")


if __name__ == "__main__":
    main()
