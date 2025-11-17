#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# 先頭何行を出すか（ターミナルの LINES と衝突しない名前にする）
READ_LINES=${READ_LINES:-25}

for dir in labs/ch??; do
  readme="$dir/README.md"
  if [[ -f "$readme" ]]; then
    echo "============================================================"
    echo ">>> $(basename "$dir")/README.md (first ${READ_LINES} lines)"
    echo "============================================================"
    sed -n "1,${READ_LINES}p" "$readme"
    echo
  fi
done
