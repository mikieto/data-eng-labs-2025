#!/usr/bin/env bash

echo "=== [LABS] data-eng-labs-2025 Status Check ==="
echo

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR" || {
  echo "[NG] repo root に移動できません: $ROOT_DIR"
  exit 1
}

STATUS=0

echo "[INFO] Git 状態"
git status --short || {
  echo "[NG] git status に失敗しました"
  STATUS=1
}
echo

echo "[INFO] 必須ファイルの存在チェック（最低限）"
check_file() {
  local path="$1"
  if [[ -f "$path" ]]; then
    echo "  [OK] $path"
  else
    echo "  [NG] $path がありません"
    STATUS=1
  fi
}

check_optional_file() {
  local path="$1"
  if [[ -f "$path" ]]; then
    echo "  [OK] $path"
  else
    echo "  [WARN] $path はまだありません（初期状態なら想定内）"
  fi
}

check_file "README.md"

# devcontainer はまだ設計中かもしれないので optional 扱い
check_optional_file ".devcontainer/devcontainer.json"

echo
echo "[INFO] labs ディレクトリの確認"

LABS_ROOT="$ROOT_DIR/labs"
if [[ -d "$LABS_ROOT" ]]; then
  echo "  [OK] labs/ ディレクトリあり ($LABS_ROOT)"
else
  echo "  [NG] labs/ ディレクトリがありません ($LABS_ROOT)"
  STATUS=1
fi

echo
echo "[INFO] labs/chXX ディレクトリと代表ファイル（情報出力のみ）"

if [[ -d "$LABS_ROOT" ]]; then
  # labs/chNN というディレクトリを自動検出
  mapfile -t CH_DIRS < <(find "$LABS_ROOT" -mindepth 1 -maxdepth 1 -type d -name 'ch[0-9][0-9]' -printf '%f\n' | sort)

  if [[ ${#CH_DIRS[@]} -eq 0 ]]; then
    echo "  [INFO] labs/chXX ディレクトリはまだありません"
  else
    for ch in "${CH_DIRS[@]}"; do
      echo
      echo "--- $ch ---"
      local_ch_dir="$LABS_ROOT/$ch"

      if [[ -f "$local_ch_dir/run.py" ]]; then
        echo "  [OK] run.py"
      else
        echo "  [WARN] run.py がありません"
      fi

      if [[ -f "$local_ch_dir/README.md" ]]; then
        echo "  [OK] README.md"
      else
        echo "  [WARN] README.md がありません"
      fi

      if [[ -d "$local_ch_dir/inputs" ]]; then
        echo "  [OK] inputs/ ディレクトリあり"
      else
        echo "  [WARN] inputs/ ディレクトリがありません"
      fi

      if [[ -d "$local_ch_dir/artifacts" ]]; then
        echo "  [OK] artifacts/ ディレクトリあり"
      else
        echo "  [WARN] artifacts/ ディレクトリがありません"
      fi

      echo "  [INFO] $ch 配下のファイル（max depth=3）"
      find "$local_ch_dir" -maxdepth 3 -type f | sort | sed 's/^/    /'
    done
  fi
else
  echo "  [INFO] labs/ が無いので chXX の詳細はスキップします"
fi

echo
if [[ $STATUS -eq 0 ]]; then
  echo "[OK] LABS repo はひとまず問題なさそうです。"
else
  echo "[NG] LABS repo に確認すべき点があります（上のログを参照してください）。"
fi

exit "$STATUS"
