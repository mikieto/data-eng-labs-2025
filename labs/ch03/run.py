#!/usr/bin/env python
from pathlib import Path
import json
import math


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def compute_metrics(pipeline_cfg: dict, sli_slo_cfg: dict):
    """
    CH03-specific logic:
    - integration_pipeline.json + sli_slo_config.json -> SLI/SLO & ROI metrics.
    """
    scenario_id = sli_slo_cfg.get("scenario_id", "baseline")

    sources = pipeline_cfg.get("sources", [])
    total_monthly_impact = sum(
        float(s.get("expected_monthly_revenue_impact_usd", 0.0)) for s in sources
    )
    total_effort_days = sum(
        float(s.get("integration_effort_days", 0.0)) for s in sources
    )

    cost_per_day = float(sli_slo_cfg.get("cost_per_engineer_day_usd", 8000.0))
    integration_cost = total_effort_days * cost_per_day

    slis = pipeline_cfg.get("slis", {})
    freshness_hours = float(slis.get("freshness_hours", 3.0))
    coverage_pct = float(slis.get("coverage_pct", 0.98))

    if integration_cost > 0 and total_monthly_impact > 0:
        roi_after_12_months = (
            12.0 * total_monthly_impact - integration_cost
        ) / integration_cost
        payback_period_months = integration_cost / total_monthly_impact
    else:
        roi_after_12_months = 0.0
        payback_period_months = math.inf

    thresholds = sli_slo_cfg.get("slo_thresholds", {})
    freshness_max = float(thresholds.get("freshness_hours_max", 6.0))
    coverage_min = float(thresholds.get("coverage_pct_min", 0.95))

    roi_target = float(sli_slo_cfg.get("roi_target_after_12_months", 3.0))
    payback_target = float(sli_slo_cfg.get("payback_period_target_months", 12.0))

    sli_slo_ok = (freshness_hours <= freshness_max) and (coverage_pct >= coverage_min)
    roi_ok = (roi_after_12_months >= roi_target) and (payback_period_months <= payback_target)
    overall_ok = sli_slo_ok and roi_ok

    metrics = {
        "total_expected_monthly_impact_usd": total_monthly_impact,
        "total_integration_effort_days": total_effort_days,
        "total_integration_cost_usd": integration_cost,
        "freshness_hours": freshness_hours,
        "coverage_pct": coverage_pct,
        "roi_after_12_months": roi_after_12_months,
        "payback_period_months": payback_period_months,
    }

    checks = {
        "sli_slo_ok": sli_slo_ok,
        "roi_ok": roi_ok,
        "overall_ok": overall_ok,
    }

    return scenario_id, metrics, checks


def main():
    base_dir = Path(__file__).resolve().parent
    inputs_dir = base_dir / "inputs"
    artifacts_dir = base_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    output_path = artifacts_dir / "result.json"

    pipeline_cfg = load_json(inputs_dir / "integration_pipeline.json")
    sli_slo_cfg = load_json(inputs_dir / "sli_slo_config.json")

    scenario_id, metrics, checks = compute_metrics(pipeline_cfg, sli_slo_cfg)

    status = "accept" if checks.get("overall_ok", False) else "reject"
    pipeline_id = pipeline_cfg.get("pipeline_id", "ch03_demo_pipeline")

    messages = [
        f"Evaluated integration pipeline '{pipeline_id}' for scenario '{scenario_id}'.",
    ]

    if status == "accept":
        messages.append(
            "All key SLI/SLO thresholds and ROI targets are satisfied for this scenario."
        )
    else:
        messages.append(
            "One or more SLI/SLO thresholds or ROI targets were not satisfied."
        )

    result = {
        "chapter": "CH03",
        "status": status,
        "change_id": scenario_id,
        "messages": messages,
        "checks": checks,
        "metrics": metrics,
    }

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[CH03] Lab completed. status={status} → {output_path.relative_to(base_dir)}")


if __name__ == "__main__":
    main()
