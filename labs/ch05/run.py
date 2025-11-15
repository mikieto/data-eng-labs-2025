#!/usr/bin/env python3
"""
CH05 lab runner — Mini Single Change Highway.

Reads a tiny pipeline configuration in YAML (very small subset),
checks whether the pipeline respects the canonical
validate → dry_run → gate → apply → export → rb30_verify order,
and writes a deterministic JSON result to artifacts/ch05_result.json.
"""

import json
from pathlib import Path
from typing import Any, Dict, List


HERE = Path(__file__).resolve().parent
INPUTS_DIR = HERE / "inputs"
ARTIFACTS_DIR = HERE / "artifacts"


CANONICAL_STAGES: List[str] = [
    "validate",
    "dry_run",
    "gate",
    "apply",
    "export",
    "rb30_verify",
]


def parse_pipeline_yaml(path: Path) -> Dict[str, Any]:
    """Parse a very small subset of YAML for this lab.

    Expected shape:

    name: ch05_mini_highway
    description: "Tiny Single Change Highway for CH05 lab."
    stages:
      - validate
      - dry_run
      - gate
      - apply
      - export
      - rb30_verify

    This parser is intentionally minimal and only understands:

    - top-level "key: value" pairs (single line)
    - a "stages:" key, followed by indented "- value" lines
    """
    name = None
    description = None
    stages: List[str] = []

    in_stages = False

    with path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")
            stripped = line.strip()

            if not stripped or stripped.startswith("#"):
                continue

            # Detect top-level keys
            if not line.startswith(" ") and stripped.endswith(":"):
                key = stripped[:-1]
                if key == "stages":
                    in_stages = True
                else:
                    in_stages = False
                continue

            # key: value on one line
            if not line.startswith(" ") and ":" in stripped:
                key, value = stripped.split(":", 1)
                key = key.strip()
                value = value.strip().strip('"')
                if key == "name":
                    name = value
                elif key == "description":
                    description = value
                continue

            # stages list items
            if in_stages and stripped.startswith("- "):
                stage_id = stripped[2:].strip()
                stages.append(stage_id)
                continue

    return {
        "name": name,
        "description": description,
        "stages": stages,
    }


def ensure_artifacts_dir() -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def evaluate_pipeline(pipeline: Dict[str, Any]) -> Dict[str, Any]:
    stages: List[str] = pipeline.get("stages", [])
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

    return {
        "chapter": "CH05",
        "pipeline_name": pipeline.get("name") or "unknown",
        "summary": {
            "stage_count": stage_count,
            "unknown_stages": unknown_stages,
            "missing_stages": missing_stages,
            "extra_stages": extra_stages,
        },
        "checks": {
            "order_ok": bool(order_ok),
            "required_stages_ok": bool(required_stages_ok),
            "rb30_ok": bool(rb30_ok),
        },
        "status": status,
        "messages": build_messages(
            order_ok=order_ok,
            required_stages_ok=required_stages_ok,
            rb30_ok=rb30_ok,
            unknown_stages=unknown_stages,
            missing_stages=missing_stages,
        ),
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
            "Pipeline stages follow the canonical validate→dry_run→gate→apply→export→rb30_verify order."
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
    pipeline_path = INPUTS_DIR / "pipeline.yml"
    pipeline = parse_pipeline_yaml(pipeline_path)
    result = evaluate_pipeline(pipeline)

    ensure_artifacts_dir()
    artifacts_path = ARTIFACTS_DIR / "ch05_result.json"
    with artifacts_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Human-friendly one-line summary
    print(f"[CH05] Lab completed. status={result['status']} → {artifacts_path}")


if __name__ == "__main__":
    main()
