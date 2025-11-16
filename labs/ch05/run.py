#!/usr/bin/env python3
"""
CH05 lab runner — Mini Single Change Highway (JSON version).

Reads a tiny pipeline configuration in JSON, checks whether the pipeline
respects the canonical
validate → dry_run → gate → apply → export → rb30_verify order,
and writes a deterministic JSON result to artifacts/result.json.

Top-level result keys (contract):
- chapter: "CH05"
- status: "accept" | "reject"
- change_id: scenario or logical ID for this run (e.g. "baseline")
- messages: list[str] for human readers
- checks: dict[str, bool] for key gate results
- metrics: dict[str, number or small string] for simple metrics
"""

import json
from pathlib import Path
from typing import Any, Dict, List


HERE = Path(__file__).resolve().parent
INPUTS_DIR = HERE / "inputs"
ARTIFACTS_DIR = HERE / "artifacts"

PIPELINE_FILE = INPUTS_DIR / "pipeline.json"

CANONICAL_STAGES: List[str] = [
    "validate",
    "dry_run",
    "gate",
    "apply",
    "export",
    "rb30_verify",
]


def load_pipeline(path: Path) -> Dict[str, Any]:
    """Load a tiny pipeline definition from JSON.

    Expected shape (example):

    {
      "pipeline_name": "ch05_mini_highway",
      "description": "Tiny Single Change Highway for CH05 lab.",
      "scenario": "baseline",
      "stages": [
        "validate",
        "dry_run",
        "gate",
        "apply",
        "export",
        "rb30_verify"
      ]
    }

    Extra fields are ignored by this runner.
    """
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def ensure_artifacts_dir() -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def evaluate_pipeline(pipeline: Dict[str, Any]) -> Dict[str, Any]:
    stages: List[str] = pipeline.get("stages", []) or []
    stage_count = len(stages)

    # Classify stages
    unknown_stages = [s for s in stages if s not in CANONICAL_STAGES]
    missing_stages = [s for s in CANONICAL_STAGES if s not in stages]
    extra_stages = [s for s in stages if s not in CANONICAL_STAGES]

    # Order check: when we filter to canonical stages, the sequence must
    # match the canonical list exactly.
    filtered = [s for s in stages if s in CANONICAL_STAGES]
    order_ok = filtered == CANONICAL_STAGES

    # Required stages: all canonical stages must be present.
    required_stages_ok = not missing_stages

    # RB-30 check: rb30_verify must be present and at the end.
    rb30_ok = (
        "rb30_verify" in stages
        and stages[-1] == "rb30_verify"
    )

    status = (
        "accept" if (
            order_ok and required_stages_ok and rb30_ok and not unknown_stages
        ) else "reject"
    )

    checks = {
        "order_ok": bool(order_ok),
        "required_stages_ok": bool(required_stages_ok),
        "rb30_ok": bool(rb30_ok),
        "overall_ok": bool(
            order_ok and required_stages_ok and rb30_ok and not unknown_stages
        ),
    }

    metrics = {
        "pipeline_name": pipeline.get("pipeline_name") or pipeline.get("name") or "unknown",
        "stage_count": stage_count,
        "num_unknown_stages": len(unknown_stages),
        "num_missing_stages": len(missing_stages),
        "num_extra_stages": len(extra_stages),
    }

    messages = build_messages(
        order_ok=order_ok,
        required_stages_ok=required_stages_ok,
        rb30_ok=rb30_ok,
        unknown_stages=unknown_stages,
        missing_stages=missing_stages,
    )

    # CH05 contract に合わせたトップレベル構造
    change_id = pipeline.get("scenario") or "baseline"

    return {
        "chapter": "CH05",
        "status": status,
        "change_id": change_id,
        "messages": messages,
        "checks": checks,
        "metrics": metrics,
    }


def build_messages(
    *,
    order_ok: bool,
    required_stages_ok: bool,
    rb30_ok: bool,
    unknown_stages: List[str],
    missing_stages: List[str],
) -> List[str]:
    messages: List[str] = []

    if order_ok:
        messages.append(
            "Pipeline stages follow the canonical "
            "validate→dry_run→gate→apply→export→rb30_verify order."
        )
    else:
        messages.append(
            "Pipeline stages do not follow the canonical Single Change Highway order."
        )

    if required_stages_ok:
        messages.append("All required stages are present.")
    else:
        messages.append(
            "Some required stages are missing: " + ", ".join(missing_stages)
        )

    if not unknown_stages:
        messages.append("There are no unknown stages in the pipeline.")
    else:
        messages.append(
            "Unknown stages detected: " + ", ".join(unknown_stages)
        )

    if rb30_ok:
        messages.append(
            "RB-30 verification stage (rb30_verify) is present at the end of the pipeline."
        )
    else:
        messages.append(
            "RB-30 verification stage is missing or not at the end of the pipeline."
        )

    return messages


def main() -> None:
    pipeline = load_pipeline(PIPELINE_FILE)
    result = evaluate_pipeline(pipeline)

    ensure_artifacts_dir()
    artifacts_path = ARTIFACTS_DIR / "result.json"
    with artifacts_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Human-friendly one-line summary（パスは Path から算出）
    display_path = artifacts_path.relative_to(HERE)
    print(f"[CH05] Lab completed. status={result['status']} → {display_path}")


if __name__ == "__main__":
    main()
