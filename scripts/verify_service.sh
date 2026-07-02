#!/usr/bin/env bash
set -euo pipefail

base_url="${1:-http://127.0.0.1}"

curl -fsS "$base_url/health"
printf '\n'
curl -fsS -X POST "$base_url/run/benchmark" \
  -H 'Content-Type: application/json' \
  -d '{}' \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print({"model": d["model"], "live": d["qwen_live_configured"], "reduction": d["token_reduction_percent"], "counts": d["governance_counts"]})'
