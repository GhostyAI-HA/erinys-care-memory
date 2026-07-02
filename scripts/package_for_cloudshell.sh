#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "$0")/.." && pwd)"
project_parent="$(dirname "$project_root")"
project_name="$(basename "$project_root")"
output="${1:-/tmp/erinys-care-memory-stdlib.tgz}"

# Never bundle secrets: .env is gitignored and holds the live API key.
# umask 077 so the tarball and its base64 sidecar are not world-readable in /tmp.
umask 077

tar \
  --exclude="${project_name}/.venv" \
  --exclude="${project_name}/.data" \
  --exclude="${project_name}/__pycache__" \
  --exclude="${project_name}/app/__pycache__" \
  --exclude="${project_name}/tests/__pycache__" \
  --exclude="${project_name}/.pytest_cache" \
  --exclude="${project_name}/.env" \
  --exclude="${project_name}/.env.*" \
  --exclude="${project_name}/.git" \
  -czf "$output" \
  -C "$project_parent" \
  "$project_name"

if base64 -i "$output" -o "${output}.b64" 2>/dev/null; then
  :
else
  base64 "$output" > "${output}.b64"
fi

wc -c "$output" "${output}.b64"
