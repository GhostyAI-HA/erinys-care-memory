#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

name="erinys-care-memory-release"
out="${1:-/tmp/${name}.tgz}"
tar --exclude ".venv" --exclude ".data" --exclude "__pycache__" --exclude ".pytest_cache" \
  -czf "$out" .
shasum -a 256 "$out"
echo "$out"
