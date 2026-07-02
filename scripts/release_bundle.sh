#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

name="erinys-care-memory-release"
out="${1:-/tmp/${name}.tgz}"
# Never bundle secrets: .env is gitignored and holds the live API key.
# umask 077 so the archive is not world-readable in a shared /tmp.
umask 077
tar --exclude ".venv" --exclude ".data" --exclude "__pycache__" --exclude ".pytest_cache" \
  --exclude ".env" --exclude ".env.*" --exclude ".git" \
  --exclude ".versions" --exclude "docs" --exclude "submissions" \
  -czf "$out" .
shasum -a 256 "$out"
echo "$out"
