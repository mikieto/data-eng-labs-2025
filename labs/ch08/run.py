#!/usr/bin/env python
from pathlib import Path
import json

def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def main():
    base_dir = Path(__file__).resolve().parent
    inputs_dir = base_dir / "inputs"
    artifacts_dir = base_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    out_path = artifacts_dir / "result.json"

    cfg = load_json(inputs_dir / "pipeline.json")

    stages = cfg.get("stages", [])
    stage_count = len(stages)
    guards_per_stage = [len(s.get("guards", [])) for s in stages]
    owners = [s.get("owner_team") for s in stages]

    missing_guards = [s["name"] for s in stages if not s.get("guards")]
    missing_owners = [s["name"] for s in stages if not s.get("owner_team")]

    checks = {
        "has_stages": stage_count > 0,
        "all_stages_have_guard": len(missing_guards) == 0,
        "all_stages_have_owner": len(missing_owners) == 0,
    }

    status = "accept" if all(checks.values()) else "reject"

    messages = [
        "Checked guard coverage and owner teams for a tiny CI/CD pipeline."
    ]
    if status == "accept":
        messages.append("Every stage has at least one guard and an owner team.")
    else:
        if missing_guards:
            messages.append(f"Stages missing guards: {missing_guards}")
        if missing_owners:
            messages.append(f"Stages missing owner_team: {missing_owners}")

    result = {
        "chapter": "CH08",
        "status": status,
        "change_id": cfg.get("pipeline_id", "unknown"),
        "messages": messages,
        "checks": checks,
        "metrics": {
            "stage_count": stage_count,
            "guards_per_stage": guards_per_stage,
            "owner_teams": owners,
            "missing_guards": missing_guards,
            "missing_owners": missing_owners,
        },
    }

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[CH08] Lab completed. status={status} → {out_path.relative_to(base_dir)}")


if __name__ == "__main__":
    main()
