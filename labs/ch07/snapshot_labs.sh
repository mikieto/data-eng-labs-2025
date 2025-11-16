#!/usr/bin/env bash
set -euo pipefail

# LABS Global Snapshot generator (Day-0 / dev helper)
# - Aggregates labs/chXX/artifacts/result.json into a single
#   labs/ch07/inputs/state_snapshot.json for CH07 Lab.
#
# This script is a dev/authoring helper, NOT part of the reader's GA flow.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CH07_DIR="${SCRIPT_DIR}"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${REPO_ROOT}" || {
  echo "[ERROR] failed to cd to LABS repo root: ${REPO_ROOT}" >&2
  exit 1
}

NOW_UTC="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

SNAPSHOT_PATH="${CH07_DIR}/inputs/state_snapshot.json"

TMP_JSON="$(mktemp)"
echo '{}' > "${TMP_JSON}"

found_any=false

# 1) Aggregate chapter result.json files
for path in labs/ch*/artifacts/result.json; do
  if [[ ! -f "${path}" ]]; then
    continue
  fi

  # labs/ch02/artifacts/result.json -> ch02 -> CH02
  CH_LOWER="$(echo "${path}" | sed -E 's|labs/(ch[0-9]+)/.*|\1|')"
  CH_UPPER="$(echo "${CH_LOWER}" | tr 'a-z' 'A-Z')"

  chapter_json="$(cat "${path}")"

  jq \
    --arg chapter "${CH_UPPER}" \
    --argjson result "${chapter_json}" \
    '.chapters[$chapter] = { "result": $result }' \
    "${TMP_JSON}" > "${TMP_JSON}.new"

  mv "${TMP_JSON}.new" "${TMP_JSON}"
  found_any=true
done

if [[ "${found_any}" != true ]]; then
  echo "[WARN] No labs/chXX/artifacts/result.json found; writing empty chapters object." >&2
fi

# 2) Wrap with meta + boundary + metrics for CH07 evaluator
jq \
  --arg generated_by "labs/ch07/snapshot_labs.sh" \
  --arg ts "${NOW_UTC}" \
  '
  .meta = {
    generated_by: $generated_by,
    generated_ts_utc: $ts,
    profile: "HDBM-LABS-Global",
    scope: "labs"
  }
  | .chapters = (.chapters // {})
  | .boundary = (.boundary // {
      allowed_targets: ["production"]
    })
  | .metrics = (.metrics // {
      current_model:  { id: "ch07_model_v1", auc: 0.92 },
      candidate_model:{ id: "ch07_model_v2", auc: 0.94 },
      min_auc: 0.90,
      max_delta_auc: 0.05
    })
  ' \
  "${TMP_JSON}" > "${SNAPSHOT_PATH}"

rm -f "${TMP_JSON}"

echo "[OK] Wrote Labs Global Snapshot to ${SNAPSHOT_PATH}"
