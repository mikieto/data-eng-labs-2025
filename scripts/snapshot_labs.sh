#!/usr/bin/env bash
set -euo pipefail

# LABS snapshot generator for HDBM
# - With CHAPTER arg: creates/refreshes labs/chxx/inputs/state_snapshot.json
#   for that chapter, then regenerates outputs/state_snapshot_labs.json
#   by aggregating all existing chapter snapshots.
# - Without arg: only regenerates outputs/state_snapshot_labs.json
#   from existing labs/chxx/inputs/state_snapshot.json files.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}" || {
  echo "[ERROR] failed to cd to LABS repo root: ${REPO_ROOT}" >&2
  exit 1
}

CHAPTER="${1:-}"

NOW_UTC="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

# ---------------------------------------------------------
# 1) Optional: generate/refresh per-chapter local snapshot
# ---------------------------------------------------------

if [[ -n "${CHAPTER}" ]]; then
  case "${CHAPTER}" in
    CH02|CH03|CH04|CH05|CH06|CH07|CH08|CH09|CH10)
      ;;
    *)
      echo "[ERROR] unsupported chapter: ${CHAPTER} (expected CH02–CH10)" >&2
      exit 1
      ;;
  esac

  CH_LOWER="$(echo "${CHAPTER}" | tr 'A-Z' 'a-z')"   # CH02 -> ch02
  OUTPUT_DIR="labs/${CH_LOWER}/inputs"
  SNAPSHOT_PATH="${OUTPUT_DIR}/state_snapshot.json"

  mkdir -p "${OUTPUT_DIR}"

  cat > "${SNAPSHOT_PATH}" <<EOF
{
  "meta": {
    "generated_by": "scripts/snapshot_labs.sh",
    "generated_ts_utc": "${NOW_UTC}",
    "profile": "HDBM-LABS-LOCAL",
    "chapter": "${CHAPTER}"
  },
  "lab_world": {
    "root": "labs/${CH_LOWER}",
    "runner": "labs/${CH_LOWER}/run.py",
    "expected_result": "labs/${CH_LOWER}/artifacts/${CH_LOWER}_result.json"
  },
  "notes": {
    "todo": [
      "Reflect actual lab file structure and learning objectives for ${CHAPTER}",
      "Keep this local snapshot derived from the global state_snapshot_labs.json in the future"
    ]
  }
}
EOF

  echo "[OK] Wrote local LABS snapshot for ${CHAPTER} to ${SNAPSHOT_PATH}"
fi

# ---------------------------------------------------------
# 2) Aggregate all chapter snapshots into a global snapshot
# ---------------------------------------------------------

OUTPUTS_DIR="outputs"
GLOBAL_SNAPSHOT_PATH="${OUTPUTS_DIR}/state_snapshot_labs.json"

mkdir -p "${OUTPUTS_DIR}"

TMP_JSON="$(mktemp)"
echo '{}' > "${TMP_JSON}"

found_any=false

for path in labs/ch*/inputs/state_snapshot.json; do
  if [[ ! -f "${path}" ]]; then
    continue
  fi

  # Extract chapter key from path: labs/ch02/inputs/state_snapshot.json -> ch02 -> CH02
  CH_LOWER="$(echo "${path}" | sed -E 's|labs/(ch[0-9]+)/.*|\1|')"
  CH_UPPER="$(echo "${CH_LOWER}" | tr 'a-z' 'A-Z')"

  chapter_json="$(cat "${path}")"

  jq \
    --arg chapter "${CH_UPPER}" \
    --argjson chapter_obj "${chapter_json}" \
    '.chapters[$chapter] = $chapter_obj' \
    "${TMP_JSON}" > "${TMP_JSON}.new"

  mv "${TMP_JSON}.new" "${TMP_JSON}"
  found_any=true
done

if [[ "${found_any}" != true ]]; then
  echo "[WARN] No labs/chxx/inputs/state_snapshot.json found; writing empty chapters object." >&2
fi

jq \
  --arg generated_by "scripts/snapshot_labs.sh" \
  --arg ts "${NOW_UTC}" \
  '.meta = {
      generated_by: $generated_by,
      generated_ts_utc: $ts,
      profile: "HDBM-LABS-Global",
      scope: "labs"
    }
   | .chapters = (.chapters // {})' \
  "${TMP_JSON}" > "${GLOBAL_SNAPSHOT_PATH}"

rm -f "${TMP_JSON}"

echo "[OK] Wrote global LABS snapshot to ${GLOBAL_SNAPSHOT_PATH}"
