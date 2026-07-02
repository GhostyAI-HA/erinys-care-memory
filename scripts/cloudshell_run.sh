#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8000}"
export QWEN_MODEL="${QWEN_MODEL:-qwen3.7-plus}"
export QWEN_BASE_URL="${QWEN_BASE_URL:-https://dashscope-intl.aliyuncs.com/compatible-mode/v1}"

if [[ -z "${QWEN_API_KEY:-${DASHSCOPE_API_KEY:-}}" ]]; then
  export QWEN_LIVE="${QWEN_LIVE:-0}"
  echo "Qwen key not detected. Starting deterministic demo fallback."
else
  export QWEN_LIVE="${QWEN_LIVE:-1}"
  echo "Qwen key detected. Starting Qwen Cloud live mode."
fi

python3 -m app.server
