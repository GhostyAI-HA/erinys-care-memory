#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

env_file="${1:-.env}"
if [[ ! -f "$env_file" ]]; then
  echo "Missing env file: $env_file" >&2
  exit 1
fi

docker build -t erinys-care-memory:latest .
docker rm -f erinys-care-memory >/dev/null 2>&1 || true
docker run -d --name erinys-care-memory --restart unless-stopped \
  --env-file "$env_file" -p "${ERINYS_PUBLIC_PORT:-80}:8000" \
  -v erinys-care-memory-data:/data erinys-care-memory:latest
docker ps --filter "name=erinys-care-memory"
